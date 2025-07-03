#!/usr/bin/env python3
"""
ParkIT - Parking Management System
Main entry point for the application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        from PyQt5 import QtWidgets
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        missing_deps.append("ultralytics (for vehicle detection)")
    
    try:
        import torch
    except ImportError:
        missing_deps.append("torch (for AI model)")
    
    return missing_deps


def main():
    """Main function to run the ParkIT application"""
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies using:")
        print("pip install -r requirements.txt")
        return 1
    
    # Enable high DPI scaling BEFORE creating QApplication
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Disable animations for instant resizing behavior
    app.setEffectEnabled(Qt.UI_AnimateMenu, False)
    app.setEffectEnabled(Qt.UI_AnimateCombo, False)
    app.setEffectEnabled(Qt.UI_AnimateTooltip, False)
    app.setEffectEnabled(Qt.UI_FadeMenu, False)
    app.setEffectEnabled(Qt.UI_FadeTooltip, False)
    
    # Set application properties
    app.setApplicationName("ParkIT")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("ParkIT Solutions")
    app.setOrganizationDomain("parkit.local")
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        # Show error message if something goes wrong
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("ParkIT - Error")
        error_msg.setText("An error occurred while starting the application:")
        error_msg.setDetailedText(str(e))
        error_msg.exec_()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 