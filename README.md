# ℝeservoir

A puzzlehunt management webapp used by ℙoNDeterministic.

## Setup

### Python Environment
1. Install `uv`
2. Run `uv sync` to set up the Python environment.

### Google Integration (For per-puzzle) Google Sheets)

1. Go to your (team's) Google account, and create a [Google Cloud Project](https://console.cloud.google.com/projectcreate)
2. Click "Enable APIs and Services" and enable the Google Sheets API and the Google Drive API
3. Under "Google Auth Platform" > "Clients", create a client. Set its type to "Desktop App". Download the credentials json and save it under `secrets/google_oauth.json`
4. Under "Google Auth Platform" > "Audience", add your (team's) Google email as a test user. 

5. Make a spreadsheet and format it however you'd like. This will be the sheet from which all puzzle sheets will be duplicated. Make sure the account used in step 4 has access to this sheet. Get its ID from the URL (`https://docs.google.com/spreadsheets/d/<ID_IS_HERE>/edit`)
 
2. In your (team's) Google Drive, create a new folder. This will be where your puzzle sheets get stored. Get its ID from the URL as you did in step 5

6. Create a `.env` file in this repo's directory with the following variables:
```
TEAM_NAME = <Your team name>
SHEETS_TEMPLATE_ID = <The ID of your template sheet from step 3.>
SHEETS_FOLDER_ID = <The ID of the Google Drive folder from step 4.>
```

7. Run `uv run authenticate_google.py` to authenticate the app with your (team's) Google account and generate (more) persistent credentials. This is done so that the end users don't have to authenticate randomly.

### Discord Integration (For authentication)

This site relies on Discord as an authentication provider. You will need to set up (or obtain credentials for) [a Discord application](https://discord.com/developers/docs/topics/oauth2).

1. Obtain the following two values for your Discord application:
   - the Client ID
   - the Client Secret. Note that clicking Reset Secret to view the secret will nullify any in-use secrets.
2. Determine the Redirect URL. 
   - This is usually where you will be hosting your server, with `/auth` appended. For debugging purposes this can be something like `http://localhost:8080/auth`.
3. Configure this URL as a valid Redirect URI for Discord OAuth.
4. Add the following entires to the `.env` file:
```
DISCORD_CLIENT_ID = <client ID>
DISCORD_CLIENT_SECRET = <client Secret>
DISCORD_REDIRECT_URI = <redirect URI you entered into Discord>
```

## Running

### Nix/NixOS
```
nix run .#reservoir
```
(Currently, this only runs the Redis instance. Eventually, it will run everything else too.)