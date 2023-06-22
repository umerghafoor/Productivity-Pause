
import psutil
import constants

from constants import watch_list_file


def get_running_apps():
    """
    :return: The function `get_running_apps()` returns a list of names of currently running processes on the system.
    """
    running_apps = []
    for proc in psutil.process_iter(['name']):
        try:
            proc_info = proc.as_dict(attrs=['name'])
            running_apps.append(proc_info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return running_apps


def track_application_time(selected_app):
    with open(watch_list_file, "r") as file:
        watch_list = file.readlines()
    if selected_app + "\n" not in watch_list:
        with open(watch_list_file, "a") as file:
            file.write(selected_app + "\n")
    else:
        print(f"{selected_app} is already in the watch list.")
