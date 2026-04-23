import "./logger-kwZIqwuw.js";
import "./paths-ViKUYWUK.js";
import "./tmp-openclaw-dir-idKIOMmb.js";
import "./theme-CdOoMzRk.js";
import "./globals-DBUMOBZ8.js";
import { m as defaultRuntime } from "./subsystem-DISldKSB.js";
import "./ansi-BEJF8NKS.js";
import "./boolean-C3GkJetE.js";
import "./env-Dnra1IpT.js";
import "./utils-CS0Ikux6.js";
import "./boundary-path-Dm0QJ7-y.js";
import "./boundary-file-read-DcZxlWD8.js";
import "./logger-BmpSCz93.js";
import "./exec-B5_AYfQG.js";
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
import { i as unsetConfiguredMcpServer, r as setConfiguredMcpServer, t as listConfiguredMcpServers } from "./mcp-config-Dp646rw6.js";
import { t as parseConfigValue } from "./config-value-D8Ad0Iav.js";
//#region src/cli/mcp-cli.ts
function fail(message) {
	defaultRuntime.error(message);
	defaultRuntime.exit(1);
	throw new Error(message);
}
function printJson(value) {
	defaultRuntime.writeJson(value);
}
function registerMcpCli(program) {
	const mcp = program.command("mcp").description("Manage OpenClaw MCP server config");
	mcp.command("list").description("List configured MCP servers").option("--json", "Print JSON").action(async (opts) => {
		const loaded = await listConfiguredMcpServers();
		if (!loaded.ok) fail(loaded.error);
		if (opts.json) {
			printJson(loaded.mcpServers);
			return;
		}
		const names = Object.keys(loaded.mcpServers).toSorted();
		if (names.length === 0) {
			defaultRuntime.log(`No MCP servers configured in ${loaded.path}.`);
			return;
		}
		defaultRuntime.log(`MCP servers (${loaded.path}):`);
		for (const name of names) defaultRuntime.log(`- ${name}`);
	});
	mcp.command("show").description("Show one configured MCP server or the full MCP config").argument("[name]", "MCP server name").option("--json", "Print JSON").action(async (name, opts) => {
		const loaded = await listConfiguredMcpServers();
		if (!loaded.ok) fail(loaded.error);
		const value = name ? loaded.mcpServers[name] : loaded.mcpServers;
		if (name && !value) fail(`No MCP server named "${name}" in ${loaded.path}.`);
		if (opts.json) {
			printJson(value ?? {});
			return;
		}
		if (name) defaultRuntime.log(`MCP server "${name}" (${loaded.path}):`);
		else defaultRuntime.log(`MCP servers (${loaded.path}):`);
		printJson(value ?? {});
	});
	mcp.command("set").description("Set one configured MCP server from a JSON object").argument("<name>", "MCP server name").argument("<value>", "JSON object, for example {\"command\":\"uvx\",\"args\":[\"context7-mcp\"]}").action(async (name, rawValue) => {
		const parsed = parseConfigValue(rawValue);
		if (parsed.error) fail(parsed.error);
		const result = await setConfiguredMcpServer({
			name,
			server: parsed.value
		});
		if (!result.ok) fail(result.error);
		defaultRuntime.log(`Saved MCP server "${name}" to ${result.path}.`);
	});
	mcp.command("unset").description("Remove one configured MCP server").argument("<name>", "MCP server name").action(async (name) => {
		const result = await unsetConfiguredMcpServer({ name });
		if (!result.ok) fail(result.error);
		if (!result.removed) fail(`No MCP server named "${name}" in ${result.path}.`);
		defaultRuntime.log(`Removed MCP server "${name}" from ${result.path}.`);
	});
}
//#endregion
export { registerMcpCli };
