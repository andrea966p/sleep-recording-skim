import { useEffect } from "react";
import { DaemonStatus } from "../types/api";
import { useSessionTimer } from "../hooks/useSessionTimer";
import { formatDuration } from "../utils/format";

interface Props {
    chamberId: string;
    status: DaemonStatus | null;
    error: Error | null;
}

export function LiveStatus({ chamberId, status, error }: Props) {
    const chamberSession = status?.sessions?.[chamberId] || null;
    const recordingState = status?.radiens.recording_states?.[chamberId] || "UNKNOWN";
    const pendingMeta = status?.pending_metadata?.[chamberId] || null;

    // We use the timer hook even if offline, it will just return 0 if no session
    const duration = useSessionTimer(chamberSession?.start_time_local);

    useEffect(() => {
        // Show toast on state changes if needed
    }, [recordingState]);

    const isRecording = recordingState === "R_ON" || recordingState === "ON";
    const recordingColor = isRecording ? "bg-error animate-pulse shadow-[0_0_15px_rgba(255,0,0,0.5)]" : "bg-base-300";

    return (
        <div className={`card shadow-xl h-full border ${isRecording ? 'border-error/50 bg-base-100' : 'border-base-300 bg-base-200'}`}>
            <div className="card-body p-4">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-4 font-bold flex justify-between">
                    <span>Live Status</span>
                    <div className="flex items-center gap-2 normal-case text-xs">
                        <span className={`w-3 h-3 rounded-full ${recordingColor}`}></span>
                        <span className={isRecording ? "text-error font-bold" : "text-base-content/50"}>
                            {recordingState || "OFF"}
                        </span>
                    </div>
                </h2>

                {error || !status ? (
                    <div className="alert alert-error text-sm py-2">
                        No connection to daemon
                    </div>
                ) : (
                    <div className="flex flex-col gap-4">

                        {/* Active Session Info */}
                        <div className={`p-4 rounded-xl border-l-4 ${isRecording ? "border-l-success bg-success/5" : "border-l-base-300 bg-base-300/30"}`}>
                            <div className="text-xs uppercase font-bold text-base-content/50 mb-1">
                                Active Session
                            </div>

                            {chamberSession ? (
                                <div className="grid grid-cols-2 gap-y-2 text-sm">
                                    <div className="text-base-content/70">Mouse ID:</div>
                                    <div className="font-mono font-bold">{chamberSession.mouse_id}</div>

                                    <div className="text-base-content/70">Protocol:</div>
                                    <div className="font-bold">{chamberSession.recording_type}</div>

                                    <div className="text-base-content/70">Chamber:</div>
                                    <div className="font-bold">{chamberSession.chamber}</div>

                                    <div className="text-base-content/70">Duration:</div>
                                    <div className="font-mono text-xl font-bold bg-base-100/50 rounded px-1 -ml-1 text-center border border-base-content/10">
                                        {formatDuration(duration)}
                                    </div>
                                </div>
                            ) : (
                                <div className="text-sm font-medium italic text-base-content/60 py-2">
                                    No active session
                                </div>
                            )}
                        </div>

                        {/* Pending Metadata Warning */}
                        {pendingMeta?.is_default && !chamberSession && (
                            <div className="alert alert-warning py-2 text-xs shadow-sm">
                                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                                <span>No metadata set — defaults will be used if recording starts</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
