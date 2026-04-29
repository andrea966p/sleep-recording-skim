export interface DaemonStatus {
    daemon: string;
    radiens: {
        connected: boolean;
        recording_states: { [chamber: string]: "R_ON" | "R_OFF" | "UNKNOWN" | string };
    };
    mqtt: {
        connected: boolean;
    };
    sessions: { [chamber: string]: ActiveSession | null };
    pending_metadata: { [chamber: string]: PendingMetadata | null };
    manual_recordings: { [camera: string]: ManualRecording };
}

export interface ManualRecording {
    session_id: string;
    camera: string;
    start_time_local: string;
    mouse_id?: string;
    recording_type?: string;
    user_name?: string;
}

export interface ActiveSession {
    session_id: string;
    mouse_id: string;
    recording_type: string;
    chamber: number;
    camera: string;
    start_time_local: string; // ISO 8601
}

export interface PendingMetadata {
    mouse_id: string;
    recording_type: string;
    user_name: string;
    chamber: number;
    is_default: boolean;
}

export interface SetMetadataRequest {
    mouse_id?: string;
    recording_type?: string;
    user_name?: string;
    chamber?: number;
}

export interface SetMetadataResponse {
    status: string;
    metadata?: PendingMetadata;
}

export interface SessionHistoryResponse {
    count: number;
    total: number;
    sessions: SessionRecord[];
}

export interface SessionRecord {
    session_id: string;
    source: "radiens" | "manual";
    start_time_utc: number;
    end_time_utc: number;
    start_time_local: string;
    end_time_local: string;
    duration_seconds: number;
    mouse_id: string;
    recording_type: string;
    user_name: string;
    chamber: number;
    camera: string;
    radiens_xdat_filename: string;
    radiens_xdat_path: string;
    video_filename: string;
    export_status: string;
    nas_transfer_status: string;
}

export interface HealthResponse {
    healthy: boolean;
    radiens_connected: boolean;
    mqtt_connected: boolean;
    storage_level?: "ok" | "warn" | "critical";
    storage_used_percent?: number;
}

export interface StorageStatus {
    total_bytes: number;
    used_bytes: number;
    available_bytes: number;
    used_percent: number;
    categories: Record<string, { path: string; bytes: number }>;
    eeg_reserve_bytes: number;
    effective_available_bytes: number;
    status_level: "ok" | "warn" | "critical";
    camera_bitrate_mbps: number;
    can_record: boolean;
    last_updated: number;
}

export interface StorageEstimate {
    cameras: number;
    hours: number;
    estimated_bytes: number;
    effective_available_bytes: number;
    fits: boolean;
    remaining_after_bytes: number;
}

export interface CameraBitratesResponse {
    camera_bitrates: Record<string, number>;  // camera_id -> Mbps
    default_mbps: number;
    source: "go2rtc" | "default";
    errors: string[];
}
