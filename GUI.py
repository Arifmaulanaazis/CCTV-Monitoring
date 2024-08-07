import sys
import json
import cv2
import numpy as np
import time
from collections import defaultdict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ultralytics import YOLO
import logging

logging.getLogger('ultralytics').setLevel(logging.WARNING)


model = YOLO('yolov8s.pt') 


with open('label_translation.json') as f:
    label_translation = json.load(f)

with open('urls.json') as f:
    urls_dict = json.load(f)


frame_rate = 30


def hash_to_color(label):
    hash_value = hash(label) % (256 * 256 * 256)
    b = hash_value % 256
    g = (hash_value // 256) % 256
    r = (hash_value // (256 * 256)) % 256
    return (b, g, r)


def process_frame(frame, start_time):
    current_time = time.time() - start_time
    results = model(frame)
    detections = results[0].boxes.data.cpu().numpy()

    object_counts = defaultdict(int)
    current_positions = defaultdict(list)

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        current_positions[label].append((center_x, center_y))
        object_counts[label] += 1

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        color = hash_to_color(label_translation.get(label, label)) 
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

        count = object_counts[label]
        label_text = f"ID: {count} Tipe: {label_translation.get(label, label)}"
        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    return frame


class WorkerSignals(QObject):
    result = pyqtSignal(np.ndarray)


class VideoProcessingWorker(QRunnable):
    def __init__(self, urls, start_time):
        super(VideoProcessingWorker, self).__init__()
        self.urls = urls
        self.start_time = start_time
        self.signals = WorkerSignals()
        self.stop_flag = False
        self.frame_rate = None

    def run(self):
        while not self.stop_flag:
            try:
                caps = [cv2.VideoCapture(url) for url in self.urls]
                frame_rates = [cap.get(cv2.CAP_PROP_FPS) for cap in caps]
                width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

                self.frame_rate = min(frame_rates)

                while not self.stop_flag:
                    frames = [cap.read()[1] for cap in caps]
                    if all(frame is None for frame in frames):
                        continue 
                    else:
                        resized_frames = [cv2.resize(frame, (width, height)) for frame in frames if frame is not None]
                        processed_frames = [process_frame(frame, self.start_time) for frame in resized_frames]

                        grid_size = int(np.ceil(np.sqrt(len(self.urls))))
                        grid_frame = np.zeros((height * grid_size, width * grid_size, 3), dtype=np.uint8)

                        for i, frame in enumerate(processed_frames):
                            row = i // grid_size
                            col = i % grid_size
                            y_offset = row * height
                            x_offset = col * width
                            grid_frame[y_offset:y_offset + height, x_offset:x_offset + width] = frame

                        self.signals.result.emit(grid_frame)
                        time.sleep(1 / self.frame_rate)

            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(1)
                continue

    def stop(self):
        self.stop_flag = True

class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.image = None

    def set_image(self, image):
        self.image = image
        self.update()

    def paintEvent(self, event):
        if self.image is not None:
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)

class DetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Monitoring CCTV")
        self.setGeometry(100, 100, 1675, 875)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.video_widget = VideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_widget)

        self.button_list = QListWidget()
        self.button_list.setFixedWidth(250)
        self.layout.addWidget(self.button_list)

        self.buttons = {}
        self.active_button = None 
        for key in urls_dict:
            button = QPushButton(key)
            button.clicked.connect(self.create_button_handler(key))
            item = QListWidgetItem(self.button_list)
            item.setSizeHint(button.sizeHint())
            self.button_list.setItemWidget(item, button)
            self.buttons[key] = button

        self.thread_pool = QThreadPool()
        self.current_frame = None
        self.start_time = None
        self.current_urls = []
        self.worker = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.setInterval(1000 // 30)

    def create_button_handler(self, key):
        def handler():
            if self.worker:
                self.worker.stop()
            self.current_urls = urls_dict[key]
            self.start_time = time.time()
            self.current_frame = None
            self.process_videos()

            if self.active_button:
                self.active_button.setStyleSheet("background-color: none") 
            self.active_button = self.buttons[key]
            self.active_button.setStyleSheet("background-color: yellow") 
        return handler

    def process_videos(self):
        if not self.current_urls:
            return

        self.worker = VideoProcessingWorker(self.current_urls, self.start_time)
        self.worker.signals.result.connect(self.update_frame)
        self.thread_pool.start(self.worker)
        self.timer.start()

    def update_frame(self, frame=None):
        if frame is not None:
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
            self.video_widget.set_image(q_image)

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DetectionApp()
    window.show()
    sys.exit(app.exec_())
