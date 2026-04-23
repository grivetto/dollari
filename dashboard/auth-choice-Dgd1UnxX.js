import { g as resolveDefaultModelForAgent } from "./model-selection-B6ao45a4.js";
import { c as ensureAuthProfileStore, n as listProfilesForProvider } from "./profiles-Cyg58FCO.js";
import { L as hasUsableCustomProviderApiKey, Ny as loadModelCatalog } from "./pi-embedded-CzQCqSlH.js";
import { c as resolveEnvApiKey } from "./provider-auth-input-DxjPWsSV.js";
import { t as buildProviderAuthRecoveryHint } from "./provider-auth-guidance-jLdnZwhv.js";
import { r as normalizeLegacyOnboardAuthChoice } from "./auth-choice-legacy-BxMo9ATY.js";
import { t as applyAuthChoiceLoadedPluginProvider } from "./provider-auth-choice-1V3Uu8iM.js";
import { n as applyAuthChoiceApiProviders, r as normalizeApiKeyTokenProviderAuthChoice } from "./provider-auth-choice-preference-GTyyR3LQ.js";
//#region src/commands/auth-choice.apply.oauth.ts
async function applyAuthChoiceOAuth(_params) {
	return null;
}
//#endregion
//#region src/commands/auth-choice.apply.ts
async function applyAuthChoice(params) {
	const normalizedProviderAuthChoice = normalizeApiKeyTokenProviderAuthChoice({
		authChoice: normalizeLegacyOnboardAuthChoice(params.authChoice) ?? params.authChoice,
		tokenProvider: params.opts?.tokenProvider,
		config: params.config,
		env: process.env
	});
	const normalizedParams = normalizedProviderAuthChoice === params.authChoice ? params : {
		...params,
		authChoice: normalizedProviderAuthChoice
	};
	const handlers = [
		applyAuthChoiceLoadedPluginProvider,
		applyAuthChoiceOAuth,
		applyAuthChoiceApiProviders
	];
	for (const handler of handlers) {
		const result = await handler(normalizedParams);
		if (result) return result;
	}
	return { config: normalizedParams.config };
}
//#endregion
//#region src/commands/auth-choice.model-check.ts
async function warnIfModelConfigLooksOff(config, prompter, options) {
	const ref = resolveDefaultModelForAgent({
		cfg: config,
		agentId: options?.agentId
	});
	const warnings = [];
	const catalog = await loadModelCatalog({
		config,
		useCache: false
	});
	if (catalog.length > 0) {
		if (!catalog.some((entry) => entry.provider === ref.provider && entry.id === ref.model)) warnings.push(`Model not found: ${ref.provider}/${ref.model}. Update agents.defaults.model or run /models list.`);
	}
	const hasProfile = listProfilesForProvider(ensureAuthProfileStore(options?.agentDir), ref.provider).length > 0;
	const envKey = resolveEnvApiKey(ref.provider);
	const hasCustomKey = hasUsableCustomProviderApiKey(config, ref.provider);
	if (!hasProfile && !envKey && !hasCustomKey) warnings.push(`No auth configured for provider "${ref.provider}". The agent may fail until credentials are added. ${buildProviderAuthRecoveryHint({
		provider: ref.provider,
		config,
		includeEnvVar: true
	})}`);
	if (warnings.length > 0) await prompter.note(warnings.join("\n"), "Model check");
}
//#endregion
export { applyAuthChoice as n, warnIfModelConfigLooksOff as t };
