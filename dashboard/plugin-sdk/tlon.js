import "../redact-BDinS1q9.js";
import "../errors-BxyFnvP3.js";
import "../unhandled-rejections-CDJ8dOVP.js";
import "../logger-kwZIqwuw.js";
import "../paths-ViKUYWUK.js";
import "../tmp-openclaw-dir-idKIOMmb.js";
import "../theme-CdOoMzRk.js";
import "../globals-DBUMOBZ8.js";
import "../subsystem-DISldKSB.js";
import "../ansi-BEJF8NKS.js";
import "../utils-CS0Ikux6.js";
import { t as formatDocsLink } from "../links-8xRhWBQL.js";
import { _ as normalizeAccountId, g as DEFAULT_ACCOUNT_ID } from "../session-key-DAhnzjyr.js";
import "../boundary-path-Dm0QJ7-y.js";
import "../boundary-file-read-DcZxlWD8.js";
import "../logger-BmpSCz93.js";
import "../exec-B5_AYfQG.js";
import "../workspace-D4K6QX9X.js";
import "../agent-scope-DoT9OqaV.js";
import "../registry-xyHjVLxh.js";
import "../ip-DIgtRRTW.js";
import "../zod-schema.core-yLTNC4-K.js";
import "../runtime-C8dQugND.js";
import "../plugins-DGdgUNcN.js";
import "../logging-C2L37N2X.js";
import "../identity-D8H54Ni5.js";
import "../path-alias-guards-CgP-6a1d.js";
import { s as isBlockedHostnameOrIp, t as SsrFBlockedError } from "../ssrf-rHmQXFZ4.js";
import { n as fetchWithSsrFGuard } from "../fetch-guard-BH3MjZoA.js";
import { t as emptyPluginConfigSchema } from "../config-schema-WTc54khc.js";
import { s as patchScopedAccountConfig, t as applyAccountNameToChannelSection } from "../setup-helpers-CLK_iaLL.js";
import { r as buildChannelConfigSchema } from "../config-schema-Bpwy_blm.js";
import { r as buildComputedAccountStatusSnapshot } from "../status-helpers-Dd-hr4j4.js";
import "../setup-binary-DXdzcWG_.js";
import "../archive-Bk8HKpaY.js";
import "../fs-safe-Dvzkbqib.js";
import "../signal-cli-install-BJB9N18P.js";
import "../setup-wizard-proxy-D0W3ulU0.js";
import "../setup-BYrV6xB7.js";
import { t as createDedupeCache } from "../dedupe-Cs92vYPk.js";
import { t as createChannelReplyPipeline } from "../channel-reply-pipeline-C0iCnI2R.js";
import { t as createLoggerBackedRuntime } from "../runtime-DB0HL3pI.js";
import { t as createOptionalChannelSetupSurface } from "../channel-setup-DWLTzZGs.js";
//#region src/plugin-sdk/tlon.ts
const tlonSetup = createOptionalChannelSetupSurface({
	channel: "tlon",
	label: "Tlon",
	npmSpec: "@openclaw/tlon",
	docsPath: "/channels/tlon"
});
const tlonSetupAdapter = tlonSetup.setupAdapter;
const tlonSetupWizard = tlonSetup.setupWizard;
//#endregion
export { DEFAULT_ACCOUNT_ID, SsrFBlockedError, applyAccountNameToChannelSection, buildChannelConfigSchema, buildComputedAccountStatusSnapshot, createChannelReplyPipeline, createDedupeCache, createLoggerBackedRuntime, emptyPluginConfigSchema, fetchWithSsrFGuard, formatDocsLink, isBlockedHostnameOrIp, normalizeAccountId, patchScopedAccountConfig, tlonSetupAdapter, tlonSetupWizard };
