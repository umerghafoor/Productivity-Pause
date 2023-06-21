import psutil
import time
import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHeaderView, QVBoxLayout, QPushButton, QWidget


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
    app_model.clear()

    current_time = int(time.time() - start_time)

    for app in apps:
        item = QStandardItem(app)
        app_model.appendRow([item, QStandardItem(str(current_time))])

    QTimer.singleShot(100, update_app_list)


def quit_app():
    app.quit()


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
app_list = QTreeView()
app_list.setModel(app_model)
app_list.setHeaderHidden(True)
app_list.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
layout.addWidget(app_list)

quit_button = QPushButton("Quit")
quit_button.clicked.connect(quit_app)
layout.addWidget(quit_button)

# Start updating the app list
update_app_list()

window.show()

sys.exit(app.exec())
