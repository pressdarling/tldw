# Character_Interaction_2.py
# Description: Functions for character interaction in Gradio UI
# Imports
import base64
import io
import uuid
from datetime import datetime
import logging
import json
import os
import gradio as gr
from PIL import Image
import sqlite3

from App_Function_Libraries.Chat import chat
#
# Local Imports
from App_Function_Libraries.DB.Character_Chat_DB import (
    add_character_card,
    get_character_cards,
    get_character_card_by_id,
    add_character_chat,
    get_character_chats,
    get_character_chat_by_id,
    update_character_chat,
    delete_character_chat,
    delete_character_card,
    update_character_card,
    save_chat_history_to_character_db
)
from App_Function_Libraries.Gradio_UI.Writing_tab import generate_writing_feedback
#
#######################################################################################################################
#
# Functions:

####################################################
#
# Utility Functions
def import_character_card(file):
    if file is None:
        logging.warning("No file provided for character card import")
        return None

    try:
        # Determine if the file is an image or a JSON file
        if file.name.lower().endswith(('.png', '.webp')):
            logging.info(f"Attempting to import character card from image: {file.name}")
            json_data = extract_json_from_image(file)
            if json_data:
                logging.info("JSON data extracted from image, attempting to parse")
                # Parse the JSON data (assuming import_character_card_json function exists)
                card_data = import_character_card_json(json_data)
                if card_data:
                    # Save the image data
                    with Image.open(file) as img:
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        card_data['image'] = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

                    # Ensure all necessary fields are present
                    if 'post_history_instructions' not in card_data:
                        card_data['post_history_instructions'] = ''
                    if 'first_message' not in card_data:
                        card_data['first_message'] = card_data.get('first_mes', "Hello! I'm ready to chat.")

                    # Save character card using the database function
                    character_id = add_character_card(card_data)
                    if character_id:
                        logging.info(f"Character card '{card_data['name']}' saved with ID {character_id}")
                        # Optionally, update the card_data with the assigned ID
                        card_data['id'] = character_id
                    else:
                        logging.error("Failed to save character card to database.")
                    return card_data
                else:
                    logging.warning("Failed to parse character card JSON.")
            else:
                logging.warning("No JSON data found in the image")
        else:
            logging.info(f"Attempting to import character card from JSON file: {file.name}")
            content = file.read().decode('utf-8')
            # Parse the JSON content (assuming import_character_card_json function exists)
            card_data = import_character_card_json(content)
            if card_data:
                # Ensure all necessary fields are present
                if 'image' not in card_data:
                    card_data['image'] = ''
                if 'post_history_instructions' not in card_data:
                    card_data['post_history_instructions'] = ''
                if 'first_message' not in card_data:
                    card_data['first_message'] = card_data.get('first_mes', "Hello! I'm ready to chat.")

                # Save character card using the database function
                character_id = add_character_card(card_data)
                if character_id:
                    logging.info(f"Character card '{card_data['name']}' saved with ID {character_id}")
                    # Optionally, update the card_data with the assigned ID
                    card_data['id'] = character_id
                else:
                    logging.error("Failed to save character card to database.")
                return card_data
            else:
                logging.warning("Failed to parse character card JSON.")
    except Exception as e:
        logging.error(f"Error importing character card: {e}")
    return None


def import_character_card_json(json_content):
    try:
        # Remove any leading/trailing whitespace
        json_content = json_content.strip()

        # Log the first 100 characters of the content
        logging.debug(f"JSON content (first 100 chars): {json_content[:100]}...")

        card_data = json.loads(json_content)
        logging.debug(f"Parsed JSON data keys: {list(card_data.keys())}")

        if 'spec' in card_data and card_data['spec'] == 'chara_card_v2':
            logging.info("Detected V2 character card")
            return card_data['data']
        else:
            logging.info("Assuming V1 character card")
            return card_data
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        logging.error(f"Problematic JSON content: {json_content[:500]}...")
    except Exception as e:
        logging.error(f"Unexpected error parsing JSON: {e}")
    return None

