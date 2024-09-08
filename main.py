# main.py
import sys
import threading
import os
from flask import Flask, request, jsonify
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QFileDialog, QTextEdit, QProgressBar, QMessageBox, QDialog, QFormLayout, 
                             QLineEdit, QComboBox, QLabel, QStackedWidget, QListWidget, QTreeWidget, 
                             QTreeWidgetItem, QSplitter)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont
from file_organizer import file_organizer
from error_handling import handle_error, FileOrganizerError
from config import config
from logger import logger
from plugin_system import plugin_system
from ai_backends import get_ai_backend

app = Flask(__name__)

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout = QFormLayout()

        self.ai_backend = QComboBox()
        self.ai_backend.addItems(["openai", "huggingface", "local", "perplexity", "bing"])
        self.ai_backend.setCurrentText(config.get("ai_backend"))
        layout.addRow("AI Backend:", self.ai_backend)

        self.openai_api_key = QLineEdit(config.get("openai_api_key"))
        layout.addRow("OpenAI API Key:", self.openai_api_key)

        self.huggingface_api_key = QLineEdit(config.get("huggingface_api_key"))
        layout.addRow("HuggingFace API Key:", self.huggingface_api_key)

        self.local_model_path = QLineEdit(config.get("local_model_path"))
        layout.addRow("Local Model Path:", self.local_model_path)

        self.perplexity_api_key = QLineEdit(config.get("perplexity_api_key"))
        layout.addRow("Perplexity API Key:", self.perplexity_api_key)

        self.bing_api_key = QLineEdit(config.get("bing_api_key"))
        layout.addRow("Bing API Key:", self.bing_api_key)

        self.bing_endpoint = QLineEdit(config.get("bing_endpoint"))
        layout.addRow("Bing Endpoint:", self.bing_endpoint)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_config)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_config(self):
        config.set("ai_backend", self.ai_backend.currentText())
        config.set("openai_api_key", self.openai_api_key.text())
        config.set("huggingface_api_key", self.huggingface_api_key.text())
        config.set("local_model_path", self.local_model_path.text())
        config.set("perplexity_api_key", self.perplexity_api_key.text())
        config.set("bing_api_key", self.bing_api_key.text())
        config.set("bing_endpoint", self.bing_endpoint.text())
        config.save_config()
        self.accept()

class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")
            logger.error(f"Error in worker thread: {str(e)}")

