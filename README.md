# Summary Bot — Setup Guide

Mention the bot in any channel to get a summary of the last 5 hours of conversation:

```
@SummaryBot summarize
```

---

## Step 1 — Create the Discord bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → name it (e.g. "SummaryBot") → Create
3. Click **Bot** in the left sidebar
4. Scroll to **Privileged Gateway Intents** and turn ON:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click **Save Changes**
6. Click **Reset Token** → copy the token and save it somewhere safe

---

## Step 2 — Invite the bot to your server

1. Click **OAuth2** → **URL Generator** in the left sidebar
2. Under Scopes, check: ✅ `bot`
3. Under Bot Permissions, check:
   - ✅ Read Messages / View Channels
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Embed Links
4. Copy the URL at the bottom, open it in your browser
5. Select your server → Authorize

---

## Step 3 — Put the code on GitHub

1. Go to https://github.com and sign in (or create a free account)
2. Click **+** → **New repository**
3. Name it `summarybot`, set it to **Private**, click **Create repository**
4. On the next page click **uploading an existing file**
5. Drag in all three files: `bot.py`, `requirements.txt`, `render.yaml`
6. Click **Commit changes**

---

## Step 4 — Deploy on Render (free, runs 24/7)

1. Go to https://render.com and sign up with your GitHub account
2. Click **New** → **Blueprint** (this reads the `render.yaml` file automatically)
3. Select your `summarybot` repository
4. Render will find the `render.yaml` and set everything up
5. It will pause and ask for the value of `DISCORD_TOKEN` — paste your token here
6. Click **Apply** and wait ~2 minutes for it to build

Once it says **Live**, your bot is running 24/7 for free.

---

## Using the bot

In any channel the bot has access to, type:

```
@SummaryBot summarize
```

The bot will read up to 1000 messages from the last 5 hours and post a summary showing:
- Who was active
- What topics came up
- The most representative messages

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Bot doesn't respond | Check Message Content Intent is enabled in the Developer Portal |
| "No messages found" | There were no non-bot messages in the last 5 hours |
| Render build fails | Make sure all 3 files are in the repo |
| Invalid token error | Re-copy the token from the Developer Portal and update it in Render's Environment settings |
