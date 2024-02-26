import os
import time
import subprocess
from dotenv import load_dotenv
import mimetypes
import vlc

load_dotenv()
START_DISPLAY_OPTION= os.getenv("START_DISPLAY_OPTION")
DISPLAY_OPTION=os.getenv("DISPLAY_OPTION")
SELECTED_FILE= os.getenv("SELECTED_FILE")

qrImage = "qr.png"
baseImageVideo = os.path.dirname(os.path.realpath(__file__))+"/static/user_uploads/"+ SELECTED_FILE

def check_file_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            play_video_in_vlc(file_path)
        else:
            return 'unknown'
    else:
        return 'unknown'




def play_video_in_vlc(video_path):
    subprocess.run(['/home/rdk/Downloads/PixelPods/site/v2/videoplay.sh'])



def main_app_mode():

    if DISPLAY_OPTION == "baseImageVideo":
        mime_type, _ = mimetypes.guess_type(baseImageVideo)
    
        if mime_type:
            if mime_type.startswith('image/'):
                subprocess.run(['sudo','fbi', '-T', '10', '-d', '/dev/fb0', '--noverbose', '--autozoom', baseImageVideo])
            elif mime_type.startswith('video/'):
                play_video_in_vlc(baseImageVideo)
            else:
                return 'unknown'
        else:
            return 'unknown'
        
        
    elif DISPLAY_OPTION == "spotify":
        subprocess.run(['sudo','python3','app.py'])
  

def start_up():
    if START_DISPLAY_OPTION == "connectionQR":
        # subprocess.run(['sudo','fbi', '-T', '10', '-d', '/dev/fb0', '--noverbose', '--autozoom', qrImage, '&', 'sleep', '5', ';', 'killall', 'fbi'])
        # Start the fbi process to display the image
        fbi_process = subprocess.Popen(['sudo','fbi', '-T', '10', '-d', '/dev/fb0', '--noverbose', '--autozoom', qrImage], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the specified display time
        time.sleep(5)

        # Kill the fbi process to stop displaying the image
        fbi_process.terminate()
        # Optionally, ensure the fbi process is killed if terminate doesn't work
        subprocess.run(['sudo','killall', 'fbi'])
        main_app_mode()
    elif START_DISPLAY_OPTION == "baseImageVideo":
        subprocess.run(['sudo','fbi', '-T', '10', '-d', '/dev/fb0', '--noverbose', '--autozoom', baseImageVideo])
        main_app_mode()
    elif START_DISPLAY_OPTION == "spotify":
        print("spot")
        main_app_mode()

start_up()