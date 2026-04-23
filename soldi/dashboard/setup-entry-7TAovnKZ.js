import { L_ as defineSetupPluginEntry } from "./pi-embedded-CzQCqSlH.js";
import { r as discordSetupAdapter } from "./setup-core-CDRAK1RF.js";
import { t as createDiscordPluginBase } from "./shared-DqX1FsVP.js";
//#region extensions/discord/src/channel.setup.ts
const discordSetupPlugin = { ...createDiscordPluginBase({ setup: discordSetupAdapter }) };
//#endregion
//#region extensions/discord/setup-entry.ts
var setup_entry_default = defineSetupPluginEntry(discordSetupPlugin);
//#endregion
export { discordSetupPlugin as n, setup_entry_default as t };
