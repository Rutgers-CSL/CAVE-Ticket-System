import gspread

# Connect to the service account
gc = gspread.service_account(filename="cred.json")

# Connect to your sheet (between "" = the name of your G Sheet, keep it short)
sh = gc.open("Ticket (Responses)").sheet1

a_column_values = sh.col_values(1)  # Assuming A is the first column (1-indexed)
c_column_values = sh.col_values(3)  # Assuming C is the third column (1-indexed)

# Find the minimum length of both columns
min_length = min(len(a_column_values), len(c_column_values))

# Iterate through the common range
for i in range(1, min_length):
        a_value = a_column_values[i]
        c_value = c_column_values[i]

    # Check if A column value is not empty
        if a_value == 'FALSE':
            print(f"Value in Column A: {a_value}, Corresponding Value in Column C: {c_value}")