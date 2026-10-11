import React, { useState, useRef, useEffect } from 'react';
import type { ModelOption } from '../types/chat';

interface AttachedFile {
  file: File;
  name: string;
  size: number;
  type: string;
  previewUrl?: string;
}

interface ComposerProps {
  onSendMessage: (text: string, attachedFile?: AttachedFile | null) => void;
  isGenerating: boolean;
  onAbort?: () => void;
  onShowToast: (msg: string) => void;
  currentModel: ModelOption;
  onSelectModel: (model: ModelOption) => void;
}

export const Composer: React.FC<ComposerProps> = ({
  onSendMessage,
  isGenerating,
  onAbort,
  onShowToast,
  currentModel,
  onSelectModel,
}) => {
  const [input, setInput] = useState('');
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Close model dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsModelDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 200)}px`;
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = input.trim();
    if ((!trimmed && !attachedFile) || isGenerating) return;

    onSendMessage(trimmed || `Please analyze the attached file: ${attachedFile?.name}`, attachedFile);
    setInput('');
    setAttachedFile(null);
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const isPdf = file.name.endsWith('.pdf');
      const isDoc = file.name.endsWith('.docx') || file.name.endsWith('.doc');
      const fileType = isPdf ? 'PDF' : isDoc ? 'DOC' : file.type.split('/')[1]?.toUpperCase() || 'FILE';

      const fileObj: AttachedFile = {
        file,
        name: file.name,
        size: file.size,
        type: fileType,
        previewUrl: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
      };

      setAttachedFile(fileObj);
      onShowToast(`Uploaded ${file.name} to chat.`);
    }
  };

  const modelLabels: Record<ModelOption, { name: string; isLocal: boolean }> = {
    'qwen2.5:3b': { name: 'Qwen 2.5 3B', isLocal: true },
    'deepseek-r1:1.5b': { name: 'DeepSeek R1', isLocal: true },
    'llama3.2:3b': { name: 'Llama 3.2 3B', isLocal: true },
    'claude-3-7-sonnet': { name: 'Sonnet 3.7', isLocal: false },
  };

  const activeModelMeta = modelLabels[currentModel] || { name: currentModel, isLocal: true };

  return (
    <div className="w-full max-w-3xl px-2 sm:px-0 relative" data-purpose="claude-style-composer">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.docx,.txt,.md,.csv,.json,.png,.jpg,.jpeg"
      />

      {/* Main Composer Box in Sandal Palette */}
      <div className="bg-[#FAF7F2] rounded-2xl border-2 border-[#D8C9B9] shadow-[0_12px_32px_rgba(45,33,26,0.12),0_2px_8px_rgba(45,33,26,0.06)] p-3.5 sm:p-4.5 flex flex-col gap-2.5 focus-within:border-[#B36B39] transition-all">
        {/* Render Attached File Pill inside Composer */}
        {attachedFile && (
          <div className="inline-flex items-center gap-3 p-2 bg-[#EFE7DC] rounded-xl border border-[#D5C6B5] text-xs text-[#2A1D15] max-w-sm self-start animate-in fade-in shadow-xs">
            {attachedFile.previewUrl ? (
              <img src={attachedFile.previewUrl} alt="preview" className="w-10 h-10 rounded-lg object-cover" />
            ) : (
              <div className="w-10 h-10 rounded-lg bg-[#DFD4C6] flex flex-col items-center justify-center text-[#9B4518] font-bold text-[10px] uppercase">
                <span>📄</span>
                <span>{attachedFile.type}</span>
              </div>
            )}
            <div className="min-w-0 pr-2">
              <p className="font-semibold text-xs truncate max-w-[200px] text-[#2A1D15]">{attachedFile.name}</p>
              <span className="text-[10px] text-[#786556]">
                {(attachedFile.size / 1024).toFixed(1)} KB · {attachedFile.type}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setAttachedFile(null)}
              className="p-1 rounded-full text-[#786556] hover:text-[#2A1D15] hover:bg-[#DFD4C6] cursor-pointer"
              title="Remove file"
            >
              ✕
            </button>
          </div>
        )}

        {/* Text Input Textarea */}
        <textarea
          ref={inputRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="How can I help you today?"
          disabled={isGenerating}
          rows={1}
          className="w-full bg-transparent border-none text-sm sm:text-base text-[#251A13] placeholder-[#8F7D70] focus:outline-none focus:ring-0 resize-none font-normal leading-relaxed min-h-[40px] max-h-[190px]"
        />

        {/* Bottom Toolbar: [+] Attachment, Model Switcher Toggle, [↑] Send */}
        <div className="flex items-center justify-between pt-1.5 border-t border-[#E8DDD1]">
          {/* Left: [+] Add Attachment Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-8 h-8 rounded-full text-[#786556] hover:text-[#251A13] hover:bg-[#EFE7DC] flex items-center justify-center transition-colors cursor-pointer text-lg font-light"
            title="Add attachment (PDF, Docs, Data)"
          >
            +
          </button>

          {/* Right: Model Dropdown & Send Button */}
          <div className="flex items-center gap-2.5">
            {/* Model Selector Popover Toggle (Clean Model Name Only - No tags) */}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold text-[#3C2719] hover:text-[#1F140D] bg-[#EFE7DC] hover:bg-[#E5DACB] transition-all cursor-pointer border border-[#D5C6B5] shadow-xs active:scale-95"
              >
                <span>{activeModelMeta.name}</span>
                <svg className="w-3 h-3 text-[#7B5940]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                </svg>
              </button>

              {/* Model Dropdown Menu */}
              {isModelDropdownOpen && (
                <div className="absolute right-0 bottom-full mb-2 w-60 bg-[#FAF7F2] rounded-2xl border-2 border-[#D8C9B9] shadow-[0_16px_40px_rgba(45,33,26,0.2)] p-2 z-50 animate-in fade-in slide-in-from-bottom-2">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase text-[#8C7A6D] tracking-wider border-b border-[#E8DDD1] mb-1">
                    Select Model
                  </div>
                  {(Object.keys(modelLabels) as ModelOption[]).map((mKey) => {
                    const mInfo = modelLabels[mKey];
                    const isSelected = currentModel === mKey;
                    return (
                      <button
                        key={mKey}
                        type="button"
                        onClick={() => {
                          onSelectModel(mKey);
                          setIsModelDropdownOpen(false);
                          onShowToast(`Switched active model to ${mInfo.name}`);
                        }}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-colors cursor-pointer font-medium ${
                          isSelected
                            ? 'bg-[#B36B39] text-[#FAF6F0] font-bold shadow-xs'
                            : 'text-[#4A382C] hover:text-[#251A13] hover:bg-[#EFE7DC]'
                        }`}
                      >
                        <span>{mInfo.name}</span>
                        {isSelected && (
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                          </svg>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Send Button or Stop Button with Kite Icon & Minimal Animation */}
            {isGenerating ? (
              <button
                type="button"
                onClick={onAbort}
                className="w-9 h-9 rounded-full bg-red-600 text-white flex items-center justify-center shadow-md hover:bg-red-700 transition-all cursor-pointer active:scale-95"
                title="Stop generation"
              >
                <div className="w-2.5 h-2.5 bg-white rounded-xs" />
              </button>
            ) : (
              <button
                type="button"
                onClick={() => handleSubmit()}
                disabled={!input.trim() && !attachedFile}
                className="relative group w-9 h-9 rounded-full bg-gradient-to-tr from-[#9B4518] to-[#C46835] disabled:from-[#D8C7B5] disabled:to-[#C9B7A3] text-white disabled:text-[#8E7E70] flex items-center justify-center shadow-[0_3px_10px_rgba(155,69,24,0.3)] hover:shadow-[0_5px_14px_rgba(155,69,24,0.4)] transition-all duration-200 cursor-pointer disabled:cursor-not-allowed hover:scale-102 active:scale-95"
                title="Send (Fly Kite)"
              >
                {/* Kite Icon */}
                <svg
                  className="w-4 h-4 transform group-hover:-translate-y-0.5 group-hover:-rotate-6 transition-transform duration-200"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path d="M12 2.5L19.5 9.5L12 21.5L4.5 9.5L12 2.5Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M12 2.5V21.5" strokeWidth="1.5" strokeLinecap="round" />
                  <path d="M4.5 9.5H19.5" strokeWidth="1.5" strokeLinecap="round" />
                  <path d="M12 21.5L14 23.5" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
