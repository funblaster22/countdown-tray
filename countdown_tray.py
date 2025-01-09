import time
from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, MenuItem, Menu
from datetime import datetime, timedelta
from cronsim import CronSim
from typing import Iterable, Optional, Union
import argparse


class CountdownTray:
    def __init__(self, due: datetime, repeat_rule: Optional[Union[Iterable[datetime], timedelta]]):
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
        while True:
            diff = self.due - datetime.now()
            diff_seconds = diff.total_seconds()
            diff_minutes = diff_seconds // 60
            diff_hours = diff_minutes / 60
            diff_days = diff_hours // 24
            print(diff)

            # Reached due date. Either exit or repeat
            if diff_seconds <= 0:
                if self.repeat_rule:
                    self.due = next(self.repeat_rule)
                    continue
                else:
                    self.exit_app()
                    break

            if diff_days > 0:
                self.traylet.icon = self.create_icon(diff_days)
                time.sleep(60 * 60 * 24)  # Sleep for a day
            elif diff_hours > 10:
                self.traylet.icon = self.create_icon(round(diff_hours))
                time.sleep(60 * 60)  # Sleep for an hour
            elif diff_hours > 1:
                self.traylet.icon = self.create_icon(round(diff_hours, 1))
                time.sleep(60 * 60 * 0.1)  # Sleep for 0.1 hours
            else:
                self.traylet.icon = self.create_icon(round(diff_hours, 1))
                time.sleep(60)  # Sleep for 1 minute

    def exit_app(self):
        self.running = False
        self.traylet.stop()

def parse_datetime(datetime_string: str):
    if datetime_string.lower() == "now":
        return datetime.now()
    try:
        # Parse like "1-5-2025 10:30 am"
        return datetime.strptime(datetime_string, "%m-%d-%Y %I:%M %p")
    except ValueError:
        try:
            # Parse like "1-5-2025 19:30"
            return datetime.strptime(datetime_string, "%m-%d-%Y %H:%M")
        except ValueError:
            # Parse like "1-5-2025"
            return datetime.strptime(datetime_string, "%m-%d-%Y")

def parse_args():
    parser = argparse.ArgumentParser(description="Create a system tray icon that counts down.")
    parser.add_argument(
        "ending_datetime",
        type=parse_datetime,
        help="Datetime input in 'M-D-YYYY H:M (am/pm)' format or 'now'."
    )
    parser.add_argument(
        "repeat_cron",
        nargs="?",
        default=None,
        help="Optional cron repeat pattern (e.g., '*/5 * * * *')."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cron_iter: Optional[Iterable] = None
    if args.repeat_cron:
        cron_iter = CronSim(args.repeat_cron, args.ending_datetime)
    return CountdownTray(args.ending_datetime, cron_iter)


if __name__ == "__main__":
    main()
