# Installation Instructions

1. You can install Python 3 or use the executable in `dist/duo_oncall.12h/duo_oncall.12h`
1. Install SwiftBar with "brew install swiftbar" or from https://github.com/swiftbar/SwiftBar/releases/latest
2. Start SwiftBar and it will ask you where you want to store plugins. I used `Documents/swiftbar_plugins`.
3. Install in plugin directory `git clone https://gist.github.com/84068616a04782930109b5ad630a259d.git -- ~/Documents/swiftbar_plugins/duo_calendar` or just download https://gist.github.com/rorynscott/84068616a04782930109b5ad630a259d/raw/duo_calendar.12h.py.
4. Restart SwiftBar
5. In the menu choose SwiftBar -> Preferences -> Launch at Login


# Updates
To update run git pull in the directory you installed the plugin: `cd ~/Documents/swiftbar_plugins/duo_oncall && git pull` or download the latest version from https://gist.github.com/rorynscott/84068616a04782930109b5ad630a259d/raw/duo_calendar.12h.py.

# Something went wrong
* Command-r when the SwiftBar menu is selected to refresh plugins.
* Option-click the menu for more options.
* Make sure the plugin is executable: `chmod +x ~/Documents/swiftbar_plugins/duo_oncall/duo_oncall.12h.py`
* Tag @rorscott in Slack.