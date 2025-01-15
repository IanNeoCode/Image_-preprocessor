import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RectangleSelector
from PIL import Image
import easygui
import tkinter as tk
from tkinter import simpledialog

# Default preprocessing settings
settings = {
    "gaussian_blur": 5,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": 8,
}

# Function to preprocess the image
def preprocess_image(image):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur for noise reduction
    blurred_image = cv2.GaussianBlur(gray_image, (settings["gaussian_blur"], settings["gaussian_blur"]), 0)

    # Enhance contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=settings["clahe_clip_limit"], tileGridSize=(settings["clahe_tile_grid_size"], settings["clahe_tile_grid_size"]))
    enhanced_image = clahe.apply(blurred_image)

    return enhanced_image


# Function to crop the image
def crop_image(image, crop_coords):
    x1, y1, x2, y2 = map(int, crop_coords)
    cropped = image[y1:y2, x1:x2]
    return cropped


# Function to open the settings page
def open_settings():
    def save_settings():
        try:
            # Update global settings
            settings["gaussian_blur"] = int(blur_var.get())
            settings["clahe_clip_limit"] = float(clip_limit_var.get())
            settings["clahe_tile_grid_size"] = int(tile_grid_var.get())
            print("Settings updated:", settings)
            settings_window.destroy()
        except ValueError:
            print("Invalid input. Please check your settings.")

    # Create a new Tkinter window for settings
    settings_window = tk.Tk()
    settings_window.title("Preprocessing Settings")

    # Gaussian Blur setting
    tk.Label(settings_window, text="Gaussian Blur Kernel Size (odd number):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    blur_var = tk.StringVar(value=str(settings["gaussian_blur"]))
    tk.Entry(settings_window, textvariable=blur_var).grid(row=0, column=1, padx=10, pady=5)

    # CLAHE Clip Limit setting
    tk.Label(settings_window, text="CLAHE Clip Limit:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    clip_limit_var = tk.StringVar(value=str(settings["clahe_clip_limit"]))
    tk.Entry(settings_window, textvariable=clip_limit_var).grid(row=1, column=1, padx=10, pady=5)

    # CLAHE Tile Grid Size setting
    tk.Label(settings_window, text="CLAHE Tile Grid Size:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
    tile_grid_var = tk.StringVar(value=str(settings["clahe_tile_grid_size"]))
    tk.Entry(settings_window, textvariable=tile_grid_var).grid(row=2, column=1, padx=10, pady=5)

    # Save button
    tk.Button(settings_window, text="Save", command=save_settings).grid(row=3, column=0, columnspan=2, pady=10)

    settings_window.mainloop()


# Function to display the original and preprocessed images
def display_images(image_path):
    # Load the original image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or unable to read.")

    # Initialize cropping coordinates
    crop_coords = [0, 0, image.shape[1], image.shape[0]]

    # Create a Matplotlib figure
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.3)  # Adjust space for the buttons

    # Display the original image
    image_display = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_plot = ax.imshow(image_display)
    ax.set_title("Original Image")
    ax.axis('off')

    # Rectangle selector for cropping
    def on_select(eclick, erelease):
        nonlocal crop_coords
        crop_coords = [eclick.xdata, eclick.ydata, erelease.xdata, erelease.ydata]
        print(f"Crop coordinates: {crop_coords}")

    rect_selector = RectangleSelector(
        ax, on_select, interactive=True,
        button=[1], minspanx=5, minspany=5, spancoords='pixels'
    )

    # Button click event to preprocess the image
    def on_preprocess(event):
        # Apply preprocessing to the cropped region
        cropped = crop_image(image, crop_coords)
        preprocessed_image = preprocess_image(cropped)

        # Update the Matplotlib plot for display
        preprocessed_display = cv2.cvtColor(preprocessed_image, cv2.COLOR_GRAY2RGB)
        img_plot.set_data(preprocessed_display)
        ax.set_title("Preprocessed Image (Cropped)")
        fig.canvas.draw()

    # Button click event to save the preprocessed image
    def on_save(event):
        # Open a file dialog to choose where to save the image
        save_fig_path = easygui.filesavebox(title="Save Image As", default="preprocessed_cropped_image.jpg",
                                            filetypes=["*.jpg", "*.png"])
        if save_fig_path:
            # Apply preprocessing to the cropped region
            cropped = crop_image(image, crop_coords)
            preprocessed_image = preprocess_image(cropped)

            # Save the preprocessed cropped image using Pillow
            pil_image = Image.fromarray(preprocessed_image)
            pil_image.save(save_fig_path)

            print(f"Preprocessed cropped image saved at: {save_fig_path}")

    # Add a button to trigger preprocessing
    ax_preprocess = plt.axes([0.2, 0.05, 0.2, 0.075])
    btn_preprocess = Button(ax_preprocess, "Preprocess")
    btn_preprocess.on_clicked(on_preprocess)

    # Add a button to open settings
    ax_settings = plt.axes([0.5, 0.05, 0.2, 0.075])
    btn_settings = Button(ax_settings, "Settings")
    btn_settings.on_clicked(lambda event: open_settings())

    # Add a button to save the preprocessed image
    ax_save = plt.axes([0.8, 0.05, 0.2, 0.075])
    btn_save = Button(ax_save, "Save Image")
    btn_save.on_clicked(on_save)

    # Show the Matplotlib window
    plt.show()


if __name__ == "__main__":
    # Open a file dialog to select the image
    input_image_path = easygui.fileopenbox(title="Select an Image", filetypes=["*.jpg", "*.jpeg", "*.png", "*.bmp"])

    if input_image_path:
        display_images(input_image_path)
    else:
        print("No file selected.")
