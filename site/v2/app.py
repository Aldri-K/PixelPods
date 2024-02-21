from flask import Flask, request, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv, set_key, dotenv_values
import os


from werkzeug.utils import secure_filename
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))+'\\static\\user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




app = Flask(__name__)

from flask_session import Session  # Import Session
app.secret_key = 'your_secret_key'  # Set a secret key for sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
Session(app)

load_dotenv()
# Assuming the .env file is in the same directory as this script
dotenv_path = '.env'


# The correct password for demonstration purposes
CORRECT_PASSWORD = 'Pods'

##########################################################################
def login_check():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
##########################################################################
@app.route('/remove-file', methods=['POST'])
def remove_file():
    filename = request.form.get('filename')
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            flash('File removed successfully.', 'success')
        else:
            flash('File does not exist.', 'error')
    return redirect(url_for('display_options'))

##########################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if the submitted password is correct
        if request.form['password'] == CORRECT_PASSWORD:
            print("Logging in")
            session['logged_in'] = True
            return redirect(url_for('menu'))
        else:
            print("wrong password")
            return redirect(url_for('login'))

    return render_template('login.html')

##########################################################################
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('logged_in', None)
    return redirect(url_for('login'))

##########################################################################
@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('menu.html')

##########################################################################
@app.route('/', methods=['GET', 'POST'])
def base_dir():
    return redirect(url_for('menu'))





##########################################################################
@app.route('/change-wifi', methods=['GET', 'POST'])
def change_wifi():
    # render_template('change-wifi.html')
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_info = {
            'wifi_ssid' : request.form['wifi_ssid'],
            'wifi_password' : request.form['wifi_password'],
        }
        
        # Update the information in the .env file
        for key, value in user_info.items():
            set_key(dotenv_path, key, value)
        
        return redirect(url_for('menu'))
    
    # Load the existing user data to pre-fill the form
    user_data = {
        'wifi_ssid' : os.getenv('wifi_ssid', ''),
        'wifi_password': os.getenv('wifi_password', ''),
    }
    
    return render_template('change-wifi.html', user_data=user_data)


##########################################################################
@app.route('/change-spot', methods=['GET', 'POST'])
def change_spot():

    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_info = {
            'spotify_username' : request.form['spotify_username'],
            'spotify_password' : request.form['spotify_password'],
            'spotify_client_secret' : request.form['spotify_client_secret'],
            'spotify_client_id' : request.form['spotify_client_id'],
            'spotify_redirect_uri' : request.form['spotify_redirect_uri']
        }
        
        # Update the information in the .env file
        for key, value in user_info.items():
            set_key(dotenv_path, key, value)
        
        return redirect(url_for('menu'))
    
    # Load the existing user data to pre-fill the form
    user_data = {
        'spotify_username': os.getenv('spotify_username', ''),
        'spotify_password': os.getenv('spotify_password', ''),
        'spotify_client_secret': os.getenv('spotify_client_secret', ''),
        'spotify_client_id': os.getenv('spotify_client_id', ''),
        'spotify_redirect_uri': os.getenv('spotify_redirect_uri', '')
    }
    
    return render_template('change-spot.html', user_data=user_data)
    

##########################################################################
# @app.route('/display-options', methods=['GET', 'POST'])
# def display_options():
#     if request.method == 'POST':
#         # Handle the file upload
#         file = request.files.get('fileUpload')
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
#         # Here you might want to save the selected display option to a session, database, etc.
#         # session['display_option'] = request.form['displayOption']

#     uploaded_files = os.listdir(UPLOAD_FOLDER)
#     uploaded_files = [file for file in uploaded_files if allowed_file(file)]
#     return render_template('display-options.html', uploaded_files=uploaded_files)

##########################################################################
@app.route('/display-options', methods=['GET'])
def display_options():
    # Load existing settings if any
    settings = dotenv_values(".env")  # Adjust path as needed
    uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    
    return render_template('display-options.html', settings=settings, uploaded_files=uploaded_files)

##########################################################################
@app.route('/update-display-options', methods=['POST'])
def update_display_options():
    # Find the .env file or specify its path
    
    # Extracting form data
    startDisplayOption = request.form.get('startDisplayOption')
    displayOption = request.form.get('displayOption')
    selectedFile = request.form.get('selectedFile')
    
    # Update .env file with the selected options
    if startDisplayOption:
        set_key(dotenv_path, 'START_DISPLAY_OPTION', startDisplayOption)
    if displayOption:
        set_key(dotenv_path, 'DISPLAY_OPTION', displayOption)
    if selectedFile:
        set_key(dotenv_path, 'SELECTED_FILE', selectedFile)
    
    flash('Display options updated successfully.', 'success')
    return redirect(url_for('display_options'))


##########################################################################

@app.route('/upload-file', methods=['POST'])
def upload_file():
    # Handle file upload
    file = request.files.get('fileUpload')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File uploaded successfully.', 'success')
    else:
        flash('Invalid file or no file selected.', 'error')
    return redirect(url_for('display_options'))

##########################################################################
@app.route('/toggle-base-image', methods=['POST'])
def toggle_base_image():

    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    display_base_image = 'displayBaseImage' in request.form
    # Here you would typically save this preference somewhere, such as in a session or a database
    print(f"Display base image: {display_base_image}")  # Placeholder action

    return redirect(url_for('menu'))


##########################################################################
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

















# @app.route('/', methods=['GET', 'POST'])
# def form():

#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))
    

#     if request.method == 'POST':
#         user_info = {
#             'wifi_ssid' : request.form['wifi_ssid'],
#             'wifi_password' : request.form['wifi_password'],
#             'spotify_username' : request.form['spotify_username'],
#             'spotify_password' : request.form['spotify_password'],
#             'spotify_client_secret' : request.form['spotify_client_secret'],
#             'spotify_client_id' : request.form['spotify_client_id'],
#             'spotify_redirect_uri' : request.form['spotify_redirect_uri']
#         }
        
#         # Save the information to the .env file
#         for key, value in user_info.items():
#             set_key(dotenv_path, key, value)
        
#         return redirect(url_for('update'))
    
#     return render_template('form.html')

# @app.route('/update', methods=['GET', 'POST'])
# def update():

#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         user_info = {
#             'wifi_ssid' : request.form['wifi_ssid'],
#             'wifi_password' : request.form['wifi_password'],
#             'spotify_username' : request.form['spotify_username'],
#             'spotify_password' : request.form['spotify_password'],
#             'spotify_client_secret' : request.form['spotify_client_secret'],
#             'spotify_client_id' : request.form['spotify_client_id'],
#             'spotify_redirect_uri' : request.form['spotify_redirect_uri']
#         }
        
#         # Update the information in the .env file
#         for key, value in user_info.items():
#             set_key(dotenv_path, key, value)
        
#         return 'Information Updated Successfully!'
    
#     # Load the existing user data to pre-fill the form
#     user_data = {
#         'wifi_ssid' : os.getenv('wifi_ssid', ''),
#         'wifi_password': os.getenv('wifi_password', ''),
#         'username': os.getenv('spotify_username', ''),
#         'spotify_username': os.getenv('spotify_password', ''),
#         'spotify_client_secret': os.getenv('spotify_client_secret', ''),
#         'spotify_client_id': os.getenv('spotify_client_id', ''),
#         'spotify_redirect_uri': os.getenv('spotify_redirect_uri', '')
#     }
    
#     return render_template('update_form.html', user_data=user_data)
