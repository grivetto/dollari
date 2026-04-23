import "../../logger-kwZIqwuw.js";
import "../../paths-ViKUYWUK.js";
import "../../tmp-openclaw-dir-idKIOMmb.js";
import "../../theme-CdOoMzRk.js";
import "../../globals-DBUMOBZ8.js";
import "../../subsystem-DISldKSB.js";
import "../../ansi-BEJF8NKS.js";
import "../../logger-BmpSCz93.js";
import "../../ip-DIgtRRTW.js";
import "../../ssrf-rHmQXFZ4.js";
import "../../fetch-guard-BH3MjZoA.js";
import { t as definePluginEntry } from "../../plugin-entry-BNczxv7M.js";
import { t as groqMediaUnderstandingProvider } from "../../media-understanding-BGz4x5yF.js";
//#region extensions/groq/index.ts
var groq_default = definePluginEntry({
	id: "groq",
	name: "Groq Media Understanding",
	description: "Bundled Groq audio transcription provider",
	register(api) {
		api.registerMediaUnderstandingProvider(groqMediaUnderstandingProvider);
	}
});
//#endregion
export { groq_default as default };
