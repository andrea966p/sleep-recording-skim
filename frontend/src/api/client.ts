import {
    DaemonStatus,
    SetMetadataRequest,
    SetMetadataResponse,
    SessionHistoryResponse,
    HealthResponse,
    ActiveSession,
    StorageStatus,
    CameraBitratesResponse,
} from "../types/api";

const API_BASE = "http://127.0.0.1:8585";

// In a real app we might switch to a mock if API is down, but we just implement the real fetch here.
// Error handling: The caller or hooks will catch the network errors.

export async function getStatus(): Promise<DaemonStatus> {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) throw new Error("Status fetch failed");
    return res.json();
}

export async function setMetadata(chamberId: string, data: SetMetadataRequest): Promise<SetMetadataResponse> {
    const res = await fetch(`${API_BASE}/api/session/metadata?chamber_id=${encodeURIComponent(chamberId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json().catch(() => ({ status: "ok" }));
}

export async function clearMetadata(chamberId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/session/metadata?chamber_id=${encodeURIComponent(chamberId)}`, {
        method: "DELETE",
    });

    if (!res.ok) throw new Error("Failed to clear metadata");
}

export async function getCurrentSession(): Promise<{ session: ActiveSession | null }> {
    const res = await fetch(`${API_BASE}/api/session/current`);
    if (!res.ok) throw new Error("Current session fetch failed");
    return res.json();
}

export async function getSessionHistory(limit = 50, source?: string): Promise<SessionHistoryResponse> {
    let url = `${API_BASE}/api/session/history?limit=${limit}`;
    if (source) url += `&source=${encodeURIComponent(source)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("History fetch failed");
    return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/api/health`);
    // Note: /api/health returns 503 if degraded, but we still want to parse the JSON
    // so we check if it's 200 or 503.
    if (res.status !== 200 && res.status !== 503) {
        throw new Error("Health check failed");
    }
    return res.json();
}

export async function getStorage(): Promise<StorageStatus> {
    const res = await fetch(`${API_BASE}/api/storage`);
    if (!res.ok) throw new Error("Storage fetch failed");
    return res.json();
}

export async function getCameraBitrates(): Promise<CameraBitratesResponse> {
    const res = await fetch(`${API_BASE}/api/storage/camera-bitrates`);
    if (!res.ok) throw new Error("Camera bitrates fetch failed");
    return res.json();
}
