import random
import time
from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, MenuItem, Menu
import threading

# Function to create an icon with a random number
def create_icon(number):
    width, height = 64, 64  # Icon size
    image = Image.new('RGBA', (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load a font (system default or custom TTF)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Get text size and position it in the center
    text = str(number)
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]  # Use textbbox for size
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    draw.text((text_x, text_y), text, fill="black", font=font)
    return image

# Function to update the icon
def update_icon(icon):
    while True:
        random_number = random.randint(1, 10)
        icon.icon = create_icon(random_number)
        time.sleep(1)

# Function to exit the application
def exit_app(icon, item):
    icon.stop()

# Main function
def main():
    menu = Menu(MenuItem("Exit", exit_app))
    icon = Icon("Random Number", create_icon(1), menu=menu)

    # Start the icon update thread
    threading.Thread(target=update_icon, args=(icon,), daemon=True).start()

    # Run the system tray icon
    icon.run()

if __name__ == "__main__":
    main()
