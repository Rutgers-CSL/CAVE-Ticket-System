import platform
import logging
import socket
import time
from typing import List, Dict
from datetime import datetime

import gspread
from google.auth.exceptions import TransportError
from gspread.exceptions import APIError
from flask import Flask, render_template, session

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key
app.static_folder = 'static'

# Constants
CREDENTIALS_FILE = "cred.json"
SPREADSHEET_NAME = "(F24/S25) iLab Dashboard"
MAX_RETRIES = 3
RETRY_DELAY = 5

def check_internet_connection() -> bool:
    """Check if there's an active internet connection."""
    try:
        # Attempt to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def get_formatted_date() -> str:
    """Get the current date formatted based on the OS."""
    current_date = datetime.now().date()
    if platform.system() == "Windows":
        return current_date.strftime("%#m/%#d/%Y")
    return current_date.strftime('%-m/%-d/%Y')

def connect_to_sheets() -> gspread.Spreadsheet:
    """Connect to Google Sheets and return the first sheet."""
    logger.info(f"Attempting to connect to Google Sheets: {SPREADSHEET_NAME}")
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Connection attempt {attempt + 1}")
            gc = gspread.service_account(filename=CREDENTIALS_FILE)
            sheet = gc.open(SPREADSHEET_NAME).sheet1
            logger.info("Successfully connected to Google Sheets")
            return sheet
        except (FileNotFoundError, TransportError, APIError) as e:
            logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("All connection attempts failed")
                raise

def get_column_values(sheet: gspread.Spreadsheet, col: int) -> List[str]:
    """Get values from a specific column with error handling."""
    logger.info(f"Fetching values from column {col}")
    for attempt in range(MAX_RETRIES):
        try:
            values = sheet.col_values(col)
            logger.info(f"Successfully fetched {len(values)} values from column {col}")
            logger.debug(f"First few values from column {col}: {values[:5]}")
            return values
        except APIError as e:
            logger.error(f"Attempt {attempt + 1} to fetch column {col} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"All attempts to fetch column {col} failed")
                raise

@app.route('/')
def display_tickets():
    logger.info("Received request to display tickets")
    
    if not check_internet_connection():
        logger.error("No internet connection detected")
        no_internet_message = {"c_value": "Please connect your device to the internet."}
        session['current_tickets'] = [no_internet_message]
        return render_template('display_tickets.html', tickets=session['current_tickets'])
    
    try:
        sheet = connect_to_sheets()
        logger.info("Fetching column values")
        checkmark_column = get_column_values(sheet, 1)
        timestamp_column = get_column_values(sheet, 3)
        name_column = get_column_values(sheet, 4)

        formatted_datetime = get_formatted_date()
        logger.info(f"Current formatted date: {formatted_datetime}")

        # Find the minimum length of all columns
        min_length = min(len(checkmark_column), len(timestamp_column), len(name_column))
        logger.info(f"Minimum length of columns: {min_length}")

        # Filter tickets based on conditions
        tickets_to_display = []
        for i in range(1, min_length):
            checkmark_val = checkmark_column[i]
            timestamp_val = timestamp_column[i]
            name_val = name_column[i]

            logger.debug(f"Processing row {i}: Checkmark: {checkmark_val}, Timestamp: {timestamp_val}, Name: {name_val}")

            if checkmark_val == 'FALSE' and (timestamp_val[:-9] == formatted_datetime or timestamp_val[:-8] == formatted_datetime):
                tickets_to_display.append({"c_value": name_val})
                logger.debug(f"Ticket added: {name_val}")

        logger.info(f"Total tickets to display: {len(tickets_to_display)}")
        logger.debug(f"Tickets to display: {tickets_to_display}")

        # Update session with new tickets
        session['current_tickets'] = tickets_to_display
        session['last_successful_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        logger.error(f"An error occurred while processing the request: {str(e)}")
        # Use the last known state of tickets if available
        tickets_to_display = session.get('current_tickets', [])
        logger.info(f"Using last known state with {len(tickets_to_display)} tickets")

    # Render the template with the filtered tickets (either new or last known state)
    return render_template('display_tickets.html', tickets=tickets_to_display)

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host="localhost", debug=True)