import psutil
import time
import tkinter as tk
from tkinter import ttk

def get_running_apps():
    running_apps = []
    for proc in psutil.process_iter(['name']):
        try:
            proc_info = proc.as_dict(attrs=['name'])
            running_apps.append(proc_info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return running_apps

def update_app_list():
    apps = get_running_apps()
    app_list.delete(*app_list.get_children())

    current_time = int(time.time() - start_time)

    for app in apps:
        app_list.insert("", tk.END, values=(app, current_time))

    
    root.after(100, update_app_list)

def quit_app():
    root.destroy()

# Main program
start_time = time.time()

root = tk.Tk()
root.title("App Monitor")

# Create GUI elements
app_list = ttk.Treeview(root, columns=("App", "Time"),show="headings")
app_list.heading("App", text="App")
app_list.heading("Time", text="Time")
app_list.pack()

quit_button = tk.Button(root, text="Quit", command=quit_app)
quit_button.pack()

# Start updating the app list
update_app_list()

root.mainloop()
