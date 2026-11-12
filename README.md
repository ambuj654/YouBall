# YouBall
Tracks players and their transfer status to be updated about football general knowledge and live scores of game and predictions
### CURRENTLY IN PROGRESS AS OF 12-11-26 ONLY SHOWS LIVE SCORES
### COMING UP WITH BETTER GUI AND A WEBPAGE ###

Running the YouBall app
1. Install Tkinter

Python’s GUI library is a separate package on Arch:

bash
sudo pacman -S tk
2. Go to the project folder
bash
cd ~/path/to/live_scores

Replace the path with wherever you saved the files. Run ls and check that you see app.py.

3. Create a virtual environment and install requirements
bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

You’ll see (venv) at the start of your terminal prompt when it’s active.

4. Start the app
bash
python app.py

A window titled “Live Football Scores” should open, with tabs for the Premier League, La Liga and Bundesliga.

Next time

You only need two commands, since the setup is already done:

bash
cd ~/path/to/live_scores
source venv/bin/activate
python app.py

To quit, close the window or press Ctrl+C in the terminal. To leave the virtual environment, type deactivate.
