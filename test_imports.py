import sys
print("Testing imports...")
try:
    print("Import PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("Import gui...")
    import gui
    print("Import speech_recognition...")
    import speech_recognition as sr
    print("Import worker...")
    import worker
    print("Everything is OK")
except Exception as e:
    print(f"Import error: {e}")
