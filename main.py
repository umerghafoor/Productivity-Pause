from msilib.schema import SelfReg
import time
import sys, os
from typing import Self
import functions
import constants

from constants import watch_list_file, icon
from functions import get_running_apps, is_startup_enabled, toggle_startup, track_application_time, modify_duration, stop_tracking_application_time, update_app_list, read_watch_list
from functions import get_application_usage_time, get_time_limit
from PyQt6.QtCore import QTimer, Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction
# from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHeaderView, QVBoxLayout, QPushButton, QWidget, QLabel, QLineEdit
# from PyQt6.QtWidgets import QStyledItemDelegate, QAbstractItemView, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtWidgets import *
ignore_list = []
app_autostart_enabled = False
settings_dialog = None


def quit_app():
    """
    The function `quit_app()` removes a desktop entry file if it exists and then quits the application.
    """
    if not app_autostart_enabled:
        desktop_entry_path = os.path.expanduser("~/.config/autostart/app_monitor.desktop")
        if os.path.exists(desktop_entry_path):
            os.remove(desktop_entry_path)
    app.quit()

def update_data_to_model(app_data):
    """
    This function appends the updated data to the app_model.
    """
    app_model.clear()
    for app_name, elapsed_time in app_data.items():
        item = QStandardItem(app_name)
        app_model.appendRow([item, QStandardItem(str(elapsed_time))])


def update_watched_app_model(watch_list):
    """
    This function appends the items from the watch list to the watched_app_model.
    """
    watched_app_model.clear()
    for app_name, duration in watch_list:
        item = QStandardItem(app_name)
        item_duration = QStandardItem(duration)
        watched_app_model.appendRow([item, item_duration])


def on_popup_finished(result, app_name):
    """
    The function `on_popup_finished` adds the `app_name` to the `ignore_list` if the `result` is equal
    to `QMessageBox.StandardButton.Close` and then prints the `ignore_list`.
    
    :param result: The result parameter is the button that was clicked in the popup dialog. It is of
    type QMessageBox.StandardButton, which is an enumeration of the standard buttons that can be clicked
    in a QMessageBox dialog
    :param app_name: The `app_name` parameter is a string that represents the name of the application
    """
    if result == QMessageBox.StandardButton.Close:
        ignore_list.append(app_name)
        print(ignore_list)


def check_the_limit(watch_list):
    """
    The function `check_the_limit` checks the usage time of applications in a watch list and displays a
    popup message if the usage time exceeds the time limit, unless the application is in the ignore
    list.
    
    :param watch_list: The `watch_list` parameter is a list of tuples where each tuple contains the name
    of an application and its duration
    """
    for app_name, duration in watch_list:
        if get_application_usage_time(app_name) > get_time_limit(app_name):
            if app_name not in ignore_list:
                popup = QMessageBox()
                popup.setWindowTitle("Time to close " + app_name)
                popup.setText("Its time to close the app take some rest!")

                popup.setStandardButtons(QMessageBox.StandardButton.Close)
                popup.finished.connect(
                    lambda result, app_name=app_name: on_popup_finished(result, app_name))
                popup.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

                popup.exec()
                popup.setModal(False)
                popup.show()
            else:
                print(1234)


def restoreApp():
    window.show()


def minimizeApp():
    window.hide()


def quit_app():
    app.quit()


def update_button_clicked():
    """
    The function `update_button_clicked()` updates the data in the model based on the app list and watch
    list, and checks if the watch list has reached its limit.
    """
    watch_list = read_watch_list()
    app_data = update_app_list()

    update_data_to_model(app_data)
    update_watched_app_model(watch_list)
    check_the_limit(watch_list)


def addtolist_button_clicked():
    """
    The function adds the selected item from a list to another function for tracking application time.
    """
    selected_indexes = app_list.selectedIndexes()
    if selected_indexes:
        track_application_time(selected_indexes[0].data())


def modify_time_button_clicked():
    """
    The function `modify_time_button_clicked()` modifies the duration of a selected item in a watched
    app list based on the value entered in the `modify_time_value` text field.
    """
    selected_indexes = watched_app_list.selectedIndexes()
    if modify_time_value.text().isdecimal():
        duration = int(modify_time_value.text())
        print(duration)
        if selected_indexes:
            modify_duration(selected_indexes[0].data(), duration)


def startup_checkbox_state_changed():
    """
    The function `startup_checkbox_state_changed()` toggles the startup state based on the value of the
    startup checkbox.
    """
    enable_startup = startup_checkbox.isChecked()
    toggle_startup(enable_startup)

def removefromlist_button_clicked():
    """
    The function removes the selected item from a list and stops tracking its application time.
    """
    selected_indexes = watched_app_list.selectedIndexes()
    if selected_indexes:
        stop_tracking_application_time(selected_indexes[0].data())


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

layout.addWidget(QLabel("Runing Apps"))
layout.addWidget(app_list)

watched_app_list = QTreeView()
watched_app_list.setModel(watched_app_model)
watched_app_list.setHeaderHidden(True)
watched_app_list.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
watched_app_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

layout.addWidget(QLabel("Watched Apps"))
layout.addWidget(watched_app_list)


addtolist_button = QPushButton("Add to Watch list")
addtolist_button.clicked.connect(addtolist_button_clicked)
layout.addWidget(addtolist_button)

removefromlist_button = QPushButton("Remove from Watch list")
removefromlist_button.clicked.connect(removefromlist_button_clicked)
layout.addWidget(removefromlist_button)


update_button = QPushButton("Update")
update_button.clicked.connect(update_button_clicked)
layout.addWidget(update_button)

modify_time_value = QLineEdit()
layout.addWidget(modify_time_value)

modify_time_button = QPushButton("Modify time")
modify_time_button.clicked.connect(modify_time_button_clicked)
layout.addWidget(modify_time_button)

minimize_button = QPushButton("Minimize App")
minimize_button.clicked.connect(minimizeApp)
layout.addWidget(minimize_button)

startup_checkbox = QCheckBox("Enable Startup")
print(is_startup_enabled())
startup_checkbox.setChecked(is_startup_enabled())
startup_checkbox.stateChanged.connect(startup_checkbox_state_changed)
layout.addWidget(startup_checkbox)


quit_button = QPushButton("Quit")
quit_button.clicked.connect(quit_app)
layout.addWidget(quit_button)
# Start Updating in Loop
timer = QTimer()
timer.setInterval(10000)
timer.timeout.connect(lambda: update_button_clicked())
timer.start()

# Move to System tray
tray_icon = QSystemTrayIcon(QIcon(icon), parent=app)

tray_menu = QMenu()
settings_action = QAction("Settings", parent=tray_menu)
exit_action = QAction("Exit", parent=tray_menu)
tray_menu.addAction(settings_action)
tray_menu.addAction(exit_action)

tray_icon.setContextMenu(tray_menu)

settings_action.triggered.connect(restoreApp)
exit_action.triggered.connect(quit_app)

tray_icon.show()

sys.exit(app.exec())