def extract_json_from_image(image_file):
    logging.debug(f"Attempting to extract JSON from image: {image_file.name}")
    try:
        with Image.open(image_file) as img:
            logging.debug("Image opened successfully")
            metadata = img.info
            if 'chara' in metadata:
                logging.debug("Found 'chara' in image metadata")
                chara_content = metadata['chara']
                logging.debug(f"Content of 'chara' metadata (first 100 chars): {chara_content[:100]}...")
                try:
                    decoded_content = base64.b64decode(chara_content).decode('utf-8')
                    logging.debug(f"Decoded content (first 100 chars): {decoded_content[:100]}...")
                    return decoded_content
                except Exception as e:
                    logging.error(f"Error decoding base64 content: {e}")

            logging.warning("'chara' not found in metadata, attempting to find JSON data in image bytes")
            # Alternative method to extract embedded JSON from image bytes if metadata is not available
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            img_str = img_bytes.decode('latin1')  # Use 'latin1' to preserve byte values

            # Search for JSON-like structures in the image bytes
            json_start = img_str.find('{')
            json_end = img_str.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                possible_json = img_str[json_start:json_end+1]
                try:
                    json.loads(possible_json)
                    logging.debug("Found JSON data in image bytes")
                    return possible_json
                except json.JSONDecodeError:
                    logging.debug("No valid JSON found in image bytes")

            logging.warning("No JSON data found in the image")
    except Exception as e:
        logging.error(f"Error extracting JSON from image: {e}")
    return None

def load_chat_history(file):
    try:
        content = file.read().decode('utf-8')
        chat_data = json.loads(content)

        # Extract history and character name from the loaded data
        history = chat_data.get('history') or chat_data.get('messages')
        character_name = chat_data.get('character') or chat_data.get('character_name')

        if not history or not character_name:
            logging.error("Chat history or character name missing in the imported file.")
            return None, None

        return history, character_name
    except Exception as e:
        logging.error(f"Error loading chat history: {e}")
        return None, None

def save_untracked_chat(history, char_data):
    if not char_data or not history:
        return "No chat to save or character not selected."

    character_id = char_data.get('id')
    if not character_id:
        return "Character ID not found."

    conversation_name = f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    chat_id = add_character_chat(character_id, conversation_name, history, is_snapshot=True)
    if chat_id:
        return f"Chat snapshot saved successfully with ID {chat_id}."
    else:
        return "Failed to save chat snapshot."

def regenerate_last_message(
    history, char_data, api_endpoint, api_key,
    temperature, user_name_val, auto_save
):
    if not history:
        return history, ""

    last_user_message = history[-1][0]
    new_history = history[:-1]

    # Re-generate the last message
    bot_message = generate_writing_feedback(
        last_user_message, char_data['name'], "Overall", api_endpoint, api_key
    )
    new_history.append((last_user_message, bot_message))

    # Update history
    history = new_history.copy()

    # Auto-save if enabled
    if auto_save:
        character_id = char_data.get('id')
        if character_id:
            conversation_name = f"Auto-saved chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            add_character_chat(character_id, conversation_name, history)
            save_status = "Chat auto-saved."
        else:
            save_status = "Character ID not found; chat not saved."
    else:
        save_status = ""

    return history, save_status

def update_chat(chat_id, updated_history):
    success = update_character_chat(chat_id, updated_history)
    if success:
        return "Chat updated successfully."
    else:
        return "Failed to update chat."

#
# End of Utility Functions
####################################################


####################################################
#
# Gradio tabs

