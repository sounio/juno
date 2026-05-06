"use client";

export function Sidebar({
  open,
  onToggle,
  sessionId,
  isConnected,
}: {
  open: boolean;
  onToggle: () => void;
  sessionId: string;
  isConnected: boolean;
}) {
  const sessions = [
    { id: sessionId, title: "Current Session", active: true },
  ];

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-20"
          onClick={onToggle}
        />
      )}
      <aside
        className={`${
          open ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-72 bg-neutral-900 border-r border-neutral-800 flex flex-col transition-transform duration-200`}
      >
        <div className="flex items-center justify-between px-4 h-14 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
            <span className="font-semibold">Juno</span>
          </div>
          <button
            onClick={onToggle}
            className="lg:hidden p-1 hover:bg-neutral-800 rounded"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {sessions.map((s) => (
            <button
              key={s.id}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                s.active
                  ? "bg-neutral-800 text-neutral-100"
                  : "text-neutral-400 hover:bg-neutral-800/50"
              }`}
            >
              <div className="truncate">{s.title}</div>
            </button>
          ))}
        </div>

        <div className="p-3 border-t border-neutral-800 space-y-2">
          <div className="flex items-center gap-2 px-3 py-2 text-xs text-neutral-500">
            <span className={`inline-block w-1.5 h-1.5 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
            {isConnected ? "Connected" : "Disconnected"}
          </div>
        </div>
      </aside>
    </>
  );
}
