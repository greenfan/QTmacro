#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QListWidget, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    '''
    finished = pyqtSignal(str)

class MacroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt Macro")
        self.setMinimumSize(500, 600)
        self.worker_signals = WorkerSignals()
        self.worker_signals.finished.connect(self.on_replay_finished)
        self.initUI()
        
    def initUI(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top image or banner
        try:
            pixmap = QPixmap("logo.png")  # Try to load image
            if pixmap.isNull():
                raise FileNotFoundError("Image not found")
            
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(460, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(image_label)
        except:
            # Display text banner if image not found
            banner = QLabel("Qt Macro")
            banner.setFont(QFont("Arial", 24, QFont.Bold))
            banner.setStyleSheet("color: #2c3e50; padding: 20px; background-color: #ecf0f1; border-radius: 10px;")
            banner.setAlignment(Qt.AlignCenter)
            banner.setFixedHeight(100)
            main_layout.addWidget(banner)
        
        # Middle spacing (100 pixels)
        spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addItem(spacer)
        
        # Text box
        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("Notes or instructions can be typed here...")
        self.text_box.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7; 
                border-radius: 5px; 
                padding: 10px;
                background-color: #ffffff;
                color: #333333;
            }
        """)
        main_layout.addWidget(self.text_box)
        
        # List widget for XNS files (initially hidden)
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                color: #333333;
                min-height: 100px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
        """)
        self.files_list.setVisible(False)
        main_layout.addWidget(self.files_list)
        
        # Bottom buttons layouts (now in two rows for better spacing)
        buttons_layout1 = QHBoxLayout()
        buttons_layout1.setSpacing(10)
        
        buttons_layout2 = QHBoxLayout()
        buttons_layout2.setSpacing(10)
        
        # Button 1: Record
        self.btn_record = QPushButton("Record")
        self.btn_record.setFixedSize(QSize(110, 40))
        self.btn_record.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.btn_record.clicked.connect(self.run_record_script)
        buttons_layout1.addWidget(self.btn_record)
        
        # Button 2: Stop Recording
        self.btn_stop = QPushButton("Stop Recording")
        self.btn_stop.setFixedSize(QSize(110, 40))
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #717171;
            }
        """)
        self.btn_stop.clicked.connect(self.run_stop_script)
        buttons_layout1.addWidget(self.btn_stop)
        
        # Button 3: Show Recordings
        self.btn_show = QPushButton("Show Recs")
        self.btn_show.setFixedSize(QSize(110, 40))
        self.btn_show.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)
        self.btn_show.clicked.connect(self.show_recordings)
        buttons_layout1.addWidget(self.btn_show)
        
        # Button 4: Replay
        self.btn_replay = QPushButton("Replay")
        self.btn_replay.setFixedSize(QSize(110, 40))
        self.btn_replay.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.btn_replay.clicked.connect(self.run_replay)
        buttons_layout1.addWidget(self.btn_replay)
        
        # New Button: Delete Recording
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setFixedSize(QSize(110, 40))
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #a04000;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_recording)
        buttons_layout2.addWidget(self.btn_delete)
        
        # Add spacers on both sides of the delete button for centering
        buttons_layout2.addStretch()
        buttons_layout2.insertStretch(0)
        
        main_layout.addLayout(buttons_layout1)
        main_layout.addLayout(buttons_layout2)
        
        self.setCentralWidget(main_widget)
        
    def run_record_script(self):
        try:
            subprocess.Popen(["bash", "script1.sh"])
            self.text_box.append("Recording started...")
        except Exception as e:
            self.text_box.append(f"Error running record script: {str(e)}")
    
    def run_stop_script(self):
        try:
            subprocess.Popen(["bash", "stoprec.sh"])
            self.text_box.append("Recording stopped.")
        except Exception as e:
            self.text_box.append(f"Error stopping recording: {str(e)}")
    
    def show_recordings(self):
        try:
            # Check if recs directory exists
            if not os.path.exists("recs"):
                self.text_box.append("recs/ directory not found.")
                return
                
            # Find all *xns files
            xns_files = []
            for file in os.listdir("recs"):
                if file.endswith(".xns"):
                    xns_files.append(file)
            
            if not xns_files:
                self.text_box.append("No .xns files found in recs/ directory.")
                self.files_list.setVisible(False)
                return
                
            # Populate list widget
            self.files_list.clear()
            for file in sorted(xns_files):
                self.files_list.addItem(file)
            
            # Select the first item by default
            if self.files_list.count() > 0:
                self.files_list.setCurrentRow(0)
            
            self.files_list.setVisible(True)
            self.text_box.append(f"Found {len(xns_files)} recording(s).")
            
        except Exception as e:
            self.text_box.append(f"Error showing recordings: {str(e)}")
    
    def delete_recording(self):
        if not self.files_list.isVisible() or self.files_list.count() == 0:
            self.text_box.append("No recording selected. Please click 'Show Recs' first.")
            return
            
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            self.text_box.append("Please select a recording from the list to delete.")
            return
            
        selected_file = selected_items[0].text()
        file_path = os.path.join("recs", selected_file)
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the recording '{selected_file}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                os.remove(file_path)
                self.text_box.append(f"Deleted recording: {selected_file}")
                
                # Refresh the recordings list
                self.show_recordings()
            except Exception as e:
                self.text_box.append(f"Error deleting file: {str(e)}")
    
    def run_replay(self):
        if not self.files_list.isVisible() or self.files_list.count() == 0:
            self.text_box.append("No recording selected. Please click 'Show Recs' first.")
            return
            
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            self.text_box.append("Please select a recording from the list.")
            return
            
        selected_file = selected_items[0].text()
        file_path = os.path.join("recs", selected_file)
        
        if not os.path.exists(file_path):
            self.text_box.append(f"Error: Selected file {file_path} not found.")
            return
            
        try:
            # Run the command directly without opening a terminal window
            self.text_box.append(f"Replaying {selected_file} after 5 seconds...")
            
            # Start a thread to execute the replay and monitor its completion
            replay_thread = threading.Thread(
                target=self.execute_replay,
                args=(file_path, selected_file)
            )
            replay_thread.daemon = True
            replay_thread.start()
            
        except Exception as e:
            self.text_box.append(f"Error running replay: {str(e)}")

    def execute_replay(self, file_path, filename):
        try:
            # Run the command and wait for it to complete
            cmd = f'sleep 5 && cnee --replay --file "{file_path}"'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()  # This will block until the process completes
            
            # Signal completion back to the main thread
            self.worker_signals.finished.emit(filename)
            
        except Exception as e:
            print(f"Error in execute_replay: {str(e)}")

    def on_replay_finished(self, filename):
        # This will be called when the replay is complete
        self.text_box.append(f"✅ Replay of {filename} completed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Consistent style across platforms
    window = MacroApp()
    window.show()
    sys.exit(app.exec_())