import type { OpenClawConfig } from "../../config/config.js";
import { type SessionEntry } from "../../config/sessions.js";
import type { FinalizedMsgContext } from "../templating.js";
import { getAbortMemory, getAbortMemorySizeForTest, isAbortRequestText, isAbortTrigger, resetAbortMemoryForTest, setAbortMemory } from "./abort-primitives.js";
export { resolveAbortCutoffFromContext, shouldSkipMessageByAbortCutoff } from "./abort-cutoff.js";
export { getAbortMemory, getAbortMemorySizeForTest, isAbortRequestText, isAbortTrigger, resetAbortMemoryForTest, setAbortMemory, };
export declare function formatAbortReplyText(stoppedSubagents?: number): string;
export declare function resolveSessionEntryForKey(store: Record<string, SessionEntry> | undefined, sessionKey: string | undefined): {
    entry?: SessionEntry;
    key?: string;
    legacyKeys?: string[];
};
export declare function stopSubagentsForRequester(params: {
    cfg: OpenClawConfig;
    requesterSessionKey?: string;
}): {
    stopped: number;
};
export declare function tryFastAbortFromMessage(params: {
    ctx: FinalizedMsgContext;
    cfg: OpenClawConfig;
}): Promise<{
    handled: boolean;
    aborted: boolean;
    stoppedSubagents?: number;
}>;
