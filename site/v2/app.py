from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv, set_key
import os

app = Flask(__name__)

load_dotenv()
# Assuming the .env file is in the same directory as this script
dotenv_path = '.env'

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_info = {
            'wifi_ssid' : request.form['wifi_ssid'],
            'wifi_password' : request.form['wifi_password'],
            'spotify_username' : request.form['spotify_username'],
            'spotify_password' : request.form['spotify_password'],
            'spotify_client_secret' : request.form['spotify_client_secret'],
            'spotify_client_id' : request.form['spotify_client_id'],
            'spotify_redirect_uri' : request.form['spotify_redirect_uri']
        }
        
        # Save the information to the .env file
        for key, value in user_info.items():
            set_key(dotenv_path, key, value)
        
        return redirect(url_for('update'))
    
    return render_template('form.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        user_info = {
            'wifi_ssid' : request.form['wifi_ssid'],
            'wifi_password' : request.form['wifi_password'],
            'spotify_username' : request.form['spotify_username'],
            'spotify_password' : request.form['spotify_password'],
            'spotify_client_secret' : request.form['spotify_client_secret'],
            'spotify_client_id' : request.form['spotify_client_id'],
            'spotify_redirect_uri' : request.form['spotify_redirect_uri']
        }
        
        # Update the information in the .env file
        for key, value in user_info.items():
            set_key(dotenv_path, key, value)
        
        return 'Information Updated Successfully!'
    
    # Load the existing user data to pre-fill the form
    user_data = {
        'wifi_ssid' : os.getenv('wifi_ssid', ''),
        'wifi_password': os.getenv('wifi_password', ''),
        'username': os.getenv('spotify_username', ''),
        'spotify_username': os.getenv('spotify_password', ''),
        'spotify_client_secret': os.getenv('spotify_client_secret', ''),
        'spotify_client_id': os.getenv('spotify_client_id', ''),
        'spotify_redirect_uri': os.getenv('spotify_redirect_uri', '')
    }
    
    return render_template('update_form.html', user_data=user_data)


@app.route('/menu')
def menu():
    return render_template('menu.html')

# Placeholder routes for each action
@app.route('/change-wifi')
def change_wifi():
    return 'Change WiFi Page Placeholder'

@app.route('/change-spot')
def change_spot():
    return 'Change Spot Page Placeholder'

@app.route('/display-options')
def display_options():
    return 'Display Options Page Placeholder'

@app.route('/toggle-base-image', methods=['POST'])
def toggle_base_image():
    display_base_image = 'displayBaseImage' in request.form
    # Here you would typically save this preference somewhere, such as in a session or a database
    print(f"Display base image: {display_base_image}")  # Placeholder action

    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)
