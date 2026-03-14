import { useState } from "react";
import { CameraConfig, AppSettings } from "../hooks/useSettings";
import { DaemonStatus, PendingMetadata } from "../types/api";

import { SessionSetup } from "./SessionSetup";
import { LiveStatus } from "./LiveStatus";
import { CameraPreview } from "./CameraPreview";

interface Props {
    chamberId: string;
    cam: CameraConfig;
    settings: AppSettings;
    status: DaemonStatus | null;
    error: Error | null;
    onSetMetadata: (chamberId: string, data: Partial<PendingMetadata>) => Promise<void>;
    onClearMetadata: (chamberId: string) => Promise<void>;
}

export function ChamberSilo({ chamberId, cam, settings, status, error, onSetMetadata, onClearMetadata }: Props) {
    const [isExpanded, setIsExpanded] = useState(false);

    const recordingState = status?.radiens.recording_states?.[chamberId] || "UNKNOWN";
    const isRecording = recordingState === "R_ON" || recordingState === "ON";
    const recordingColor = isRecording ? "bg-error animate-pulse shadow-[0_0_10px_rgba(255,0,0,0.8)]" : "bg-base-300";

    const session = status?.sessions?.[chamberId];
    const mouseId = session?.mouse_id || status?.pending_metadata?.[chamberId]?.mouse_id || "No Mouse";

    const cameraId = cam.id;
    const manualRec = status?.manual_recordings?.[cameraId];

    return (
        <div className={`collapse bg-base-200/50 border shadow-sm transition-all duration-300 ease-in-out ${isExpanded ? "collapse-open border-base-content/20 rounded-3xl" : "collapse-close border-base-300 rounded-xl"
            }`}>
            {/* Header / Toggle Button */}
            <div
                className="collapse-title flex items-center justify-between cursor-pointer p-4 group hover:bg-base-200"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-4">
                    <span className={`w-3.5 h-3.5 rounded-full ${recordingColor}`}></span>
                    <h2 className="text-lg font-bold tracking-wide">{cam.label.toUpperCase()}</h2>

                    {manualRec && (
                        <div className="badge badge-warning gap-1 text-[10px] sm:text-xs">
                            <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-current animate-pulse"></span>
                            Manual Recording — {new Date(manualRec.start_time_local).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    )}

                    {!isExpanded && !manualRec && (
                        <div className="badge badge-outline border-base-content/20 text-base-content/70 font-mono text-xs hidden sm:flex">
                            {mouseId}
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs text-base-content/50 uppercase font-bold tracking-widest hidden sm:inline">
                        {isExpanded ? "Collapse" : "Expand"}
                    </span>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={2}
                        stroke="currentColor"
                        className={`w-5 h-5 text-base-content/50 transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`}
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                    </svg>
                </div>
            </div>

            {/* Content Body */}
            <div className="collapse-content px-4 pb-4">
                {/* 
                  When expanded, show the 3 blocks.
                  If you want to save processing completely, you could conditionally render the blocks here:
                  `{isExpanded && ( ... )}`
                  But keeping them mounted ensures the timer stays smooth and snapshots resume instantly. 
                  We will rely on CSS to hide them, which `collapse-content` does by setting height to 0. 
                */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-2">
                    {/* Left Column: Form + Status */}
                    <div className="flex flex-col gap-4">
                        <div className="flex-none" style={{ minHeight: "360px" }}>
                            <SessionSetup
                                chamberId={chamberId}
                                chamberLabel={cam.label}
                                pendingMetadata={status?.pending_metadata?.[chamberId] || undefined}
                                isSessionActive={!!session}
                                onSetMetadata={onSetMetadata}
                                onClearMetadata={onClearMetadata}
                                settings={settings}
                            />
                        </div>
                        <div className="flex-none" style={{ minHeight: "180px" }}>
                            <LiveStatus
                                chamberId={chamberId}
                                cameraId={cam.id}
                                status={status}
                                error={error}
                            />
                        </div>
                    </div>

                    {/* Right Column: Video Feed */}
                    <div className="flex-none xl:h-auto" style={{ minHeight: "360px" }}>
                        <CameraPreview
                            cameraId={cam.id}
                            cameraLabel={cam.label}
                            frigateBaseUrl={settings.frigateBaseUrl}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
