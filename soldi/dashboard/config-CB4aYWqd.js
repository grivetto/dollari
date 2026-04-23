import { b as validateConfigObjectWithPlugins, wt as applyLegacyMigrations } from "./io-cPs4dU7X.js";
//#region src/config/legacy-migrate.ts
function migrateLegacyConfig(raw) {
	const { next, changes } = applyLegacyMigrations(raw);
	if (!next) return {
		config: null,
		changes: []
	};
	const validated = validateConfigObjectWithPlugins(next);
	if (!validated.ok) {
		changes.push("Migration applied, but config still invalid; fix remaining issues manually.");
		return {
			config: null,
			changes
		};
	}
	return {
		config: validated.config,
		changes
	};
}
//#endregion
//#region src/config/types.tools.ts
const TOOLS_BY_SENDER_KEY_TYPES = [
	"id",
	"e164",
	"username",
	"name"
];
function parseToolsBySenderTypedKey(rawKey) {
	const trimmed = rawKey.trim();
	if (!trimmed) return;
	const lowered = trimmed.toLowerCase();
	for (const type of TOOLS_BY_SENDER_KEY_TYPES) {
		const prefix = `${type}:`;
		if (!lowered.startsWith(prefix)) continue;
		return {
			type,
			value: trimmed.slice(prefix.length)
		};
	}
}
//#endregion
export { parseToolsBySenderTypedKey as n, migrateLegacyConfig as r, TOOLS_BY_SENDER_KEY_TYPES as t };
