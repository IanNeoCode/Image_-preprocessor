import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RectangleSelector
import easygui

# Function to preprocess the image
def preprocess_image(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

# Function to crop the image
def crop_image(image, crop_coords):
    x1, y1, x2, y2 = map(int, crop_coords)
    cropped = image[y1:y2, x1:x2]
    return cropped

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
        preprocessed_display = cv2.cvtColor(preprocessed_image, cv2.COLOR_GRAY2RGB)

        # Update the Matplotlib plot
        img_plot.set_data(preprocessed_display)
        ax.set_title("Preprocessed Image (Cropped)")
        fig.canvas.draw()

        # Save the preprocessed cropped image
        output_path = "preprocessed_cropped_image.jpg"
        cv2.imwrite(output_path, preprocessed_image)
        print(f"Preprocessed cropped image saved at: {output_path}")

    # Add a button to trigger preprocessing
    ax_preprocess = plt.axes([0.4, 0.05, 0.2, 0.075])
    btn_preprocess = Button(ax_preprocess, "Preprocess")
    btn_preprocess.on_clicked(on_preprocess)

    # Show the Matplotlib window
    plt.show()

if __name__ == "__main__":
    # Open a file dialog to select the image
    input_image_path = easygui.fileopenbox(title="Select an Image", filetypes=["*.jpg", "*.jpeg", "*.png", "*.bmp"])

    if input_image_path:
        display_images(input_image_path)
    else:
        print("No file selected.")
