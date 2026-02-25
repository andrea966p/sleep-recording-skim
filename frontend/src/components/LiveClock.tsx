import { useState, useEffect } from "react";

export function LiveClock() {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="flex flex-col items-end text-right">
            <div className="text-xl font-bold font-mono tracking-widest text-base-content/80">
                {time.toLocaleTimeString('en-US', { hour12: false })}
            </div>
            <div className="text-xs uppercase font-bold text-base-content/40 tracking-wider">
                {time.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
            </div>
        </div>
    );
}
