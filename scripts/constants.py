"""
Constants for the TouchSelfie program
"""
import os

#### File Paths ####
# Configuration Settings for the TouchSelfie program
CONFIGURATION_FILE = "configuration.json"
APP_ID_FILE = "google_client_id.json"
CREDENTIALS_STORE_FILE = "google_credentials.dat"
RESOURCES_FOLDER = "resources"  # Folder containing resources like icons, images, etc.
LOGS_FOLDER = "../Logs"  # Folder for storing logs
LOG_FORMAT = "%(asctime)s \t " + \
    "%(module)s \t " + \
    "%(funcName)s \t " + \
    "%(lineno)s \t " + \
    "%(levelname)s \t " + \
    "%(message)s"  # Log format
TEMP_FOLDER = "../Temp"  # Temporary folder for storing files
ARCHIVE_FOLDER = "../Photos"  # Folder for storing photos
LOGO_FOLDER = "../logos"  # Folder for storing frames and logos

#### UI Constants ####
# Buttons configuration
BUTTON_PHOTO_ONE = {
    "name": "Single Photo",  # Name of the button
    "location": "bottom",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_portrait.png"), # Path to the button icon
    "photo_size": (3280, 2464),  # Size for a single photo
    "foreground_image": os.path.join(LOGO_FOLDER, 
                                     "logo.png"), 
                                     # Overlay image on top of the collage
}
BUTTON_PHOTO_FOUR = {
    "name": "Four Square",  # Name of the button
    "location": "bottom",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_four.png"), # Path to the button icon
    "photo_size": (1640, 1232),  # Size for a single photo
    "photo_count": 4,  # Number of photos to take
    "foreground_image": os.path.join(LOGO_FOLDER, 
                                     "collage_four_square_logo.png"), 
                                     # Overlay image on top of the collage
}
BUTTON_PHOTO_NINE = {
    "name": "Nine Square",  # Name of the button
    "location": "bottom",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_nine.png"), # Path to the button icon
    "photo_size": (1093, 821),  # Size for a single photo
    "photo_count": 9,  # Number of photos to take
    "foreground_image": os.path.join(LOGO_FOLDER, 
                                     "collage_nine_square_logo.png"), 
                                     # Overlay image on top of the collage
}
BUTTON_PHOTO_ANIMATION = {
    "name": "Animated GIF",  # Name of the button
    "location": "bottom",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_anim.png"), # Path to the button icon
    "photo_size": (1093, 821),  # Size for a single photo
    "photo_count": 10,  # Number of photos to take
    "foreground_image": "", # Overlay image on top of the collage
    "snap_period_millis": 200,  # Time between two snaps in milliseconds
    'gif_period_millis' : 50    # time interval in the animated gif
}
BUTTON_PRINT_PHOTO = {
    "name": "Print Photo",  # Name of the button
    "location": "left",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_print.png"), # Path to the button icon
}
BUTTON_EMAIL_PHOTO = {
    "name": "Email Photo",  # Name of the button
    "location": "right",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_email.png"), # Path to the button icon
}
BUTTON_EFFECTS = {
    "name": "Effects",  # Name of the button
    "location": "right",  # Location of the button on the screen
    "icon": os.path.join(RESOURCES_FOLDER, "ic_effects.png"), # Path to the button icon
}
BUTTONS = [
    BUTTON_PHOTO_ONE,
    BUTTON_PHOTO_FOUR,
    BUTTON_PHOTO_NINE,
    BUTTON_PHOTO_ANIMATION,
    BUTTON_PRINT_PHOTO,
    BUTTON_EMAIL_PHOTO,
    BUTTON_EFFECTS
]

#Image list for in-preview countdown
#Use as many as you want
# COUNTDOWN_OVERLAY_IMAGES[0] will be used during the last second of countdown
# COUNTDOWN_OVERLAY_IMAGES[1] will be used during 1s to 2s
# ...
# last image of the list will be used for greater counts
# (e.g. during the first 5 secs of a 10 secs countdown in this case)
COUNTDOWN_OVERLAY_IMAGES=[
    os.path.join(RESOURCES_FOLDER,"count_down_1.png"),
    os.path.join(RESOURCES_FOLDER,"count_down_2.png"),
    os.path.join(RESOURCES_FOLDER,"count_down_3.png"),
    os.path.join(RESOURCES_FOLDER,"count_down_4.png"),
    os.path.join(RESOURCES_FOLDER,"count_down_5.png"),
    os.path.join(RESOURCES_FOLDER,"count_down_ready.png")]
