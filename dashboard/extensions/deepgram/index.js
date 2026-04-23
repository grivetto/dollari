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
import { n as deepgramMediaUnderstandingProvider } from "../../media-understanding-BGz4x5yF.js";
//#region extensions/deepgram/index.ts
var deepgram_default = definePluginEntry({
	id: "deepgram",
	name: "Deepgram Media Understanding",
	description: "Bundled Deepgram audio transcription provider",
	register(api) {
		api.registerMediaUnderstandingProvider(deepgramMediaUnderstandingProvider);
	}
});
//#endregion
export { deepgram_default as default };
