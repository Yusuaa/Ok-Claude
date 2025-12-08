import sys
import subprocess
import shutil
from PyQt6.QtWidgets import QApplication
from gui import ClaudeOverlay
from worker import AudioWorker

def configure_hyprland():
    """Injecte dynamiquement les règles pour faire flotter la fenêtre sous Hyprland."""
    if shutil.which("hyprctl"):
        print("Hyprland détecté : Injection des règles de fenêtre...")
        rules = [
            "float,class:^(claude-overlay)$",
            "pin,class:^(claude-overlay)$",
            "noborder,class:^(claude-overlay)$",
            "noshadow,class:^(claude-overlay)$", # Pas d'ombre
            "noblur,class:^(claude-overlay)$",   # Pas de flou d'arrière-plan
            "center,class:^(claude-overlay)$", # RETOUR AU CENTRE
            # "move 100%-w-50 50%-h,class:^(claude-overlay)$", # Droite + Centré Verticalement (Désactivé)
            "size 400 200,class:^(claude-overlay)$"
        ]
        for rule in rules:
            try:
                subprocess.run(["hyprctl", "keyword", "windowrulev2", rule], check=False)
            except Exception as e:
                print(f"Erreur Hyprland: {e}")

def main():
    # Configuration du format de surface pour la transparence
    from PyQt6.QtGui import QSurfaceFormat
    format = QSurfaceFormat()
    format.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(format)

    # Configuration Hyprland AVANT de créer l'app
    configure_hyprland()
    
    app = QApplication(sys.argv)
    app.setApplicationName("claude-overlay") # Pour que la règle Hyprland 'class' fonctionne
    app.setApplicationDisplayName("Claude Overlay")
    app.setDesktopFileName("claude-overlay") # Pour Wayland
    app.setQuitOnLastWindowClosed(False) # Empêche l'app de quitter quand la fenêtre est cachée
    
    # Création de l'interface
    overlay = ClaudeOverlay()
    
    # Création du worker audio (thread séparé)
    worker = AudioWorker()
    
    # Connexion des signaux Worker -> GUI
    worker.signal_listening.connect(overlay.show_listening)
    worker.signal_recognized.connect(lambda text: overlay.show_processing(f"Entendu : {text}"))
    worker.signal_processing.connect(lambda text: overlay.show_processing(f"Traitement : {text}"))
    worker.signal_finished.connect(overlay.show_success)
    worker.signal_error.connect(overlay.handle_error)
    
    # Feedback de démarrage : On affiche l'interface 3 secondes pour dire qu'on est prêt
    overlay.show_processing("Démarrage...")
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(3000, overlay.hide_overlay)
    
    # Démarrage du worker
    worker.start()
    
    # Lancement de la boucle d'événements
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
