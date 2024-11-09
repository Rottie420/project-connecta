import json
import os
from config import JSON_FILE_PATH
from Logger import Logger
from FileHandler import FileHandler
from flask import request, render_template

class PetHandler:
    def __init__(self, json_file_path=JSON_FILE_PATH):
        self.json_file_path = json_file_path
        self.pets = self.load_pets()

    def load_pets(self):
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            Logger.log(f"Error loading pets data: {e}")
        return {}

    def save_pets(self):
        try:
            with open(self.json_file_path, 'w') as f:
                json.dump(self.pets, f, indent=4)
        except Exception as e:
            Logger.log(f"Error saving pets data: {e}")

    def is_valid_control_number(self, control_number):
        return control_number.isdigit() and control_number not in self.pets

    def pet_profile_edit(self, control_number):
        try:
            pet = self.pets.get(control_number) if control_number else None
            if not pet:
                return "Pet not found or invalid control number", 404

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
                    return render_template('pet-profile-edit.html', pet=pet, error="Invalid or duplicate control number")

                # Handle file upload
                if 'photo' not in request.files:
                    return render_template('pet-profile-edit.html', pet=pet, error="No file part")
                file = request.files['photo']
                if file.filename == '':
                    return render_template('pet-profile-edit.html', pet=pet, error="No selected file")
                if file and FileHandler.allowed_file(file.filename):
                    try:
                        pet_data['photo'] = FileHandler.save_and_convert_image(file, control_number)
                    except Exception as e:
                        return render_template('pet-profile-edit.html', pet=pet, error="Failed to convert image.")

                    # Save pet data
                    self.pets[control_number] = pet_data
                    self.save_pets()
            
            return render_template('pet-profile-edit.html', pet=pet)

        except Exception as e:
            Logger.log(f"edit pet profile error: {e}")
            return render_template('pet-profile-edit.html', error="An error occurred while processing your request.")

    def pet_profile_view(self, control_number):
        try:
            pet = self.pets.get(control_number) if control_number else None
            if not pet:
                return "Pet not found or invalid control number", 404

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
                    return render_template('pet-profile-view.html', pet=pet, error="Invalid or duplicate control number")

                # Handle file upload
                if 'photo' not in request.files:
                    return render_template('pet-profile-view.html', pet=pet, error="No file part")
                file = request.files['photo']
                if file.filename == '':
                    return render_template('pet-profile-view.html', pet=pet, error="No selected file")
                if file and FileHandler.allowed_file(file.filename):
                    try:
                        pet_data['photo'] = FileHandler.save_and_convert_image(file, control_number)
                    except Exception as e:
                        return render_template('pet-profile-view.html', pet=pet, error="Failed to convert image.")

                    # Save pet data
                    self.pets[control_number] = pet_data
                    self.save_pets()
            
            return render_template('pet-profile-view.html', pet=pet)

        except Exception as e:
            Logger.log(f"pet profile view error: {e}")
            return render_template('pet-profile-view.html', error="An error occurred while processing your request.")