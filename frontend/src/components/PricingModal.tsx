import React from 'react';

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPlan?: (planId: string) => void;
  activePlanTier?: string;
}

export const PricingModal: React.FC<PricingModalProps> = ({
  isOpen,
  onClose,
  onSelectPlan,
  activePlanTier = 'Free plan',
}) => {
  if (!isOpen) return null;

  // Determine currently active plan id
  const getActivePlanId = (tierStr: string): string => {
    const t = tierStr.toLowerCase();
    if (t.includes('pro')) return 'pro_10';
    if (t.includes('team')) return 'team_20';
    if (t.includes('paid') || t.includes('enterprise')) return 'enterprise_50';
    return 'free';
  };

  const activePlanId = getActivePlanId(activePlanTier);

  const plans = [
    {
      id: 'free',
      name: 'Free (Default)',
      price: '$0',
      period: 'forever',
      description: 'Core tactical growth assistance running on local GPU hardware.',
      highlight: false,
      badge: 'Default Tier',
      features: [
        'Local GPU acceleration (CUDA on RTX 2050)',
        'Qwen 2.5 3B (Fast ~44 tok/s)',
        'DeepSeek R1 1.5B with Chain of Thought',
        'Llama 3.2 3B Drafting',
        'Strict Lenny transcript citations (303 episodes)',
        'Standard Reciprocal Rank Fusion search',
      ],
    },
    {
      id: 'pro_10',
      name: 'Pro',
      price: '$10',
      period: '/ month',
      description: 'For startup operators requiring faster throughput and Claude frontier intelligence.',
      highlight: true,
      badge: 'Most Popular',
      features: [
        'Everything in Free',
        'Claude 3.7 Sonnet (100 cloud queries/day)',
        'Unlimited interactive HTML/CSS sandboxed artifacts',
        'Automated Ship 30 for 30 essay generation & scoring',
        'High-priority local GPU queue',
        'Supabase cloud sync across devices',
      ],
    },
    {
      id: 'team_20',
      name: 'Team',
      price: '$20',
      period: '/ month / seat',
      description: 'For product & growth teams collaborating on shared strategy and frameworks.',
      highlight: false,
      badge: 'Team Power',
      features: [
        'Everything in Pro',
        'Claude 3.7 Sonnet & Opus with high rate limits',
        'Team Transcripts S3 Archive & shared knowledge base',
        'Export conversations to S3 / JSON with one click',
        'Dedicated Supabase team schema',
        'Centralized model usage & token analytics',
      ],
    },
    {
      id: 'enterprise_50',
      name: 'Enterprise',
      price: '$50',
      period: '/ month',
      description: 'Dedicated enterprise infrastructure with custom database instance, fine-tuned models, and 99.9% SLA.',
      highlight: false,
      badge: 'Enterprise',
      features: [
        'Everything in Team',
        'Dedicated Supabase PostgreSQL instance',
        'Automated cloud storage sync for all chats & attachments',
        'Real-time tokens usage & cost monitoring tables',
        'Custom fine-tuned models for internal company playbooks',
        '99.9% uptime SLA & dedicated support',
      ],
    },
  ];

  const handleSelect = (planId: string) => {
    if (onSelectPlan) {
      onSelectPlan(planId);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-xs animate-in fade-in">
      <div className="bg-[#181922] text-[#FAF6F0] rounded-3xl max-w-5xl w-full p-6 sm:p-8 shadow-2xl border border-[#2d2f3c] relative max-h-[92vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between pb-6 border-b border-[#2d2f3c]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl text-amber-500 font-bold">✻</span>
              <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-[#FAF6F0]">
                Choose your Lenny Growth plan
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-[#A89885] mt-1.5">
              Supercharge your product & growth workflows. Easily switch between Free, Pro, Team, or Enterprise anytime.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-[#A89885] hover:text-[#FAF6F0] hover:bg-[#252736] transition-colors cursor-pointer"
            title="Close modal"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        </div>

        {/* Pricing Cards Grid with Interactive Hover Highlights & Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          {plans.map((p) => {
            const isActive = p.id === activePlanId;

            return (
              <div
                key={p.id}
                onClick={() => handleSelect(p.id)}
                className={`group rounded-2xl p-5 flex flex-col justify-between border transition-all duration-200 cursor-pointer select-none ${
                  isActive
                    ? 'bg-gradient-to-b from-[#252a22] to-[#151c16] border-emerald-500 shadow-xl ring-2 ring-emerald-500/50 hover:border-emerald-400 hover:-translate-y-1'
                    : p.highlight
                    ? 'bg-gradient-to-b from-[#2a2428] to-[#1c1d28] border-amber-600/70 shadow-lg hover:border-amber-400 hover:shadow-2xl hover:shadow-amber-500/20 hover:-translate-y-1.5'
                    : 'bg-[#14151e] border-[#2d2f3c] hover:border-amber-400/80 hover:bg-[#1a1c29] hover:shadow-2xl hover:shadow-amber-500/15 hover:-translate-y-1.5'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-[#FAF6F0] group-hover:text-amber-300 transition-colors">
                      {p.name}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isActive
                          ? 'bg-emerald-600 text-white'
                          : p.highlight
                          ? 'bg-amber-600 text-white'
                          : 'bg-[#252736] text-[#A89885] group-hover:bg-amber-900/60 group-hover:text-amber-200'
                      }`}
                    >
                      {isActive ? '✓ Active Plan' : p.badge}
                    </span>
                  </div>

                  <div className="mt-3 flex items-baseline gap-1">
                    <span className="text-2xl sm:text-3xl font-extrabold text-[#FAF6F0] group-hover:text-amber-200 transition-colors">
                      {p.price}
                    </span>
                    <span className="text-xs text-[#A89885]">{p.period}</span>
                  </div>

                  <p className="text-[11px] text-[#A89885] mt-2 leading-relaxed min-h-[36px]">
                    {p.description}
                  </p>

                  <div className="mt-5 space-y-2 border-t border-[#2d2f3c]/60 pt-4 text-xs">
                    {p.features.map((f, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-[11px] text-[#D7CEBE]">
                        <svg
                          className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${
                            isActive ? 'text-emerald-400' : 'text-amber-400'
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                        </svg>
                        <span>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelect(p.id);
                  }}
                  className={`w-full mt-6 py-2 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-emerald-700 hover:bg-emerald-600 text-white shadow-md'
                      : p.id === 'free'
                      ? 'bg-[#2E241E] hover:bg-amber-600 hover:text-white text-amber-200 border border-amber-500/40 shadow-sm active:scale-95'
                      : p.highlight
                      ? 'bg-gradient-to-tr from-amber-600 to-amber-500 text-[#FAF6F0] hover:brightness-110 shadow-md active:scale-95'
                      : 'bg-[#FAF6F0] text-[#171822] hover:bg-amber-400 hover:text-black active:scale-95'
                  }`}
                >
                  {isActive
                    ? '✓ Currently Active'
                    : p.id === 'free'
                    ? 'Switch to Free (Default)'
                    : `Switch to ${p.name}`}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
