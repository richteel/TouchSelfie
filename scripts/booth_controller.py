"""Controller Class for Booth Management System."""

import os
import shutil
import time
import logging
import math

from PIL import Image # type: ignore # pylint: disable=E0401

import helpers
import constants
from configuration import Configuration
from booth_model import BoothModel
from booth_view import BoothView
from booth_camera import BoothCamera
from booth_google import BoothGoogle

class BoothController:
    """Controller class for managing the booth application."""

    def __init__(self):
        """Initialize the BoothController."""
        # Set up logging
        if not os.path.exists(constants.LOGS_FOLDER):
            os.makedirs(constants.LOGS_FOLDER)
        logging.basicConfig(
            filename=os.path.join(constants.LOGS_FOLDER,
                                  f"touchselfie_{time.strftime('%Y-%m-%d')}.log"),
            format=constants.LOG_FORMAT,
            # level=logging.CRITICAL # 50
            # level=logging.ERROR  # 40
            # level=logging.WARNING  # 30
            level=logging.INFO # 20
            # level=logging.DEBUG # 10
            # level=logging.NOTSET # 0
            )
        self.log = logging.getLogger(__name__)

        self.log.info("Started Initialization of Photobooth")

        self.camera = BoothCamera(
            screen_width=800,
            screen_height=480
        )
        self.configuration = Configuration(constants.CONFIGURATION_FILE)
        self.model = BoothModel()
        self.view = BoothView(self)

        self.camera.screen_width = self.view.screen_width
        self.camera.screen_height = self.view.screen_height
        self.log.info("Camera Initialization Completed")
        # Set the EXIF metadata for the camera
        self.camera.camera_make = self.configuration.camera_make
        self.camera.camera_model = self.configuration.camera_model
        self.camera.image_description = self.configuration.image_description
        self.camera.image_artist = self.configuration.image_artist
        self.camera.image_comment = self.configuration.image_comment
        self.camera.software = self.configuration.software
        self.camera.image_keywords = self.configuration.image_keywords

        self.google_handler = BoothGoogle()
        self.suspend_preview = False
        self.last_photo_path = None
        self.usb_archive_path = None

        self.log.info("os.path.expanduser('~'): %s", os.path.expanduser('~'))
        print(f"os.path.expanduser('~'): {os.path.expanduser('~')}")
        self.log.info("Finished Initialization of Photobooth")


    def main(self):
        """Main function to run the booth application."""
        self.log.info("Starting Photobooth UI")
        self.view.main()

    def _assemble_animation(self, button, photos):
        """Assemble an annimation from the list of photos taken."""
        if not button or not photos or len(photos) == 0:
            self.view.update_status("No photos taken.")
            self.log.warning("No photos taken.")
            return None

        for photo in photos:
            if not os.path.exists(photo):
                self.view.update_status(f"Photo does not exist. {photo}")
                self.log.warning("Photo does not exist. %s", photo)
                return None

        gif_period_millis = int(button["gif_period_millis"]) or 50
        self.log.info("Creating animated GIF with %d photos, period %d ms.",
                         len(photos), gif_period_millis)
        for photo_filename in photos:
            if not os.path.exists(photo_filename):
                self.view.update_status(f"Photo {photo_filename} does not exist.")
                self.log.warning("Photo %s does not exist.", photo_filename)
                return None

        self.log.debug("Assembling animation")

        animation_filename = os.path.join(constants.TEMP_FOLDER, "animation.gif")
        command_string = f"convert -delay {gif_period_millis} " + \
            f"{os.path.join(constants.TEMP_FOLDER,'photo_')}*.jpg " + \
                f"{animation_filename}"
        os.system(command_string)
        if not os.path.exists(animation_filename):
            self.view.update_status("Failed to create animated GIF.")
            self.log.warning("Failed to create animated GIF.")
            return None

        return animation_filename

    def _assemble_collage(self, button, photos):
        """Assemble a photo from the list of photos taken."""
        if not button or not photos or len(photos) == 0:
            self.view.update_status("No photos taken.")
            self.log.warning("No photos taken.")
            return None

        photo_count = button.get("photo_count", 1)
        if photo_count != len(photos):
            self.view.update_status(f"Expected {photo_count} photos, but got {len(photos)}.")
            self.log.warning("Expected %d photos, but got %d.", photo_count, len(photos))
            return None

        photos_sqr = int(math.sqrt(photo_count))
        if photos_sqr * photos_sqr != photo_count:
            self.view.update_status(f"Photo count {photo_count} is not a perfect square.")
            self.log.warning("Photo count %d is not a perfect square.", photo_count)
            return None

        photo_index = 0
        temp_image = Image.open(photos[photo_index])
        photo_width = temp_image.width
        photo_height = temp_image.height
        temp_image = None
        collage_width = photo_width * photos_sqr
        collage_height = photo_height * photos_sqr
        collage = Image.new('RGBA', (collage_width, collage_height))
        # print(f"Complete image size: {snapshot_width}x{snapshot_height}")
        # self.handle_exit()
        self.log.info("Creating collage of size %dx%d from %d photos.",
                         collage_width, collage_height, photo_count)
        for i in range(photos_sqr):
            for j in range(photos_sqr):
                if not os.path.exists(photos[photo_index]):
                    self.view.update_status(f"Photo {photos[photo_index]} does not exist.")
                    return None
                im = Image.open(photos[photo_index])
                collage.paste(im, (j * photo_width,   i * photo_height,
                                    (j + 1) * photo_width, (i + 1) * photo_height))
                photo_index += 1

        # Add foreground image if specified
        if "foreground_image" in button and button["foreground_image"]:
            if not os.path.exists(button["foreground_image"]):
                self.view.update_status(f"Foreground image {button['foreground_image']} " +
                                        "does not exist.")
            else:
                frame_image = Image.open(button["foreground_image"])
                # Resize foreground image to fit the assembled photo size
                frame_image = frame_image.resize((collage_width,collage_height), Image.ANTIALIAS)
                frame_image = frame_image.convert("RGBA")
                collage = collage.convert('RGBA')
                # Paste the foreground image on top of the assembled photo
                collage = Image.alpha_composite(collage, frame_image)
                self.log.info("Foreground image added to the assembled photo.")

        # Save the assembled photo to a temporary file
        assembled_photo_path = os.path.join(constants.TEMP_FOLDER, "assembled_photo.jpg")
        collage = collage.convert('RGB')
        collage.save(assembled_photo_path)
        self.camera.add_exif_metadata(assembled_photo_path)

        return assembled_photo_path

    def _countdown_and_take_photos(self, button):
        """Handle countdown and take photos based on the button clicked."""
        photo_last_ms = helpers.millis()
        current_ms = helpers.millis()
        self.view.update_status("Counting down to take photo...")
        self.log.info("Counting down to take photo...")

        self._delete_temp_files()

        # Wait for the countdown to finish
        countdown_last_ms = helpers.millis()
        countdown_running = self.view.show_countdown(99)
        while countdown_running:
            # Update the view and check for events
            self.view.update()

            # Change the countdown overlay every second
            current_ms = helpers.millis()
            if (current_ms - countdown_last_ms) >= 1000:
                countdown_last_ms = current_ms
                countdown_running = self.view.show_countdown()

            # Update the preview image
            if (current_ms - photo_last_ms) >= self.view.poll_interval:
                photo_last_ms = current_ms
                if not self.suspend_preview:
                    self.update_preview_image()

        # Take the photo after the countdown
        ms_between_photos = button.get("snap_period_millis", 1000)
        number_of_photos = button.get("photo_count", 1)
        photos_taken = 0
        photos = []  # List to store paths of photos taken
        countdown_last_ms = helpers.millis()
        if not os.path.exists(constants.TEMP_FOLDER):
            os.makedirs(constants.TEMP_FOLDER)
        # Take first photo immediately after countdown
        photo_file = os.path.join(constants.TEMP_FOLDER, f"photo_{photos_taken + 1}.jpg")
        self.view.update_status("Taking photo...")
        status = self.take_photo_save_to_file(
            filepath=photo_file,
            width=button["photo_size"][0],
            height=button["photo_size"][1]
        )
        if status:
            photos_taken += 1
            photos.append(photo_file)
            self.view.update_status(f"Photo {photos_taken} of {number_of_photos} taken.")
        while photos_taken < number_of_photos:
            # Update the view and check for events
            self.view.update()

            # Take a photo
            current_ms = helpers.millis()
            if (current_ms - countdown_last_ms) >= ms_between_photos:
                countdown_last_ms = current_ms
                # Take the next photo
                photo_file = os.path.join(constants.TEMP_FOLDER,
                                            f"photo_{photos_taken + 1}.jpg")
                self.view.update_status("Taking photo...")
                status = self.take_photo_save_to_file(
                    filepath=photo_file,
                    width=button["photo_size"][0],
                    height=button["photo_size"][1]
                )
                if status:
                    photos_taken += 1
                    photos.append(photo_file)
                    self.view.update_status(f"Photo {photos_taken} of " +
                                            f"{number_of_photos} taken.")

            # If it's the last photo, update the status
            if photos_taken == number_of_photos:
                self.view.update_status("Photos taken successfully.")
        return photos

    def _delete_temp_files(self):
        """Removes all files from the temp folder."""

        # Use glob to find all files ending with .jpg or .JPG
        for filename in os.listdir(constants.TEMP_FOLDER):
            file_path = os.path.join(constants.TEMP_FOLDER, filename)
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")

    def handle_button_click(self, button):
        """Handle button click events."""
        self.view.suspend_poll = True
        self.log.info("Button clicked: %s", button['name'])

        # Show the countdown overlay if button is for taking a photo
        if button["name"] in ["Single Photo", "Four Square", "Nine Square",
                              "Animated GIF"]:
            self.view.hide_buttons()
            photos = self._countdown_and_take_photos(button)
            # Stop the camera after taking photos
            # If the camera remains active, the camera buffer may fill up
            # and cause the camera to stop working.
            self.camera.stop_camera()

            if not photos or len(photos) == 0:
                self.view.update_status("No photos taken.")
                self.log.warning("No photos taken.")
                self.view.show_buttons()
                self.view.suspend_poll = False
                return

            self.view.update_status("Photo(s) taken successfully.")
            # Show an information image while processing the photos
            self.view.show_image(os.path.join(constants.RESOURCES_FOLDER, "processing.png"))
            assembled_image = None
            if button["name"] == "Animated GIF":
                # Assemble the animation from the photos taken
                assembled_image = self._assemble_animation(button, photos)
            else:
                # Assemble the photo from the photos taken
                assembled_image = self._assemble_collage(button, photos)

            if assembled_image is None:
                self.view.update_status("Failed to assemble the photo.")
                self.log.warning("Failed to assemble the photo.")
                self.view.show_buttons()
                self.view.suspend_poll = False
                return

            # Archive the final assembled image
            photo_filename = f"touchselfie_{time.strftime('%Y%m%d_%H%M%S')}"
            if button["name"] == "Animated GIF":
                photo_filename += ".gif"
            else:
                photo_filename += ".jpg"

            if not os.path.exists(constants.ARCHIVE_FOLDER):
                os.makedirs(constants.ARCHIVE_FOLDER)
            self.last_photo_path = os.path.join(constants.ARCHIVE_FOLDER, photo_filename)
            self.log.info("Archiving final photo to %s", self.last_photo_path)
            shutil.copy2(assembled_image, self.last_photo_path)

            self.view.update_status("Photo processed successfully.")

            if button["name"] == "Animated GIF":
                # self.view.show_animation(assembled_photo_path)
                pass
            else:
                self.view.show_image(self.last_photo_path)
            current_millis = helpers.millis()
            while helpers.millis() - current_millis < 3000:
                self.view.update()

            self.view.update_status("Uploading photo...")
            # Show an information image while processing the photos
            self.view.show_image(os.path.join(constants.RESOURCES_FOLDER, "uploading.png"))
            self.google_handler.upload_photo_to_album(self.last_photo_path)

            # USB Archive?
            if self.configuration.archive_to_all_usb_drives:
                try:
                    # Get the path to the USB drive if not set
                    if not self.usb_archive_path:
                        usb_mount_point_root = "/media/pi/"
                        root, dirs, files = next(os.walk(usb_mount_point_root)) # pylint: disable=W0612
                        for directory in dirs:
                            mountpoint = os.path.join(root,directory)
                            if mountpoint.find("SETTINGS") != -1:
                                #don't write into SETTINGS directories
                                continue
                            if os.access(mountpoint,os.W_OK):
                                #can write in this mountpoint
                                self.usb_archive_path = mountpoint

                    if self.usb_archive_path:
                        dest_dir = os.path.join(mountpoint,"TouchSelfiePhotos")
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                        shutil.copy(self.last_photo_path, dest_dir)
                        self.log.info("Archived photo %s to USB: %s",
                                      self.last_photo_path, dest_dir)
                except Exception as e: # pylint: disable=W0718
                    self.log.error("Error while getting USB mount point: %s", e)
                    self.usb_archive_path = None

            self.update_preview_image()
            self.view.show_buttons()
            self.view.update_status("Ready")

        if button["name"] == "Print Photo":
            # self.model.print_photo()
            self.view.update_status("Printing photo...")
        elif button["name"] == "Email Photo":
            # self.model.email_photo()
            if not self.google_handler.ready:
                self.view.update_status("Google handler is not ready. Cannot email photo.")
                self.log.error("Google handler is not ready. Cannot email photo.")
                self.view.suspend_poll = False
                return
            if not self.last_photo_path or not os.path.exists(self.last_photo_path):
                self.view.update_status("No photo taken to email.")
                self.log.warning("No photo taken to email.")
                self.view.suspend_poll = False
                return

            self.view.update_status("Emailing photo...")
            self.google_handler.send_email("richjteel@gmail.com", self.last_photo_path)
        elif button["name"] == "Effects":
            # self.model.apply_effects()
            self.view.update_status("Applying effects...")

        # self.view.update_preview_image(image = Image.open(button["icon"]))

        self.view.suspend_poll = False

    def handle_exit(self):
        """Handle exit events."""
        self.view.suspend_poll = True
        self.view.update_status("Exiting the application...")
        self.log.info("Exiting the application")
        self.camera.stop_camera()
        time.sleep(1)  # Reduced sleep time since we're handling callbacks better
        self._delete_temp_files()

        # Use quit() instead of destroy() to properly exit the mainloop
        # This prevents the "invalid command name" error from scheduled callbacks
        try:
            self.view.quit()
        except Exception as e: # pylint: disable=W0718
            self.log.warning("Error during quit: %s", e)
            # Fallback to destroy if quit fails
            self.view.destroy()

    def handle_poll_timer(self):
        """Handle poll timer events."""
        # This method can be used to handle any timer-related events
        # For example, updating the countdown overlay or handling timeouts
        # print("Handling timer event...")
        # self.view.update_countdown_overlay()

        self.view.suspend_poll = True

        if not self.suspend_preview:
            # Update the preview image if not suspended
            self.update_preview_image()

        # Resume polling after handling the event
        self.view.suspend_poll = False

    def take_photo_save_to_file(self, filepath, width=None, height=None):
        """Take a photo and save it to a file."""
        if not filepath:
            self.view.update_status("No file path provided for saving photo.")
            return False

        self.log.info("Taking photo with width=%s, height=%s to %s",
                         width, height, filepath)
        status_take_photo = self.camera.take_photo(False, width, height)

        if not status_take_photo["success"] or status_take_photo["pil_image"] is None:
            self.view.update_status(status_take_photo["message"])
            return False

        # If the photo was taken successfully, show in preview
        self.view.update_status("Photo taken successfully.")
        preview_image = status_take_photo["pil_image"].transpose(Image.FLIP_LEFT_RIGHT)
        preview_image.thumbnail((self.camera.preview_width, self.camera.preview_height))
        if preview_image is None:
            self.view.update_status("Failed to create preview image.")
            self.log.warning("Failed to create preview image.")
            print("Failed to create preview image.")
        else:
            # Update the preview image in the view
            self.view.update_preview_image(preview_image)
        # If the photo was taken successfully, save it to a file
        status_save_photo = self.camera.save_image(status_take_photo["pil_image"], filepath)

        if not status_save_photo["success"]:
            self.view.update_status(status_save_photo["message"])
            return False

        return True

    def snap_photo(self, preview=False, width=None, height=None):
        """Take a photo and return the image."""
        self.log.info("Taking photo with preview=%s, width=%s, height=%s",
                         preview, width, height)
        status = self.camera.take_photo(preview, width, height)

        if not status["success"] or status["pil_image"] is None:
            self.view.update_status(status["message"])
            return None

        # If the photo was taken successfully, update the view
        self.view.update_preview_image(status["pil_image"])
        return status["pil_image"]

    def update_preview_image(self):
        """Update the preview image in the view."""
        # Update the preview image if not suspended
        status = self.camera.take_photo(True)

        if not status["success"] or status["pil_image"] is None:
            self.view.update_status(status["message"])
        else:
            # If the preview image was updated successfully, update the view
            self.view.update_preview_image(status["pil_image"])
