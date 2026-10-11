import React from 'react';
import type { Session } from '../types/chat';
import { DrawnBrandTitle } from './WolfDrawnLogo';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onNewChat: () => void;
  onOpenSettings: () => void;
  onOpenPricing: () => void;
  activePlanTier?: string;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  onOpenSettings,
  onOpenPricing,
  activePlanTier = 'Free plan',
  isCollapsed,
  onToggleCollapse,
}) => {
  if (isCollapsed) {
    return (
      <aside className="w-16 min-w-16 h-full flex flex-col justify-between items-center py-5 bg-[#201712] border-r border-[#3B2B20] text-[#D4C3B2] select-none z-20 transition-all duration-300 ease-in-out">
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={onToggleCollapse}
            className="w-10 h-10 rounded-full overflow-hidden bg-[#FAF5EE] hover:opacity-90 border-2 border-[#B36B39] flex items-center justify-center transition-all cursor-pointer shadow-xs"
            title="Expand Sidebar"
          >
            <img
              src="/wolf_logo.jpg"
              alt="Lenny Growth Assistant"
              className="w-full h-full object-cover"
            />
          </button>
          <button
            onClick={onNewChat}
            className="w-9 h-9 rounded-full bg-[#C46835] hover:bg-[#D97736] flex items-center justify-center text-[#FAF5EE] shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer active:scale-95 group border border-[#E08244]/40"
            title="Start new chat"
            aria-label="New chat"
          >
            <svg
              className="w-4 h-4 text-[#FAF5EE] group-hover:rotate-90 transition-transform duration-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 4.5v15m7.5-7.5h-15" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
            </svg>
          </button>
        </div>

        <button
          onClick={onOpenSettings}
          className="w-9 h-9 rounded-xl hover:bg-[#2E2018] flex items-center justify-center text-[#B3A090] hover:text-[#FAF5EE] transition-colors cursor-pointer"
          title="Settings"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
            ></path>
            <circle cx="12" cy="12" r="3" strokeWidth="2"></circle>
          </svg>
        </button>
      </aside>
    );
  }

  return (
    <aside
      className="w-[285px] min-w-[285px] h-full flex flex-col justify-between p-3.5 text-[#D8C7B5] select-none z-20 border-r border-[#3E2D22] bg-gradient-to-b from-[#241A14] via-[#211712] to-[#1C130E] transition-all duration-300 ease-in-out"
      data-purpose="navigation-sidebar"
    >
      {/* Top Header & New Chat */}
      <div className="flex flex-col space-y-3.5">
        {/* Brand Header with Hand-Drawn Wolf and Drawn Title */}
        <div className="flex items-center justify-between pt-1 gap-2">
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            <div className="w-9 h-9 rounded-full overflow-hidden flex items-center justify-center border-2 border-[#B36B39] flex-shrink-0 bg-[#FAF5EE] shadow-sm">
              <img
                src="/wolf_logo.jpg"
                alt="Lenny Growth Assistant"
                className="w-full h-full object-cover"
              />
            </div>
            <DrawnBrandTitle className="flex-1 overflow-visible" />
          </div>

          <button
            onClick={onToggleCollapse}
            className="text-[#9E8A7A] hover:text-[#FAF5EE] p-1.5 rounded-lg hover:bg-[#2F2118] transition-all cursor-pointer flex-shrink-0"
            title="Collapse sidebar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M15 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        </div>

        {/* Start New Chat Button */}
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl bg-[#2F2118] hover:bg-[#3E2C20] text-[#FAF5EE] font-semibold text-xs border border-[#483528] shadow-xs transition-all cursor-pointer group active:scale-98"
        >
          <div className="w-5 h-5 rounded-full bg-[#C46835] group-hover:bg-[#D97736] flex items-center justify-center flex-shrink-0 transition-colors shadow-xs">
            <svg className="w-3.5 h-3.5 text-white group-hover:rotate-90 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
            </svg>
          </div>
          <span>Start new chat</span>
        </button>

        {/* Recent Chats Section Header */}
        <div className="flex items-center justify-between px-1 pt-1">
          <span className="text-[11px] font-bold text-[#A89280] uppercase tracking-wider">
            Recent chats ({sessions.length})
          </span>
        </div>

        {/* Scrollable Chats List with Dark Brown Hover & High-Contrast Text */}
        <div className="overflow-y-auto max-h-[calc(100vh-340px)] space-y-1 pr-1 font-sans scrollbar-none">
          {sessions.length === 0 ? (
            <div className="text-xs text-[#827163] p-3 text-center italic">
              No recent chats yet
            </div>
          ) : (
            sessions.map((sess) => {
              const isActive = sess.id === activeSessionId;
              return (
                <div
                  key={sess.id}
                  onClick={() => onSelectSession(sess.id)}
                  className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#4A2F20] text-[#FFFDF8] font-bold border border-[#68432E] shadow-sm'
                      : 'text-[#C9B6A5] hover:bg-[#3E271B] hover:text-[#FFFDF8]'
                  }`}
                >
                  <span className="truncate pr-4 flex-1">
                    {sess.title || 'Untitled conversation'}
                  </span>

                  <button
                    onClick={(e) => onDeleteSession(sess.id, e)}
                    className="p-1 rounded text-[#9E8A79] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer flex-shrink-0"
                    title="Delete chat"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
                    </svg>
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Bottom Section: Settings & Selectable Plan & 3D Walking Wolf */}
      <div className="space-y-2 pt-2.5 border-t border-[#3E2D22]">
        {/* Settings Button (Clean, no blue dot) */}
        <button
          onClick={onOpenSettings}
          className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium text-[#C9B6A5] hover:text-[#FFFDF8] hover:bg-[#3E271B] transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2.5">
            <svg className="w-4 h-4 text-[#A89280]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
              ></path>
              <circle cx="12" cy="12" r="3" strokeWidth="2"></circle>
            </svg>
            <span className="font-semibold">Settings</span>
          </div>
        </button>

        {/* Selectable Interactive Plan Card with Hover Reactions */}
        <div
          onClick={onOpenPricing}
          className="group w-full p-2.5 rounded-xl bg-[#281D15] hover:bg-[#3E281C] border border-[#483526] hover:border-amber-400 hover:shadow-lg hover:shadow-amber-900/30 transition-all duration-200 cursor-pointer shadow-xs active:scale-[0.98]"
          title="Click to view or switch plan tiers"
        >
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-[10px] text-[#A69282] group-hover:text-amber-200/90 uppercase tracking-wider font-semibold transition-colors">
                Active Plan
              </span>
              <span className="text-xs font-bold text-[#FAF5EE] group-hover:text-amber-300 transition-colors">
                {activePlanTier}
              </span>
            </div>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-[#3F2B1D] text-[#E0A96D] group-hover:bg-amber-500 group-hover:text-[#1F140D] group-hover:shadow-xs transition-all">
              Switch ▾
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
