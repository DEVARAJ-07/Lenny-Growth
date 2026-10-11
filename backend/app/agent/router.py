"""
Deterministic Agent Router for user intent classification.
Routes to:
1. "greeting": Conversational greetings and assistant capabilities introduction
2. "question": Standard grounded RAG Q&A with episode citations
3. "ship30": Ship 30 for 30 structured essay generation with length validation
4. "artifact": Interactive Markdown/HTML document generation
"""
import re
from typing import Literal

RouteType = Literal["greeting", "question", "ship30", "artifact"]


class AgentRouter:
    def classify(self, user_prompt: str) -> RouteType:
        prompt_lower = user_prompt.lower().strip()

        # Greeting patterns (e.g. "hiii man", "hello", "hey", "who are you")
        greeting_patterns = [
            r"^h(i+|ey|ello|owdy|ola)(\s+(there|man|bro|friend|buddy|all|team))?[\s!.,?]*$",
            r"^good\s+(morning|afternoon|evening|day)[\s!.,?]*$",
            r"^(who\s+are\s+you|what\s+can\s+you\s+do|help\s*me|what\s+is\s+this)[\s!.,?]*$"
        ]
        for pat in greeting_patterns:
            if re.search(pat, prompt_lower):
                return "greeting"

        # Ship 30 keywords
        ship30_patterns = [
            r"ship\s*30",
            r"essay",
            r"blog\s*post",
            r"article",
            r"write\s+a\s+post",
            r"thought\s*leadership",
            r"atomic\s*essay"
        ]
        for pat in ship30_patterns:
            if re.search(pat, prompt_lower):
                return "ship30"

        # Artifact keywords
        artifact_patterns = [
            r"html",
            r"css",
            r"dashboard",
            r"ui\s*mockup",
            r"calculator",
            r"generate\s*code",
            r"component",
            r"widget",
            r"interactive\s*page",
            r"visualize",
            r"chart",
            r"diagram"
        ]
        for pat in artifact_patterns:
            if re.search(pat, prompt_lower):
                return "artifact"

        # Default is grounded question path
        return "question"


agent_router = AgentRouter()
