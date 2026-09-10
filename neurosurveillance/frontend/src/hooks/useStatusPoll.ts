import { useState, useEffect, useRef } from "react";
import { getStatus } from "../api/client";
import { DaemonStatus } from "../types/api";

const STATUS_POLL_INTERVAL = 1500;

export function useStatusPoll() {
    const [status, setStatus] = useState<DaemonStatus | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [isOffline, setIsOffline] = useState(false);

    // Track previous session IDs to detect when any of them end
    const previousSessionIds = useRef<Record<string, string | null>>({});
    const [sessionEndedTick, setSessionEndedTick] = useState(0);

    useEffect(() => {
        let mounted = true;

        const poll = async () => {
            try {
                const data = await getStatus();
                if (!mounted) return;

                setStatus(data);
                setIsOffline(false);
                setError(null);

                let sessionEnded = false;

                // Track sessions per chamber
                Object.keys(data.sessions || {}).forEach(chamber => {
                    const currentSessionId = data.sessions[chamber]?.session_id || null;
                    const prevId = previousSessionIds.current[chamber];

                    if (prevId !== null && prevId !== undefined && currentSessionId === null) {
                        sessionEnded = true;
                    }
                    previousSessionIds.current[chamber] = currentSessionId;
                });

                if (sessionEnded) {
                    setSessionEndedTick(t => t + 1);
                }

            } catch (err: any) {
                if (!mounted) return;
                setIsOffline(true);
                setError(err);
            }
        };

        // Initial fetch
        poll();

        const interval = setInterval(poll, STATUS_POLL_INTERVAL);
        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    return { status, error, isOffline, sessionEndedTick };
}
