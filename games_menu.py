'''

import tkinter as tk
from tkinter import Toplevel, Button, Label, messagebox

class GamesManager:
    """A class to manage and launch all games."""

    def __init__(self, parent):
        self.parent = parent
        self.games = [
            ("Minesweeper", self.launch_minesweeper),
            ("Sudoku", self.launch_sudoku),
            ("Four in a Row", self.launch_four_in_a_row),
            ("Tic Tac Toe", self.launch_tic_tac_toe),
            ("Snake", self.launch_snake),
        ]
        self.instructions = {
            "Minesweeper": (
                "Uncover all safe cells without hitting a mine!\n"
                "• Left-click to reveal a cell.\n"
                "• Right-click to place a flag.\n"
                "• Use hints and safe clicks wisely.\n"
                "• Difficulty is chosen at the start."
            ),
            "Sudoku": (
                "Fill the grid so every row, column, and 3x3 box contains 1–9.\n"
                "• Click a cell and type a number.\n"
                "• Use 'Hint' or 'Solve' if stuck.\n"
                "• Choose difficulty and enjoy!"
            ),
            "Four in a Row": (
                "Connect four of your discs in a row (vertically, horizontally, or diagonally) before your opponent!\n"
                "• Click the arrow above a column to drop your disc.\n"
                "• Play against a friend or bot."
            ),
            "Tic Tac Toe": (
                "Get three in a row (across, down, or diagonal) to win.\n"
                "• Click a square to place X.\n"
                "• Try to beat the bot at different difficulties."
            ),
            "Snake": (
                "Eat food to grow and score points.\n"
                "• Arrow keys (or WASD) to move.\n"
                "• Avoid hitting the walls or yourself.\n"
                "• Try classic or effects mode!"
            )
        }

    def show_games_menu(self):
        """Show the games menu in a popup window."""
        menu = Toplevel(self.parent)
        menu.title("Games Menu")
        menu.geometry("340x540")
        menu.resizable(False, False)
        Label(menu, text="Select a Game", font=("Arial", 20, "bold")).pack(pady=18)

        for name, func in self.games:
            Button(menu, text=name, font=("Arial", 16), width=20, height=2, command=func).pack(pady=8)

        Button(menu, text="Instructions", font=("Arial", 13), width=20, height=2, bg="#f0e68c", command=self.show_instructions).pack(pady=16)
        Button(menu, text="Close", font=("Arial", 12), command=menu.destroy).pack(pady=6)

    def show_instructions(self):
        win = Toplevel(self.parent)
        win.title("Game Instructions")
        win.geometry("420x470")
        win.resizable(False, False)
        Label(win, text="Game Instructions", font=("Arial", 18, "bold")).pack(pady=10)
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        text = tk.Text(frame, font=("Arial", 13), wrap="word", width=48, height=22, bg="#fcfcf7")
        for game, instr in self.instructions.items():
            text.insert("end", f"{game}:\n{instr}\n\n")
        text.config(state="disabled")
        text.pack(fill="both", expand=True)
        Button(win, text="Close", font=("Arial", 12), command=win.destroy).pack(pady=8)

    # --- Game launchers (assume each file has a main class with these names) ---

    def launch_minesweeper(self):
        try:
            from minesweeper import Minesweeper
            Minesweeper(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Minesweeper", e)

    def launch_sudoku(self):
        try:
            from sudoku import Sudoku
            Sudoku(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Sudoku", e)

    def launch_four_in_a_row(self):
        try:
            from four_in_a_row import FourInARow
            FourInARow(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Four in a Row", e)

    def launch_tic_tac_toe(self):
        try:
            from tic_tac_toe import TicTacToe
            TicTacToe(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Tic Tac Toe", e)

    def launch_snake(self):
        try:
            from snake import SnakeGame
            SnakeGame(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Snake", e)

    def _show_error(self, game, e):
        from tkinter import messagebox
        messagebox.showerror("Game Launch Error", f"Could not launch {game}:\n{e}")
'''

import tkinter as tk
from tkinter import Toplevel, Button, Label, messagebox


