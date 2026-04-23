import { L_ as defineSetupPluginEntry } from "./pi-embedded-CzQCqSlH.js";
import { a as imessageSetupAdapter } from "./setup-core-a_FfaAlo.js";
import { r as imessageSetupWizard, t as createIMessagePluginBase } from "./shared--Cht3FtI.js";
//#region extensions/imessage/src/channel.setup.ts
const imessageSetupPlugin = { ...createIMessagePluginBase({
	setupWizard: imessageSetupWizard,
	setup: imessageSetupAdapter
}) };
//#endregion
//#region extensions/imessage/setup-entry.ts
var setup_entry_default = defineSetupPluginEntry(imessageSetupPlugin);
//#endregion
export { imessageSetupPlugin as n, setup_entry_default as t };
