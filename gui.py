from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPixmap, QPainterPath, QPen

class ClaudeOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.state = "IDLE" # IDLE, LISTENING, PROCESSING, SUCCESS
        
        # Animation parameters
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16) # ~60 FPS
        
        self.pulse_phase = 0.0 # For breathing
        self.ripple_phase = 0.0 # For waves
        self.morph_factor = 0.0 # To deform the logo (if needed)

    def initUI(self):
        self.setObjectName("claude-overlay")
        self.setWindowTitle("Claude Overlay")
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        # Force absolute transparency of the window background
        self.setStyleSheet("background: transparent;")
        
        # Variables for window movement
        self.oldPos = self.pos()


        
        # Minimum size for the logo
        # No more fixed minimum size that blocks, we let the content decide
        # self.setMinimumSize(600, 350) 
        
        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # We keep margin for the logo at the top (increased to avoid clipping)
        layout.setContentsMargins(20, 220, 20, 50)
        # This constraint allows the window to grow and shrink according to the content
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        self.setLayout(layout)

        # Text Label
        self.status_label = QLabel("Claude")
        font = QFont("Segoe UI", 18) # Back to an elegant size
        font.setBold(True)
        self.status_label.setFont(font)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 240);
                background-color: rgba(20, 20, 20, 200);
                padding: 15px 30px;
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumWidth(1000) # Much wider to avoid the "column" effect
        self.status_label.setMinimumWidth(400)
        
        # Policy so that the label expands properly
        from PyQt6.QtWidgets import QSizePolicy
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.status_label.setGraphicsEffect(shadow)
        
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        self.center_on_screen()
        self.hide()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        # INITIAL positioning at CENTER
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def update_layout_and_center(self):
        self.status_label.adjustSize()
        self.adjustSize() # The window adapts to the content
        self.center_on_screen() # Re-center since the size has changed

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2
        center_y = 160 # Logo lowered to not clip the animation
        
        # 1. RIPPLE Animation (Waves)
        if self.state == "LISTENING":
            for i in range(3):
                phase_offset = i * 20
                r = 60 + (self.ripple_phase + phase_offset) % 80
                alpha = 100 * (1 - (r - 60) / 80)
                if alpha < 0: alpha = 0
                
                color = QColor(217, 119, 87, int(alpha))
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(center_x - r), int(center_y - r), int(r*2), int(r*2))

        # 2. Draw the Logo "PNG Image"
        import math
        breath = math.sin(self.pulse_phase) * 0.05 + 1.0
        base_size = 100 # Base logo size
        size = base_size * breath
        
        painter.translate(center_x, center_y)
        
        # Load the image
        import os
        logo_path = os.path.abspath("logo.png")
        pixmap = QPixmap(logo_path)
        
        if not pixmap.isNull():
            # Resize the image to match the desired size (with breathing effect)
            scaled_pixmap = pixmap.scaled(
                int(size), int(size),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Draw the image centered at (0,0) since we already translated
            painter.drawPixmap(int(-size/2), int(-size/2), scaled_pixmap)
        else:
            print(f"ERROR: Cannot load image from {logo_path}")
            # Fallback if the image is not found (Old drawing)
            claude_color = QColor(217, 119, 87)
            if self.state == "PROCESSING":
                 claude_color = QColor(255, 150, 120)
            
            painter.setBrush(QBrush(claude_color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            path = QPainterPath()
            R = size * 0.8
            r = size * 0.4 * 0.8
            path.moveTo(0, -R)
            path.quadTo(r/2, -r/2, R, 0)
            path.quadTo(r/2, r/2, 0, R)
            path.quadTo(-r/2, r/2, -R, 0)
            path.quadTo(-r/2, -r/2, 0, -R)
            painter.drawPath(path)

    def animate(self):
        self.pulse_phase += 0.1
        self.ripple_phase += 1.5
        self.update()

    def show_listening(self):
        # If we just displayed a response (SUCCESS), we KEEP the text so the user can read it
        # We only change the state to restart the animation (Ripples)
        if self.state != "SUCCESS":
            self.status_label.setText("Listening...")
            
        self.state = "LISTENING"
        self.show()
        self.status_label.show()
        self.update_layout_and_center()

    def show_processing(self, text):
        self.state = "PROCESSING"
        self.show()
        self.status_label.setText(text)
        self.status_label.show()
        self.update_layout_and_center()
        
    def show_success(self, message):
        self.state = "SUCCESS"
        self.status_label.setText(message)
        self.status_label.show()
        self.update_layout_and_center()
        # We no longer hide automatically here, because the worker manages the loop
        # QTimer.singleShot(3000, self.hide_overlay) 

    def handle_error(self, message):
        if message == "STOP_OVERLAY":
            self.hide_overlay()
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.show()
            self.update_layout_and_center()
            QTimer.singleShot(3000, self.hide_overlay)

    def hide_overlay(self):
        self.hide()
        self.state = "IDLE"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setDesktopFileName("claude-overlay")
    app.setQuitOnLastWindowClosed(False)
    overlay = ClaudeOverlay()
    overlay.show_listening()
    sys.exit(app.exec())
