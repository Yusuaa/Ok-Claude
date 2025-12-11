import sys
import subprocess
import shutil
from PyQt6.QtWidgets import QApplication
from gui import ClaudeOverlay
from worker import AudioWorker

def configure_hyprland():
    """Dynamically injects rules to float the window under Hyprland."""
    if shutil.which("hyprctl"):
        print("Hyprland detected: Injecting window rules...")
        rules = [
            "float,class:^(claude-overlay)$",
            "pin,class:^(claude-overlay)$",
            "noborder,class:^(claude-overlay)$",
            "noshadow,class:^(claude-overlay)$", # No shadow
            "noblur,class:^(claude-overlay)$",   # No background blur
            "center,class:^(claude-overlay)$", # RETURN TO CENTER
            # "move 100%-w-50 50%-h,class:^(claude-overlay)$", # Right + Vertically Centered (Disabled)
            "size 400 200,class:^(claude-overlay)$"
        ]
        for rule in rules:
            try:
                subprocess.run(["hyprctl", "keyword", "windowrulev2", rule], check=False)
            except Exception as e:
                print(f"Hyprland error: {e}")

def main():
    # Configure surface format for transparency
    from PyQt6.QtGui import QSurfaceFormat
    format = QSurfaceFormat()
    format.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(format)

    # Hyprland configuration BEFORE creating the app
    configure_hyprland()
    
    app = QApplication(sys.argv)
    app.setApplicationName("claude-overlay") # So that the Hyprland 'class' rule works
    app.setApplicationDisplayName("Claude Overlay")
    app.setDesktopFileName("claude-overlay") # For Wayland
    app.setQuitOnLastWindowClosed(False) # Prevents the app from quitting when the window is hidden
    
    # Create the interface
    overlay = ClaudeOverlay()
    
    # Create the audio worker (separate thread)
    worker = AudioWorker()
    
    # Connect Worker -> GUI signals
    worker.signal_listening.connect(overlay.show_listening)
    worker.signal_recognized.connect(lambda text: overlay.show_processing(f"Heard: {text}"))
    worker.signal_processing.connect(lambda text: overlay.show_processing(f"Processing: {text}"))
    worker.signal_finished.connect(overlay.show_success)
    worker.signal_error.connect(overlay.handle_error)
    
    # Startup feedback: Display the interface for 3 seconds to show we're ready
    overlay.show_processing("Starting...")
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(3000, overlay.hide_overlay)
    
    # Start the worker
    worker.start()
    
    # Launch the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
