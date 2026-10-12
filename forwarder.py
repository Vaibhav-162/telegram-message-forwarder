import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 1. Load credentials securely from the .env file
load_dotenv()
API_ID = int(os.environ.get('TG_API_ID'))
API_HASH = os.environ.get('TG_API_HASH')
SOURCE_CHANNEL = int(os.environ.get('SOURCE_CHANNEL'))

# 2. Add as many destinations as you want to this list. 
# Use -100 IDs for private channels, and positive integers for direct messages.
DESTINATION_CHANNELS = [
    783726088,
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
            # Check if the message contains any media (photo, video, document, etc.)
            if event.message.media:
                print(f"Downloading protected media for message {event.id}...")
                
                # Physically download the file to the GCP server
                file_path = await client.download_media(event.message)
                
                if file_path:
                    # Upload it back to Telegram as a new message with the original text
                    await client.send_message(dest, event.message.text, file=file_path)
                    print(f"Successfully copied media message ID {event.id} to {dest}")
                    
                    # Delete the file from the GCP server to save storage space
                    os.remove(file_path)
                else:
                    # Fallback if the media couldn't be downloaded (e.g., unsupported format)
                    await client.send_message(dest, event.message.text)
                    print(f"Successfully copied text-only (media failed) for ID {event.id} to {dest}")
            else:
                # If there is no media, just copy the text normally
                await client.send_message(dest, event.message.text)
                print(f"Successfully copied text message ID {event.id} to {dest}")
                
        except Exception as e:
            print(f"Failed to copy message to {dest}. Error: {e}")

async def main():
    print("Starting client...")
    await client.start()
    
    print("Fetching dialogs to load channel access hashes into cache...")
    await client.get_dialogs()
    
    print("Bot is listening for new messages. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
