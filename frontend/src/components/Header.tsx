import React from 'react';

interface HeaderProps {
  onOpenInfo: () => void;
  onOpenPricing: () => void;
  onToggleSidebar?: () => void;
  activePlanTier?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenInfo,
  onOpenPricing,
  onToggleSidebar,
  activePlanTier = 'Free plan',
}) => {
  return (
    <header
      className="h-14 px-4 sm:px-6 flex items-center justify-between bg-transparent z-10 flex-shrink-0"
      data-purpose="workspace-header"
    >
      {/* Left: Sidebar toggle if on mobile */}
      <div className="flex items-center gap-2">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-1.5 rounded-lg text-[#A89885] hover:text-[#FAF6F0] hover:bg-[#252736] transition-colors cursor-pointer"
            title="Toggle sidebar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        )}
      </div>

      {/* Center: "Free plan · Upgrade" pill (Sandal styled) */}
      <div className="flex items-center">
        <button
          onClick={onOpenPricing}
          className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-semibold text-[#3C2719] hover:text-[#1F140D] bg-[#FAF7F2] hover:bg-[#F2ECE2] border border-[#D8C9B9] transition-all shadow-xs cursor-pointer active:scale-95"
        >
          <span>{activePlanTier}</span>
          <span className="text-[#A89280]">·</span>
          <span className="text-[#B36B39] hover:text-[#9B4518] font-bold">Upgrade</span>
        </button>
      </div>

      {/* Right: Info / Help modal */}
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenInfo}
          className="w-8 h-8 rounded-full border border-[#D8C9B9] bg-[#FAF7F2] flex items-center justify-center text-[#786556] hover:bg-[#F2ECE2] hover:text-[#2A1D15] transition-colors cursor-pointer shadow-xs"
          title="Info & Documentation"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
            ></path>
          </svg>
        </button>
      </div>
    </header>
  );
};
