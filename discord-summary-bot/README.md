# Discord Summary Bot

A Discord bot that reads recent channel messages and posts a summary when you mention it.  
**No AI/LLM API required** — summarization runs entirely on your machine using text analysis.

---

## What it does

Mention the bot with the word "summarize" in any channel:

```
@SummaryBot summarize
```

It will read the last 100 messages (excluding bot messages), then post an embed with:

- 👥 Who participated and how many messages each sent
- 🕐 The timespan of the conversation
- 🔑 The most frequently discussed topics (key words)
- 📝 A summary of the most important sentences
- 🔗 Any links that were shared

---

## Setup Guide

### Step 1 — Install Python

Make sure you have **Python 3.11 or newer** installed.

- Download from: https://www.python.org/downloads/
- During install on Windows, check ✅ **"Add Python to PATH"**

Verify it works by opening a terminal and running:
```
python --version
```

---

### Step 2 — Create your Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **"New Application"** → give it a name (e.g. "SummaryBot")
3. In the left sidebar, click **"Bot"**
4. Click **"Add Bot"** → confirm
5. Under **"Privileged Gateway Intents"**, enable ALL THREE:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Click **"Save Changes"**
7. Click **"Reset Token"** → copy the token that appears (you'll need it shortly)

---

### Step 3 — Invite the bot to your server

1. In the left sidebar, click **"OAuth2"** → **"URL Generator"**
2. Under **Scopes**, check: ✅ `bot`
3. Under **Bot Permissions**, check:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Embed Links
   - ✅ Mention Everyone (only needed if you want it to ping)
4. Copy the generated URL at the bottom and open it in your browser
5. Select your server and click **Authorize**

---

### Step 4 — Set up the project files

1. Put all the bot files in a folder (e.g. `discord-summary-bot/`)
2. In that folder, rename `.env.example` to `.env`
3. Open `.env` in a text editor and replace `paste_your_token_here` with your actual bot token:

```
DISCORD_TOKEN=MTExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Step 5 — Install dependencies

Open a terminal in your bot folder and run:

```bash
pip install -r requirements.txt
```

---

### Step 6 — Run the bot

```bash
python bot.py
```

You should see:
```
✅ Logged in as SummaryBot#1234 (ID: 123456789)
Bot is ready and listening for mentions.
```

---

## Usage

In any channel the bot has access to, type:

```
@SummaryBot summarize
```

The bot will read up to 100 recent messages and reply with a summary embed.

---

## Keeping the bot running

The bot only runs while the terminal is open. To keep it running permanently:

- **Windows**: Use Task Scheduler or run it in Windows Terminal and leave it open
- **Mac/Linux**: Use `screen` or `tmux`, or set up a systemd service
- **Cloud**: You can host it for free on services like [Railway](https://railway.app) or [Fly.io](https://fly.io)

---

## File overview

```
discord-summary-bot/
├── bot.py           ← Main bot logic (connects to Discord, handles mentions)
├── summarizer.py    ← Text summarization engine (no AI needed)
├── requirements.txt ← Python packages to install
├── .env             ← Your secret bot token (never share this!)
├── .env.example     ← Template for .env
└── .gitignore       ← Keeps .env out of git
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: discord` | Run `pip install -r requirements.txt` |
| `LoginFailure` / invalid token | Double-check your token in `.env` |
| Bot doesn't respond to mentions | Make sure Message Content Intent is enabled in the Developer Portal |
| "I don't have permission" error | Re-invite the bot with the correct permissions (Step 3) |
| Summary seems off | Works best with 20+ messages; very short chats may not summarize well |
