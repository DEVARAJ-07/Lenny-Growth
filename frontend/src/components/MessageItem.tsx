import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message, Artifact } from '../types/chat';

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: (artifact: Artifact) => void;
  onShowToast: (msg: string) => void;
  onRegenerate?: () => void;
  isLast?: boolean;
  isGenerating?: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onOpenArtifact,
  onShowToast,
  onRegenerate,
  isLast = false,
  isGenerating = false,
}) => {
  const [activeTab, setActiveTab] = useState<'html' | 'css' | 'js'>('js');
  const [isThoughtOpen, setIsThoughtOpen] = useState(false);
  const [hasCopied, setHasCopied] = useState(false);
  const [hasCopiedCode, setHasCopiedCode] = useState(false);

  const isUser = message.role === 'user';

  // Extract <think> blocks if present (from DeepSeek-R1)
  let rawContent = message.content;
  let thoughtProcess = message.thought || '';

  if (rawContent.includes('<think>')) {
    const parts = rawContent.split('</think>');
    if (parts.length > 1) {
      thoughtProcess = parts[0].replace('<think>', '').trim();
      rawContent = parts[1].trim();
    } else {
      thoughtProcess = rawContent.replace('<think>', '').trim();
      rawContent = '';
    }
  }

  // Extract snippet per language if multiple are detected
  const getCodeSnippet = (lang: string) => {
    const regex = new RegExp(`\`\`\`${lang}\\s*([\\s\\S]*?)\`\`\``, 'i');
    const match = rawContent.match(regex);
    return match ? match[1].trim() : null;
  };

  const htmlCode = getCodeSnippet('html');
  const cssCode = getCodeSnippet('css');
  const jsCode = getCodeSnippet('javascript') || getCodeSnippet('js');

  const showCodeTabs = Boolean(htmlCode || cssCode || jsCode);
  const currentCode =
    activeTab === 'html' ? htmlCode : activeTab === 'css' ? cssCode : jsCode || htmlCode || cssCode || '';

  const handleCopyCode = () => {
    if (currentCode) {
      navigator.clipboard.writeText(currentCode);
      setHasCopiedCode(true);
      onShowToast('Code copied to clipboard!');
      setTimeout(() => setHasCopiedCode(false), 2000);
    }
  };

  const handleCopyFullMessage = () => {
    if (message.content) {
      navigator.clipboard.writeText(message.content);
      setHasCopied(true);
      onShowToast(isUser ? 'Question copied!' : 'Response copied!');
      setTimeout(() => setHasCopied(false), 2000);
    }
  };

  const formatMessageTime = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return '';
      return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true });
    } catch {
      return '';
    }
  };

  const timeString = formatMessageTime(message.created_at);

  // 1. User Message (Claude-Style Right Bubble with Hover Copy Button)
  if (isUser) {
    return (
      <div className="w-full max-w-3xl flex justify-end group py-1">
        <div className="relative max-w-[85%] flex items-start gap-2">
          {/* Quick Copy Button on Hover */}
          <button
            type="button"
            onClick={handleCopyFullMessage}
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 p-1.5 rounded-lg bg-[#FAF5EE] hover:bg-[#EDE3D4] border border-[#D5C4B0] text-[#735E4E] hover:text-[#251A13] shadow-xs cursor-pointer flex-shrink-0 mt-1"
            title="Copy question"
            aria-label="Copy question"
          >
            {hasCopied ? (
              <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                ></path>
              </svg>
            )}
          </button>

          {/* User Bubble with Timestamp at Right Bottom */}
          <div className="flex flex-col bg-[#EFE5D6] text-[#251A13] px-4.5 py-3 rounded-2xl rounded-tr-md border border-[#DACBB8] shadow-xs font-sans text-sm sm:text-[14px] leading-relaxed">
            <div>{message.content}</div>
            {timeString && (
              <div className="self-end mt-1 text-[11px] font-medium text-[#8C7665] select-none tracking-tight">
                {timeString}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 2. Assistant Message (Claude-Style Clean, Flexible, Fully Visible Box)
  return (
    <article
      className="w-full max-w-3xl bg-[#FAF7F2] rounded-2xl border border-[#E4D7C5] p-5 sm:p-7 relative transition-all text-[#241A14] shadow-xs group"
      data-purpose="assistant-response-card"
    >
      {/* DeepSeek Reasoning Process Accordion */}
      {thoughtProcess && (
        <div className="mb-4 relative z-10">
          <button
            onClick={() => setIsThoughtOpen(!isThoughtOpen)}
            className="w-full flex items-center justify-between px-3.5 py-2 bg-[#EBE0D2] rounded-xl border border-[#DFCFBA] text-left text-xs font-semibold text-[#5A4638] hover:bg-[#E4D8CB] transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-600 animate-pulse"></span>
              <span>Reasoning Process ({isThoughtOpen ? 'Hide' : 'Show'})</span>
            </div>
            <svg
              className={`w-3.5 h-3.5 transform transition-transform ${isThoughtOpen ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
            </svg>
          </button>
          {isThoughtOpen && (
            <div className="mt-2 p-3 bg-[#FAF7F2] rounded-xl border border-[#E6DAC8] text-xs font-mono text-[#5F544F] whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto">
              {thoughtProcess}
            </div>
          )}
        </div>
      )}

      {/* Thinking Shimmer while awaiting first tokens */}
      {!rawContent.trim() ? (
        <div className="py-2.5 space-y-3.5 animate-in fade-in duration-300">
          <div className="flex items-center gap-2.5">
            <div className="relative w-5 h-5 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-2 border-amber-600/30 border-t-amber-600 animate-spin" />
              <div className="w-2 h-2 rounded-full bg-[#B36B39] animate-ping" />
            </div>
            <span className="text-xs font-semibold text-[#8C603D] animate-pulse font-sans">
              Generating response...
            </span>
          </div>

          <div className="space-y-2">
            <div className="h-3.5 bg-gradient-to-r from-[#EFE6D8] via-[#FAF6F0] to-[#EFE6D8] rounded-full animate-pulse w-4/5" />
            <div className="h-3.5 bg-gradient-to-r from-[#EFE6D8] via-[#FAF6F0] to-[#EFE6D8] rounded-full animate-pulse w-3/5" />
            <div className="h-3.5 bg-gradient-to-r from-[#EFE6D8] via-[#FAF6F0] to-[#EFE6D8] rounded-full animate-pulse w-2/3" />
          </div>
        </div>
      ) : (
        <>
          {/* Code Header Bar: Language Tabs & Copy Button (When code snippets exist) */}
          {showCodeTabs && (
            <div className="flex items-center justify-between pb-3 relative z-10 border-b border-[#E6DAC8] mb-3">
              <div
                className="inline-flex p-1 bg-[#EBE0D2] rounded-xl text-xs font-semibold text-[#5A4638] space-x-1 border border-[#DFCFBA]"
                id="language-tab-bar"
              >
                {htmlCode && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('html')}
                    className={`px-3.5 py-1 rounded-lg transition-all cursor-pointer ${
                      activeTab === 'html'
                        ? 'bg-[#FAF6F0] text-[#231F20] shadow-sm font-bold border border-[#DFCFBA]/50'
                        : 'text-[#6B5A4D] hover:text-[#231F20]'
                    }`}
                  >
                    HTML
                  </button>
                )}
                {cssCode && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('css')}
                    className={`px-3.5 py-1 rounded-lg transition-all cursor-pointer ${
                      activeTab === 'css'
                        ? 'bg-[#FAF6F0] text-[#231F20] shadow-sm font-bold border border-[#DFCFBA]/50'
                        : 'text-[#6B5A4D] hover:text-[#231F20]'
                    }`}
                  >
                    CSS
                  </button>
                )}
                {jsCode && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('js')}
                    className={`px-3.5 py-1 rounded-lg transition-all cursor-pointer ${
                      activeTab === 'js'
                        ? 'bg-[#FAF6F0] text-[#231F20] shadow-sm font-bold border border-[#DFCFBA]/50'
                        : 'text-[#6B5A4D] hover:text-[#231F20]'
                    }`}
                  >
                    JS
                  </button>
                )}
              </div>

              <button
                type="button"
                onClick={handleCopyCode}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#FAF6F0] hover:bg-[#F3EBE1] border border-[#D5C4B0] text-[#231F20] text-xs font-semibold rounded-lg shadow-xs transition-all cursor-pointer"
              >
                {hasCopiedCode ? (
                  <>
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                    </svg>
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5 text-[#5A4638]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      ></path>
                    </svg>
                    <span>Copy Code</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Full Markdown Content - Completely flexible, No vertical clipping */}
          <div className="prose prose-stone max-w-none text-sm sm:text-[14.5px] leading-relaxed text-[#241A14] font-sans break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{rawContent}</ReactMarkdown>
            {isGenerating && isLast && (
              <span className="inline-block w-2 h-4 ml-1 bg-[#B36B39] animate-pulse align-middle rounded-xs" />
            )}
          </div>

          {/* Artifact Pill */}
          {message.artifact && (
            <div className="mt-4 flex items-center justify-between p-3 px-4 bg-[#EDE4DA] border border-[#DFCFBA] rounded-xl">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
                <span className="text-xs font-semibold text-[#2C2623] font-sans">
                  {message.artifact.title || 'Interactive Growth Artifact Created'}
                </span>
              </div>
              <button
                type="button"
                onClick={() => onOpenArtifact?.(message.artifact!)}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#231F20] hover:text-[#9B4518] bg-[#FAF6F0] px-3.5 py-1.5 rounded-lg border border-[#D5C4B0] shadow-xs hover:shadow transition-all cursor-pointer"
              >
                <span>View Sandbox</span>
              </button>
            </div>
          )}

          {/* Claude-Style Action Bar at Bottom of Response */}
          <div className="mt-4 pt-3 flex items-center justify-between border-t border-[#E8DDD1]/80 text-xs text-[#735E4E]">
            {/* Left: Quick Actions (Copy Response, Feedback) */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleCopyFullMessage}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[#735E4E] hover:text-[#231F20] hover:bg-[#EBE0D2] transition-colors cursor-pointer text-xs font-medium"
                title="Copy response"
              >
                {hasCopied ? (
                  <>
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5"></path>
                    </svg>
                    <span className="text-emerald-700 font-semibold">Copied!</span>
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      ></path>
                    </svg>
                    <span>Copy</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => onShowToast('Helpful feedback recorded')}
                className="p-1.5 text-[#735E4E] hover:text-[#231F20] rounded-lg hover:bg-[#EBE0D2] transition-colors cursor-pointer"
                title="Helpful"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                  ></path>
                </svg>
              </button>

              <button
                type="button"
                onClick={() => onShowToast('Unhelpful feedback recorded')}
                className="p-1.5 text-[#735E4E] hover:text-[#231F20] rounded-lg hover:bg-[#EBE0D2] transition-colors cursor-pointer"
                title="Unhelpful"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                  ></path>
                </svg>
              </button>
            </div>

            {/* Right: Actions & Timestamp on the right side end */}
            <div className="flex items-center gap-2.5">
              {isLast && onRegenerate && (
                <button
                  type="button"
                  onClick={onRegenerate}
                  className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#FAF6F0] hover:bg-[#F3EBE1] border border-[#D5C4B0] text-[#231F20] text-xs font-medium rounded-lg shadow-xs hover:shadow transition-all active:scale-95 cursor-pointer"
                >
                  <svg className="w-3.5 h-3.5 text-[#5A4638]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                    ></path>
                  </svg>
                  <span>Regenerate</span>
                </button>
              )}
              {timeString && (
                <span
                  className="text-[11px] font-medium text-[#8C7665] tracking-tight tabular-nums select-none"
                  title={`Response time: ${timeString}`}
                >
                  {timeString}
                </span>
              )}
            </div>
          </div>
        </>
      )}
    </article>
  );
};
