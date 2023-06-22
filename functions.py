
import psutil


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
