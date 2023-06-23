###############################################################
#  run this file to stop showing console
###############################################################
import time
import sys
import functions
import constants

from constants import watch_list_file, icon
from functions import get_running_apps, track_application_time, modify_duration, stop_tracking_application_time, update_app_list, read_watch_list
from functions import get_application_usage_time, get_time_limit
from PyQt6.QtCore import QTimer, Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHeaderView, QVBoxLayout, QPushButton, QWidget, QLabel, QLineEdit
from PyQt6.QtWidgets import QStyledItemDelegate, QAbstractItemView, QSystemTrayIcon, QMenu, QMessageBox

ignore_list = []


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
    if result == QMessageBox.StandardButton.Close:
        ignore_list.append(app_name)
        print(ignore_list)


def check_the_limit(watch_list):
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
    watch_list = read_watch_list()
    app_data = update_app_list()

    update_data_to_model(app_data)
    update_watched_app_model(watch_list)
    check_the_limit(watch_list)


def addtolist_button_clicked():
    selected_indexes = app_list.selectedIndexes()
    if selected_indexes:
        track_application_time(selected_indexes[0].data())


def modify_time_button_clicked():
    selected_indexes = watched_app_list.selectedIndexes()
    if modify_time_value.text().isdecimal():
        duration = int(modify_time_value.text())
        print(duration)
        if selected_indexes:
            modify_duration(selected_indexes[0].data(), duration)


def removefromlist_button_clicked():
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

minimize_button = QPushButton("Minimize to System Tray")
minimize_button.clicked.connect(minimizeApp)
layout.addWidget(minimize_button)


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
