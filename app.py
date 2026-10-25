"""Vietnamese desktop interface for OmniVoice application - Optimized for seniors & family use with eye-care themes."""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
import os
from PySide6.QtCore import Qt, QTimer, QUrl, QThread, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QTabWidget, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QScrollArea, QProgressBar, QListWidget, QSplitter, QDialog, QDialogButtonBox,
    QPlainTextEdit, QGridLayout, QToolButton, QSizePolicy, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from service import ROOT, Job, GenerationWorker, read_text
from dialogue import parse_dialogue, role_name, NARRATOR
from paths import STATE_ROOT, DEFAULT_OUTPUT

CHECK_ICON = (ROOT / 'assets' / 'check.png').as_posix()
ARROW_ICON_LIGHT = (ROOT / 'assets' / 'arrow_down_white.png').as_posix()
ARROW_ICON_DARK = (ROOT / 'assets' / 'arrow_down.png').as_posix()

# ================= GIAO DIỆN TỐI DỊU MẮT (MẶC ĐỊNH - CHỐNG MỎI MẮT) =================
STYLE_DARK = f"""
QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
    color: #e2e8f0;
}}
QMainWindow, #page {{
    background-color: #1a202c;
}}

QLabel#app_title {{
    font-size: 23px;
    font-weight: 800;
    color: #60a5fa;
}}
QLabel#app_subtitle {{
    font-size: 13px;
    color: #94a3b8;
}}

QGroupBox {{
    background-color: #242c3d;
    border: 1.5px solid #3b4758;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 10px 12px;
    font-size: 15px;
    font-weight: 700;
    color: #93c5fd;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 8px;
    background-color: #242c3d;
    border-radius: 4px;
}}

QPushButton, QToolButton {{
    background-color: #2d3748;
    border: 1.5px solid #4a5568;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 14px;
    min-height: 24px;
    color: #f1f5f9;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: #3b4758;
    border-color: #60a5fa;
    color: #ffffff;
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: #1e2634;
}}
QPushButton:disabled {{
    background-color: #1e2430;
    border-color: #2d3748;
    color: #64748b;
}}

QPushButton#btn_generate {{
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    border-radius: 10px;
    color: #ffffff;
    font-size: 16px;
    font-weight: 800;
    padding: 10px 24px;
    min-height: 28px;
}}
QPushButton#btn_generate:hover {{
    background-color: #1d4ed8;
}}
QPushButton#btn_generate:disabled {{
    background-color: #1e3a5f;
    border-color: #2563eb;
    color: #64748b;
}}

QPushButton#btn_stop {{
    background-color: #dc2626;
    border: 1px solid #ef4444;
    border-radius: 10px;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    padding: 10px 20px;
    min-height: 28px;
}}
QPushButton#btn_stop:hover {{
    background-color: #b91c1c;
}}
QPushButton#btn_stop:disabled {{
    background-color: #451a1a;
    border-color: #5c2020;
    color: #7f3d3d;
}}

QPushButton#btn_preview {{
    background-color: #0284c7;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 14px;
}}
QPushButton#btn_preview:hover {{
    background-color: #0369a1;
}}

QPushButton#btn_play_result {{
    background-color: #16a34a;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 16px;
}}
QPushButton#btn_play_result:hover {{
    background-color: #15803d;
}}
QPushButton#btn_play_result:disabled {{
    background-color: #143823;
    color: #4ade80;
}}

QPushButton#btn_open_folder {{
    background-color: #475569;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 14px;
}}
QPushButton#btn_open_folder:hover {{
    background-color: #334155;
}}

QPushButton.speed_preset {{
    background-color: #2d3748;
    border: 1px solid #4a5568;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 13px;
    font-weight: 600;
    color: #cbd5e1;
}}
QPushButton.speed_preset:hover {{
    background-color: #3b4758;
    color: #ffffff;
}}

QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget {{
    background-color: #19202b;
    border: 1.5px solid #414f63;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 14px;
    color: #f1f5f9;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}}
QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #60a5fa;
    background-color: #1a2330;
}}

QComboBox {{
    min-height: 26px;
    padding-right: 24px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: url({ARROW_ICON_LIGHT});
    width: 14px;
    height: 14px;
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: #1e2634;
    border: 1px solid #414f63;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    color: #f1f5f9;
}}

QTabWidget::pane {{
    border: 1.5px solid #3b4758;
    border-radius: 10px;
    background-color: #242c3d;
    padding: 6px;
}}
QTabBar::tab {{
    background-color: #1e2634;
    color: #94a3b8;
    font-weight: 700;
    font-size: 14px;
    padding: 8px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background-color: #2563eb;
    color: #ffffff;
}}
QTabBar::tab:hover:!selected {{
    background-color: #2d3748;
    color: #e2e8f0;
}}

QCheckBox {{
    spacing: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #e2e8f0;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #64748b;
    border-radius: 4px;
    background-color: #19202b;
}}
QCheckBox::indicator:hover {{
    border-color: #60a5fa;
}}
QCheckBox::indicator:checked {{
    background-color: #2563eb;
    border-color: #2563eb;
    image: url({CHECK_ICON});
}}

QProgressBar {{
    border: 1px solid #414f63;
    border-radius: 6px;
    background-color: #19202b;
    text-align: center;
    font-weight: 700;
    font-size: 12px;
    color: #e2e8f0;
    min-height: 16px;
    max-height: 16px;
}}
QProgressBar::chunk {{
    background-color: #3b82f6;
    border-radius: 5px;
}}

#status_box {{
    background-color: #0f291e;
    border: 1.5px solid #22c55e;
    border-radius: 8px;
    padding: 6px 12px;
}}
#status_text {{
    font-size: 14px;
    font-weight: 700;
    color: #86efac;
}}

QScrollBar:vertical {{
    width: 10px;
    background-color: #1a202c;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: #3b4758;
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: #4a5568;
}}
"""

