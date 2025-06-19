"""Configuration module to adapt TouchSelfie behavior"""
import json
import os

class Configuration():
    """Configuration class acts as configuration keys/values holder"""
    # default values
    user_name = None
    logo_file = None
    countdown1  = 5 # seconds of preview before first snap
    countdown2  = 3 # seconds of preview between snaps (Four pictures mode)
    photo_caption = "" # Caption in the photo album
    archive      = True # Do we archive photos locally
    archive_dir  = os.path.join("..","Photos") # Where do we archive photos
    archive_to_all_usb_drives  = True
    album_id      = None #  use install_credentials.py to create 'album.id'
    album_name   = "Drop Box"
    email_subject = "Here's your photo!" # subject line of the email sent from the photobooth
    # Brief body of the message sent from the photobooth
    email_message     = "Greetings, here's your photo sent from the photobooth"
    full_screen  = True #Start application in full screen
    enable_email  = True #Enable the 'send email" feature
    enable_upload = True #Enable the upload feature
    enable_print = False #Enable the printer feature
    enable_effects = True
    selected_printer = None #No printer select
    enable_hardware_buttons = False #Enable hardware buttons
    enable_email_logging = False # Should we log outgoing emails?
    test_email_address = None # Email address to use for testing purposes
    # EXIF Data to be added to the photos
    camera_make = "Raspberry Pi"
    camera_model = "Raspberry Pi Camera Module v2"
    image_description = "MAHS Class of 1985 40th Class Reunion"
    image_artist = "TouchSelfie project by Caroline Dunn modified by Richard Teel"
    image_comment = "5 July 2025, MAHS Class of 1985 40th Class Reunion at the Montrose, PA VFW"
    software = "TouchSelfie by Caroline Dunn modified by Richard Teel"
    image_keywords = "TouchSelfie, Raspberry Pi, Photobooth"

    #init
    def __init__(self,configuration_file_name):
        """Creates the configuration object with default values and load the configuration file

        __init__ will parse the configuration file given as its argument
        After parsing, is_valid property is set to True if no error was encountered

        Arguments:
            configuration_file_name -- the conf.json file to read from or write to
        """
        self.config_file = configuration_file_name
        self.is_valid = False
        self.__read_config_file()

    def __read_config_file(self):
        self.is_valid = True
        config = None
        if not os.path.exists(self.config_file):
            print(f"Configuration file {self.config_file} does not exist, using default values")
            self.is_valid = False
            return False
        try:
            with open(self.config_file, 'r', encoding='utf-8') as content_file:
                file_content = content_file.read()
            config = json.loads(file_content)
        except json.JSONDecodeError as error:
            print(f"Error while parsing {self.config_file} config file : {error}")
            self.is_valid = False
            return False
        except FileNotFoundError as error:
            print(f"Configuration file {self.config_file} not found: {error}")
            self.is_valid = False
            return False
        except IOError as error:
            print(f"Error reading {self.config_file} config file : {error}")
            self.is_valid = False
            return False

        if "gmail_user" in list(config.keys()):
            self.user_name = config['gmail_user']
        else:
            #mandatory configuration!!
            self.is_valid = False


        # all other configuration keys are optional
        if "countdown_before_snap" in list(config.keys()):
            self.countdown1 = config["countdown_before_snap"]
        if "countdown_inter_snap" in list(config.keys()):
            self.countdown2 = config["countdown_inter_snap"]
        if "snap_caption" in list(config.keys()):
            self.photo_caption = config["snap_caption"]
        if "local_archive" in list(config.keys()):
            self.archive = config["local_archive"]
        if "archive_to_all_usb_drives" in list(config.keys()):
            self.archive_to_all_usb_drives = config["archive_to_all_usb_drives"]
        if "local_archive_dir" in list(config.keys()):
            self.archive_dir = config["local_archive_dir"]
        if "google_photo_album_id" in list(config.keys()):
            self.album_id = config["google_photo_album_id"]
        if "google_photo_album_name" in list(config.keys()):
            self.album_name = config["google_photo_album_name"]
        if "email_subject" in list(config.keys()):
            self.email_subject = config["email_subject"]
        if "email_body" in list(config.keys()):
            self.email_message = config["email_body"]
        if "logo_file" in list(config.keys()):
            self.logo_file = config["logo_file"]
        if "full_screen" in list(config.keys()):
            self.full_screen = config["full_screen"]
        if "enable_email" in list(config.keys()):
            self.enable_email = config["enable_email"]
        if "enable_upload" in list(config.keys()):
            self.enable_upload = config["enable_upload"]
        if "enable_print" in list(config.keys()):
            self.enable_print = config["enable_print"]
        if "enable_effects" in list(config.keys()):
            self.enable_effects = config["enable_effects"]
        if "selected_printer" in list(config.keys()):
            self.selected_printer = config["selected_printer"]
        if "enable_hardware_buttons" in list(config.keys()):
            self.enable_hardware_buttons = config["enable_hardware_buttons"]
        if "enable_email_logging" in list(config.keys()):
            self.enable_email_logging = config["enable_email_logging"]
        if "test_email_address" in list(config.keys()):
            self.test_email_address = config["test_email_address"]
        else:
            self.test_email_address = self.user_name
        # EXIF Data
        if "cameraMake" in list(config.keys()):
            self.camera_make = config["cameraMake"]
        if "cameraModel" in list(config.keys()):
            self.camera_model = config["cameraModel"]
        if "imageDescription" in list(config.keys()):
            self.image_description = config["imageDescription"]
        if "imageArtist" in list(config.keys()):
            self.image_artist = config["imageArtist"]
        if "imageComment" in list(config.keys()):
            self.image_comment = config["imageComment"]
        if "software" in list(config.keys()):
            self.software = config["software"]
        if "imageKeyWords" in list(config.keys()):
            self.image_keywords = config["imageKeyWords"]

        return self.is_valid


    def write(self):
        """ write the configuration object to the configuration file given at creation time"""
        myconfig = {
            "gmail_user": self.user_name,
            "countdown_before_snap": self.countdown1,
            "countdown_inter_snap": self.countdown2,
            "snap_caption": self.photo_caption,
            "local_archive" : self.archive,
            "archive_to_all_usb_drives" : self.archive_to_all_usb_drives,
            "local_archive_dir" : self.archive_dir,
            "google_photo_album_id" : self.album_id,
            "google_photo_album_name" : self.album_name,
            "email_subject": self.email_subject,
            "email_body":self.email_message,
            "logo_file": self.logo_file,
            "full_screen": self.full_screen,
            "enable_email": self.enable_email,
            "enable_upload": self.enable_upload,
            "enable_print": self.enable_print,
            "enable_effects": self.enable_effects,
            "selected_printer": self.selected_printer,
            "enable_hardware_buttons": self.enable_hardware_buttons,
            "enable_email_logging" : self.enable_email_logging,
            "test_email_address": self.test_email_address,
            # EXIF Data
            "cameraMake": self.camera_make,
            "cameraModel": self.camera_model,
            "imageDescription": self.image_description,
            "imageArtist": self.image_artist,
            "imageComment": self.image_comment,
            "software": self.software,
            "imageKeyWords": self.image_keywords
        }
        try:
            with open(self.config_file,'w', encoding='utf-8') as config:
                config.write(json.dumps(myconfig, indent =4, sort_keys=True))
        except Exception as error:
            raise ValueError(f"Problem writing {self.config_file} " +
                             "configuration file: {error}") from error


if __name__ == "__main__":

    configuration = Configuration("myconf.conf")
    if not configuration.is_valid:
        configuration.write()
