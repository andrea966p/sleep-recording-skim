

type StatusLevel = 'ok' | 'warn' | 'error' | 'offline';

interface Props {
    level: StatusLevel;
    text: string;
}

export function StatusBadge({ level, text }: Props) {
    let colorClass = 'badge-ghost';
    let icon = '❓';

    if (level === 'ok') {
        colorClass = 'badge-success text-success-content';
        icon = '✓';
    } else if (level === 'warn') {
        colorClass = 'badge-warning text-warning-content';
        icon = '⚠';
    } else if (level === 'error' || level === 'offline') {
        colorClass = 'badge-error text-error-content';
        icon = '✕';
    }

    return (
        <div className={`badge ${colorClass} gap-1 font-semibold whitespace-nowrap`}>
            <span>{icon}</span> {text}
        </div>
    );
}
