#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up TTB Label App development environment...${NC}\n"

# Check if tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo -e "${RED}Tesseract OCR is not installed.${NC}"
    
    # Check the operating system
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing Tesseract OCR for Linux..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}Homebrew is required for macOS installation. Please install it first.${NC}"
            exit 1
        fi
        echo "Installing Tesseract OCR for macOS..."
        brew install tesseract
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo -e "${RED}For Windows, please install Tesseract OCR manually:${NC}"
        echo "1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki"
        echo "2. Run the installer"
        echo "3. Add the Tesseract installation directory to your PATH"
        exit 1
    else
        echo -e "${RED}Unsupported operating system${NC}"
        exit 1
    fi
fi

# Verify tesseract installation
if command -v tesseract &> /dev/null; then
    echo -e "${GREEN}✓ Tesseract OCR is installed${NC}"
    echo "Tesseract version: $(tesseract --version | head -n 1)"
else
    echo -e "${RED}Failed to install Tesseract OCR${NC}"
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Python dependencies for backend
echo -e "\n${YELLOW}Installing backend dependencies...${NC}"
cd backend
uv sync

# Install Python dependencies for test-data
echo -e "\n${YELLOW}Installing test-data dependencies...${NC}"
cd ../test-data
uv sync
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
uv run playwright install chromium
uv run playwright install-deps

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
cd ../frontend
npm install

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "You can now use: ${YELLOW}just setup${NC} to run this again"
echo -e "Or use ${YELLOW}just generate-test-data${NC} to create test data"
echo -e "Use ${YELLOW}just test-api-local <image-path>${NC} to test local API"
echo -e "Use ${YELLOW}just lint${NC} and ${YELLOW}just format${NC} for code quality"