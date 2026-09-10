import { useState, useEffect } from "react";

export function useSessionTimer(startTimeLocal: string | undefined): number {
    const [elapsedSeconds, setElapsedSeconds] = useState(0);

    useEffect(() => {
        if (!startTimeLocal) {
            setElapsedSeconds(0);
            return;
        }

        const updateTimer = () => {
            // Parse ISO 8601 local time
            const start = new Date(startTimeLocal).getTime();
            const now = new Date().getTime();
            const diffSeconds = Math.max(0, Math.floor((now - start) / 1000));
            setElapsedSeconds(diffSeconds);
        };

        updateTimer();
        const interval = setInterval(updateTimer, 1000);
        return () => clearInterval(interval);
    }, [startTimeLocal]);

    return elapsedSeconds;
}
