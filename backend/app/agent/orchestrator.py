"""
Agent Orchestrator managing query routing, retrieval, generation, and persistence.
"""
import time
import json
import re
from typing import AsyncGenerator, Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    Message,
    Artifact,
    Session as DbSession,
    ResponseTime,
    FileUploadGeneration,
    ModelHistoryTokenUsage,
)
from app.storage.supabase_storage import supabase_storage_service
from app.db.supabase_client import supabase_service
from app.config import settings
from app.retrieval.search import hybrid_search, SearchResult
from app.agent.router import agent_router, RouteType
from app.agent.skills.ship30.validator import ship30_validator
from app.llm.factory import LLMFactory
from app.logging import logger


class AgentOrchestrator:
    async def process_message_stream(
        self,
        session_id: str,
        user_query: str,
        db_session: AsyncSession,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        start_time = time.time()
        route = agent_router.classify(user_query)
        provider = LLMFactory.get_provider(
            override_provider=provider_override,
            override_model=model_override
        )

        # 1. Handle Greetings / Introductions directly
        if route == "greeting":
            greeting_text = (
                "Hey! I'm **The Lenny Growth Assistant**, grounded in 303+ transcripts from Lenny's Podcast.\n\n"
                "I synthesize battle-tested wisdom from world-class product and growth operators. Here are a few areas you can explore:\n\n"
                "• **PLG & Growth Loops**: How Elena Verna or Brian Balfour design B2B self-serve engines\n"
                "• **Activation & Onboarding**: Adam Fishman's and Darius Contractor's onboarding benchmarks\n"
                "• **Product Strategy**: Shreyas Doshi's Good Product Manager frameworks and LNO prioritization\n"
                "• **Ship 30 for 30**: Write an atomic essay grounded in operator insights\n"
                "• **Interactive Artifacts**: Build a growth calculator, metric dashboard, or UI widget\n\n"
                "What product or growth challenge are you tackling today?"
            )
            yield {"type": "route", "route": "greeting"}
            words = greeting_text.split(" ")
            for i, word in enumerate(words):
                yield {"type": "token", "content": word + (" " if i < len(words) - 1 else "")}
                await asyncio.sleep(0.015)
            yield {"type": "citations", "citations": []}
            latency_ms = int((time.time() - start_time) * 1000)
            yield {"type": "done", "latency_ms": latency_ms}

            msg = Message(
                chat_id=session_id,
                role="assistant",
                content=greeting_text,
                citations=[]
            )
            db_session.add(msg)
            await db_session.flush()

            resp_metric = ResponseTime(
                chat_id=session_id,
                message_id=msg.id,
                model_used=model_override or settings.llm_model,
                provider=provider_override or settings.llm_provider,
                latency_ms=latency_ms,
                tokens_per_second=len(words) / max(0.1, latency_ms / 1000.0),
                status="success"
            )
            db_session.add(resp_metric)
            await db_session.commit()

            # Sync to Supabase
            await supabase_service.sync_message(
                message_id=msg.id,
                chat_id=session_id,
                role="assistant",
                content=greeting_text,
                citations=[]
            )
            await supabase_service.sync_response_metric(
                chat_id=session_id,
                message_id=msg.id,
                model_used=model_override or settings.llm_model,
                latency_ms=latency_ms,
                status="success",
                provider=provider_override or settings.llm_provider
            )
            return

        # 2. Contextualization & Hybrid Search (Preserving multi-turn context)
        stmt = (
            select(Message)
            .where(Message.chat_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(6)
        )
        res = await db_session.execute(stmt)
        past_msgs = list(reversed(res.scalars().all()))
        previous_turns = [m for m in past_msgs if m.content != user_query]

        search_query = user_query
        if previous_turns and len(user_query.split()) < 7:
            last_user_turn = next((m.content for m in reversed(previous_turns) if m.role == "user"), "")
            if any(p in user_query.lower().split() for p in ("he", "she", "it", "they", "that", "this", "their", "more", "size", "why", "how", "what", "team")):
                search_query = f"{last_user_turn} {user_query}"

        results, is_covered = await hybrid_search.search(search_query, db_session, top_k=4)
        citations = [r.to_citation_dict() for r in results]

        # 3. Refusal handling if not covered
        if not is_covered:
            refusal_text = (
                "I searched through Lenny's 300+ podcast transcripts, but this topic is not covered in the episodes. "
                "I am strictly grounded in the podcast conversations and do not speculate without direct transcript evidence."
            )
            yield {"type": "route", "route": "refusal"}
            yield {"type": "token", "content": refusal_text}
            yield {"type": "citations", "citations": []}
            yield {"type": "done", "latency_ms": int((time.time() - start_time) * 1000)}

            # Persist assistant refusal
            msg = Message(
                chat_id=session_id,
                role="assistant",
                content=refusal_text,
                citations=[]
            )
            db_session.add(msg)
            await db_session.flush()

            # Record refusal in responses_and_times
            resp_metric = ResponseTime(
                chat_id=session_id,
                message_id=msg.id,
                model_used=model_override or settings.llm_model,
                provider=provider_override or settings.llm_provider,
                latency_ms=int((time.time() - start_time) * 1000),
                tokens_per_second=0.0,
                status="refusal"
            )
            db_session.add(resp_metric)
            await db_session.commit()

            # Sync to Supabase
            await supabase_service.sync_message(
                message_id=msg.id,
                chat_id=session_id,
                role="assistant",
                content=refusal_text,
                citations=[]
            )
            await supabase_service.sync_response_metric(
                chat_id=session_id,
                message_id=msg.id,
                model_used=model_override or settings.llm_model,
                latency_ms=int((time.time() - start_time) * 1000),
                status="refusal",
                provider=provider_override or settings.llm_provider
            )
            return

        yield {"type": "route", "route": route}
        yield {"type": "citations", "citations": citations}

        # 3. Assemble Grounded Context (Trimmed for fast GPU prefill)
        context_chunks = []
        for idx, r in enumerate(results, 1):
            snippet = r.text[:850].strip()
            context_chunks.append(
                f"[Source {idx}]: Episode: '{r.title}' | Guest: {r.guest} | Time: ({r.start_ref})\n"
                f"{snippet}\n"
            )
        context_str = "\n---\n".join(context_chunks)

        # 4. Route-specific system prompt and token budget
        if route == "ship30":
            max_tokens_for_route = 1800
            system_prompt = (
                "You are an expert growth essayist writing in the Ship 30 for 30 style. "
                "Write an in-depth atomic essay of approximately 1,200 to 1,300 words grounded strictly in the provided Lenny's Podcast transcripts.\n"
                "Follow these structural principles:\n"
                "1. Irresistible Hook (Headline + punchy 1-2 sentence lead framing the core operator problem).\n"
                "2. High Skimmability: Use 4-5 descriptive H2 subheadings, short 2-sentence paragraphs, bullet points, and **selective bolding** on key insights.\n"
                "3. Grounded Operator Citations: Explicitly cite guests and timestamps (e.g. 'As Adam Fishman noted (00:04:26)...').\n"
                "4. Clear Narrative Arc: Mistake -> Mindset Shift -> Tactical Framework -> Action Steps.\n"
                "5. Actionable Monday-morning takeaway checklist at the end."
            )
        elif route == "artifact":
            max_tokens_for_route = 1400
            system_prompt = (
                "You are a principal frontend engineer and growth architect. "
                "The user requested an interactive artifact, dashboard, or code component grounded in Lenny's Podcast transcripts.\n"
                "Generate complete, self-contained HTML/CSS inside a ```html ... ``` code block.\n"
                "Requirements:\n"
                "- Beautiful modern dark design matching background #0F1117, cards #1A1D24, accent #FF6B35.\n"
                "- Inline CSS only. No external CDN fonts or scripts.\n"
                "- Include practical product management / growth calculations, interactive toggles, or metrics comparison based on the transcripts."
            )
        else:
            max_tokens_for_route = 650
            system_prompt = (
                "You are The Lenny Growth Assistant, a precise, high-signal advisory intelligence for product and growth leaders.\n"
                "Strict Guidelines:\n"
                "1. Answer strictly using the provided podcast transcript excerpts. Never speculate or hallucinate outside the given text.\n"
                "2. Be concise, punchy, and direct. Deliver a high-impact answer in 2 to 3 structured paragraphs or bullet points.\n"
                "3. Answer the core question immediately in the first sentence.\n"
                "4. Cite the relevant guest name and timestamp marker (e.g. 'Elena Verna (00:00:26)...').\n"
                "5. Use clean bullets and bold highlights for rapid skimmability."
            )

        user_content = f"TRANSCRIPT EXCERPTS:\n{context_str}\n\nUSER QUESTION:\n{user_query}"
        messages = [{"role": "system", "content": system_prompt}]
        for prev in previous_turns[-4:]:
            if prev.role in ("user", "assistant"):
                prev_text = prev.content
                if "<think>" in prev_text and "</think>" in prev_text:
                    prev_text = prev_text.split("</think>")[-1].strip()
                messages.append({"role": prev.role, "content": prev_text[:500]})
        messages.append({"role": "user", "content": user_content})

        # 5. Stream Generation
        accumulated_text = []
        async for token in provider.generate_stream(messages, model=model_override, max_tokens=max_tokens_for_route):
            accumulated_text.append(token)
            yield {"type": "token", "content": token}

        full_response = "".join(accumulated_text)
        latency_ms = int((time.time() - start_time) * 1000)

        # 6. Artifact Detection & Extraction
        artifact_id = None
        if "```html" in full_response:
            match = re.search(r"```html\s*(.*?)\s*```", full_response, re.DOTALL)
            if match:
                html_code = match.group(1).strip()
                art = Artifact(
                    session_id=session_id,
                    type="html",
                    title="Growth Component / Dashboard",
                    content=html_code
                )
                db_session.add(art)
                await db_session.flush()
                artifact_id = art.id
                yield {
                    "type": "artifact",
                    "id": art.id,
                    "artifact_type": "html",
                    "title": art.title,
                    "content": html_code
                }
        elif route == "ship30":
            art = Artifact(
                session_id=session_id,
                type="markdown",
                title="Ship 30 for 30 Atomic Essay",
                content=full_response
            )
            db_session.add(art)
            await db_session.flush()
            artifact_id = art.id
            yield {
                "type": "artifact",
                "id": art.id,
                "artifact_type": "markdown",
                "title": art.title,
                "content": full_response
            }

        # 7. Ship 30 Validation
        if route == "ship30":
            val_report = ship30_validator.validate(full_response)
            yield {
                "type": "validation",
                "score": val_report.score,
                "word_count": val_report.word_count,
                "is_valid": val_report.is_valid,
                "feedback": val_report.feedback
            }

        # 8. Persist assistant message in chat_history
        assistant_msg = Message(
            chat_id=session_id,
            role="assistant",
            content=full_response,
            citations=citations
        )
        db_session.add(assistant_msg)
        await db_session.flush()

        # 9. Record response time metric in responses_and_times
        tokens_count = len(accumulated_text)
        tps = round(tokens_count / (latency_ms / 1000.0), 2) if latency_ms > 0 else 0.0
        active_model_name = model_override or settings.llm_model
        active_provider_name = provider_override or settings.llm_provider

        resp_metric = ResponseTime(
            chat_id=session_id,
            message_id=assistant_msg.id,
            model_used=active_model_name,
            provider=active_provider_name,
            latency_ms=latency_ms,
            tokens_per_second=tps,
            status="success"
        )
        db_session.add(resp_metric)

        # 10. Record token usage in each_models_history_and_tokens_usage
        prompt_tokens = max(1, len(user_query.split()) * 2)
        completion_tokens = max(1, len(full_response.split()) * 2)
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = 0.0 if "ollama" in active_provider_name.lower() else round(0.003 * total_tokens / 1000.0, 6)

        token_record = ModelHistoryTokenUsage(
            chat_id=session_id,
            model_name=active_model_name,
            provider=active_provider_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_estimate_usd=cost_usd
        )
        db_session.add(token_record)

        # 11. Record artifact in file_uploads_and_generations if generated
        if artifact_id and "```html" in full_response:
            file_gen = FileUploadGeneration(
                chat_id=session_id,
                file_name="growth_dashboard.html",
                file_type="html",
                generation_type="artifact_html",
                generated_content=html_code
            )
            db_session.add(file_gen)

        await db_session.commit()

        # Real-time sync to Supabase database tables
        extracted_thought = None
        if "<think>" in full_response:
            parts = full_response.split("</think>")
            if len(parts) > 1:
                extracted_thought = parts[0].replace("<think>", "").strip()
            else:
                extracted_thought = full_response.replace("<think>", "").strip()

        # Yield done immediately so client UI finishes rendering with zero delay
        yield {"type": "done", "latency_ms": latency_ms, "artifact_id": artifact_id}

        # Background sync to Supabase (non-blocking)
        async def _background_supabase_sync():
            try:
                await supabase_service.sync_message(
                    message_id=assistant_msg.id,
                    chat_id=session_id,
                    role="assistant",
                    content=full_response,
                    thought=extracted_thought,
                    citations=citations,
                    created_at=assistant_msg.created_at
                )
                await supabase_service.sync_response_metric(
                    chat_id=session_id,
                    message_id=assistant_msg.id,
                    model_used=active_model_name,
                    provider=active_provider_name,
                    latency_ms=latency_ms,
                    tokens_per_second=tps,
                    status="success",
                    created_at=resp_metric.created_at
                )
                await supabase_service.sync_token_usage(
                    chat_id=session_id,
                    model_name=active_model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    plan_type="free",
                    cost_usd=cost_usd,
                    provider=active_provider_name,
                    created_at=token_record.created_at
                )
                storage_url = await supabase_storage_service.archive_chat(
                    chat_id=session_id,
                    chat_title=user_query[:40],
                    history=[
                        {"role": "user", "content": user_query},
                        {"role": "assistant", "content": full_response}
                    ]
                )
                if storage_url:
                    logger.info("chat_archived_to_supabase_storage", storage_url=storage_url, chat_id=session_id)
            except Exception as sync_err:
                logger.warning("background_supabase_sync_error", error=str(sync_err))

        import asyncio
        asyncio.create_task(_background_supabase_sync())


agent_orchestrator = AgentOrchestrator()
