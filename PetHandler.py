import json
import os
from config import JSON_FILE_PATH
from Logger import Logger
from FileHandler import FileHandler
from flask import request, render_template, jsonify

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

    def handle_pet_profile(self, control_number, template):
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
        data = request.form.to_dict()  # Handles text fields from FormData
        control_number = data.get('control_number')
        
        if not control_number or control_number not in self.pets:
            return {"success": False, "message": "Pet not found"}, 404
        
        pet = self.pets[control_number]

        # Update pet details
        pet.update({
            'petname': data.get('petname', pet.get('petname')),
            'petage': data.get('petage', pet.get('petage')),
            'petbreed': data.get('petbreed', pet.get('petbreed')),
            'email': data.get('email', pet.get('email')),
            'phone': data.get('phone', pet.get('phone')),
            'address': data.get('address', pet.get('address'))
        })

        # Validate control number
        if not self.is_valid_control_number(control_number):
            return render_template('pet-profile-edit.html', pet=pet, error="Invalid or duplicate control number")

        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename == '':
                return render_template('pet-profile-edit.html', pet=pet, error="No selected file")
            if file and FileHandler.allowed_file(file.filename):
                try:
                    pet['photo'] = FileHandler.save_and_convert_image(file, control_number)
                except Exception as e:
                    Logger.log(f"Error saving or converting image: {e}")
                    return render_template('pet-profile-edit.html', pet=pet, error="Failed to convert image.")
            else:
                return render_template('pet-profile-edit.html', pet=pet, error="Invalid file type")

        # Save the updated pet data
        self.pets[control_number] = pet
        self.save_pets()

        return {"success": True}

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