# ================= GIAO DIỆN SÁNG (TÙY CHỌN DỰ PHÒNG) =================
STYLE_LIGHT = f"""
QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
    color: #0f172a;
}}
QMainWindow, #page {{
    background-color: #f1f5f9;
}}

QLabel#app_title {{
    font-size: 23px;
    font-weight: 800;
    color: #1e3a8a;
}}
QLabel#app_subtitle {{
    font-size: 13px;
    color: #475569;
}}

QGroupBox {{
    background-color: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 10px 12px;
    font-size: 15px;
    font-weight: 700;
    color: #1e40af;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 8px;
    background-color: #ffffff;
    border-radius: 4px;
}}

QPushButton, QToolButton {{
    background-color: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 14px;
    min-height: 24px;
    color: #1e293b;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: #e2e8f0;
}}
QPushButton:disabled {{
    background-color: #f1f5f9;
    border-color: #e2e8f0;
    color: #94a3b8;
}}

QPushButton#btn_generate {{
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    border-radius: 10px;
    color: #ffffff;
    font-size: 16px;
    font-weight: 800;
    padding: 10px 24px;
    min-height: 28px;
}}
QPushButton#btn_generate:hover {{
    background-color: #1d4ed8;
}}
QPushButton#btn_generate:disabled {{
    background-color: #93c5fd;
    border-color: #bfdbfe;
    color: #ffffff;
}}

QPushButton#btn_stop {{
    background-color: #ef4444;
    border: 1px solid #dc2626;
    border-radius: 10px;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    padding: 10px 20px;
    min-height: 28px;
}}
QPushButton#btn_stop:hover {{
    background-color: #dc2626;
}}
QPushButton#btn_stop:disabled {{
    background-color: #fca5a5;
    border-color: #fecaca;
    color: #ffffff;
}}

QPushButton#btn_preview {{
    background-color: #0284c7;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 14px;
}}
QPushButton#btn_preview:hover {{
    background-color: #0369a1;
}}

QPushButton#btn_play_result {{
    background-color: #16a34a;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 16px;
}}
QPushButton#btn_play_result:hover {{
    background-color: #15803d;
}}
QPushButton#btn_play_result:disabled {{
    background-color: #86efac;
    color: #ffffff;
}}

QPushButton#btn_open_folder {{
    background-color: #475569;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 8px 14px;
}}
QPushButton#btn_open_folder:hover {{
    background-color: #334155;
}}

QPushButton.speed_preset {{
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
}}
QPushButton.speed_preset:hover {{
    background-color: #e2e8f0;
    color: #0f172a;
}}

QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget {{
    background-color: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 14px;
    color: #0f172a;
    selection-background-color: #bfdbfe;
    selection-color: #0f172a;
}}
QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #2563eb;
    background-color: #ffffff;
}}

QComboBox {{
    min-height: 26px;
    padding-right: 24px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: url({ARROW_ICON_DARK});
    width: 14px;
    height: 14px;
    margin-right: 6px;
}}

QTabWidget::pane {{
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    background-color: #ffffff;
    padding: 6px;
}}
QTabBar::tab {{
    background-color: #e2e8f0;
    color: #475569;
    font-weight: 700;
    font-size: 14px;
    padding: 8px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background-color: #2563eb;
    color: #ffffff;
}}
QTabBar::tab:hover:!selected {{
    background-color: #cbd5e1;
}}

QCheckBox {{
    spacing: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #64748b;
    border-radius: 4px;
    background-color: #ffffff;
}}
QCheckBox::indicator:hover {{
    border-color: #2563eb;
}}
QCheckBox::indicator:checked {{
    background-color: #2563eb;
    border-color: #2563eb;
    image: url({CHECK_ICON});
}}

QProgressBar {{
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background-color: #e2e8f0;
    text-align: center;
    font-weight: 700;
    font-size: 12px;
    color: #1e293b;
    min-height: 16px;
    max-height: 16px;
}}
QProgressBar::chunk {{
    background-color: #2563eb;
    border-radius: 5px;
}}

#status_box {{
    background-color: #f0fdf4;
    border: 1.5px solid #bbf7d0;
    border-radius: 8px;
    padding: 6px 12px;
}}
#status_text {{
    font-size: 14px;
    font-weight: 700;
    color: #166534;
}}

QScrollBar:vertical {{
    width: 10px;
    background-color: #f1f5f9;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: #cbd5e1;
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: #94a3b8;
}}
"""

STYLE = STYLE_DARK

