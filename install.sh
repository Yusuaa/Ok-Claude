#!/bin/bash

# Terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0;0m' # No Color

echo -e "${BLUE}=== Claude Overlay Installation ===${NC}"

# 1. Check system dependencies
echo -e "\n${BLUE}[1/5] Checking system dependencies...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed.${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 detected${NC}"
        return 0
    fi
}

# List of required packages (adapted for Debian/Ubuntu/Arch)
# We only check critical commands
check_command python3 || exit 1
check_command ffmpeg || echo -e "${RED}Warning: ffmpeg missing. Required for Whisper.${NC}"
check_command claude || echo -e "${RED}Warning: CLI 'claude' missing. Required for AI.${NC}"

# 2. Create virtual environment
echo -e "\n${BLUE}[2/5] Configuring Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating venv..."
else
    echo "venv already exists."
fi

# Activate venv
source venv/bin/activate

# 3. Install Python dependencies
echo -e "\n${BLUE}[3/5] Installing Python libraries...${NC}"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}Error: requirements.txt not found!${NC}"
    exit 1
fi

# 4. Download Vosk model (if absent)
echo -e "\n${BLUE}[4/5] Checking voice model (Vosk)...${NC}"
MODEL_DIR="models"
MODEL_NAME="fr"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"

if [ ! -d "$MODEL_PATH" ]; then
    echo "The 'fr' model is missing."
    mkdir -p "$MODEL_DIR"
    
    # URL of the lightweight French model (vosk-model-small-fr-0.22)
    # Can change to a larger one if needed
    VOSK_URL="https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
    ZIP_FILE="model.zip"
    
    echo "Downloading from $VOSK_URL ..."
    wget $VOSK_URL -O $ZIP_FILE
    
    echo "Extracting..."
    unzip -q $ZIP_FILE
    mv vosk-model-small-fr-0.22 "$MODEL_PATH"
    rm $ZIP_FILE
    
    echo -e "${GREEN}Model installed in $MODEL_PATH${NC}"
else
    echo -e "${GREEN}✓ Vosk model present${NC}"
fi

# 5. Done
echo -e "\n${BLUE}[5/5] Installation complete!${NC}"
echo -e "To launch the assistant:"
echo -e "  ${GREEN}source venv/bin/activate${NC}"
echo -e "  ${GREEN}python main.py${NC}"
echo -e "\nNote: Make sure you have configured your Claude API key via 'claude login' if not already done."

# Make the script executable itself (just in case)
chmod +x "$0"
