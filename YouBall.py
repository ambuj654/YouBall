import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import requests

LEAGUES = {"Premier League": "eng.1", "La Liga": "esp.1", "Bundesliga": "ger.1"}
URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/{}/scoreboard"
REFRESH_SECONDS = 30
ORDER = {"in": 0, "pre": 1, "post": 2}  # live first, then upcoming, then finished


def fetch_league(code):
    """Return a list of matches for one league: (state, when, home, score, away)."""
    r = requests.get(URL.format(code), timeout=10)
    r.raise_for_status()
    matches = []
    for ev in r.json().get("events", []):
        comp = ev["competitions"][0]
        sides = {c["homeAway"]: c for c in comp["competitors"]}
        home, away = sides["home"], sides["away"]
        status = ev["status"]["type"]
        state = status.get("state", "pre")
        kickoff = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")).astimezone()
        if state == "pre":
            when, score = kickoff.strftime("%a %d %b %H:%M"), "vs"
        else:
            when = status.get("shortDetail") or ("FT" if state == "post" else "LIVE")
            score = f"{home.get('score', 0)} - {away.get('score', 0)}"
        matches.append((state, when, home["team"]["displayName"], score,
                        away["team"]["displayName"], kickoff))
    matches.sort(key=lambda m: (ORDER.get(m[0], 3), m[5]))
    return matches


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Live Football Scores")
        self.geometry("760x480")
        ttk.Style(self).theme_use("clam")
        ttk.Style(self).configure("Treeview", rowheight=30, font=("TkDefaultFont", 11))

        self.queue = queue.Queue()
        self.busy = False
        self.error = None
        self.trees = {}

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        self.status = tk.StringVar(value="Loading...")
        ttk.Label(top, textvariable=self.status).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for name in LEAGUES:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=name)
            self.trees[name] = self.make_tree(frame)

        self.refresh()
        self.after(200, self.poll)
        self.after(REFRESH_SECONDS * 1000, self.auto_refresh)

    def make_tree(self, parent):
        cols = ("when", "home", "score", "away")
        tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="none")
        for col, text, width, anchor in [("when", "Status", 130, "w"), ("home", "Home", 230, "e"),
                                         ("score", "Score", 80, "center"), ("away", "Away", 230, "w")]:
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor=anchor)
        tree.tag_configure("in", foreground="#0a7d2c", font=("TkDefaultFont", 11, "bold"))
        tree.tag_configure("pre", foreground="#555555")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def refresh(self):
        if self.busy:
            return
        self.busy, self.error = True, None
        self.status.set("Updating...")
        threading.Thread(target=self.worker, daemon=True).start()

    def auto_refresh(self):
        self.refresh()
        self.after(REFRESH_SECONDS * 1000, self.auto_refresh)

    def worker(self):  # runs in a background thread so the window never freezes
        for name, code in LEAGUES.items():
            try:
                self.queue.put((name, fetch_league(code), None))
            except Exception as e:
                self.queue.put((name, None, e))
        self.queue.put(None)

    def poll(self):  # runs in the GUI thread and applies results from the worker
        try:
            while True:
                item = self.queue.get_nowait()
                if item is None:
                    self.busy = False
                    if self.error:
                        self.status.set(self.error)
                    else:
                        self.status.set(f"Updated {datetime.now():%H:%M:%S}  |  auto-refresh every {REFRESH_SECONDS}s")
                else:
                    self.show(*item)
        except queue.Empty:
            pass
        self.after(200, self.poll)

    def show(self, name, matches, error):
        if error:
            self.error = f"Could not load {name}: {error}"
            return
        tree = self.trees[name]
        tree.delete(*tree.get_children())
        if not matches:
            tree.insert("", "end", values=("", "No matches right now", "", ""))
        for state, when, home, score, away, _ in matches:
            tree.insert("", "end", values=(when, home, score, away), tags=(state,))


if __name__ == "__main__":
    App().mainloop()
