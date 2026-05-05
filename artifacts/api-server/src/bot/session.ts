import { STEPS, MODES } from "./constants.js";

type Step = (typeof STEPS)[keyof typeof STEPS];
type Mode = (typeof MODES)[keyof typeof MODES];

export interface UserSession {
  step: Step;
  mode?: Mode;
  pendingText?: string;
  pendingInstruction?: string;
  language?: string;
}

const sessions = new Map<number, UserSession>();

export function getSession(userId: number): UserSession {
  if (!sessions.has(userId)) {
    sessions.set(userId, { step: STEPS.IDLE });
  }
  return sessions.get(userId)!;
}

export function setSession(userId: number, data: Partial<UserSession>): void {
  const current = getSession(userId);
  sessions.set(userId, { ...current, ...data });
}

export function resetSession(userId: number): void {
  sessions.set(userId, { step: STEPS.IDLE });
}
