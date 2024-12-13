import json
import os
import subprocess
from datetime import datetime
from config import JSON_FILE_PATH
from Logger import Logger
from FileHandler import FileHandler
from flask import request, render_template, jsonify
import google.generativeai as ai

class PromptProcessor:
    """Class to handle text prompts and responses using Google Gemini AI."""
    
    def __init__(self, api_key):
        """
        Initializes the PromptProcessor with the Google Gemini API key.
        
        :param api_key: API key for authentication.
        """
        ai.configure(api_key=api_key)
        self.model = ai.GenerativeModel("gemini-pro")
        self.chat = self.model.start_chat()

    def generate_message(self, prompt):
        """
        Sends a prompt to the Gemini model and retrieves the response.
        
        :param prompt: The text prompt to send.
        :return: Response message from the model.
        """
        try:
            response = self.chat.send_message(prompt)
            response_msg = response.text
            return response_msg
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "An unexpected error occurred while generating the response."

class PetHandler:
    def __init__(self, json_file_path=JSON_FILE_PATH):
        self.json_file_path = json_file_path
        self.pets = self.load_pets()
    
    def load_pets(self):
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            Logger.log(f"Error loading pets data: {e}")
        return {}

    def load_training_data(self, control_number):
        """
        Load training data from a .jsonl file and filter by user/pet control number.
        Returns a list of previous interactions that can be used as context in the prompt.
        """
        training_data = []
        try:
            with open('training_data.jsonl', 'r') as file:
                for line in file:
                    entry = json.loads(line.strip())  # Parse each line
                    if control_number in entry:  # Check if the control number is a key in the entry
                        training_data.append(entry[control_number])  # Append the data associated with the control number
        except Exception as e:
            Logger.log(f"Error loading training data for {control_number}: {e}")
        return training_data


    def save_pets(self):
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.pets, f, indent=4)
        except Exception as e:
            Logger.log(f"Error saving pets data: {e}")

    def is_valid_control_number(self, control_number):
        return control_number.isalnum() and control_number not in self.pets

    def is_empty(self, data, key):
        # Check if the key exists and is a dictionary with a petname entry
        if key not in data or not isinstance(data[key], dict):
            return False  # Key does not exist or is not in the expected format

        # If 'petname' is empty, set it to "new user"
        if data[key].get("petname", "").strip() == "":
            data[key]["petname"] = "new user"
            try:
                self.save_pets()
                Logger.log(f"New user name was triggered and data was saved successfully")
                return True
            except Exception as e:
                Logger.log(f"Failed to save data: {e}")
                return False  # Return False if saving fails

        return False
        
    def handle_pet_profile(self, control_number, template):
        pet = self.pets.get(control_number) if control_number else None

        # Check if the control_number is valid
        if not pet:
            return "Pet not found or invalid control number", 404

        # Check if the pet profile is empty
        if self.is_empty(self.pets, control_number):
            return render_template(
                "setup-tag.html",
                title="Setup Your Tag",
                message=control_number
            ), 400

        if request.method == 'POST':
            # Collect form data
            pet_data = {
                'petname': request.form.get('petNameInput', ''),
                'petage': request.form.get('petAgeInput', ''),
                'petbreed': request.form.get('petBreedInput', ''),
                'email': request.form.get('email', ''),
                'phone': request.form.get('phone', ''),
                'address': request.form.get('address', ''),
                "control_number": request.form.get('petControlNumber', ''),
                'medical history': request.form.get('petMedicalHistoryInput', ''),
                'vaccination date': request.form.get('vaccinationDateInput', ''),
                'vet check-up date': request.form.get('vetCheckupDateInput', ''),
                'allergy status': request.form.get('allergyStatusInput', ''),
                'feed time': request.form.get('feedTimeInput', ''),
                'walk time': request.form.get('walkTimeInput', ''),
                'vet appointment date': request.form.get('vetAppointmentDateInput', ''),
                'walk distance': request.form.get('walkDistanceInput', ''),
                'last activity': request.form.get('lastActivityInput', '')
            }

            control_number = pet_data["control_number"]
                
            # Validate control number
            if not self.is_valid_control_number(control_number):
                return render_template(template, pet=pet, error="Invalid or duplicate control number")

            # Handle file upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename == '':
                    return render_template(template, pet=pet, error="No selected file")
                if file and FileHandler.allowed_file(file.filename):
                    try:
                        pet_data['photo'] = FileHandler.save_and_convert_image(file, control_number)
                    except Exception as e:
                        Logger.log(f"Error saving or converting image: {e}")
                        return render_template(template, pet=pet, error="Failed to convert image.")
                else:
                    return render_template(template, pet=pet, error="Invalid file type")

            # Save pet data
            self.pets[control_number] = pet_data
            self.save_pets()
            
        
        return render_template(template, pet=pet)

    def pet_profile_edit(self, control_number):
        return self.handle_pet_profile(control_number, 'pet-profile-edit.html')

    def pet_profile_view(self, control_number):
        return self.handle_pet_profile(control_number, 'pet-profile-view.html')

    def update_pet_profile(self):
        try:
            # Extract control_number from request.form (for multipart data)
            control_number = request.form.get('control_number')
            Logger.log(f'the control number is {control_number}')
            
            if not control_number or control_number not in self.pets:
                return jsonify({"success": False, "message": "Pet not found"}), 404

            pet = self.pets[control_number]

            # Update pet details using request.form for other fields
            pet['photo'] = request.form.get('photo', pet.get('photo'))
            pet['petname'] = request.form.get('petname', pet.get('petname'))
            pet['petage'] = request.form.get('petage', pet.get('petage'))
            pet['petbreed'] = request.form.get('petbreed', pet.get('petbreed'))
            pet['email'] = request.form.get('email', pet.get('email'))
            pet['phone'] = request.form.get('phone', pet.get('phone'))
            pet['address'] = request.form.get('address', pet.get('address'))

            # Handle file upload from request.files
            file = request.files.get('photo')
            if file:
                if FileHandler.allowed_file(file.filename):
                    try:
                        pet['photo'] = FileHandler.save_and_convert_image(file, control_number)
                    except Exception as e:
                        Logger.log(f"Error saving or converting image: {e}")
                        return jsonify({"success": False, "message": "Failed to convert image."}), 500
                else:
                    return jsonify({"success": False, "message": "Invalid file type"}), 400

            # Save the updated pet data
            self.pets[control_number] = pet
            try:
                Logger.log(f"Updating pet info: {pet['petname']}, {pet['petage']}, {pet['petbreed']}")
                self.save_pets()  # Saving updated pet data
                
            except Exception as e:
                Logger.log(f"Error saving pet data: {e}")
                return jsonify({"success": False, "message": "An error occurred while saving the data."}), 500

            return jsonify({"success": True})

        except Exception as e:
            Logger.log(f"Unexpected error: {e}")
            return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


    def update_medical_history(self, data):
        control_number = data.get('control_number')
        if not control_number or control_number not in self.pets:
            return jsonify({"success": False, "message": "Pet not found"}), 404

        pet = self.pets[control_number]

        # Update medical history data
        pet['medical_history'] = data.get('medical_history', pet.get('medical_history'))
        pet['vaccination_date'] = data.get('vaccination_date', pet.get('vaccination_date'))
        pet['vet_checkup_date'] = data.get('vet_checkup_date', pet.get('vet_checkup_date'))
        pet['allergy_status'] = data.get('allergy_status', pet.get('allergy_status'))

        # Save updated pet data
        self.pets[control_number] = pet
        self.save_pets()
        

        return jsonify({"success": True})

    def update_care_reminders(self, data):
        control_number = data.get('control_number')
        if not control_number or control_number not in self.pets:
            return jsonify({"success": False, "message": "Pet not found"}), 404

        pet = self.pets[control_number]

        # Update care reminder data
        pet['feed_time'] = data.get('feed_time', pet.get('feed_time'))
        pet['walk_time'] = data.get('walk_time', pet.get('walk_time'))
        pet['vet_appointment_date'] = data.get('vet_appointment_date', pet.get('vet_appointment_date'))

        # Save updated pet data
        self.pets[control_number] = pet
        self.save_pets()
        

        return jsonify({"success": True})

    def update_activity_log(self, data):
        control_number = data.get('control_number')
        if not control_number or control_number not in self.pets:
            return jsonify({"success": False, "message": "Pet not found"}), 404

        pet = self.pets[control_number]

        # Update activity log data
        pet['walk_distance'] = data.get('walk_distance', pet.get('walk_distance'))
        pet['last_activity'] = data.get('last_activity', pet.get('last_activity'))

        # Save updated pet data
        self.pets[control_number] = pet
        self.save_pets()
        

        return jsonify({"success": True})

    def prompt_message(self, control_number, user_input):
        """
        Handles user input, retrieves relevant data, and generates a response using an AI prompt processor.
        """
        pet_data = self.pets.get(control_number)
        training_data = self.load_training_data(control_number)

        if not pet_data:
            return jsonify({"success": False, "message": "Pet not found"}), 404

        # Create an instance of PromptProcessor with the API key
        prompt_processor = PromptProcessor(api_key='AIzaSyC0CI07I0ozsLXFVNaEkMec_I4iTuyrmFE')

        # Keywords to check for owner-related questions
        owner_keywords = ["contact the owner", "owner's email", "who is the owner", "owner contact", "reach the owner"]

        # Add training data as context to the prompt
        training_context = "\n".join(
            [f"Input: {entry['input']}\nResponse: {entry['output']}" for entry in training_data]
        )

        # Check for owner-related questions and modify the user input
        if any(keyword in user_input.lower() for keyword in owner_keywords):
            owner_email = pet_data.get('email', 'No email found.')
            owner_phone = pet_data.get('phone', 'No phone number found.')
            user_input = f"{user_input} The owner's email is {owner_email} and phone number is {owner_phone}."

        # Prepare the prompt for the AI with additional context from past training data
        prompt = f"""
            YOU ARE A HELPFUL AND KNOWLEDGEABLE ASSISTANT. 

            Please carefully analyze the following user input: {user_input}.
            
            Use the provided pet data to craft an accurate and relevant response:
            {pet_data}.

            Here is additional context from previous conversations that may help provide a more informed answer:
            {training_context}

            IMPORTANT INSTRUCTIONS:
            1. **Accuracy is key**: Ensure the response is factual and based on the provided pet data.
            2. **Completeness**: If the pet data lacks the necessary information, make sure to mention what is missing in your response.
            3. **Web Search**: If critical information is missing, search the web for reliable sources to complete your response. Mention the source of the information if you refer to an external source.

            Respond as clearly and precisely as possible, taking into account the pet's details and any relevant past interactions.
            """

        try:
            # Generate AI response using the PromptProcessor
            response = prompt_processor.generate_message(prompt)
            return jsonify({"response": response})
        except Exception as e:
            Logger.log(f"Error generating AI response: {e}")
            return jsonify({"success": False, "message": "Error generating AI response."}), 500
