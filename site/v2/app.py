from flask import Flask, request, render_template, redirect, url_for
import os

script_path= os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def check_user_data_exists():
    """Check if user data already exists."""
    return os.path.exists(f"{script_path}\\user_information.txt") and os.path.getsize(f"{script_path}\\user_information.txt") > 0

@app.route('/', methods=['GET', 'POST'])
def form():
    # Check if data already exists
    if check_user_data_exists():
        # Redirect to update page if data exists
        return redirect(url_for('update'))
    
    if request.method == 'POST':
        # Extract information from form data
        wifi_ssid = request.form['wifi_ssid']
        wifi_password = request.form['wifi_password']
        spotify_username = request.form['spotify_username']
        spotify_password = request.form['spotify_password']
        
        # Store the information in a text file
        with open(f"{script_path}\\user_information.txt", "w") as file:
            file.write(f"{wifi_ssid},{wifi_password},{spotify_username},{spotify_password}\n")
        
        return 'Information Submitted Successfully!'
    
    return render_template('form.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    # Assume the first line contains the existing user data
    with open(f"{script_path}\\user_information.txt", "r") as file:
        user_data = file.readline().strip().split(',')
    
    if request.method == 'POST':
        # Update the information in the text file
        with open(f"{script_path}\\user_information.txt", "w") as file:
            file.write(f"{request.form['wifi_ssid']},{request.form['wifi_password']},{request.form['spotify_username']},{request.form['spotify_password']}\n")
        
        return 'Information Updated Successfully! '
    
    # Pre-fill the form with the existing user data
    return render_template('update_form.html', user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True)
