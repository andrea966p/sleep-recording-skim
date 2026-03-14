import { useState, useEffect } from "react";

export interface CameraConfig {
    id: string;      // e.g. 'pi_cam_0'
    label: string;   // e.g. 'Chamber 0'
}

export interface AppSettings {
    frigateBaseUrl: string;
    cameras: CameraConfig[];
    recordingTypes: string[];
    labMembers: string[];
}

const DEFAULT_SETTINGS: AppSettings = {
    frigateBaseUrl: "http://192.168.0.50:5000",
    cameras: [
        { id: "pi_cam_0", label: "Chamber 0" },
        { id: "pi_cam_1", label: "Chamber 1" },
        { id: "pi_cam_2", label: "Chamber 2" },
        { id: "pi_cam_3", label: "Chamber 3" },
    ],
    recordingTypes: ["basal", "recovery", "sd"],
    labMembers: ["andrea"],
};

export function useSettings() {
    const [settings, setSettings] = useState<AppSettings>(() => {
        try {
            const stored = localStorage.getItem("ns_settings");
            if (stored) {
                return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
            }
        } catch {
            // ignore
        }
        return DEFAULT_SETTINGS;
    });

    useEffect(() => {
        localStorage.setItem("ns_settings", JSON.stringify(settings));
    }, [settings]);

    // Specific updaters
    const updateFrigateUrl = (url: string) => setSettings(s => ({ ...s, frigateBaseUrl: url }));

    const setCameras = (cams: CameraConfig[]) => setSettings(s => ({ ...s, cameras: cams }));

    const setRecordingTypes = (types: string[]) => setSettings(s => ({ ...s, recordingTypes: types }));

    const setLabMembers = (members: string[]) => setSettings(s => ({ ...s, labMembers: members }));

    return {
        settings,
        updateFrigateUrl,
        setCameras,
        setRecordingTypes,
        setLabMembers,
        resetToDefaults: () => setSettings(DEFAULT_SETTINGS)
    };
}
