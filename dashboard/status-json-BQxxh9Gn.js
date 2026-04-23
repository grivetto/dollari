import "./redact-BDinS1q9.js";
import "./errors-BxyFnvP3.js";
import { h as loggingState } from "./logger-kwZIqwuw.js";
import { _ as resolveStateDir, o as resolveConfigPath } from "./paths-ViKUYWUK.js";
import "./tmp-openclaw-dir-idKIOMmb.js";
import "./theme-CdOoMzRk.js";
import "./globals-DBUMOBZ8.js";
import { h as writeRuntimeJson } from "./subsystem-DISldKSB.js";
import "./ansi-BEJF8NKS.js";
import "./boolean-C3GkJetE.js";
import "./env-Dnra1IpT.js";
import "./utils-CS0Ikux6.js";
import "./boundary-path-Dm0QJ7-y.js";
import "./boundary-file-read-DcZxlWD8.js";
import "./logger-BmpSCz93.js";
import { r as runExec } from "./exec-B5_AYfQG.js";
import "./workspace-D4K6QX9X.js";
import "./agent-scope-DoT9OqaV.js";
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
import "./audit-fs-CEN00XrG.js";
import "./resolve-uXRpJb-M.js";
import "./tailnet-BVzEE6AW.js";
import "./net-Dk658jWW.js";
import "./credentials-CO55Yx_u.js";
import "./message-channel-DUrzQUcI.js";
import "./paths-BPfguEtH.js";
import "./method-scopes-BWG4Q18M.js";
import "./call-VZCb020X.js";
import "./control-ui-shared-SxKiMaO4.js";
import "./ports-lsof-C3NOmuKA.js";
import "./restart-stale-pids-CQbYk99d.js";
import "./runtime-parse-CQJ3sqUO.js";
import "./launchd-DDdD9wdn.js";
import "./service-s9kmDqmL.js";
import "./ports-CQIuVpXl.js";
import "./systemd-CLf_Dm5l.js";
import "./probe-D_QJRkwc.js";
import "./probe-auth-mN67ThXX.js";
import "./heartbeat-FZaB85hC.js";
import "./system-events-D9mayVHC.js";
import { n as hasPotentialConfiguredChannels } from "./config-presence-CovoxGn8.js";
import { a as resolveSharedMemoryStatusSnapshot, c as getNodeDaemonStatusSummary, h as pickGatewaySelfPresence, i as resolveMemoryPluginStatus, m as resolveOsSummary, n as buildTailscaleHttpsUrl, o as getAgentLocalStatuses, r as resolveGatewayProbeSnapshot, s as getDaemonStatusSummary, t as getStatusSummary } from "./status.summary-DIPdKcC5.js";
import "./heartbeat-summary-E6ZOkXBo.js";
import { h as resolveUpdateChannelDisplay, p as normalizeUpdateChannel } from "./update-check-2WnATJeU.js";
import "./node-service-13PfEqf2.js";
import { r as getUpdateCheckResult } from "./status.update-Dat8Dv2g.js";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";
//#region src/commands/status.scan.fast-json.ts
let pluginRegistryModulePromise;
let configIoModulePromise;
let commandSecretTargetsModulePromise;
let commandSecretGatewayModulePromise;
let memorySearchModulePromise;
let statusScanDepsRuntimeModulePromise;
function loadPluginRegistryModule() {
	pluginRegistryModulePromise ??= import("./plugin-registry-BplrWWOt.js");
	return pluginRegistryModulePromise;
}
function loadConfigIoModule() {
	configIoModulePromise ??= import("./io-BnxnFMfJ.js");
	return configIoModulePromise;
}
function loadCommandSecretTargetsModule() {
	commandSecretTargetsModulePromise ??= import("./command-secret-targets-ChvWPEc7.js");
	return commandSecretTargetsModulePromise;
}
function loadCommandSecretGatewayModule() {
	commandSecretGatewayModulePromise ??= import("./command-secret-gateway-KXp5HryD.js");
	return commandSecretGatewayModulePromise;
}
function loadMemorySearchModule() {
	memorySearchModulePromise ??= import("./memory-search-thLdyfQp.js");
	return memorySearchModulePromise;
}
function loadStatusScanDepsRuntimeModule() {
	statusScanDepsRuntimeModulePromise ??= import("./status.scan.deps.runtime-BPgdSFIJ.js");
	return statusScanDepsRuntimeModulePromise;
}
function shouldSkipMissingConfigFastPath() {
	return process.env.VITEST === "true" || process.env.VITEST_POOL_ID !== void 0 || false;
}
function isMissingConfigColdStart() {
	return !shouldSkipMissingConfigFastPath() && !existsSync(resolveConfigPath(process.env));
}
function buildColdStartUpdateResult() {
	return {
		root: null,
		installKind: "unknown",
		packageManager: "unknown"
	};
}
function resolveDefaultMemoryStorePath(agentId) {
	return path.join(resolveStateDir(process.env, os.homedir), "memory", `${agentId}.sqlite`);
}
async function resolveMemoryStatusSnapshot(params) {
	const { resolveMemorySearchConfig } = await loadMemorySearchModule();
	const { getMemorySearchManager } = await loadStatusScanDepsRuntimeModule();
	return await resolveSharedMemoryStatusSnapshot({
		cfg: params.cfg,
		agentStatus: params.agentStatus,
		memoryPlugin: params.memoryPlugin,
		resolveMemoryConfig: resolveMemorySearchConfig,
		getMemorySearchManager,
		requireDefaultStore: resolveDefaultMemoryStorePath
	});
}
async function readStatusSourceConfig() {
	if (!shouldSkipMissingConfigFastPath() && !existsSync(resolveConfigPath(process.env))) return {};
	const { readBestEffortConfig } = await loadConfigIoModule();
	return await readBestEffortConfig();
}
async function resolveStatusConfig(params) {
	if (!shouldSkipMissingConfigFastPath() && !existsSync(resolveConfigPath(process.env))) return {
		resolvedConfig: params.sourceConfig,
		diagnostics: []
	};
	const [{ resolveCommandSecretRefsViaGateway }, { getStatusCommandSecretTargetIds }] = await Promise.all([loadCommandSecretGatewayModule(), loadCommandSecretTargetsModule()]);
	return await resolveCommandSecretRefsViaGateway({
		config: params.sourceConfig,
		commandName: params.commandName,
		targetIds: getStatusCommandSecretTargetIds(),
		mode: "read_only_status"
	});
}
async function scanStatusJsonFast(opts, _runtime) {
	const coldStart = isMissingConfigColdStart();
	const loadedRaw = await readStatusSourceConfig();
	const { resolvedConfig: cfg, diagnostics: secretDiagnostics } = await resolveStatusConfig({
		sourceConfig: loadedRaw,
		commandName: "status --json"
	});
	const hasConfiguredChannels = hasPotentialConfiguredChannels(cfg);
	if (hasConfiguredChannels) {
		const { ensurePluginRegistryLoaded } = await loadPluginRegistryModule();
		const prev = loggingState.forceConsoleToStderr;
		loggingState.forceConsoleToStderr = true;
		try {
			ensurePluginRegistryLoaded({ scope: "configured-channels" });
		} finally {
			loggingState.forceConsoleToStderr = prev;
		}
	}
	const osSummary = resolveOsSummary();
	const tailscaleMode = cfg.gateway?.tailscale?.mode ?? "off";
	const updateTimeoutMs = opts.all ? 6500 : 2500;
	const skipColdStartNetworkChecks = coldStart && !hasConfiguredChannels && opts.all !== true;
	const updatePromise = skipColdStartNetworkChecks ? Promise.resolve(buildColdStartUpdateResult()) : getUpdateCheckResult({
		timeoutMs: updateTimeoutMs,
		fetchGit: true,
		includeRegistry: true
	});
	const agentStatusPromise = getAgentLocalStatuses(cfg);
	const summaryPromise = getStatusSummary({
		config: cfg,
		sourceConfig: loadedRaw
	});
	const tailscaleDnsPromise = tailscaleMode === "off" ? Promise.resolve(null) : loadStatusScanDepsRuntimeModule().then(({ getTailnetHostname }) => getTailnetHostname((cmd, args) => runExec(cmd, args, {
		timeoutMs: 1200,
		maxBuffer: 2e5
	}))).catch(() => null);
	const gatewayProbePromise = resolveGatewayProbeSnapshot({
		cfg,
		opts: {
			...opts,
			...skipColdStartNetworkChecks ? { skipProbe: true } : {}
		}
	});
	const [tailscaleDns, update, agentStatus, gatewaySnapshot, summary] = await Promise.all([
		tailscaleDnsPromise,
		updatePromise,
		agentStatusPromise,
		gatewayProbePromise,
		summaryPromise
	]);
	const tailscaleHttpsUrl = buildTailscaleHttpsUrl({
		tailscaleMode,
		tailscaleDns,
		controlUiBasePath: cfg.gateway?.controlUi?.basePath
	});
	const { gatewayConnection, remoteUrlMissing, gatewayMode, gatewayProbeAuth, gatewayProbeAuthWarning, gatewayProbe } = gatewaySnapshot;
	const gatewayReachable = gatewayProbe?.ok === true;
	const gatewaySelf = gatewayProbe?.presence ? pickGatewaySelfPresence(gatewayProbe.presence) : null;
	const memoryPlugin = resolveMemoryPluginStatus(cfg);
	return {
		cfg,
		sourceConfig: loadedRaw,
		secretDiagnostics,
		osSummary,
		tailscaleMode,
		tailscaleDns,
		tailscaleHttpsUrl,
		update,
		gatewayConnection,
		remoteUrlMissing,
		gatewayMode,
		gatewayProbeAuth,
		gatewayProbeAuthWarning,
		gatewayProbe,
		gatewayReachable,
		gatewaySelf,
		channelIssues: [],
		agentStatus,
		channels: {
			rows: [],
			details: []
		},
		summary,
		memory: opts.all ? await resolveMemoryStatusSnapshot({
			cfg,
			agentStatus,
			memoryPlugin
		}) : null,
		memoryPlugin,
		pluginCompatibility: []
	};
}
//#endregion
//#region src/commands/status-json.ts
let providerUsagePromise;
let securityAuditModulePromise;
let gatewayCallModulePromise;
function loadProviderUsage() {
	providerUsagePromise ??= import("./provider-usage-DsX-ZfZP.js");
	return providerUsagePromise;
}
function loadSecurityAuditModule() {
	securityAuditModulePromise ??= import("./audit.runtime-BIagqEgo.js");
	return securityAuditModulePromise;
}
function loadGatewayCallModule() {
	gatewayCallModulePromise ??= import("./call-XjCI0CPk.js");
	return gatewayCallModulePromise;
}
async function statusJsonCommand(opts, runtime) {
	const scan = await scanStatusJsonFast({
		timeoutMs: opts.timeoutMs,
		all: opts.all
	}, runtime);
	const securityAudit = opts.all ? await loadSecurityAuditModule().then(({ runSecurityAudit }) => runSecurityAudit({
		config: scan.cfg,
		sourceConfig: scan.sourceConfig,
		deep: false,
		includeFilesystem: true,
		includeChannelSecurity: true
	})) : void 0;
	const usage = opts.usage ? await loadProviderUsage().then(({ loadProviderUsageSummary }) => loadProviderUsageSummary({ timeoutMs: opts.timeoutMs })) : void 0;
	const gatewayCall = opts.deep ? await loadGatewayCallModule().then((mod) => mod.callGateway) : null;
	const health = gatewayCall != null ? await gatewayCall({
		method: "health",
		params: { probe: true },
		timeoutMs: opts.timeoutMs,
		config: scan.cfg
	}).catch(() => void 0) : void 0;
	const lastHeartbeat = gatewayCall != null && scan.gatewayReachable ? await gatewayCall({
		method: "last-heartbeat",
		params: {},
		timeoutMs: opts.timeoutMs,
		config: scan.cfg
	}).catch(() => null) : null;
	const [daemon, nodeDaemon] = await Promise.all([getDaemonStatusSummary(), getNodeDaemonStatusSummary()]);
	const channelInfo = resolveUpdateChannelDisplay({
		configChannel: normalizeUpdateChannel(scan.cfg.update?.channel),
		installKind: scan.update.installKind,
		gitTag: scan.update.git?.tag ?? null,
		gitBranch: scan.update.git?.branch ?? null
	});
	writeRuntimeJson(runtime, {
		...scan.summary,
		os: scan.osSummary,
		update: scan.update,
		updateChannel: channelInfo.channel,
		updateChannelSource: channelInfo.source,
		memory: scan.memory,
		memoryPlugin: scan.memoryPlugin,
		gateway: {
			mode: scan.gatewayMode,
			url: scan.gatewayConnection.url,
			urlSource: scan.gatewayConnection.urlSource,
			misconfigured: scan.remoteUrlMissing,
			reachable: scan.gatewayReachable,
			connectLatencyMs: scan.gatewayProbe?.connectLatencyMs ?? null,
			self: scan.gatewaySelf,
			error: scan.gatewayProbe?.error ?? null,
			authWarning: scan.gatewayProbeAuthWarning ?? null
		},
		gatewayService: daemon,
		nodeService: nodeDaemon,
		agents: scan.agentStatus,
		secretDiagnostics: scan.secretDiagnostics,
		...securityAudit ? { securityAudit } : {},
		...health || usage || lastHeartbeat ? {
			health,
			usage,
			lastHeartbeat
		} : {}
	});
}
//#endregion
export { statusJsonCommand };
