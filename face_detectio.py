import sys
import cv2
import numpy as np
import os
from typing import List, Dict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QFileDialog, QComboBox,
                            QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit, 
                            QScrollArea, QGroupBox, QGridLayout, QSlider,
                            QProgressBar, QMessageBox, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor

class FaceDetector:
    """
    Simple face detection system using OpenCV Haar cascades
    """
    
    def __init__(self):
        try:
            # Load cascade classifiers
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            
            # Check if cascades loaded successfully
            if self.face_cascade.empty():
                print("Warning: Could not load frontal face cascade")
            if self.profile_cascade.empty():
                print("Warning: Could not load profile face cascade")
                
        except Exception as e:
            print(f"Error initializing face detector: {e}")
            self.face_cascade = None
            self.profile_cascade = None
    
    def detect_faces(self, image: np.ndarray, scale_factor: float = 1.1, 
                    min_neighbors: int = 5, min_size: tuple = (30, 30)) -> List[Dict]:
        """Detect faces using Haar cascade classifiers"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            detected_faces = []
            face_id = 1
            
            # Detect frontal faces
            if self.face_cascade is not None and not self.face_cascade.empty():
                frontal_faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=min_size
                )
                
                for (x, y, w, h) in frontal_faces:
                    detected_faces.append({
                        'id': face_id,
                        'type': 'frontal',
                        'bbox': (x, y, w, h),
                        'confidence': 0.85,
                        'area': w * h
                    })
                    face_id += 1
            
            # Detect profile faces
            if self.profile_cascade is not None and not self.profile_cascade.empty():
                profile_faces = self.profile_cascade.detectMultiScale(
                    gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=min_size
                )
                
                # Remove overlapping detections
                for (x, y, w, h) in profile_faces:
                    is_duplicate = False
                    for existing_face in detected_faces:
                        ex, ey, ew, eh = existing_face['bbox']
                        if (abs(x - ex) < 50 and abs(y - ey) < 50):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        detected_faces.append({
                            'id': face_id,
                            'type': 'profile',
                            'bbox': (x, y, w, h),
                            'confidence': 0.75,
                            'area': w * h
                        })
                        face_id += 1
            
            return detected_faces
            
        except Exception as e:
            print(f"Error in face detection: {e}")
            return []
    
    def visualize_faces(self, image: np.ndarray, faces: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels around detected faces"""
        try:
            result = image.copy()
            
            # Colors for different detection types
            colors = {
                'frontal': (0, 255, 0),    # Green
                'profile': (255, 255, 0),  # Yellow
                'unknown': (255, 255, 255) # White
            }
            
            for face in faces:
                x, y, w, h = face['bbox']
                face_type = face.get('type', 'unknown')
                color = colors.get(face_type, (255, 255, 255))
                
                # Draw bounding box
                cv2.rectangle(result, (x, y), (x + w, y + h), color, 3)
                
                # Prepare label
                label = f"Face {face['id']}"
                
                # Calculate label position
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                thickness = 2
                
                (label_width, label_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                
                # Draw label background
                label_y = y - 10 if y - 10 > label_height else y + h + label_height + 10
                cv2.rectangle(result, 
                             (x, label_y - label_height - baseline - 5), 
                             (x + label_width + 10, label_y + baseline), 
                             color, -1)
                
                # Draw label text
                cv2.putText(result, label, (x + 5, label_y - 5), 
                           font, font_scale, (0, 0, 0), thickness)
            
            return result
            
        except Exception as e:
            print(f"Error in visualization: {e}")
            return image


class FaceDetectionWorker(QThread):
    """Worker thread for face detection"""
    finished = pyqtSignal(np.ndarray, list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, detector, image, detection_params):
        super().__init__()
        self.detector = detector
        self.image = image
        self.detection_params = detection_params
    
    def run(self):
        try:
            self.progress.emit(25)
            
            # Run face detection
            faces = self.detector.detect_faces(
                self.image,
                self.detection_params['scale_factor'],
                self.detection_params['min_neighbors'],
                self.detection_params['min_size']
            )
            
            self.progress.emit(75)
            
            # Visualize results
            result_image = self.detector.visualize_faces(self.image, faces)
            
            self.progress.emit(100)
            self.finished.emit(result_image, faces)
            
        except Exception as e:
            self.error.emit(str(e))


class FaceDetectionGUI(QMainWindow):
    """Main GUI application for face detection"""
    
    def __init__(self):
        super().__init__()
        self.detector = FaceDetector()
        self.current_image = None
        self.current_faces = []
        self.detection_worker = None
        
        self.init_ui()
        self.setup_styles()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Face Detection Studio")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel for image display
        right_panel = self.create_image_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([350, 1050])
        
        main_layout.addWidget(splitter)
        
    def create_control_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        panel.setFixedWidth(350)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🎯 Face Detection Studio")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # File operations
        file_group = QGroupBox("📁 File Operations")
        file_layout = QVBoxLayout(file_group)
        
        self.load_image_btn = QPushButton("📷 Load Image")
        self.load_image_btn.clicked.connect(self.load_image)
        file_layout.addWidget(self.load_image_btn)
        
        self.save_results_btn = QPushButton("💾 Save Results")
        self.save_results_btn.clicked.connect(self.save_results)
        self.save_results_btn.setEnabled(False)
        file_layout.addWidget(self.save_results_btn)
        
        layout.addWidget(file_group)
        
        # Detection settings
        detection_group = QGroupBox("⚙️ Detection Settings")
        detection_layout = QGridLayout(detection_group)
        
        detection_layout.addWidget(QLabel("Scale Factor:"), 0, 0)
        self.scale_factor = QDoubleSpinBox()
        self.scale_factor.setRange(1.05, 2.0)
        self.scale_factor.setValue(1.1)
        self.scale_factor.setSingleStep(0.05)
        detection_layout.addWidget(self.scale_factor, 0, 1)
        
        detection_layout.addWidget(QLabel("Min Neighbors:"), 1, 0)
        self.min_neighbors = QSpinBox()
        self.min_neighbors.setRange(3, 10)
        self.min_neighbors.setValue(5)
        detection_layout.addWidget(self.min_neighbors, 1, 1)
        
        detection_layout.addWidget(QLabel("Min Face Size:"), 2, 0)
        self.min_face_size = QSpinBox()
        self.min_face_size.setRange(20, 200)
        self.min_face_size.setValue(30)
        detection_layout.addWidget(self.min_face_size, 2, 1)
        
        layout.addWidget(detection_group)
        
        # Detection button and progress
        self.detect_btn = QPushButton("🚀 Detect Faces")
        self.detect_btn.clicked.connect(self.run_detection)
        self.detect_btn.setEnabled(False)
        layout.addWidget(self.detect_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results display
        results_group = QGroupBox("📊 Detection Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        layout.addStretch()
        
        return panel
    
    def create_image_panel(self):
        """Create the right image display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Image display area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.image_label.setText("📸 Load an image to start face detection")
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # Image info
        self.image_info_label = QLabel("No image loaded")
        self.image_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_info_label)
        
        return panel
    
    def setup_styles(self):
        """Setup application styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            #titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                padding: 15px;
                border-radius: 8px;
                margin: 5px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 5px 0px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10px;
            }
            
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px;
            }
        """)
    
    def load_image(self):
        """Load an image file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Image", "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
            )
            
            if file_path:
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.display_image(self.current_image)
                    self.detect_btn.setEnabled(True)
                    file_name = os.path.basename(file_path)
                    h, w = self.current_image.shape[:2]
                    self.image_info_label.setText(f"📁 {file_name} | 📐 {w}×{h} pixels")
                    self.results_text.clear()
                    self.current_faces = []
                    self.save_results_btn.setEnabled(False)
                else:
                    QMessageBox.warning(self, "Error", "Could not load the selected image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading image: {str(e)}")
    
    def run_detection(self):
        """Run face detection"""
        try:
            if self.current_image is None:
                return
            
            # Prepare detection parameters
            detection_params = {
                'scale_factor': self.scale_factor.value(),
                'min_neighbors': self.min_neighbors.value(),
                'min_size': (self.min_face_size.value(), self.min_face_size.value())
            }
            
            # Start detection in worker thread
            self.detection_worker = FaceDetectionWorker(
                self.detector, self.current_image.copy(), detection_params
            )
            self.detection_worker.finished.connect(self.on_detection_finished)
            self.detection_worker.progress.connect(self.progress_bar.setValue)
            self.detection_worker.error.connect(self.on_detection_error)
            
            self.detect_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            self.detection_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting detection: {str(e)}")
            self.detect_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def on_detection_finished(self, result_image, faces):
        """Handle detection completion"""
        try:
            self.current_faces = faces
            self.display_image(result_image)
            self.save_results_btn.setEnabled(True)
            
            # Update results text
            results_text = f"🎯 Face Detection Complete!\n"
            results_text += f"📊 Found {len(faces)} face(s):\n\n"
            
            for face in faces:
                bbox = face['bbox']
                face_type = face.get('type', 'unknown')
                confidence = face.get('confidence', 0)
                
                results_text += f"👤 Face {face['id']}:\n"
                results_text += f"   📍 Position: ({bbox[0]}, {bbox[1]})\n"
                results_text += f"   📏 Size: {bbox[2]}×{bbox[3]} pixels\n"
                results_text += f"   🔍 Type: {face_type.title()}\n"
                results_text += f"   ⭐ Confidence: {confidence:.2f}\n\n"
            
            if len(faces) == 0:
                results_text += "❌ No faces detected.\n"
                results_text += "💡 Try adjusting detection parameters."
            
            self.results_text.setText(results_text)
            
        except Exception as e:
            print(f"Error in detection finished: {e}")
        finally:
            self.detect_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def on_detection_error(self, error_message):
        """Handle detection error"""
        QMessageBox.critical(self, "Detection Error", f"Detection failed: {error_message}")
        self.detect_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def display_image(self, cv_image):
        """Display OpenCV image in QLabel"""
        try:
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale image to fit display
            pixmap = QPixmap.fromImage(qt_image)
            max_width = 800
            max_height = 600
            
            if pixmap.width() > max_width or pixmap.height() > max_height:
                pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.image_label.setPixmap(pixmap)
            self.image_label.adjustSize()
            
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def save_results(self):
        """Save detection results"""
        try:
            if self.current_faces and self.current_image is not None:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Results", "face_detection_results.jpg",
                    "Image Files (*.png *.jpg *.jpeg *.bmp)"
                )
                
                if file_path:
                    result_image = self.detector.visualize_faces(self.current_image, self.current_faces)
                    success = cv2.imwrite(file_path, result_image)
                    
                    if success:
                        QMessageBox.information(self, "Success", f"Results saved to {file_path}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to save the image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving results: {str(e)}")


def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Face Detection Studio")
        
        # Create and show the main window
        window = FaceDetectionGUI()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting application: {e}")


if __name__ == "__main__":
    main()