#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Installation de Claude Overlay ===${NC}"

# 1. Vérification des dépendances système
echo -e "\n${BLUE}[1/5] Vérification des dépendances système...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Erreur: $1 n'est pas installé.${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 détecté${NC}"
        return 0
    fi
}

# Liste des paquets requis (adapté pour Debian/Ubuntu/Arch)
# On vérifie juste les commandes critiques
check_command python3 || exit 1
check_command ffmpeg || echo -e "${RED}Attention: ffmpeg manquant. Requis pour Whisper.${NC}"
check_command claude || echo -e "${RED}Attention: CLI 'claude' manquant. Requis pour l'IA.${NC}"

# 2. Création de l'environnement virtuel
echo -e "\n${BLUE}[2/5] Configuration de l'environnement Python...${NC}"
if [ ! -d "venv" ]; then
    echo "Création du venv..."
    python3 -m venv venv
else
    echo "venv existe déjà."
fi

# Activation du venv
source venv/bin/activate

# 3. Installation des dépendances Python
echo -e "\n${BLUE}[3/5] Installation des librairies Python...${NC}"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}Erreur: requirements.txt introuvable!${NC}"
    exit 1
fi

# 4. Téléchargement du modèle Vosk (si absent)
echo -e "\n${BLUE}[4/5] Vérification du modèle vocal (Vosk)...${NC}"
MODEL_DIR="models"
MODEL_NAME="fr"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"

if [ ! -d "$MODEL_PATH" ]; then
    echo "Le modèle 'fr' est manquant."
    mkdir -p "$MODEL_DIR"
    
    # URL du modèle français léger (vosk-model-small-fr-0.22)
    # On peut changer pour un plus gros si besoin
    VOSK_URL="https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
    ZIP_FILE="model.zip"
    
    echo "Téléchargement de $VOSK_URL ..."
    wget $VOSK_URL -O $ZIP_FILE
    
    echo "Extraction..."
    unzip -q $ZIP_FILE
    mv vosk-model-small-fr-0.22 "$MODEL_PATH"
    rm $ZIP_FILE
    
    echo -e "${GREEN}Modèle installé dans $MODEL_PATH${NC}"
else
    echo -e "${GREEN}✓ Modèle Vosk présent${NC}"
fi

# 5. Fin
echo -e "\n${BLUE}[5/5] Installation terminée !${NC}"
echo -e "Pour lancer l'assistant :"
echo -e "  ${GREEN}source venv/bin/activate${NC}"
echo -e "  ${GREEN}python main.py${NC}"
echo -e "\nNote: Assurez-vous d'avoir configuré votre clé API Claude via 'claude login' si ce n'est pas déjà fait."

# Rendre le script exécutable lui-même (au cas où)
chmod +x "$0"
