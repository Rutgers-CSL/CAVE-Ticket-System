#https://callmefred.com/how-to-connect-python-to-google-sheets/

import platform
import gspread
from datetime import datetime, time
from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')

def display_tickets():
    # Connect to the Google Sheets service account
    gc = gspread.service_account(filename="cred.json")

    # Open the Google Sheets document and select the sheet
    sh = gc.open("(F24/S25) iLab Dashboard").sheet1

    # Get column values
    try :
        checkmark_column = sh.col_values(1) 
        timestamp_column = sh.col_values(3)
        name_column = sh.col_values(4)
    except:
        # Retry in a couple of seconds
        print("Error retrieving data. Retrying in 5 seconds...")
        time.sleep(5)
        checkmark_column = sh.col_values(1)
        timestamp_column = sh.col_values(3)
        name_column = sh.col_values(4)

    # Get current date and time
    current_datetime = datetime.now()

    os_type = platform.system()
    if os_type == "Windows":
        formatted_datetime = current_datetime.strftime("%#m/%#d/%Y")
    else:
        formatted_datetime = current_datetime.strftime('%-m/%-d/%Y')

    # Find the minimum length of both columns
    min_length = min(len(checkmark_column), len(name_column))
    min_length = min(min_length, len(timestamp_column))

    # Filter tickets based on conditions
    tickets_to_display = []
    for i in range(1, min_length):
        checkmark_val = checkmark_column[i]
        timestamp_val = timestamp_column[i]
        name_val = name_column[i]

        if checkmark_val == 'FALSE' and (timestamp_val[:-9] == formatted_datetime or timestamp_val[:-8] == formatted_datetime):
            tickets_to_display.append({"c_value": name_val})


    # Render the template with the filtered tickets
    return render_template('display_tickets.html', tickets=tickets_to_display)

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True)
