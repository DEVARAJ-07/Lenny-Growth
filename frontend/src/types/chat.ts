export interface Citation {
  chunk_id: string;
  episode_id: string;
  episode_title: string;
  guest: string;
  timestamp: string;
  text: string;
  score?: number;
}

export interface Artifact {
  id: string;
  type: string;
  title: string;
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  thought?: string;
  citations?: Citation[];
  artifact_id?: string;
  artifact?: Artifact;
  model_used?: string;
  created_at: string;
  // UI helpers
  rawCodeTabs?: {
    html?: string;
    css?: string;
    js?: string;
  };
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export type ModelOption =
  | 'qwen2.5:3b'
  | 'deepseek-r1:1.5b'
  | 'llama3.2:3b'
  | 'claude-3-7-sonnet';

export interface ModelInfo {
  id: ModelOption;
  name: string;
  badge: string;
  description: string;
  speed: string;
  isLocal: boolean;
}