class VoiceScanWorker(QThread):
    ready = Signal(object)
    failed = Signal(str)
    def run(self):
        try:
            from process.tts import voice_manager
            voice_manager._audio_duration = lambda path: 0.0
            voice_manager.voice_search_dirs = lambda extra_dirs=None: [str(ROOT/'data'/'voices')]
            self.ready.emit(voice_manager.scan_voices())
        except Exception as exc:
            self.failed.emit(str(exc))

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Omni Voice — Đọc Truyện & Văn Bản Thành Giọng Nói')
        self.resize(1180, 820)
        self.setMinimumSize(960, 680)
        self.worker = None
        self.voices = []
        self.dialogue_script = parse_dialogue('')
        self.role_voices = {}
        self.role_combos = {}
        self.outputs = []
        self.dictionary = []
        self.pauses = {'enabled': False}
        self.is_dark_theme = True
        self._restoring = True
        self._close_after_stop = False
        self.audio = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.player.errorOccurred.connect(lambda error, msg: self.set_status('Không phát được âm thanh: ' + msg, error=True))
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_session)
        self.dialogue_timer = QTimer(self)
        self.dialogue_timer.setSingleShot(True)
        self.dialogue_timer.timeout.connect(self.identify_dialogue)
        self.build()
        self.restore_session()
        self._restoring = False
        self.apply_theme()
        self.scan = VoiceScanWorker(self)
        self.scan.ready.connect(self.voices_ready)
        self.scan.failed.connect(lambda msg: self.set_status('Không đọc được danh sách giọng: ' + msg, error=True))
        self.scan.start()

    def button(self, text, handler, obj_name=None):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        if obj_name:
            btn.setObjectName(obj_name)
        return btn

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        self.schedule_save()

    def apply_theme(self):
        sheet = STYLE_DARK if self.is_dark_theme else STYLE_LIGHT
        self.setStyleSheet(sheet)
        self.btn_theme.setText('Chế độ: Dịu mắt (Tối)' if self.is_dark_theme else 'Chế độ: Sáng')
        # Re-apply current status styling
        current_status = self.status.text()
        is_err = 'Không' in current_status or 'Lỗi' in current_status or '⚠️' in current_status
        is_run = 'Đang' in current_status or 'chờ' in current_status
        self.set_status(current_status, error=is_err, running=is_run)
        base, border = ('#1a202c', '#475569') if self.is_dark_theme else ('#ffffff', '#cbd5e1')
        surface = '#242c3d' if self.is_dark_theme else '#ffffff'
        self.right_scroll.setStyleSheet(f'QScrollArea {{background:{surface};border:0;}} QWidget#voice_controls {{background:{surface};}}')
        self.role_table.setStyleSheet(f'QTableWidget {{background:{base}; border:1px solid {border}; gridline-color:{border};}} QHeaderView::section {{background:{base}; padding:5px; border:1px solid {border};}}')

    def set_status(self, text, error=False, running=False):
        self.status.setText(text)
        if self.is_dark_theme:
            if error:
                self.status_box.setStyleSheet("background-color: #451a1a; border: 1.5px solid #ef4444; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #fca5a5;")
            elif running:
                self.status_box.setStyleSheet("background-color: #422006; border: 1.5px solid #f59e0b; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #fde047;")
            else:
                self.status_box.setStyleSheet("background-color: #0f291e; border: 1.5px solid #22c55e; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #86efac;")
        else:
            if error:
                self.status_box.setStyleSheet("background-color: #fef2f2; border: 1.5px solid #fecaca; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #b91c1c;")
            elif running:
                self.status_box.setStyleSheet("background-color: #fefce8; border: 1.5px solid #fef08a; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #854d0e;")
            else:
                self.status_box.setStyleSheet("background-color: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 6px 12px;")
                self.status.setStyleSheet("font-size: 14px; font-weight: 700; color: #166534;")

    def build(self):
        page = QWidget()
        page.setObjectName('page')
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        # ------------------- HEADER -------------------
        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        title = QLabel('Omni Voice — Đọc Truyện và Văn Bản Thành Giọng Nói')
        title.setObjectName('app_title')
        header_text.addWidget(title)
        subtitle = QLabel('Chuyển văn bản thành giọng đọc tự nhiên, ấm áp · Giao diện dịu mắt, dễ nhìn, dễ sử dụng cho gia đình')
        subtitle.setObjectName('app_subtitle')
        header_text.addWidget(subtitle)
        header.addLayout(header_text, 1)

        self.btn_theme = self.button('Chế độ: Dịu mắt (Tối)', self.toggle_theme)
        self.btn_theme.setToolTip('Bấm vào đây để chuyển đổi màu nền Sáng hoặc Dịu mắt')
        header.addWidget(self.btn_theme)

        log_toggle = QToolButton()
        log_toggle.setText('Nhật ký xử lý')
        log_toggle.setCheckable(True)
        log_toggle.setCursor(Qt.PointingHandCursor)
        header.addWidget(log_toggle)
        layout.addLayout(header)

        # ------------------- THÂN CHÍNH (2 CỘT) -------------------
        main_content = QHBoxLayout()
        main_content.setSpacing(12)

        # === CỘT TRÁI: BƯỚC 1 (NỘI DUNG CẦN ĐỌC) ===
        left_box = QGroupBox('[ BƯỚC 1 ] CHỌN NỘI DUNG CẦN ĐỌC')
        left_box.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        ll = QVBoxLayout(left_box)
        ll.setContentsMargins(10, 12, 10, 8)
        ll.setSpacing(6)

        self.mode = QTabWidget()
        
        # Tab 1: Đoạn văn bản
        tab_single = QWidget()
        ts_layout = QVBoxLayout(tab_single)
        ts_layout.setContentsMargins(4, 6, 4, 4)
        ts_layout.setSpacing(6)

        btn_row = QHBoxLayout()
        btn_open_txt = self.button('Mở tệp văn bản (.txt)', self.load_text)
        btn_open_sub = self.button('Mở tệp phụ đề (.srt)', self.load_subtitle)
        btn_row.addWidget(btn_open_txt)
        btn_row.addWidget(btn_open_sub)
        btn_row.addStretch()
        ts_layout.addLayout(btn_row)

        self.text = QTextEdit()
        self.text.setPlaceholderText('Nhấp chuột vào đây rồi gõ hoặc dán nội dung muốn đọc…')
        self.text.setMinimumHeight(130)
        self.text.textChanged.connect(self.schedule_save)
        ts_layout.addWidget(self.text, 1)

        tool_row = QHBoxLayout()
        tool_row.addWidget(self.button('Chèn khoảng nghỉ', self.insert_pause))
        tool_row.addWidget(self.button('Từ điển phát âm', self.edit_dictionary))
        tool_row.addWidget(self.button('Nghỉ theo dấu câu', self.edit_pauses))
        tool_row.addStretch()
        ts_layout.addLayout(tool_row)

        self.mode.addTab(tab_single, '  Đoạn văn bản  ')

        # Tab 2: labelled dialogue, preserving the user's existing layout/theme.
        tab_dialogue = QWidget()
        td_layout = QVBoxLayout(tab_dialogue)
        td_layout.setContentsMargins(4, 6, 4, 4)
        td_layout.setSpacing(6)
        dialogue_buttons = QHBoxLayout()
        dialogue_buttons.addWidget(self.button('Mở hội thoại (.txt)', self.load_text))
        dialogue_buttons.addWidget(self.button('Nhận diện lại các vai', self.identify_dialogue))
        dialogue_buttons.addStretch()
        td_layout.addLayout(dialogue_buttons)
        self.dialogue_text = QTextEdit()
        self.dialogue_text.setMinimumHeight(130)
        self.dialogue_text.setPlaceholderText('Dán toàn bộ bài nghe, gồm cả hướng dẫn và hội thoại.\n\nPart II. Listen to a conversation…\nLan: Hi, Duy.\nDuy: Yes, I am.\nNow listen again\nLan: Hi, Duy.\nDuy: Yes, I am.')
        self.dialogue_text.textChanged.connect(self.dialogue_changed)
        td_layout.addWidget(self.dialogue_text, 1)
        self.dialogue_summary = QLabel('Nhập hội thoại có nhãn Tên: lời thoại. Các vai sẽ được nhận diện tự động.')
        self.dialogue_summary.setWordWrap(True)
        td_layout.addWidget(self.dialogue_summary)
        dialogue_help = QLabel('Lời dẫn giữ phần hướng dẫn và “Now listen again”. Tên vai không được đọc thành tiếng.')
        dialogue_help.setWordWrap(True)
        td_layout.addWidget(dialogue_help)
        self.mode.addTab(tab_dialogue, '  Nhiều giọng / Vai thoại  ')
        self.mode.currentChanged.connect(self.mode_changed)
        ll.addWidget(self.mode, 1)

        main_content.addWidget(left_box, 55)

        # === CỘT PHẢI: BƯỚC 2 (CHỌN GIỌNG & CÀI ĐẶT) ===
        right_box = QGroupBox('[ BƯỚC 2 ] CHỌN GIỌNG ĐỌC && CÁCH ĐỌC')
        right_content = QWidget()
        right_content.setObjectName('voice_controls')
        rl = QVBoxLayout(right_content)
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setFrameShape(QScrollArea.NoFrame)
        self.right_scroll.setWidget(right_content)
        self.right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_box.setMinimumWidth(505)
        right_outer = QVBoxLayout(right_box)
        right_outer.setContentsMargins(0, 6, 0, 0)
        right_outer.addWidget(self.right_scroll)
        rl.setContentsMargins(10, 12, 10, 8)
        rl.setSpacing(6)

        filter_row = QHBoxLayout()
        self.language = QComboBox()
        self.language.addItems(['Tiếng Việt', 'Tất cả ngôn ngữ', 'English', 'Chinese', 'Japanese', 'Korean', 'French', 'Thai'])
        self.gender = QComboBox()
        self.gender.addItems(['Tất cả', 'Giọng nữ', 'Giọng nam'])
        filter_row.addWidget(QLabel('Ngôn ngữ:'))
        filter_row.addWidget(self.language, 1)
        filter_row.addWidget(QLabel('Giới tính:'))
        filter_row.addWidget(self.gender, 1)
        rl.addLayout(filter_row)

        self.single_voice_section = QWidget()
        single_layout = QVBoxLayout(self.single_voice_section)
        single_layout.setContentsMargins(0, 0, 0, 0)
        self.voice = QComboBox()
        self.voice.setMinimumHeight(32)
        self.voice.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.voice.setMinimumContentsLength(15)
        single_layout.addWidget(self.voice)

        self.voice_hint = QLabel('Đang nạp danh mục giọng đọc…')
        self.voice_hint.setStyleSheet('color: #94a3b8; font-size: 13px;')
        single_layout.addWidget(self.voice_hint)

        voice_btn_row = QHBoxLayout()
        btn_preview = self.button('▶ Nghe thử giọng này', self.preview, 'btn_preview')
        btn_stop_preview = self.button('■ Dừng nghe', self.player.stop)
        voice_btn_row.addWidget(btn_preview, 1)
        voice_btn_row.addWidget(btn_stop_preview)
        single_layout.addLayout(voice_btn_row)
        rl.addWidget(self.single_voice_section)

        self.language.currentIndexChanged.connect(self.filter_voices)
        self.gender.currentIndexChanged.connect(self.filter_voices)
        self.voice.currentIndexChanged.connect(self.voice_selected)

        self.role_section = QWidget()
        self.role_section.setMinimumHeight(260)
        role_layout = QVBoxLayout(self.role_section)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(4)
        role_layout.addWidget(QLabel('Chọn giọng riêng cho từng vai (kể cả Lời dẫn):'))
        self.role_table = QTableWidget(0, 3)
        self.role_table.setHorizontalHeaderLabels(['Vai / số lượt', 'Giọng đọc', 'Nghe mẫu'])
        self.role_table.verticalHeader().hide()
        self.role_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.role_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.role_table.setMinimumHeight(170)
        self.role_table.setMaximumHeight(185)
        self.role_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.role_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.role_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        role_layout.addWidget(self.role_table)
        gap_row = QHBoxLayout()
        gap_row.addWidget(QLabel('Nghỉ giữa hai lượt:'))
        self.turn_gap = self.number(0, 5, 0.4, 0.1)
        self.turn_gap.setSuffix(' giây')
        gap_row.addWidget(self.turn_gap)
        gap_row.addStretch()
        role_layout.addLayout(gap_row)
        self.role_section.setVisible(False)
        rl.addWidget(self.role_section)

        # Tốc độ đọc
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel('Tốc độ đọc:'))
        self.speed = self.number(0.5, 2.0, 1.0, 0.05)
        self.speed.setSuffix(' x')
        self.speed.setMinimumWidth(75)
        speed_row.addWidget(self.speed)

        for label, val in [('Chậm 0.8x', 0.8), ('Chuẩn 1.0x', 1.0), ('Nhanh 1.2x', 1.2)]:
            b = QPushButton(label)
            b.setProperty('class', 'speed_preset')
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, v=val: self.speed.setValue(v))
            speed_row.addWidget(b)
        speed_row.addStretch()
        rl.addLayout(speed_row)

        # Âm lượng
        vol_row = QHBoxLayout()
        vol_row.addWidget(QLabel('Độ to (Âm lượng):'))
        self.volume = self.number(0.1, 2.0, 1.0, 0.1)
        self.volume.setSuffix(' x')
        self.volume.setMinimumWidth(75)
        vol_row.addWidget(self.volume)
        vol_row.addStretch()
        rl.addLayout(vol_row)

        # Nơi lưu
        out_row = QHBoxLayout()
        self.output_dir = QLineEdit(str(DEFAULT_OUTPUT))
        self.output_dir.textChanged.connect(self.schedule_save)
        btn_choose_out = self.button('Đổi nơi lưu…', self.choose_output)
        out_row.addWidget(self.output_dir, 1)
        out_row.addWidget(btn_choose_out)
        rl.addLayout(out_row)

        fmt_row = QHBoxLayout()
        self.format = QComboBox()
        self.format.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.format.setMinimumContentsLength(10)
        for label, value in [('MP3 — Nhẹ, tiện nghe loa/điện thoại', 'mp3'), ('WAV — Gốc sắc nét', 'wav'), ('FLAC', 'flac'), ('OGG', 'ogg')]:
            self.format.addItem(label, value)
        self.srt = QCheckBox('Kèm phụ đề (.srt)')
        self.srt.setChecked(True)
        fmt_row.addWidget(QLabel('Định dạng:'))
        fmt_row.addWidget(self.format, 1)
        fmt_row.addWidget(self.srt)
        rl.addLayout(fmt_row)

        # Cài đặt nâng cao (Gập lại)
        adv_toggle_row = QHBoxLayout()
        adv_btn = QToolButton()
        adv_btn.setText('Cài đặt nâng cao (GPU / Độ nét)')
        adv_btn.setCheckable(True)
        adv_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        adv_btn.setArrowType(Qt.RightArrow)
        adv_toggle_row.addWidget(adv_btn)
        adv_toggle_row.addStretch()
        rl.addLayout(adv_toggle_row)

        self.advanced = QWidget()
        al = QFormLayout(self.advanced)
        al.setContentsMargins(6, 6, 6, 6)
        self.device = QComboBox()
        self.device.addItem('Tự động dùng GPU nếu có', 'auto')
        self.device.addItem('Chỉ dùng CPU (chậm hơn)', 'cpu')
        self.pitch = self.number(0.5, 2.0, 1.0, 0.05)
        self.steps = QComboBox()
        self.steps.addItems(['1', '2', '4', '8', '16', '32', '64'])
        self.steps.setCurrentText('32')
        self.guidance = self.number(1.0, 4.0, 3.0, 0.5)
        self.temperature = self.number(0.1, 1.0, 0.1, 0.1)
        self.postprocess = QCheckBox('Làm mượt âm thanh')
        self.postprocess.setChecked(True)
        self.watermark = QCheckBox('Chèn lời nhận diện kênh')
        self.watermark_text = QLineEdit()
        self.watermark_text.setPlaceholderText('Ví dụ: Bạn đang nghe truyện…')
        self.interval = QSpinBox()
        self.interval.setRange(1, 60)
        self.interval.setValue(10)
        self.interval.setSuffix(' phút')

        al.addRow('Bộ xử lý:', self.device)
        al.addRow('Độ cao giọng (Pitch):', self.pitch)
        al.addRow('Số bước sinh (Steps):', self.steps)
        al.addRow('Độ chuẩn (Guidance):', self.guidance)
        al.addRow('Nhiệt độ (Temp):', self.temperature)
        al.addRow('', self.postprocess)
        al.addRow('', self.watermark)
        al.addRow('Lời nhận diện:', self.watermark_text)
        al.addRow('Lặp lại mỗi:', self.interval)
        self.advanced.setVisible(False)
        adv_btn.toggled.connect(lambda checked: (self.advanced.setVisible(checked), adv_btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)))
        rl.addWidget(self.advanced)

        rl.addStretch()
        main_content.addWidget(right_box, 45)
        content_widget = QWidget()
        content_widget.setLayout(main_content)
        layout.addWidget(content_widget, 1)

        # ------------------- KHỐI NHẬT KÝ CHI TIẾT (ẨN MẶC ĐỊNH) -------------------
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(90)
        self.log.setVisible(False)
        log_toggle.toggled.connect(self.log.setVisible)
        layout.addWidget(self.log)

        # ------------------- BƯỚC 3: HÀNH ĐỘNG & KẾT QUẢ (FOOTER) -------------------
        footer_box = QGroupBox('[ BƯỚC 3 ] BẮT ĐẦU TẠO GIỌNG ĐỌC && KẾT QUẢ')
        fl = QVBoxLayout(footer_box)
        fl.setContentsMargins(12, 12, 12, 8)
        fl.setSpacing(6)

        # Hàng trạng thái + Nút tạo chính
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.status_box = QFrame()
        self.status_box.setObjectName('status_box')
        sb_layout = QHBoxLayout(self.status_box)
        sb_layout.setContentsMargins(8, 4, 8, 4)
        self.status = QLabel('Đã sẵn sàng. Bấm nút "BẮT ĐẦU TẠO GIỌNG ĐỌC" để chạy!')
        self.status.setObjectName('status_text')
        self.status.setWordWrap(True)
        sb_layout.addWidget(self.status)
        action_row.addWidget(self.status_box, 1)

        self.create = self.button('▶  BẮT ĐẦU TẠO GIỌNG ĐỌC', self.generate, 'btn_generate')
        self.stop = self.button('■ DỪNG LẠI', self.stop_generation, 'btn_stop')
        self.stop.setEnabled(False)
        action_row.addWidget(self.create)
        action_row.addWidget(self.stop)
        fl.addLayout(action_row)

        # Thanh tiến trình
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        fl.addWidget(self.progress)

        # Hàng nghe kết quả & mở thư mục
        result_row = QHBoxLayout()
        result_row.setSpacing(8)
        lbl_res = QLabel('Bài vừa tạo:')
        lbl_res.setStyleSheet('font-weight:700;')
        result_row.addWidget(lbl_res)

        self.result_list = QComboBox()
        self.result_list.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.result_list.setMinimumContentsLength(20)
        result_row.addWidget(self.result_list, 1)

        self.play_result = self.button('▶ Nghe bài này', self.listen_result, 'btn_play_result')
        self.play_result.setEnabled(False)
        result_row.addWidget(self.play_result)

        btn_open_out = self.button('Mở thư mục lưu', self.open_output, 'btn_open_folder')
        result_row.addWidget(btn_open_out)
        fl.addLayout(result_row)

        layout.addWidget(footer_box)

        self.setCentralWidget(page)
        self.input_area = content_widget

        # Lưu thay đổi tự động
        for widget in (self.srt, self.postprocess, self.watermark):
            widget.toggled.connect(self.schedule_save)
        for widget in (self.interval,):
            widget.valueChanged.connect(self.schedule_save)
        for widget in (self.format, self.device, self.steps):
            widget.currentIndexChanged.connect(self.schedule_save)
        self.watermark_text.textChanged.connect(self.schedule_save)

    def number(self, low, high, value, step):
        widget = QDoubleSpinBox()
        widget.setRange(low, high)
        widget.setValue(value)
        widget.setSingleStep(step)
        widget.setDecimals(2)
        widget.valueChanged.connect(self.schedule_save)
        return widget

    def voices_ready(self, voices):
        self.voices = voices
        self.filter_voices()

    def filter_voices(self, *args):
        selected = self.voice.currentData() or getattr(self, 'saved_voice', None)
        self.voice.blockSignals(True)
        self.voice.clear()
        lang = {'Tiếng Việt': 'Vietnamese', 'Tất cả ngôn ngữ': ''}.get(self.language.currentText(), self.language.currentText())
        gender = {'Tất cả': '', 'Giọng nữ': 'female', 'Giọng nam': 'male'}[self.gender.currentText()]
        filtered = [v for v in self.voices if (not lang or v.language.lower() == lang.lower()) and (not gender or v.gender.lower() == gender)]
        self.filtered_voices = filtered
        for v in filtered:
            self.voice.addItem(v.name, v.path)
        i = self.voice.findData(selected)
        if i >= 0:
            self.voice.setCurrentIndex(i)
        self.voice.blockSignals(False)
        hint_color = '#94a3b8' if self.is_dark_theme else '#64748b'
        self.voice_hint.setStyleSheet(f'color: {hint_color}; font-size: 13px;')
        self.voice_hint.setText(f'Có {len(filtered)} giọng phù hợp. Bấm "Nghe thử" để nghe mẫu!' if filtered else 'Không có giọng phù hợp. Hãy chọn lại bộ lọc.')
        self.schedule_save()
        self.refresh_roles()

    def mode_changed(self, index):
        self.single_voice_section.setVisible(index == 0)
        self.role_section.setVisible(index == 1)
        if index == 1:
            if not self.dialogue_text.toPlainText().strip() and self.text.toPlainText().strip():
                self.dialogue_text.setPlainText(self.text.toPlainText())
            self.identify_dialogue()
        self.schedule_save()

    def dialogue_changed(self):
        self.dialogue_timer.start(500)
        self.schedule_save()

    def identify_dialogue(self):
        self.dialogue_timer.stop()
        self.dialogue_script = parse_dialogue(self.dialogue_text.toPlainText())
        characters = [r for r in self.dialogue_script.roles if r != NARRATOR]
        summary = f'{len(characters)} nhân vật · {len(self.dialogue_script.turns)} lượt đọc (gồm lời dẫn).'
        if not self.dialogue_script.turns:
            summary = 'Nhập hội thoại có nhãn Tên: lời thoại để nhận diện các vai.'
        if self.dialogue_script.warnings:
            summary += '\n' + ' '.join(self.dialogue_script.warnings)
        self.dialogue_summary.setText(summary)
        self.refresh_roles()

    def refresh_roles(self):
        if not hasattr(self, 'role_table'):
            return
        roles = self.dialogue_script.roles
        for row in range(self.role_table.rowCount()):
            for column in (1, 2):
                old_widget = self.role_table.cellWidget(row, column)
                if old_widget:
                    old_widget.blockSignals(True)
                    old_widget.hide()
        self.role_table.setRowCount(0)
        self.role_table.setRowCount(len(roles))
        self.role_combos = {}
        for row, role in enumerate(roles):
            count = sum(t.role == role for t in self.dialogue_script.turns)
            label = QTableWidgetItem(f'{role_name(role)} ({count})')
            label.setToolTip('Lời hướng dẫn và các câu không có nhãn nhân vật' if role == NARRATOR else 'Tên lấy từ nhãn thoại, không đọc thành tiếng')
            self.role_table.setItem(row, 0, label)
            combo = QComboBox()
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(10)
            combo.addItem('— Chọn giọng —', '')
            selected = self.role_voices.get(role, '')
            available = list(getattr(self, 'filtered_voices', self.voices))
            # A filter change must not discard an assignment already made.
            chosen = next((v for v in self.voices if v.path == selected), None)
            if chosen and all(v.path != selected for v in available):
                available.insert(0, chosen)
            for voice in available:
                combo.addItem(voice.name, voice.path)
            index = combo.findData(selected)
            combo.setCurrentIndex(index if index >= 0 else 0)
            combo.currentIndexChanged.connect(lambda _, r=role, c=combo: self.assign_role(r, c.currentData()))
            self.role_combos[role] = combo
            self.role_table.setCellWidget(row, 1, combo)
            button = self.button('▶ Mẫu', lambda _, r=role: self.preview_role(r))
            button.setToolTip('Nghe mẫu giọng của ' + role_name(role))
            self.role_table.setCellWidget(row, 2, button)
            self.role_table.setRowHeight(row, 42)

    def assign_role(self, role, path):
        self.player.stop()
        self.role_voices[role] = path or ''
        self.schedule_save()

    def preview_role(self, role):
        path = self.role_voices.get(role)
        if path:
            self.play(path)
        else:
            self.set_status('Hãy chọn giọng cho ' + role_name(role) + ' trước khi nghe mẫu.', error=True)

    def voice_selected(self, *args):
        self.player.stop()
        self.schedule_save()

    def preview(self):
        path = self.voice.currentData()
        if path:
            self.play(path)

    def play(self, path):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def listen_result(self):
        path = self.result_list.currentData()
        if path:
            self.play(path)

    def open_output(self):
        path = Path(self.output_dir.text()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, 'Chọn nơi lưu âm thanh', self.output_dir.text())
        if path:
            self.output_dir.setText(path)

    def load_text(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Mở tệp văn bản', '', 'Văn bản (*.txt)')
        if path:
            try:
                target = self.dialogue_text if self.mode.currentIndex() == 1 else self.text
                target.setPlainText(read_text(path))
            except Exception as exc:
                QMessageBox.warning(self, 'Không mở được tệp', str(exc))

    def load_subtitle(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Mở tệp phụ đề', '', 'Phụ đề (*.srt *.vtt *.ass)')
        if path:
            try:
                from process.tts.subtitle_parser import maybe_convert_subtitle_text
                self.text.setPlainText(maybe_convert_subtitle_text(read_text(path)))
            except Exception as exc:
                QMessageBox.warning(self, 'Không mở được phụ đề', str(exc))

    def insert_pause(self):
        from PySide6.QtWidgets import QInputDialog
        seconds, ok = QInputDialog.getDouble(self, 'Chèn khoảng nghỉ', 'Nghỉ bao nhiêu giây?', 0.5, 0.1, 60, 1)
        if ok:
            self.text.textCursor().insertText(f'<break time={int(seconds*1000)}ms/>')

    def edit_dictionary(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Từ điển phát âm')
        dialog.resize(500, 360)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('Mỗi dòng ghi: từ gốc = cách đọc\nVí dụ:\nAI = ây ai\nDr = bác sĩ'))
        edit = QPlainTextEdit()
        edit.setPlainText('\n'.join(f"{d['word']} = {d['pronunciation']}" for d in self.dictionary))
        layout.addWidget(edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText('Lưu')
        buttons.button(QDialogButtonBox.Cancel).setText('Hủy')
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec():
            entries = []
            for line in edit.toPlainText().splitlines():
                if '=' in line:
                    old, new = line.split('=', 1)
                    if old.strip() and new.strip():
                        entries.append({'word': old.strip(), 'pronunciation': new.strip()})
            self.dictionary = entries
            self.schedule_save()

    def edit_pauses(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Nghỉ theo dấu câu')
        layout = QFormLayout(dialog)
        enabled = QCheckBox('Tự thêm khoảng nghỉ theo dấu câu')
        enabled.setChecked(self.pauses.get('enabled', False))
        layout.addRow(enabled)
        fields = {}
        for name, label in [('period', 'Dấu chấm (.)'), ('comma', 'Dấu phẩy (,)'), ('semicolon', 'Chấm phẩy (;)'), ('colon', 'Hai chấm (:)'), ('question', 'Dấu hỏi (?)'), ('exclamation', 'Dấu cảm thán (!)'), ('newline', 'Xuống dòng')]:
            widget = QDoubleSpinBox()
            widget.setRange(0, 5)
            widget.setSingleStep(0.1)
            widget.setValue(self.pauses.get(name, 0))
            widget.setSuffix(' giây')
            fields[name] = widget
            layout.addRow(label, widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText('Lưu')
        buttons.button(QDialogButtonBox.Cancel).setText('Hủy')
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec():
            self.pauses = {'enabled': enabled.isChecked(), **{k: v.value() for k, v in fields.items()}}
            self.schedule_save()

    def options(self):
        return {
            'speed': self.speed.value(),
            'pitch': self.pitch.value(),
            'volume': self.volume.value(),
            'num_steps': int(self.steps.currentText()),
            'guidance_scale': self.guidance.value(),
            'temperature': self.temperature.value(),
            'postprocess': self.postprocess.isChecked(),
            'device': self.device.currentData(),
            'output_format': self.format.currentData(),
            'watermark_enabled': self.watermark.isChecked(),
            'watermark_text': self.watermark_text.text().strip(),
            'watermark_interval': self.interval.value() * 60
        }

    def generate(self):
        if self.worker and self.worker.isRunning():
            return
        turns = []
        text = self.text.toPlainText()
        if self.mode.currentIndex() == 1:
            self.identify_dialogue()
            text = self.dialogue_text.toPlainText()
            turns = self.dialogue_script.turns
            if not turns:
                QMessageBox.information(self, 'Chưa có hội thoại', 'Hãy nhập toàn bộ bài nghe, gồm hướng dẫn và lời thoại.')
                return
            missing = [role_name(role) for role in self.dialogue_script.roles
                       if not self.role_voices.get(role) or not Path(self.role_voices[role]).is_file()]
            if missing:
                QMessageBox.information(self, 'Chọn giọng cho từng vai', 'Hãy chọn giọng cho: ' + ', '.join(missing))
                return
        elif not text.strip():
            self.text.setFocus()
            QMessageBox.information(self, 'Chưa có nội dung', 'Hãy gõ hoặc mở tệp văn bản muốn đọc nhé.')
            return

        if not turns and not self.voice.currentData():
            QMessageBox.information(self, 'Chưa chọn giọng', 'Hãy chọn một giọng đọc trước khi tạo.')
            return

        if not self.output_dir.text().strip():
            self.choose_output()
            if not self.output_dir.text().strip():
                return

        if self.watermark.isChecked() and not self.watermark_text.text().strip():
            QMessageBox.information(self, 'Lời nhận diện', 'Hãy nhập lời nhận diện hoặc bỏ chọn tính năng này.')
            return

        self.player.stop()
        self.save_session()
        self.log.clear()

        job = Job(
            text=text, output_dir=self.output_dir.text().strip(),
            voice_path=self.role_voices.get(NARRATOR, self.voice.currentData() or '') if turns else self.voice.currentData(),
            options=self.options(), srt=self.srt.isChecked(),
            dictionary=list(self.dictionary), pauses=dict(self.pauses),
            turns=list(turns), role_voices=dict(self.role_voices), turn_gap=self.turn_gap.value()
        )
        self.worker = GenerationWorker(job)
        self.worker.message.connect(self.on_message)
        self.worker.progress.connect(lambda current, total: (self.progress.setRange(0, total), self.progress.setValue(current)))
        self.worker.output.connect(self.on_output)
        self.worker.completed.connect(self.on_completed)
        self.worker.finished.connect(self.worker_finished)

        self.input_area.setEnabled(False)
        self.create.setEnabled(False)
        self.stop.setEnabled(True)
        self.progress.setRange(0, 0)
        self.set_status('Đang chuẩn bị giọng đọc… Xin vui lòng đợi một chút', running=True)
        self.worker.start()

    def on_message(self, msg):
        self.log.appendPlainText(msg)
        if 'Chunk ' in msg:
            self.set_status('Đang chuyển văn bản thành giọng đọc… (Bạn có thể bấm Dừng lại nếu muốn)', running=True)
        elif 'Đang đọc' in msg or 'Đang ghép' in msg:
            self.set_status(msg, running=True)
        elif 'tải model' in msg.lower():
            self.set_status('Đang tải mô hình trí tuệ nhân tạo, lần đầu có thể mất một lát…', running=True)

    def on_output(self, path):
        self.outputs.append(path)
        self.result_list.addItem(Path(path).name, path)
        self.result_list.setCurrentIndex(self.result_list.count() - 1)
        self.play_result.setEnabled(True)

    def on_completed(self, ok, msg):
        self.log.appendPlainText(msg)
        if ok:
            self.set_status(msg, error=False)
        else:
            self.set_status(msg, error=True)
            if not self.worker.cancel.is_set():
                QMessageBox.warning(self, 'Chưa tạo được âm thanh', msg + '\n\nChi tiết kỹ thuật đã được lưu trong config/last_error.log.')

    def worker_finished(self):
        self.input_area.setEnabled(True)
        self.create.setEnabled(True)
        self.stop.setEnabled(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(1 if self.worker.result and self.worker.result[0] else 0)
        self.worker.deleteLater()
        self.worker = None
        if self._close_after_stop:
            self.close()

    def stop_generation(self):
        if self.worker:
            self.worker.stop()
            self.stop.setEnabled(False)
            self.set_status('Đang dừng sau đoạn đang đọc dở… Xin chờ một chút.', running=True)

    def schedule_save(self, *args):
        if not self._restoring:
            self.save_timer.start(700)

    def save_session(self):
        data = {
            'schema': 2,
            'text': self.text.toPlainText(),
            'dialogue_text': self.dialogue_text.toPlainText(),
            'role_voices': self.role_voices,
            'turn_gap': self.turn_gap.value(),
            'output': self.output_dir.text(),
            'mode': self.mode.currentIndex(),
            'voice': self.voice.currentData(),
            'language': self.language.currentText(),
            'gender': self.gender.currentText(),
            'options': self.options(),
            'srt': self.srt.isChecked(),
            'dictionary': self.dictionary,
            'pauses': self.pauses,
            'is_dark_theme': self.is_dark_theme
        }
        path = STATE_ROOT / 'config' / 'session.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            os.replace(temporary, path)
        except OSError as exc:
            self.set_status('Không lưu được phiên làm việc: ' + str(exc), error=True)

    def restore_session(self):
        try:
            data = json.loads((STATE_ROOT / 'config' / 'session.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return
        self.text.setPlainText(data.get('text', ''))
        self.output_dir.setText(data.get('output', str(DEFAULT_OUTPUT)))
        self.saved_voice = data.get('voice')
        self.language.setCurrentText(data.get('language', 'Tiếng Việt'))
        self.gender.setCurrentText(data.get('gender', 'Tất cả'))
        self.is_dark_theme = data.get('is_dark_theme', True)
        self.role_voices = data.get('role_voices', {})
        self.dialogue_text.setPlainText(data.get('dialogue_text', ''))
        self.turn_gap.setValue(data.get('turn_gap', 0.4))
        self.mode.setCurrentIndex(data.get('mode', 0) if data.get('schema') == 2 else 0)
        self.identify_dialogue()
        options = data.get('options', {})
        for key, widget in [('speed', self.speed), ('pitch', self.pitch), ('volume', self.volume), ('guidance_scale', self.guidance), ('temperature', self.temperature)]:
            if key in options:
                widget.setValue(options[key])
        self.steps.setCurrentText(str(options.get('num_steps', 32)))
        for key, widget in [('device', self.device), ('output_format', self.format)]:
            index = widget.findData(options.get(key))
            if index >= 0:
                widget.setCurrentIndex(index)
        self.postprocess.setChecked(options.get('postprocess', True))
        self.watermark.setChecked(options.get('watermark_enabled', False))
        self.watermark_text.setText(options.get('watermark_text', ''))
        self.interval.setValue(options.get('watermark_interval', 600) // 60)
        self.srt.setChecked(data.get('srt', True))
        self.dictionary = data.get('dictionary', [])
        self.pauses = data.get('pauses', {'enabled': False})

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            if QMessageBox.question(self, 'Đang tạo giọng đọc', 'Dừng xử lý và đóng ứng dụng khi đoạn đang đọc kết thúc?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self._close_after_stop = True
                self.stop_generation()
            event.ignore()
            return
        if self.scan.isRunning():
            event.ignore()
            QTimer.singleShot(500, self.close)
            return
        self.player.stop()
        self.save_session()
        event.accept()
