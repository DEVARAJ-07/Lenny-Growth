import React from 'react';
import type { Session } from '../types/chat';

interface HistoryDrawerProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onClearAll: () => void;
  onClose: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onClearAll,
  onClose,
}) => {
  return (
    <aside
      className="w-[280px] min-w-[280px] h-full bg-[#F3EDE4] border-l border-[#DFD3C3] flex flex-col justify-between p-4 z-10 select-none text-[#231F20]"
      data-purpose="history-panel"
    >
      {/* History Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#E0D4C3]">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-bold text-[#231F20]">History</h3>
          <span className="text-[10px] font-bold text-[#5A4638] bg-[#E3D7C7] px-2 py-0.5 rounded-full border border-[#D5C6B3]">
            {sessions.length}/50
          </span>
        </div>
        {/* Dock / Close Button */}
        <button
          onClick={onClose}
          className="w-6 h-6 rounded-md hover:bg-[#E5D9C9] flex items-center justify-center text-[#7E695B] hover:text-[#231F20] transition-colors cursor-pointer"
          title="Collapse history"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
          </svg>
        </button>
      </div>

      {/* History Items List */}
      <div className="flex-1 overflow-y-auto py-3 space-y-2 pr-0.5 font-sans">
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-xs text-[#8C7D73]">
            No conversation history yet. Start asking questions!
          </div>
        ) : (
          sessions.map((sess) => {
            const isActive = sess.id === activeSessionId;
            return (
              <div
                key={sess.id}
                onClick={() => onSelectSession(sess.id)}
                className={`p-2.5 rounded-xl border transition-all cursor-pointer group relative ${
                  isActive
                    ? 'bg-[#FAF6F0] border-[#D5C4B0] shadow-sm'
                    : 'hover:bg-[#EAE0D2] border-transparent hover:border-[#DFCFBA]'
                }`}
              >
                <div className="flex items-start gap-2.5">
                  {/* Indicator Box */}
                  <span
                    className={`w-3.5 h-3.5 mt-0.5 rounded-sm flex items-center justify-center flex-shrink-0 ${
                      isActive
                        ? 'border-2 border-brand-500 bg-brand-500 text-[#FAF6F0]'
                        : 'border border-[#B8A796] group-hover:border-[#7E695B]'
                    }`}
                  >
                    {isActive && (
                      <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          clipRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          fillRule="evenodd"
                        ></path>
                      </svg>
                    )}
                  </span>

                  <div className="flex-1 min-w-0 pr-5">
                    <h5
                      className={`text-xs truncate ${
                        isActive ? 'font-bold text-[#231F20]' : 'font-semibold text-[#433B38] group-hover:text-[#231F20]'
                      }`}
                    >
                      {sess.title}
                    </h5>
                    <p className="text-[10px] text-[#7F726B] truncate mt-0.5">
                      {new Date(sess.updated_at || sess.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>

                  {/* Delete Item Button */}
                  <button
                    onClick={(e) => onDeleteSession(sess.id, e)}
                    className="absolute right-2 top-2 p-1 text-[#8C7D73] hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity rounded cursor-pointer"
                    title="Delete session"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Clear History Button */}
      <div className="pt-3 border-t border-[#E0D4C3]">
        <button
          onClick={onClearAll}
          disabled={sessions.length === 0}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 border border-[#D5C4B0] bg-[#EDE4DA] rounded-xl text-xs font-semibold text-[#433B38] hover:text-red-700 hover:border-red-300 hover:bg-red-50/70 transition-all shadow-2xs cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          id="clear-history-btn"
        >
          <svg className="w-3.5 h-3.5 text-[#7E695B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
            ></path>
          </svg>
          <span>Clear history</span>
        </button>
      </div>
    </aside>
  );
};
