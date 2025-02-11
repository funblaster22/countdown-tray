# countdown-tray

Download from [pyPI](https://pypi.org/project/countdown-tray/): `pip install countdown-tray`

Create a system tray icon that counts down to a specified date and time, optionally repeating.

![countdown-tray](https://raw.githubusercontent.com/funblaster22/countdown-tray/refs/heads/main/docs/demo.png)

In this example, it is counting down hours to 7pm. The unit will change depending on the time remaining.

- \> 1 day: days
- \> 10 hour: hours rounded to whole hours
- \< 100 minutes IF timer started with less than 100 minutes remaining: minutes
- \> 1 hour: hours rounded to 0.1 hour
- < 1 hour: minutes

```
usage: countdown_tray.py [-h] ending_time [ending_date] [repeat_cron]

Create a system tray icon that counts down.

positional arguments:
  ending_time  Ending time in 'H:M(am/pm)' format, 'now', or '(?h)(?m)' from now. Parentheses denote optional.
  ending_date  Ending time in 'M-D-YYYY' format or 'today'. Defaults to 'today'. Ignored if using `?h?m` ending time.
  repeat_cron  Optional cron repeat pattern (e.g., '*/5 * * * *').

options:
  -h, --help   show this help message and exit
```
