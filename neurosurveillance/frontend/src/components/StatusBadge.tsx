

type StatusLevel = 'ok' | 'warn' | 'error' | 'offline';

interface Props {
    level: StatusLevel;
    text: string;
}

export function StatusBadge({ level, text }: Props) {
    let dotClass = 'bg-base-content/20'; // Default ghost/unknown color

    if (level === 'ok') {
        dotClass = 'bg-success';
    } else if (level === 'warn') {
        dotClass = 'bg-warning';
    } else if (level === 'error' || level === 'offline') {
        dotClass = 'bg-error shadow-[0_0_8px_rgba(255,0,0,0.5)]'; // Add a subtle red glow when error
    }

    // Add a pulsing effect to the error dot to draw attention if desired
    const pulse = (level === 'error' || level === 'offline') ? 'animate-pulse' : '';

    return (
        <div className="flex items-center gap-2 font-semibold">
            <span className={`w-2.5 h-2.5 rounded-full ${dotClass} ${pulse}`}></span>
            <span className="text-base-content/90">{text}</span>
        </div>
    );
}
