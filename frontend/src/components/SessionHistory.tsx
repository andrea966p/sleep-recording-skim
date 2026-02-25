import React, { useState, useEffect } from "react";
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

    useEffect(() => {
        let mounted = true;
        const fetchHistory = async () => {
            try {
                setIsLoading(true);
                const data = await getSessionHistory(50);
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
    }, [refreshTick]);

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
                <h2 className="card-title text-sm text-base-content/70 flex-none font-bold uppercase tracking-widest mb-2 border-b border-base-300 pb-2">
                    Session History
                </h2>

                <div className="flex-grow overflow-y-auto pr-2 -mr-2">
                    {isLoading && sessions.length === 0 ? (
                        <div className="flex justify-center p-8">
                            <span className="loading loading-spinner text-primary"></span>
                        </div>
                    ) : sessions.length === 0 ? (
                        <div className="text-center italic text-base-content/50 py-10 text-sm">
                            No sessions recorded yet
                        </div>
                    ) : (
                        <table className="table table-compact w-full text-xs">
                            <thead className="bg-base-200 sticky top-0 z-10">
                                <tr>
                                    <th className="bg-base-200">Date</th>
                                    <th className="bg-base-200">Mouse ID</th>
                                    <th className="bg-base-200">Type</th>
                                    <th className="bg-base-200">Dur</th>
                                    <th className="bg-base-200">Stat</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.map((session) => (
                                    <React.Fragment key={session.session_id}>
                                        <tr
                                            className="hover:bg-base-300 cursor-pointer border-t border-base-300 transition-colors"
                                            onClick={() => setExpandedId(expandedId === session.session_id ? null : session.session_id)}
                                        >
                                            <td className="whitespace-nowrap tabular-nums">{formatShortDate(session.start_time_local)}</td>
                                            <td className="font-mono font-bold max-w-xs truncate" title={session.mouse_id}>{session.mouse_id}</td>
                                            <td>{session.recording_type}</td>
                                            <td className="tabular-nums whitespace-nowrap">{formatShortDuration(session.duration_seconds)}</td>
                                            <td>
                                                <span className={`badge badge-sm badge-outline ${session.export_status === 'completed' ? 'badge-success text-success' :
                                                        session.export_status === 'failed' ? 'badge-error text-error' :
                                                            'badge-warning text-warning'
                                                    }`}>
                                                    {session.export_status === 'completed' ? 'done' : session.export_status}
                                                </span>
                                            </td>
                                        </tr>

                                        {/* Expanded Details Row */}
                                        {expandedId === session.session_id && (
                                            <tr>
                                                <td colSpan={5} className="p-0 border-none bg-base-300/50">
                                                    <div className="px-4 py-3 border-l-4 border-l-primary text-xs grid grid-cols-2 gap-x-4 gap-y-2">
                                                        <div className="col-span-2 text-base-content/60 font-mono text-[10px] break-all">{session.session_id}</div>

                                                        <div><span className="text-base-content/70">Start:</span><br />{new Date(session.start_time_local).toLocaleString()}</div>
                                                        <div><span className="text-base-content/70">End:</span><br />{session.end_time_local ? new Date(session.end_time_local).toLocaleString() : 'N/A'}</div>

                                                        <div>
                                                            <span className="text-base-content/70">Video ({session.camera}):</span><br />
                                                            <span className="font-mono bg-base-300 px-1 py-0.5 rounded text-[10px] block truncate" title={session.video_filename}>{session.video_filename || 'N/A'}</span>
                                                        </div>
                                                        <div>
                                                            <span className="text-base-content/70">EEG:</span><br />
                                                            <span className="font-mono bg-base-300 px-1 py-0.5 rounded text-[10px] block truncate" title={session.radiens_xdat_filename}>{session.radiens_xdat_filename || 'N/A'}</span>
                                                        </div>

                                                        <div><span className="text-base-content/70">User:</span> {session.user_name}</div>
                                                        <div><span className="text-base-content/70">Chamber:</span> {session.chamber}</div>

                                                        <div className="col-span-2 border-t border-base-300 mt-1 pt-2 flex gap-4">
                                                            <span>Export: <strong className={session.export_status === "completed" ? "text-success" : ""}>{session.export_status}</strong></span>
                                                            <span>NAS: <strong className={session.nas_transfer_status === "completed" ? "text-success" : ""}>{session.nas_transfer_status}</strong></span>
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
