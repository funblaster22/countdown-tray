import random
import time
from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, MenuItem, Menu
from datetime import datetime, timedelta
from cronsim import CronSim
from typing import Iterable, Optional
import argparse


class CountdownTray:
    def __init__(self, due: datetime, repeat_rule: Optional[Iterable | timedelta]):
        self.due = due
        self.running = True
        if isinstance(repeat_rule, Iterable):
            self.repeat_rule = repeat_rule
        elif isinstance(repeat_rule, timedelta):
            self.repeat_rule = self.timedelta_iterator(repeat_rule)
        else:
            self.repeat_rule = None

        menu = Menu(MenuItem("Exit", self.exit_app))
        self.traylet = Icon("Random Number", self.create_icon(0), menu=menu)

        # Run the system tray icon
        self.traylet.run(setup=self.update_icon)

    def timedelta_iterator(self, delta: timedelta):
        """Convert a timedelta to iterator that yields the next due time in constant increments"""
        while True:
            yield self.due + delta
    
    @staticmethod
    def create_icon(number: float):
        """create an icon with the provided number"""
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

    def update_icon(self, _: Icon):
        """Update the icon with the new time remaining"""
        self.traylet.visible = True
        while self.running:
            random_number = random.randint(1, 10)
            self.traylet.icon = self.create_icon(random_number)
            time.sleep(1)

    def exit_app(self):
        self.running = False
        self.traylet.stop()

def parse_datetime(datetime_string: str):
    try:
        # Parse like "1-5-2025 10:30 am"
        return datetime.strptime(datetime_string, "%d-%m-%Y %I:%M %p")
    except ValueError:
        try:
            # Parse like "1-5-2025 19:30"
            return datetime.strptime(datetime_string, "%d-%m-%Y %H:%M")
        except ValueError:
            # Parse like "1-5-2025"
            return datetime.strptime(datetime_string, "%d-%m-%Y")

def parse_args():
    parser = argparse.ArgumentParser(description="Create a system tray icon that counts down.")
    parser.add_argument(
        "ending_datetime",
        type=parse_datetime,
        help="Datetime input in 'M-D-YYYY H:M (am/pm)' format."
    )
    parser.add_argument(
        "repeat_cron",
        nargs="?",
        default=None,
        help="Optional cron repeat pattern (e.g., '*/5 * * * *')."
    )
    return parser.parse_args(["1-6-2024 7:00 pm", "0 19 * * *"])

if __name__ == "__main__":
    args = parse_args()
    cron_iter: Optional[Iterable] = None
    if args.repeat_cron:
        cron_iter = CronSim(args.repeat_cron, args.ending_datetime)
    t = CountdownTray(args.ending_datetime, cron_iter)
