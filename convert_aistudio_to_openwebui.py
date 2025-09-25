import json
import os
import uuid
from datetime import datetime
import argparse

def convert_aistudio_to_openwebui(aistudio_data, filename=None):
    """
    Convert AIStudio chat format to OpenWebUI chat format
    
    Args:
        aistudio_data (dict): Parsed AIStudio JSON data
        filename (str): Original filename for title
        
    Returns:
        list: OpenWebUI formatted chat data
    """
    # Extract conversation chunks
    chunks = aistudio_data.get("chunkedPrompt", {}).get("chunks", [])
    
    if not chunks:
        return []
    
    # Generate chat ID and user ID
    chat_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create message dictionary
    messages = {}
    messages_list = []
    
    # Track parent ID for building conversation chain
    parent_id = None
    
    # Generate base timestamp (using current time)
    base_timestamp = int(datetime.now().timestamp())
    
    # Keep track of pending thoughts
    pending_thoughts = []
    
    # Process each chunk in order to maintain sequence
    message_index = 0
    for i, chunk in enumerate(chunks):
        # Check if this is a thought chunk
        if chunk.get("isThought", False):
            # Collect thought content
            thought_content = chunk.get("text", "")
            
            # If there are parts, use those instead
            thought_parts = chunk.get("parts", [])
            if thought_parts:
                # Combine all thought parts that are marked as thoughts
                thought_texts = [part.get("text", "") for part in thought_parts if part.get("thought", False)]
                if thought_texts:
                    thought_content = "\n\n".join(thought_texts)
            
            pending_thoughts.append(thought_content)
            continue  # Skip creating a message for thought chunks
        
        # This is a regular chunk (user or model response)
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Determine role
        role = "user" if chunk.get("role") == "user" else "assistant"
        
        # Get content
        content = chunk.get("text", "")
        
        # If this is a model response and we have pending thoughts, prepend them
        if role == "assistant" and pending_thoughts:
            # Combine all pending thoughts
            combined_thoughts = "\n\n".join(pending_thoughts)
            # Format as details tag
            thought_section = f'<details type="reasoning" done="true" duration="5">\n<summary>Thought for 5 seconds</summary>\n{combined_thoughts}\n</details>\n\n'
            content = thought_section + content
            # Clear pending thoughts
            pending_thoughts = []
        
        # Create message object with sequential timestamps
        message = {
            "id": message_id,
            "parentId": parent_id,
            "childrenIds": [],
            "role": role,
            "content": content,
            "timestamp": base_timestamp + message_index
        }
        
        # Add model information for assistant messages
        if role == "assistant":
            message["model"] = aistudio_data.get("runSettings", {}).get("model", "unknown")
            message["modelName"] = "Converted from AIStudio"
            message["modelIdx"] = 0
            message["done"] = True
        
        # Add to messages dictionary
        messages[message_id] = message
        
        # Add to messages list
        messages_list.append(message)
        
        # Update parent ID for next iteration
        if parent_id and parent_id in messages:
            messages[parent_id]["childrenIds"].append(message_id)
        
        parent_id = message_id
        message_index += 1
    
    # Determine chat title (use filename or first user message)
    if filename:
        # Remove path and extension for cleaner title
        title = os.path.splitext(os.path.basename(filename))[0]
    else:
        title = "AIStudio Conversation"
        if messages_list and messages_list[0]["role"] == "user":
            title = messages_list[0]["content"][:50] + "..." if len(messages_list[0]["content"]) > 50 else messages_list[0]["content"]
    
    # Create the OpenWebUI chat structure
    openwebui_chat = {
        "id": chat_id,
        "user_id": user_id,
        "title": title,
        "chat": {
            "id": "",
            "title": title,
            "models": [aistudio_data.get("runSettings", {}).get("model", "unknown")],
            "params": {},
            "history": {
                "messages": messages,
                "currentId": parent_id  # Last message ID
            },
            "messages": messages_list,
            "tags": [],
            "timestamp": base_timestamp,
            "files": []
        },
        "updated_at": base_timestamp,
        "created_at": base_timestamp,
        "archived": False,
        "pinned": False,
        "meta": {
            "tags": ["aistudio", "converted"]
        }
    }
    
    return [openwebui_chat]

def process_file(input_path, output_path):
    """
    Process a single AIStudio file and convert it to OpenWebUI format
    
    Args:
        input_path (str): Path to input AIStudio file
        output_path (str): Path to output OpenWebUI JSON file
    """
    try:
        # Read AIStudio file
        with open(input_path, 'r', encoding='utf-8') as f:
            aistudio_data = json.load(f)
        
        # Get filename for title
        filename = os.path.basename(input_path)
        
        # Convert to OpenWebUI format
        openwebui_data = convert_aistudio_to_openwebui(aistudio_data, filename)
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(openwebui_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

def process_directory(input_dir, output_dir):
    """
    Process all AIStudio files in a directory and convert them to OpenWebUI format
    
    Args:
        input_dir (str): Path to directory containing AIStudio files
        output_dir (str): Path to directory for output OpenWebUI JSON files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all files in the input directory
    success_count = 0
    error_count = 0
    
    for filename in os.listdir(input_dir):
        # Process all files (AIStudio files don't necessarily have .json extension)
        input_path = os.path.join(input_dir, filename)
        
        # Skip directories
        if os.path.isdir(input_path):
            continue
            
        # Determine output filename (always add .json extension)
        if filename.endswith('.json'):
            output_filename = filename
        else:
            output_filename = filename + '.json'
            
        output_path = os.path.join(output_dir, output_filename)
        
        # Process the file
        if process_file(input_path, output_path):
            success_count += 1
        else:
            error_count += 1
    
    print(f"Conversion complete: {success_count} successful, {error_count} errors")

def main():
    parser = argparse.ArgumentParser(description='Convert AIStudio chat files to OpenWebUI format')
    parser.add_argument('input', help='Input file or directory path')
    parser.add_argument('output', help='Output file or directory path')
    parser.add_argument('--batch', action='store_true', help='Process multiple files in batch mode')
    
    args = parser.parse_args()
    
    if args.batch or os.path.isdir(args.input):
        # Batch mode - process directory
        process_directory(args.input, args.output)
    else:
        # Single file mode
        process_file(args.input, args.output)

if __name__ == "__main__":
    main()