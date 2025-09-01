# YouTube Uploader Setup Guide for Mac

This guide will walk you through setting up the YouTube Uploader Python application on macOS, including virtual environment setup and YouTube API credentials configuration.

## Prerequisites

- macOS (tested on macOS 24.3.0)
- Python 3.x installed
- Terminal application
- Google account for YouTube API access

## Step-by-Step Setup

### Step 1: Navigate to Your Project Directory

Open Terminal and navigate to where you saved the Python program:

```bash
cd /path/to/your/project
# For example: cd ~/Desktop/youtube-uploader
```

### Step 2: Create a Virtual Environment

Create a virtual environment named `venv`:

```bash
python3 -m venv venv
```

**Note:** If you get an error, try using `python` instead of `python3`:

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

Activate the virtual environment:

```bash
source venv/bin/activate
```

**Success indicator:** You'll see `(venv)` at the beginning of your terminal prompt.

### Step 4: Upgrade pip (Optional but Recommended)

```bash
pip install --upgrade pip
```

### Step 5: Install Required Dependencies

Install the YouTube API dependencies:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 6: Verify Installation

Check if packages are installed correctly:

```bash
pip list
```

**Expected result:** You should see the Google API packages listed in the output.

### Step 7: Set Up YouTube API Credentials

#### 7.1 Go to Google Cloud Console
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Sign in with your Google account

#### 7.2 Create or Select a Project
- Create a new project or select an existing one
- Make note of your project ID

#### 7.3 Enable the YouTube Data API v3
1. Navigate to **"APIs & Services"** > **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it and press **"Enable"**

#### 7.4 Create OAuth 2.0 Credentials
1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** > **"OAuth 2.0 Client IDs"**
3. Choose **"Desktop Application"**
4. Download the JSON file

#### 7.5 Configure Credentials File
1. Rename the downloaded file to `credentials.json`
2. Place `credentials.json` in the same directory as your Python program

## Running the Application

### Step 8: Run the Program

Make sure your virtual environment is still activated (you should see `(venv)` in your prompt), then run:

```bash
python video_uploader.py
```

### Step 9: Deactivate Virtual Environment (When Done)

When you're finished working with the program, deactivate the virtual environment:

```bash
deactivate
```

## Future Usage

Every time you want to run the program:

1. **Navigate** to your project directory
2. **Activate** the virtual environment: `source venv/bin/activate`
3. **Run** the program: `python video_uploader.py`
4. **Deactivate** when done: `deactivate`

source venv/bin/activate
python video_uploader.py

## Troubleshooting

### Common Issues

- **Python not found:** Ensure Python is installed and in your PATH
- **Permission denied:** Use `sudo` if necessary for system-wide installations
- **API errors:** Verify your credentials.json file is in the correct location
- **Virtual environment issues:** Delete the `venv` folder and recreate it

### Getting Help

If you encounter issues:
1. Check that all dependencies are properly installed
2. Verify your YouTube API credentials are correct
3. Ensure your virtual environment is activated
4. Check the console output for specific error messages

## File Structure

After setup, your project directory should look like this:

```
youtube-uploader/
├── venv/                    # Virtual environment folder
├── credentials.json         # YouTube API credentials
├── video_uploader.py       # Main application file
├── requirements.txt         # Python dependencies
└── setup_guide.md          # This file
```

---

**Note:** Keep your `credentials.json` file secure and never commit it to version control.