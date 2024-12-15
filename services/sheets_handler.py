import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Authenticate and initialize Google Sheets API
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials file from environment
credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
if not credentials_file:
    raise FileNotFoundError("GOOGLE_SHEETS_CREDENTIALS environment variable is not set.")

# Authenticate with Google Sheets API
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
    client = gspread.authorize(credentials)
    logger.info("Successfully authenticated with Google Sheets API.")
except Exception as e:
    logger.error(f"Error authenticating Google Sheets API: {e}")
    raise

def save_to_sheet(call_id: int, question: str, response: str):
    """
    Save response data to a Google Sheet.

    Args:
        call_id (int): Unique call ID.
        question (str): The question asked during the call.
        response (str): The response provided by the patient.
    """
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "NHS Consultation Responses")
    
    try:
        # Open the Google Sheet
        sheet = client.open(sheet_name).sheet1

        # Append data to the Google Sheet
        sheet.append_row([call_id, question, response])
        logger.info(f"Appended row to Google Sheet: Call ID: {call_id}, Question: {question}, Response: {response}")
    except gspread.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{sheet_name}' not found. Check the name or permissions.")
        raise
    except Exception as e:
        logger.error(f"Failed to append data to Google Sheet: {e}")
        raise
