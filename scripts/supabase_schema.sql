-- ==============================================================================
-- The Lenny Growth Assistant - Complete Supabase Production Database & Storage Schema
-- Run this in your Supabase Project -> SQL Editor
-- Project URL: https://hbuevcxmlmysbhfiknsn.supabase.co
-- ==============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Table: public.chats
-- Stores chat sessions with model identifier and storage archive URL
CREATE TABLE IF NOT EXISTS public.chats (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(255) DEFAULT 'Vetrii',
    title VARCHAR(255) DEFAULT 'New Chat',
    plan_tier VARCHAR(50) DEFAULT 'free', -- 'free', 'pro_10', 'team_20', 'enterprise_50'
    provider VARCHAR(50) DEFAULT 'ollama', -- 'ollama', 'anthropic', 'openai'
    model VARCHAR(100) DEFAULT 'qwen2.5:3b',
    storage_archive_url VARCHAR(500), -- Supabase Storage Public URL for archived JSON thread
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON public.chats(updated_at DESC);

-- 3. Table: public.chat_history
-- Stores message turns with DeepSeek-R1 reasoning thoughts and podcast citations
CREATE TABLE IF NOT EXISTS public.chat_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    chat_id VARCHAR(36) NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    thought TEXT, -- DeepSeek-R1 <think> reasoning process
    citations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_history_chat_id ON public.chat_history(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON public.chat_history(created_at);

-- 4. Table: public.responses_and_times
-- Realtime latency, tokens/sec, and status tracking for observability
CREATE TABLE IF NOT EXISTS public.responses_and_times (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    chat_id VARCHAR(36) NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    message_id VARCHAR(36) REFERENCES public.chat_history(id) ON DELETE SET NULL,
    model_used VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    latency_ms INTEGER NOT NULL,
    tokens_per_second NUMERIC(8, 2),
    time_to_first_token_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success', -- 'success', 'refusal', 'error'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_responses_chat_id ON public.responses_and_times(chat_id);
CREATE INDEX IF NOT EXISTS idx_responses_model ON public.responses_and_times(model_used);

-- 5. Table: public.file_uploads_and_generations
-- User-uploaded files (PDFs, docs) and generated HTML artifacts in Supabase Storage
CREATE TABLE IF NOT EXISTS public.file_uploads_and_generations (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    chat_id VARCHAR(36) NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT DEFAULT 0,
    storage_path VARCHAR(500), -- Supabase Storage object path (e.g. uploads/1741..._doc.pdf)
    storage_url VARCHAR(1000), -- Supabase Storage public CDN URL
    extracted_text TEXT,
    generation_type VARCHAR(50), -- 'artifact_html', 'ship30_essay', 'analysis'
    generated_content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_chat_id ON public.file_uploads_and_generations(chat_id);

-- 6. Table: public.each_models_history_and_tokens_usage
-- Token usage analytics and cost accounting per LLM model
CREATE TABLE IF NOT EXISTS public.each_models_history_and_tokens_usage (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    chat_id VARCHAR(36) NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    plan_type VARCHAR(50) DEFAULT 'free',
    cost_estimate_usd NUMERIC(10, 6) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_usage_chat_id ON public.each_models_history_and_tokens_usage(chat_id);
CREATE INDEX IF NOT EXISTS idx_model_usage_model_name ON public.each_models_history_and_tokens_usage(model_name);

-- 7. Knowledge Base Tables: Lenny's Podcast Transcripts
CREATE TABLE IF NOT EXISTS public.documents (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    title VARCHAR(500) NOT NULL,
    guest VARCHAR(255) NOT NULL,
    source_path VARCHAR(500) NOT NULL,
    source_url VARCHAR(500),
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.chunks (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    document_id VARCHAR(36) NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    speaker VARCHAR(255),
    start_ref VARCHAR(50),
    embedding vector(768) -- nomic-embed-text generates 768-dimensional embeddings
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON public.chunks(document_id);

-- 8. Supabase Storage Bucket Initialization
-- Creates the public bucket 'lenny-growth-chats' for chat archives and file uploads
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'lenny-growth-chats',
    'lenny-growth-chats',
    true,
    52428800, -- 50 MB
    ARRAY['application/json', 'application/pdf', 'text/plain', 'text/html', 'image/png', 'image/jpeg']
)
ON CONFLICT (id) DO UPDATE SET public = true;

-- 9. Storage Object Access Policies (Public Read & Authenticated/Anon Insert)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'Public Access for lenny-growth-chats'
    ) THEN
        CREATE POLICY "Public Access for lenny-growth-chats"
        ON storage.objects FOR SELECT
        USING (bucket_id = 'lenny-growth-chats');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE policyname = 'Allow Uploads to lenny-growth-chats'
    ) THEN
        CREATE POLICY "Allow Uploads to lenny-growth-chats"
        ON storage.objects FOR INSERT
        WITH CHECK (bucket_id = 'lenny-growth-chats');
    END IF;
END $$;

-- 10. Table Security & Grants (Direct Access for App & Anon Keys)
ALTER TABLE public.chats DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses_and_times DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads_and_generations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.each_models_history_and_tokens_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.chunks DISABLE ROW LEVEL SECURITY;

GRANT ALL ON TABLE public.chats TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.chat_history TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.responses_and_times TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.file_uploads_and_generations TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.each_models_history_and_tokens_usage TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.documents TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.chunks TO anon, authenticated, service_role;
