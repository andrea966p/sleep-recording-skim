
import { useHealthPoll } from "../hooks/useHealthPoll";
import { StatusBadge } from "./StatusBadge";

export function SystemHealth() {
    const { health, error } = useHealthPoll();

    let daemonStatus: "ok" | "error" = "ok";
    if (error || !health) daemonStatus = "error";

    let radiensStatus: "ok" | "error" = health?.radiens_connected ? "ok" : "error";
    let mqttStatus: "ok" | "error" = health?.mqtt_connected ? "ok" : "error";

    // Note: Frigate health depends on the camera preview loading, we keep it simple here.
    // In a more complex setup, CameraPreview could lift state up or we rely on the backend.
    // For the handoff doc, we show overall health text too.

    return (
        <div className="card bg-base-200 shadow-xl h-full border border-base-300">
            <div className="card-body p-4">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-2 font-bold">
                    System Health
                </h2>

                {error && (
                    <div className="alert alert-error text-sm p-2 mb-2 rounded-md">
                        <span>Daemon Offline — check service</span>
                    </div>
                )}

                <div className="grid grid-cols-2 gap-2 text-sm mt-1">
                    <div className="flex justify-between items-center border-b border-base-300 pb-1">
                        <span className="font-medium">Daemon</span>
                        <StatusBadge level={daemonStatus} text={daemonStatus === "ok" ? "Running" : "Offline"} />
                    </div>
                    <div className="flex justify-between items-center border-b border-base-300 pb-1">
                        <span className="font-medium">Radiens</span>
                        <StatusBadge level={radiensStatus} text={radiensStatus === "ok" ? "Conn" : "Disc"} />
                    </div>
                    <div className="flex justify-between items-center border-b border-base-300 pb-1">
                        <span className="font-medium">MQTT</span>
                        <StatusBadge level={mqttStatus} text={mqttStatus === "ok" ? "Conn" : "Disc"} />
                    </div>
                    <div className="flex justify-between items-center border-b border-base-300 pb-1">
                        <span className="font-medium">System</span>
                        <StatusBadge
                            level={health?.healthy ? "ok" : (health ? "warn" : "error")}
                            text={health?.healthy ? "Healthy" : (health ? "Degraded" : "Down")}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
