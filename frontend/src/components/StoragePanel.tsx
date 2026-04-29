import { useState } from "react";
import { useStoragePoll } from "../hooks/useStoragePoll";
import { getCameraBitrates } from "../api/client";
import { CameraBitratesResponse } from "../types/api";
import { formatBytes } from "../utils/format";

export function StoragePanel() {
    const { storage, error } = useStoragePoll();

    // Calculator state
    const [calcCameras, setCalcCameras] = useState(4);
    const [calcHours, setCalcHours] = useState(24);

    // Bitrate refresh state
    const [cameraBitrates, setCameraBitrates] = useState<CameraBitratesResponse | null>(null);
    const [bitrateLoading, setBitrateLoading] = useState(false);

    // Progress bar color based on status level
    const progressColor =
        !storage || storage.status_level === "ok"
            ? "progress-success"
            : storage.status_level === "warn"
              ? "progress-warning"
              : "progress-error";

    // Calculator: use per-camera bitrates if available, else default
    const getAvgBitrateMbps = (): number => {
        if (cameraBitrates && Object.keys(cameraBitrates.camera_bitrates).length > 0) {
            const values = Object.values(cameraBitrates.camera_bitrates);
            return values.reduce((sum, v) => sum + v, 0) / values.length;
        }
        return storage?.camera_bitrate_mbps ?? 1.7;
    };

    const avgBitrateMbps = getAvgBitrateMbps();
    const bitrateBytes = avgBitrateMbps * 1_000_000 / 8;
    const estimatedBytes = calcCameras * bitrateBytes * calcHours * 3600;
    const effectiveAvailable = storage?.effective_available_bytes ?? 0;
    const fits = estimatedBytes < effectiveAvailable;

    // Refresh bitrates from go2rtc APIs on the Pis
    const handleRefreshBitrates = async () => {
        setBitrateLoading(true);
        try {
            const data = await getCameraBitrates();
            setCameraBitrates(data);
        } catch {
            // Silently fail — keep using default or last known values
        } finally {
            setBitrateLoading(false);
        }
    };

    return (
        <div className="card bg-base-200 shadow-xl h-full border border-base-300">
            <div className="card-body p-4">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-2 font-bold">
                    Storage
                </h2>

                {error && (
                    <div className="alert alert-error text-sm p-2 mb-2 rounded-md">
                        <span>Storage data unavailable</span>
                    </div>
                )}

                {storage && (
                    <>
                        {/* Progress bar + summary on one line */}
                        <div className="flex items-center gap-2 mb-2">
                            <progress
                                className={`progress ${progressColor} flex-1 h-3`}
                                value={storage.used_percent}
                                max={100}
                            />
                            <span className="text-xs font-mono font-bold whitespace-nowrap">
                                {storage.used_percent}%
                            </span>
                        </div>

                        {/* Compact two-column summary */}
                        <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-xs mb-2">
                            <div className="flex justify-between text-base-content/60">
                                <span>Used</span>
                                <span className="font-mono">{formatBytes(storage.used_bytes)}</span>
                            </div>
                            <div className="flex justify-between text-base-content/60">
                                <span>Total</span>
                                <span className="font-mono">{formatBytes(storage.total_bytes)}</span>
                            </div>
                            <div className="flex justify-between text-warning">
                                <span>EEG Rsv</span>
                                <span className="font-mono">{formatBytes(storage.eeg_reserve_bytes)}</span>
                            </div>
                            <div className="flex justify-between font-bold">
                                <span>Free</span>
                                <span className="font-mono">{formatBytes(storage.effective_available_bytes)}</span>
                            </div>
                        </div>

                        {/* Cannot record warning */}
                        {!storage.can_record && (
                            <div className="alert alert-error text-xs p-2 mb-2 rounded-md">
                                <span>Recording blocked — disk below EEG reserve</span>
                            </div>
                        )}

                        {/* Calculator */}
                        <div className="border-t border-base-300 pt-2">
                            <div className="flex justify-between items-center mb-1.5">
                                <h3 className="text-xs text-base-content/50 uppercase tracking-wider font-semibold">
                                    Calculator
                                </h3>
                                <button
                                    className="btn btn-ghost btn-xs gap-1 text-base-content/50 hover:text-primary"
                                    onClick={handleRefreshBitrates}
                                    disabled={bitrateLoading}
                                    title="Sync bitrates from go2rtc on each Pi"
                                >
                                    {bitrateLoading ? (
                                        <span className="loading loading-spinner loading-xs" />
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3.5 h-3.5">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
                                        </svg>
                                    )}
                                    <span className="text-[10px]">Sync</span>
                                </button>
                            </div>

                            {/* Inputs + result in one compact block */}
                            <div className="flex gap-2 mb-1.5">
                                <label className="flex flex-col text-xs flex-1">
                                    <span className="text-base-content/60 mb-0.5">Cams</span>
                                    <select
                                        className="select select-bordered select-xs w-full"
                                        value={calcCameras}
                                        onChange={(e) => setCalcCameras(Number(e.target.value))}
                                    >
                                        {[1, 2, 3, 4].map((n) => (
                                            <option key={n} value={n}>{n}</option>
                                        ))}
                                    </select>
                                </label>
                                <label className="flex flex-col text-xs flex-1">
                                    <span className="text-base-content/60 mb-0.5">Hours</span>
                                    <input
                                        type="number"
                                        className="input input-bordered input-xs w-full"
                                        min={0.5}
                                        max={168}
                                        step={0.5}
                                        value={calcHours}
                                        onChange={(e) => setCalcHours(Number(e.target.value) || 1)}
                                    />
                                </label>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span className="font-mono font-bold">{formatBytes(estimatedBytes)}</span>
                                <span className={fits ? "text-success font-bold" : "text-error font-bold"}>
                                    {fits ? "Fits" : "Won't fit"}
                                </span>
                            </div>

                            {/* Bitrate info - tiny, only if synced */}
                            <div className="text-[10px] text-base-content/40 mt-1">
                                {cameraBitrates ? (
                                    <span className="text-success">go2rtc synced — {avgBitrateMbps.toFixed(1)} Mbps/cam</span>
                                ) : (
                                    <span>{avgBitrateMbps.toFixed(1)} Mbps/cam</span>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