def create_character_card_interaction_tab_two():
    with gr.TabItem("Chat with a Character Card"):
        gr.Markdown("# Chat with a Character Card")
        with gr.Row():
            with gr.Column(scale=1):
                character_image = gr.Image(label="Character Image", type="filepath")
                character_card_upload = gr.File(label="Upload Character Card")
                import_card_button = gr.Button("Import Character Card")
                load_characters_button = gr.Button("Load Existing Characters")
                character_dropdown = gr.Dropdown(label="Select Character", choices=[])
                user_name_input = gr.Textbox(label="Your Name", placeholder="Enter your name here")
                api_name_input = gr.Dropdown(
                    choices=[
                        "Local-LLM", "OpenAI", "Anthropic", "Cohere", "Groq", "DeepSeek", "Mistral",
                        "OpenRouter", "Llama.cpp", "Kobold", "Ooba", "Tabbyapi", "VLLM", "ollama", "HuggingFace",
                        "Custom-OpenAI-API"
                    ],
                    value="HuggingFace",
                    label="API for Interaction (Mandatory)"
                )
                api_key_input = gr.Textbox(
                    label="API Key (if not set in Config_Files/config.txt)",
                    placeholder="Enter your API key here", type="password"
                )
                temperature_slider = gr.Slider(
                    minimum=0.0, maximum=2.0, value=0.7, step=0.05, label="Temperature"
                )
                import_chat_button = gr.Button("Import Chat History")
                chat_file_upload = gr.File(label="Upload Chat History JSON", visible=False)

                # Checkbox to Decide Whether to Save Chats by Default
                auto_save_checkbox = gr.Checkbox(label="Save chats automatically", value=True)

            with gr.Column(scale=2):
                chat_history = gr.Chatbot(label="Conversation", height=800)
                user_input = gr.Textbox(label="Your message")
                send_message_button = gr.Button("Send Message")
                regenerate_button = gr.Button("Regenerate Last Message")
                clear_chat_button = gr.Button("Clear Chat")
                chat_media_name = gr.Textbox(label="Custom Chat Name (optional)", visible=True)
                save_chat_history_to_db = gr.Button("Save Chat History to Database")
                save_status = gr.Textbox(label="Save Status", interactive=False)

        # States
        character_data = gr.State(None)
        user_name = gr.State("")
        selected_chat_id = gr.State(None)  # To track the selected chat for updates

        # Callback Functions

        def import_chat_history(file, current_history, char_data):
            loaded_history, char_name = load_chat_history(file)
            if loaded_history is None:
                return current_history, char_data, "Failed to load chat history."

            # Check if the loaded chat is for the current character
            if char_data and char_data.get('name') != char_name:
                return current_history, char_data, (
                    f"Warning: Loaded chat is for character '{char_name}', "
                    f"but current character is '{char_data.get('name')}'. Chat not imported."
                )

            # If no character is selected, try to load the character from the chat
            if not char_data:
                characters = get_character_cards()
                character = next((char for char in characters if char['name'] == char_name), None)
                if character:
                    char_data = character
                else:
                    return current_history, char_data, (
                        f"Warning: Character '{char_name}' not found. Please select the character manually."
                    )

            return loaded_history, char_data, f"Chat history for '{char_name}' imported successfully."

        def load_character(name):
            characters = get_character_cards()
            character = next((char for char in characters if char['name'] == name), None)
            if character:
                first_message = character.get('first_message', "Hello! I'm ready to chat.")
                return character, [(None, first_message)] if first_message else [], None
            return None, [], None

        def load_character_image(name):
            character = next((char for char in get_character_cards() if char['name'] == name), None)
            if character and 'image' in character and character['image']:
                # Decode the base64 image
                image_data = base64.b64decode(character['image'])
                return image_data
            return None

        def load_character_and_image(name):
            char_data, chat_history, _ = load_character(name)
            if char_data and 'image' in char_data and char_data['image']:
                # Convert base64 image to bytes
                image_data = base64.b64decode(char_data['image'])
                # Save to a temporary file
                img = Image.open(io.BytesIO(image_data))
                img_path = f"temp_{uuid.uuid4()}.png"
                img.save(img_path)
                return char_data, chat_history, img_path
            return char_data, chat_history, None

        def character_chat_wrapper(
            message, history, char_data, api_endpoint, api_key,
            temperature, user_name_val, auto_save
        ):
            logging.debug("Entered character_chat_wrapper")
            if char_data is None:
                return history, "Please select a character first."

            if not user_name_val:
                user_name_val = "User"

            char_name = char_data.get('name', 'AI Assistant')

            # Prepare the character's background information
            char_background = f"""
            Name: {char_name}
            Description: {char_data.get('description', 'N/A')}
            Personality: {char_data.get('personality', 'N/A')}
            Scenario: {char_data.get('scenario', 'N/A')}
            """

            # Prepare the system prompt for character impersonation
            system_message = f"""You are roleplaying as {char_name}, the character described below. Respond to the user's messages in character, maintaining the personality and background provided. Do not break character or refer to yourself as an AI. Always refer to yourself as "{char_name}" and refer to the user as "{user_name_val}".

            {char_background}

            Additional instructions: {char_data.get('post_history_instructions', '')}
            """

            # Prepare media_content and selected_parts
            media_content = {
                'id': char_name,
                'title': char_name,
                'content': char_background,
                'description': char_data.get('description', ''),
                'personality': char_data.get('personality', ''),
                'scenario': char_data.get('scenario', '')
            }
            selected_parts = ['description', 'personality', 'scenario']

            prompt = char_data.get('post_history_instructions', '')

            # Prepare the input for the chat function
            if not history:
                full_message = (
                    f"{prompt}\n\n{user_name_val}: {message}"
                    if prompt else f"{user_name_val}: {message}"
                )
            else:
                full_message = f"{user_name_val}: {message}"

            # Call the chat function
            bot_message = chat(
                full_message,
                history,
                media_content,
                selected_parts,
                api_endpoint,
                api_key,
                prompt,
                temperature,
                system_message
            )

            # Update history
            history.append((message, bot_message))

            # Auto-save if enabled
            if auto_save:
                character_id = char_data.get('id')
                if character_id:
                    conversation_name = f"Auto-saved chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    add_character_chat(character_id, conversation_name, history)
                    save_status = "Chat auto-saved."
                else:
                    save_status = "Character ID not found; chat not saved."
            else:
                save_status = ""

            return history, save_status

        def save_chat_history_to_db_wrapper(
            chat_history, conversation_id, media_content,
            chat_media_name, char_data, auto_save
        ):
            if not char_data or not chat_history:
                return "No character or chat history available.", ""

            character_id = char_data.get('id')
            if not character_id:
                return "Character ID not found.", ""

            conversation_name = chat_media_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            chat_id = add_character_chat(character_id, conversation_name, chat_history)
            if chat_id:
                return f"Chat saved successfully with ID {chat_id}.", ""
            else:
                return "Failed to save chat.", ""

        def update_character_info(name):
            return load_character_and_image(name)

        def on_character_select(name):
            logging.debug(f"Character selected: {name}")
            return update_character_info(name)

        def clear_chat_history():
            return [], None  # Return empty list for chat_history and None for character_data

        def regenerate_last_message(
            history, char_data, api_endpoint, api_key,
            temperature, user_name_val, auto_save
        ):
            if not history:
                return history, ""

            last_user_message = history[-1][0]
            new_history = history[:-1]

            # Re-generate the last message
            bot_message = generate_writing_feedback(
                last_user_message, char_data['name'], "Overall", api_endpoint, api_key
            )
            new_history.append((last_user_message, bot_message))

            # Update history
            history = new_history.copy()

            # Auto-save if enabled
            if auto_save:
                character_id = char_data.get('id')
                if character_id:
                    conversation_name = f"Auto-saved chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    add_character_chat(character_id, conversation_name, history)
                    save_status = "Chat auto-saved."
                else:
                    save_status = "Character ID not found; chat not saved."
            else:
                save_status = ""

            return history, save_status

        def toggle_chat_file_upload():
            return gr.update(visible=True)

        def save_untracked_chat_action(history, char_data):
            if not char_data or not history:
                return "No chat to save or character not selected."

            character_id = char_data.get('id')
            if not character_id:
                return "Character ID not found."

            conversation_name = f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            chat_id = add_character_chat(character_id, conversation_name, history, is_snapshot=True)
            if chat_id:
                return f"Chat snapshot saved successfully with ID {chat_id}."
            else:
                return "Failed to save chat snapshot."

        def select_chat_for_update():
            # Fetch all chats for the selected character
            if character_data.value:
                character_id = character_data.value.get('id')
                if character_id:
                    chats = get_character_chats(character_id)
                    chat_choices = [
                        f"{chat['conversation_name']} (ID: {chat['id']})" for chat in chats
                    ]
                    return gr.update(choices=chat_choices), None
            return gr.update(choices=[]), "No character selected."

        def load_selected_chat(chat_selection):
            if not chat_selection:
                return [], "No chat selected."

            try:
                chat_id = int(chat_selection.split('(ID: ')[1].rstrip(')'))
                chat = get_character_chat_by_id(chat_id)
                if chat:
                    history = chat['chat_history']
                    selected_chat_id.value = chat_id  # Update the selected_chat_id state
                    return history, f"Loaded chat '{chat['conversation_name']}' successfully."
                else:
                    return [], "Chat not found."
            except Exception as e:
                logging.error(f"Error loading selected chat: {e}")
                return [], f"Error loading chat: {e}"

        def update_chat(chat_id, updated_history):
            success = update_character_chat(chat_id, updated_history)
            if success:
                return "Chat updated successfully."
            else:
                return "Failed to update chat."

        # Define States for conversation_id and media_content, which are required for saving chat history
        conversation_id = gr.State(str(uuid.uuid4()))
        media_content = gr.State({})

        # Button Callbacks

        import_card_button.click(
            fn=import_character_card,
            inputs=[character_card_upload],
            outputs=[character_data, character_dropdown, save_status]
        )

        load_characters_button.click(
            fn=lambda: [char['name'] for char in get_character_cards()],
            outputs=character_dropdown
        )

        clear_chat_button.click(
            fn=clear_chat_history,
            inputs=[],
            outputs=[chat_history, character_data]
        )

        character_dropdown.change(
            fn=on_character_select,
            inputs=[character_dropdown],
            outputs=[character_data, chat_history, character_image]
        )

        send_message_button.click(
            fn=character_chat_wrapper,
            inputs=[
                user_input,
                chat_history,
                character_data,
                api_name_input,
                api_key_input,
                temperature_slider,
                user_name_input,
                auto_save_checkbox  # Pass the auto_save state
            ],
            outputs=[chat_history, save_status]
        ).then(lambda: "", outputs=user_input)

        regenerate_button.click(
            fn=regenerate_last_message,
            inputs=[
                chat_history,
                character_data,
                api_name_input,
                api_key_input,
                temperature_slider,
                user_name_input,
                auto_save_checkbox
            ],
            outputs=[chat_history, save_status]
        )

        import_chat_button.click(
            fn=lambda: gr.update(visible=True),
            outputs=chat_file_upload
        )

        chat_file_upload.change(
            fn=import_chat_history,
            inputs=[chat_file_upload, chat_history, character_data],
            outputs=[chat_history, character_data, save_status]
        )

        save_chat_history_to_db.click(
            fn=save_chat_history_to_db_wrapper,
            inputs=[
                chat_history,
                conversation_id,
                media_content,
                chat_media_name,
                character_data,
                auto_save_checkbox  # Pass the auto_save state
            ],
            outputs=[conversation_id, save_status]
        )

        # Additional Buttons for Saving Snapshots and Updating Chats
        with gr.Row():
            save_snapshot_button = gr.Button("Save Chat Snapshot")
            update_chat_dropdown = gr.Dropdown(label="Select Chat to Update", choices=[])
            load_selected_chat_button = gr.Button("Load Selected Chat")
            update_chat_button = gr.Button("Update Selected Chat")

        # Populate the update_chat_dropdown based on selected character
        character_dropdown.change(
            fn=select_chat_for_update,
            inputs=[],
            outputs=[update_chat_dropdown, save_status]
        )

        load_selected_chat_button.click(
            fn=load_selected_chat,
            inputs=[update_chat_dropdown],
            outputs=[chat_history, save_status]
        )

        save_snapshot_button.click(
            fn=save_untracked_chat_action,
            inputs=[chat_history, character_data],
            outputs=save_status
        )

        update_chat_button.click(
            fn=update_chat,
            inputs=[selected_chat_id, chat_history],
            outputs=save_status
        )

        return character_data, chat_history, user_input, user_name, character_image


