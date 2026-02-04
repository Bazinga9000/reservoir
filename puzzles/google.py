import gspread
from dotenv import load_dotenv
import os

load_dotenv()
TEMPLATE_ID = os.getenv("SHEETS_TEMPLATE_ID")
FOLDER_ID = os.getenv("SHEETS_FOLDER_ID")
TEAM_NAME = os.getenv("TEAM_NAME")

def get_client():
    return gspread.oauth(
        credentials_filename='secrets/google_oauth.json',
        authorized_user_filename='secrets/google_authorized_user.json'
    )


# Returns the ID of the new sheet
# The title will always be prefixed with the team name in case you're running multiple instances linked to the same gdrive (for say, multiple teams)
# for maximum disambiguation
def make_puzzle_sheet(puzzle_title):
    client = get_client()
    new = client.copy(TEMPLATE_ID, f"{TEAM_NAME} - {puzzle_title}", False, FOLDER_ID, False)
    new.share(None, "anyone", "writer", False, with_link=True)
    # TODO: share directly with anyone who adds a gmail account so they aren't anonymous on the sheet?
    return new.id

# Rename a given sheet to match the puzzle's name, if it has one
def rename_sheet(sheet_id, puzzle_title):
    if sheet_id != "":
        client = get_client()
        sheet = client.open_by_key(sheet_id)
        sheet.update_title(f"{TEAM_NAME} - {puzzle_title}")