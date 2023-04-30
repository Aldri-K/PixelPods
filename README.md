How to run the code:

Go to spotify developer https://developer.spotify.com
create an app
Give it whatever name and description
In the Redirect URI put "http://localhost:8000/callback"

Once you have that go to the app settings and get a copy of the Client ID and Client Secret
Put the client id and secret in the file called ".env" in the respective fields

Now you can run the code
Press run

When the code starts it will give you a url you need to open
open that url (you may be prompted to login to your spotify)
you will then be redirect to a new page and it will show something like "unable to connect"
in the address bar you will see a new url from the one you entered something like for example "http://localhost:8000/callback?code=ABCD"
from that you want to copy everything AFTER "http://localhost:8000/callback?code=" so in this example you will copy "ABCD"

now go back to the window that is running the code and paste this in where it asks for authorization code
if there are no errors the code will begin to retreive the current playing song every 5 seconds
it will also get the song art, this may be just album art or the spotify canvas where available, either way you will be given a link to the respective one
