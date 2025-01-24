import json
import os
import requests
import google.generativeai as ai
from time import sleep
from config import JSON_FILE_PATH, API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID
from flask import render_template, request, jsonify, Response
from Logger import Logger
from flask import jsonify


class PromptHandler:   
    def __init__(self):
        self.api_keys = API_KEY
        self.current_key_index = 0
        self.api_key = self.api_keys[self.current_key_index]
        self.api_keys = ai.configure(api_key=self.api_key)
        self.model = ai.GenerativeModel("gemini-2.0-flash-exp")
        self.chat = self.model.start_chat()
        self.user_data = JSON_FILE_PATH
        self.user = self.load_user()

    def switch_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    
    def generate_message(self, prompt):
        max_retries = 3
        delay = 5

        for attempt in range(1, max_retries + 1):
            try:
                response = self.chat.send_message(prompt)
                return response.text  
            
            except Exception as e:
                Logger.log(f"Response error (attempt {attempt}): {e}. Switching to new API key.")
                if attempt < max_retries:
                    self.switch_api_key()
                    sleep(delay)

        return False

    def load_user(self):
        try:
            if os.path.exists(self.user_data):
                with open(self.user_data, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            Logger.log(f"Error loading pets data: {e}")
        return {}

    def load_training_data(self, control_number):
        try:
            with open('training_data.jsonl', 'r') as file:
                training_data = [
                    json.loads(line.strip())[control_number]
                    for line in file
                    if control_number in json.loads(line.strip())
                ]
            
            training_data.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return training_data

        except Exception as e:
            Logger.log(f"Error loading training data for {control_number}: {e}")
            return []

    def prompt_message(self, control_number, user_input): 
        user_data = self.user.get(control_number)
        if not user_data:
            return jsonify({"success": False, "message": "Pet not found"}), 404

        training_data = self.load_training_data(control_number)

        owner_email = user_data.get('email', 'No email found.')
        owner_phone = user_data.get('phone', 'No phone number found.')

        training_context = "\n".join(
            f"{entry['input']}\n{entry['output']}" for entry in training_data
        )

        prompt = (
            f"You are a friendly and helpful assistant designed specifically for kids and first-time pet owners.\n\n"
            f"Your task is to respond accurately and cheerfully based on:\n"
            f"- User input: {user_input}\n"
            f"- Pet data: {user_data}\n"
            f"- Context from prior conversations: {training_context}\n\n"
            f"IMPORTANT GUIDELINES:\n"
            f"1. DO NOT repeat or restate the user’s input in your response.\n"
            f"   Example:\n"
            f"   - User Input: 'What is the size and weight of this dog?'\n"
            f"   - Incorrect: 'What is the size and weight of this dog?'\n"
            f"   - Correct: 'A Shih-Tzu typically stands 20-28 cm tall and weighs 4-7 kg.'\n"
            f"2. Keep answers brief and clear, using simple and kind language suitable for kids.\n"
            f"3. Tailor responses to the query:\n"
            f"   - Describe pets in a fun and friendly way.\n"
            f"   - Offer practical advice for feeding, grooming, and playing with pets.\n"
            f"   - Explain body parts or organs positively and in a non-scary manner.\n"
            f"   - For health concerns, suggest practical steps (e.g., 'Make sure Max drinks water and rests.').\n"
            f"   - If asked about the owner, provide contact details: {owner_email}, {owner_phone}.\n"
            f"4. If specific information is missing:\n"
            f"   - Use reliable online sources to find accurate answers.\n"
            f"   - Clearly indicate when information comes from online research.\n"
            f"5. Maintain a cheerful and encouraging tone, inviting users to ask more questions about pet care.\n"
        )

        try:
            response = self.generate_message(prompt)

            if not response:
                no_answer_keywords = [
                    "sorry", "can't", "don't know", "don't understand", "help", "unable", "error", "clarify",
                    "information", "not sure", "beyond my knowledge", "not able", "process"
                ]

                if any(keyword.lower() in response.lower() for keyword in no_answer_keywords) or not response.strip():
                    search_results = self.perform_duckduckgo_search(user_input)
                    if search_results:
                        response = (
                            f"I couldn't find specific data in the records, but here's what I found online: {search_results}. "
                            "Let me know if you'd like more help!"
                        )
                    else:
                        response = (
                            "I'm here to help! While I don't have enough data to answer that specific question, "
                            "I can assist with general pet information, tips for care, or updating the NFC tag. Let me know how I can help!"
                        )

            return jsonify({"response": response})

        except Exception as e:
            Logger.log(f"Error generating response: {e}")
            return jsonify({"success": False, "message": "An error occurred while generating the response."}), 500


    def perform_duckduckgo_search(self, query):
        search_url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }

        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("AbstractText", "No results found")
        except Exception as e:
            Logger.log(f"Error performing DuckDuckGo search: {e}")
            return None

    def handle_prompt(self, control_number):
        try:
            if request.method == 'POST':
                data = request.get_json()
                if not data:
                    Logger.log(f"Request received with no data for pet {control_number}")
                    return jsonify({"success": False, "message": "No data received in POST body."}), 400

                user_input = data.get('prompt', '').strip()
                if not user_input:
                    Logger.log(f"Received empty or invalid prompt for pet {control_number}")
                    return jsonify({"success": False, "message": "Invalid or empty prompt."}), 400

                Logger.log(f"Received request data for pet {control_number}: {data}")

                response = self.prompt_message(control_number, user_input)

                # Ensure response is a valid Response object
                if not isinstance(response, Response):
                    Logger.log(f"Unexpected response format from pet_handler for {control_number}: {response}")
                    return jsonify({"success": False, "message": "Unexpected response from pet_handler."}), 500

                try:
                    response_json = response.get_json()
                    ai_response = response_json.get("response")
                    
                    if ai_response:
                        Logger.log_for_ai_training(control_number, user_input, ai_response)

                    return jsonify(response_json)

                except Exception as decode_error:
                    Logger.log(f"Error decoding JSON response: {decode_error}")
                    return jsonify({"success": False, "message": "Error decoding JSON response from pet_handler."}), 500

            # If not POST, handle rendering pet profile page
            pet_data = self.user.get(control_number)
            if not pet_data:
                Logger.log(f"Pet not found for control_number {control_number}")
                return jsonify({"success": False, "message": "Pet not found"}), 404

            return render_template('pet-profile-prompt.html', pet=pet_data, control_number=control_number)

        except Exception as e:
            Logger.log(f"Error processing prompt for pet {control_number}: {str(e)}")
            return jsonify({"success": False, "message": "An error occurred while processing your request."}), 500
