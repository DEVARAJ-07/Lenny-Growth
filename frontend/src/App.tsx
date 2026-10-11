import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Composer } from './components/Composer';
import { MessageItem } from './components/MessageItem';
import { ArtifactViewer } from './components/ArtifactViewer';
import { PricingModal } from './components/PricingModal';
import { SettingsModal } from './components/SettingsModal';
import { InfoModal } from './components/InfoModal';
import { Toast } from './components/Toast';
import type { Message, Session, Artifact, ModelOption, Citation } from './types/chat';
import { api } from './api/client';

export const App: React.FC = () => {
  // State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentModel, setCurrentModel] = useState<ModelOption>('qwen2.5:3b');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isPricingOpen, setIsPricingOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [activePlanTier, setActivePlanTier] = useState<string>('Free plan');

  const chatScrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isUserScrolledUpRef = useRef<boolean>(false);
  const abortStreamRef = useRef<(() => void) | null>(null);

  // Toast helper
  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((curr) => (curr === msg ? null : curr));
    }, 2500);
  }, []);

  // Handle scroll detection
  const handleScroll = () => {
    if (!chatScrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatScrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 150;
    isUserScrolledUpRef.current = !isAtBottom;
  };

  // Auto scroll chat to follow new tokens
  const scrollToBottom = useCallback((smooth: boolean = false) => {
    if (!chatScrollRef.current) return;
    if (smooth) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    } else {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, []);

  // Follow generating message stream continuously without stutter
  useEffect(() => {
    if (isGenerating && !isUserScrolledUpRef.current) {
      if (chatScrollRef.current) {
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
      }
    }
  }, [messages, isGenerating]);

  // Deduplicate messages helper
  const deduplicateMessages = (msgs: Message[]): Message[] => {
    const seen = new Set<string>();
    return msgs.filter((m) => {
      if (seen.has(m.id)) return false;
      seen.add(m.id);
      return true;
    });
  };

  // Initial load: Fetch recent sessions but start on a clean, blank new chat canvas (Claude AI style)
  useEffect(() => {
    (async () => {
      try {
        const fetchedSessions = await api.fetchSessions();
        setSessions(fetchedSessions);
        setActiveSessionId(null);
        setMessages([]);
      } catch (err) {
        console.warn('Backend loading error:', err);
        setActiveSessionId(null);
        setMessages([]);
      }
    })();
  }, []);

  // Select a session from recent chats
  const handleSelectSession = async (id: string) => {
    if (id === activeSessionId) return;
    try {
      setActiveSessionId(id);
      const detail = await api.fetchSessionDetails(id);
      setMessages(deduplicateMessages(detail.messages));
      isUserScrolledUpRef.current = false;
      setTimeout(() => scrollToBottom(false), 60);
    } catch {
      showToast('Could not load chat messages.');
    }
  };

  // Start new blank chat
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    showToast('New chat ready.');
  };

  // Delete session
  const handleDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteSession(id);
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (activeSessionId === id) {
        if (updated.length > 0) {
          handleSelectSession(updated[0].id);
        } else {
          handleNewChat();
        }
      }
      showToast('Chat deleted.');
    } catch {
      showToast('Could not delete chat.');
    }
  };

  // Send message
  const handleSendMessage = async (
    text: string,
    attachedFile?: { file: File; name: string } | null
  ) => {
    if ((!text.trim() && !attachedFile) || isGenerating) return;

    let targetSessionId = activeSessionId;

    // If new chat, create session first in database
    if (!targetSessionId) {
      try {
        const titleSnippet = text.trim() ? text.trim().slice(0, 36) : 'Document Analysis';
        const newSess = await api.createSession(titleSnippet, 'ollama', currentModel);
        setSessions((prev) => [newSess, ...prev]);
        targetSessionId = newSess.id;
        setActiveSessionId(newSess.id);
      } catch (err) {
        showToast('Error creating new chat session. Check backend status.');
        return;
      }
    }

    // Upload file if attached
    if (attachedFile && targetSessionId) {
      try {
        await api.uploadFile(targetSessionId, attachedFile.file);
      } catch (uploadErr) {
        console.warn('File upload warning:', uploadErr);
      }
    }

    // Append user message immediately
    const userMsgId = 'user-' + Date.now();
    const userMsg: Message = {
      id: userMsgId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    const assistantMsgId = 'asst-' + Date.now();
    const assistantMsgPlaceholder: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      citations: [],
      created_at: new Date().toISOString(),
    };

    isUserScrolledUpRef.current = false;
    setMessages((prev) => [...prev, userMsg, assistantMsgPlaceholder]);
    setIsGenerating(true);
    setTimeout(() => scrollToBottom(true), 50);

    let accumulatedContent = '';
    let accumulatedThought = '';
    let accumulatedCitations: Citation[] = [];

    const abortFn = api.streamMessage(targetSessionId, text, currentModel, {
      onToken: (token) => {
        accumulatedContent += token;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId ? { ...m, content: accumulatedContent } : m
          )
        );
      },
      onThought: (thoughtToken) => {
        accumulatedThought += thoughtToken;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId ? { ...m, thought: accumulatedThought } : m
          )
        );
      },
      onCitations: (citations) => {
        accumulatedCitations = citations;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId ? { ...m, citations: accumulatedCitations } : m
          )
        );
      },
      onArtifact: (art) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId ? { ...m, artifact: art } : m
          )
        );
        setActiveArtifact(art);
        showToast(`Artifact generated: ${art.title}`);
      },
      onDone: () => {
        setIsGenerating(false);
        abortStreamRef.current = null;
        api.fetchSessions().then(setSessions).catch(() => {});
      },
      onError: (err) => {
        setIsGenerating(false);
        abortStreamRef.current = null;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  content:
                    accumulatedContent ||
                    `⚠️ Error: ${err.message || 'Stream disconnected'}. Verify backend on port 8000.`,
                }
              : m
          )
        );
        showToast('Stream interrupted or backend offline.');
      },
    });

    abortStreamRef.current = abortFn;
  };

  const handleAbort = () => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
      setIsGenerating(false);
      showToast('Generation stopped.');
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="w-full max-w-[98vw] 2xl:max-w-[1720px] h-[96vh] bg-[#F7F1E8] rounded-3xl shadow-[0_28px_65px_rgba(28,19,14,0.4),0_0_35px_rgba(179,107,57,0.15)] flex overflow-hidden border-2 border-[#4A3527] ring-1 ring-[#B36B39]/25 relative text-[#251A13] transition-all">
      <Toast message={toastMessage} />

      {/* Claude AI Style Left Sidebar in Dark Sandal & Brown */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onNewChat={handleNewChat}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenPricing={() => setIsPricingOpen(true)}
        activePlanTier={activePlanTier}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Chat Workspace in Sandal Palette */}
      <main
        className="flex-1 bg-gradient-to-b from-[#FAF5ED] via-[#F6EFE5] to-[#EFE6D8] flex flex-col h-full relative overflow-hidden text-[#251A13]"
        data-purpose="chat-workspace"
      >
        {/* Workspace Top Header */}
        <Header
          onOpenInfo={() => setIsInfoOpen(true)}
          onOpenPricing={() => setIsPricingOpen(true)}
          onToggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          activePlanTier={activePlanTier}
        />

        {/* Central Workspace Body */}
        {!hasMessages ? (
          /* Empty / New Chat Canvas (Sandal Theme) */
          <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 pb-20 select-none">
            <Composer
              onSendMessage={handleSendMessage}
              isGenerating={isGenerating}
              onAbort={handleAbort}
              onShowToast={showToast}
              currentModel={currentModel}
              onSelectModel={setCurrentModel}
            />
          </div>
        ) : (
          /* Active Chat Conversation View */
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            <section
              ref={chatScrollRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto p-4 sm:p-6 pb-32 sm:pb-44 space-y-6 flex flex-col items-center"
              data-purpose="chat-messages"
            >
              {messages.map((msg, idx) => (
                <MessageItem
                  key={msg.id}
                  message={msg}
                  onOpenArtifact={(art) => setActiveArtifact(art)}
                  onShowToast={showToast}
                  isLast={idx === messages.length - 1}
                  isGenerating={isGenerating}
                />
              ))}
              <div ref={messagesEndRef} className="h-6 w-full flex-shrink-0" />
            </section>

            {/* Docked Composer at bottom of chat */}
            <div className="p-4 flex flex-col items-center bg-[#F6EFE5]/90 backdrop-blur-md border-t border-[#DFD3C4] flex-shrink-0">
              <Composer
                onSendMessage={handleSendMessage}
                isGenerating={isGenerating}
                onAbort={handleAbort}
                onShowToast={showToast}
                currentModel={currentModel}
                onSelectModel={setCurrentModel}
              />
            </div>
          </div>
        )}
      </main>

      {/* Claude Style Sandboxed Artifact Viewer Drawer */}
      {activeArtifact && (
        <ArtifactViewer
          artifact={activeArtifact}
          onClose={() => setActiveArtifact(null)}
          onShowToast={showToast}
        />
      )}

      {/* Modals */}
      <PricingModal
        isOpen={isPricingOpen}
        onClose={() => setIsPricingOpen(false)}
        activePlanTier={activePlanTier}
        onSelectPlan={(planId) => {
          if (planId === 'free') setActivePlanTier('Free plan');
          else if (planId === 'pro_10') setActivePlanTier('Pro plan ($10)');
          else if (planId === 'team_20') setActivePlanTier('Team plan ($20)');
          else if (planId === 'enterprise_50') setActivePlanTier('Enterprise plan ($50)');
          showToast(`Switched plan to ${planId === 'free' ? 'FREE (Default)' : planId.toUpperCase()}`);
        }}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentModel={currentModel}
        activePlanTier={activePlanTier}
        onOpenPricing={() => setIsPricingOpen(true)}
      />

      <InfoModal isOpen={isInfoOpen} onClose={() => setIsInfoOpen(false)} />
    </div>
  );
};

export default App;
