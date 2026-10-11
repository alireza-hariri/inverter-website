/**
 * JWT session handling: where the tokens live, and how an expired one is
 * renewed without the user noticing.
 *
 * Access tokens are short-lived, so every authenticated call has to be prepared
 * for one 401 that means "refresh me", not "log in again". `authRequest` does
 * that once per call; only a refresh that itself fails ends the session.
 *
 * The tokens are kept in `localStorage`, which means these functions only work
 * in the browser -- call them from client components, and read the session
 * server-side from a cookie instead if a page must render logged-in on the
 * server.
 */

import { apiRequest, asObject, withFields, type Check, type RequestOptions } from "./api";

export type User = {
  id: number;
  email: string;
  username: string;
  mobile: string;
  first_name: string;
  last_name: string;
};

export type Tokens = { access: string; refresh: string };

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
/** Client components listen for this to re-render when the session changes. */
export const AUTH_CHANGED_EVENT = "auth-changed";

const asUser: Check<User> = (value, endpoint) =>
  withFields<User>(asObject(value, endpoint), endpoint, ["id", "email", "username"]);

const asTokens: Check<Tokens> = (value, endpoint) =>
  withFields<Tokens>(asObject(value, endpoint), endpoint, ["access", "refresh"]);

const asSession: Check<Tokens & { user: User }> = (value, endpoint) => {
  const record = asObject(value, endpoint);
  return { ...asTokens(record, endpoint), user: asUser(record.user, endpoint) };
};

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_KEY);
}

export function isSignedIn(): boolean {
  return getAccessToken() !== null;
}

export function storeTokens(tokens: Tokens): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_KEY, tokens.access);
  window.localStorage.setItem(REFRESH_KEY, tokens.refresh);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function signOut(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export async function signInWithPassword(email: string, password: string): Promise<Tokens> {
  const tokens = await apiRequest("/token/", asTokens, { method: "POST", body: { email, password } });
  storeTokens(tokens);
  return tokens;
}

/** Sends a login code by SMS. Answers 202 whether or not the number is registered. */
export function requestMobileCode(mobile: string): Promise<void> {
  return apiRequest("/users/mobile/request-code/", () => undefined, { method: "POST", body: { mobile } });
}

/** Verifies the code, signs the user in, and creates the account if the number is new. */
export async function signInWithMobileCode(mobile: string, code: string): Promise<User> {
  const session = await apiRequest("/users/mobile/verify-code/", asSession, {
    method: "POST",
    body: { mobile, code },
  });
  storeTokens({ access: session.access, refresh: session.refresh });
  return session.user;
}

/** Exchanges the stored refresh token for a new access token, or ends the session. */
async function renewAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const refresh = window.localStorage.getItem(REFRESH_KEY);
  if (!refresh) return null;
  try {
    const renewed = await apiRequest(
      "/token/refresh/",
      (value, endpoint) => withFields<{ access: string }>(asObject(value, endpoint), endpoint, ["access"]),
      { method: "POST", body: { refresh } },
    );
    window.localStorage.setItem(ACCESS_KEY, renewed.access);
    return renewed.access;
  } catch {
    signOut();
    return null;
  }
}

/** Raised instead of retrying forever when there is no usable session left. */
export class NotSignedInError extends Error {
  constructor() {
    super("Please sign in to continue.");
    this.name = "NotSignedInError";
  }
}

/**
 * `apiRequest` with the access token attached, retried once through a refresh
 * when the token has expired.
 */
export async function authRequest<T>(
  endpoint: string,
  check: Check<T>,
  options: Omit<RequestOptions, "token"> = {},
): Promise<T> {
  const token = getAccessToken();
  if (!token) throw new NotSignedInError();
  try {
    return await apiRequest(endpoint, check, { ...options, token });
  } catch (error) {
    if (!isExpiredToken(error)) throw error;
    const renewed = await renewAccessToken();
    if (!renewed) throw new NotSignedInError();
    return apiRequest(endpoint, check, { ...options, token: renewed });
  }
}

function isExpiredToken(error: unknown): boolean {
  return typeof error === "object" && error !== null && (error as { status?: number }).status === 401;
}

export function getCurrentUser(): Promise<User> {
  return authRequest("/users/me/", asUser);
}

export function updateCurrentUser(changes: Partial<Omit<User, "id">>): Promise<User> {
  return authRequest("/users/me/", asUser, { method: "PATCH", body: changes });
}

export function register(input: {
  email: string;
  username: string;
  password: string;
  mobile?: string;
  first_name?: string;
  last_name?: string;
}): Promise<void> {
  return apiRequest("/users/register/", () => undefined, { method: "POST", body: input });
}
