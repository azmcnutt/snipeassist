# snipeassist
A simple Python program to scan assets into SnipeIT.

Tested on Python Version 3.11 and Windows 11.  It may run on Linux, more testing is required.  It will not run on ChromeOS Linux.

Requires python, git, pipenv
# Installation (Windows)

First you will need a working installation of [SnipeIT](https://snipeitapp.com/).  Hosted and self-install on premise supported

1. Get your SnipeIT URL.  This is address you use to access the root page of you SnipeIT install with ```/api/v1/``` added at the end (please note it should end with a trailing slash).
   1. Example: ```https://develop.snipeitapp.com/api/v1/```
2. Generate a SnipeAPI Key
   1. Click on your user account in the upper right of the SnipeIT screen and select Manage API Keys
   2. Click Create New
   3. Give the key a name and click Create New
   4. Once generated, copy the API and save it someplace secure.  It will only be shown once and you cannot retrieve it again.  Protect it like a password.
3. On your computer, open a terminal windows or command prompt
4. Test to see if you have Python installed:  ```python --version```.  If you receive Python 3.11 (or similar) you should be good to go.  Otherwise:
   1. To install Python enter ```winget install Python.Python.3.11```
5. Install pipenv: ```pip install pipenv```
6. Install Git: ```Git.Git```
7. In the terminal/command prompt navigate to the folder where you would like to clone SnipeAssist.  Please note: git will create a folder named snipeassist and then download everything in that folder.
8. Clone the snipeassist repository:  ```git clone https://github.com/azmcnutt/snipeassist.git```
9.  Change into the snipeassist folder ```cd snipeassist```
10. Make a copy of the setting.example.py file:  ```copy snipeassist\setting.example.py snipeassist\settings.py```
11. make a folder for your virtual environment: ```mkdir venv```
12. Now install the pipenv requirements:  ```pipenv install```
13. Add your Snipe URL and API key to the setting.py file (for low security installation, the Snipe URL and API key can be stored directly in the setting.py file.  If you require more security, use environment variables).  The SnipeIT API Key can be quite long and should be entered on a single line.
    1.  ```SNIPE_URL = 'https://develop.snipeitapp.com/api/v1/'```
    2.  ```API_KEY = [APIKEY]```
14. Optional settings:
    1.  SAVE_ON_EXIT = ```True```: settings will be saved when exiting the program and during scanning, ```False```: settings will only be saved when you click File --> Save
    2.  SOUND_DING = Path to a sound file to signify that something was scanned without error.
    3.  SOUND_SUCCESS = Path to a sound file to signify that an asset was created or created + checked out.
    4.  SOUND_WARNING = Path to a sound file to signify that something was not created, checked out, or scanned properly.
    5.  ASK_BEFORE_QUIT = ```True```: you will get a confirmation when exiting the program, ```False```: when clicking the X or File --> Exit, the program will quit without asking
    6.  Logging:
        1.  LOG_LEVEL = Logging level for the console.  Valid values are: ```DEBUG```, ```INFO```, ```WARNING```, ```ERROR```, ```CRITICAL```.
        2.  LOG_FILE_LEVEL = Logging level for file logs
        3.  LOG_NAME = Filename for the log file
        4.  LOG_SIZE = Size of the log file
        5.  LOG_COUNT = Number of log files to keep
        6.  LOGGING_CONFIG = {} - Python Logging config.  
15. You should now be able to launch snipeassist: ``` pipenv run python snipeassist/snipe_assist.py```

# Running snipeassist
1. On the snipeassist screen, there are many options:
   1. Required Items - the items across the top are required:
      1. Company:  Choose the company for the scanned assets
      2. Model: Choose the model for the scanned assets
      3. Location:  Choose the location and default location for the scanned assets
      4. Status:  Choose the status for the scanned assets
         1. Please note: This should be Ready to Deploy for assets that will be checked out
      5. Supplier:  Choose the supplier for the scanned assets
   2. Static Items - Asset properties that can be set to static items (tick the checkbox to enable and fill the fields).  These items match to SnipeIT Asset fields
      1. Asset Name and Append and Increment
         1. When asset name is ticked, the asset name will be filled in.  If you also tick the append checkbox, the number enetered in the append box will be added to the name each time an asset is created.  The number will then be incremented and added to the next asset.
         2. The append and increment setting is useful when scanning in groups of items (like lab computers).
      2. Purchase Date
      3. Order Number
      4. Purchase Cost
      5. Warranty (in months)
      6. Notes
   3. Scannable Items
      1. Asset Tag:  If you have auto asset tags enabled in Snipe, this can remain blank.  However, if you have your own asset tags with bar codes, check this box and you will be prompted to scan the asset tag.
      2. Serial Num:  Tick this box to be prompted to scan the serial number.
   4. Custom Fields - when a model with custom fields is selected, this area will have a tab for each custom field.
      1. For each custom field you will have the option to ```Do not record``` (ignore this field), ```Fill```, or ```Scan```.
      2. If ```Fill``` is selected, choose the option from the combo box or enter the data into the text box.
      3. If ```Scan``` is selected you will be prompted to scan the data.
   5. Check Out
      1. If you would like created assets to be checked out to a User, Location, or Asset, tick the box next to Enable Check Out
      2. Then from the drop down, select User, Asset, or Location
      3. From the bottom drop down, select the user, asset, or location to check the newly created asset out.
         1. Please note:  If you have a large number of Users, Locations, and Assets it will take time for the screen to refresh when enabling check out.
   6. Refresh Req Items Button - click this button to refresh the lists of required items.  Handy if you just created a model and do not want to exit and reopen snipeassist.
   7. Start Scann Button - Once all of the data has been entered, click this to start scanning.
# Scanning
Note: snpieassist is designed to work with barcode scanners that enter the scanned data and then press enter like a keyboard.  It is not compatible with serial or other non-HID scanners.

1. In the scanning box, a label will appear above the text box requesting you scan a particular field.  The cursor should be in the text box.
2. Scan the bar code for the field requested.  You should hear a "ding" when the data is accepted
3. If there more item(s) to scan, the label will request the next item.
4. Once all items have been scanned, snipeassist will attempt to create the item.  If successful you will hear the success sound.
   1. If you hear the warning sound, check the console log to see what went wrong.
5. When finished scanning, click Stop Scanning.





### Sound File Source
[Ding](https://pixabay.com/sound-effects/ding-126626/)

[Success](https://pixabay.com/sound-effects/new-notification-7-210334/)

[Warning](https://pixabay.com/sound-effects/error-call-to-attention-129258/)