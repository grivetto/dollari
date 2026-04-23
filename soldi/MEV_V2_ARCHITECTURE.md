# MEV V2 ARCHITECTURE: Arbitrum Flash Loans

## Panoramica dell'Architettura ("L'Angelo Custode")

Questa architettura mira a sfruttare le inefficienze di prezzo (arbitraggio) tra i DEX su rete Arbitrum (es. Uniswap V3, Sushiswap, Camelot) utilizzando i Flash Loans forniti da Aave V3.

Arbitrum è scelto per i bassi costi di transazione (gas fees) rispetto a Ethereum Mainnet, aumentando significativamente il numero di opportunità profittevoli di arbitraggio.

### Componenti Principali

1.  **Off-chain Bot (Rust/Python/Node.js)**:
    *   Monitora il mempool e i prezzi dei pool sui vari DEX in tempo reale.
    *   Identifica le opportunità di arbitraggio (es. `Prezzo ETH Uniswap V3` < `Prezzo ETH Sushiswap`).
    *   Calcola la profittabilità netta considerando gas fees e slippage.
    *   Costruisce e invia la transazione al contratto Smart Contract personalizzato.

2.  **Smart Contract Custom (Solidity su Arbitrum)**:
    *   Richiede il Flash Loan ad Aave V3.
    *   Riceve i fondi.
    *   Esegue i trade sui DEX in un'unica transazione atomica.
    *   Ripaga il Flash Loan ad Aave (capitale + fee, tipicamente 0.05% o 0.09%).
    *   **Meccanismo di Sicurezza**: `require(profit > 0, "Loss detected, reverting");`. Se i trade non generano profitto o lo slippage è troppo alto, l'intera transazione fallisce (revert) e si paga solo il costo del gas.

---

## Contratto Solidity di Base (Scheletro)

Ecco lo scheletro del contratto Solidity che integra `FlashLoanSimpleReceiverBase` di Aave V3.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {FlashLoanSimpleReceiverBase} from "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import {IPoolAddressesProvider} from "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import {IERC20} from "@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol";

// Interfacce fittizie per i DEX (Uniswap/Sushiswap Router)
interface IDexRouter {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract ArbitrageFlashLoan is FlashLoanSimpleReceiverBase {
    address payable owner;

    constructor(address _addressProvider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider)) {
        owner = payable(msg.sender);
    }

    /**
     * @dev Funzione chiamata dal Bot per iniziare l'operazione.
     */
    function requestFlashLoan(address _token, uint256 _amount) public {
        require(msg.sender == owner, "Only owner");
        address receiverAddress = address(this);
        address asset = _token;
        uint256 amount = _amount;
        bytes memory params = ""; // Parametri extra per l'esecuzione (es. path dei DEX)
        uint16 referralCode = 0;

        // Richiama Aave Pool per avviare il prestito lampo
        POOL.flashLoanSimple(
            receiverAddress,
            asset,
            amount,
            params,
            referralCode
        );
    }

    /**
     * @dev Callback chiamata da Aave dopo aver trasferito i fondi a questo contratto.
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        
        // 1. I fondi (amount) sono ora nel contratto.
        
        uint256 balanceBefore = IERC20(asset).balanceOf(address(this));

        // 2. Esegui la logica di arbitraggio qui (es. acquista su DexA, vendi su DexB)
        // Esempio fittizio:
        // uint256 boughtTokens = DexA.swapExactTokensForTokens(amount, ...);
        // DexB.swapExactTokensForTokens(boughtTokens, ...);
        
        uint256 balanceAfter = IERC20(asset).balanceOf(address(this));

        // 3. Calcola l'importo da restituire (Capitale + Fee)
        uint256 amountToOwe = amount + premium;

        // 4. VERIFICA PROFITTO E REVERT ON LOSS
        // Se il saldo finale è minore di quello che dobbiamo restituire, annulla tutto.
        require(balanceAfter >= amountToOwe, "Arbitrage non profittevole: revert in corso!");

        // 5. Approva il pool di Aave a ritirare i fondi per ripagare il prestito
        IERC20(asset).approve(address(POOL), amountToOwe);

        // Il profitto (balanceAfter - amountToOwe) rimane nel contratto e può essere prelevato dall'owner
        return true;
    }

    /**
     * @dev Permette all'owner di prelevare i profitti.
     */
    function withdraw(address _tokenAddress) public {
        require(msg.sender == owner, "Only owner");
        IERC20 token = IERC20(_tokenAddress);
        token.transfer(msg.sender, token.balanceOf(address(this)));
    }
}
```

### Prossimi Passi (Fase 2)
1. Implementare l'interazione specifica con i Router di Uniswap V3 (utilizzando `ISwapRouter`) in `executeOperation`.
2. Sviluppare il bot off-chain in Rust/Python per calcolare le path ottimali in microsecondi.
3. Testare il contratto su Arbitrum Goerli/Sepolia testnet per valutare le stime del gas e i tempi di esecuzione.
