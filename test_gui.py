import sys
print("Start of test")
try:
    from PyQt6.QtWidgets import QApplication, QLabel
    print("Import OK")
    app = QApplication(sys.argv)
    print("App created")
    label = QLabel("Test")
    label.show()
    print("Label displayed")
    # Exit immediately to avoid blocking
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
