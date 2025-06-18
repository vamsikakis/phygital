#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Gopalan Atlantis Facility Manager Setup ===${NC}"

# Check if .env file exists in backend, if not create it from example
if [ ! -f ./backend/.env ]; then
  echo -e "${YELLOW}Creating backend .env file from example...${NC}"
  cp ./backend/.env.example ./backend/.env
  echo -e "${GREEN}Created .env file in backend directory.${NC}"
  echo -e "${YELLOW}Important: Please edit ./backend/.env file to add your OpenAI API key!${NC}"
fi

# Setup virtual environment and install Python dependencies
echo -e "${BLUE}Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd frontend
npm install

# Start both servers
echo -e "${GREEN}Starting servers...${NC}"
echo -e "${YELLOW}Backend will run on http://localhost:5000${NC}"
echo -e "${YELLOW}Frontend will run on http://localhost:5173${NC}"

# Use terminal tabs or tmux to run both servers
if command -v tmux &> /dev/null; then
  echo "Using tmux to run servers..."
  tmux new-session -d -s facility-manager "cd $(pwd)/.. && source venv/bin/activate && cd backend && python app.py"
  tmux split-window -h -t facility-manager "cd $(pwd) && npm run dev"
  tmux -2 attach-session -d -t facility-manager
else
  # Fall back to running one after another
  echo -e "${YELLOW}tmux not found. Please open a new terminal to run the frontend server.${NC}"
  echo -e "Run these commands in a new terminal:"
  echo -e "${GREEN}cd $(pwd) && npm run dev${NC}"
  
  # Start the backend server in the current terminal
  cd ../backend
  python app.py
fi
