# ℝeservoir

A puzzlehunt management webapp used by ℙoNDeterministic.

## Setup

1. Install `uv`

2. Set up Google Cloud for Sheets Integration:
   1. Go to your (team's) Google account, and create a [Google Cloud Project](https://console.cloud.google.com/projectcreate)
   2. Click "Enable APIs and Services" and enable the Google Sheets API and the Google Drive API
   3. Under "Google Auth Platform" > "Clients", create a client. Set its type to "Desktop App". Download the credentials json and save it under `secrets/google_oauth.json`
   4. Under "Google Auth Platform" > "Audience", add your (team's) Google email as a test user. 

3. Make a spreadsheet and format it however you'd like. This will be the sheet from which all puzzle sheets will be duplicated. Make sure the account used in step 2.4 has access to this sheet. Get its ID from the URL (`https://docs.google.com/spreadsheets/d/<ID_IS_HERE>/edit`)
 
4. In your (team's) Google Drive, create a new folder. This will be where your puzzle sheets get stored. Get its ID from the URL as you did in step 3.

5. Create a `.env` file in this repo's directory with the following variables:
```
TEAM_NAME = <Your team name>
SHEETS_TEMPLATE_ID = <The ID of your template sheet from step 3.>
SHEETS_FOLDER_ID = <The ID of the Google Drive folder from step 4.>
```

6. Run `uv sync` to set up the Python environment.
7. Run `uv run authenticate_google.py` to authenticate the app with your (team's) Google account and generate (more) persistent credentials. This is done so that the end users don't have to authenticate randomly.