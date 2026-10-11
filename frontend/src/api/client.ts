import type { Session, Message, Artifact, Citation } from '../types/chat';

export interface StreamCallbacks {
  onToken?: (token: string) => void;
  onThought?: (thoughtToken: string) => void;
  onRoute?: (route: string) => void;
  onCitations?: (citations: Citation[]) => void;
  onArtifact?: (artifact: Artifact) => void;
  onValidation?: (validation: {
    score: number;
    word_count: number;
    is_valid: boolean;
    feedback: string[];
  }) => void;
  onDone?: (data: { latency_ms: number; artifact_id?: string }) => void;
  onError?: (error: { code?: string; message: string; hint?: string }) => void;
}

export const api = {
  async fetchSessions(): Promise<Session[]> {
    const res = await fetch('/sessions');
    if (!res.ok) throw new Error(`Failed to fetch sessions: ${res.statusText}`);
    return res.json();
  },

  async createSession(title: string = 'New Chat', provider?: string, model?: string): Promise<Session> {
    const res = await fetch('/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, provider, model }),
    });
    if (!res.ok) throw new Error(`Failed to create session: ${res.statusText}`);
    return res.json();
  },

  async fetchSessionDetails(id: string): Promise<{ session: Session; messages: Message[] }> {
    const res = await fetch(`/sessions/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch session: ${res.statusText}`);
    const data = await res.json();
    return {
      session: {
        id: data.id,
        title: data.title,
        created_at: data.created_at,
        updated_at: data.updated_at,
      },
      messages: (data.messages || []).map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        citations: m.citations,
        created_at: m.created_at,
      })),
    };
  },

  async deleteSession(id: string): Promise<void> {
    const res = await fetch(`/sessions/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`Failed to delete session: ${res.statusText}`);
  },

  async clearAllHistory(): Promise<void> {
    const res = await fetch('/sessions', { method: 'DELETE' });
    if (!res.ok) throw new Error(`Failed to clear history: ${res.statusText}`);
  },

  async uploadFile(chatId: string, file: File): Promise<{ id: string; file_name: string; file_type: string; file_size: number; s3_url?: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`/chats/${chatId}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`File upload failed: ${res.statusText}`);
    return res.json();
  },

  async fetchArtifact(id: string): Promise<Artifact> {
    const res = await fetch(`/artifacts/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch artifact: ${res.statusText}`);
    return res.json();
  },

  async checkHealth(): Promise<{ status: string; ollama_connected: boolean }> {
    try {
      const res = await fetch('/health');
      if (!res.ok) return { status: 'unhealthy', ollama_connected: false };
      return res.json();
    } catch {
      return { status: 'unreachable', ollama_connected: false };
    }
  },

  streamMessage(
    sessionId: string,
    content: string,
    model: string,
    callbacks: StreamCallbacks
  ): () => void {
    const controller = new AbortController();

    (async () => {
      try {
        const provider = model.includes('claude') ? 'anthropic' : 'ollama';
        const res = await fetch(`/sessions/${sessionId}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({
            content,
            provider,
            model,
          }),
          signal: controller.signal,
        });

        if (!res.ok) {
          const errText = await res.text();
          callbacks.onError?.({
            message: `Request failed (${res.status}): ${errText}`,
          });
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) {
          callbacks.onError?.({ message: 'ReadableStream not supported.' });
          return;
        }

        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const block of lines) {
            const dataLine = block
              .split('\n')
              .find((line) => line.startsWith('data: '));
            if (!dataLine) continue;

            const jsonStr = dataLine.slice(6).trim();
            if (!jsonStr) continue;

            try {
              const event = JSON.parse(jsonStr);
              if (event.type === 'token') {
                callbacks.onToken?.(event.content);
              } else if (event.type === 'thought') {
                callbacks.onThought?.(event.content);
              } else if (event.type === 'route') {
                callbacks.onRoute?.(event.route);
              } else if (event.type === 'citations') {
                callbacks.onCitations?.(event.citations);
              } else if (event.type === 'artifact') {
                callbacks.onArtifact?.(event);
              } else if (event.type === 'validation') {
                callbacks.onValidation?.(event);
              } else if (event.type === 'done') {
                callbacks.onDone?.(event);
              } else if (event.type === 'error') {
                callbacks.onError?.(event.error);
              }
            } catch (err) {
              console.warn('Failed to parse SSE JSON block:', jsonStr, err);
            }
          }
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Stream aborted by user');
          return;
        }
        callbacks.onError?.({ message: err.message || 'Stream connection error' });
      }
    })();

    return () => controller.abort();
  },
};
