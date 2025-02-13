from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from PetHandler import PetHandler
from PromptHandler import PromptHandler
from BookingManager import BookingManager
from OpenMapper import OpenMapper

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'my_secret_key'
pet_handler = PetHandler()
prompt_handler = PromptHandler()
booking_manager = BookingManager()
mapper = OpenMapper()
stock_data = {'red': 1, 'blue': 0, 'green': 1, 'white': 1, 'grey': 0, 'orange': 2}
global control_number

@app.route('/')
def index():
    original_price = 14.49
    discounted_price = 8.69
    flash('🎉 Limited-Time Offer!  Get 40% OFF on all items   Order Now & Save Big! 🎉')
    return render_template('home-v2.html', original_price=original_price, discounted_price=discounted_price)

@app.route('/order-now/<color>')
def order_now(color):
    original_price = 14.49
    discounted_price = 8.69
    stock = stock_data.get(color)
    return render_template('order-form.html', color=color, stock=stock, original_price=original_price, discounted_price=discounted_price)

@app.route('/demo')
def demo():
    return render_template('demo.html'), 500

@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms-and-conditions.html'), 500

@app.route('/pet/<control_number>/edit', methods=['GET', 'POST'])
def pet_profile_edit(control_number):
    return pet_handler.pet_profile_edit(control_number)

@app.route('/pet/<control_number>/view', methods=['GET', 'POST'])
def pet_profile_view(control_number):
    return pet_handler.pet_profile_view(control_number)

@app.route('/pet/<control_number>/prompt', methods=['GET', 'POST'])
def pet_profile_prompt(control_number):
    return prompt_handler.handle_prompt(control_number)
   
@app.route('/search-tag-number', methods=['GET'])
def search_tag_number():
    control_number = request.args.get('control_number')
    if control_number:
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
