import os
import json
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

# 3. File to store message ID mappings (Extremely lightweight for GCP Free Tier)
MAPPING_FILE = 'message_mapping.json'

def load_mapping():
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_mapping(mapping):
    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f)

# 4. Create the client
client = TelegramClient('my_forwarder_session', API_ID, API_HASH)

# 5. Listen for new messages
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_new_messages(event):
    # Load historical memory of copied messages
    mapping = load_mapping()
    source_id = str(event.message.id)
    reply_to_source_id = str(event.message.reply_to_msg_id) if event.message.reply_to_msg_id else None
    
    # Initialize the dictionary for this new message
    if source_id not in mapping:
        mapping[source_id] = {}

    # Loop through every destination in the list
    for dest in DESTINATION_CHANNELS:
        dest_str = str(dest)
        
        # Figure out if this new message is a reply to an older tracked message
        reply_to_dest_id = None
        if reply_to_source_id and reply_to_source_id in mapping:
            reply_to_dest_id = mapping[reply_to_source_id].get(dest_str)

        try:
            sent_msg = None
            
            # Check if the message contains any media (photo, video, document, etc.)
            if event.message.media:
                print(f"Downloading protected media for message {event.id}...")
                
                # Physically download the file to the GCP server
                file_path = await client.download_media(event.message)
                
                if file_path:
                    # Upload it back to Telegram as a new message, linking as a reply if applicable
                    sent_msg = await client.send_message(
                        dest, 
                        event.message.text, 
                        file=file_path,
                        reply_to=reply_to_dest_id
                    )
                    print(f"Successfully copied media message ID {event.id} to {dest}")
                    
                    # Delete the file from the GCP server to save storage space
                    os.remove(file_path)
                else:
                    # Fallback if the media couldn't be downloaded
                    sent_msg = await client.send_message(
                        dest, 
                        event.message.text,
                        reply_to=reply_to_dest_id
                    )
                    print(f"Successfully copied text-only (media failed) for ID {event.id} to {dest}")
            else:
                # If there is no media, just copy the text normally, linking as a reply if applicable
                sent_msg = await client.send_message(
                    dest, 
                    event.message.text,
                    reply_to=reply_to_dest_id
                )
                print(f"Successfully copied text message ID {event.id} to {dest}")
            
            # Save the newly created message ID to our memory dictionary
            if sent_msg:
                mapping[source_id][dest_str] = sent_msg.id
                
        except Exception as e:
            print(f"Failed to copy message to {dest}. Error: {e}")

    # Save the updated memory back to the JSON file
    save_mapping(mapping)

async def main():
    print("Starting client...")
    await client.start()
    
    print("Fetching dialogs to load channel access hashes into cache...")
    await client.get_dialogs()
    
    print("Bot is listening for new messages. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
