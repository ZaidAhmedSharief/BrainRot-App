from __future__ import print_function
import time
from os import system
from activity import ActivityList, Activity, TimeEntry
import json
import datetime
import sys
if sys.platform in ['Windows', 'win32', 'cygwin']:
    import win32gui
    import uiautomation as auto
elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
    from AppKit import NSWorkspace
    from Foundation import *


active_window_name = ""
activity_name = ""
start_time = datetime.datetime.now()
activeList = ActivityList([])  # Correct usage of ActivityList
first_time = True

def url_to_name(url):
    string_list = url.split('/')
    return string_list[2]

def get_active_window():
    _active_window_name = None
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        window = win32gui.GetForegroundWindow()
        _active_window_name = win32gui.GetWindowText(window)
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        _active_window_name = (NSWorkspace.sharedWorkspace()
                               .activeApplication()['NSApplicationName'])
    else:
        print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
        print(sys.version)
    return _active_window_name

def get_chrome_url():
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        window = win32gui.GetForegroundWindow()
        chromeControl = auto.ControlFromHandle(window)
        edit = chromeControl.EditControl()
        return 'https://' + edit.GetValuePattern().Value
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        textOfMyScript = """tell app "google chrome" to get the url of the active tab of window 1"""
        s = NSAppleScript.initWithSource_(
            NSAppleScript.alloc(), textOfMyScript)
        results, err = s.executeAndReturnError_(None)
        return results.stringValue()
    else:
        print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
        print(sys.version)
    return _active_window_name

try:
    activeList.initialize_me()
except Exception:
    print('No json file found, starting fresh')

try:
    while True:
        previous_site = ""
        if sys.platform not in ['linux', 'linux2']:
            new_window_name = get_active_window()
            if 'Google Chrome' in new_window_name:
                new_window_name = url_to_name(get_chrome_url())
        if sys.platform in ['linux', 'linux2']:
            new_window_name = l.get_active_window_x()
            if 'Google Chrome' in new_window_name:
                new_window_name = l.get_chrome_url_x()

        if active_window_name != new_window_name:
            print(f"Switched from {active_window_name} to {new_window_name}")
            activity_name = active_window_name

            if not first_time:
                end_time = datetime.datetime.now()
                time_entry = TimeEntry(start_time, end_time, 0, 0, 0, 0)
                time_entry._get_specific_times()

                print(f"Logging activity: {activity_name} from {start_time} to {end_time}")
                exists = False
                for activity in activeList.activities:
                    if activity.name == activity_name:
                        exists = True
                        print(f"Updating existing activity: {activity_name}")
                        activity.time_entries.append(time_entry)

                if not exists:
                    print(f"Creating new activity: {activity_name}")
                    activity = Activity(activity_name, [time_entry])
                    activeList.activities.append(activity)
                
                print(f"Saving activities to activities.json: {activeList.serialize()}")

                # Save to JSON file
                with open('activities.json', 'w') as json_file:
                    json.dump(activeList.serialize(), json_file, indent=4, sort_keys=True)

                start_time = datetime.datetime.now()

            first_time = False
            active_window_name = new_window_name

        time.sleep(1)

except KeyboardInterrupt:
    print(f"Saving activities to activities.json before exit")
    with open('activities.json', 'w') as json_file:
        json.dump(activeList.serialize(), json_file, indent=4, sort_keys=True)
