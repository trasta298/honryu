import asyncio
import ctypes
import io
import os
import sys

import mss
import mss.tools
from dotenv import load_dotenv
from PIL import Image
from PyQt6 import QtCore, QtGui, QtWidgets
from qt_material import apply_stylesheet

from translate_image import (initialize_genai,
                             transcribe_and_translate_image_stream)

load_dotenv()


class SelectWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        api_key = os.getenv("GENAI_API_KEY", "")
        model_name = os.getenv("GENAI_MODEL", "gemini-1.5-flash-002")

        self.model = initialize_genai(api_key, model_name)

        self.total_geometry = QtCore.QRect()
        for screen in QtWidgets.QApplication.screens():
            self.total_geometry = self.total_geometry.united(screen.geometry())

        self.setGeometry(self.total_geometry)
        self.setWindowTitle("")
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.sct = mss.mss()

        self.escape_pressed = False

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.Tool)

        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        qp.setBrush(QtGui.QColor(0, 0, 0, 150))
        qp.setPen(QtCore.Qt.PenStyle.NoPen)
        qp.drawRect(self.rect())

        if not self.begin.isNull() and not self.end.isNull():
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
            rect = QtCore.QRect(self.begin, self.end).normalized()

            qp.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
            qp.drawRect(rect)

            qp.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
            qp.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
            qp.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.position().toPoint()
        self.global_begin = event.globalPosition().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.position().toPoint()
        self.global_end = event.globalPosition().toPoint()
        self.close()

        adjusted_begin = self.adjust_coordinates(self.global_begin)
        adjusted_end = self.adjust_coordinates(self.global_end)

        x1 = int(adjusted_begin.x())
        y1 = int(adjusted_begin.y())
        x2 = int(adjusted_end.x())
        y2 = int(adjusted_end.y())

        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)

        monitor = {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top
        }

        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        asyncio.create_task(self.transcribe_image(img))

    async def transcribe_image(self, img):
        self.result_dialog = ResultDialog()
        self.result_dialog.show()

        with io.BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format='JPEG')
            image_bytes = img_byte_arr.getvalue()

        async for detected_lang, ja_text, en_text in transcribe_and_translate_image_stream(self.model, image_bytes):
            self.result_dialog.update_results(detected_lang, ja_text, en_text)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.escape_pressed = True
            self.close()

    def adjust_coordinates(self, global_pos):
        for screen in QtWidgets.QApplication.screens():
            screen_geometry = screen.geometry()
            if screen_geometry.contains(global_pos):
                local_x = global_pos.x() - screen_geometry.x()
                local_y = global_pos.y() - screen_geometry.y()

                scale_factor = screen.devicePixelRatio()
                scaled_x = local_x * scale_factor
                scaled_y = local_y * scale_factor

                return QtCore.QPoint(
                    int(scaled_x + screen_geometry.x()),
                    int(scaled_y + screen_geometry.y())
                )

        return global_pos


class ResultDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("翻訳結果")
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowMaximizeButtonHint | QtCore.Qt.WindowType.WindowMinimizeButtonHint | QtCore.Qt.WindowType.Window)
        QtWidgets.QApplication.restoreOverrideCursor()

        layout = QtWidgets.QVBoxLayout()

        self.lang_label = QtWidgets.QLabel("detected language: ")
        layout.addWidget(self.lang_label)

        ja_layout = QtWidgets.QHBoxLayout()
        ja_label = QtWidgets.QLabel("Japanese:")
        ja_layout.addWidget(ja_label)
        ja_layout.addStretch()
        ja_copy_button = QtWidgets.QPushButton("copy")
        ja_copy_button.clicked.connect(self.copy_ja_text)
        ja_layout.addWidget(ja_copy_button)
        layout.addLayout(ja_layout)

        self.ja_text_edit = QtWidgets.QPlainTextEdit()
        self.ja_text_edit.setReadOnly(False)
        layout.addWidget(self.ja_text_edit)

        en_layout = QtWidgets.QHBoxLayout()
        en_label = QtWidgets.QLabel("English:")
        en_layout.addWidget(en_label)
        en_layout.addStretch()
        en_copy_button = QtWidgets.QPushButton("copy")
        en_copy_button.clicked.connect(self.copy_en_text)
        en_layout.addWidget(en_copy_button)
        layout.addLayout(en_layout)

        self.en_text_edit = QtWidgets.QPlainTextEdit()
        self.en_text_edit.setReadOnly(False)
        layout.addWidget(self.en_text_edit)

        self.setLayout(layout)

    def update_results(self, detected_lang, ja_text, en_text):
        self.lang_label.setText(f"detected language: {detected_lang}")
        self.ja_text_edit.setPlainText(ja_text)
        self.en_text_edit.setPlainText(en_text)

    def copy_ja_text(self):
        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.ja_text_edit.toPlainText())

    def copy_en_text(self):
        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.en_text_edit.toPlainText())


async def run_app():
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml', extra={"font_size": 18})

    window = SelectWidget()
    window.show()

    while True:
        app.processEvents()
        await asyncio.sleep(0.01)
        # windowが閉じられた際にループを終了する
        if not window.isVisible():
            if window.escape_pressed or (window.result_dialog is None or not window.result_dialog.isVisible()):
                break

    app.quit()

if __name__ == '__main__':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    asyncio.run(run_app())
