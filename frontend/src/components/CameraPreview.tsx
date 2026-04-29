import { useState, useEffect, useCallback, useRef } from "react";

interface Props {
    cameraId: string;
    cameraLabel: string;
    frigateBaseUrl: string;
    onStatusChange?: (online: boolean) => void;
}

export function CameraPreview({ cameraId, cameraLabel, frigateBaseUrl, onStatusChange }: Props) {
    const [timestamp, setTimestamp] = useState(Date.now());
    const lastStatusRef = useRef(true);

    const updateStatus = useCallback((online: boolean) => {
        if (lastStatusRef.current !== online) {
            lastStatusRef.current = online;
            onStatusChange?.(online);
        }
    }, [onStatusChange]);

    useEffect(() => {
        // Refresh snapshot every 1000ms
        const interval = setInterval(() => {
            setTimestamp(Date.now());
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const url = `${frigateBaseUrl}/api/${cameraId}/latest.jpg?t=${timestamp}`;

    return (
        <div className="card bg-base-200 shadow-xl border border-base-300 flex flex-col h-full w-full">
            <div className="card-body p-4 flex flex-col h-full">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-2 font-bold flex-none">
                    Live Feed
                </h2>

                <div className="relative flex flex-col rounded-xl overflow-hidden shadow-inner bg-black ring-1 ring-base-300 flex-grow min-h-0">
                    {/* Overlay Label */}
                    <div className="absolute top-0 left-0 right-0 bg-base-300/80 backdrop-blur-sm p-1 px-3 z-10 text-xs font-mono font-bold flex justify-between">
                        <span className="text-base-content">{cameraLabel}</span>
                        <span className="text-base-content/60 z-10">{cameraId}</span>
                    </div>

                    {/* Image */}
                    <div className="flex-grow flex items-center justify-center relative w-full h-full pt-6 group">
                        <img
                            src={url}
                            alt={`${cameraLabel} feed`}
                            className="object-contain w-full h-full absolute inset-0 pt-7 pb-1 px-1 z-0"
                            onError={(e) => {
                                (e.target as HTMLImageElement).style.visibility = 'hidden';
                                updateStatus(false);
                            }}
                            onLoad={(e) => {
                                (e.target as HTMLImageElement).style.visibility = 'visible';
                                updateStatus(true);
                            }}
                        />
                        <div className="absolute inset-0 pt-7 flex items-center justify-center text-sm font-bold text-base-content/30 z-[-1]">
                            Camera offline
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
