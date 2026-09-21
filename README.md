# Installation Instructions

1. You will need a credential file (named `.victorops`), which contains an API key and ID from VictorOps. Ask @rorscott for one! It looks like this:
```
API_KEY:<your_api_key>
API_ID:<your_api_id>
```
2. Put the credential file in your home directory, i.e. `~/.victorops`. The plugin checks these locations in order and uses the first one it finds:
    1. the path in the `DUO_ONCALL_CREDS` environment variable, if set
    2. the plugin directory, e.g. `~/Documents/swiftbar_plugins/duo_oncall/.victorops`
    3. your home directory, i.e. `~/.victorops`
    4. the pre-SwiftBar-2.1.1 cache directory, i.e. `~/Library/Caches/com.ameba.SwiftBar/Plugins/duo_oncall.12h.py/.victorops`

    The cache directory is checked last and only for backwards compatibility. SwiftBar derives that path from the plugin's location and renames it when the app changes its naming scheme, so don't put new credentials there.
3. Install Python 3.
4. Install SwiftBar with `brew install swiftbar` or from https://github.com/swiftbar/SwiftBar/releases/latest
5. Start SwiftBar and it will ask you where you want to store plugins. I used `Documents/swiftbar_plugins`.
6. Install in plugin directory `git clone https://github.com/rorynscott/duo_oncall.git -- ~/Documents/swiftbar_plugins/duo_oncall`
7. Create a `.config.ini` file in the plugin directory. You can use the `.config.ini.sample` file and remove any teams you aren't interested in. The `display_conf` block is optional; if you omit it, user names are shown using `displayName`. If you include it, `user_display` can be any field associated with a user found in the `/v2/user` response body found in [the docs](https://portal.victorops.com/public/api-docs.html#!/Users/get_api). My config file looks like this:
```
[display_conf]
user_display = displayName

[teams]
admin-user-management = team-jAyTiBSiiyygnKJL
```
8. Restart SwiftBar
9. In the menu choose SwiftBar -> Preferences -> Launch at Login


# Updates
To update run git pull in the directory you installed the plugin: `cd ~/Documents/swiftbar_plugins/duo_oncall && git pull`


# Something went wrong
* Command-r when the SwiftBar menu is selected to refresh plugins.
* Option-click the menu for more options.
* Make sure the plugin is executable: `chmod +x ~/Documents/swiftbar_plugins/duo_oncall/duo_oncall.12h.py`
* `No .victorops found in: ...` means the credential file isn't in any of the locations listed in step 2. The error lists every directory that was checked. If you have an older install with credentials in a SwiftBar cache directory, move them to your home directory:
```
mv ~/Library/Caches/com.ameba.SwiftBar/Plugins/*/.victorops ~/.victorops
```
* Tag @rorscott in Slack.