def create_chat_management_tab_two():
    with gr.TabItem("Chat Management"):
        gr.Markdown("# Chat Management")

        with gr.Row():
            search_query = gr.Textbox(label="Search Conversations or Characters")
            search_button = gr.Button("Search")

        conversation_list = gr.Dropdown(label="Select Conversation or Character", choices=[])
        conversation_mapping = gr.State({})

        with gr.Tabs():
            with gr.TabItem("Edit"):
                chat_content = gr.TextArea(label="Chat/Character Content (JSON)", lines=20, max_lines=50)
                save_button = gr.Button("Save Changes")
                delete_button = gr.Button("Delete Conversation/Character", variant="stop")

            with gr.TabItem("Preview"):
                chat_preview = gr.HTML(label="Chat/Character Preview")
        result_message = gr.Markdown("")

        # Callback Functions

        def search_conversations_or_characters(query):
            # Search in both CharacterChats and CharacterCards
            characters = get_character_cards()
            # FIXME - Add option to search specific a character_id
            chats = get_character_chats()  # Retrieves all chats when character_id is None

            # Filter based on query (case-insensitive substring match)
            filtered_chats = [chat for chat in chats if query.lower() in chat['conversation_name'].lower()]
            filtered_characters = [char for char in characters if query.lower() in char['name'].lower()]

            chat_choices = [f"Chat: {conv['conversation_name']} (ID: {conv['id']})" for conv in filtered_chats]
            character_choices = [f"Character: {char['name']} (ID: {char['id']})" for char in filtered_characters]

            all_choices = chat_choices + character_choices
            mapping = {choice: conv['id'] for choice, conv in zip(chat_choices, filtered_chats)}
            mapping.update({choice: char['id'] for choice, char in zip(character_choices, filtered_characters)})

            return gr.update(choices=all_choices), mapping

        def load_conversation_or_character(selected, conversation_mapping):
            if not selected or selected not in conversation_mapping:
                return "", "<p>No selection made.</p>"

            selected_id = conversation_mapping[selected]
            if selected.startswith("Chat:"):
                # Load Chat
                chat = get_character_chat_by_id(selected_id)
                if chat:
                    json_content = json.dumps({
                        "conversation_id": chat['id'],
                        "conversation_name": chat['conversation_name'],
                        "messages": chat['chat_history']
                    }, indent=2)

                    # Create HTML preview
                    html_preview = "<div style='max-height: 500px; overflow-y: auto;'>"
                    for idx, (user_msg, bot_msg) in enumerate(chat['chat_history']):
                        user_style = "background-color: #e6f3ff; padding: 10px; border-radius: 5px;"
                        bot_style = "background-color: #f0f0f0; padding: 10px; border-radius: 5px;"

                        html_preview += f"<div style='margin-bottom: 10px;'>"
                        html_preview += f"<div style='{user_style}'><strong>User:</strong> {user_msg}</div>"
                        html_preview += f"<div style='{bot_style}'><strong>Bot:</strong> {bot_msg}</div>"
                        html_preview += "</div>"
                    html_preview += "</div>"

                    return json_content, html_preview
            elif selected.startswith("Character:"):
                # Load Character
                character = get_character_card_by_id(selected_id)
                if character:
                    json_content = json.dumps({
                        "id": character['id'],
                        "name": character['name'],
                        "description": character['description'],
                        "personality": character['personality'],
                        "scenario": character['scenario'],
                        "post_history_instructions": character['post_history_instructions'],
                        "first_message": character['first_message'],
                        "image": character['image']  # Include image data if necessary
                    }, indent=2)

                    # Create HTML preview
                    html_preview = f"""
                    <div>
                        <h2>{character['name']}</h2>
                        <p><strong>Description:</strong> {character['description']}</p>
                        <p><strong>Personality:</strong> {character['personality']}</p>
                        <p><strong>Scenario:</strong> {character['scenario']}</p>
                        <p><strong>First Message:</strong> {character['first_message']}</p>
                    </div>
                    """

                    return json_content, html_preview

            return "", "<p>Unable to load the selected item.</p>"

        def validate_content(selected, content):
            if selected.startswith("Chat:"):
                # Validate Chat JSON
                try:
                    data = json.loads(content)
                    assert "conversation_id" in data and "messages" in data
                    return True, data
                except Exception as e:
                    return False, f"Invalid Chat JSON: {e}"
            elif selected.startswith("Character:"):
                # Validate Character JSON
                try:
                    data = json.loads(content)
                    assert "id" in data and "name" in data
                    return True, data
                except Exception as e:
                    return False, f"Invalid Character JSON: {e}"
            return False, "Unknown selection type."

        def save_conversation_or_character(selected, conversation_mapping, content):
            if not selected or selected not in conversation_mapping:
                return "Please select an item to save.", "<p>No changes made.</p>"

            is_valid, result = validate_content(selected, content)
            if not is_valid:
                return f"Error: {result}", "<p>No changes made due to validation error.</p>"

            selected_id = conversation_mapping[selected]

            if selected.startswith("Chat:"):
                # Update Chat
                chat_data = result
                success = update_character_chat(selected_id, chat_data['messages'])
                if success:
                    return "Chat updated successfully.", "<p>Chat updated.</p>"
                else:
                    return "Failed to update chat.", "<p>Failed to update chat.</p>"
            elif selected.startswith("Character:"):
                # Update Character
                character_data = result
                # Ensure the JSON aligns with the expected fields
                card_data = {
                    'name': character_data.get('name'),
                    'description': character_data.get('description'),
                    'personality': character_data.get('personality'),
                    'scenario': character_data.get('scenario'),
                    'post_history_instructions': character_data.get('post_history_instructions'),
                    'first_message': character_data.get('first_message'),
                    'image': character_data.get('image', '')  # Handle image data appropriately
                }
                success = update_character_card(selected_id, card_data)
                if success:
                    return "Character updated successfully.", "<p>Character updated.</p>"
                else:
                    return "Failed to update character.", "<p>Failed to update character.</p>"

            return "Unknown item type.", "<p>No changes made.</p>"

        def delete_conversation_or_character(selected, conversation_mapping):
            if not selected or selected not in conversation_mapping:
                return "Please select an item to delete.", "<p>No changes made.</p>", gr.update(choices=[])

            selected_id = conversation_mapping[selected]

            if selected.startswith("Chat:"):
                success = delete_character_chat(selected_id)
                if success:
                    # Remove the deleted item from the conversation list
                    updated_choices = [choice for choice in conversation_mapping.keys() if choice != selected]
                    # Remove the item from the mapping
                    conversation_mapping.value.pop(selected, None)
                    return "Chat deleted successfully.", "<p>Chat deleted.</p>", gr.update(choices=updated_choices)
                else:
                    return "Failed to delete chat.", "<p>Failed to delete chat.</p>", gr.update()
            elif selected.startswith("Character:"):
                success = delete_character_card(selected_id)
                if success:
                    # Remove the deleted item from the conversation list
                    updated_choices = [choice for choice in conversation_mapping.keys() if choice != selected]
                    # Remove the item from the mapping
                    conversation_mapping.value.pop(selected, None)
                    return "Character deleted successfully.", "<p>Character deleted.</p>", gr.update(choices=updated_choices)
                else:
                    return "Failed to delete character.", "<p>Failed to delete character.</p>", gr.update()

            return "Unknown item type.", "<p>No changes made.</p>", gr.update()

        # Gradio Component Callbacks

        search_button.click(
            fn=search_conversations_or_characters,
            inputs=[search_query],
            outputs=[conversation_list, conversation_mapping]
        )

        conversation_list.change(
            fn=load_conversation_or_character,
            inputs=[conversation_list, conversation_mapping],
            outputs=[chat_content, chat_preview]
        )

        save_button.click(
            fn=save_conversation_or_character,
            inputs=[conversation_list, conversation_mapping, chat_content],
            outputs=[result_message, chat_preview]
        )

        delete_button.click(
            fn=delete_conversation_or_character,
            inputs=[conversation_list, conversation_mapping],
            outputs=[result_message, chat_preview, conversation_list]
        )

    return (
        search_query, search_button, conversation_list, conversation_mapping,
        chat_content, save_button, delete_button, result_message, chat_preview
    )

#
# End of Character_Interaction_2.py
#######################################################################################################################