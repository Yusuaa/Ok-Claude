import sys
print("Début du test")
try:
    from PyQt6.QtWidgets import QApplication, QLabel
    print("Import OK")
    app = QApplication(sys.argv)
    print("App créée")
    label = QLabel("Test")
    label.show()
    print("Label affiché")
    # On quitte tout de suite pour ne pas bloquer
    sys.exit(0)
except Exception as e:
    print(f"Erreur: {e}")
