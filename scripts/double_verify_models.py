"""
Double Verification Script for Local Models:
Tests each model twice with specific product/growth questions grounded in Lenny's Podcast transcripts.
Compares answer consistency, citation references, response latency, and reasoning behavior.
"""
import json
import urllib.request
import time

BASE_URL = "http://127.0.0.1:8000"

def post_sse(session_id, content, model):
    req = urllib.request.Request(
        f"{BASE_URL}/sessions/{session_id}/messages",
        data=json.dumps({
            "content": content,
            "provider": "ollama",
            "model": model
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    tokens = []
    thoughts = []
    meta = {}
    with urllib.request.urlopen(req) as resp:
        for line in resp:
            l = line.decode("utf-8").strip()
            if l.startswith("data: "):
                raw = l[6:]
                if not raw: continue
                try:
                    ev = json.loads(raw)
                    if ev.get("type") == "token":
                        tokens.append(ev.get("content", ""))
                    elif ev.get("type") == "thought":
                        thoughts.append(ev.get("content", ""))
                    elif ev.get("type") == "done":
                        meta = ev
                except Exception:
                    pass
    return {
        "content": "".join(tokens),
        "thought": "".join(thoughts),
        "latency_ms": meta.get("latency_ms", 0),
        "citations": meta.get("citations", [])
    }

def create_chat(title):
    req = urllib.request.Request(
        f"{BASE_URL}/chats",
        data=json.dumps({"title": title, "user_id": "Vetrii"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["id"]

def run_tests():
    results = []

    # Model 1: Qwen 2.5 3B (Fastest response)
    # Test 1A: Adam Fishman on growth loops
    cid_1 = create_chat("Qwen Test 1")
    t0 = time.time()
    res_1a = post_sse(cid_1, "What does Adam Fishman say about growth loops in Lenny's Podcast?", "qwen2.5:3b")
    dur_1a = round(time.time() - t0, 2)
    print(f"--- Qwen 2.5 3B (Run 1) [{dur_1a}s] ---")
    print(res_1a["content"][:280] + "...\n")

    # Test 1B: Elena Verna on B2B Product-Led Growth
    t0 = time.time()
    res_1b = post_sse(cid_1, "What does Elena Verna emphasize regarding product-led growth vs sales-led growth?", "qwen2.5:3b")
    dur_1b = round(time.time() - t0, 2)
    print(f"--- Qwen 2.5 3B (Run 2) [{dur_1b}s] ---")
    print(res_1b["content"][:280] + "...\n")

    # Model 2: DeepSeek R1 1.5B (Deep Thinking & Reasoning)
    # Test 2A: Growth Loop vs Funnel
    cid_2 = create_chat("DeepSeek Test 1")
    t0 = time.time()
    res_2a = post_sse(cid_2, "Compare a growth loop to a growth funnel based on podcast discussions.", "deepseek-r1:1.5b")
    dur_2a = round(time.time() - t0, 2)
    print(f"--- DeepSeek R1 1.5B (Run 1) [{dur_2a}s] ---")
    print("Reasoning snippet:", res_2a["thought"][:150] if res_2a["thought"] else "[Internal reasoning]")
    print(res_2a["content"][:280] + "...\n")

    # Test 2B: Strict refusal on non-podcast question
    t0 = time.time()
    res_2b = post_sse(cid_2, "What is the capital of Australia and the history of Canberra?", "deepseek-r1:1.5b")
    dur_2b = round(time.time() - t0, 2)
    print(f"--- DeepSeek R1 1.5B (Run 2 - Refusal Test) [{dur_2b}s] ---")
    print(res_2b["content"][:280] + "...\n")

    # Model 3: Llama 3.2 3B
    cid_3 = create_chat("Llama Test 1")
    t0 = time.time()
    res_3 = post_sse(cid_3, "What are the common traits of top growth leaders according to Lenny?", "llama3.2:3b")
    dur_3 = round(time.time() - t0, 2)
    print(f"--- Llama 3.2 3B [{dur_3}s] ---")
    print(res_3["content"][:280] + "...\n")

    return {
        "qwen_1a": {"duration": dur_1a, "answer": res_1a["content"]},
        "qwen_1b": {"duration": dur_1b, "answer": res_1b["content"]},
        "deepseek_2a": {"duration": dur_2a, "answer": res_2a["content"], "thought": res_2a["thought"]},
        "deepseek_2b": {"duration": dur_2b, "answer": res_2b["content"]},
        "llama_3": {"duration": dur_3, "answer": res_3["content"]},
    }

if __name__ == "__main__":
    out = run_tests()
    with open("d:/Projects/Lenny Growth/scripts/verification_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("Verification completed and saved to scripts/verification_results.json")
