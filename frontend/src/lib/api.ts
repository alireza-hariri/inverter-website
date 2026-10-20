/**
 * The one place that talks to the backend.
 *
 * Every response is checked before it is returned, because the failure this
 * prevents is silent: a cast such as `as Product[]` compiles, and the mismatch
 * only surfaces later inside a component as `map is not a function`, pointing
 * at the wrong file. A check here throws naming the endpoint instead.
 *
 * `apiRequest` holds no state, so it is safe in server components. Anything
 * behind a login goes through `authRequest` in `auth.ts`.
 */

/**
 * The serve pipeline allocates the backend's port per run and passes it in, so
 * the fallback only matters when the frontend is started by hand.
 */
export const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

/** The paginated envelope every list endpoint answers with. */
export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/**
 * The backend wraps errors as `{ "error": { "code", "detail" } }`, where
 * `detail` is a message for most failures and a dict of field errors for a
 * rejected form.
 */
export type ErrorDetail = string | Record<string, unknown> | unknown[];

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly endpoint: string,
    readonly detail: ErrorDetail,
  ) {
    super(typeof detail === "string" ? detail : `${endpoint} failed with ${status}`);
    this.name = "ApiError";
  }

  /** Field errors as `{ field: ["message"] }`, empty when the failure was not a rejected form. */
  get fieldErrors(): Record<string, string[]> {
    if (!this.detail || typeof this.detail !== "object" || Array.isArray(this.detail)) return {};
    const errors: Record<string, string[]> = {};
    for (const [field, value] of Object.entries(this.detail)) {
      errors[field] = Array.isArray(value) ? value.map(String) : [String(value)];
    }
    return errors;
  }

  /** One line to show the user, whichever shape the backend answered with. */
  get userMessage(): string {
    if (typeof this.detail === "string") return this.detail;
    const first = Object.entries(this.fieldErrors)[0];
    if (first) return `${first[0]}: ${first[1][0]}`;
    return `Something went wrong (${this.status}).`;
  }
}

/**
 * For `.catch()` on a record fetch: a 404 becomes `null` (the page calls
 * `notFound()`), anything else is rethrown. Swallowing every error instead
 * would turn a backend outage into a wave of 404s, which search engines
 * read as "these pages were deleted".
 */
export function nullIfNotFound(error: unknown): null {
  if (error instanceof ApiError && error.status === 404) return null;
  throw error;
}

/** Turns one response body into `T`, or throws saying which endpoint lied. */
export type Check<T> = (value: unknown, endpoint: string) => T;

export type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  /** Access token to send as `Authorization: Bearer`. */
  token?: string;
  query?: Record<string, string | number | boolean | null | undefined>;
  headers?: Record<string, string>;
  /**
   * Server components render at request time against a live database, so the
   * default is to never cache. Pass `"force-cache"` for genuinely static data.
   */
  cache?: RequestCache;
  signal?: AbortSignal;
};

function buildUrl(endpoint: string, query: RequestOptions["query"]): string {
  const url = new URL(`${API_BASE}/api${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`);
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  }
  return url.toString();
}

/** Calls `/api<endpoint>` and returns the checked body. Throws `ApiError` on failure. */
export async function apiRequest<T>(endpoint: string, check: Check<T>, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, token, query, headers, cache = "no-store", signal } = options;
  let response: Response;
  try {
    response = await fetch(buildUrl(endpoint, query), {
      method,
      cache,
      signal,
      headers: {
        Accept: "application/json",
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (cause) {
    // A refused connection or an aborted request is not an empty result, and
    // must never be reported as one.
    throw new ApiError(0, endpoint, `The server could not be reached: ${(cause as Error).message}`);
  }

  const text = await response.text();
  let parsed: unknown = undefined;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new ApiError(response.status, endpoint, `The server answered with ${response.status} and a non-JSON body.`);
    }
  }

  if (!response.ok) {
    const envelope = parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>).error : undefined;
    const detail = envelope && typeof envelope === "object"
      ? ((envelope as Record<string, unknown>).detail as ErrorDetail)
      : ((parsed as ErrorDetail) ?? `The request failed with ${response.status}.`);
    throw new ApiError(response.status, endpoint, detail);
  }

  return check(parsed, endpoint);
}

/** The response was not the shape this endpoint is documented to return. */
export function invalidShape(endpoint: string, why: string): never {
  throw new ApiError(0, endpoint, `${endpoint} answered with an unexpected shape: ${why}.`);
}

export function asObject(value: unknown, endpoint: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    invalidShape(endpoint, `expected an object, got ${Array.isArray(value) ? "an array" : typeof value}`);
  }
  return value as Record<string, unknown>;
}

export function asArray(value: unknown, endpoint: string): unknown[] {
  if (!Array.isArray(value)) invalidShape(endpoint, `expected an array, got ${typeof value}`);
  return value;
}

/** Asserts the fields the app reads are present, and hands back the record as `T`. */
export function withFields<T>(record: Record<string, unknown>, endpoint: string, fields: readonly string[]): T {
  const missing = fields.filter((field) => !(field in record));
  if (missing.length) invalidShape(endpoint, `missing ${missing.join(", ")}`);
  return record as T;
}

/** Wraps an item check into a check for the paginated envelope. */
export function asPage<T>(item: Check<T>): Check<Page<T>> {
  return (value, endpoint) => {
    const record = asObject(value, endpoint);
    if (typeof record.count !== "number") invalidShape(endpoint, "missing the pagination count");
    return {
      count: record.count,
      next: (record.next as string | null) ?? null,
      previous: (record.previous as string | null) ?? null,
      results: asArray(record.results, endpoint).map((entry) => item(entry, endpoint)),
    };
  };
}

/** For the endpoints whose body carries nothing the app reads. */
export const asNothing: Check<void> = () => undefined;
