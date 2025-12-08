# Claude Overlay

Assistant vocal pour Linux intégrant Claude AI.
Interface minimaliste, reconnaissance vocale hybride (Vosk + Whisper) et contrôle système.

![Claude Overlay](claude_logo.png)

## Fonctionnalités

*   **Interface Overlay** : Fenêtre transparente et non intrusive (PyQt6).
*   **Wake Word Local** : Détection hors-ligne du mot-clé "Claude" (Vosk).
*   **Transcription** : Utilisation de Whisper pour une compréhension précise.
*   **Intelligence** : Connecté à l'API Claude pour les réponses et commandes complexes.
*   **Contrôle** : Lancement d'applications et navigation web.

## Installation

Prérequis : Linux, Python 3.10+, `ffmpeg`, `portaudio`, `claude` CLI.

1.  **Cloner le projet**
    ```bash
    git clone https://github.com/votre-user/claude-overlay.git
    cd claude-overlay
    ```

2.  **Installer**
    Le script `install.sh` configure l'environnement virtuel et télécharge les modèles nécessaires.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

3.  **Connexion Claude**
    ```bash
    claude login
    ```

## Utilisation

Lancer l'assistant :
```bash
source venv/bin/activate
python main.py
```

*   **Activer** : Dites "Claude".
*   **Commander** : Posez votre question ou donnez un ordre.
*   **Terminer** : Dites "Fin Claude" ou "Envoyer".
*   **Annuler** : Dites "Merci" ou "Stop".

## Configuration

*   **Hyprland** : Règles de fenêtre incluses dans `main.py`.
*   **Modèles** :
    *   Vosk (Wake word) : `models/fr`
    *   Whisper (Transcription) : Configurable dans `worker.py`.
