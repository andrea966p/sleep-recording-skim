import React, { useState, useEffect } from "react";
import { PendingMetadata } from "../types/api";
import { AppSettings } from "../hooks/useSettings";

interface Props {
    chamberId: string;
    chamberLabel: string;
    pendingMetadata: PendingMetadata | undefined;
    isSessionActive: boolean;
    onSetMetadata: (chamberId: string, data: Partial<PendingMetadata>) => Promise<void>;
    onClearMetadata: (chamberId: string) => Promise<void>;
    settings: AppSettings;
}

export function SessionSetup({
    chamberId,
    chamberLabel,
    pendingMetadata,
    isSessionActive,
    onSetMetadata,
    onClearMetadata,
    settings
}: Props) {
    const [mouseId, setMouseId] = useState("");
    const [recordingType, setRecordingType] = useState<string>("");
    const [userName, setUserName] = useState<string>("");

    const [isSubmitting, setIsSubmitting] = useState(false);
    const lastPendingJson = React.useRef<string>("");

    // Sync form state with pending metadata/defaults only when source values change.
    useEffect(() => {
        const source = pendingMetadata ?? {
            mouse_id: "unknown",
            recording_type: settings.recordingTypes[0] || "basal",
            user_name: settings.labMembers[0] || "andrea",
            chamber: Number.parseInt(chamberId, 10) || 0,
            is_default: true,
        };

        const currentJson = JSON.stringify(source);
        if (currentJson !== lastPendingJson.current) {
            setMouseId(source.mouse_id === "unknown" ? "" : source.mouse_id);
            setRecordingType(source.recording_type === "unknown"
                ? (settings.recordingTypes[0] || "basal")
                : source.recording_type);
            setUserName(source.user_name === "unknown"
                ? (settings.labMembers[0] || "andrea")
                : source.user_name);

            lastPendingJson.current = currentJson;
        }
    }, [pendingMetadata, settings, chamberId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await onSetMetadata(chamberId, {
                mouse_id: mouseId || "unknown",
                recording_type: recordingType,
                chamber: Number.parseInt(chamberId, 10) || 0,
                user_name: userName
            });
            // the toast will be handled in App.tsx or parent
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClear = async () => {
        if (confirm(`Clear all metadata to defaults for ${chamberLabel}?`)) {
            await onClearMetadata(chamberId);
        }
    };

    const baseline = pendingMetadata ?? {
        mouse_id: "unknown",
        recording_type: settings.recordingTypes[0] || "basal",
        user_name: settings.labMembers[0] || "andrea",
    };

    const isFormDirty =
        (mouseId || "unknown") !== baseline.mouse_id ||
        recordingType !== baseline.recording_type ||
        userName !== baseline.user_name;

    return (
        <div className="card bg-base-200 shadow-xl border border-base-300 h-full relative overflow-hidden">

            {/* Locked overlay */}
            {isSessionActive && (
                <div className="absolute inset-0 bg-base-300/60 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center p-6 text-center">
                    <div className="bg-base-100 p-4 rounded-xl shadow-lg border border-base-content/10 flex flex-col items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-warning mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        <h3 className="font-bold text-lg text-base-content">Session in Progress</h3>
                        <p className="text-sm text-base-content/70 mt-1">Metadata is locked and cannot be changed.</p>
                    </div>
                </div>
            )}

            <div className="card-body p-4 lg:p-6">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-4 font-bold border-b border-base-300 pb-2 flex justify-between">
                    <span>Session Setup</span>
                    <span className="text-primary">{chamberLabel}</span>
                </h2>

                <form onSubmit={handleSubmit} className="flex flex-col flex-grow gap-4">

                    <div className="form-control w-full">
                        <label className="label py-1">
                            <span className="label-text font-semibold">Mouse ID</span>
                        </label>
                        <input
                            type="text"
                            placeholder="e.g. HETCF3R1"
                            className="input input-bordered w-full font-mono font-bold uppercase"
                            maxLength={20}
                            value={mouseId}
                            onChange={(e) => setMouseId(e.target.value.replace(/[^a-zA-Z0-9-,_]/g, ''))}
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="form-control w-full">
                            <label className="label py-1">
                                <span className="label-text font-semibold">Recording Type</span>
                            </label>
                            <select
                                className="select select-bordered w-full font-mono font-bold"
                                value={recordingType}
                                onChange={(e) => setRecordingType(e.target.value)}
                            >
                                {settings.recordingTypes.map(t => (
                                    <option key={t} value={t}>{t}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-control w-full">
                            <label className="label py-1">
                                <span className="label-text font-semibold">User</span>
                            </label>
                            <select
                                className="select select-bordered w-full font-mono"
                                value={userName}
                                onChange={(e) => setUserName(e.target.value)}
                            >
                                {settings.labMembers.map(u => (
                                    <option key={u} value={u}>{u}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="mt-auto pt-6 flex gap-2">
                        <button
                            type="button"
                            className="btn btn-outline flex-1"
                            onClick={handleClear}
                            disabled={isSubmitting || (pendingMetadata?.is_default ?? true)}
                        >
                            Clear Defaults
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary flex-1 shadow-lg"
                            disabled={isSubmitting || !isFormDirty}
                        >
                            {isSubmitting ? <span className="loading loading-spinner"></span> : "Set Metadata"}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    );
}
