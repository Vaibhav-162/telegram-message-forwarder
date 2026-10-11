import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 1. Load credentials securely from the .env file
load_dotenv()
API_ID = int(os.environ.get('TG_API_ID'))
API_HASH = os.environ.get('TG_API_HASH')

# 2. Channel IDs 
SOURCE_CHANNEL = -1003978130783

# Add as many destinations as you want to this list. 
# Use -100 IDs for private channels, and '@username' strings for public channels/people.
DESTINATION_CHANNELS = [
    -1001241292889, 
    '@TheBoyInYellow'
    # '@Keshav2900',  # Example of a second person
    # -1009876543210, # Example of a third channel
]

# 3. Create the client
client = TelegramClient('my_forwarder_session', API_ID, API_HASH)

# 4. Listen for new messages
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_new_messages(event):
    # Loop through every destination in the list
    for dest in DESTINATION_CHANNELS:
        try:
            await event.forward_to(dest)
            print(f"Successfully forwarded message ID {event.id} to {dest}")
        except Exception as e:
            print(f"Failed to forward message to {dest}. Error: {e}")

async def main():
    print("Starting client...")
    await client.start()
    
    print("Fetching dialogs to load channel access hashes into cache...")
    await client.get_dialogs()
    
    print("Bot is listening for new messages. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())