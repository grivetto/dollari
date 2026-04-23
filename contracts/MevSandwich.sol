// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MevSandwich (Orbital Command - Phase 2)
 * @dev Smart Contract per l'estrazione di valore asimmetrica (MEV) su reti EVM.
 * Include il blocco di Rischio Zero Matematico tramite revert().
 */

interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract MevSandwich {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "ACCESSO NEGATO: Solo l'Orbital Command puo' impartire ordini.");
        _;
    }

    /**
     * @dev Esegue l'attacco atomico. Se il profitto finale e' inferiore al target,
     * l'intera transazione fallisce e torna indietro (Rischio Zero).
     */
    function executeAtomicSandwich(
        address router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minProfitExpected
    ) external onlyOwner {
        uint256 startBalance = IERC20(tokenIn).balanceOf(address(this));
        
        // 1. Autorizziamo l'Exchange
        IERC20(tokenIn).approve(router, amountIn);

        // 2. FASE DI FRONT-RUN (Compriamo un millisecondo prima della Balena)
        address[] memory pathBuy = new address[](2);
        pathBuy[0] = tokenIn;
        pathBuy[1] = tokenOut;
        
        IUniswapV2Router(router).swapExactTokensForTokens(
            amountIn,
            0, // MinOut calcolato off-chain dal server Python in millisecondi
            pathBuy,
            address(this),
            block.timestamp + 120
        );

        // 3. FASE DI BACK-RUN (Vendiamo subito dopo che la Balena ha alzato il prezzo)
        uint256 amountToSell = IERC20(tokenOut).balanceOf(address(this));
        IERC20(tokenOut).approve(router, amountToSell);
        
        address[] memory pathSell = new address[](2);
        pathSell[0] = tokenOut;
        pathSell[1] = tokenIn;

        IUniswapV2Router(router).swapExactTokensForTokens(
            amountToSell,
            0,
            pathSell,
            address(this),
            block.timestamp + 120
        );

        // 4. VERIFICA RISCHIO ZERO (Circuit Breaker On-Chain)
        uint256 endBalance = IERC20(tokenIn).balanceOf(address(this));
        
        // Se non abbiamo guadagnato almeno il profitto minimo richiesto (piu' le gas fees),
        // annulliamo l'intera linea temporale. Come se l'attacco non fosse mai avvenuto.
        require(endBalance >= startBalance + minProfitExpected, "ATTACCO FALLITO: Profitto insufficiente. Esecuzione Revert Immediato.");
    }
    
    // Funzione per prelevare il bottino e murarlo nella Cassaforte (Vault)
    function sweepProfits(address token) external onlyOwner {
        uint256 bal = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, bal);
    }
}
