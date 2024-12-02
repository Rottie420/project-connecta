from flask import Flask, render_template, request, redirect, url_for, jsonify
from PetHandler import PetHandler
from Logger import Logger
from BookingManager import BookingManager

# Initialize Flask app and configuration
app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize custom handlers
pet_handler = PetHandler()
booking_manager = BookingManager()

# Define routes with error handling
@app.route('/')
def index():
    try:
        return render_template('home-v2.html')
    except Exception as e:
        Logger.log(f"Index page error: {e}")
        return "An error occurred loading the homepage.", 500

@app.route('/order-now')
def order_now():
    return render_page_with_logging('order-form.html', "Order Form")

@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_page_with_logging('terms-and-conditions.html', "Terms & Conditions")

@app.route('/pet/<control_number>/edit', methods=['GET', 'POST'])
def pet_profile_edit(control_number):
    return pet_handler.pet_profile_edit(control_number)

@app.route('/pet/<control_number>/view', methods=['GET'])
def pet_profile_view(control_number):
    return pet_handler.pet_profile_view(control_number)

@app.route('/search-tag-number', methods=['GET'])
def search_tag_number():
    control_number = request.args.get('control_number')
    if control_number:
        # Redirect to the pet profile edit route with the control number
        return redirect(url_for('pet_profile_edit', control_number=control_number))
    return "Tag number invalid!", 400

@app.route('/api/pet/update', methods=['POST'])
def update_pet_profile():
    return pet_handler.update_pet_profile()

@app.route('/api/pet/update/medical', methods=['POST'])
def update_medical_history():
    data = request.json
    return pet_handler.update_medical_history(data)

@app.route('/api/pet/update/care', methods=['POST'])
def update_care_reminders():
    data = request.json
    return pet_handler.update_care_reminders(data)

@app.route('/api/pet/update/activity', methods=['POST'])
def update_activity_log():
    data = request.json
    return pet_handler.update_activity_log(data)

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