class GamesManager:
    """A class to manage and launch all games."""

    def __init__(self, parent):
        self.parent = parent
        self.games = [
            ("Chess", self.launch_chess),
            ("Minesweeper", self.launch_minesweeper),
            ("Sudoku", self.launch_sudoku),
            ("Four in a Row", self.launch_four_in_a_row),
            ("Tic Tac Toe", self.launch_tic_tac_toe),
            ("Snake", self.launch_snake),
        ]
        self.instructions = {
            "Chess": (
                "Classic chess game with multiple modes!\n"
                "• Play against AI (Easy, Medium, Hard)\n"
                "• Play locally with a friend (2 players)\n"
                "• Play online against remote opponents\n"
                "• Click a piece to select it, then click destination\n"
                "• All standard chess rules apply\n"
                "• Pawn promotion to Queen is automatic\n"
                "• Game detects check and checkmate"
            ),
            "Minesweeper": (
                "Uncover all safe cells without hitting a mine!\n"
                "• Left-click to reveal a cell.\n"
                "• Right-click to place a flag.\n"
                "• Use hints and safe clicks wisely.\n"
                "• Difficulty is chosen at the start."
            ),
            "Sudoku": (
                "Fill the grid so every row, column, and 3x3 box contains 1–9.\n"
                "• Click a cell and type a number.\n"
                "• Use 'Hint' or 'Solve' if stuck.\n"
                "• Choose difficulty and enjoy!"
            ),
            "Four in a Row": (
                "Connect four of your discs in a row (vertically, horizontally, or diagonally) before your opponent!\n"
                "• Click the arrow above a column to drop your disc.\n"
                "• Play against a friend or bot."
            ),
            "Tic Tac Toe": (
                "Get three in a row (across, down, or diagonal) to win.\n"
                "• Click a square to place X.\n"
                "• Try to beat the bot at different difficulties."
            ),
            "Snake": (
                "Eat food to grow and score points.\n"
                "• Arrow keys (or WASD) to move.\n"
                "• Avoid hitting the walls or yourself.\n"
                "• Try classic or effects mode!"
            )
        }

    def show_games_menu(self):
        """Show the games menu in a popup window."""
        menu = Toplevel(self.parent)
        menu.title("Games Menu")
        menu.geometry("340x600")
        menu.resizable(False, False)
        Label(menu, text="Select a Game", font=("Arial", 20, "bold")).pack(pady=18)

        for name, func in self.games:
            Button(menu, text=name, font=("Arial", 16), width=20, height=2, command=func).pack(pady=8)

        Button(menu, text="Instructions", font=("Arial", 13), width=20, height=2, bg="#f0e68c",
               command=self.show_instructions).pack(pady=16)
        Button(menu, text="Close", font=("Arial", 12), command=menu.destroy).pack(pady=6)

    def show_instructions(self):
        win = Toplevel(self.parent)
        win.title("Game Instructions")
        win.geometry("450x550")
        win.resizable(False, False)
        Label(win, text="Game Instructions", font=("Arial", 18, "bold")).pack(pady=10)
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Add scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        text = tk.Text(frame, font=("Arial", 12), wrap="word", width=50, height=26,
                       bg="#fcfcf7", yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)

        for game, instr in self.instructions.items():
            text.insert("end", f"♔ {game}:\n{instr}\n\n", "bold" if game == "Chess" else "")

        text.tag_config("bold", font=("Arial", 13, "bold"))
        text.config(state="disabled")
        text.pack(side='left', fill="both", expand=True)

        Button(win, text="Close", font=("Arial", 12), command=win.destroy).pack(pady=8)

    # --- Game launchers ---

    def launch_chess(self):
        """Launch the chess game."""
        try:
            from chess import ChessGame
            ChessGame(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Chess", e)

    def launch_minesweeper(self):
        try:
            from minesweeper import Minesweeper
            Minesweeper(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Minesweeper", e)

    def launch_sudoku(self):
        try:
            from sudoku import Sudoku
            Sudoku(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Sudoku", e)

    def launch_four_in_a_row(self):
        try:
            from four_in_a_row import FourInARow
            FourInARow(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Four in a Row", e)

    def launch_tic_tac_toe(self):
        try:
            from tic_tac_toe import TicTacToe
            TicTacToe(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Tic Tac Toe", e)

    def launch_snake(self):
        try:
            from snake import SnakeGame
            SnakeGame(tk.Toplevel(self.parent))
        except Exception as e:
            self._show_error("Snake", e)

    def _show_error(self, game, e):
        from tkinter import messagebox
        messagebox.showerror("Game Launch Error", f"Could not launch {game}:\n{e}")