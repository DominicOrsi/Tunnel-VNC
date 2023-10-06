'''
TODO: Fully comment out code, finished error checking, and create signed EXE
'''

import sys, os, tempfile, tunnel
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, launch_vnc, parent=None):
        super().__init__(parent)
        self.stopped = False
        self.launch_vnc = launch_vnc

    def stop(self):
        self.stopped = True

    def run(self):
        server_started = True
        try:
            server = tunnel.createTunnel(self.instance_ip, self.ssl_key_path)
            tunnel.startServer(server)
        except Exception as e:
            server_started = False
            tunnel.stopServer(server)
            self.error_signal.emit("Check Instance IP Address and SSL Key Path\nSSH Error Message: " + str(e))


        # Start tigerVNC
        try:
            if self.launch_vnc and server_started:
                tunnel.startTigerVNC(self.vnc_install_path)
        except Exception as e:
            tunnel.stopServer(server)
            self.error_signal.emit("VNC INSTALL PATH IS INCORRECT")

        # Emit the finished signal when the work is done
        self.finished.emit()

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Connect to Instance")

        # Set window size to 400x400 pixels
        self.setFixedSize(400, 400)

        # Create central widget and set it as the main window's central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout for the central widget
        main_layout = QVBoxLayout()

        # Create a form layout for labels and text fields
        form_layout = QFormLayout()

        # Create labels and input fields
        instance_ip_label = QLabel("Instance IP Address:")
        self.instance_ip_input = QLineEdit()
        ssl_key_label = QLabel("SSL Private Key Path:")
        self.ssl_key_input = QLineEdit()
        vnc_install_path_label = QLabel("TigerVNC Install Path:")
        self.vnc_install_path_input = QLineEdit()

        # Add labels and input fields to the form layout
        form_layout.addRow(instance_ip_label, self.instance_ip_input)
        form_layout.addRow(ssl_key_label, self.ssl_key_input)
        form_layout.addRow(vnc_install_path_label, self.vnc_install_path_input)

        # Create a spacer item to add space between the text fields and buttons
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a checkbox 
        vnc_checkbox = QLabel("Launch TigerVNC:")
        self.launch_vnc_checkbox = QCheckBox("")

        # Add the checkbox to the form layout
        form_layout.addRow(vnc_checkbox, self.launch_vnc_checkbox)

        '''
        ************************************************************ 
        Start of Button Layout
        ''' 

        # Create a layout for buttons (horizontal layout)
        button_layout = QVBoxLayout()

        # Create buttons
        self.connect_button = QPushButton("Connect to Instance")
        exit_button = QPushButton("Exit")

        # Set the "Exit" button's background color to red
        exit_button.setStyleSheet("background-color: red;")

        # Connect button click signals to functions
        self.connect_button.clicked.connect(self.on_connect_button_clicked)
        exit_button.clicked.connect(self.close)

        # Add buttons to the button layout
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(exit_button)

        # Create a label
        bottom_label = QLabel("Made for Gonzaga University")

        # Set alignment for "Made for Gonzaga University" label
        bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the form layout, spacer item, button layout, and "Made with Love" label to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addItem(spacer_item)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(bottom_label)

        # Set the layout for the central widget
        central_widget.setLayout(main_layout)

        # Populate text fields with data from temporary files (if available)
        self.load_data_from_temp_files()

        # Initialize the worker thread
        self.worker_thread = None

    def on_connect_button_clicked(self):
        # Save the data to the temp files to reflect edits
        self.save_data_to_temp_files()
        if self.worker_thread is None or not self.worker_thread.isRunning():
            # Only start a new worker thread if none is running
            self.worker_thread = WorkerThread(self.launch_vnc_checkbox.isChecked())  # Pass checkbox state
            self.worker_thread.instance_ip = self.instance_ip_input.text()
            self.worker_thread.ssl_key_path = self.ssl_key_input.text()
            self.worker_thread.vnc_install_path = self.vnc_install_path_input.text()
            self.connect_button.setEnabled(False)  # Disable the button during execution
            self.worker_thread.finished.connect(self.on_worker_finished)
            self.worker_thread.error_signal.connect(self.display_error)
            self.worker_thread.start()

    def on_worker_finished(self):
        # This slot is called when the worker thread has finished
        self.connect_button.setEnabled(True)

    def load_data_from_temp_files(self):
        # Load data from temporary files and populate text fields
        try:
            with open(os.path.join(tempfile.gettempdir(), 'instance_ip.txt'), 'r', encoding='utf-8') as ip_file:
                instance_ip = ip_file.read()
                self.instance_ip_input.setText(instance_ip)

            with open(os.path.join(tempfile.gettempdir(), 'ssl_key.txt'), 'r', encoding='utf-8') as key_file:
                ssl_key_path = key_file.read()
                self.ssl_key_input.setText(ssl_key_path)

            with open(os.path.join(tempfile.gettempdir(), 'vnc_install_path.txt'), 'r', encoding='utf-8') as path_file:
                vnc_install_path = path_file.read()
                self.vnc_install_path_input.setText(vnc_install_path)
                if self.vnc_install_path_input.text():
                    self.launch_vnc_checkbox.setChecked(True)
        except FileNotFoundError:
            pass

    def save_data_to_temp_files(self):
        instance_ip = self.instance_ip_input.text()
        ssl_key_path = self.ssl_key_input.text()
        vnc_install_path = self.vnc_install_path_input.text()

        # Create temporary files and save the data to them
        with open(os.path.join(tempfile.gettempdir(), 'instance_ip.txt'), 'w', encoding='utf-8') as ip_file:
            ip_file.write(instance_ip)

        with open(os.path.join(tempfile.gettempdir(), 'ssl_key.txt'), 'w', encoding='utf-8') as key_file:
            key_file.write(ssl_key_path)

        with open(os.path.join(tempfile.gettempdir(), 'vnc_install_path.txt'), 'w', encoding='utf-8') as path_file:
            path_file.write(vnc_install_path)

    def display_error(self, error_message):
        QMessageBox.critical(self, "ERROR", error_message)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
