"""
Transcript parsing and chunking engine.
Splits by speaker turns and time-windows (roughly 300-600 tokens) with context overlap.
"""
import re
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedChunk:
    chunk_index: int
    text: str
    speaker: str
    start_ref: str  # e.g., "00:04:26"
    char_length: int


@dataclass
class ParsedTranscript:
    title: str
    guest: str
    youtube_url: Optional[str]
    publish_date: Optional[str]
    content_hash: str
    chunks: List[ParsedChunk]


def parse_frontmatter(content: str) -> Dict[str, Any]:
    metadata = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    metadata[key] = val
    return metadata


def parse_speaker_turns(text: str) -> List[Dict[str, str]]:
    """
    Parses sections matching:
    Speaker (HH:MM:SS):
    Spoken text...
    """
    pattern = re.compile(r"([A-Za-z0-9\s\.\-]+)\s*\(([0-9]{2}:[0-9]{2}:[0-9]{2})\):\s*")
    matches = list(pattern.finditer(text))

    turns = []
    if not matches:
        # Fallback: whole text or split by double newline
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for idx, p in enumerate(paragraphs):
            turns.append({
                "speaker": "Speaker",
                "timestamp": "00:00:00",
                "text": p
            })
        return turns

    for i in range(len(matches)):
        speaker = matches[i].group(1).strip()
        timestamp = matches[i].group(2).strip()
        start_pos = matches[i].end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        speech = text[start_pos:end_pos].strip()
        if speech:
            turns.append({
                "speaker": speaker,
                "timestamp": timestamp,
                "text": speech
            })

    return turns


def chunk_transcript(file_path: str, raw_content: str, target_chunk_words: int = 250) -> ParsedTranscript:
    content_hash = hashlib.md5(raw_content.encode("utf-8")).hexdigest()
    metadata = parse_frontmatter(raw_content)

    title = metadata.get("title", "Lenny's Podcast Episode")
    guest = metadata.get("guest", "Unknown Guest")
    youtube_url = metadata.get("youtube_url")
    publish_date = metadata.get("publish_date")

    # Remove frontmatter from body
    body = raw_content
    if raw_content.startswith("---"):
        parts = raw_content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    turns = parse_speaker_turns(body)

    chunks: List[ParsedChunk] = []
    chunk_index = 0

    current_turn_texts = []
    current_word_count = 0
    current_speaker = ""
    current_timestamp = "00:00:00"

    for turn in turns:
        words = turn["text"].split()
        if not current_speaker:
            current_speaker = turn["speaker"]
            current_timestamp = turn["timestamp"]

        turn_formatted = f"{turn['speaker']} ({turn['timestamp']}): {turn['text']}"
        current_turn_texts.append(turn_formatted)
        current_word_count += len(words)

        if current_word_count >= target_chunk_words:
            chunk_text = "\n\n".join(current_turn_texts)
            chunks.append(ParsedChunk(
                chunk_index=chunk_index,
                text=chunk_text,
                speaker=current_speaker,
                start_ref=current_timestamp,
                char_length=len(chunk_text)
            ))
            chunk_index += 1

            # Retain the last turn for 50-token conversational overlap
            if len(current_turn_texts) > 1:
                current_turn_texts = [current_turn_texts[-1]]
                current_word_count = len(current_turn_texts[0].split())
                current_speaker = turn["speaker"]
                current_timestamp = turn["timestamp"]
            else:
                current_turn_texts = []
                current_word_count = 0
                current_speaker = ""

    if current_turn_texts:
        chunk_text = "\n\n".join(current_turn_texts)
        chunks.append(ParsedChunk(
            chunk_index=chunk_index,
            text=chunk_text,
            speaker=current_speaker or "Lenny",
            start_ref=current_timestamp,
            char_length=len(chunk_text)
        ))

    return ParsedTranscript(
        title=title,
        guest=guest,
        youtube_url=youtube_url,
        publish_date=publish_date,
        content_hash=content_hash,
        chunks=chunks
    )
