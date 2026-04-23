import { C as KILOCODE_MODEL_CATALOG, g as KILOCODE_BASE_URL, i as MINIMAX_TEXT_MODEL_ORDER, r as MINIMAX_TEXT_MODEL_CATALOG, v as KILOCODE_DEFAULT_COST } from "./provider-model-minimax-XdwKeUOE.js";
import { A as TOGETHER_MODEL_CATALOG, E as discoverVeniceModels, F as buildSyntheticModelDefinition, G as buildHuggingfaceModelDefinition, H as discoverKilocodeModels, K as discoverHuggingfaceModels, M as SYNTHETIC_BASE_URL, P as SYNTHETIC_MODEL_CATALOG, S as VENICE_BASE_URL, U as HUGGINGFACE_BASE_URL, W as HUGGINGFACE_MODEL_CATALOG, _ as BYTEPLUS_BASE_URL, b as BYTEPLUS_MODEL_CATALOG, f as DOUBAO_BASE_URL, g as buildDoubaoModelDefinition, h as DOUBAO_MODEL_CATALOG, j as buildTogetherModelDefinition, k as TOGETHER_BASE_URL, m as DOUBAO_CODING_MODEL_CATALOG, n as VERCEL_AI_GATEWAY_BASE_URL, p as DOUBAO_CODING_BASE_URL, r as discoverVercelAiGatewayModels, v as BYTEPLUS_CODING_BASE_URL, x as buildBytePlusModelDefinition, y as BYTEPLUS_CODING_MODEL_CATALOG } from "./provider-models-DfgBoVpf.js";
import { i as resolveAnthropicVertexRegion } from "./anthropic-vertex-provider-e_sRR8fp.js";
//#region src/plugins/provider-catalog.ts
function findCatalogTemplate(params) {
	return params.templateIds.map((templateId) => params.entries.find((entry) => entry.provider.toLowerCase() === params.providerId.toLowerCase() && entry.id.toLowerCase() === templateId.toLowerCase())).find((entry) => entry !== void 0);
}
async function buildSingleProviderApiKeyCatalog(params) {
	const apiKey = params.ctx.resolveProviderApiKey(params.providerId).apiKey;
	if (!apiKey) return null;
	const explicitProvider = params.allowExplicitBaseUrl ? params.ctx.config.models?.providers?.[params.providerId] : void 0;
	const explicitBaseUrl = typeof explicitProvider?.baseUrl === "string" ? explicitProvider.baseUrl.trim() : "";
	return { provider: {
		...await params.buildProvider(),
		...explicitBaseUrl ? { baseUrl: explicitBaseUrl } : {},
		apiKey
	} };
}
async function buildPairedProviderApiKeyCatalog(params) {
	const apiKey = params.ctx.resolveProviderApiKey(params.providerId).apiKey;
	if (!apiKey) return null;
	const providers = await params.buildProviders();
	return { providers: Object.fromEntries(Object.entries(providers).map(([id, provider]) => [id, {
		...provider,
		apiKey
	}])) };
}
//#endregion
//#region extensions/anthropic-vertex/provider-catalog.ts
const ANTHROPIC_VERTEX_DEFAULT_MODEL_ID = "claude-sonnet-4-6";
const ANTHROPIC_VERTEX_DEFAULT_CONTEXT_WINDOW = 1e6;
const GCP_VERTEX_CREDENTIALS_MARKER = "gcp-vertex-credentials";
function buildAnthropicVertexModel(params) {
	return {
		id: params.id,
		name: params.name,
		reasoning: params.reasoning,
		input: params.input,
		cost: params.cost,
		contextWindow: ANTHROPIC_VERTEX_DEFAULT_CONTEXT_WINDOW,
		maxTokens: params.maxTokens
	};
}
function buildAnthropicVertexCatalog() {
	return [buildAnthropicVertexModel({
		id: "claude-opus-4-6",
		name: "Claude Opus 4.6",
		reasoning: true,
		input: ["text", "image"],
		cost: {
			input: 5,
			output: 25,
			cacheRead: .5,
			cacheWrite: 6.25
		},
		maxTokens: 128e3
	}), buildAnthropicVertexModel({
		id: ANTHROPIC_VERTEX_DEFAULT_MODEL_ID,
		name: "Claude Sonnet 4.6",
		reasoning: true,
		input: ["text", "image"],
		cost: {
			input: 3,
			output: 15,
			cacheRead: .3,
			cacheWrite: 3.75
		},
		maxTokens: 128e3
	})];
}
function buildAnthropicVertexProvider(params) {
	const region = resolveAnthropicVertexRegion(params?.env);
	return {
		baseUrl: region.toLowerCase() === "global" ? "https://aiplatform.googleapis.com" : `https://${region}-aiplatform.googleapis.com`,
		api: "anthropic-messages",
		apiKey: GCP_VERTEX_CREDENTIALS_MARKER,
		models: buildAnthropicVertexCatalog()
	};
}
//#endregion
//#region extensions/byteplus/provider-catalog.ts
function buildBytePlusProvider() {
	return {
		baseUrl: BYTEPLUS_BASE_URL,
		api: "openai-completions",
		models: BYTEPLUS_MODEL_CATALOG.map(buildBytePlusModelDefinition)
	};
}
function buildBytePlusCodingProvider() {
	return {
		baseUrl: BYTEPLUS_CODING_BASE_URL,
		api: "openai-completions",
		models: BYTEPLUS_CODING_MODEL_CATALOG.map(buildBytePlusModelDefinition)
	};
}
//#endregion
//#region extensions/huggingface/provider-catalog.ts
async function buildHuggingfaceProvider(discoveryApiKey) {
	const resolvedSecret = discoveryApiKey?.trim() ?? "";
	return {
		baseUrl: HUGGINGFACE_BASE_URL,
		api: "openai-completions",
		models: resolvedSecret !== "" ? await discoverHuggingfaceModels(resolvedSecret) : HUGGINGFACE_MODEL_CATALOG.map(buildHuggingfaceModelDefinition)
	};
}
//#endregion
//#region extensions/kimi-coding/provider-catalog.ts
const KIMI_BASE_URL = "https://api.kimi.com/coding/";
const KIMI_CODING_USER_AGENT = "claude-code/0.1.0";
const KIMI_DEFAULT_MODEL_ID = "kimi-code";
const KIMI_LEGACY_MODEL_ID = "k2p5";
const KIMI_CODING_DEFAULT_CONTEXT_WINDOW = 262144;
const KIMI_CODING_DEFAULT_MAX_TOKENS = 32768;
const KIMI_CODING_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildKimiCodingProvider() {
	return {
		baseUrl: KIMI_BASE_URL,
		api: "anthropic-messages",
		headers: { "User-Agent": KIMI_CODING_USER_AGENT },
		models: [{
			id: KIMI_DEFAULT_MODEL_ID,
			name: "Kimi Code",
			reasoning: true,
			input: ["text", "image"],
			cost: KIMI_CODING_DEFAULT_COST,
			contextWindow: KIMI_CODING_DEFAULT_CONTEXT_WINDOW,
			maxTokens: KIMI_CODING_DEFAULT_MAX_TOKENS
		}, {
			id: KIMI_LEGACY_MODEL_ID,
			name: "Kimi Code (legacy model id)",
			reasoning: true,
			input: ["text", "image"],
			cost: KIMI_CODING_DEFAULT_COST,
			contextWindow: KIMI_CODING_DEFAULT_CONTEXT_WINDOW,
			maxTokens: KIMI_CODING_DEFAULT_MAX_TOKENS
		}]
	};
}
const KIMI_CODING_BASE_URL = KIMI_BASE_URL;
const KIMI_CODING_DEFAULT_MODEL_ID = KIMI_DEFAULT_MODEL_ID;
//#endregion
//#region extensions/kilocode/provider-catalog.ts
function buildKilocodeProvider() {
	return {
		baseUrl: KILOCODE_BASE_URL,
		api: "openai-completions",
		models: KILOCODE_MODEL_CATALOG.map((model) => ({
			id: model.id,
			name: model.name,
			reasoning: model.reasoning,
			input: model.input,
			cost: KILOCODE_DEFAULT_COST,
			contextWindow: model.contextWindow ?? 1e6,
			maxTokens: model.maxTokens ?? 128e3
		}))
	};
}
async function buildKilocodeProviderWithDiscovery() {
	return {
		baseUrl: KILOCODE_BASE_URL,
		api: "openai-completions",
		models: await discoverKilocodeModels()
	};
}
//#endregion
//#region extensions/minimax/provider-catalog.ts
const MINIMAX_PORTAL_BASE_URL = "https://api.minimax.io/anthropic";
const MINIMAX_DEFAULT_VISION_MODEL_ID = "MiniMax-VL-01";
const MINIMAX_DEFAULT_CONTEXT_WINDOW = 204800;
const MINIMAX_DEFAULT_MAX_TOKENS = 131072;
const MINIMAX_API_COST = {
	input: .3,
	output: 1.2,
	cacheRead: .06,
	cacheWrite: .375
};
function buildMinimaxModel(params) {
	return {
		id: params.id,
		name: params.name,
		reasoning: params.reasoning,
		input: params.input,
		cost: MINIMAX_API_COST,
		contextWindow: MINIMAX_DEFAULT_CONTEXT_WINDOW,
		maxTokens: MINIMAX_DEFAULT_MAX_TOKENS
	};
}
function buildMinimaxTextModel(params) {
	return buildMinimaxModel({
		...params,
		input: ["text"]
	});
}
function buildMinimaxCatalog() {
	return [buildMinimaxModel({
		id: MINIMAX_DEFAULT_VISION_MODEL_ID,
		name: "MiniMax VL 01",
		reasoning: false,
		input: ["text", "image"]
	}), ...MINIMAX_TEXT_MODEL_ORDER.map((id) => {
		const model = MINIMAX_TEXT_MODEL_CATALOG[id];
		return buildMinimaxTextModel({
			id,
			name: model.name,
			reasoning: model.reasoning
		});
	})];
}
function buildMinimaxProvider() {
	return {
		baseUrl: MINIMAX_PORTAL_BASE_URL,
		api: "anthropic-messages",
		authHeader: true,
		models: buildMinimaxCatalog()
	};
}
function buildMinimaxPortalProvider() {
	return {
		baseUrl: MINIMAX_PORTAL_BASE_URL,
		api: "anthropic-messages",
		authHeader: true,
		models: buildMinimaxCatalog()
	};
}
//#endregion
//#region extensions/modelstudio/provider-catalog.ts
const MODELSTUDIO_BASE_URL = "https://coding-intl.dashscope.aliyuncs.com/v1";
const MODELSTUDIO_DEFAULT_MODEL_ID = "qwen3.5-plus";
const MODELSTUDIO_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
const MODELSTUDIO_MODEL_CATALOG = [
	{
		id: "qwen3.5-plus",
		name: "qwen3.5-plus",
		reasoning: false,
		input: ["text", "image"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 1e6,
		maxTokens: 65536
	},
	{
		id: "qwen3-max-2026-01-23",
		name: "qwen3-max-2026-01-23",
		reasoning: false,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 262144,
		maxTokens: 65536
	},
	{
		id: "qwen3-coder-next",
		name: "qwen3-coder-next",
		reasoning: false,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 262144,
		maxTokens: 65536
	},
	{
		id: "qwen3-coder-plus",
		name: "qwen3-coder-plus",
		reasoning: false,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 1e6,
		maxTokens: 65536
	},
	{
		id: "MiniMax-M2.5",
		name: "MiniMax-M2.5",
		reasoning: true,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 1e6,
		maxTokens: 65536
	},
	{
		id: "glm-5",
		name: "glm-5",
		reasoning: false,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 202752,
		maxTokens: 16384
	},
	{
		id: "glm-4.7",
		name: "glm-4.7",
		reasoning: false,
		input: ["text"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 202752,
		maxTokens: 16384
	},
	{
		id: "kimi-k2.5",
		name: "kimi-k2.5",
		reasoning: false,
		input: ["text", "image"],
		cost: MODELSTUDIO_DEFAULT_COST,
		contextWindow: 262144,
		maxTokens: 32768
	}
];
function buildModelStudioProvider() {
	return {
		baseUrl: MODELSTUDIO_BASE_URL,
		api: "openai-completions",
		models: MODELSTUDIO_MODEL_CATALOG.map((model) => ({ ...model }))
	};
}
//#endregion
//#region extensions/moonshot/provider-catalog.ts
const MOONSHOT_BASE_URL = "https://api.moonshot.ai/v1";
const MOONSHOT_DEFAULT_MODEL_ID = "kimi-k2.5";
const MOONSHOT_DEFAULT_CONTEXT_WINDOW = 262144;
const MOONSHOT_DEFAULT_MAX_TOKENS = 262144;
const MOONSHOT_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
const MOONSHOT_MODEL_CATALOG = [
	{
		id: "kimi-k2.5",
		name: "Kimi K2.5",
		reasoning: false,
		input: ["text", "image"],
		cost: MOONSHOT_DEFAULT_COST,
		contextWindow: MOONSHOT_DEFAULT_CONTEXT_WINDOW,
		maxTokens: MOONSHOT_DEFAULT_MAX_TOKENS
	},
	{
		id: "kimi-k2-thinking",
		name: "Kimi K2 Thinking",
		reasoning: true,
		input: ["text"],
		cost: MOONSHOT_DEFAULT_COST,
		contextWindow: 262144,
		maxTokens: 262144
	},
	{
		id: "kimi-k2-thinking-turbo",
		name: "Kimi K2 Thinking Turbo",
		reasoning: true,
		input: ["text"],
		cost: MOONSHOT_DEFAULT_COST,
		contextWindow: 262144,
		maxTokens: 262144
	},
	{
		id: "kimi-k2-turbo",
		name: "Kimi K2 Turbo",
		reasoning: false,
		input: ["text"],
		cost: MOONSHOT_DEFAULT_COST,
		contextWindow: 256e3,
		maxTokens: 16384
	}
];
function buildMoonshotProvider() {
	return {
		baseUrl: MOONSHOT_BASE_URL,
		api: "openai-completions",
		models: MOONSHOT_MODEL_CATALOG.map((model) => ({
			...model,
			input: [...model.input]
		}))
	};
}
//#endregion
//#region extensions/nvidia/provider-catalog.ts
const NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1";
const NVIDIA_DEFAULT_MODEL_ID = "nvidia/llama-3.1-nemotron-70b-instruct";
const NVIDIA_DEFAULT_CONTEXT_WINDOW = 131072;
const NVIDIA_DEFAULT_MAX_TOKENS = 4096;
const NVIDIA_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildNvidiaProvider() {
	return {
		baseUrl: NVIDIA_BASE_URL,
		api: "openai-completions",
		models: [
			{
				id: NVIDIA_DEFAULT_MODEL_ID,
				name: "NVIDIA Llama 3.1 Nemotron 70B Instruct",
				reasoning: false,
				input: ["text"],
				cost: NVIDIA_DEFAULT_COST,
				contextWindow: NVIDIA_DEFAULT_CONTEXT_WINDOW,
				maxTokens: NVIDIA_DEFAULT_MAX_TOKENS
			},
			{
				id: "meta/llama-3.3-70b-instruct",
				name: "Meta Llama 3.3 70B Instruct",
				reasoning: false,
				input: ["text"],
				cost: NVIDIA_DEFAULT_COST,
				contextWindow: 131072,
				maxTokens: 4096
			},
			{
				id: "nvidia/mistral-nemo-minitron-8b-8k-instruct",
				name: "NVIDIA Mistral NeMo Minitron 8B Instruct",
				reasoning: false,
				input: ["text"],
				cost: NVIDIA_DEFAULT_COST,
				contextWindow: 8192,
				maxTokens: 2048
			}
		]
	};
}
//#endregion
//#region extensions/openai/openai-codex-catalog.ts
const OPENAI_CODEX_BASE_URL = "https://chatgpt.com/backend-api";
function buildOpenAICodexProvider() {
	return {
		baseUrl: OPENAI_CODEX_BASE_URL,
		api: "openai-codex-responses",
		models: []
	};
}
//#endregion
//#region extensions/openrouter/provider-catalog.ts
const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1";
const OPENROUTER_DEFAULT_MODEL_ID = "auto";
const OPENROUTER_DEFAULT_CONTEXT_WINDOW = 2e5;
const OPENROUTER_DEFAULT_MAX_TOKENS = 8192;
const OPENROUTER_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildOpenrouterProvider() {
	return {
		baseUrl: OPENROUTER_BASE_URL,
		api: "openai-completions",
		models: [
			{
				id: OPENROUTER_DEFAULT_MODEL_ID,
				name: "OpenRouter Auto",
				reasoning: false,
				input: ["text", "image"],
				cost: OPENROUTER_DEFAULT_COST,
				contextWindow: OPENROUTER_DEFAULT_CONTEXT_WINDOW,
				maxTokens: OPENROUTER_DEFAULT_MAX_TOKENS
			},
			{
				id: "openrouter/hunter-alpha",
				name: "Hunter Alpha",
				reasoning: true,
				input: ["text"],
				cost: OPENROUTER_DEFAULT_COST,
				contextWindow: 1048576,
				maxTokens: 65536
			},
			{
				id: "openrouter/healer-alpha",
				name: "Healer Alpha",
				reasoning: true,
				input: ["text", "image"],
				cost: OPENROUTER_DEFAULT_COST,
				contextWindow: 262144,
				maxTokens: 65536
			}
		]
	};
}
//#endregion
//#region extensions/qianfan/provider-catalog.ts
const QIANFAN_BASE_URL = "https://qianfan.baidubce.com/v2";
const QIANFAN_DEFAULT_MODEL_ID = "deepseek-v3.2";
const QIANFAN_DEFAULT_CONTEXT_WINDOW = 98304;
const QIANFAN_DEFAULT_MAX_TOKENS = 32768;
const QIANFAN_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildQianfanProvider() {
	return {
		baseUrl: QIANFAN_BASE_URL,
		api: "openai-completions",
		models: [{
			id: QIANFAN_DEFAULT_MODEL_ID,
			name: "DEEPSEEK V3.2",
			reasoning: true,
			input: ["text"],
			cost: QIANFAN_DEFAULT_COST,
			contextWindow: QIANFAN_DEFAULT_CONTEXT_WINDOW,
			maxTokens: QIANFAN_DEFAULT_MAX_TOKENS
		}, {
			id: "ernie-5.0-thinking-preview",
			name: "ERNIE-5.0-Thinking-Preview",
			reasoning: true,
			input: ["text", "image"],
			cost: QIANFAN_DEFAULT_COST,
			contextWindow: 119e3,
			maxTokens: 64e3
		}]
	};
}
//#endregion
//#region extensions/qwen-portal-auth/provider-catalog.ts
const QWEN_PORTAL_BASE_URL = "https://portal.qwen.ai/v1";
const QWEN_PORTAL_DEFAULT_CONTEXT_WINDOW = 128e3;
const QWEN_PORTAL_DEFAULT_MAX_TOKENS = 8192;
const QWEN_PORTAL_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildModelDefinition(params) {
	return {
		id: params.id,
		name: params.name,
		reasoning: false,
		input: params.input,
		cost: QWEN_PORTAL_DEFAULT_COST,
		contextWindow: QWEN_PORTAL_DEFAULT_CONTEXT_WINDOW,
		maxTokens: QWEN_PORTAL_DEFAULT_MAX_TOKENS
	};
}
function buildQwenPortalProvider() {
	return {
		baseUrl: QWEN_PORTAL_BASE_URL,
		api: "openai-completions",
		models: [buildModelDefinition({
			id: "coder-model",
			name: "Qwen Coder",
			input: ["text"]
		}), buildModelDefinition({
			id: "vision-model",
			name: "Qwen Vision",
			input: ["text", "image"]
		})]
	};
}
//#endregion
//#region extensions/synthetic/provider-catalog.ts
function buildSyntheticProvider() {
	return {
		baseUrl: SYNTHETIC_BASE_URL,
		api: "anthropic-messages",
		models: SYNTHETIC_MODEL_CATALOG.map(buildSyntheticModelDefinition)
	};
}
//#endregion
//#region extensions/together/provider-catalog.ts
function buildTogetherProvider() {
	return {
		baseUrl: TOGETHER_BASE_URL,
		api: "openai-completions",
		models: TOGETHER_MODEL_CATALOG.map(buildTogetherModelDefinition)
	};
}
//#endregion
//#region extensions/venice/provider-catalog.ts
async function buildVeniceProvider() {
	return {
		baseUrl: VENICE_BASE_URL,
		api: "openai-completions",
		models: await discoverVeniceModels()
	};
}
//#endregion
//#region extensions/vercel-ai-gateway/provider-catalog.ts
async function buildVercelAiGatewayProvider() {
	return {
		baseUrl: VERCEL_AI_GATEWAY_BASE_URL,
		api: "anthropic-messages",
		models: await discoverVercelAiGatewayModels()
	};
}
//#endregion
//#region extensions/volcengine/provider-catalog.ts
function buildDoubaoProvider() {
	return {
		baseUrl: DOUBAO_BASE_URL,
		api: "openai-completions",
		models: DOUBAO_MODEL_CATALOG.map(buildDoubaoModelDefinition)
	};
}
function buildDoubaoCodingProvider() {
	return {
		baseUrl: DOUBAO_CODING_BASE_URL,
		api: "openai-completions",
		models: DOUBAO_CODING_MODEL_CATALOG.map(buildDoubaoModelDefinition)
	};
}
//#endregion
//#region extensions/xiaomi/provider-catalog.ts
const XIAOMI_BASE_URL = "https://api.xiaomimimo.com/v1";
const XIAOMI_DEFAULT_MODEL_ID = "mimo-v2-flash";
const XIAOMI_DEFAULT_CONTEXT_WINDOW = 262144;
const XIAOMI_DEFAULT_MAX_TOKENS = 8192;
const XIAOMI_DEFAULT_COST = {
	input: 0,
	output: 0,
	cacheRead: 0,
	cacheWrite: 0
};
function buildXiaomiProvider() {
	return {
		baseUrl: XIAOMI_BASE_URL,
		api: "openai-completions",
		models: [
			{
				id: XIAOMI_DEFAULT_MODEL_ID,
				name: "Xiaomi MiMo V2 Flash",
				reasoning: false,
				input: ["text"],
				cost: XIAOMI_DEFAULT_COST,
				contextWindow: XIAOMI_DEFAULT_CONTEXT_WINDOW,
				maxTokens: XIAOMI_DEFAULT_MAX_TOKENS
			},
			{
				id: "mimo-v2-pro",
				name: "Xiaomi MiMo V2 Pro",
				reasoning: true,
				input: ["text"],
				cost: XIAOMI_DEFAULT_COST,
				contextWindow: 1048576,
				maxTokens: 32e3
			},
			{
				id: "mimo-v2-omni",
				name: "Xiaomi MiMo V2 Omni",
				reasoning: true,
				input: ["text", "image"],
				cost: XIAOMI_DEFAULT_COST,
				contextWindow: XIAOMI_DEFAULT_CONTEXT_WINDOW,
				maxTokens: 32e3
			}
		]
	};
}
//#endregion
export { buildHuggingfaceProvider as A, buildMinimaxPortalProvider as C, KIMI_CODING_BASE_URL as D, buildKilocodeProviderWithDiscovery as E, buildPairedProviderApiKeyCatalog as F, buildSingleProviderApiKeyCatalog as I, findCatalogTemplate as L, buildBytePlusProvider as M, ANTHROPIC_VERTEX_DEFAULT_MODEL_ID as N, KIMI_CODING_DEFAULT_MODEL_ID as O, buildAnthropicVertexProvider as P, buildModelStudioProvider as S, buildKilocodeProvider as T, MOONSHOT_BASE_URL as _, buildVercelAiGatewayProvider as a, MODELSTUDIO_BASE_URL as b, buildSyntheticProvider as c, QIANFAN_BASE_URL as d, QIANFAN_DEFAULT_MODEL_ID as f, buildNvidiaProvider as g, buildOpenAICodexProvider as h, buildDoubaoProvider as i, buildBytePlusCodingProvider as j, buildKimiCodingProvider as k, QWEN_PORTAL_BASE_URL as l, buildOpenrouterProvider as m, buildXiaomiProvider as n, buildVeniceProvider as o, buildQianfanProvider as p, buildDoubaoCodingProvider as r, buildTogetherProvider as s, XIAOMI_DEFAULT_MODEL_ID as t, buildQwenPortalProvider as u, MOONSHOT_DEFAULT_MODEL_ID as v, buildMinimaxProvider as w, MODELSTUDIO_DEFAULT_MODEL_ID as x, buildMoonshotProvider as y };
