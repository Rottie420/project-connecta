import json
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

# Path to the JSON file
JSON_FILE_PATH = 'pets.json'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
LOG_FILE_PATH = 'log.txt'  # Path to the log file

# Create upload folder if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to log errors to log.txt
def log_error(error_message):
    with open(LOG_FILE_PATH, 'a') as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - ERROR: {error_message}\n")

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
        log_error(f"Index page error: {e}")
        return "An error occurred loading the homepage.", 500

@app.route('/smart-nfc-tag')
def smart_nfc_tag():
    try:
        return render_template('smart-nfc-tag.html')
    except Exception as e:
        log_error(f"Smart NFC Tag page error: {e}")
        return "An error occurred loading the Smart NFC Tag page.", 500

@app.route('/smart-nfc-card')
def smart_nfc_card():
    try:
        return render_template('smart-nfc-card.html')
    except Exception as e:
        log_error(f"Smart NFC Card page error: {e}")
        return "An error occurred loading the Smart NFC Card page.", 500

@app.route('/smart-nfc-sticker')
def smart_nfc_sticker():
    try:
        return render_template('smart-nfc-sticker.html')
    except Exception as e:
        log_error(f"Smart NFC Sticker page error: {e}")
        return "An error occurred loading the Smart NFC Sticker page.", 500

@app.route('/pet/<control_number>')
def pet_profile(control_number):
    try:
        pet = pets.get(control_number)
        if pet:
            timestamp = datetime.now().timestamp()
            return render_template('pet-profile.html', pet=pet, timestamp=timestamp)
        else:
            return "Pet not found", 404
    except Exception as e:
        log_error(f"Pet profile error for control number {control_number}: {e}")
        return "An error occurred while loading the pet profile.", 500

@app.route('/add-pet', methods=['GET', 'POST'])
def add_pet():
    try:
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

                # Convert image to WEBP format
                webp_filename = f"{control_number}.webp"
                webp_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)

                try:
                    img = Image.open(original_path)
                    img.save(webp_path, 'webp')
                except Exception as e:
                    log_error(f"Image conversion error for {filename}: {e}")
                    return render_template('add-pet.html', error="Failed to convert image.")
                finally:
                    os.remove(original_path)  # Ensure original image is deleted

                # Save pet data
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

    except Exception as e:
        log_error(f"Add pet error: {e}")
        return render_template('add-pet.html', error="An error occurred while processing your request.")

@app.route('/nfc-pet-tag')
def nfc_pet_tag_page():
    return render_template('nfc-pet-tag.html')

# Define the path to the JSON data file
DATA_FILE = os.path.join('data', 'demo_bookings.json')

# Function to read JSON data from the file
def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

# Function to write JSON data to the file
def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/api/book-a-demo', methods=['GET', 'POST'])
def book_demo():
    if request.method == 'POST':
        # Capture form data
        booking_info = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'date': request.form.get('date'),
            'time': request.form.get('time'),
            'message': request.form.get('message')
        }
        
        # Validate that required fields are filled
        if not booking_info['name'] or not booking_info['email']:
            return jsonify({'error': 'Name and email are required.'}), 400  # Handle missing fields
        
        bookings = read_data()
        bookings.append(booking_info)
        write_data(bookings)
        
        # Return a JSON response indicating success
        return jsonify({'message': 'Demo booked successfully!', 'booking_info': booking_info}), 200

    # Handle GET requests (if needed)
    return render_template('book-a-demo.html')  # Just return the form if it's a GET request



if __name__ == '__main__':
    # Create the data directory and file if they do not exist
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DATA_FILE):
        write_data([])  # Create an empty JSON file
    app.run(host='0.0.0.0', port=5000)
