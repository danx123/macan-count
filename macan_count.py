# -*- coding: utf-8 -*-

"""
Macan Count - Kalkulator Estetik & Modern
Dibuat dengan Python dan PyQt6
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QIcon, QFont, QMouseEvent, QColor, QPalette
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

# --- Data SVG untuk Ikon di Title Bar (Embedded) ---
# Ini membuat aplikasi tidak butuh file eksternal
SVG_CLOSE = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="6" x2="6" y2="18"></line>
  <line x1="6" y1="6" x2="18" y2="18"></line>
</svg>
"""

SVG_MINIMIZE = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="5" y1="12" x2="19" y2="12"></line>
</svg>
"""

SVG_MAXIMIZE = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
</svg>
"""

SVG_RESTORE = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="8" y="8" width="13" height="13" rx="2" ry="2"></rect>
  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
</svg>
"""

class SvgIcon(QIcon):
    """Kelas helper untuk membuat QIcon dari data string SVG."""
    def __init__(self, svg_data):
        super().__init__()
        renderer = QSvgRenderer(svg_data.encode('utf-8'))
        # Ukuran default ikon
        pixmap = self.render_pixmap(renderer, 64)
        self.addPixmap(pixmap)

    def render_pixmap(self, renderer, size):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

# Untuk PyQt6, kita harus membuat QIcon dari QPixmap yang dirender
# Jadi, kita buat fungsi helper
def create_svg_icon(svg_data):
    renderer = QSvgRenderer(svg_data.encode('utf-8'))
    pixmap = QPixmap(256, 256) # Render di resolusi tinggi
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class MacanCountCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Konfigurasi Window Utama ---
        self.setWindowTitle("Macan Count")
        self.setWindowIcon(QIcon("icon.png")) # Ganti dengan path ikon jika ada
        self.setMinimumSize(360, 540)

        # Membuat window frameless (tanpa title bar bawaan)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Variabel untuk fungsionalitas drag window
        self._drag_pos = QPoint()

        # --- Inisialisasi Variabel Kalkulator ---
        self.current_input = "0"
        self.first_operand = None
        self.operator = None
        self.new_input_started = True

        # --- Inisialisasi UI ---
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Widget utama sebagai dasar container
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)

        # Layout vertikal utama
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Custom Title Bar ---
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(10, 0, 5, 0)

        app_icon_label = QLabel("🐯")
        app_icon_label.setFont(QFont("Arial", 14))
        title_label = QLabel("Macan Count")
        title_label.setObjectName("TitleLabel")

        # Tombol-tombol di title bar
        self.btn_minimize = QPushButton(create_svg_icon(SVG_MINIMIZE), "")
        self.btn_maximize = QPushButton(create_svg_icon(SVG_MAXIMIZE), "")
        self.btn_close = QPushButton(create_svg_icon(SVG_CLOSE), "")
        
        for btn in [self.btn_minimize, self.btn_maximize, self.btn_close]:
            btn.setObjectName("TitleBarButton")
            btn.setFixedSize(30, 30)
            btn.setIconSize(QSize(16, 16))

        title_bar_layout.addWidget(app_icon_label)
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.btn_minimize)
        title_bar_layout.addWidget(self.btn_maximize)
        title_bar_layout.addWidget(self.btn_close)

        # Koneksi sinyal tombol title bar
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close)

        # --- Display (Layar Kalkulator) ---
        self.display = QLineEdit(self.current_input)
        self.display.setObjectName("Display")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(80)

        # --- Grid Tombol Kalkulator ---
        button_grid = QGridLayout()
        button_grid.setSpacing(5)
        button_grid.setContentsMargins(10, 10, 10, 10)

        # Definisi layout dan teks tombol
        buttons = {
            (0, 0): 'C', (0, 1): '±', (0, 2): '%', (0, 3): '÷',
            (1, 0): '7', (1, 1): '8', (1, 2): '9', (1, 3): '×',
            (2, 0): '4', (2, 1): '5', (2, 2): '6', (2, 3): '-',
            (3, 0): '1', (3, 1): '2', (3, 2): '3', (3, 3): '+',
            (4, 0): '0', (4, 2): '.', (4, 3): '=',
        }

        for pos, text in buttons.items():
            button = QPushButton(text)
            button.clicked.connect(self.on_button_clicked)
            button.setSizePolicy(
                button.sizePolicy().horizontalPolicy(),
                button.sizePolicy().verticalPolicy()
            )
            
            # Memberi nama objek untuk styling QSS
            if text in "÷×-+=":
                button.setObjectName("OperatorButton")
            elif text in "C±%":
                button.setObjectName("FunctionButton")
            
            if text == '0':
                button_grid.addWidget(button, pos[0], pos[1], 1, 2) # Tombol 0 span 2 kolom
            elif text == '=':
                 button.setObjectName("EqualsButton")
                 button_grid.addWidget(button, pos[0], pos[1])
            else:
                button_grid.addWidget(button, pos[0], pos[1])

        # Menambahkan semua widget ke layout utama
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.display)
        self.main_layout.addLayout(button_grid)

    def apply_styles(self):
        """Menerapkan QSS untuk seluruh aplikasi."""
        qss = """
            #CentralWidget {
                background-color: #1e1e1e; /* Dark Grey */
                border-radius: 15px;
            }
            #TitleBar {
                background-color: #2a2a2a; /* Slightly Lighter Grey */
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
            #TitleLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
            }
            #TitleBarButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
            }
            #TitleBarButton:hover {
                background-color: #4a4a4a;
            }
            #TitleBarButton:pressed {
                background-color: #5a5a5a;
            }
            #Display {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                font-size: 48px;
                font-weight: 300;
                padding: 0 15px;
            }
            QPushButton {
                background-color: #2c2c2c;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
            QPushButton:pressed {
                background-color: #4c4c4c;
            }
            #FunctionButton {
                background-color: #3e3e3e;
                color: #e0e0e0;
            }
            #FunctionButton:hover {
                background-color: #4e4e4e;
            }
            #OperatorButton {
                background-color: #ff9500; /* Orange Accent */
                color: #ffffff;
            }
            #OperatorButton:hover {
                background-color: #ffaa33;
            }
            #EqualsButton {
                background-color: #ff9500; /* Orange Accent */
                color: #ffffff;
            }
            #EqualsButton:hover {
                background-color: #ffaa33;
            }
        """
        self.setStyleSheet(qss)

    # --- Logika Kalkulator ---

    def on_button_clicked(self):
        """Handler utama saat tombol ditekan."""
        button = self.sender()
        text = button.text()

        if text.isdigit() or text == '.':
            self.handle_number(text)
        elif text in "÷×-+":
            self.handle_operator(text)
        elif text == '=':
            self.handle_equals()
        elif text == 'C':
            self.handle_clear()
        elif text == '%':
            self.handle_percentage()
        elif text == '±':
            self.handle_plus_minus()
        
        self.display.setText(self.format_number(self.current_input))

    def handle_number(self, num_text):
        if self.new_input_started:
            self.current_input = "0"
            self.new_input_started = False
            
        if num_text == '.' and '.' in self.current_input:
            return
        
        if self.current_input == "0" and num_text != '.':
            self.current_input = num_text
        else:
            self.current_input += num_text

    def handle_operator(self, op_text):
        if not self.new_input_started:
            if self.first_operand is not None:
                self.handle_equals()
            
            self.first_operand = float(self.current_input.replace(',', ''))
        
        self.operator = op_text
        self.new_input_started = True

    def handle_equals(self):
        if self.first_operand is None or self.operator is None:
            return
            
        second_operand = float(self.current_input.replace(',', ''))
        result = 0

        try:
            if self.operator == '+':
                result = self.first_operand + second_operand
            elif self.operator == '-':
                result = self.first_operand - second_operand
            elif self.operator == '×':
                result = self.first_operand * second_operand
            elif self.operator == '÷':
                if second_operand == 0:
                    self.current_input = "Error"
                    self.reset_state()
                    return
                result = self.first_operand / second_operand
        except Exception:
            self.current_input = "Error"
            self.reset_state()
            return

        self.current_input = str(result)
        self.reset_state()
        self.new_input_started = True # Agar bisa langsung mulai op baru

    def handle_clear(self):
        self.current_input = "0"
        self.reset_state()
        self.new_input_started = True

    def handle_percentage(self):
        value = float(self.current_input.replace(',', ''))
        self.current_input = str(value / 100)
    
    def handle_plus_minus(self):
        if self.current_input != "0":
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input

    def reset_state(self):
        self.first_operand = None
        self.operator = None
    
    def format_number(self, num_str):
        """Format angka agar mudah dibaca."""
        if num_str == "Error":
            return "Error"
        try:
            num = float(num_str)
            # Tampilkan sebagai integer jika tidak ada koma
            if num == int(num):
                return f"{int(num):,}"
            else:
                # Batasi jumlah angka di belakang koma untuk kerapian
                return f"{num:,.10f}".rstrip('0').rstrip('.')
        except (ValueError, TypeError):
            return num_str


    # --- Event Handler untuk Window ---

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setIcon(create_svg_icon(SVG_MAXIMIZE))
        else:
            self.showMaximized()
            self.btn_maximize.setIcon(create_svg_icon(SVG_RESTORE))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < self.title_bar.height():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = QPoint()
        event.accept()

    def keyPressEvent(self, event):
        """Menangani input dari keyboard/numpad."""
        key = event.key()
        text = event.text()

        key_map = {
            Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2',
            Qt.Key.Key_3: '3', Qt.Key.Key_4: '4', Qt.Key.Key_5: '5',
            Qt.Key.Key_6: '6', Qt.Key.Key_7: '7', Qt.Key.Key_8: '8',
            Qt.Key.Key_9: '9', Qt.Key.Key_Period: '.',
            Qt.Key.Key_Plus: '+', Qt.Key.Key_Minus: '-',
            Qt.Key.Key_Asterisk: '×', Qt.Key.Key_Slash: '÷',
            Qt.Key.Key_Enter: '=', Qt.Key.Key_Return: '=',
            Qt.Key.Key_Backspace: 'C', # Atau bisa dibuat fungsi backspace
            Qt.Key.Key_Escape: 'C',
        }

        if key in key_map:
            # Cari tombol yang sesuai dan simulasikan klik
            btn_text = key_map[key]
            for button in self.findChildren(QPushButton):
                if button.text() == btn_text:
                    button.click()
                    return
        
        # Penanganan khusus untuk koma keyboard
        if text == ',':
            for button in self.findChildren(QPushButton):
                if button.text() == '.':
                    button.click()
                    return


if __name__ == '__main__':
    # Fix untuk beberapa masalah rendering di PyQt6
    from PyQt6.QtGui import QPixmap
    
    app = QApplication(sys.argv)
    
    # Atur palet global untuk mendukung dark theme dengan lebih baik
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    # ... atur warna lain jika perlu
    app.setPalette(dark_palette)
    
    calculator = MacanCountCalculator()
    calculator.show()
    sys.exit(app.exec())