#import library
import gspread

#connect to the service account
gc = gspread.service_account(filename="cred.json")

#connect to your sheet (between "" = the name of your G Sheet, keep it short)
sh = gc.open("(F24/S25) iLab Dashboard").sheet1

#get the values from cells a2 and b2
name = sh.acell("a2").value
website = sh.acell("b1").value

print(name)
print(website)