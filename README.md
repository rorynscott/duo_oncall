# Installation Instructions

1. You will need a credential file (named `.victorops`), which contains an API key and ID from VictorOps. Ask @rorscott for one! You will need to put it in your SwiftBar cache directory; mine is `/Users/rorscott/Library/Caches/com.ameba.SwiftBar/Plugins/duo_oncall.12h.py/.victorops` 
2. You can install Python 3 or use the executable in `dist/duo_oncall.12h/duo_oncall.12h`
2. Install SwiftBar with "brew install swiftbar" or from https://github.com/swiftbar/SwiftBar/releases/latest
3. Start SwiftBar and it will ask you where you want to store plugins. I used `Documents/swiftbar_plugins`.
4. Install in plugin directory `git clone https://github.com/rorynscott/duo_oncall.git -- ~/Documents/swiftbar_plugins/duo_oncall`
5. Restart SwiftBar
6. In the menu choose SwiftBar -> Preferences -> Launch at Login


# Updates
To update run git pull in the directory you installed the plugin: `cd ~/Documents/swiftbar_plugins/duo_oncall && git pull`


# Something went wrong
* Command-r when the SwiftBar menu is selected to refresh plugins.
* Option-click the menu for more options.
* Make sure the plugin is executable: `chmod +x ~/Documents/swiftbar_plugins/duo_oncall/duo_oncall.12h.py`
* Tag @rorscott in Slack.