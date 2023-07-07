
import psutil
import time
import constants
import os
import winreg as reg
import winreg as reg

from winshell import startup, CreateShortcut
from constants import watch_list_file
from os import path,remove,path
from sys import argv
app_start_times = {}


def is_startup_enabled():
    """
    The function `is_startup_enabled` checks whether the application is set as a startup item in Windows.

    :return: Returns `True` if the application is set as a startup item, `False` otherwise.
    """
    script_path = os.path.abspath(__file__)

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.HKEY_CURRENT_USER

    try:
        reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_READ)
        value_count = reg.QueryInfoKey(reg_key)[1]
        for i in range(value_count):
            value_name = reg.EnumValue(reg_key, i)[0]
            if value_name == "MyApp":
                reg.CloseKey(reg_key)
                return True
        reg.CloseKey(reg_key)
    except Exception as e:
        print("Error: ", e)

    return False


def toggle_startup(enable):
    """
    The function `toggle_startup` adds or removes a shortcut to the application in the user's startup
    folder based on the `enable` parameter.

    :param enable: The `enable` parameter is a boolean value that determines whether to add or remove
    the application from the startup folder. If `enable` is `True`, the application will be added to the
    startup folder. If `enable` is `False`, the application will be removed from the startup folder
    """
    script_path = os.path.abspath(__file__)

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.HKEY_CURRENT_USER

    if enable:
        reg_value_name = "MyApp"
        reg_value_data = script_path

        try:
            reg.CreateKey(key, key_path)
            reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
            reg.SetValueEx(reg_key, reg_value_name, 0, reg.REG_SZ, reg_value_data)
            reg.CloseKey(reg_key)
            print("Added application to startup")
        except Exception as e:
            print("Error: ", e)
    else:
        reg_value_name = "MyApp"

        try:
            reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
            reg.DeleteValue(reg_key, reg_value_name)
            reg.CloseKey(reg_key)
            print("Removed application from startup")
        except Exception as e:
            print("Error: ", e)


def read_watch_list():
    """
    This function reads the contents of a file called "watch_list.txt" and returns a list of tuples
    containing the app name and duration.
    """
    watch_list = []
    with open("watch_list.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            app_name, duration = line.strip().split(",")
            watch_list.append((app_name, duration))
    return watch_list


def sort_running_apps(running_apps):
    """
    This function sorts the watched apps from the watchlist and places them at the top of the running_apps list.
    """
    running_apps.sort()
    watched_apps = read_watch_list()
    sorted_apps = []
    for app in watched_apps:
        if app[0] in running_apps:
            running_apps.remove(app[0])
            running_apps.insert(0, app[0])
    return sorted_apps


def get_running_apps():
    """
    :return: The function `get_running_apps()` returns a list of names of currently running processes on the system.
    """
    running_apps = []
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            proc_info = proc.as_dict(attrs=['name'])
            running_apps.append(proc_info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    sort_running_apps(running_apps)
    return running_apps


def track_application_time(selected_app):
    """
    This function checks if a selected application is in a watch list file and adds it with a time of 0
    if it is not already in the list.

    :param selected_app: The name of the application that the user wants to track the time for
    """
    with open(watch_list_file, "r") as file:
        watch_list = file.readlines()
    if selected_app + "\n" not in watch_list:
        with open(watch_list_file, "a") as file:
            file.write(selected_app + ",0\n")
    else:
        print(f"{selected_app} is already in the watch list.")


def stop_tracking_application_time(application_name):
    """
    This function removes an application from the watch list.
    It takes the application name as input and removes it from the file "watch_list.txt".
    """
    with open(watch_list_file, "r") as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if not line.startswith(application_name):
            modified_lines.append(line)

    with open(watch_list_file, "w") as file:
        file.writelines(modified_lines)


def modify_duration(app_name, new_duration):
    """
    This function modifies the duration of an app in the "watch_list.txt" file.
    It takes the app name and the new duration as input.
    """
    with open(watch_list_file, "r") as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith(app_name):
            line = f"{app_name},{new_duration}\n"
        modified_lines.append(line)

    with open(watch_list_file, "w") as file:
        file.writelines(modified_lines)


def update_app_list():
    """
    This function updates the time in the existing list of running apps and returns the updated data as a dictionary.
    """
    apps = get_running_apps()
    current_time = time.time()
    updated_data = {}

    for app_name in apps:
        if app_name in app_start_times:
            elapsed_time = int(current_time - app_start_times[app_name])
            updated_data[app_name] = elapsed_time
        else:
            app_start_times[app_name] = current_time
            updated_data[app_name] = 0

    return updated_data


def get_application_usage_time(application_name):
    """
    This function reads the watch list and returns the usage time for the selected application.
    It takes the application name as input and returns the corresponding usage time in seconds.
    """
    updated_data = update_app_list()
    return updated_data.get(application_name, 0)


def get_time_limit(application_name):
    """
    This function reads the watch list and returns the time limit for the selected application.
    It takes the application name as input and returns the corresponding time limit in seconds.
    """
    with open(watch_list_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith(application_name):
            _, time_limit = line.strip().split(",")
            return int(time_limit)

    return 0
