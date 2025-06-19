"""
View Class for Booth Management System.
The User Interface (UI) for the Photobooth application.
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, Canvas, Button, messagebox  # pylint: disable=W0611
from PIL import Image, ImageTk, ImageSequence # type: ignore # pylint: disable=E0401

import constants

class BoothView(tk.Tk):
    """View class for managing the booth application."""

    def __init__(self, controller):
        """Initialize the BoothModel."""
        self.logger = logging.getLogger(__name__)
        super().__init__()

        self.controller = controller
        # self.update_idletasks()
        self.update()
        self.attributes("-fullscreen", True)  # Set the window to fullscreen
        # self.update_idletasks()
        self.update()
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.configure(bg="black",
                            width=self.screen_width,
                            height=self.screen_height)

        # Canvas for camera preview
        self.canvas = Canvas(self, width=self.screen_width,
                             height=self.screen_height, bg='black',
                             highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        ## If keyboard is present, pressing <Ctrl>+Q will quit the application
        self.bind("<Control-q>", lambda event: self.exit_application())
        self.bind("<Escape>", lambda event: self.exit_application())

        self._make_buttons()
        self.preview_tkimage = None  # Initialize attribute to avoid linter error
        self._make_preview_image()
        self.show_buttons()

        # Countdown
        self.countdown_index = -1
        self.countdown_image = None
        self.countdown_tkimages = []  # List to hold countdown images
        self._load_countdown_images()

        # Status label
        self._make_status_label()

        # Polling interval for the canvas update
        self.poll_interval = 33  # milliseconds
        self.suspend_poll = False  # Flag to suspend polling
        self.after(250, self.run_poll) # Should be last line in __init__

    def main(self):
        """Main function to run the booth application."""
        if not self.controller.camera.camera_started:
            self.logger.error(
                "Camera not started. Please check the camera connection and try again.")
            self.logger.info("Exiting application due to camera error.")
            self.exit_application_error(
                "Camera not started. Please check the camera connection and try again.")
        self.mainloop()

    def _load_countdown_images(self):
        """Load countdown images."""
        # Load countdown images

        self.countdown_tkimages = []
        for img in constants.COUNTDOWN_OVERLAY_IMAGES:
            self.countdown_tkimages.append(ImageTk.PhotoImage(Image.open(img)))

    def _make_buttons(self):
        """Create the buttons for the booth application."""
        self.buttons_bottom = []
        self.buttons_left = []
        self.buttons_right = []
        self.button_tkimgs_bottom = []
        self.button_tkimgs_left = []
        self.button_tkimgs_right = []
        for button in constants.BUTTONS:
            img = Image.open(button["icon"])
            tkimg = ImageTk.PhotoImage(img)
            btn = tk.Button(
                self.canvas,
                image=tkimg,
                width=img.width,
                height=img.height,
                bg='black',
                activebackground='white',
                command=lambda b=button: self.controller.handle_button_click(b)
            )

            if button["name"] == constants.BUTTON_PRINT_PHOTO["name"] and \
               not self.controller.configuration.enable_print:
                continue  # Skip this button if printing is disabled
            if button["name"] == constants.BUTTON_EMAIL_PHOTO["name"] and \
               not self.controller.configuration.enable_email:
                continue  # Skip this button if email is disabled
            if button["name"] == constants.BUTTON_EFFECTS["name"] and \
               not self.controller.configuration.enable_effects:
                continue  # Skip this button if effects are disabled

            if button["location"] == "bottom":
                self.buttons_bottom.append(btn)
                self.button_tkimgs_bottom.append(tkimg)
            elif button["location"] == "left":
                self.buttons_left.append(btn)
                self.button_tkimgs_left.append(tkimg)
            elif button["location"] == "right":
                self.buttons_right.append(btn)
                self.button_tkimgs_right.append(tkimg)

    def _make_preview_image(self):
        """Create the preview image for the camera feed."""
        self.preview_tkimage = ImageTk.PhotoImage(Image.new("RGB",
                                                            (640, 480),
                                                            color="black"))
        self.preview_image = self.canvas.create_image(self.screen_width // 2,
                                                      self.screen_height // 2,
                                                      image=self.preview_tkimage,
                                                      anchor='center')

    def _make_status_label(self):
        """Create status label on the canvas"""
        # Placeholder for status label functionality
        self.status_label = tk.Label(self.canvas, text="", justify="center", bg='blue', fg='white')
        self.update_status("Status: Ready")

    def exit_application(self):
        """Exit the application."""
        if tk.messagebox.askyesno("Confirm Exit", "Are you sure you want to quit?"):
            self.controller.handle_exit()

    def exit_application_error(self,
                               message: str = "An error occurred.\nQuitting the application."):
        """Exit the application."""
        if tk.messagebox.showerror("Error", message):
            self.controller.handle_exit()

    def hide_buttons(self):
        """Hide all buttons on the canvas."""
        # Hide the buttons by placing them off-screen
        for button in self.buttons_bottom:
            button.place_forget()
        for button in self.buttons_left:
            button.place_forget()
        for button in self.buttons_right:
            button.place_forget()
        self.update()

    def run_poll(self):
        """
        Run a polling loop to update the canvas.
        This method can be used to update the canvas periodically.
        """
        if not self.suspend_poll:
            self.controller.handle_poll_timer()

        try:
            # Only schedule the next poll if the window is still valid
            if self.winfo_exists():
                self.after(self.poll_interval, self.run_poll)
            else:
                return
        except tk.TclError:
            # Window has been destroyed, stop polling
            return

    def show_animation(self, gif_path):
        """
        Show an animation on the canvas.
        The animation is expected to be a valid file path.
        """
        if not os.path.exists(gif_path) or os.path.splitext(gif_path)[1].lower() != ".gif":
            self.logger.error("Animation file %s does not exist.", gif_path)
            self.update_status("Animation file not found", level="error")
            return

        # Get file information
        annimation = Image.open(gif_path)
        # Keep frames as PIL Images so we can resize them
        frames = [frame.copy() for frame in ImageSequence.Iterator(annimation)]

        if not frames or len(frames) == 0:
            self.logger.error("No frames found in the animation file %s.", gif_path)
            self.update_status("No frames found in animation", level="error")
            return

        self.suspend_poll = True  # Suspend polling while showing animation
        self._show_animation_frames(frames, 100)  # Show the animation frames
        self.suspend_poll = False  # Restart polling after showing animation

    def _show_animation_frames(self, frames, delay=100):
        """Show the frames of an animation on the canvas."""
        for frame in frames:
            # Update the canvas with the new frame
            frame.thumbnail((800, 480), Image.ANTIALIAS)
            self.update_preview_image(frame)
            self.canvas.update()
            self.after(delay)

    def show_buttons(self):
        """Show all buttons on the canvas."""
        # Place the buttons along the bottom row
        # Calculate padding for buttons in bottom row
        x_offset = 0  # Offset for horizontal alignment of buttons
        y_offset = 0  # Offset for vertical alignment of buttons
        padding_x = self.screen_width
        for button in self.buttons_bottom:
            padding_x -= button.winfo_reqwidth()

        padding_x = (padding_x - x_offset) // (len(self.buttons_bottom) - 1)
        x = 0
        bottom_button_row_height = 0
        # Place the buttons in the bottom row
        for button in self.buttons_bottom:
            y = (self.screen_height - 1) - button.winfo_reqheight() - y_offset
            button.place(x=x, y=y)
            x += button.winfo_reqwidth() + padding_x
            bottom_button_row_height = max(bottom_button_row_height, button.winfo_reqheight())
            self.update()

        # Place the buttons in the left column
        if len(self.buttons_left) > 0:
            # Calculate padding for buttons
            padding_y = self.screen_height - bottom_button_row_height
            for button in self.buttons_left:
                padding_y -= button.winfo_reqheight()

            padding_y = (padding_y - y_offset) // (len(self.buttons_left))
            x = 0
            y = 0
            # Place the buttons
            for button in self.buttons_left:
                button.place(x=x, y=y)
                y += button.winfo_reqheight() + padding_y
                self.update()

        # Place the buttons in the right column
        if len(self.buttons_right) > 0:
            # Calculate padding for buttons
            padding_y = self.screen_height - bottom_button_row_height
            for button in self.buttons_right:
                padding_y -= button.winfo_reqheight()

            padding_y = (padding_y - y_offset) // (len(self.buttons_right))
            x = 0
            y = 0
            # Place the buttons
            for button in self.buttons_right:
                x = self.screen_width - button.winfo_reqwidth()
                button.place(x=x, y=y)
                y += button.winfo_reqheight() + padding_y
                self.update()
        # Update the canvas to reflect the changes
        self.update()

    def show_countdown(self, countdown_index = None):
        """
        Show the countdown overlay on the canvas.
        Return True if the countdown image is shown, False if it is not.
        To start the countdown, call this method with a countdown_index value.
        To start the countdown from the last image, pass a large value (e.g., 99).
        If countdown_index is None, it will decrement the countdown index by 1.
        """
        # Decrement the countdown index if not specified
        if countdown_index is None:
            self.countdown_index = self.countdown_index - 1
        else:
            self.countdown_index = countdown_index

        if self.countdown_index < 0:
            if self.countdown_image is not None:
                self.canvas.delete(self.countdown_image)
                self.countdown_image = None
                self.countdown_index = -1
            return False

        # Passing a large value to show_countdown will reset the countdown index to last image
        self.countdown_index = min(self.countdown_index, len(self.countdown_tkimages) - 1)

        if self.countdown_image is None:
            self.countdown_image = self.canvas.create_image(
                self.screen_width // 2, self.screen_height // 2,
                image=self.countdown_tkimages[self.countdown_index],
                anchor="center"
            )
        else:
            self.canvas.itemconfig(self.countdown_image,
                                   image=self.countdown_tkimages[self.countdown_index])

        self.canvas.update()
        return True

    def show_image(self, filename):
        """
        Show an image on the canvas.
        The image is expected to be a valid file path.
        """
        try:
            image = Image.open(filename)
            image.thumbnail((800, 480), Image.ANTIALIAS)
            self.update_preview_image(image)
        except Exception as e: # pylint: disable=W0718
            self.logger.error("Failed to load image %s: %s", filename, e)
            self.update_status("Failed to load image", level="error")

    def update_preview_image(self, image):
        """Update the preview image on the canvas."""
        # Convert the image to a PhotoImage
        if isinstance(image, Image.Image):
            self.preview_tkimage = ImageTk.PhotoImage(image)
        else:
            raise ValueError("Expected an instance of PIL.Image.Image")
        # Update the canvas with the new image
        self.canvas.itemconfig(self.preview_image, image=self.preview_tkimage)
        self.canvas.update()

    def update_status(self, message="", level="info"):
        """Update the status label with a message and level."""
        if hasattr(self, "status_label"):
            self.status_label.config(text=message)

            if not message:
                self.status_label.place_forget()
            else:
                self.status_label.place(relx=0.5, rely=0.0, anchor="n")

                # Update the background and foreground colors based on the level
                match level.strip().lower():
                    case "info":
                        self.status_label.config(bg='blue', fg='white')
                    case "warning":
                        self.status_label.config(bg='yellow', fg='black')
                    case "error":
                        self.status_label.config(bg='red', fg='white')
                    case _:
                        self.status_label.config(bg='purple', fg='white')
