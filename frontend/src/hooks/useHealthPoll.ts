import { useState, useEffect } from "react";
import { getHealth } from "../api/client";
import { HealthResponse } from "../types/api";

// The interval for checking system health
const HEALTH_POLL_INTERVAL = 5000;

export function useHealthPoll() {
    const [health, setHealth] = useState<HealthResponse | null>(null);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let mounted = true;

        // Using a wrapper around the client's getHealth to handle states
        const poll = async () => {
            try {
                const data = await getHealth();
                if (mounted) {
                    setHealth(data);
                    setError(null);
                }
            } catch (err: any) {
                if (mounted) {
                    setError(err);
                    setHealth(null);
                }
            }
        };

        // Initial fetch immediately on mount
        poll();

        // Start polling loop
        const interval = setInterval(poll, HEALTH_POLL_INTERVAL);
        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    return { health, error };
}
