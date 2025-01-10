# countdown-tray

Download from [pyPI](https://pypi.org/project/countdown-tray/): `pip install countdown-tray`

Create a system tray icon that counts down to a specified date and time, optionally repeating.

![countdown-tray](https://raw.githubusercontent.com/funblaster22/countdown-tray/refs/heads/main/docs/demo.png)

In this example, it is counting down hours to 7pm. The unit will change depending on the time remaining.

- \> 1 day: days
- \> 10 hour: hours rounded to whole hours
- \> 1 hour: hours rounded to 0.5 hour
- < 1 hour: minutes

```
usage: countdown_tray.py [-h] ending_datetime [repeat_cron]

Create a system tray icon that counts down.

positional arguments:
  ending_datetime  Datetime input in 'M-D-YYYY H:M (am/pm)' format or 'now'.
  repeat_cron      Optional cron repeat pattern (e.g., '*/5 * * * *').

options:
  -h, --help       show this help message and exit
```
