import json
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

# Path to the JSON file
JSON_FILE_PATH = 'pets.json'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to load pets from JSON file
def load_pets():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    return {}

# Function to save pets to JSON file
def save_pets(pets):
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(pets, f, indent=4)

# Load pets into the dictionary
pets = load_pets()

# Function to validate control number
def is_valid_control_number(control_number):
    return control_number.isdigit() and control_number not in pets

@app.route('/')
def index():
    try:
        return render_template('home.html')
    except Exception as e:
        print(e)
        return render_template('home.html')

@app.route('/pet/<control_number>')
def pet_profile(control_number):
    pet = pets.get(control_number)
    if pet:
        timestamp = datetime.now().timestamp()
        return render_template('pet-profile.html', pet=pet, timestamp=timestamp)
    else:
        return "Pet not found", 404

@app.route('/add-pet', methods=['GET', 'POST'])
def add_pet():
    if request.method == 'POST':
        control_number = request.form['control_number']
        petname = request.form['petname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        social = {
            'facebook': request.form['facebook'],
            'twitter': request.form['twitter'],
            'instagram': request.form['instagram']
        }

        if not is_valid_control_number(control_number):
            return render_template('add-pet.html', error="Invalid or duplicate control number")

        if 'photo' not in request.files:
            return render_template('add-pet.html', error="No file part")
        
        file = request.files['photo']
        
        if file.filename == '':
            return render_template('add-pet.html', error="No selected file")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{control_number}_{filename}"

            original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(original_path)

            webp_filename = f"{control_number}.webp"
            webp_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)

            img = Image.open(original_path)
            img.save(webp_path, 'webp')
            os.remove(original_path)

            pets[control_number] = {
                'control_number': control_number,
                'name': petname,
                'email': email,
                'phone': phone,
                'address': address,
                'social': social,
                'photo': f'uploads/{webp_filename}'
            }

            save_pets(pets)
            return redirect(url_for('pet_profile', control_number=control_number))
    
    return render_template('add-pet.html')

@app.route('/nfc-pet-tag')
def nfc_pet_tag_page():
    return render_template('nfc-pet-tag.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)