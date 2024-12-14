from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from PetHandler import PetHandler
from Logger import Logger
from BookingManager import BookingManager
import json

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

@app.route('/order-now/<color>')
def order_now(color):
    stock_data = {
                    'red': 0,
                    'blue': 0,
                    'green': 1,
                    'white': 1,
                    'grey': 0,
                    'blue': 0,
                    'orange': 2,
                }

    stock = stock_data.get(color)
    return render_template('order-form.html', color=color, stock=stock)

@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms-and-conditions.html'), 500

@app.route('/pet/<control_number>/edit', methods=['GET', 'POST'])
def pet_profile_edit(control_number):
    return pet_handler.pet_profile_edit(control_number)

@app.route('/pet/<control_number>/view', methods=['GET'])
def pet_profile_view(control_number):
    return pet_handler.pet_profile_view(control_number)

@app.route('/pet/<control_number>/prompt', methods=['GET', 'POST'])
def pet_profile_prompt(control_number):
    """
    Handles POST requests for generating AI responses and GET requests for displaying pet profiles.
    """
    print(f"Received control number: {control_number}")  # Debug print

    if request.method == 'POST':
        try:
            # Parse JSON data from the request
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "No data received in POST body."}), 400

            # Extract the user input, expecting 'prompt' from the front-end
            user_input = data.get('prompt')

            if not isinstance(user_input, str) or not user_input.strip():
                return jsonify({"success": False, "message": "Invalid or empty prompt."}), 400

            # Process the prompt using the pet handler
            response = pet_handler.prompt_message(control_number, user_input)

            # Check if response is a valid Flask Response object and read its JSON data
            if isinstance(response, Response):
                response_data = response.get_data(as_text=True)

                try:
                    response_json = json.loads(response_data)  # Parse response data to JSON

                    # Ensure AI response is logged in the new format
                    ai_response = response_json.get("response")
                    if ai_response:  # Log only if there is a valid AI response
                        Logger.log_for_ai_training(control_number, user_input, ai_response)

                    return jsonify(response_json)
                except json.JSONDecodeError:
                    return jsonify({"success": False, "message": "Error decoding JSON response from pet_handler."}), 500
            else:
                return jsonify({"success": False, "message": "Unexpected response format from pet_handler."}), 500

        except Exception as e:
            Logger.log(f"Error processing prompt for pet {control_number}: {e}")
            return jsonify({"success": False, "message": "An error occurred while processing your request."}), 500

    # Handle GET request (for displaying the pet profile page)
    pet_data = pet_handler.pets.get(control_number)
    print(f"Fetched pet data: {pet_data}")  # Debug print
    if not pet_data:
        return jsonify({"success": False, "message": "Pet not found"}), 404

    return render_template('pet-profile-prompt.html', pet=pet_data, control_number=control_number)

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
def render_page_with_logging(template, page_name, color):
    try:
        return render_template(template, color=color)
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
