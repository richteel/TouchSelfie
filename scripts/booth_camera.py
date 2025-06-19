"""Camera control script for the photobooth."""

import os
import time
import logging

from PIL import Image # type: ignore # pylint: disable=E0401
from picamera2 import Picamera2 # type: ignore # pylint: disable=E0401
from libcamera import Transform # type: ignore # pylint: disable=E0401
import piexif # type: ignore # pylint: disable=E0401

class BoothCamera:
    """Class to take a photo with the Raspberry Pi camera and save it with EXIF metadata."""
    camera_make: str = "Raspberry Pi"
    camera_model: str = ""
    image_description: str = ""
    image_artist: str = ""
    image_comment: str = ""
    software: str = "TouchSelfie"
    image_keywords: str = "TouchSelfie, Raspberry Pi, Photobooth"
    filepath: str = None

    def __init__(self, screen_width: int = 800, screen_height: int = 480):
        """Take photo for the photobooth"""
        self.logger = logging.getLogger(__name__)

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sensor_width = 2592
        self.sensor_height = 1944
        self.preview_width = 640
        self.preview_height = 480
        self.preview_position_x = 0
        self.preview_position_y = 0
        self.camera_model = None
        self.camera = None
        self.still_config = None
        self.preview_config = None
        self.camera_started = False
        self.last_config_was_preview = False
        self.last_photo_width = 0
        self.last_photo_height = 0
        self.camera_is_stopped = True

        self._start_camera()

    def _start_camera(self):
        """Initialize the Raspberry Pi camera."""
        try:
            self.camera = Picamera2()
            camera_info = self.camera.sensor_resolution
            if camera_info:
                self.sensor_width, self.sensor_height = camera_info
            else:
                # fallback default Camera Module v1
                self.sensor_width, self.sensor_height = 2592, 1944

            ratio1 = self.sensor_width / self.sensor_height  # Sensor aspect ratio
            ratio2 = self.preview_width / self.preview_height # Screen aspect ratio
            if ratio1 > ratio2:
                self.preview_height = int(self.preview_width / ratio1)
                self.preview_position_y = int((self.screen_height - self.preview_height) / 2)
                self.preview_position_x = 0
            else:
                self.preview_width = int(self.preview_height * ratio1)
                self.preview_position_x = int((self.screen_width - self.preview_width) / 2)
                self.preview_position_y = 0

            # Create preview configuration
            self.preview_config = self.camera.create_preview_configuration(buffer_count=4,
                                                            display="main",
                                                            transform=Transform(hflip=1),
                                                                sensor={
                                                                    'output_size':
                                                                        (self.sensor_width,
                                                                            self.sensor_height)})
            self.preview_config['raw'] = None
            self.preview_config['lores'] = None

            # Create still configuration
            self.still_config = self.camera.create_still_configuration(
                main={"size": (self.sensor_width, self.sensor_height),
                      "format": "BGR888"},
                # lores={"size": (self.preview_width, self.preview_height),
                #        "format": "YUV420"},
                       buffer_count=2)
            self.still_config['raw'] = None
            self.still_config['lores'] = None

            # Set camera options & use the preview configuration
            self.camera.align_configuration(self.preview_config)
            self.camera.configure(self.preview_config)
            self.camera.options["compress_level"] = 2
            self.last_photo_width = self.sensor_width
            self.last_photo_height = self.sensor_height

            self.camera.start()
            self.camera_is_stopped = False
            time.sleep(2)  # Allow camera to warm up

            # Get camera model (if available)
            if self.camera_model is None or not self.camera_model.strip():
                self.camera_model = getattr(self.camera, "revision", "Camera Module")

            self.camera_started = True
            return {"success": True, "message": "Camera initialized successfully"}
        except Exception as e:  # pylint: disable=W0718
            self.camera_started = False
            self.logger.error("Error initializing camera: %s", e)
            return {"success": False, "message": f"Error initializing camera: {e}"}

    def add_exif_metadata(self, filepath):
        """Add EXIF metadata to the captured photo."""
        if not filepath or not os.path.exists(filepath):
            return {"success": False, "message": "Filepath is None or file does not exist"}

        # Prepare EXIF data using piexif
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        # ImageDescription (0th, tag 270)
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = self.image_description
        # Artist (Photographer) (0th, tag 315)
        exif_dict["0th"][piexif.ImageIFD.Artist] = self.image_artist
        # Model (0th, tag 271)
        exif_dict["0th"][piexif.ImageIFD.Make] = self.camera_make
        # Model (0th, tag 272)
        exif_dict["0th"][piexif.ImageIFD.Model] = self.camera_model
        # Software (0th, tag 305)
        exif_dict["0th"][piexif.ImageIFD.Software] = self.software
        # Comment (0th, tag 37510)
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = self.image_comment.encode('utf-8')
        # XPComment (0th, tag 40092)
        exif_dict["0th"][piexif.ImageIFD.XPComment] = self.image_comment.encode('utf-16')
        # XPKeywords (0th, tag 40094)
        exif_dict["0th"][piexif.ImageIFD.XPKeywords] = self.image_keywords.encode('utf-16')
        # DateTime (0th, tag 306)
        dt = time.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["0th"][piexif.ImageIFD.DateTime] = dt
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = dt

        # OffsetTime (Exif, tag 36880)
        offset = time.strftime("%z")
        if offset:
            offset = offset[:3] + ":" + offset[3:]
            exif_dict["Exif"][36880] = offset

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filepath)

        return {"success": True, "message": "EXIF metadata added successfully"}

    def save_image(self, pil_image = None, filepath: str = None):
        """Save the image to a file"""
        if pil_image is None or filepath is None:
            return {"success": False, "message": "Image or filepath is None"}

        try:
            # Convert numpy array to PIL Image
            pil_image.save(filepath, "JPEG")

            return {"success": True, "message": "Image saved successfully"}
        except Exception as e:  # pylint: disable=W0718
            self.logger.error("Error saving image: %s", e)
            return {"success": False, "message": f"Error saving image: {e}"}

    def stop_camera(self):
        """Stop the camera."""
        if self.camera is not None and self.camera_started:
            try:
                self.camera.stop()
                self.camera_is_stopped = True
                time.sleep(2) # Allow camera to warm up
                self.logger.info("Camera stopped successfully: %s", self.camera_is_stopped)
                return {"success": True, "message": "Camera stopped successfully"}
            except Exception as e:  # pylint: disable=W0718
                self.logger.error("Error stopping camera: %s", e)
                return {"success": False, "message": f"Error stopping camera: {e}"}

    def take_photo(self, preview=False, width = None, height = None):
        """Take a photo and return image."""
        if self.camera is None:
            self.logger.error("Camera not initialized")
            return {"success": False, "pil_image": None, "message": "Camera not initialized"}

        if not self.camera_started:
            self.logger.error("Camera not started")
            return {"success": False, "pil_image": None, "message": "Camera not started"}

        if width is None or height is None:
            width = self.sensor_width
            height = self.sensor_height

        # Ensure width and height are even numbers
        if width % 2 != 0:
            width -= 1
        if height % 2 != 0:
            height -= 1

        self.still_config['main']["size"] = (width, height)

        # Check if the camera is started
        # The camera may be stopped after a photo was taken
        if self.camera_is_stopped:
            # Restart the camera in preview mode if it was stopped
            self.camera.configure(self.preview_config)
            self.last_config_was_preview = False
            self.camera.start()
            self.camera_is_stopped = False
            time.sleep(2) # Allow camera to warm up
            self.logger.info("Camera started successfully: %s", not self.camera_is_stopped)

        # Check that the camera did started successfully
        if self.camera_is_stopped:
            self.logger.error("Camera failed to start")
            return {"success": False, "pil_image": None, "message": "Camera failed to start"}

        if preview != self.last_config_was_preview or \
           (self.last_photo_width != width or self.last_photo_height != height):
            # Reconfigure the camera and take the image
            if preview:
                image = self.camera.switch_mode_and_capture_array(self.preview_config, "main")
                self.last_config_was_preview = True
            else:
                image = self.camera.switch_mode_and_capture_array(self.still_config, "main")
        else:
            image = self.camera.capture_array("main")

        self.last_photo_width = width
        self.last_photo_height = height

        if image is not None:
            return {"success": True, "pil_image": Image.fromarray(image),
                    "message": "Image captured successfully"}

        self.logger.warning("Failed to capture image")
        return {"success": False, "pil_image": None, "message": "Failed to capture image"}
