import React from 'react';
import type { ModelOption } from '../types/chat';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentModel: ModelOption;
  activePlanTier?: string;
  onOpenPricing?: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  currentModel,
  activePlanTier = 'Free plan',
  onOpenPricing,
}) => {
  if (!isOpen) return null;

  const modelsList = [
    {
      name: 'Qwen 2.5 3B',
      oneLiner: 'Ultra-fast local inference for rapid product insights, metrics, and tactical Q&A.',
      type: 'Local GPU',
    },
    {
      name: 'DeepSeek R1 1.5B',
      oneLiner: 'Specialized reasoning model featuring step-by-step chain-of-thought analysis.',
      type: 'Local GPU',
    },
    {
      name: 'Llama 3.2 3B',
      oneLiner: 'Compact local model optimized for structured frameworks, notes, and outlines.',
      type: 'Local GPU',
    },
    {
      name: 'Claude 3.7 Sonnet',
      oneLiner: 'Frontier cloud intelligence for comprehensive strategic synthesis and artifacts.',
      type: 'Cloud Provider',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in">
      <div className="bg-[#FAF7F2] text-[#2A1D15] rounded-3xl max-w-xl w-full p-6 sm:p-7 shadow-[0_20px_50px_rgba(35,26,20,0.35)] border-2 border-[#D8C9B9] relative max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#E8DDD1]">
          <div className="flex items-center gap-2.5">
            <span className="text-xl text-[#B36B39] font-bold">✻</span>
            <h3 className="text-base sm:text-lg font-serif font-bold text-[#2A1D15]">Settings</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-[#8C7A6D] hover:text-[#2A1D15] hover:bg-[#EFE7DC] transition-colors cursor-pointer"
            title="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="mt-5 space-y-6 text-xs sm:text-[13px]">
          {/* Section 1: Models & One-Liners (Non-selectable in Settings) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[#8C7A6D]">
                Available Models & Architecture
              </h4>
              <span className="text-[11px] text-[#A66030] font-medium bg-[#F3E7DC] px-2 py-0.5 rounded-md border border-[#E3D1C2]">
                Active: {currentModel} (Switch in Composer)
              </span>
            </div>

            <div className="space-y-2.5">
              {modelsList.map((m) => (
                <div
                  key={m.name}
                  className="p-3.5 bg-[#F4EFE7] rounded-xl border border-[#DFD3C4] flex flex-col gap-1 cursor-default select-none transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-[#2A1D15]">{m.name}</span>
                    <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-[#E5DACE] text-[#695444]">
                      {m.type}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#635142] leading-relaxed">
                    {m.oneLiner}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Plan Settings */}
          <div className="p-4 bg-[#F2ECE2] rounded-2xl border border-[#D8C9B9] space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-xs text-[#2A1D15]">Plan Settings</h4>
                <p className="text-[11px] text-[#7A6757] mt-0.5">
                  Current Tier: <span className="font-bold text-[#B36B39]">{activePlanTier}</span>
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  onClose();
                  if (onOpenPricing) onOpenPricing();
                }}
                className="px-3.5 py-1.5 rounded-xl bg-gradient-to-tr from-[#9B4518] to-[#D47135] text-white font-semibold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer active:scale-95"
              >
                Upgrade Plan
              </button>
            </div>
            <p className="text-[11px] text-[#786556] leading-relaxed">
              Upgrade to Pro ($10), Team ($20), or Enterprise ($50) for unlimited cloud reasoning, automated S3 synchronization, and dedicated Supabase schemas.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
