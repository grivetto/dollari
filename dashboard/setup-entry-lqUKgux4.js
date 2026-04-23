import { L_ as defineSetupPluginEntry } from "./pi-embedded-CzQCqSlH.js";
import { o as signalSetupAdapter } from "./setup-core-BoUlSB_z.js";
import { i as signalSetupWizard, t as createSignalPluginBase } from "./shared-CpbJMMlV.js";
//#region extensions/signal/src/channel.setup.ts
const signalSetupPlugin = { ...createSignalPluginBase({
	setupWizard: signalSetupWizard,
	setup: signalSetupAdapter
}) };
//#endregion
//#region extensions/signal/setup-entry.ts
var setup_entry_default = defineSetupPluginEntry(signalSetupPlugin);
//#endregion
export { signalSetupPlugin as n, setup_entry_default as t };
