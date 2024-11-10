from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import UPLOAD_FOLDER
from PetHandler import PetHandler
from Logger import Logger
from BookingManager import BookingManager

# Initialize Flask app and configuration
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize custom handlers
pet_handler = PetHandler()
booking_manager = BookingManager()

# Define routes with error handling
@app.route('/')
def index():
    try:
        return render_template('home.html')
    except Exception as e:
        Logger.log(f"Index page error: {e}")
        return "An error occurred loading the homepage.", 500

@app.route('/smart-nfc-tag')
def smart_nfc_tag():
    return render_page_with_logging('smart-nfc-tag.html', "Smart NFC Tag")

@app.route('/smart-nfc-card')
def smart_nfc_card():
    return render_page_with_logging('smart-nfc-card.html', "Smart NFC Card")

@app.route('/smart-nfc-sticker')
def smart_nfc_sticker():
    return render_page_with_logging('smart-nfc-sticker.html', "Smart NFC Sticker")

@app.route('/smart-nfc-wearables')
def smart_nfc_wearables():
    return render_page_with_logging('smart-nfc-wearables.html', "Smart NFC Wearables")

@app.route('/pet-profile-edit/<control_number>/<type>', methods=['GET', 'POST'])
def pet_profile_edit(control_number, type):
    if not control_number.isdigit():
        return jsonify({"success": False, "message": "Invalid control number"}), 400

    # Based on the type (profile, medicalHistory, etc.), call the respective handler method
    if type == 'profile':
        result = pet_handler.update_pet_profile(data, control_number)
    elif type == 'medicalHistory':
        result = pet_handler.update_medical_history(data, control_number)
    elif type == 'careReminders':
        result = pet_handler.update_care_reminders(data, control_number)
    elif type == 'activityLog':
        result = pet_handler.update_activity_log(data, control_number)
    else:
        return jsonify({"success": False, "message": "Unknown profile type"}), 400

    # If the update was successful, return a success message
    if result:
        return jsonify({"success": True, "message": f"{type} updated successfully!"})
    else:
        return jsonify({"success": False, "message": f"Failed to update {type}"}), 500



@app.route('/pet-profile-view/<control_number>', methods=['GET', 'POST'])
def pet_profile_view(control_number=None):
    return pet_handler.pet_profile_view(control_number)

@app.route('/consult-now', methods=['GET', 'POST'])
def consult_now():
    if request.method == 'POST':
        booking_info = get_booking_info()
        response, status_code = booking_manager.book_demo(booking_info)
        return jsonify(response), status_code
    return render_template('consult-now.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    logs = booking_manager.get_admin_dashboard_data()
    if isinstance(logs, tuple):  # Check if there's an error
        return jsonify(logs[0]), logs[1]
    return render_template('admin-dashboard.html', logs=logs)

# Helper functions
def render_page_with_logging(template, page_name):
    try:
        return render_template(template)
    except Exception as e:
        Logger.log(f"{page_name} page error: {e}")
        return f"An error occurred loading the {page_name} page.", 500

def get_booking_info():
    return {
        'name': request.json.get('name') if request.is_json else request.form.get('name'),
        'email': request.json.get('email') if request.is_json else request.form.get('email'),
        'phone': request.json.get('phone') if request.is_json else request.form.get('phone'),
        'date': request.json.get('date') if request.is_json else request.form.get('date'),
        'time': request.json.get('time') if request.is_json else request.form.get('time'),
        'message': request.json.get('message') if request.is_json else request.form.get('message')
    }

# Run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
