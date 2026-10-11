from telethon import TelegramClient, events

# 1. Enter your API ID and API Hash from my.telegram.org
api_id = 34099834  # Replace with your API ID (integer)
api_hash = '5ddfb34c667d8dd8eb1c0c693d462e2d' # Replace with your API Hash (string)

# 2. Enter the channel IDs
# Note: Private channel IDs usually start with -100
SOURCE_CHANNEL = -3978130783 
DESTINATION_CHANNEL = 783726088 

# 3. Create the Telegram Client
# 'my_forwarder_session' creates a local file to save your login so you only log in once.
client = TelegramClient('my_forwarder_session', api_id, api_hash)

# 4. Listen for new messages in the source channel
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_new_messages(event):
    try:
        # Forward the exact message to the destination
        await event.forward_to(DESTINATION_CHANNEL)
        print(f"Successfully forwarded message ID: {event.id}")
    except Exception as e:
        print(f"Failed to forward message. Error: {e}")

print("Starting the Userbot...")
client.start()
print("Bot is listening for new messages. Press Ctrl+C to stop.")
client.run_until_disconnected()