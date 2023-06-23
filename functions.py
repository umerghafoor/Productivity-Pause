
import psutil
import time
import constants

from constants import watch_list_file


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
    watched_apps = read_watch_list()
    print(watched_apps)
    print(running_apps)


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


def get_application_usage_time(application_name):
    """
    This function reads the watch list and returns the usage time for the selected application.
    It takes the application name as input and returns the corresponding usage time in seconds.
    """
    with open(watch_list_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith(application_name):
            _, duration = line.strip().split(",")
            return int(duration)

    return 0


app_start_times = {}


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
