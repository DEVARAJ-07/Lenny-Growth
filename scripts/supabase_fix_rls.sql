-- ==============================================================================
-- Run this in Supabase -> SQL Editor (Click 'Run' / Cmd+Enter)
-- Project: https://hbuevcxmlmysbhfiknsn.supabase.co
-- This unlocks insert and read access so chats & responses save directly to Supabase
-- ==============================================================================

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
