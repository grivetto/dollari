import "../logger-kwZIqwuw.js";
import "../paths-ViKUYWUK.js";
import "../tmp-openclaw-dir-idKIOMmb.js";
import "../theme-CdOoMzRk.js";
import "../globals-DBUMOBZ8.js";
import "../subsystem-DISldKSB.js";
import "../ansi-BEJF8NKS.js";
import "../utils-CS0Ikux6.js";
import "../paths-BFl2-hCf.js";
import "../boundary-path-Dm0QJ7-y.js";
import "../boundary-file-read-DcZxlWD8.js";
import "../logger-BmpSCz93.js";
import "../exec-B5_AYfQG.js";
import "../workspace-D4K6QX9X.js";
import "../agent-scope-DoT9OqaV.js";
import "../model-selection-B6ao45a4.js";
import "../file-lock-DoKDW8jx.js";
import "../profiles-Cyg58FCO.js";
import "../provider-catalog-7bUKai5_.js";
import "../provider-env-vars-Bhzl_gIs.js";
import "../provider-model-minimax-XdwKeUOE.js";
import { c as VLLM_DEFAULT_API_KEY_ENV_VAR, d as VLLM_PROVIDER_LABEL, l as VLLM_DEFAULT_BASE_URL, u as VLLM_MODEL_PLACEHOLDER } from "../provider-models-DfgBoVpf.js";
import "../anthropic-vertex-provider-e_sRR8fp.js";
import { t as OLLAMA_DEFAULT_BASE_URL } from "../ollama-defaults--y6cuBln.js";
import { a as SELF_HOSTED_DEFAULT_COST, i as SELF_HOSTED_DEFAULT_CONTEXT_WINDOW, n as buildSglangProvider, o as SELF_HOSTED_DEFAULT_MAX_TOKENS, r as buildVllmProvider, t as buildOllamaProvider } from "../models-config.providers.discovery-Ch23kOpG.js";
import "../setup-binary-DXdzcWG_.js";
import "../provider-auth-helpers-BeqTsaJO.js";
import "../upsert-with-lock-B2QGUxoM.js";
import "../setup-browser-DBIhFnBs.js";
import { i as promptAndConfigureOllama, n as configureOllamaNonInteractive, r as ensureOllamaModelPulled, t as OLLAMA_DEFAULT_MODEL } from "../provider-ollama-setup-BRzHUBXb.js";
import { a as promptAndConfigureOpenAICompatibleSelfHostedProviderAuth, i as promptAndConfigureOpenAICompatibleSelfHostedProvider, n as configureOpenAICompatibleSelfHostedProviderNonInteractive, r as discoverOpenAICompatibleSelfHostedProvider, t as applyProviderDefaultModel } from "../provider-self-hosted-setup-CdR2owmR.js";
//#region src/plugins/provider-vllm-setup.ts
const VLLM_DEFAULT_CONTEXT_WINDOW = SELF_HOSTED_DEFAULT_CONTEXT_WINDOW;
const VLLM_DEFAULT_MAX_TOKENS = SELF_HOSTED_DEFAULT_MAX_TOKENS;
const VLLM_DEFAULT_COST = SELF_HOSTED_DEFAULT_COST;
async function promptAndConfigureVllm(params) {
	const result = await promptAndConfigureOpenAICompatibleSelfHostedProvider({
		cfg: params.cfg,
		prompter: params.prompter,
		providerId: "vllm",
		providerLabel: VLLM_PROVIDER_LABEL,
		defaultBaseUrl: VLLM_DEFAULT_BASE_URL,
		defaultApiKeyEnvVar: VLLM_DEFAULT_API_KEY_ENV_VAR,
		modelPlaceholder: VLLM_MODEL_PLACEHOLDER
	});
	return {
		config: result.config,
		modelId: result.modelId,
		modelRef: result.modelRef
	};
}
//#endregion
export { OLLAMA_DEFAULT_BASE_URL, OLLAMA_DEFAULT_MODEL, SELF_HOSTED_DEFAULT_CONTEXT_WINDOW, SELF_HOSTED_DEFAULT_COST, SELF_HOSTED_DEFAULT_MAX_TOKENS, VLLM_DEFAULT_BASE_URL, VLLM_DEFAULT_CONTEXT_WINDOW, VLLM_DEFAULT_COST, VLLM_DEFAULT_MAX_TOKENS, applyProviderDefaultModel, buildOllamaProvider, buildSglangProvider, buildVllmProvider, configureOllamaNonInteractive, configureOpenAICompatibleSelfHostedProviderNonInteractive, discoverOpenAICompatibleSelfHostedProvider, ensureOllamaModelPulled, promptAndConfigureOllama, promptAndConfigureOpenAICompatibleSelfHostedProvider, promptAndConfigureOpenAICompatibleSelfHostedProviderAuth, promptAndConfigureVllm };
