import "./redact-BDinS1q9.js";
import "./errors-BxyFnvP3.js";
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
import "./file-lock-DoKDW8jx.js";
import "./audit-fs-CEN00XrG.js";
import "./resolve-uXRpJb-M.js";
import "./profiles-Cyg58FCO.js";
import "./daemon-install-plan.shared-BDa2vR66.js";
import "./runtime-paths-DDyo7wy3.js";
import { n as buildGatewayInstallPlan, r as gatewayInstallErrorHint, t as resolveGatewayInstallToken } from "./gateway-install-token-CmxKhUyh.js";
import { r as isGatewayDaemonRuntime } from "./daemon-runtime-BVpor8un.js";
import "./tailscale-CSUwCuE9.js";
import "./tailnet-BVzEE6AW.js";
import "./net-Dk658jWW.js";
import "./auth-C_pTuZtn.js";
import "./credentials-CO55Yx_u.js";
import "./message-channel-DUrzQUcI.js";
import "./store-D_eNuCKK.js";
import "./runtime-C8dQugND.js";
import "./plugins-DGdgUNcN.js";
import "./sessions-C8WesgCl.js";
import "./paths-BPfguEtH.js";
import "./session-write-lock-bE2vQvvO.js";
import "./method-scopes-BWG4Q18M.js";
import "./call-VZCb020X.js";
import "./control-ui-shared-SxKiMaO4.js";
import "./onboard-helpers-Cks5EPpw.js";
import "./prompt-style-MhFLSlua.js";
import "./ports-lsof-C3NOmuKA.js";
import "./restart-stale-pids-CQbYk99d.js";
import "./runtime-parse-CQJ3sqUO.js";
import "./launchd-DDdD9wdn.js";
import { n as resolveGatewayService } from "./service-s9kmDqmL.js";
import "./ports-CQIuVpXl.js";
import { i as isSystemdUserServiceAvailable } from "./systemd-CLf_Dm5l.js";
import "./note-DFCwFXVH.js";
import { n as ensureSystemdUserLingerNonInteractive } from "./systemd-linger-DmGBYuE6.js";
//#region src/commands/onboard-non-interactive/local/daemon-install.ts
async function installGatewayDaemonNonInteractive(params) {
	const { opts, runtime, port } = params;
	if (!opts.installDaemon) return { installed: false };
	const daemonRuntimeRaw = opts.daemonRuntime ?? "node";
	const systemdAvailable = process.platform === "linux" ? await isSystemdUserServiceAvailable() : true;
	if (process.platform === "linux" && !systemdAvailable) {
		runtime.log("Systemd user services are unavailable; skipping service install. Use a direct shell run (`openclaw gateway run`) or rerun without --install-daemon on this session.");
		return {
			installed: false,
			skippedReason: "systemd-user-unavailable"
		};
	}
	if (!isGatewayDaemonRuntime(daemonRuntimeRaw)) {
		runtime.error("Invalid --daemon-runtime (use node or bun)");
		runtime.exit(1);
		return { installed: false };
	}
	const service = resolveGatewayService();
	const tokenResolution = await resolveGatewayInstallToken({
		config: params.nextConfig,
		env: process.env
	});
	for (const warning of tokenResolution.warnings) runtime.log(warning);
	if (tokenResolution.unavailableReason) {
		runtime.error([
			"Gateway install blocked:",
			tokenResolution.unavailableReason,
			"Fix gateway auth config/token input and rerun setup."
		].join(" "));
		runtime.exit(1);
		return { installed: false };
	}
	const { programArguments, workingDirectory, environment } = await buildGatewayInstallPlan({
		env: process.env,
		port,
		runtime: daemonRuntimeRaw,
		warn: (message) => runtime.log(message),
		config: params.nextConfig
	});
	try {
		await service.install({
			env: process.env,
			stdout: process.stdout,
			programArguments,
			workingDirectory,
			environment
		});
	} catch (err) {
		runtime.error(`Gateway service install failed: ${String(err)}`);
		runtime.log(gatewayInstallErrorHint());
		return { installed: false };
	}
	await ensureSystemdUserLingerNonInteractive({ runtime });
	return { installed: true };
}
//#endregion
export { installGatewayDaemonNonInteractive };
