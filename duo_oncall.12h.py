#!/usr/bin/env python3
from collections import defaultdict
import configparser
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


BASE_URL = (
    "https://api.victorops.com/api-public"
)
CACHE_PATH = (
    Path.home() / "Library" / "Caches" / "com.ameba.SwiftBar" /
    "Plugins" / "duo_oncall.12h.py"
)
# CREDS_FILE should be in your home dir with the following format:
#   API_KEY:<your_api_key>
#   API_ID:<your_api_id>
CREDS_FILE = ".victorops"
CONFIG_FILE = ".config.ini"
DT_FMT = "%Y-%m-%dT%H:%M:%S%z"
FMT = " | color=#000001,#FFFFFE md=True"
SCHEDULE_URI = "/v2/team/{team}/oncall/schedule?daysForward=30"
SWIFTBAR_CACHE_PATH = os.environ.get(
    "SWIFTBAR_PLUGIN_CACHE_PATH",
    CACHE_PATH
)
USER_URI = "/v2/user"


class Creds:
    """Class to hold the credentials for the API request."""

    __slots__ = ("api_key", "api_id")

    def __init__(self, api_key: str, api_id: str):
        self.api_key = api_key
        self.api_id = api_id


class UserShift:
    """Class to hold the user shift information."""

    __slots__ = ("start_hour", "end_hour", "shift", "user")

    def __init__(self, start_hour: str, end_hour: str, shift: str, user: str):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.shift = shift
        self.user = user

    def __repr__(self) -> str:
        return f"‣ {self.user} for {self.shift} ({self.start_hour} - {self.end_hour}) {FMT}"


def _construct_headers(creds: Creds) -> dict:
    """Construct the headers for the API request."""
    return {
        "X-VO-Api-Id": creds.api_id,
        "X-VO-Api-Key": creds.api_key,
        "Accept": "application/json",
    }


