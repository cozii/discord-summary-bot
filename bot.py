import discord
import os
import re
from datetime import datetime, timezone, timedelta
from collections import Counter

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ── Summarizer ────────────────────────────────────────────────────────────────

STOP_WORDS = {
    "i","me","my","we","our","you","your","he","she","it","they","them",
    "his","her","its","this","that","these","those","is","are","was","were",
    "be","been","being","have","has","had","do","does","did","will","would",
    "could","should","may","might","can","a","an","the","and","but","or",
    "so","at","by","in","of","on","to","up","as","if","no","not","with",
    "from","than","then","when","where","who","how","what","just","also",
    "like","about","get","got","ok","okay","yeah","yes","lol","haha","oh",
    "well","hey","hi","hello","thanks","thank","please","sorry","np","idk",
    "lmk","btw","fyi","tbh","imo",
}

def clean(text):
    text = re.sub(r"<@!?\d+>|<#\d+>|<:\w+:\d+>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()

def summarize(messages):
    # Build cleaned corpus
    entries = []
    for m in messages:
        c = clean(m.content)
        if len(c) > 10:
            entries.append((m.author.display_name, c))

    if not entries:
        return None

    # Word frequency across all messages
    all_words = []
    for _, text in entries:
        for w in re.findall(r"\b[a-z]{3,}\b", text.lower()):
            if w not in STOP_WORDS:
                all_words.append(w)
    freq = Counter(all_words)

    # Score each message by the avg frequency of its meaningful words
    scored = []
    for name, text in entries:
        words = [w for w in re.findall(r"\b[a-z]{3,}\b", text.lower()) if w not in STOP_WORDS]
        if not words:
            continue
        score = sum(freq[w] for w in words) / len(words)
        scored.append((score, name, text))

    scored.sort(reverse=True)

    # Pick top messages (roughly 1 per 10, min 3 max 8)
    n = max(3, min(8, len(entries) // 10))
    top = scored[:n]

    # Restore chronological order
    order = {text: i for i, (_, text) in enumerate(entries)}
    top.sort(key=lambda x: order.get(x[2], 0))

    # Participants
    speakers = Counter(name for _, name, _ in [(s,n,t) for s,n,t in scored])
    top_speakers = ", ".join(f"**{n}**" for n, _ in speakers.most_common(5))

    # Key words
    keywords = ", ".join(w for w, _ in freq.most_common(20) if len(w) > 3)[:80]

    # Summary lines
    lines = [f"• {name}: {text}" for _, name, text in top]

    return top_speakers, keywords, "\n".join(lines), len(entries)


# ── Bot events ────────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions and "summarize" in message.content.lower():
        await do_summary(message)

async def do_summary(trigger):
    channel = trigger.channel
    working = await channel.send("⏳ Summarizing the last 5 hours...")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=5)

    messages = []
    async for msg in channel.history(limit=1000, after=cutoff):
        if not msg.author.bot and msg.id != trigger.id:
            messages.append(msg)

    if not messages:
        await working.edit(content="No messages found in the last 5 hours.")
        return

    result = summarize(messages)
    if not result:
        await working.edit(content="Not enough text content to summarize.")
        return

    speakers, keywords, highlights, total = result

    embed = discord.Embed(
        title="📋 Last 5 Hours — Summary",
        color=0x5865F2
    )
    embed.add_field(name="👥 Active members", value=speakers, inline=False)
    embed.add_field(name="🔑 Topics discussed", value=keywords or "—", inline=False)
    embed.add_field(name="💬 Key messages", value=highlights, inline=False)
    embed.set_footer(text=f"{total} messages read • {datetime.now().strftime('%b %d, %H:%M')}")

    await working.delete()
    await channel.send(embed=embed)


client.run(TOKEN)
