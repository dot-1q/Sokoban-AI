# Sokoban
Sokoban clone for AI teaching

![Demo](https://github.com/dgomes/iia-ia-sokoban/raw/master/data/sokoban_screenshot.png)

## How to install

Make sure you are running Python 3.5 or higher

1. Create a virtual environment (venv)
```bash
python3 -m venv venv
```

2. Activate the virtual environment (you need to repeat this step, and this step only, every time you start a new terminal/session):
```bash
source venv/bin/activate
```

3. Install the game requirements:
```bash
pip install -r requirements.txt
```

## How to play

### AI Solver

Simply run: 
```bash
chmod +x start.sh
./start.sh
```
Currently goes to level 135

### Important Files
student.py - Responsible for the sending the solution keys to the local server and calling the solving algorithm

solve.py - Where the solution is created. It has all the functions necessary to create the set of keeper movements.


## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- Ubuntu 20.04 LTS

# Credits

[Diogo Gomes](https://github.com/dgomes) for the [game engine](https://github.com/dgomes/iia-ia-sokoban)

[Kenney](https://www.kenney.nl/assets/sokoban) for the sprites


