import { _ as normalizeAccountId, g as DEFAULT_ACCOUNT_ID, v as normalizeOptionalAccountId } from "./session-key-DAhnzjyr.js";
import { n as resolveNormalizedAccountEntry } from "./account-lookup-De_hUz0X.js";
import { It as listConfiguredAccountIds } from "./pi-embedded-CzQCqSlH.js";
import { a as resolveListedDefaultAccountId, r as listCombinedAccountIds } from "./account-helpers-BVDd7S3q.js";
import { c as resolveThreadBindingLifecycle } from "./thread-bindings-policy-9hlYF-wX.js";
import { t as createOptionalChannelSetupSurface } from "./channel-setup-DWLTzZGs.js";
import path from "node:path";
import crypto from "node:crypto";
//#region extensions/matrix/src/auth-precedence.ts
const MATRIX_DEFAULT_ACCOUNT_AUTH_ONLY_FIELDS = new Set([
	"userId",
	"accessToken",
	"password",
	"deviceId"
]);
function resolveMatrixStringSourceValue(value) {
	return typeof value === "string" ? value : "";
}
function shouldAllowBaseAuthFallback(accountId, field) {
	return normalizeAccountId(accountId) === "default" || !MATRIX_DEFAULT_ACCOUNT_AUTH_ONLY_FIELDS.has(field);
}
function resolveMatrixAccountStringValues(params) {
	const fields = [
		"homeserver",
		"userId",
		"accessToken",
		"password",
		"deviceId",
		"deviceName"
	];
	const resolved = {};
	for (const field of fields) resolved[field] = resolveMatrixStringSourceValue(params.account?.[field]) || resolveMatrixStringSourceValue(params.scopedEnv?.[field]) || (shouldAllowBaseAuthFallback(params.accountId, field) ? resolveMatrixStringSourceValue(params.channel?.[field]) || resolveMatrixStringSourceValue(params.globalEnv?.[field]) : "");
	return resolved;
}
//#endregion
//#region extensions/matrix/src/env-vars.ts
const MATRIX_SCOPED_ENV_SUFFIXES = [
	"HOMESERVER",
	"USER_ID",
	"ACCESS_TOKEN",
	"PASSWORD",
	"DEVICE_ID",
	"DEVICE_NAME"
];
const MATRIX_GLOBAL_ENV_KEYS = MATRIX_SCOPED_ENV_SUFFIXES.map((suffix) => `MATRIX_${suffix}`);
const MATRIX_SCOPED_ENV_RE = new RegExp(`^MATRIX_(.+)_(${MATRIX_SCOPED_ENV_SUFFIXES.join("|")})$`);
function resolveMatrixEnvAccountToken(accountId) {
	return Array.from(normalizeAccountId(accountId)).map((char) => /[a-z0-9]/.test(char) ? char.toUpperCase() : `_X${char.codePointAt(0)?.toString(16).toUpperCase() ?? "00"}_`).join("");
}
function getMatrixScopedEnvVarNames(accountId) {
	const token = resolveMatrixEnvAccountToken(accountId);
	return {
		homeserver: `MATRIX_${token}_HOMESERVER`,
		userId: `MATRIX_${token}_USER_ID`,
		accessToken: `MATRIX_${token}_ACCESS_TOKEN`,
		password: `MATRIX_${token}_PASSWORD`,
		deviceId: `MATRIX_${token}_DEVICE_ID`,
		deviceName: `MATRIX_${token}_DEVICE_NAME`
	};
}
function decodeMatrixEnvAccountToken(token) {
	let decoded = "";
	for (let index = 0; index < token.length;) {
		const hexEscape = /^_X([0-9A-F]+)_/.exec(token.slice(index));
		if (hexEscape) {
			const hex = hexEscape[1];
			const codePoint = hex ? Number.parseInt(hex, 16) : NaN;
			if (!Number.isFinite(codePoint)) return;
			decoded += String.fromCodePoint(codePoint);
			index += hexEscape[0].length;
			continue;
		}
		const char = token[index];
		if (!char || !/[A-Z0-9]/.test(char)) return;
		decoded += char.toLowerCase();
		index += 1;
	}
	const normalized = normalizeOptionalAccountId(decoded);
	if (!normalized) return;
	return resolveMatrixEnvAccountToken(normalized) === token ? normalized : void 0;
}
function listMatrixEnvAccountIds(env = process.env) {
	const ids = /* @__PURE__ */ new Set();
	for (const key of MATRIX_GLOBAL_ENV_KEYS) if (typeof env[key] === "string" && env[key]?.trim()) {
		ids.add(normalizeAccountId("default"));
		break;
	}
	for (const key of Object.keys(env)) {
		const match = MATRIX_SCOPED_ENV_RE.exec(key);
		if (!match) continue;
		const accountId = decodeMatrixEnvAccountToken(match[1]);
		if (accountId) ids.add(accountId);
	}
	return Array.from(ids).toSorted((a, b) => a.localeCompare(b));
}
//#endregion
//#region extensions/matrix/src/account-selection.ts
function isRecord(value) {
	return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
function resolveMatrixChannelConfig(cfg) {
	return isRecord(cfg.channels?.matrix) ? cfg.channels.matrix : null;
}
function findMatrixAccountEntry(cfg, accountId) {
	const channel = resolveMatrixChannelConfig(cfg);
	if (!channel) return null;
	const accounts = isRecord(channel.accounts) ? channel.accounts : null;
	if (!accounts) return null;
	const entry = resolveNormalizedAccountEntry(accounts, accountId, normalizeAccountId);
	return isRecord(entry) ? entry : null;
}
function resolveConfiguredMatrixAccountIds(cfg, env = process.env) {
	const channel = resolveMatrixChannelConfig(cfg);
	return listCombinedAccountIds({
		configuredAccountIds: listConfiguredAccountIds({
			accounts: channel && isRecord(channel.accounts) ? channel.accounts : void 0,
			normalizeAccountId
		}),
		additionalAccountIds: listMatrixEnvAccountIds(env),
		fallbackAccountIdWhenEmpty: channel ? DEFAULT_ACCOUNT_ID : void 0
	});
}
function resolveMatrixDefaultOrOnlyAccountId(cfg, env = process.env) {
	const channel = resolveMatrixChannelConfig(cfg);
	if (!channel) return DEFAULT_ACCOUNT_ID;
	const configuredDefault = normalizeOptionalAccountId(typeof channel.defaultAccount === "string" ? channel.defaultAccount : void 0);
	return resolveListedDefaultAccountId({
		accountIds: resolveConfiguredMatrixAccountIds(cfg, env),
		configuredDefaultAccountId: configuredDefault,
		ambiguousFallbackAccountId: DEFAULT_ACCOUNT_ID
	});
}
function requiresExplicitMatrixDefaultAccount(cfg, env = process.env) {
	const channel = resolveMatrixChannelConfig(cfg);
	if (!channel) return false;
	const configuredAccountIds = resolveConfiguredMatrixAccountIds(cfg, env);
	if (configuredAccountIds.length <= 1) return false;
	const configuredDefault = normalizeOptionalAccountId(typeof channel.defaultAccount === "string" ? channel.defaultAccount : void 0);
	return !(configuredDefault && configuredAccountIds.includes(configuredDefault));
}
//#endregion
//#region extensions/matrix/src/storage-paths.ts
function sanitizeMatrixPathSegment(value) {
	return value.trim().toLowerCase().replace(/[^a-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "") || "unknown";
}
function resolveMatrixHomeserverKey(homeserver) {
	try {
		const url = new URL(homeserver);
		if (url.host) return sanitizeMatrixPathSegment(url.host);
	} catch {}
	return sanitizeMatrixPathSegment(homeserver);
}
function hashMatrixAccessToken(accessToken) {
	return crypto.createHash("sha256").update(accessToken).digest("hex").slice(0, 16);
}
function resolveMatrixCredentialsFilename(accountId) {
	const normalized = normalizeAccountId(accountId);
	return normalized === "default" ? "credentials.json" : `credentials-${normalized}.json`;
}
function resolveMatrixCredentialsDir(stateDir) {
	return path.join(stateDir, "credentials", "matrix");
}
function resolveMatrixCredentialsPath(params) {
	return path.join(resolveMatrixCredentialsDir(params.stateDir), resolveMatrixCredentialsFilename(params.accountId));
}
function resolveMatrixLegacyFlatStoreRoot(stateDir) {
	return path.join(stateDir, "matrix");
}
function resolveMatrixLegacyFlatStoragePaths(stateDir) {
	const rootDir = resolveMatrixLegacyFlatStoreRoot(stateDir);
	return {
		rootDir,
		storagePath: path.join(rootDir, "bot-storage.json"),
		cryptoPath: path.join(rootDir, "crypto")
	};
}
function resolveMatrixAccountStorageRoot(params) {
	const accountKey = sanitizeMatrixPathSegment(params.accountId ?? "default");
	const userKey = sanitizeMatrixPathSegment(params.userId);
	const serverKey = resolveMatrixHomeserverKey(params.homeserver);
	const tokenHash = hashMatrixAccessToken(params.accessToken);
	return {
		rootDir: path.join(params.stateDir, "matrix", "accounts", accountKey, `${serverKey}__${userKey}`, tokenHash),
		accountKey,
		tokenHash
	};
}
//#endregion
//#region extensions/matrix/src/matrix/thread-bindings-shared.ts
const MANAGERS_BY_ACCOUNT_ID = /* @__PURE__ */ new Map();
function resolveBindingKey(params) {
	return `${params.accountId}:${params.parentConversationId?.trim() || "-"}:${params.conversationId}`;
}
function toSessionBindingTargetKind(raw) {
	return raw === "subagent" ? "subagent" : "session";
}
function resolveEffectiveBindingExpiry(params) {
	return resolveThreadBindingLifecycle(params);
}
function toSessionBindingRecord(record, defaults) {
	const lifecycle = resolveEffectiveBindingExpiry({
		record,
		defaultIdleTimeoutMs: defaults.idleTimeoutMs,
		defaultMaxAgeMs: defaults.maxAgeMs
	});
	const idleTimeoutMs = typeof record.idleTimeoutMs === "number" ? record.idleTimeoutMs : defaults.idleTimeoutMs;
	const maxAgeMs = typeof record.maxAgeMs === "number" ? record.maxAgeMs : defaults.maxAgeMs;
	return {
		bindingId: resolveBindingKey(record),
		targetSessionKey: record.targetSessionKey,
		targetKind: toSessionBindingTargetKind(record.targetKind),
		conversation: {
			channel: "matrix",
			accountId: record.accountId,
			conversationId: record.conversationId,
			parentConversationId: record.parentConversationId
		},
		status: "active",
		boundAt: record.boundAt,
		expiresAt: lifecycle.expiresAt,
		metadata: {
			agentId: record.agentId,
			label: record.label,
			boundBy: record.boundBy,
			lastActivityAt: record.lastActivityAt,
			idleTimeoutMs,
			maxAgeMs
		}
	};
}
function setMatrixThreadBindingIdleTimeoutBySessionKey(params) {
	const manager = MANAGERS_BY_ACCOUNT_ID.get(params.accountId)?.manager;
	if (!manager) return [];
	return manager.setIdleTimeoutBySessionKey(params).map((record) => toSessionBindingRecord(record, {
		idleTimeoutMs: manager.getIdleTimeoutMs(),
		maxAgeMs: manager.getMaxAgeMs()
	}));
}
function setMatrixThreadBindingMaxAgeBySessionKey(params) {
	const manager = MANAGERS_BY_ACCOUNT_ID.get(params.accountId)?.manager;
	if (!manager) return [];
	return manager.setMaxAgeBySessionKey(params).map((record) => toSessionBindingRecord(record, {
		idleTimeoutMs: manager.getIdleTimeoutMs(),
		maxAgeMs: manager.getMaxAgeMs()
	}));
}
//#endregion
//#region src/plugin-sdk/matrix.ts
const matrixSetup = createOptionalChannelSetupSurface({
	channel: "matrix",
	label: "Matrix",
	npmSpec: "@openclaw/matrix",
	docsPath: "/channels/matrix"
});
const matrixSetupWizard = matrixSetup.setupWizard;
const matrixSetupAdapter = matrixSetup.setupAdapter;
//#endregion
export { resolveMatrixAccountStorageRoot as a, resolveMatrixLegacyFlatStoragePaths as c, resolveConfiguredMatrixAccountIds as d, resolveMatrixChannelConfig as f, resolveMatrixAccountStringValues as h, setMatrixThreadBindingMaxAgeBySessionKey as i, findMatrixAccountEntry as l, getMatrixScopedEnvVarNames as m, matrixSetupWizard as n, resolveMatrixCredentialsDir as o, resolveMatrixDefaultOrOnlyAccountId as p, setMatrixThreadBindingIdleTimeoutBySessionKey as r, resolveMatrixCredentialsPath as s, matrixSetupAdapter as t, requiresExplicitMatrixDefaultAccount as u };
