import json
import os
import subprocess
from datetime import datetime
from config import JSON_FILE_PATH
from Logger import Logger
from FileHandler import FileHandler
from flask import request, render_template, jsonify

class PetHandler:
    def __init__(self, json_file_path=JSON_FILE_PATH):
        self.json_file_path = json_file_path
        self.pets = self.load_pets()
        self.repo_path = r'C:\Users\Administrator\Desktop\project-connecta'  # Your repository path

    def commit_changes_to_git(self):
        try:
            # Ensure you're in the Git repository directory
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                Logger.log(f"Error: {self.repo_path} is not a valid Git repository.")
                return
            
            os.chdir(self.repo_path)  # Change working directory to repo

            # Check if there are changes to commit (i.e., untracked or modified files)
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True
            )

            # Debugging the status output to check the repository state
            Logger.log(f"Git status output: {status.stdout}")

            if status.returncode != 0:
                Logger.log(f"Error checking Git status: {status.stderr}")
                return

            # If there are no changes, exit early
            if not status.stdout.strip():
                Logger.log("No changes to commit.")
                return
            
            # Stage the changes (add all changes)
            add_result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True, text=True, check=True
            )
            Logger.log(f"Git add output: {add_result.stdout}")
            
            # Create a commit message with a timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f'Update pet profile data at {timestamp}'

            # Commit the changes with the timestamped message
            commit = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True, text=True, check=True
            )

            Logger.log(f"Git commit output: {commit.stdout}")
            
            # Optionally, push the changes to a remote repository
            push = subprocess.run(
                ['git', 'push'],
                capture_output=True, text=True, check=True
            )

            Logger.log(f"Git push output: {push.stdout}")

            Logger.log(f"Changes committed successfully with message: {commit_message}")
        
        except subprocess.CalledProcessError as e:
            Logger.log(f"Error during Git operation: {e}")
            Logger.log(f"Standard error output: {e.stderr}")
            Logger.log(f"Standard output: {e.stdout}")
        except Exception as e:
            Logger.log(f"Unexpected error: {e}")
    
    def load_pets(self):
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            Logger.log(f"Error loading pets data: {e}")
        return {}

    def save_pets(self):
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.pets, f, indent=4)
        except Exception as e:
            Logger.log(f"Error saving pets data: {e}")

    def is_valid_control_number(self, control_number):
        return control_number.isalnum() and control_number not in self.pets

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
            self.commit_changes_to_git()
        
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
                self.commit_changes_to_git()
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
        self.commit_changes_to_git()

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
        self.commit_changes_to_git()

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
        self.commit_changes_to_git()

        return jsonify({"success": True})