def _date_to_str(date_obj: datetime, dt_fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format the date string to a more readable format."""

    return date_obj.strftime(dt_fmt)


def _get_creds() -> dict:
    """Get the credentials from the creds file."""
    cred_dict = {}
    file_ = os.path.join(SWIFTBAR_CACHE_PATH, CREDS_FILE)
    with open(file_, encoding="utf-8") as f:
        for line in f.readlines():
            key, value = line.strip().split(":")
            cred_dict[key.lower()] = value
    creds = Creds(**cred_dict)
    return creds


def _get_config() -> configparser.ConfigParser:
    """Get the config file."""

    config = configparser.ConfigParser()
    plugin_path = os.environ.get(
        "SWIFTBAR_PLUGIN_PATH",
        os.path.realpath(__file__)
    )
    plugin_dir = os.path.dirname(plugin_path)
    config.read(os.path.join(plugin_dir, CONFIG_FILE))
    return config


def _date_str_to_dt(date_str: str, dt_fmt: str = DT_FMT) -> datetime:
    """Convert a date string to a datetime object."""

    return datetime.strptime(date_str, dt_fmt)


def _shifts_equal(shifts1: list, shifts2: list) -> bool:
    """Check if two lists of shifts are identical."""
    if len(shifts1) != len(shifts2):
        return False
    
    # Sort shifts by user and shift name for comparison
    sorted1 = sorted(shifts1, key=lambda s: (s.user, s.shift, s.start_hour, s.end_hour))
    sorted2 = sorted(shifts2, key=lambda s: (s.user, s.shift, s.start_hour, s.end_hour))
    
    for s1, s2 in zip(sorted1, sorted2):
        if (s1.user != s2.user or s1.shift != s2.shift or 
            s1.start_hour != s2.start_hour or s1.end_hour != s2.end_hour):
            return False
    
    return True


def _group_consecutive_dates(shift_collection: dict) -> list:
    """Group consecutive dates with identical shift assignments into date ranges.
    
    Returns a list of tuples: ((start_date, end_date), [shifts])
    """
    if not shift_collection:
        return []
    
    sorted_dates = sorted(shift_collection.keys())
    date_ranges = []
    
    current_start = sorted_dates[0]
    current_end = sorted_dates[0]
    current_shifts = shift_collection[sorted_dates[0]]
    
    for i in range(1, len(sorted_dates)):
        date = sorted_dates[i]
        shifts = shift_collection[date]
        
        # Check if this date is consecutive and has the same shifts
        if (date == current_end + timedelta(days=1) and 
            _shifts_equal(shifts, current_shifts)):
            # Extend the current range
            current_end = date
        else:
            # Save the current range and start a new one
            date_ranges.append(((current_start, current_end), current_shifts))
            current_start = date
            current_end = date
            current_shifts = shifts
    
    # Don't forget the last range
    date_ranges.append(((current_start, current_end), current_shifts))
    
    return date_ranges


def display_schedules(user_display: str, data: dict, **users) -> None:
    """Display the on-call schedules in a readable format."""
    print(f'**Team: {data["team"]["name"]}** {FMT}')
    shift_collection = defaultdict(list)
    for schedule in data["schedules"]:
        print(f"*Policy: {schedule['policy']['name']}* {FMT}")
        sched = schedule["schedule"]
        overrides = schedule.get("overrides", [])
        for s in sched:
            for r in s["rolls"]:
                start = _date_str_to_dt(r["start"])
                end = _date_str_to_dt(r["end"])
                days = (
                    start + timedelta(days=x) for x in range(
                        0, (end - start).days + 1
                    )
                )
                for dt in days:
                    shift_collection[dt.date()].append(
                        UserShift(
                            _date_to_str(start, "%H:%M"),
                            _date_to_str(end, "%H:%M"),
                            s["shiftName"],
                            users[r["onCallUser"]["username"]][user_display]
                        )
                    )
        
        # Group consecutive dates with identical shifts
        date_ranges = _group_consecutive_dates(shift_collection)
        
        for date_range, shifts in date_ranges:
            if date_range[0] == date_range[1]:
                # Single day
                print(f"**{date_range[0]}** {FMT}")
            else:
                # Date range
                print(f"**{date_range[0]} - {date_range[1]}** {FMT}")
            for shift in shifts:
                print(shift)
        # print_overrides(overrides)
        # sep()


def get_oncall_schedule(team: str, creds: Creds) -> dict:
    """Get the on-call schedule for a given team."""
    headers = _construct_headers(creds)
    url = f"{BASE_URL}{SCHEDULE_URI.format(team=team)}"
    req = Request(url, headers=headers)
    with urlopen(req) as response:
        data = response.read().decode("utf-8")
        json_data = json.loads(data)
    return json_data


def get_users(creds: Creds) -> dict:
    """Get the users from the API."""
    headers = _construct_headers(creds)
    url = f"{BASE_URL}{USER_URI}"
    req = Request(url, headers=headers)
    with urlopen(req) as response:
        data = response.read().decode("utf-8")
        json_data = json.loads(data)
    return {user["username"]: user for user in json_data["users"]}


def print_overrides(overrides: list) -> None:
    """Print the overrides for the on-call schedule."""
    if not overrides:
        return
    print("Overrides:")
    for o in overrides:
        start = _date_str_to_dt(o["start"])
        end = _date_str_to_dt(o["end"])
        start_str = _date_to_str(start)
        end_str = _date_to_str(end)
        print(
            f"**{o['overrideOnCallUser']['username']}** for "
            f"**{o['origOnCallUser']['username']}**: Start "
            f"{start_str}, End {end_str} {FMT}"
        )


def sep():
    """Print a separator line."""
    print("---")


def main():
    """Main function to run the script."""

    conf = _get_config()
    try:
        display_conf = conf["display_conf"]
    except KeyError:
        display_conf = {}
    print("DuoOnCall")
    sep()
    creds = _get_creds()
    users = get_users(creds)
    for team in conf["teams"].values():
        data = get_oncall_schedule(team, creds)
        display_schedules(
            display_conf.get("user_display", "displayName"),
            data,
            **users
        )
    print("Refresh | refresh=true")
    sep()


# metadata
# <bitbar.title>Duo OnCall</bitbar.title>
# <bitbar.version>v1.1</bitbar.version>
# <bitbar.author>Rory Scott</bitbar.author>
# <bitbar.author.github>rorynscott</bitbar.author.github>
# <bitbar.desc>Plugin shows who is on call.</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>http://url-to-about.com/</bitbar.abouturl>
# <bitbar.droptypes>Supported UTI's for dropping things on menu bar</bitbar.droptypes>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>


if __name__ == "__main__":
    main()
