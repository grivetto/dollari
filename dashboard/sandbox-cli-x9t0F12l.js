import "./redact-BDinS1q9.js";
import "./errors-BxyFnvP3.js";
import "./logger-kwZIqwuw.js";
import "./paths-ViKUYWUK.js";
import "./tmp-openclaw-dir-idKIOMmb.js";
import { n as isRich, r as theme, t as colorize } from "./theme-CdOoMzRk.js";
import "./globals-DBUMOBZ8.js";
import { h as writeRuntimeJson, m as defaultRuntime } from "./subsystem-DISldKSB.js";
import "./ansi-BEJF8NKS.js";
import "./boolean-C3GkJetE.js";
import "./env-Dnra1IpT.js";
import "./utils-CS0Ikux6.js";
import { t as formatDocsLink } from "./links-8xRhWBQL.js";
import { T as parseAgentSessionKey, c as normalizeAgentId, l as normalizeMainKey, r as buildAgentMainSessionKey, u as resolveAgentIdFromSessionKey } from "./session-key-DAhnzjyr.js";
import "./boundary-path-Dm0QJ7-y.js";
import "./boundary-file-read-DcZxlWD8.js";
import "./logger-BmpSCz93.js";
import "./exec-B5_AYfQG.js";
import "./workspace-D4K6QX9X.js";
import { i as resolveAgentConfig } from "./agent-scope-DoT9OqaV.js";
import "./model-selection-B6ao45a4.js";
import { s as loadConfig } from "./io-cPs4dU7X.js";
import "./host-env-security-DEKL50zA.js";
import "./shell-env-BKuVS72k.js";
import "./safe-text-DIDDfQyI.js";
import "./version-BpHNkJed.js";
import "./env-substitution-B8NFl2Jd.js";
import "./includes-CCK6fRRs.js";
import "./zod-schema.providers-core-DLPfih2y.js";
import "./legacy-web-search-CTvir-Bl.js";
import { o as normalizeAnyChannelId } from "./registry-xyHjVLxh.js";
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
import { t as formatCliCommand } from "./command-format-DRptdHvm.js";
import "./tailscale-CSUwCuE9.js";
import "./tailnet-BVzEE6AW.js";
import "./net-Dk658jWW.js";
import "./auth-C_pTuZtn.js";
import "./credentials-CO55Yx_u.js";
import { t as INTERNAL_MESSAGE_CHANNEL } from "./message-channel-DUrzQUcI.js";
import { n as loadSessionStore } from "./store-D_eNuCKK.js";
import "./runtime-C8dQugND.js";
import "./plugins-DGdgUNcN.js";
import { i as resolveMainSessionKey, n as resolveAgentMainSessionKey } from "./main-session-Dw8Q-wqf.js";
import "./sessions-C8WesgCl.js";
import { l as resolveStorePath } from "./paths-BPfguEtH.js";
import "./session-write-lock-bE2vQvvO.js";
import "./ports-lsof-C3NOmuKA.js";
import "./ports-CQIuVpXl.js";
import { t as formatHelpExamples } from "./help-format-BW49iAcY.js";
import "./tool-catalog-6VPSKPp9.js";
import { E as resolveSandboxConfigForAgent, k as resolveSandboxToolPolicyForAgent } from "./docker-YL21-mX4.js";
import { i as removeSandboxContainer, n as listSandboxContainers, r as removeSandboxBrowserContainer, t as listSandboxBrowsers } from "./sandbox-C3lR2qEl.js";
import "./image-ops-BLXW6hKm.js";
import "./path-alias-guards-CgP-6a1d.js";
import "./sandbox-paths-Bk2ZwMsR.js";
import "./mime-D7Q9o2pi.js";
import "./ssrf-rHmQXFZ4.js";
import "./fs-safe-Dvzkbqib.js";
import "./frontmatter-DUZeCF_V.js";
import "./env-overrides-DbK0fm-W.js";
import "./skills-CreXENx9.js";
import "./config-BkPtspys.js";
import "./routes-CdaHRCET.js";
import "./ssh-tunnel-CnI7n7iv.js";
import "./server-middleware-DcKqo5DB.js";
import { t as formatDurationCompact } from "./format-duration-PnUDQ_ov.js";
import { confirm } from "@clack/prompts";
//#region src/commands/sandbox-explain.ts
const SANDBOX_DOCS_URL = "https://docs.openclaw.ai/sandbox";
function normalizeExplainSessionKey(params) {
	const raw = (params.session ?? "").trim();
	if (!raw) return resolveAgentMainSessionKey({
		cfg: params.cfg,
		agentId: params.agentId
	});
	if (raw.includes(":")) return raw;
	if (raw === "global") return "global";
	return buildAgentMainSessionKey({
		agentId: params.agentId,
		mainKey: normalizeMainKey(raw)
	});
}
function inferProviderFromSessionKey(params) {
	const parsed = parseAgentSessionKey(params.sessionKey);
	if (!parsed) return;
	const rest = parsed.rest.trim();
	if (!rest) return;
	const parts = rest.split(":").filter(Boolean);
	if (parts.length === 0) return;
	const configuredMainKey = normalizeMainKey(params.cfg.session?.mainKey);
	if (parts[0] === configuredMainKey) return;
	const candidate = parts[0]?.trim().toLowerCase();
	if (!candidate) return;
	if (candidate === "webchat") return INTERNAL_MESSAGE_CHANNEL;
	return normalizeAnyChannelId(candidate) ?? void 0;
}
function resolveActiveChannel(params) {
	const entry = loadSessionStore(resolveStorePath(params.cfg.session?.store, { agentId: params.agentId }))[params.sessionKey];
	const candidate = (entry?.lastChannel ?? entry?.channel ?? entry?.lastProvider ?? entry?.provider ?? "").trim().toLowerCase();
	if (candidate === "webchat") return INTERNAL_MESSAGE_CHANNEL;
	const normalized = normalizeAnyChannelId(candidate);
	if (normalized) return normalized;
	return inferProviderFromSessionKey({
		cfg: params.cfg,
		sessionKey: params.sessionKey
	});
}
async function sandboxExplainCommand(opts, runtime) {
	const cfg = loadConfig();
	const defaultAgentId = resolveAgentIdFromSessionKey(resolveMainSessionKey(cfg));
	const resolvedAgentId = normalizeAgentId(opts.agent?.trim() ? opts.agent : opts.session?.trim() ? resolveAgentIdFromSessionKey(opts.session) : defaultAgentId);
	const sessionKey = normalizeExplainSessionKey({
		cfg,
		agentId: resolvedAgentId,
		session: opts.session
	});
	const sandboxCfg = resolveSandboxConfigForAgent(cfg, resolvedAgentId);
	const toolPolicy = resolveSandboxToolPolicyForAgent(cfg, resolvedAgentId);
	const mainSessionKey = resolveAgentMainSessionKey({
		cfg,
		agentId: resolvedAgentId
	});
	const sessionIsSandboxed = sandboxCfg.mode === "all" ? true : sandboxCfg.mode === "off" ? false : sessionKey.trim() !== mainSessionKey.trim();
	const channel = resolveActiveChannel({
		cfg,
		agentId: resolvedAgentId,
		sessionKey
	});
	const agentConfig = resolveAgentConfig(cfg, resolvedAgentId);
	const elevatedGlobal = cfg.tools?.elevated;
	const elevatedAgent = agentConfig?.tools?.elevated;
	const elevatedGlobalEnabled = elevatedGlobal?.enabled !== false;
	const elevatedAgentEnabled = elevatedAgent?.enabled !== false;
	const elevatedEnabled = elevatedGlobalEnabled && elevatedAgentEnabled;
	const globalAllow = channel ? elevatedGlobal?.allowFrom?.[channel] : void 0;
	const agentAllow = channel ? elevatedAgent?.allowFrom?.[channel] : void 0;
	const allowTokens = (values) => (values ?? []).map((v) => String(v).trim()).filter(Boolean);
	const globalAllowTokens = allowTokens(globalAllow);
	const agentAllowTokens = allowTokens(agentAllow);
	const elevatedAllowedByConfig = elevatedEnabled && Boolean(channel) && globalAllowTokens.length > 0 && (elevatedAgent?.allowFrom ? agentAllowTokens.length > 0 : true);
	const elevatedAlwaysAllowedByConfig = elevatedAllowedByConfig && globalAllowTokens.includes("*") && (elevatedAgent?.allowFrom ? agentAllowTokens.includes("*") : true);
	const elevatedFailures = [];
	if (!elevatedGlobalEnabled) elevatedFailures.push({
		gate: "enabled",
		key: "tools.elevated.enabled"
	});
	if (!elevatedAgentEnabled) elevatedFailures.push({
		gate: "enabled",
		key: "agents.list[].tools.elevated.enabled"
	});
	if (channel && globalAllowTokens.length === 0) elevatedFailures.push({
		gate: "allowFrom",
		key: `tools.elevated.allowFrom.${channel}`
	});
	if (channel && elevatedAgent?.allowFrom && agentAllowTokens.length === 0) elevatedFailures.push({
		gate: "allowFrom",
		key: `agents.list[].tools.elevated.allowFrom.${channel}`
	});
	const fixIt = [];
	if (sandboxCfg.mode !== "off") {
		fixIt.push("agents.defaults.sandbox.mode=off");
		fixIt.push("agents.list[].sandbox.mode=off");
	}
	fixIt.push("tools.sandbox.tools.allow");
	fixIt.push("tools.sandbox.tools.deny");
	fixIt.push("agents.list[].tools.sandbox.tools.allow");
	fixIt.push("agents.list[].tools.sandbox.tools.deny");
	fixIt.push("tools.elevated.enabled");
	if (channel) fixIt.push(`tools.elevated.allowFrom.${channel}`);
	const payload = {
		docsUrl: SANDBOX_DOCS_URL,
		agentId: resolvedAgentId,
		sessionKey,
		mainSessionKey,
		sandbox: {
			mode: sandboxCfg.mode,
			scope: sandboxCfg.scope,
			perSession: sandboxCfg.scope === "session",
			workspaceAccess: sandboxCfg.workspaceAccess,
			workspaceRoot: sandboxCfg.workspaceRoot,
			sessionIsSandboxed,
			tools: {
				allow: toolPolicy.allow,
				deny: toolPolicy.deny,
				sources: toolPolicy.sources
			}
		},
		elevated: {
			enabled: elevatedEnabled,
			channel,
			allowedByConfig: elevatedAllowedByConfig,
			alwaysAllowedByConfig: elevatedAlwaysAllowedByConfig,
			allowFrom: {
				global: channel ? globalAllowTokens : void 0,
				agent: elevatedAgent?.allowFrom && channel ? agentAllowTokens : void 0
			},
			failures: elevatedFailures
		},
		fixIt
	};
	if (opts.json) {
		writeRuntimeJson(runtime, payload);
		return;
	}
	const rich = isRich();
	const heading = (value) => colorize(rich, theme.heading, value);
	const key = (value) => colorize(rich, theme.muted, value);
	const value = (val) => colorize(rich, theme.info, val);
	const ok = (val) => colorize(rich, theme.success, val);
	const warn = (val) => colorize(rich, theme.warn, val);
	const err = (val) => colorize(rich, theme.error, val);
	const bool = (flag) => flag ? ok("true") : err("false");
	const lines = [];
	lines.push(heading("Effective sandbox:"));
	lines.push(`  ${key("agentId:")} ${value(payload.agentId)}`);
	lines.push(`  ${key("sessionKey:")} ${value(payload.sessionKey)}`);
	lines.push(`  ${key("mainSessionKey:")} ${value(payload.mainSessionKey)}`);
	lines.push(`  ${key("runtime:")} ${payload.sandbox.sessionIsSandboxed ? warn("sandboxed") : ok("direct")}`);
	lines.push(`  ${key("mode:")} ${value(payload.sandbox.mode)} ${key("scope:")} ${value(payload.sandbox.scope)} ${key("perSession:")} ${bool(payload.sandbox.perSession)}`);
	lines.push(`  ${key("workspaceAccess:")} ${value(payload.sandbox.workspaceAccess)} ${key("workspaceRoot:")} ${value(payload.sandbox.workspaceRoot)}`);
	lines.push("");
	lines.push(heading("Sandbox tool policy:"));
	lines.push(`  ${key(`allow (${payload.sandbox.tools.sources.allow.source}):`)} ${value(payload.sandbox.tools.allow.join(", ") || "(empty)")}`);
	lines.push(`  ${key(`deny  (${payload.sandbox.tools.sources.deny.source}):`)} ${value(payload.sandbox.tools.deny.join(", ") || "(empty)")}`);
	lines.push("");
	lines.push(heading("Elevated:"));
	lines.push(`  ${key("enabled:")} ${bool(payload.elevated.enabled)}`);
	lines.push(`  ${key("channel:")} ${value(payload.elevated.channel ?? "(unknown)")}`);
	lines.push(`  ${key("allowedByConfig:")} ${bool(payload.elevated.allowedByConfig)}`);
	if (payload.elevated.failures.length > 0) lines.push(`  ${key("failing gates:")} ${warn(payload.elevated.failures.map((f) => `${f.gate} (${f.key})`).join(", "))}`);
	if (payload.sandbox.mode === "non-main" && payload.sandbox.sessionIsSandboxed) {
		lines.push("");
		lines.push(`${warn("Hint:")} sandbox mode is non-main; use main session key to run direct: ${value(payload.mainSessionKey)}`);
	}
	lines.push("");
	lines.push(heading("Fix-it:"));
	for (const key of payload.fixIt) lines.push(`  - ${key}`);
	lines.push("");
	lines.push(`${key("Docs:")} ${formatDocsLink("/sandbox", "docs.openclaw.ai/sandbox")}`);
	runtime.log(`${lines.join("\n")}\n`);
}
//#endregion
//#region src/commands/sandbox-formatters.ts
/**
* Formatting utilities for sandbox CLI output
*/
function formatStatus(running) {
	return running ? "🟢 running" : "⚫ stopped";
}
function formatSimpleStatus(running) {
	return running ? "running" : "stopped";
}
function formatImageMatch(matches) {
	return matches ? "✓" : "⚠️  mismatch";
}
//#endregion
//#region src/commands/sandbox-display.ts
function displayItems(items, config, runtime) {
	if (items.length === 0) {
		runtime.log(config.emptyMessage);
		return;
	}
	runtime.log(`\n${config.title}\n`);
	for (const item of items) config.renderItem(item, runtime);
}
function displayContainers(containers, runtime) {
	displayItems(containers, {
		emptyMessage: "No sandbox runtimes found.",
		title: "📦 Sandbox Runtimes:",
		renderItem: (container, rt) => {
			rt.log(`  ${container.runtimeLabel ?? container.containerName}`);
			rt.log(`    Status:  ${formatStatus(container.running)}`);
			rt.log(`    ${container.configLabelKind ?? "Image"}:   ${container.image} ${formatImageMatch(container.imageMatch)}`);
			rt.log(`    Backend: ${container.backendId ?? "docker"}`);
			rt.log(`    Age:     ${formatDurationCompact(Date.now() - container.createdAtMs, { spaced: true }) ?? "0s"}`);
			rt.log(`    Idle:    ${formatDurationCompact(Date.now() - container.lastUsedAtMs, { spaced: true }) ?? "0s"}`);
			rt.log(`    Session: ${container.sessionKey}`);
			rt.log("");
		}
	}, runtime);
}
function displayBrowsers(browsers, runtime) {
	displayItems(browsers, {
		emptyMessage: "No sandbox browser containers found.",
		title: "🌐 Sandbox Browser Containers:",
		renderItem: (browser, rt) => {
			rt.log(`  ${browser.containerName}`);
			rt.log(`    Status:  ${formatStatus(browser.running)}`);
			rt.log(`    Image:   ${browser.image} ${formatImageMatch(browser.imageMatch)}`);
			rt.log(`    CDP:     ${browser.cdpPort}`);
			if (browser.noVncPort) rt.log(`    noVNC:   ${browser.noVncPort}`);
			rt.log(`    Age:     ${formatDurationCompact(Date.now() - browser.createdAtMs, { spaced: true }) ?? "0s"}`);
			rt.log(`    Idle:    ${formatDurationCompact(Date.now() - browser.lastUsedAtMs, { spaced: true }) ?? "0s"}`);
			rt.log(`    Session: ${browser.sessionKey}`);
			rt.log("");
		}
	}, runtime);
}
function displaySummary(containers, browsers, runtime) {
	const totalCount = containers.length + browsers.length;
	const runningCount = containers.filter((c) => c.running).length + browsers.filter((b) => b.running).length;
	const mismatchCount = containers.filter((c) => !c.imageMatch).length + browsers.filter((b) => !b.imageMatch).length;
	runtime.log(`Total: ${totalCount} (${runningCount} running)`);
	if (mismatchCount > 0) {
		runtime.log(`\n⚠️  ${mismatchCount} runtime(s) with config mismatch detected.`);
		runtime.log(`   Run '${formatCliCommand("openclaw sandbox recreate --all")}' to update all runtimes.`);
	}
}
function displayRecreatePreview(containers, browsers, runtime) {
	runtime.log("\nSandbox runtimes to be recreated:\n");
	if (containers.length > 0) {
		runtime.log("📦 Sandbox Runtimes:");
		for (const container of containers) runtime.log(`  - ${container.runtimeLabel ?? container.containerName} [${container.backendId ?? "docker"}] (${formatSimpleStatus(container.running)})`);
	}
	if (browsers.length > 0) {
		runtime.log("\n🌐 Browser Containers:");
		for (const browser of browsers) runtime.log(`  - ${browser.containerName} (${formatSimpleStatus(browser.running)})`);
	}
	const total = containers.length + browsers.length;
	runtime.log(`\nTotal: ${total} runtime(s)`);
}
function displayRecreateResult(result, runtime) {
	runtime.log(`\nDone: ${result.successCount} removed, ${result.failCount} failed`);
	if (result.successCount > 0) runtime.log("\nRuntimes will be automatically recreated when the agent is next used.");
}
//#endregion
//#region src/commands/sandbox.ts
async function sandboxListCommand(opts, runtime) {
	const containers = opts.browser ? [] : await listSandboxContainers().catch(() => []);
	const browsers = opts.browser ? await listSandboxBrowsers().catch(() => []) : [];
	if (opts.json) {
		writeRuntimeJson(runtime, {
			containers,
			browsers
		});
		return;
	}
	if (opts.browser) displayBrowsers(browsers, runtime);
	else displayContainers(containers, runtime);
	displaySummary(containers, browsers, runtime);
}
async function sandboxRecreateCommand(opts, runtime) {
	if (!validateRecreateOptions(opts, runtime)) return;
	const filtered = await fetchAndFilterContainers(opts);
	if (filtered.containers.length + filtered.browsers.length === 0) {
		runtime.log("No sandbox runtimes found matching the criteria.");
		return;
	}
	displayRecreatePreview(filtered.containers, filtered.browsers, runtime);
	if (!opts.force && !await confirmRecreate()) {
		runtime.log("Cancelled.");
		return;
	}
	const result = await removeContainers(filtered, runtime);
	displayRecreateResult(result, runtime);
	if (result.failCount > 0) runtime.exit(1);
}
function validateRecreateOptions(opts, runtime) {
	if (!opts.all && !opts.session && !opts.agent) {
		runtime.error("Please specify --all, --session <key>, or --agent <id>");
		runtime.exit(1);
		return false;
	}
	if ([
		opts.all,
		opts.session,
		opts.agent
	].filter(Boolean).length > 1) {
		runtime.error("Please specify only one of: --all, --session, --agent");
		runtime.exit(1);
		return false;
	}
	return true;
}
async function fetchAndFilterContainers(opts) {
	const allContainers = await listSandboxContainers().catch(() => []);
	const allBrowsers = await listSandboxBrowsers().catch(() => []);
	let containers = opts.browser ? [] : allContainers;
	let browsers = opts.browser ? allBrowsers : [];
	if (opts.session) {
		containers = containers.filter((c) => c.sessionKey === opts.session);
		browsers = browsers.filter((b) => b.sessionKey === opts.session);
	} else if (opts.agent) {
		const matchesAgent = createAgentMatcher(opts.agent);
		containers = containers.filter(matchesAgent);
		browsers = browsers.filter(matchesAgent);
	}
	return {
		containers,
		browsers
	};
}
function createAgentMatcher(agentId) {
	const agentPrefix = `agent:${agentId}`;
	return (item) => item.sessionKey === agentPrefix || item.sessionKey.startsWith(`${agentPrefix}:`);
}
async function confirmRecreate() {
	const result = await confirm({
		message: "This will stop and remove these containers. Continue?",
		initialValue: false
	});
	return result !== false && result !== Symbol.for("clack:cancel");
}
async function removeContainers(filtered, runtime) {
	runtime.log("\nRemoving sandbox runtimes...\n");
	let successCount = 0;
	let failCount = 0;
	for (const container of filtered.containers) if ((await removeContainer(container.containerName, removeSandboxContainer, runtime)).success) successCount++;
	else failCount++;
	for (const browser of filtered.browsers) if ((await removeContainer(browser.containerName, removeSandboxBrowserContainer, runtime)).success) successCount++;
	else failCount++;
	return {
		successCount,
		failCount
	};
}
async function removeContainer(containerName, removeFn, runtime) {
	try {
		await removeFn(containerName);
		runtime.log(`✓ Removed ${containerName}`);
		return { success: true };
	} catch (err) {
		runtime.error(`✗ Failed to remove ${containerName}: ${String(err)}`);
		return { success: false };
	}
}
//#endregion
//#region src/cli/sandbox-cli.ts
const SANDBOX_EXAMPLES = {
	main: [
		["openclaw sandbox list", "List all sandbox containers."],
		["openclaw sandbox list --browser", "List only browser containers."],
		["openclaw sandbox recreate --all", "Recreate all containers."],
		["openclaw sandbox recreate --session main", "Recreate a specific session."],
		["openclaw sandbox recreate --agent mybot", "Recreate agent containers."],
		["openclaw sandbox explain", "Explain effective sandbox config."]
	],
	list: [
		["openclaw sandbox list", "List all sandbox containers."],
		["openclaw sandbox list --browser", "List only browser containers."],
		["openclaw sandbox list --json", "JSON output."]
	],
	recreate: [
		["openclaw sandbox recreate --all", "Recreate all containers."],
		["openclaw sandbox recreate --session main", "Recreate a specific session."],
		["openclaw sandbox recreate --agent mybot", "Recreate a specific agent (includes sub-agents)."],
		["openclaw sandbox recreate --browser --all", "Recreate only browser containers."],
		["openclaw sandbox recreate --all --force", "Skip confirmation."]
	],
	explain: [
		["openclaw sandbox explain", "Show effective sandbox config."],
		["openclaw sandbox explain --session agent:main:main", "Explain a specific session."],
		["openclaw sandbox explain --agent work", "Explain an agent sandbox."],
		["openclaw sandbox explain --json", "JSON output."]
	]
};
function createRunner(commandFn) {
	return async (opts) => {
		try {
			await commandFn(opts, defaultRuntime);
		} catch (err) {
			defaultRuntime.error(String(err));
			defaultRuntime.exit(1);
		}
	};
}
function registerSandboxCli(program) {
	const sandbox = program.command("sandbox").description("Manage sandbox containers (Docker-based agent isolation)").addHelpText("after", () => `\n${theme.heading("Examples:")}\n${formatHelpExamples(SANDBOX_EXAMPLES.main)}\n`).addHelpText("after", () => `\n${theme.muted("Docs:")} ${formatDocsLink("/cli/sandbox", "docs.openclaw.ai/cli/sandbox")}\n`).action(() => {
		sandbox.help({ error: true });
	});
	sandbox.command("list").description("List sandbox containers and their status").option("--json", "Output result as JSON", false).option("--browser", "List browser containers only", false).addHelpText("after", () => `\n${theme.heading("Examples:")}\n${formatHelpExamples(SANDBOX_EXAMPLES.list)}\n\n${theme.heading("Output includes:")}\n${theme.muted("- Container name and status (running/stopped)")}\n${theme.muted("- Docker image and whether it matches current config")}\n${theme.muted("- Age (time since creation)")}\n${theme.muted("- Idle time (time since last use)")}\n${theme.muted("- Associated session/agent ID")}`).action(createRunner((opts) => sandboxListCommand({
		browser: Boolean(opts.browser),
		json: Boolean(opts.json)
	}, defaultRuntime)));
	sandbox.command("recreate").description("Remove containers to force recreation with updated config").option("--all", "Recreate all sandbox containers", false).option("--session <key>", "Recreate container for specific session").option("--agent <id>", "Recreate containers for specific agent").option("--browser", "Only recreate browser containers", false).option("--force", "Skip confirmation prompt", false).addHelpText("after", () => `\n${theme.heading("Examples:")}\n${formatHelpExamples(SANDBOX_EXAMPLES.recreate)}\n\n${theme.heading("Why use this?")}\n${theme.muted("After updating Docker images or sandbox configuration, existing containers continue running with old settings.")}\n${theme.muted("This command removes them so they'll be recreated automatically with current config when next needed.")}\n\n${theme.heading("Filter options:")}\n${theme.muted("  --all          Remove all sandbox containers")}\n${theme.muted("  --session      Remove container for specific session key")}\n${theme.muted("  --agent        Remove containers for agent (includes agent:id:* variants)")}\n\n${theme.heading("Modifiers:")}\n${theme.muted("  --browser      Only affect browser containers (not regular sandbox)")}\n${theme.muted("  --force        Skip confirmation prompt")}`).action(createRunner((opts) => sandboxRecreateCommand({
		all: Boolean(opts.all),
		session: opts.session,
		agent: opts.agent,
		browser: Boolean(opts.browser),
		force: Boolean(opts.force)
	}, defaultRuntime)));
	sandbox.command("explain").description("Explain effective sandbox/tool policy for a session/agent").option("--session <key>", "Session key to inspect (defaults to agent main)").option("--agent <id>", "Agent id to inspect (defaults to derived agent)").option("--json", "Output result as JSON", false).addHelpText("after", () => `\n${theme.heading("Examples:")}\n${formatHelpExamples(SANDBOX_EXAMPLES.explain)}\n`).action(createRunner((opts) => sandboxExplainCommand({
		session: opts.session,
		agent: opts.agent,
		json: Boolean(opts.json)
	}, defaultRuntime)));
}
//#endregion
export { registerSandboxCli };
