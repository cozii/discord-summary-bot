"""
summarizer.py — Extractive text summarizer (no AI/LLM API required)

How it works:
1. Groups messages by author clusters to find "conversation threads"
2. Scores every sentence by:
   - Word frequency (common important words score higher)
   - Position (earlier messages get slight weight as topic-setters)
   - Length (very short or very long sentences score lower)
3. Picks the top-scoring sentences as the summary
4. Identifies the most active participants
5. Detects any links or attachments shared
"""

import re
from collections import Counter, defaultdict


# Words that carry no meaning and should be ignored when scoring
STOP_WORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they",
    "them", "his", "her", "its", "this", "that", "these", "those", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "shall", "can",
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so", "at",
    "by", "in", "of", "on", "to", "up", "as", "if", "no", "not", "with",
    "from", "into", "than", "then", "when", "where", "who", "how", "what",
    "just", "also", "like", "about", "go", "get", "got", "ok", "okay", "yeah",
    "yes", "yep", "nope", "lol", "haha", "hm", "hmm", "oh", "ah", "uh",
    "um", "well", "hey", "hi", "hello", "thanks", "thank", "please", "sorry",
    "np", "nvm", "tbh", "imo", "idk", "lmk", "btw", "fyi", "afk", "brb",
}


def clean_text(text: str) -> str:
    """Remove mentions, URLs, emoji shortcodes, and extra whitespace."""
    text = re.sub(r"<@!?\d+>", "", text)          # Discord mentions
    text = re.sub(r"<#\d+>", "", text)             # Channel mentions
    text = re.sub(r"<:\w+:\d+>", "", text)         # Custom emoji
    text = re.sub(r"https?://\S+", "[link]", text) # URLs → placeholder
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences (rough but effective for chat)."""
    # Split on sentence-ending punctuation or newlines
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 15]


def word_frequency(all_sentences: list[str]) -> Counter:
    """Count meaningful word frequencies across all sentences."""
    words = []
    for sentence in all_sentences:
        for word in re.findall(r"\b[a-zA-Z']+\b", sentence.lower()):
            if word not in STOP_WORDS and len(word) > 2:
                words.append(word)
    return Counter(words)


def score_sentence(sentence: str, freq: Counter, position: int, total: int) -> float:
    """Score a sentence based on word importance, position, and length."""
    words = re.findall(r"\b[a-zA-Z']+\b", sentence.lower())
    meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    if not meaningful:
        return 0.0

    # Average frequency score of the meaningful words
    freq_score = sum(freq[w] for w in meaningful) / len(meaningful)

    # Position bonus: first 20% of messages are often topic-setting
    position_score = 1.2 if position / max(total, 1) < 0.2 else 1.0

    # Length penalty: very short (<4 words) or very long (>40 words) sentences score lower
    length_penalty = 1.0
    word_count = len(words)
    if word_count < 4:
        length_penalty = 0.5
    elif word_count > 40:
        length_penalty = 0.8

    return freq_score * position_score * length_penalty


def extract_links(messages) -> list[str]:
    """Pull any URLs shared in the conversation."""
    links = []
    url_pattern = re.compile(r"https?://\S+")
    for msg in messages:
        found = url_pattern.findall(msg.content)
        links.extend(found)
    return links[:5]  # Cap at 5 links


def participant_summary(messages) -> str:
    """Return a short string listing the most active speakers."""
    counts = Counter(msg.author.display_name for msg in messages)
    top = counts.most_common(5)
    parts = [f"**{name}** ({count})" for name, count in top]
    return ", ".join(parts)


def summarize_messages(messages) -> str:
    """
    Main entry point. Takes a list of discord.Message objects,
    returns a formatted summary string.
    """
    if not messages:
        return "No messages to summarize."

    # ── 1. Collect all cleaned text and sentences ──────────────────────────
    cleaned_texts = []
    for msg in messages:
        cleaned = clean_text(msg.content)
        if cleaned and cleaned != "[link]":
            cleaned_texts.append(cleaned)

    if not cleaned_texts:
        return "The messages didn't contain enough text to summarize (maybe it was all links or images)."

    all_sentences = []
    sentence_to_source = {}  # sentence → original cleaned text index

    for idx, text in enumerate(cleaned_texts):
        sentences = extract_sentences(text)
        for s in sentences:
            all_sentences.append(s)
            sentence_to_source[s] = idx

    if not all_sentences:
        # Fallback: treat each message as its own sentence
        all_sentences = cleaned_texts

    # ── 2. Score sentences ─────────────────────────────────────────────────
    freq = word_frequency(all_sentences)
    total = len(all_sentences)

    scored = []
    seen = set()
    for i, sentence in enumerate(all_sentences):
        # Deduplicate near-identical sentences
        key = sentence.lower()[:60]
        if key in seen:
            continue
        seen.add(key)
        score = score_sentence(sentence, freq, i, total)
        scored.append((score, sentence))

    scored.sort(reverse=True, key=lambda x: x[0])

    # ── 3. Pick top sentences (up to 6, or fewer for short convos) ─────────
    num_sentences = min(6, max(2, len(all_sentences) // 8))
    top_sentences = [s for _, s in scored[:num_sentences]]

    # Restore chronological order
    order = {s: i for i, s in enumerate(all_sentences)}
    top_sentences.sort(key=lambda s: order.get(s, 0))

    summary_body = " ".join(top_sentences)

    # ── 4. Build the final output ──────────────────────────────────────────
    output_parts = []

    # Participants
    output_parts.append(f"👥 **Participants:** {participant_summary(messages)}\n")

    # Message count & timespan
    first = messages[0].created_at.strftime("%b %d, %H:%M")
    last = messages[-1].created_at.strftime("%b %d, %H:%M")
    output_parts.append(f"🕐 **Timespan:** {first} → {last}\n")

    # Key topics (top 5 non-stop words overall)
    top_words = [word for word, _ in freq.most_common(10)
                 if len(word) > 3][:5]
    if top_words:
        output_parts.append(f"🔑 **Key topics:** {', '.join(top_words)}\n")

    # Summary text
    output_parts.append(f"\n📝 **Summary:**\n{summary_body}")

    # Links
    links = extract_links(messages)
    if links:
        link_lines = "\n".join(f"• {l}" for l in links)
        output_parts.append(f"\n\n🔗 **Links shared:**\n{link_lines}")

    return "\n".join(output_parts)
