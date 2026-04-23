import { I_ as defineChannelPluginEntry } from "./pi-embedded-CzQCqSlH.js";
import { t as zaloPlugin } from "./channel-BNeaciYj.js";
import { n as setZaloRuntime } from "./runtime-C-tPhd8L.js";
//#region extensions/zalo/index.ts
var zalo_default = defineChannelPluginEntry({
	id: "zalo",
	name: "Zalo",
	description: "Zalo channel plugin",
	plugin: zaloPlugin,
	setRuntime: setZaloRuntime
});
//#endregion
export { zalo_default as t };
