import "./logger-kwZIqwuw.js";
import "./paths-ViKUYWUK.js";
import "./tmp-openclaw-dir-idKIOMmb.js";
import "./theme-CdOoMzRk.js";
import "./globals-DBUMOBZ8.js";
import "./subsystem-DISldKSB.js";
import "./ansi-BEJF8NKS.js";
import "./boolean-C3GkJetE.js";
import "./env-Dnra1IpT.js";
import "./utils-CS0Ikux6.js";
import "./paths-BFl2-hCf.js";
import "./auth-profiles-CVFpgeL-.js";
import "./boundary-path-Dm0QJ7-y.js";
import "./boundary-file-read-DcZxlWD8.js";
import "./logger-BmpSCz93.js";
import "./exec-B5_AYfQG.js";
import "./workspace-D4K6QX9X.js";
import { a as resolveAgentDir, m as resolveDefaultAgentId, v as resolveSessionAgentId } from "./agent-scope-DoT9OqaV.js";
import "./defaults-CyhDhBAD.js";
import "./model-selection-B6ao45a4.js";
import "./io-cPs4dU7X.js";
import "./host-env-security-DEKL50zA.js";
import "./shell-env-BKuVS72k.js";
import "./safe-text-DIDDfQyI.js";
import "./version-BpHNkJed.js";
import "./env-substitution-B8NFl2Jd.js";
import "./includes-CCK6fRRs.js";
import "./zod-schema.providers-core-DLPfih2y.js";
import "./legacy-web-search-CTvir-Bl.js";
import "./registry-xyHjVLxh.js";
import "./config-state-Dx9-tLPS.js";
import "./min-host-version-xbc6BJ_K.js";
import "./manifest-registry-D5E7Gxgl.js";
import "./runtime-guard-QGt7fm0l.js";
import "./avatar-policy-DVf9B9eu.js";
import "./ip-DIgtRRTW.js";
import "./zod-schema.agent-runtime-C659GPl8.js";
import "./zod-schema.core-yLTNC4-K.js";
import "./config-CB4aYWqd.js";
import "./file-lock-DoKDW8jx.js";
import "./audit-fs-CEN00XrG.js";
import "./resolve-uXRpJb-M.js";
import "./profiles-Cyg58FCO.js";
import "./message-channel-DUrzQUcI.js";
import { l as updateSessionStore } from "./store-D_eNuCKK.js";
import "./runtime-C8dQugND.js";
import "./plugins-DGdgUNcN.js";
import "./paths-BPfguEtH.js";
import "./session-write-lock-bE2vQvvO.js";
import "./thinking-CSfcimRZ.js";
import { d as lookupCachedContextTokens, t as applyVerboseOverride } from "./level-overrides-DoL5t4pG.js";
import { t as applyModelOverrideToSessionEntry } from "./model-overrides-CrDQFrUM.js";
import { r as enqueueSystemEvent } from "./system-events-D9mayVHC.js";
import { c as resolveModelSelectionFromDirective, n as enqueueModeSwitchEvents, t as canPersistInternalExecDirective } from "./directive-handling.shared-CNxULHMr.js";
//#region src/auto-reply/reply/directive-handling.persist.ts
async function persistInlineDirectives(params) {
	const { directives, cfg, sessionEntry, sessionStore, sessionKey, storePath, elevatedEnabled, elevatedAllowed, defaultProvider, defaultModel, aliasIndex, allowedModelKeys, initialModelLabel, formatModelSwitchEvent, agentCfg } = params;
	let { provider, model } = params;
	const allowInternalExecPersistence = canPersistInternalExecDirective({
		surface: params.surface,
		gatewayClientScopes: params.gatewayClientScopes
	});
	const activeAgentId = sessionKey ? resolveSessionAgentId({
		sessionKey,
		config: cfg
	}) : resolveDefaultAgentId(cfg);
	const agentDir = params.agentDir ?? resolveAgentDir(cfg, activeAgentId);
	if (sessionEntry && sessionStore && sessionKey) {
		const prevElevatedLevel = sessionEntry.elevatedLevel ?? agentCfg?.elevatedDefault ?? (elevatedAllowed ? "on" : "off");
		const prevReasoningLevel = sessionEntry.reasoningLevel ?? "off";
		let elevatedChanged = directives.hasElevatedDirective && directives.elevatedLevel !== void 0 && elevatedEnabled && elevatedAllowed;
		let reasoningChanged = directives.hasReasoningDirective && directives.reasoningLevel !== void 0;
		let updated = false;
		if (directives.hasThinkDirective && directives.thinkLevel) {
			sessionEntry.thinkingLevel = directives.thinkLevel;
			updated = true;
		}
		if (directives.hasVerboseDirective && directives.verboseLevel) {
			applyVerboseOverride(sessionEntry, directives.verboseLevel);
			updated = true;
		}
		if (directives.hasReasoningDirective && directives.reasoningLevel) {
			if (directives.reasoningLevel === "off") sessionEntry.reasoningLevel = "off";
			else sessionEntry.reasoningLevel = directives.reasoningLevel;
			reasoningChanged = reasoningChanged || directives.reasoningLevel !== prevReasoningLevel && directives.reasoningLevel !== void 0;
			updated = true;
		}
		if (directives.hasElevatedDirective && directives.elevatedLevel && elevatedEnabled && elevatedAllowed) {
			sessionEntry.elevatedLevel = directives.elevatedLevel;
			elevatedChanged = elevatedChanged || directives.elevatedLevel !== prevElevatedLevel && directives.elevatedLevel !== void 0;
			updated = true;
		}
		if (directives.hasExecDirective && directives.hasExecOptions && allowInternalExecPersistence) {
			if (directives.execHost) {
				sessionEntry.execHost = directives.execHost;
				updated = true;
			}
			if (directives.execSecurity) {
				sessionEntry.execSecurity = directives.execSecurity;
				updated = true;
			}
			if (directives.execAsk) {
				sessionEntry.execAsk = directives.execAsk;
				updated = true;
			}
			if (directives.execNode) {
				sessionEntry.execNode = directives.execNode;
				updated = true;
			}
		}
		const modelDirective = directives.hasModelDirective && params.effectiveModelDirective ? params.effectiveModelDirective : void 0;
		if (modelDirective) {
			const modelResolution = resolveModelSelectionFromDirective({
				directives: {
					...directives,
					hasModelDirective: true,
					rawModelDirective: modelDirective
				},
				cfg,
				agentDir,
				defaultProvider,
				defaultModel,
				aliasIndex,
				allowedModelKeys,
				allowedModelCatalog: [],
				provider
			});
			if (modelResolution.modelSelection) {
				const { updated: modelUpdated } = applyModelOverrideToSessionEntry({
					entry: sessionEntry,
					selection: modelResolution.modelSelection,
					profileOverride: modelResolution.profileOverride
				});
				provider = modelResolution.modelSelection.provider;
				model = modelResolution.modelSelection.model;
				const nextLabel = `${provider}/${model}`;
				if (nextLabel !== initialModelLabel) enqueueSystemEvent(formatModelSwitchEvent(nextLabel, modelResolution.modelSelection.alias), {
					sessionKey,
					contextKey: `model:${nextLabel}`
				});
				updated = updated || modelUpdated;
			}
		}
		if (directives.hasQueueDirective && directives.queueReset) {
			delete sessionEntry.queueMode;
			delete sessionEntry.queueDebounceMs;
			delete sessionEntry.queueCap;
			delete sessionEntry.queueDrop;
			updated = true;
		}
		if (updated) {
			sessionEntry.updatedAt = Date.now();
			sessionStore[sessionKey] = sessionEntry;
			if (storePath) await updateSessionStore(storePath, (store) => {
				store[sessionKey] = sessionEntry;
			});
			enqueueModeSwitchEvents({
				enqueueSystemEvent,
				sessionEntry,
				sessionKey,
				elevatedChanged,
				reasoningChanged
			});
		}
	}
	return {
		provider,
		model,
		contextTokens: agentCfg?.contextTokens ?? lookupCachedContextTokens(model) ?? 2e5
	};
}
//#endregion
export { persistInlineDirectives };
