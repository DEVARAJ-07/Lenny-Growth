import React, { useState } from 'react';
import type { Artifact } from '../types/chat';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
  onShowToast: (msg: string) => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  onClose,
  onShowToast,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  if (!artifact) return null;

  // Prepare sandboxed HTML content with strict CSP and dark theme wrapper if needed
  const secureSandboxSrc = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data: https:;">
  <style>
    body {
      margin: 0;
      padding: 16px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #0e1017;
      color: #EDE4DA;
    }
  </style>
</head>
<body>
  ${artifact.content}
</body>
</html>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    onShowToast('Artifact code copied to clipboard!');
  };

  const handleDownload = () => {
    const blob = new Blob([artifact.content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.toLowerCase().replace(/\s+/g, '-') || 'artifact'}.html`;
    a.click();
    URL.revokeObjectURL(url);
    onShowToast('Downloaded artifact file.');
  };

  return (
    <div
      className="fixed inset-y-0 right-0 w-full sm:w-[540px] lg:w-[640px] bg-[#1a1b24] text-[#FAF6F0] z-50 shadow-2xl border-l border-[#2d2f3c] flex flex-col transform transition-transform duration-300 ease-out"
      data-purpose="sandboxed-artifact-viewer"
    >
      {/* Header */}
      <div className="h-16 px-6 border-b border-[#2d2f3c] flex items-center justify-between bg-[#171822]">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-pulse"></span>
          <div>
            <h3 className="text-sm font-bold text-[#FAF6F0] truncate max-w-xs sm:max-w-md">
              {artifact.title || 'Interactive Growth Artifact'}
            </h3>
            <span className="text-[10px] text-amber-400 font-mono">SANDBOXED IFRAME (NO SAME-ORIGIN)</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#A89885] hover:text-[#FAF6F0] hover:bg-[#252736] transition-colors cursor-pointer"
          title="Close sandbox"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></path>
          </svg>
        </button>
      </div>

      {/* Tabs & Actions Bar */}
      <div className="px-6 py-2.5 bg-[#20222f] border-b border-[#2d2f3c] flex items-center justify-between text-xs">
        {/* Preview / Code Tabs */}
        <div className="inline-flex p-1 bg-[#171822] rounded-lg border border-[#2d2f3c]">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1 rounded-md transition-all font-semibold cursor-pointer ${
              activeTab === 'preview' ? 'bg-brand-500 text-[#FAF6F0] shadow-sm' : 'text-[#A89885] hover:text-[#FAF6F0]'
            }`}
          >
            Preview
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-3 py-1 rounded-md transition-all font-semibold cursor-pointer ${
              activeTab === 'code' ? 'bg-brand-500 text-[#FAF6F0] shadow-sm' : 'text-[#A89885] hover:text-[#FAF6F0]'
            }`}
          >
            Source Code
          </button>
        </div>

        {/* Copy & Download Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#252736] hover:bg-[#2e3144] border border-[#373a4e] text-xs font-semibold text-[#FAF6F0] transition-colors cursor-pointer"
            title="Copy code"
          >
            <svg className="w-3.5 h-3.5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
              ></path>
            </svg>
            <span>Copy</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#252736] hover:bg-[#2e3144] border border-[#373a4e] text-xs font-semibold text-[#FAF6F0] transition-colors cursor-pointer"
            title="Download file"
          >
            <svg className="w-3.5 h-3.5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
              ></path>
            </svg>
            <span>Download</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative bg-[#0e1017]">
        {activeTab === 'preview' ? (
          <iframe
            title="Artifact Preview Sandbox"
            srcDoc={secureSandboxSrc}
            sandbox="allow-scripts"
            className="w-full h-full border-none"
          />
        ) : (
          <pre className="w-full h-full p-4 overflow-auto font-mono text-xs text-[#FAF6F0] bg-[#12141c] leading-relaxed">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};
