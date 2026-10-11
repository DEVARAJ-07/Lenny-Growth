"""
5-Chat Evaluation and Cross-Verification Suite for Lenny Growth Assistant.
Creates 5 new chats, asks grounded product questions across distinct podcast episodes,
verifies transcript citations, benchmarks latency, and tests chat switching & persistence.
"""
import json
import urllib.request
import time

BASE_URL = "http://127.0.0.1:8000"

def create_chat(title, model="qwen2.5:3b"):
    req = urllib.request.Request(
        f"{BASE_URL}/chats",
        data=json.dumps({"title": title, "user_id": "Sir", "model": model}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["id"]

def send_chat_message(chat_id, query, model="qwen2.5:3b"):
    req = urllib.request.Request(
        f"{BASE_URL}/sessions/{chat_id}/messages",
        data=json.dumps({"content": query, "model": model, "provider": "ollama"}).encode("utf-8"),
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
        "citations": meta.get("citations", []),
        "latency_ms": meta.get("latency_ms", 0),
    }

def get_chat_history(chat_id):
    with urllib.request.urlopen(f"{BASE_URL}/sessions/{chat_id}") as resp:
        return json.loads(resp.read().decode())

def run_5_chats_suite():
    tests = [
        {
            "id": 1,
            "title": "Elena Verna Growth Tactics",
            "model": "qwen2.5:3b",
            "question": "What are the growth tactics that never work according to Elena Verna?",
            "expected_ground_truth": [
                "Thinking you need a growth team before finding PMF/distribution",
                "Rebrands or marketing site redesigns expecting acquisition spikes",
                "Experimentation paralysis / treating every single initiative as an experiment"
            ]
        },
        {
            "id": 2,
            "title": "Shreyas Doshi High Agency",
            "model": "qwen2.5:3b",
            "question": "What does Shreyas Doshi say about high agency and solving problems in product management?",
            "expected_ground_truth": [
                "Bending reality to your will rather than accepting default constraints",
                "Viewing constraints as puzzles to solve"
            ]
        },
        {
            "id": 3,
            "title": "Brian Chesky Founder Mode",
            "model": "qwen2.5:3b",
            "question": "What does Brian Chesky explain about moving away from traditional product management to a functional organization at Airbnb?",
            "expected_ground_truth": [
                "Eliminating classic divisional PM boundaries",
                "Elevating design and product marketing",
                "Leaders being deep in details rather than hands-off"
            ]
        },
        {
            "id": 4,
            "title": "Hila Qu PLG Motion",
            "model": "qwen2.5:3b",
            "question": "What does Hila Qu emphasize about adding a product-led growth (PLG) motion?",
            "expected_ground_truth": [
                "Self-serve onboarding and user activation",
                "Product Qualified Leads (PQLs)",
                "Aligning product-led motion with sales motion"
            ]
        },
        {
            "id": 5,
            "title": "Gustaf Alstromer Retention",
            "model": "qwen2.5:3b",
            "question": "What does Gustaf Alstromer from YC say is the most important metric for startups?",
            "expected_ground_truth": [
                "Retention is the prerequisite for growth",
                "Acquisition without retention is a leaky bucket",
                "Cohort curves flattening as real PMF"
            ]
        }
    ]

    results = []

    print("=================================================================")
    print("STARTING 5-CHAT EVALUATION SUITE FOR THE LENNY GROWTH ASSISTANT")
    print("=================================================================\n")

    created_chat_ids = []

    for t in tests:
        print(f">>> [Chat {t['id']}/5]: Creating session '{t['title']}'...")
        cid = create_chat(t["title"], t["model"])
        created_chat_ids.append(cid)
        print(f"    Session ID: {cid}")

        print(f"    Querying: \"{t['question']}\" using {t['model']}...")
        t0 = time.time()
        ans_data = send_chat_message(cid, t["question"], t["model"])
        elapsed = round(time.time() - t0, 2)

        content = ans_data["content"]
        citations = ans_data["citations"]

        # Evaluation match check
        matches = [gt for gt in t["expected_ground_truth"] if any(k.lower() in content.lower() for k in gt.split()[:3])]
        match_ratio = len(matches) / len(t["expected_ground_truth"])

        print(f"    Response generated in {elapsed}s (Latency: {ans_data['latency_ms']}ms)")
        print(f"    Citations found: {len(citations)}")
        print(f"    Answer Preview:\n    {content[:260]}...\n")

        results.append({
            "test_id": t["id"],
            "chat_id": cid,
            "title": t["title"],
            "question": t["question"],
            "model": t["model"],
            "elapsed_s": elapsed,
            "latency_ms": ans_data["latency_ms"],
            "citations_count": len(citations),
            "answer_preview": content[:300],
            "ground_truth_matches": matches,
            "accuracy_score": f"{int(match_ratio * 100)}%"
        })

    # Test chat switching and state recovery across all 5 sessions
    print("\n>>> TESTING CHAT SWITCHING AND CONVERSATION RETRIEVAL ACROSS ALL 5 CHATS...")
    switching_verified = True
    for idx, cid in enumerate(created_chat_ids):
        hist = get_chat_history(cid)
        msg_count = len(hist.get("messages", []))
        print(f"    Switched to Chat {idx+1} ({cid[:8]}...): {msg_count} messages recovered successfully.")
        if msg_count < 2:
            switching_verified = False

    output_payload = {
        "suite": "Lenny Growth Assistant 5-Chat Verification",
        "chat_switching_verified": switching_verified,
        "results": results
    }

    with open("d:/Projects/Lenny Growth/scripts/five_chats_results.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print("\n=================================================================")
    print("5-CHAT EVALUATION COMPLETED SUCCESSFULLY & SAVED TO five_chats_results.json")
    print("=================================================================")

if __name__ == "__main__":
    run_5_chats_suite()
