import { useState, useEffect } from "react";
import { getSessionHistory } from "../api/client";
import { SessionRecord } from "../types/api";
import { formatShortDuration, formatShortDate } from "../utils/format";

interface Props {
    refreshTick: number;
}

export function SessionHistory({ refreshTick }: Props) {
    const [sessions, setSessions] = useState<SessionRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [sourceFilter, setSourceFilter] = useState<string>("");

    useEffect(() => {
        let mounted = true;
        const fetchHistory = async () => {
            try {
                setIsLoading(true);
                const data = await getSessionHistory(50, sourceFilter || undefined);
                if (mounted) {
                    setSessions(data.sessions || []);
                    setError(null);
                }
            } catch (err: any) {
                if (mounted) setError(err);
            } finally {
                if (mounted) setIsLoading(false);
            }
        };

        fetchHistory();

        return () => { mounted = false; };
    }, [refreshTick, sourceFilter]);

    if (error) {
        return (
            <div className="card bg-base-200 shadow-xl border border-base-300 h-full">
                <div className="card-body p-4">
                    <h2 className="card-title text-sm text-base-content/70 flex-none font-bold uppercase tracking-widest">History</h2>
                    <div className="alert alert-error text-sm">Failed to load history</div>
                </div>
            </div>
        );
    }

    return (
        <div className="card bg-base-200 shadow-xl border border-base-300 h-full flex flex-col">
            <div className="card-body p-4 flex flex-col h-full overflow-hidden">
                <div className="flex flex-wrap items-center justify-between mb-2 border-b border-base-300 pb-2">
                    <h2 className="card-title text-sm text-base-content/70 flex-none font-bold uppercase tracking-widest">
                        Session History
                    </h2>
                    <div className="join">
                        <button className={`join-item btn btn-xs min-w-[3rem] ${sourceFilter === "" ? "btn-active" : ""}`} onClick={() => setSourceFilter("")}>All</button>
                        <button className={`join-item btn btn-xs min-w-[4rem] ${sourceFilter === "radiens" ? "btn-active" : ""}`} onClick={() => setSourceFilter("radiens")}>Radiens</button>
                        <button className={`join-item btn btn-xs min-w-[4rem] ${sourceFilter === "manual" ? "btn-active" : ""}`} onClick={() => setSourceFilter("manual")}>Manual</button>
                    </div>
                </div>

                <div className="flex-grow overflow-y-auto pr-2 -mr-2 flex flex-col gap-2">
                    {isLoading && sessions.length === 0 ? (
                        <div className="flex justify-center p-8">
                            <span className="loading loading-spinner text-primary"></span>
                        </div>
                    ) : sessions.length === 0 ? (
                        <div className="text-center italic text-base-content/50 py-10 text-sm">
                            No sessions recorded yet
                        </div>
                    ) : (
                        <div className="w-full text-xs flex flex-col">
                            {/* Header Row */}
                            <div className="flex items-center pb-2 mb-2 border-b border-base-300 font-bold text-base-content/70 sticky top-0 bg-base-200 z-10 px-2">
                                <div className="w-32 flex-none">Date</div>
                                <div className="flex-1 min-w-0 pr-2">Mouse ID</div>
                                <div className="w-16 flex-none">Type</div>
                                <div className="w-12 flex-none text-right pr-4">Dur</div>
                                <div className="w-16 flex-none text-center">Stat</div>
                            </div>

                            {/* Session Rows */}
                            <div className="flex flex-col gap-1">
                                {sessions.map((session) => (
                                    <div key={session.session_id} className="flex flex-col">
                                        <div
                                            className="flex items-center hover:bg-base-300 cursor-pointer p-2 rounded-md transition-colors"
                                            onClick={() => setExpandedId(expandedId === session.session_id ? null : session.session_id)}
                                        >
                                            <div className="w-32 flex-none whitespace-nowrap tabular-nums flex items-center gap-2">
                                                {session.source === "radiens" ? (
                                                    <span className="badge badge-error badge-xs font-bold px-1.5 py-2.5 opacity-80" title="Radiens EEG Session">EEG</span>
                                                ) : (
                                                    <span className="badge badge-warning badge-xs font-bold px-1.5 py-2.5 opacity-80" title="Manual Frigate UI Recording">MAN</span>
                                                )}
                                                {formatShortDate(session.start_time_local)}
                                            </div>
                                            <div className="flex-1 min-w-0 pr-2 font-mono font-bold truncate" title={session.mouse_id}>
                                                {session.mouse_id}
                                            </div>
                                            <div className="w-16 flex-none truncate">
                                                {session.recording_type}
                                            </div>
                                            <div className="w-12 flex-none text-right pr-4 tabular-nums">
                                                {formatShortDuration(session.duration_seconds)}
                                            </div>
                                            <div className="w-16 flex-none text-center">
                                                <span className={`badge badge-sm badge-outline ${session.export_status === 'completed' ? 'badge-success text-success' :
                                                    session.export_status === 'failed' ? 'badge-error text-error' :
                                                        'badge-warning text-warning'
                                                    }`}>
                                                    {session.export_status === 'completed' ? 'done' : session.export_status}
                                                </span>
                                            </div>
                                        </div>

                                        {/* Expanded Details Panel */}
                                        {expandedId === session.session_id && (
                                            <div className="mt-1 mb-2 mx-2 p-3 bg-base-300/50 rounded-r-md border-l-4 border-l-primary text-xs grid grid-cols-2 gap-x-4 gap-y-2 animate-in slide-in-from-top-2 duration-200">
                                                <div className="col-span-2 text-base-content/60 font-mono text-[10px] break-all">
                                                    ID: {session.session_id}
                                                </div>

                                                <div><span className="text-base-content/70">Start:</span><br />{new Date(session.start_time_local).toLocaleString()}</div>
                                                <div><span className="text-base-content/70">End:</span><br />{session.end_time_local ? new Date(session.end_time_local).toLocaleString() : 'N/A'}</div>

                                                <div>
                                                    <span className="text-base-content/70">Video ({session.camera || 'none'}):</span><br />
                                                    <span className="font-mono bg-base-300 px-1 py-0.5 rounded text-[10px] block truncate" title={session.video_filename}>{session.video_filename || 'N/A'}</span>
                                                </div>
                                                <div>
                                                    <span className="text-base-content/70">EEG:</span><br />
                                                    <span className="font-mono bg-base-300 px-1 py-0.5 rounded text-[10px] block truncate" title={session.radiens_xdat_filename}>{session.radiens_xdat_filename || 'N/A'}</span>
                                                </div>

                                                <div><span className="text-base-content/70">User:</span> {session.user_name || 'N/A'}</div>
                                                <div><span className="text-base-content/70">Chamber:</span> {session.chamber !== undefined ? session.chamber : 'N/A'}</div>

                                                <div className="col-span-2 border-t border-base-300 mt-1 pt-2 flex gap-4">
                                                    <span>Export: <strong className={session.export_status === "completed" ? "text-success" : ""}>{session.export_status}</strong></span>
                                                    <span>NAS: <strong className={session.nas_transfer_status === "completed" ? "text-success" : ""}>{session.nas_transfer_status}</strong></span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
