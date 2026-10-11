import React from 'react';

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InfoModal: React.FC<InfoModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-[#FAF6F0] rounded-2xl max-w-xl w-full p-6 text-[#231F20] shadow-2xl border border-[#D5C4B0] relative max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#E6DAC8]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center text-[#FAF6F0] font-bold text-xs">
              LG
            </div>
            <h3 className="text-base font-bold text-[#231F20]">The Lenny Growth Assistant</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#8C7D73] hover:text-[#231F20] hover:bg-[#EDE4DA] transition-colors cursor-pointer"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="mt-4 space-y-4 text-xs sm:text-[13px] leading-relaxed text-[#433B38]">
          <section>
            <h4 className="font-bold text-[#231F20] text-sm mb-1">Architecture & Purpose</h4>
            <p>
              Built for Forward Deployed Engineering, this system indexes 303 episodes of Lenny's Podcast transcripts.
              It operates as an internal strategic partner for growth, product, and leadership questions.
            </p>
          </section>

          <section className="bg-[#EDE4DA] p-3.5 rounded-xl border border-[#DFCFBA]">
            <h4 className="font-bold text-[#231F20] mb-1">Strict Grounding & Zero Hallucination</h4>
            <p>
              Every response is bound to transcript excerpts. If a query falls outside the knowledge base
              (e.g., cooking or general trivia), the system refuses immediately without speculating or wasting tokens.
            </p>
          </section>

          <section>
            <h4 className="font-bold text-[#231F20] text-sm mb-1">Hybrid Retrieval (RRF)</h4>
            <p>
              Retrieval uses Reciprocal Rank Fusion combining BM25 keyword matching and 768-dimensional dense vector embeddings
              generated locally via <code className="font-mono bg-[#E2D5C3] px-1 py-0.5 rounded">nomic-embed-text</code>.
            </p>
          </section>

          <section>
            <h4 className="font-bold text-[#231F20] text-sm mb-1">Ship 30 for 30 Atomic Essays</h4>
            <p>
              When prompted for essays or deep-dives, the orchestrator triggers the Ship 30 skill, generating a ~1,250-word
              article with hook, framework, operator citations, and automated scoring validation.
            </p>
          </section>

          <section>
            <h4 className="font-bold text-[#231F20] text-sm mb-1">Security Isolation (Artifacts)</h4>
            <p>
              Interactive HTML/CSS components run inside a sandboxed iframe with strict Content Security Policy and
              <code className="font-mono bg-[#E2D5C3] px-1 py-0.5 rounded">sandbox="allow-scripts"</code> (without <code className="font-mono bg-[#E2D5C3] px-1 py-0.5 rounded">allow-same-origin</code>).
            </p>
          </section>
        </div>

        <div className="mt-6 pt-3 border-t border-[#E6DAC8] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gradient-to-tr from-brand-600 to-brand-500 text-[#FAF6F0] rounded-xl text-xs font-bold shadow-sm hover:opacity-95 cursor-pointer"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