class ProposedChangesDialog(QDialog):
    def __init__(self, parent=None, current_structure=None, proposed_structure=None):
        super().__init__(parent)
        self.setWindowTitle("Proposed Changes")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        # Current structure
        current_group = QWidget()
        current_layout = QVBoxLayout(current_group)
        current_layout.addWidget(QLabel("Current Structure:"))
        self.current_tree = QTreeWidget()
        self.current_tree.setHeaderLabels(["Current"])
        current_layout.addWidget(self.current_tree)
        splitter.addWidget(current_group)

        # Proposed structure
        proposed_group = QWidget()
        proposed_layout = QVBoxLayout(proposed_group)
        proposed_layout.addWidget(QLabel("Proposed Structure:"))
        self.proposed_tree = QTreeWidget()
        self.proposed_tree.setHeaderLabels(["Proposed"])
        proposed_layout.addWidget(self.proposed_tree)
        splitter.addWidget(proposed_group)

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        self.accept_button = QPushButton("Accept Changes")
        self.accept_button.clicked.connect(self.accept)
        button_layout.addWidget(self.accept_button)

        self.modify_button = QPushButton("Modify Structure")
        self.modify_button.clicked.connect(self.modify_structure)
        button_layout.addWidget(self.modify_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.populate_trees(current_structure, proposed_structure)

    def populate_trees(self, current_structure, proposed_structure):
        self.populate_tree(self.current_tree, current_structure)
        self.populate_tree(self.proposed_tree, proposed_structure)

    def populate_tree(self, tree, structure):
        tree.clear()
        self.add_tree_items(tree.invisibleRootItem(), structure)

    def add_tree_items(self, parent, structure):
        if isinstance(structure, dict):
            for key, value in structure.items():
                item = QTreeWidgetItem(parent, [key])
                self.add_tree_items(item, value)
        elif isinstance(structure, list):
            for value in structure:
                item = QTreeWidgetItem(parent, [value])

    def modify_structure(self):
        # This method will open a dialog to allow the user to modify the proposed structure
        # For simplicity, we'll just show a message box here
        QMessageBox.information(self, "Modify Structure", "This feature allows you to modify the proposed structure. Implement the modification logic here.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI File Organizer")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)

        main_layout = QHBoxLayout()
        
        # Left sidebar
        sidebar_layout = QVBoxLayout()
        self.sidebar_list = QListWidget()
        self.sidebar_list.addItems(["Home", "Analyze", "Reorganize", "Plugins", "Configuration"])
        self.sidebar_list.currentRowChanged.connect(self.display_page)
        sidebar_layout.addWidget(self.sidebar_list)
        
        # Main content area
        self.stack = QStackedWidget()
        
        # Home page
        home_page = QWidget()
        home_layout = QVBoxLayout()
        home_label = QLabel("Welcome to AI File Organizer")
        home_label.setAlignment(Qt.AlignCenter)
        home_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        home_layout.addWidget(home_label)
        home_page.setLayout(home_layout)
        self.stack.addWidget(home_page)
        
        # Analyze page
        analyze_page = QWidget()
        analyze_layout = QVBoxLayout()
        self.select_button = QPushButton("Select Directory")
        self.select_button.clicked.connect(self.select_directory)
        analyze_layout.addWidget(self.select_button)
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze_directory)
        analyze_layout.addWidget(self.analyze_button)
        self.text_edit = QTextEdit()
        analyze_layout.addWidget(self.text_edit)
        self.progress_bar = QProgressBar()
        analyze_layout.addWidget(self.progress_bar)
        analyze_page.setLayout(analyze_layout)
        self.stack.addWidget(analyze_page)
        
        # Reorganize page
        reorganize_page = QWidget()
        reorganize_layout = QVBoxLayout()
        self.preview_button = QPushButton("Preview Reorganization")
        self.preview_button.clicked.connect(self.preview_reorganization)
        reorganize_layout.addWidget(self.preview_button)
        self.reorganize_button = QPushButton("Reorganize")
        self.reorganize_button.clicked.connect(self.reorganize_files)
        reorganize_layout.addWidget(self.reorganize_button)
        self.undo_button = QPushButton("Undo Last Reorganization")
        self.undo_button.clicked.connect(self.undo_reorganization)
        reorganize_layout.addWidget(self.undo_button)
        reorganize_page.setLayout(reorganize_layout)
        self.stack.addWidget(reorganize_page)
        
        # Plugins page
        plugins_page = QWidget()
        plugins_layout = QVBoxLayout()
        plugins_label = QLabel("Plugins")
        plugins_label.setAlignment(Qt.AlignCenter)
        plugins_layout.addWidget(plugins_label)
        self.plugins_list = QListWidget()
        self.update_plugins_list()
        plugins_layout.addWidget(self.plugins_list)
        plugins_page.setLayout(plugins_layout)
        self.stack.addWidget(plugins_page)
        
        # Configuration page
        config_page = QWidget()
        config_layout = QVBoxLayout()
        self.config_button = QPushButton("Open Configuration")
        self.config_button.clicked.connect(self.open_config_dialog)
        config_layout.addWidget(self.config_button)
        config_page.setLayout(config_layout)
        self.stack.addWidget(config_page)

        main_layout.addLayout(sidebar_layout, 1)
        main_layout.addWidget(self.stack, 4)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.selected_directory = ""
        self.worker_thread = None
        self.suggestions = ""
        self.ai_backend = get_ai_backend()

        plugin_system.load_plugins()

    def display_page(self, index):
        self.stack.setCurrentIndex(index)

    def update_plugins_list(self):
        self.plugins_list.clear()
        for plugin_name, plugin_info in plugin_system.plugins.items():
            self.plugins_list.addItem(f"{plugin_name}: {plugin_info['description']}")

    def open_config_dialog(self):
        dialog = ConfigDialog(self)
        if dialog.exec_():
            self.ai_backend = get_ai_backend()
            self.text_edit.setText("Configuration updated.")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selected_directory = directory
            self.text_edit.setText(f"Selected directory: {self.selected_directory}")
        else:
            self.text_edit.setText("No directory selected.")

    def analyze_directory(self):
        if not self.selected_directory:
            self.text_edit.setText("Please select a directory first.")
            return
        
        if not os.path.isdir(self.selected_directory):
            self.text_edit.setText("The selected directory no longer exists. Please choose another directory.")
            return

        self.text_edit.setText("Analyzing directory...")
        self.progress_bar.setValue(0)
        
        self.worker_thread = WorkerThread(self._analyze_directory_task)
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.update_status.connect(self.update_status)
        self.worker_thread.start()

    def _analyze_directory_task(self):
        try:
            current_structure = file_organizer.get_directory_structure(self.selected_directory)
            file_list = file_organizer.analyze_directory(self.selected_directory)
            self.worker_thread.update_progress.emit(50)
            self.worker_thread.update_status.emit("Generating suggestions...")
            self.suggestions = self.ai_backend.get_organization_suggestions(file_list)
            proposed_structure = file_organizer.get_proposed_structure(current_structure, self.suggestions)
            self.worker_thread.update_progress.emit(100)
            self.worker_thread.update_status.emit("Analysis complete. Review the proposed changes.")
            self.show_proposed_changes(current_structure, proposed_structure)
        except FileOrganizerError as e:
            self.worker_thread.update_status.emit(f"Error: {str(e)}")
        except Exception as e:
            handle_error(e, logger)
            self.worker_thread.update self.worker_thread.update_status.emit("An unexpected error occurred.")

    def show_proposed_changes(self, current_structure, proposed_structure):
        dialog = ProposedChangesDialog(self, current_structure, proposed_structure)
        if dialog.exec_() == QDialog.Accepted:
            self.suggestions = proposed_structure  # Update suggestions with user-modified structure
            self.text_edit.setText("Proposed changes accepted. You can now reorganize the files.")
        else:
            self.text_edit.setText("Proposed changes cancelled. You can analyze the directory again or modify the current structure.")

    def preview_reorganization(self):
        if not self.selected_directory or not self.suggestions:
            self.text_edit.setText("Please analyze the directory before previewing reorganization.")
            return
        
        self.text_edit.setText("Generating preview...")
        self.progress_bar.setValue(0)
        
        self.worker_thread = WorkerThread(self._preview_reorganization_task)
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.update_status.connect(self.update_status)
        self.worker_thread.start()

    def _preview_reorganization_task(self):
        try:
            file_list = file_organizer.analyze_directory(self.selected_directory)
            self.worker_thread.update_progress.emit(50)
            preview = file_organizer.preview_reorganization(file_list, self.suggestions)
            self.worker_thread.update_progress.emit(100)
            preview_text = "\n".join([f"{old} -> {new}" for old, new in preview])
            self.worker_thread.update_status.emit(f"Preview of reorganization:\n\n{preview_text}")
        except FileOrganizerError as e:
            self.worker_thread.update_status.emit(f"Error: {str(e)}")
        except Exception as e:
            handle_error(e, logger)
            self.worker_thread.update_status.emit("An unexpected error occurred.")

    def reorganize_files(self):
        if not self.selected_directory or not self.suggestions:
            self.text_edit.setText("Please analyze the directory before reorganizing.")
            return
        
        self.text_edit.setText("Reorganizing files...")
        self.progress_bar.setValue(0)
        
        self.worker_thread = WorkerThread(self._reorganize_files_task)
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.update_status.connect(self.update_status)
        self.worker_thread.start()

    def _reorganize_files_task(self):
        try:
            file_list = file_organizer.analyze_directory(self.selected_directory)
            self.worker_thread.update_progress.emit(33)
            self.worker_thread.update_status.emit("Applying reorganization...")
            file_organizer.reorganize_files(file_list, self.suggestions)
            self.worker_thread.update_progress.emit(100)
            self.worker_thread.update_status.emit("Reorganization complete.")
            
            # Execute post-reorganization plugins
            for plugin_name, plugin_info in plugin_system.plugins.items():
                if plugin_info.get("type") == "post_reorganization":
                    result = plugin_system.execute_plugin(plugin_name, self.selected_directory)
                    if result:
                        self.worker_thread.update_status.emit(f"Plugin {plugin_name} executed: {result}")
        except FileOrganizerError as e:
            self.worker_thread.update_status.emit(f"Error: {str(e)}")
        except Exception as e:
            handle_error(e, logger)
            self.worker_thread.update_status.emit("An unexpected error occurred.")

    def undo_reorganization(self):
        if not file_organizer.last_reorganization:
            self.text_edit.setText("No recent reorganization to undo.")
            return
        
        self.text_edit.setText("Undoing last reorganization...")
        self.progress_bar.setValue(0)
        
        self.worker_thread = WorkerThread(self._undo_reorganization_task)
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.update_status.connect(self.update_status)
        self.worker_thread.start()

    def _undo_reorganization_task(self):
        try:
            file_organizer.undo_last_reorganization()
            self.worker_thread.update_progress.emit(100)
            self.worker_thread.update_status.emit("Undo operation completed successfully.")
        except Exception as e:
            handle_error(e, logger)
            self.worker_thread.update_status.emit("An error occurred while undoing the reorganization.")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.text_edit.setText(status)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            logger.info("Application closed by user")
        else:
            event.ignore()

