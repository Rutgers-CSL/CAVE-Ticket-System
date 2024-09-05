#https://callmefred.com/how-to-connect-python-to-google-sheets/

import platform
import gspread
from datetime import datetime
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
    a_column_values = sh.col_values(1) 
    b_column_values = sh.col_values(3)
    c_column_values = sh.col_values(4)

    # Get current date and time
    current_datetime = datetime.now()

    os_type = platform.system()
    if os_type == 'nt':
        formatted_datetime = current_datetime.strftime("%#m/%#d/%Y")
    else:
        formatted_datetime = current_datetime.strftime('%-m/%-d/%Y')

    # Find the minimum length of both columns
    min_length = min(len(a_column_values), len(c_column_values))
    min_length = min(min_length, len(b_column_values))

    # Filter tickets based on conditions
    tickets_to_display = []
    for i in range(1, min_length):
        a_value = a_column_values[i]
        b_value = b_column_values[i]
        c_value = c_column_values[i]

        if a_value == 'FALSE' and (b_value[:-9] == formatted_datetime or b_value[:-8] == formatted_datetime):
            tickets_to_display.append({"c_value": c_value})


    # Render the template with the filtered tickets
    return render_template('display_tickets.html', tickets=tickets_to_display)

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True)
