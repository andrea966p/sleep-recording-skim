import { useState } from "react";
import { AppSettings, CameraConfig } from "../hooks/useSettings";

interface Props {
    isOpen: boolean;
    onClose: () => void;
    settings: AppSettings;
    updateFrigateUrl: (url: string) => void;
    setCameras: (cams: CameraConfig[]) => void;
    setRecordingTypes: (types: string[]) => void;
    setLabMembers: (members: string[]) => void;
}

export function SettingsModal({
    isOpen, onClose, settings, updateFrigateUrl, setCameras, setRecordingTypes, setLabMembers
}: Props) {
    const [activeTab, setActiveTab] = useState<"users" | "types" | "cameras">("users");

    // Local state for editing fields before saving
    const [newLabMember, setNewLabMember] = useState("");
    const [newRecType, setNewRecType] = useState("");

    const [newCamId, setNewCamId] = useState("");
    const [newCamLabel, setNewCamLabel] = useState("");

    if (!isOpen) return null;

    // --- Handlers ---
    const handleAddMember = () => {
        if (newLabMember && !settings.labMembers.includes(newLabMember)) {
            setLabMembers([...settings.labMembers, newLabMember]);
            setNewLabMember("");
        }
    };

    const handleRemoveMember = (member: string) => {
        setLabMembers(settings.labMembers.filter((m) => m !== member));
    };

    const handleAddType = () => {
        if (newRecType && !settings.recordingTypes.includes(newRecType)) {
            setRecordingTypes([...settings.recordingTypes, newRecType]);
            setNewRecType("");
        }
    };

    const handleRemoveType = (type: string) => {
        setRecordingTypes(settings.recordingTypes.filter((t) => t !== type));
    };

    const handleAddCamera = () => {
        if (newCamId && newCamLabel && !settings.cameras.find(c => c.id === newCamId)) {
            setCameras([...settings.cameras, { id: newCamId, label: newCamLabel }]);
            setNewCamId("");
            setNewCamLabel("");
        }
    };

    const handleRemoveCamera = (id: string) => {
        setCameras(settings.cameras.filter((c) => c.id !== id));
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-base-300/80 backdrop-blur-sm p-4">
            <div className="card bg-base-100 shadow-2xl border border-base-300 w-full max-w-2xl max-h-[85vh] flex flex-col">

                {/* Header */}
                <div className="card-body p-6 flex-none border-b border-base-300 flex flex-row justify-between items-center">
                    <h2 className="card-title text-xl font-bold flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                        </svg>
                        System Configuration
                    </h2>
                    <button className="btn btn-sm btn-circle btn-ghost" onClick={onClose}>✕</button>
                </div>

                {/* Tabs */}
                <div className="tabs tabs-boxed rounded-none bg-base-200 p-2 flex-none">
                    <button className={`tab flex-1 font-bold ${activeTab === 'users' ? 'tab-active' : ''}`} onClick={() => setActiveTab('users')}>Users</button>
                    <button className={`tab flex-1 font-bold ${activeTab === 'types' ? 'tab-active' : ''}`} onClick={() => setActiveTab('types')}>Recording Types</button>
                    <button className={`tab flex-1 font-bold ${activeTab === 'cameras' ? 'tab-active' : ''}`} onClick={() => setActiveTab('cameras')}>Cameras & Network</button>
                </div>

                {/* Content Area */}
                <div className="card-body p-6 overflow-y-auto">

                    {/* USERS TAB */}
                    {activeTab === 'users' && (
                        <div className="flex flex-col gap-6">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="New Lab Member Name"
                                    className="input input-bordered w-full"
                                    value={newLabMember}
                                    onChange={e => setNewLabMember(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleAddMember()}
                                />
                                <button className="btn btn-primary" onClick={handleAddMember} disabled={!newLabMember}>Add</button>
                            </div>

                            <div className="bg-base-200 rounded-xl p-4 border border-base-300">
                                <h3 className="text-sm font-bold uppercase text-base-content/50 mb-4">Configured Users</h3>
                                <div className="flex flex-col gap-2">
                                    {settings.labMembers.length === 0 ? <span className="text-sm italic opacity-50">No users configured.</span> : null}
                                    {settings.labMembers.map(user => (
                                        <div key={user} className="flex justify-between items-center bg-base-100 p-2 px-4 rounded shadow-sm border border-base-content/5">
                                            <span className="font-mono">{user}</span>
                                            <button className="btn btn-xs btn-error btn-outline" onClick={() => handleRemoveMember(user)}>Remove</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* RECORDING TYPES TAB */}
                    {activeTab === 'types' && (
                        <div className="flex flex-col gap-6">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="New Recording Protocol"
                                    className="input input-bordered w-full font-mono"
                                    value={newRecType}
                                    onChange={e => setNewRecType(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ''))}
                                    onKeyDown={e => e.key === 'Enter' && handleAddType()}
                                />
                                <button className="btn btn-primary" onClick={handleAddType} disabled={!newRecType}>Add</button>
                            </div>

                            <div className="bg-base-200 rounded-xl p-4 border border-base-300">
                                <h3 className="text-sm font-bold uppercase text-base-content/50 mb-4">Configured Protocols</h3>
                                <div className="flex flex-col gap-2">
                                    {settings.recordingTypes.length === 0 ? <span className="text-sm italic opacity-50">No types configured.</span> : null}
                                    {settings.recordingTypes.map(type => (
                                        <div key={type} className="flex justify-between items-center bg-base-100 p-2 px-4 rounded shadow-sm border border-base-content/5">
                                            <span className="font-mono">{type}</span>
                                            <button className="btn btn-xs btn-error btn-outline" onClick={() => handleRemoveType(type)}>Remove</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* CAMERAS TAB */}
                    {activeTab === 'cameras' && (
                        <div className="flex flex-col gap-8">

                            {/* Frigate Base URL */}
                            <div>
                                <label className="label py-1"><span className="label-text font-bold">Frigate API Base URL</span></label>
                                <div className="flex gap-2">
                                    <input
                                        type="url"
                                        className="input input-bordered w-full font-mono text-sm"
                                        value={settings.frigateBaseUrl}
                                        onChange={e => updateFrigateUrl(e.target.value)}
                                    />
                                </div>
                            </div>

                            <hr className="border-base-300" />

                            {/* Cameras List */}
                            <div className="flex flex-col gap-4">
                                <h3 className="text-sm font-bold uppercase text-base-content/50">Camera Mappings</h3>

                                <div className="flex gap-2 items-end bg-base-200 p-4 rounded-xl border border-base-300">
                                    <div className="flex-1">
                                        <label className="label py-1"><span className="label-text text-xs">Frigate Camera ID</span></label>
                                        <input
                                            type="text"
                                            placeholder="e.g. pi_cam_2"
                                            className="input input-sm input-bordered w-full font-mono"
                                            value={newCamId}
                                            onChange={e => setNewCamId(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <label className="label py-1"><span className="label-text text-xs">Display Label</span></label>
                                        <input
                                            type="text"
                                            placeholder="e.g. Chamber 2"
                                            className="input input-sm input-bordered w-full"
                                            value={newCamLabel}
                                            onChange={e => setNewCamLabel(e.target.value)}
                                            onKeyDown={e => e.key === 'Enter' && handleAddCamera()}
                                        />
                                    </div>
                                    <button className="btn btn-sm btn-primary mb-[2px]" onClick={handleAddCamera} disabled={!newCamId || !newCamLabel}>Add</button>
                                </div>

                                <div className="flex flex-col gap-2">
                                    {settings.cameras.length === 0 ? <span className="text-sm italic opacity-50 p-2">No cameras configured.</span> : null}
                                    {settings.cameras.map(cam => (
                                        <div key={cam.id} className="flex justify-between items-center bg-base-100 p-3 rounded shadow-sm border border-base-content/10">
                                            <div className="flex flex-col">
                                                <span className="font-bold">{cam.label}</span>
                                                <span className="text-xs font-mono text-base-content/50">{cam.id}</span>
                                            </div>
                                            <button className="btn btn-xs btn-error btn-ghost" onClick={() => handleRemoveCamera(cam.id)}>Remove</button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                        </div>
                    )}

                </div>

            </div>
        </div>
    );
}
