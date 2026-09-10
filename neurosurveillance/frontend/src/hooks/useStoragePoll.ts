import { useState, useEffect } from "react";
import { getStorage } from "../api/client";
import { StorageStatus } from "../types/api";

const STORAGE_POLL_INTERVAL = 10_000; // 10 seconds

export function useStoragePoll() {
    const [storage, setStorage] = useState<StorageStatus | null>(null);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let mounted = true;

        const poll = async () => {
            try {
                const data = await getStorage();
                if (mounted) {
                    setStorage(data);
                    setError(null);
                }
            } catch (err: any) {
                if (mounted) {
                    setError(err);
                    setStorage(null);
                }
            }
        };

        poll(); // Immediate first fetch
        const interval = setInterval(poll, STORAGE_POLL_INTERVAL);
        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    return { storage, error };
}
