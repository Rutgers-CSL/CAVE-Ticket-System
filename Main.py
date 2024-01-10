import gspread
from datetime import datetime

# Connect to the service account
# https://callmefred.com/how-to-connect-python-to-google-sheets/
gc = gspread.service_account(filename="cred.json")

sh = gc.open("Ticket (Responses)").sheet1

a_column_values = sh.col_values(1) 
b_column_values = sh.col_values(2)
c_column_values = sh.col_values(3)  

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%#m/%#d/%Y %H:%M:%S")
test_day = "1/7/2024"
#print("Formatted Date and Time:", formatted_datetime)

# Find the minimum length of both columns
min_length = min(len(a_column_values), len(c_column_values))

# Iterate through the common range
for i in range(1, min_length):
        a_value = a_column_values[i]
        b_value = b_column_values[i]
        c_value = c_column_values[i]

    # Check if A column value is not empty
        if a_value == 'FALSE' and (b_value[:-9] == test_day or b_value[:-8] == test_day):
            print(f"Value in Column C: {c_value}")



