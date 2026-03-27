import discord
import os
from dotenv import load_dotenv
from summarizer import summarize_messages

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready and listening for mentions.")


@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the bot is mentioned and the message contains "summarize"
    if client.user in message.mentions and "summarize" in message.content.lower():
        await handle_summarize(message)


async def handle_summarize(message):
    channel = message.channel

    # Let the user know the bot is working
    thinking_msg = await channel.send("📖 Reading the channel... hang tight!")

    try:
        # Fetch up to 100 messages before this one (excluding the command itself)
        messages = []
        async for msg in channel.history(limit=100, before=message):
            if not msg.author.bot:  # Skip bot messages
                messages.append(msg)

        if not messages:
            await thinking_msg.edit(content="❌ No messages found to summarize.")
            return

        # Reverse so they're in chronological order
        messages.reverse()

        # Generate summary
        summary = summarize_messages(messages)

        # Build the embed response
        embed = discord.Embed(
            title="📋 Channel Summary",
            description=summary,
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text=f"Summarized {len(messages)} messages • Requested by {message.author.display_name}"
        )

        await thinking_msg.delete()
        await channel.send(embed=embed)

    except discord.Forbidden:
        await thinking_msg.edit(
            content="❌ I don't have permission to read this channel's history."
        )
    except Exception as e:
        await thinking_msg.edit(content=f"❌ Something went wrong: {e}")


client.run(TOKEN)