@app.route('/analyze', methods=['POST'])
def analyze():
    directory = request.json.get('directory')
    if not directory:
        return jsonify({'error': 'No directory provided'}), 400
    
    try:
        current_structure = file_organizer.get_directory_structure(directory)
        file_list = file_organizer.analyze_directory(directory)
        ai_backend = get_ai_backend()
        suggestions = ai_backend.get_organization_suggestions(file_list)
        proposed_structure = file_organizer.get_proposed_structure(current_structure, suggestions)
        return jsonify({
            'current_structure': current_structure,
            'proposed_structure': proposed_structure,
            'suggestions': suggestions
        })
    except FileOrganizerError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        handle_error(e, logger)
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/reorganize', methods=['POST'])
def reorganize():
    directory = request.json.get('directory')
    proposed_structure = request.json.get('proposed_structure')
    
    if not directory or not proposed_structure:
        return jsonify({'error': 'Directory and proposed structure are required'}), 400
    
    try:
        file_list = file_organizer.analyze_directory(directory)
        file_organizer.reorganize_files(file_list, proposed_structure)
        return jsonify({'status': 'success'})
    except FileOrganizerError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        handle_error(e, logger)
        return jsonify({'error': 'An unexpected error occurred'}), 500

def run_flask():
    app.run(port=5000, threaded=True)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec_())