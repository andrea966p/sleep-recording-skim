import { useState, useEffect } from 'react';
import { useStatusPoll } from './hooks/useStatusPoll';
import { useSettings } from './hooks/useSettings';
import { setMetadata, clearMetadata } from './api/client';
import { PendingMetadata } from './types/api';

import { SystemHealth } from './components/SystemHealth';
import { SessionHistory } from './components/SessionHistory';
import { LiveClock } from './components/LiveClock';
import { SettingsModal } from './components/SettingsModal';
import { ChamberSilo } from './components/ChamberSilo';

export default function App() {
  const { status, error, isOffline, sessionEndedTick } = useStatusPoll();
  const { settings, updateFrigateUrl, setCameras, setRecordingTypes, setLabMembers } = useSettings();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Theme state
  const storedTheme = localStorage.getItem('theme');
  const initialTheme = (storedTheme === 'dark' || storedTheme === 'light') ? storedTheme : 'dark';
  const [theme, setTheme] = useState(initialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  // Toast state simple wrapper
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleSetMetadata = async (chamberId: string, data: Partial<PendingMetadata>) => {
    try {
      await setMetadata(chamberId, data as any);
      showToast(`Metadata set for ${chamberId}`);
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    }
  };

  const handleClearMetadata = async (chamberId: string) => {
    try {
      await clearMetadata(chamberId);
      showToast(`Defaults cleared for ${chamberId}`);
    } catch (err: any) {
      showToast(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-base-100 text-base-content p-4 lg:p-6 flex flex-col font-sans relative">

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        updateFrigateUrl={updateFrigateUrl}
        setCameras={setCameras}
        setRecordingTypes={setRecordingTypes}
        setLabMembers={setLabMembers}
      />

      {toastMessage && (
        <div className="toast toast-top toast-end z-50">
          <div className="alert alert-info shadow-lg py-2">
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="flex justify-between items-center mb-6 max-w-[1600px] mx-auto w-full border-b border-base-300 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            NeuroSurveillance <span className="text-primary font-normal">Session Controller</span>
          </h1>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <LiveClock />
            <div className="divider divider-horizontal mx-0"></div>
            <button
              className="btn btn-circle btn-ghost text-base-content/70 hover:text-primary transition-colors"
              onClick={toggleTheme}
              title="Toggle Theme"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-2.227l-1.591 1.591M5.25 12H3m4.227-4.773l1.591 1.591M12 6.75a5.25 5.25 0 100 10.5 5.25 5.25 0 000-10.5v0z" />
              </svg>
            </button>
            <button
              className="btn btn-circle btn-ghost text-base-content/70 hover:text-primary transition-colors"
              onClick={() => setIsSettingsOpen(true)}
              title="System Configuration"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
            </button>
          </div>

          {isOffline && (
            <div className="badge badge-error gap-2 p-3 font-bold shadow-lg shadow-error/20">
              <span className="loading loading-spinner loading-xs"></span>
              Daemon Offline
            </div>
          )}
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-grow max-w-[1600px] mx-auto w-full flex flex-col gap-6 pb-6">

        {/* Dynamic Chamber Grids */}
        {settings.cameras.length === 0 ? (
          <div className="alert alert-info shadow-lg py-4 flex justify-center text-lg w-full max-w-2xl mx-auto">
            No chambers configured. Please click the gear icon to add a camera!
          </div>
        ) : (
          <div className={`grid gap-4 w-full ${settings.cameras.length > 3 ? 'lg:grid-cols-2 lg:max-w-7xl mx-auto' : 'grid-cols-1 lg:max-w-4xl mx-auto'}`}>

            {settings.cameras.map((cam, idx) => {
              // Backend status dictionaries are keyed by chamber_id ("0", "1", ...).
              // Camera IDs (e.g. pi_cam_0) are kept for Frigate preview URLs.
              const chamberId = String(idx);

              return (
                <ChamberSilo
                  key={cam.id}
                  chamberId={chamberId}
                  cam={cam}
                  settings={settings}
                  status={status}
                  error={error}
                  onSetMetadata={handleSetMetadata}
                  onClearMetadata={handleClearMetadata}
                />
              );
            })}

          </div>
        )}

        {/* Global Footer Row: Health & History */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-4 border-t border-base-300 pt-8">
          <div className="lg:col-span-1 min-h-[180px]">
            <SystemHealth />
          </div>
          <div className="lg:col-span-3 min-h-[300px]">
            <SessionHistory refreshTick={sessionEndedTick} />
          </div>
        </div>

      </main>

    </div>
  );
}
