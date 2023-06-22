import psutil
import time
import sys
import constants

from constants import watch_list_file
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHeaderView, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtWidgets import QStyledItemDelegate, QAbstractItemView


app_start_times = {}


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


def update_app_list():
    """
    This function updates the time in the existing list of running apps.
    """
    apps = get_running_apps()
    current_time = time.time()

    for row in range(app_model.rowCount()):
        item = app_model.item(row, 0)
        app_name = item.text()

        if app_name in apps:
            elapsed_time = int(current_time - app_start_times[app_name])
            app_model.setItem(row, 1, QStandardItem(str(elapsed_time)))
        else:
            app_model.setItem(row, 1, QStandardItem(0))

    for app in apps:
        if app not in app_start_times:
            app_start_times[app] = current_time

            elapsed_time = int(current_time - app_start_times[app])
            item = QStandardItem(app)
            app_model.appendRow([item, QStandardItem(str(elapsed_time))])


def read_watched_list():
    """
    This function reads the contents of a file called "watch_list.txt" and adds each line as an item to
    the watched app list
    """
    watched_app_model.clear()
    with open(watch_list_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            item = QStandardItem(line.strip())
            watched_app_model.appendRow(item)


def quit_app():
    app.quit()


def update_button_clicked():
    update_app_list()
    read_watched_list()


def addtolist_button_clicked():
    selected_indexes = app_list.selectedIndexes()
    if selected_indexes:
        selected_app = selected_indexes[0].data()
        with open(watch_list_file, "r") as file:
            watch_list = file.readlines()
        if selected_app + "\n" not in watch_list:
            with open(watch_list_file, "a") as file:
                file.write(selected_app + "\n")
        else:
            print(f"{selected_app} is already in the watch list.")


# Main program
start_time = time.time()

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("App Monitor")

# Create GUI elements
widget = QWidget()
layout = QVBoxLayout(widget)
window.setCentralWidget(widget)

app_model = QStandardItemModel()
watched_app_model = QStandardItemModel()

app_list = QTreeView()
app_list.setModel(app_model)
app_list.setHeaderHidden(True)
app_list.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
app_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

layout.addWidget(app_list)

watched_app_list = QTreeView()
watched_app_list.setModel(watched_app_model)
watched_app_list.setHeaderHidden(True)
watched_app_list.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
watched_app_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

layout.addWidget(watched_app_list)


addtolist_button = QPushButton("Add to Watch list")
addtolist_button.clicked.connect(addtolist_button_clicked)
layout.addWidget(addtolist_button)


update_button = QPushButton("Update")
update_button.clicked.connect(update_button_clicked)
layout.addWidget(update_button)


quit_button = QPushButton("Quit")
quit_button.clicked.connect(quit_app)
layout.addWidget(quit_button)

# Start updating the app list
update_app_list()

window.show()

sys.exit(app.exec())
