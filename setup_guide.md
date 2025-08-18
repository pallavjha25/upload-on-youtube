Mac Virtual Environment Setup Guide
Step 1: Navigate to Your Project Directory
Open Terminal and navigate to where you saved the Python program:
bashcd /path/to/your/project
# For example: cd ~/Desktop/youtube-uploader
Step 2: Create a Virtual Environment
Create a virtual environment named venv:
bashpython3 -m venv venv
If you get an error, try using python instead of python3:
bashpython -m venv venv
Step 3: Activate the Virtual Environment
Activate the virtual environment:
bashsource venv/bin/activate
You'll know it's activated when you see (venv) at the beginning of your terminal prompt.
Step 4: Upgrade pip (Optional but Recommended)
bashpip install --upgrade pip
Step 5: Install Required Dependencies
Install the YouTube API dependencies:
bashpip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
Step 6: Verify Installation
Check if packages are installed correctly:
bashpip list
You should see the Google API packages listed.
Step 7: Set Up YouTube API Credentials

Go to Google Cloud Console
Create a new project or select an existing one
Enable the YouTube Data API v3:

Go to "APIs & Services" > "Library"
Search for "YouTube Data API v3"
Click on it and press "Enable"


Create OAuth 2.0 credentials:

Go to "APIs & Services" > "Credentials"
Click "Create Credentials" > "OAuth 2.0 Client IDs"
Choose "Desktop Application"
Download the JSON file


Rename the downloaded file to credentials.json
Place credentials.json in the same directory as your Python program

Step 8: Run the Program
Make sure your virtual environment is still activated (you should see (venv) in your prompt), then run:
bashpython video_uploader.py
Step 9: Deactivate Virtual Environment (When Done)
When you're finished working with the program, deactivate the virtual environment:
bashdeactivate
Future Usage
Every time you want to run the program:

Navigate to your project directory
Activate the virtual environment: source venv/bin/activate
Run the program: python video_uploader.py
Deactivate when done: deactivate