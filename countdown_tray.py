from PIL import Image, ImageDraw, ImageFont
from pystray import Icon, MenuItem, Menu
from datetime import datetime, timedelta
from cronsim import CronSim
from typing import Iterable, Optional, Union
import argparse
import re
import threading


class CountdownTray:
    def __init__(self, due: datetime, repeat_rule: Optional[Union[Iterable[datetime], timedelta]]):
        self.due = due
        self.stopped = threading.Event()
        self.initial_diff = int((self.due - datetime.now()).total_seconds() // 60)
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
    def create_icon(number: Union[float, int]):
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
        while not self.stopped.is_set():
            diff = self.due - datetime.now()
            diff_seconds = int(diff.total_seconds())
            diff_minutes = diff_seconds // 60
            diff_hours = diff_minutes / 60
            diff_days = int(diff_hours // 24)
            print(diff)

            # Reached due date. Either exit or repeat
            if diff_seconds <= 0:
                if self.repeat_rule:
                    self.due = next(self.repeat_rule)
                    self.initial_diff = int((self.due - datetime.now()).total_seconds() // 60)
                    continue
                else:
                    self.exit_app()
                    break

            if diff_days > 0:
                diff = diff_days
            elif diff_hours > 9.9:
                diff = int(round(diff_hours))
            elif diff_minutes < 100 and self.initial_diff < 100:
                # If timer started with less than 100 minutes, show minutes
                diff = diff_minutes
            elif diff_hours > 1:
                diff = round(diff_hours, 1)
            else:
                diff = diff_minutes

            self.traylet.icon = self.create_icon(diff)
            self.stopped.wait(timeout=60)  # Sleep for 1 minute

    def exit_app(self):
        self.stopped.set()
        self.traylet.stop()

def parse_timedelta(time_str: str):
    """Parses a string formatted as '?h?m' in either order or one"""
    hours = 0
    minutes = 0
    minute_match = re.search(r"(\d+)m", time_str)
    hour_match = re.search(r"(\d+)h", time_str)

    if minute_match:
        minutes = int(minute_match.group(1))
    if hour_match:
        hours = int(hour_match.group(1))
    if not (hours or minutes):
        raise ValueError("Invalid timedelta format. Must contain 'h' or 'm'.")

    return timedelta(hours=hours, minutes=minutes)

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
            try:
                # Parse like "1-5-2025"
                return datetime.strptime(datetime_string, "%m-%d-%Y")
            except ValueError:
                # Parse like "?h?m" from now
                return datetime.now() + parse_timedelta(datetime_string)

def parse_args():
    parser = argparse.ArgumentParser(description="Create a system tray icon that counts down.")
    parser.add_argument(
        "ending_datetime",
        type=parse_datetime,
        help="Datetime input in 'M-D-YYYY (H:M) (am/pm)' format, 'now', or '?h?m' from now."
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
