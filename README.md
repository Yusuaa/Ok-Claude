# Claude Overlay - Assistant Vocal Linux

Un assistant vocal élégant et performant pour Linux, conçu pour s'intégrer parfaitement avec les gestionnaires de fenêtres comme Hyprland. Il combine la rapidité de la reconnaissance locale et l'intelligence de Claude AI.

![Claude Overlay](claude_logo.png)

## Fonctionnalités

*   **Interface Moderne** : Une superposition (overlay) transparente, animée et minimaliste qui ne gêne pas votre travail.
*   **Reconnaissance Hybride** :
    *   **Vosk** (Local) : Détection instantanée du mot-clé ("Claude") et gestion des commandes rapides.
    *   **Whisper** (OpenAI) : Transcription haute précision pour les requêtes complexes.
*   **Intelligence Artificielle** : Intégration directe avec la CLI Claude pour répondre à vos questions et exécuter des tâches.
*   **Contrôle du Système** : Capable de lancer des applications, ouvrir des sites web et chercher des fichiers localement.
*   **Mode Dictée** : Dictez vos messages ou commandes avec une grande fiabilité.

## Prérequis

*   **Système** : Linux (Testé sur Arch Linux / Hyprland, mais compatible avec d'autres environnements).
*   **Audio** : Un microphone fonctionnel.
*   **Dépendances Système** :
    *   Python 3.10 ou supérieur
    *   `ffmpeg` (pour le traitement audio)
    *   `portaudio` (pour l'accès micro)
    *   `claude` CLI (installé via `npm install -g @anthropic-ai/claude-code` ou équivalent)

## Installation Rapide

Un script d'installation automatisé est fourni pour configurer l'environnement en quelques secondes.

1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-utilisateur/claude-overlay.git
    cd claude-overlay
    ```

2.  **Lancer l'installation** :
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    Ce script va :
    *   Créer un environnement virtuel Python (`venv`).
    *   Installer toutes les librairies nécessaires.
    *   Télécharger automatiquement le modèle vocal français pour Vosk.

3.  **Configurer Claude** :
    Assurez-vous d'être connecté à votre compte Anthropic :
    ```bash
    claude login
    ```

## Utilisation

1.  **Démarrer l'assistant** :
    ```bash
    source venv/bin/activate
    python main.py
    ```

2.  **Interagir** :
    *   Dites **"Claude"** pour l'activer. L'interface apparaîtra.
    *   Posez votre question ou donnez une commande (ex: "Ouvre Firefox", "Quelle heure est-il ?", "Écris un script Python pour...").
    *   Pour terminer une dictée longue, dites **"Fin Claude"** ou **"Envoyer"**.
    *   Pour annuler, dites **"Merci"** ou **"Stop"**.

## Configuration Avancée

### Hyprland
Le fichier `main.py` contient déjà des règles pour faire flotter la fenêtre intelligemment sous Hyprland. Si vous utilisez un autre WM, vous devrez peut-être ajuster les règles de fenêtre.

### Modèles
*   **Vosk** : Le modèle par défaut est `vosk-model-small-fr-0.22` (léger et rapide). Vous pouvez le remplacer par un modèle plus gros dans le dossier `models/` pour une meilleure précision du mot-clé.
*   **Whisper** : Configuré par défaut sur `base`. Vous pouvez changer cela dans `worker.py` (`whisper.load_model("small")` ou `medium`) si vous avez un GPU puissant.

## Structure du Projet

*   `main.py` : Point d'entrée, gestion de la fenêtre et configuration Hyprland.
*   `gui.py` : Interface utilisateur (PyQt6), animations et rendu visuel.
*   `worker.py` : Cerveau de l'assistant. Gère les threads audio, Vosk, Whisper et les appels à Claude.
*   `install.sh` : Script d'installation.

## Licence

Ce projet est sous licence MIT. Libre à vous de le modifier et de l'améliorer.
