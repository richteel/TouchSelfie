"""Handle calls to the Google API for Photobooth."""

import os
import os.path
import json
import subprocess

import logging

# import configuration
# import constants

class BoothGoogle:
    """Class to handle Google API interactions for Photobooth."""

    USER_HOME = os.path.expanduser("~")
    SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    VIRTUAL_ENV_DIRECTORY = os.path.join(USER_HOME, "photobooth")
    VIRTUAL_ENV_PYTHON = os.path.join(USER_HOME, "photobooth/bin/python")
    SCRIPT_FILE_PATH = os.path.join(SCRIPT_DIRECTORY, "google_apis.py")
    CREDENTIALS_FILE = os.path.join(SCRIPT_DIRECTORY, "OpenSelfie.json")

    def __init__(self):
        """Initialize the BoothGoogle with the provided API key."""

        self.log = logging.getLogger(__name__)
        self.log.info("Initializing BoothGoogle for Photobooth")

        self.ready = True
        if not os.path.exists(self.SCRIPT_FILE_PATH):
            self.log.error("Script file %s does not exist.", self.SCRIPT_FILE_PATH)
            self.ready = False
        if not os.path.exists(self.CREDENTIALS_FILE):
            self.log.error("Credentials file %s does not exist.", self.CREDENTIALS_FILE)
            self.ready = False
        if not os.path.exists(self.VIRTUAL_ENV_DIRECTORY):
            self.log.error("Virtual environment directory %s does not exist.",
                           self.VIRTUAL_ENV_DIRECTORY)
            self.ready = False
        if not os.path.exists(self.VIRTUAL_ENV_PYTHON):
            self.log.error("Virtual environment Python executable %s does not exist.",
                           self.VIRTUAL_ENV_PYTHON)
            self.ready = False

    def upload_photo_to_album(self, filename: str):
        """Add a photo to the Google Photos album."""
        if not self.ready:
            self.log.error("BoothGoogle is not ready. Cannot add photo to album.")
            return
        if not os.path.exists(filename):
            self.log.error("File %s does not exist.", filename)
            return

        action = "add_photo"
        payload = {
            "filename": filename
        }

        process = subprocess.run(
            [self.VIRTUAL_ENV_PYTHON, self.SCRIPT_FILE_PATH, action, json.dumps(payload)],
            capture_output=True,
            text=True,
            check=False
        )

        if process.returncode != 0:
            self.log.error("Failed to add photo to album: %s", process.stderr)
            return
        self.log.info("Photo added to album successfully for file: %s", filename)


    def send_email(self, email_address: str, filename: str = None):
        """Send a photo via email using the Google API."""

        if not self.ready:
            self.log.error("BoothGoogle is not ready. Cannot send email.")
            return
        if filename is not None and filename.strip():
            if not os.path.exists(filename):
                self.log.error("File %s does not exist.", filename)
                return

        action = "send_email"
        payload = {
            "to": email_address,
            "subject": "Photobooth Selfie",
            "body": "Here is your selfie from the Photobooth!",
            "filename": filename
        }

        process = subprocess.run(
            [self.VIRTUAL_ENV_PYTHON, self.SCRIPT_FILE_PATH, action, json.dumps(payload)],
            capture_output=True,
            text=True,
            check=False
        )

        if process.returncode != 0:
            self.log.error("Failed to send email: %s", process.stderr)
            return
        self.log.info("Email sent successfully for file: %s", filename)
