import React from 'react';
import type { ModelOption } from '../types/chat';

interface ModelSelectorProps {
  currentModel: ModelOption;
  onSelectModel: (model: ModelOption) => void;
  disabled?: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  currentModel,
  onSelectModel,
  disabled = false,
}) => {
  const models: { id: ModelOption; label: string; badge: string; isLocal: boolean }[] = [
    {
      id: 'qwen2.5:3b',
      label: 'Qwen 2.5 3B',
      badge: '~44 tok/s Local',
      isLocal: true,
    },
    {
      id: 'deepseek-r1:1.5b',
      label: 'DeepSeek R1',
      badge: 'Reasoning Local',
      isLocal: true,
    },
    {
      id: 'llama3.2:3b',
      label: 'Llama 3.2 3B',
      badge: '~32 tok/s Local',
      isLocal: true,
    },
    {
      id: 'claude-3-7-sonnet',
      label: 'Claude Sonnet 3.7',
      badge: 'Frontier Cloud',
      isLocal: false,
    },
  ];

  return (
    <div className="mt-2.5 inline-flex items-center p-0.5 rounded-xl bg-[#E2D5C3] border border-[#D3C3AF] text-[11px] font-medium text-[#5F544F] shadow-inner select-none flex-wrap justify-center gap-0.5">
      {models.map((m) => {
        const isActive = currentModel === m.id;
        return (
          <button
            key={m.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelectModel(m.id)}
            className={`px-3 py-1 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer ${
              isActive
                ? 'bg-[#FAF6F0] text-[#231F20] font-bold shadow-xs'
                : 'hover:text-[#231F20] text-[#6B5A4D] hover:bg-[#FAF6F0]/40'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <span>{m.label}</span>
            <span
              className={`text-[9px] px-1.5 py-0.2 rounded font-semibold ${
                isActive
                  ? m.isLocal
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                  : 'bg-[#DFCFBA] text-[#5A4638]'
              }`}
            >
              {m.badge}
            </span>
          </button>
        );
      })}
    </div>
  );
};
