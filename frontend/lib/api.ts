/**
 * Centralized API client with resilient error handling and backend URL configuration.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {}

/**
 * Fetch wrapper with error handling.
 */
async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}/api${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  try {
    const response = await fetch(url, {
      ...options,
      cache: 'no-store', // Prevent browser/Next.js caching of API responses
    });

    if (!response.ok) {
      throw new Error(
        `API request failed with status ${response.status}: ${response.statusText}`
      );
    }

    const data: T = await response.json();
    return data;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
      throw new Error(
        `Cannot connect to backend at ${API_BASE_URL}. Is the server running?`
      );
    }
    throw error;
  }
}

/**
 * POST to /api/memory to save denomination preference.
 */
export async function savePreference(
  sessionId: string,
  denomination: string
): Promise<{ session_id: string; denomination: string; status: string }> {
  return apiFetch("/memory", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      denomination: denomination,
    }),
  });
}

/**
 * GET /api/history to fetch conversation history.
 */
export async function fetchHistory(sessionId: string): Promise<{
  session_id: string;
  history: Array<{ role: string; message: string; timestamp?: string }>;
}> {
  const params = new URLSearchParams({ session_id: sessionId });
  return apiFetch(`/history?${params.toString()}`);
}

/**
 * POST to /api/chat to send a message.
 */
export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<{
  message: string;
  citations: Array<{
    reference: string;
    text: string;
    verified: boolean;
  }>;
  safety_status: string;
  safety_reason: string;
}> {
  return apiFetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });
}

/**
 * POST to /api/image to generate an image.
 */
export async function generateImage(prompt: string, style?: string, enhance?: boolean): Promise<{
  image_url?: string;
  base64_image?: string;
  enhanced_prompt: string;
  safety_status: string;
  safety_reason: string;
}> {
  return apiFetch("/image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt,
      style: style || "oil painting",
      enhance: enhance ?? true,
    }),
    timeout: 60000,
  });
}

/**
 * GET /api/health to check backend status.
 */
export async function checkHealth(): Promise<{
  status: string;
  timestamp?: string;
  chroma_status?: string;
  sqlite_status?: string;
}> {
  return apiFetch("/health", { timeout: 60000 });
}

/**
 * GET /api/evaluate to fetch pre-evaluated results.
 */
export async function fetchEvaluations(): Promise<{
  total_cases: number;
  evaluations: Array<{
    test_id: string;
    category: string;
    test_case: string;
    result: string;
    score: number;
    llm_response: string;
    timestamp: string;
  }>;
  running?: boolean;
}> {
  return apiFetch("/evaluate", { timeout: 120000 });
}

/**
 * POST /api/evaluate to trigger evaluation suite run.
 */
export async function runEvaluationSuite(
  testIdSubset?: string[]
): Promise<{ status: string; message?: string }> {
  return apiFetch("/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      test_id_subset: testIdSubset || null,
    }),
    timeout: 30000, // 30 second timeout for the trigger
  });
}

export { API_BASE_URL };
