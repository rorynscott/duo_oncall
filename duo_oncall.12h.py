#!/usr/bin/env python3
from datetime import datetime
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


BASE_URL = (
    "https://api.victorops.com/api-public/v2/team/{team}/oncall/schedule?daysForward=30"
)
CACHE_PATH = (
    Path.home() / "Library" / "Caches" / "com.ameba.SwiftBar" /
    "Plugins" / "duo_oncall.12h.py"
)
# CREDS_FILE should be in your home dir with the following format:
#   API_KEY:<your_api_key>
#   API_ID:<your_api_id>
CREDS_FILE = ".victorops"
FMT = " | color=#000001,#FFFFFE md=True"
SWIFTBAR_CACHE_PATH = os.environ.get(
    "SWIFTBAR_PLUGIN_CACHE_PATH",
    CACHE_PATH
)
TEAM_MAP = {
    "admin-user-management": "team-jAyTiBSiiyygnKJL",
    "Applications": "team-DehKy1LuixchxEbi",
    "Platform-Services": "team-1z9FXy224k5xWjrM",
}


class Creds:
    """Class to hold the credentials for the API request."""

    __slots__ = ("api_key", "api_id")

    def __init__(self, api_key: str, api_id: str):
        self.api_key = api_key
        self.api_id = api_id


def _construct_headers(creds: Creds) -> dict:
    """Construct the headers for the API request."""
    return {
        "X-VO-Api-Id": creds.api_id,
        "X-VO-Api-Key": creds.api_key,
        "Accept": "application/json",
    }


def _format_date(date_str: str) -> str:
    """Format the date string to a more readable format."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
    return date_obj.strftime("%Y-%m-%d %H:%M")


def _get_creds() -> dict:
    """Get the credentials from the creds file."""
    cred_dict = {}
    file_ = os.path.join(
        SWIFTBAR_CACHE_PATH,
        CREDS_FILE
    )
    with open(file_, encoding="utf-8") as f:
        for line in f.readlines():
            key, value = line.strip().split(":")
            cred_dict[key.lower()] = value
    creds = Creds(**cred_dict)
    return creds


def display_schedules(data: dict) -> None:
    """Display the on-call schedules in a readable format."""
    print(f'**Team: {data["team"]["name"]}** {FMT}')
    for schedule in data["schedules"]:
        print(f"*Policy Name: {schedule['policy']['name']}* {FMT}")
        sched = schedule["schedule"]
        overrides = schedule.get("overrides", [])
        for s in sched:
            for r in s["rolls"]:
                start_dt = _format_date(r["start"])
                end_dt = _format_date(r["end"])
                print(
                    f"**{r['onCallUser']['username']}**: Start {start_dt}, End {end_dt} {FMT}"
                )
        if overrides:
            print("Overrides:")
            for o in overrides:
                start_dt = _format_date(o["start"])
                end_dt = _format_date(o["end"])
                print(
                    f"**{o['overrideOnCallUser']['username']}** for "
                    f"**{o['origOnCallUser']['username']}**: Start "
                    f"{start_dt}, End {end_dt} {FMT}"
                )
        sep()


def get_oncall_schedule(team: str) -> dict:
    """Get the on-call schedule for a given team."""
    creds = _get_creds()
    headers = _construct_headers(creds)
    url = BASE_URL.format(team=team)
    req = Request(url, headers=headers)
    with urlopen(req) as response:
        data = response.read().decode("utf-8")
        json_data = json.loads(data)
    return json_data


def sep():
    """Print a separator line."""
    print("---")


def main():
    """Main function to run the script."""

    print("DuoOnCall")
    sep()
    for team in TEAM_MAP.values():
        data = get_oncall_schedule(team)
        display_schedules(data)
    print("Refresh | refresh=true")
    sep()


# metadata
# <bitbar.title>Duo OnCall</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
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
