"""Google API interactions for Photobooth."""

import os
import sys
import json
import logging
import time

from oauth2services import OAuthServices
from configuration import Configuration
import constants

def send_email(data):
    """Send a photo via email using the Google API."""
    filename = data["filename"]
    if filename is not None and filename.strip():
        filename = filename.strip()
        if not os.path.exists(filename):
            logging.error("File %s does not exist.", filename)
            return {"status": "error", "message": "File does not exist."}

    to = data["to"]
    subject = data.get("subject", "Photobooth Selfie")
    body = data.get("body", "Here is your selfie from the Photobooth!")

    if not to or not to.strip():
        logging.error("Email address is required.")
        return {"status": "error", "message": "Email address is required."}

    config = Configuration("configuration.json")
    if not config.is_valid:
        logging.error("Configuration is not valid.")
        return {"status": "error", "message": "Invalid configuration."}

    # configdir = os.path.expanduser('./')
    configdir = os.path.dirname(os.path.abspath(__file__))

    try:
        oauth2service = OAuthServices(
            client_secret=os.path.join(configdir, constants.APP_ID_FILE),
            credentials_store=os.path.join(configdir, constants.CREDENTIALS_STORE_FILE),
            username=config.user_name,
            enable_upload = config.enable_upload,
            enable_email = config.enable_email,
            log_level = logging.WARNING)
    except Exception as e: # pylint: disable=W0718
        logging.error("Failed to send the email: %s", str(e))
        return {"status": "error", "message": "Failed to send the email."}

    retcode = oauth2service.send_message(
                    to,
                    subject,
                    body,
                    filename)

    if retcode:
        return {"status": "success", "message": "Email sent successfully."}

    return {"status": "error", "message": "Failed to send email."}

def upload_photo(data):
    """Add a photo to the Google Photos library."""

    config = Configuration("configuration.json")
    if not config.is_valid:
        logging.error("Configuration is not valid.")
        return {"status": "error", "message": "Invalid configuration."}


    # configdir = os.path.expanduser('./')
    configdir = os.path.dirname(os.path.abspath(__file__))

    try:
        oauth2service = OAuthServices(
            client_secret=os.path.join(configdir, constants.APP_ID_FILE),
            credentials_store=os.path.join(configdir, constants.CREDENTIALS_STORE_FILE),
            username=config.user_name,
            enable_upload = config.enable_upload,
            enable_email = config.enable_email,
            log_level = logging.WARNING)
    except Exception as e: # pylint: disable=W0718
        logging.error("Failed to upload photo: %s", str(e))
        return {"status": "error", "message": "Failed to upload photo."}

    retcode = oauth2service.upload_picture(
                    filename=data["filename"],
                    album_id=config.album_id,
                    title=f"Photobooth Selfie {time.strftime('%d %b %Y %I%M%S')}",
                    caption=f"Photobooth Selfie {time.strftime('%d %b %Y %I%M%S')}"
                    )

    if retcode:
        return {"status": "success", "message": "Photo added successfully."}

    return {"status": "error", "message": "Failed to add photo to album."}

if __name__ == "__main__":
    action = sys.argv[1]
    payload = json.loads(sys.argv[2])

    if action == "add_photo":
        result = upload_photo(payload)
    elif action == "send_email":
        result = send_email(payload)
    else:
        result = {"error": "Unknown action"}
