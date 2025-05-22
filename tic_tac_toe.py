import tkinter as tk
from tkinter import messagebox
import random
import copy

# Bot personalities
BOT_PERSONALITIES = [
    "You won't beat me this time!",
    "Nice try!",
    "Hmm... Let me think...",
    "Are you sure about that move?",
    "I'm just warming up.",
    "You got lucky last time.",
    "My circuits are ready for this.",
    "This is fun, right?",
    "I see what you're doing.",
    "I'm on to you!"
]

# Themes
THEMES = {
    "Classic": {
        "bg": "#222",
        "fg": "#fafafa",
        "x": "#44f",
        "o": "#f44",
        "hl": "#ff0",
        "board": "#fafafa",
        "turn_bg": "#333",
        "turn_fg": "#fafafa"
    },
    "Light": {
        "bg": "#f5f5f5",
        "fg": "#333",
        "x": "#0066ff",
        "o": "#ee2222",
        "hl": "#f2e300",
        "board": "#ffffff",
        "turn_bg": "#e0e0e0",
        "turn_fg": "#222"
    },
    "Ocean": {
        "bg": "#023047",
        "fg": "#8ecae6",
        "x": "#219ebc",
        "o": "#ffb703",
        "hl": "#fb8500",
        "board": "#8ecae6",
        "turn_bg": "#219ebc",
        "turn_fg": "#fff"
    }
}

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Ultimate Edition")
        self.player_symbol = "X"
        self.bot_symbol = "O"
        self.stats = {"Wins": 0, "Losses": 0, "Draws": 0}
        self.move_stack = []
        self.turn = "player"
        self.theme_name = "Classic"
        self.theme = THEMES[self.theme_name]
        self.replay_moves = []
        self.replay_index = 0
        self.replay_mode = False
        self.access_keymap = {}
        self.create_menu()

    # ---------------- UI AND THEMES -----------------------
    def apply_theme(self):
        self.theme = THEMES[self.theme_name]
        self.root.config(bg=self.theme["bg"])
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=self.theme["bg"])
            except:
                pass

    def create_menu(self):
        self.clear_window()
        self.replay_mode = False
        self.apply_theme()
        frame = tk.Frame(self.root, bg=self.theme["bg"])
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Tic Tac Toe", font=("Arial", 26, "bold"), fg=self.theme["x"], bg=self.theme["bg"]).pack(pady=16)
        tk.Label(frame, text="Choose Difficulty:", font=("Arial", 16), fg=self.theme["fg"], bg=self.theme["bg"]).pack(pady=10)
        btn_frame = tk.Frame(frame, bg=self.theme["bg"])
        btn_frame.pack()
        for text, diff in [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard"), ("Impossible", "impossible")]:
            tk.Button(
                btn_frame, text=text, width=14, font=("Arial", 13, "bold"),
                bg=self.theme["turn_bg"], fg=self.theme["turn_fg"], activebackground=self.theme["x"], activeforeground=self.theme["fg"],
                command=lambda d=diff: self.start_game(d)
            ).pack(padx=8, pady=6, side=tk.LEFT)
        theme_frame = tk.Frame(frame, bg=self.theme["bg"])
        theme_frame.pack(pady=(10, 0))
        tk.Label(theme_frame, text="Theme:", font=("Arial", 12), fg=self.theme["fg"], bg=self.theme["bg"]).pack(side=tk.LEFT)
        for name in THEMES:
            tk.Button(theme_frame, text=name, width=9, font=("Arial", 10),
                      bg=self.theme["turn_bg"], fg=self.theme["turn_fg"],
                      command=lambda n=name: self.change_theme(n)).pack(side=tk.LEFT, padx=4)
        stats_txt = f"Wins: {self.stats['Wins']}   Losses: {self.stats['Losses']}   Draws: {self.stats['Draws']}"
        tk.Label(frame, text=stats_txt, font=("Arial", 12, "italic"), fg=self.theme["fg"], bg=self.theme["bg"]).pack(pady=25)
        # Accessibility: focus set
        frame.focus_set()

    def change_theme(self, name):
        self.theme_name = name
        self.theme = THEMES[self.theme_name]
        self.create_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_turn_ui(self):
        """Update UI to reflect whose turn it is, and disable/enable buttons appropriately."""
        if self.replay_mode:
            return
        if self.turn == "player":
            self.turn_label.config(text="Your turn! (X)", fg=self.theme["x"], bg=self.theme["turn_bg"])
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "" and not self.game_over:
                        self.buttons[i][j].config(state=tk.NORMAL, cursor="hand2")
                    else:
                        self.buttons[i][j].config(state=tk.DISABLED, cursor="arrow")
            self.hint_button.config(state=tk.NORMAL)
            self.undo_button.config(state=tk.NORMAL if len(self.move_stack) > 0 and not self.game_over else tk.DISABLED)
        else:
            self.turn_label.config(text="Bot's turn... (O)", fg=self.theme["o"], bg=self.theme["turn_bg"])
            for i in range(3):
                for j in range(3):
                    self.buttons[i][j].config(state=tk.DISABLED, cursor="arrow")
            self.hint_button.config(state=tk.DISABLED)
            self.undo_button.config(state=tk.DISABLED)
            # Show bot personality
            self.personality_label.config(text=random.choice(BOT_PERSONALITIES), fg=self.theme["fg"])
            self.root.after(650, self.bot_move)

    # ---------------- GAME FLOW -----------------------
    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.move_count = 0
        self.game_over = False
        self.turn = "player"
        self.move_stack = []
        self.replay_moves = []
        self.replay_index = 0
        self.replay_mode = False
        self.clear_window()
        self.apply_theme()

        top = tk.Frame(self.root, bg=self.theme["bg"])
        top.pack(pady=(15, 0), fill=tk.X)
        tk.Label(top, text=f"Difficulty: {difficulty.capitalize()}  (You: X, Bot: O)", font=("Arial", 15, "bold"), fg=self.theme["fg"], bg=self.theme["bg"]).pack(side=tk.LEFT, padx=10)
        tk.Button(top, text="Back", command=self.create_menu, font=("Arial", 10, "bold"),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"]).pack(side=tk.RIGHT, padx=10)

        board_frame = tk.Frame(self.root, bg=self.theme["bg"])
        board_frame.pack(pady=18)
        self.buttons = []
        self.access_keymap = {}
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(
                    board_frame, text="", width=5, height=2, font=("Arial", 32, "bold"),
                    bg=self.theme["board"], fg=self.theme["fg"], relief=tk.RAISED,
                    command=lambda x=i, y=j: self.player_move(x, y)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
                # Accessibility: keyboard bindings
                key = str(1 + i*3 + j)
                self.root.bind(f"<KeyPress-{key}>", lambda e, x=i, y=j: self.player_move(x, y))
                self.access_keymap[key] = (i, j)
            self.buttons.append(row)

        bottom = tk.Frame(self.root, bg=self.theme["bg"])
        bottom.pack(pady=0, fill=tk.X)
        self.turn_label = tk.Label(bottom, text="Your turn! (X)", font=("Arial", 16, "bold"),
                                   fg=self.theme["x"], bg=self.theme["turn_bg"], anchor="w")
        self.turn_label.pack(side=tk.LEFT, padx=(3, 0), fill=tk.X, expand=True)
        self.personality_label = tk.Label(bottom, text="", font=("Arial", 13, "italic"),
                                          fg=self.theme["fg"], bg=self.theme["turn_bg"])
        self.personality_label.pack(side=tk.LEFT, padx=8)

        self.hint_button = tk.Button(bottom, text="Hint", command=self.show_hint, font=("Arial", 11, "bold"),
                                     bg=self.theme["turn_bg"], fg=self.theme["turn_fg"])
        self.hint_button.pack(side=tk.RIGHT, padx=8)
        self.undo_button = tk.Button(bottom, text="Undo", command=self.undo_move, font=("Arial", 11, "bold"),
                                     bg=self.theme["turn_bg"], fg=self.theme["turn_fg"])
        self.undo_button.pack(side=tk.RIGHT, padx=8)
        self.replay_button = tk.Button(bottom, text="Replay", command=self.start_replay, font=("Arial", 11, "bold"),
                                       bg=self.theme["turn_bg"], fg=self.theme["turn_fg"])
        self.replay_button.pack(side=tk.RIGHT, padx=8)

        stats_txt = f"Wins: {self.stats['Wins']}   Losses: {self.stats['Losses']}   Draws: {self.stats['Draws']}"
        self.stats_label = tk.Label(self.root, text=stats_txt, font=("Arial", 12, "italic"),
                                    fg=self.theme["fg"], bg=self.theme["bg"])
        self.stats_label.pack(pady=(7, 4))

        self.update_turn_ui()
        # Accessibility: focus set
        board_frame.focus_set()

    def player_move(self, row, col):
        if self.turn != "player" or self.board[row][col] or self.game_over or self.replay_mode:
            return
        self.make_move(row, col, self.player_symbol)
        if not self.game_over:
            self.turn = "bot"
            self.update_turn_ui()

    def make_move(self, row, col, symbol):
        """Place move, update state, and check for win/draw."""
        if self.board[row][col] or self.game_over:
            return
        # Record move for undo and replay
        self.move_stack.append((copy.deepcopy(self.board), self.turn))
        self.replay_moves.append((row, col, symbol))
        self.board[row][col] = symbol
        self.move_count += 1
        self.update_board_ui()

        winner, win_line = self.check_winner(return_line=True)
        if winner:
            self.game_over = True
            self.highlight_winner(win_line)
            self.turn_label.config(
                text="You win! 🎉" if winner == self.player_symbol else "Bot wins! 😢" if winner == self.bot_symbol else "It's a draw.",
                fg=self.theme["x"] if winner == self.player_symbol else self.theme["o"] if winner == self.bot_symbol else self.theme["fg"],
                bg=self.theme["turn_bg"]
            )
            if winner == self.player_symbol:
                self.stats["Wins"] += 1
            elif winner == self.bot_symbol:
                self.stats["Losses"] += 1
            else:
                self.stats["Draws"] += 1
            self.update_stats_ui()
            self.show_end_screen(winner)
        elif self.move_count == 9:
            self.game_over = True
            self.turn_label.config(text="It's a draw.", fg=self.theme["fg"], bg=self.theme["turn_bg"])
            self.stats["Draws"] += 1
            self.update_stats_ui()
            self.show_end_screen("draw")

    def update_board_ui(self):
        # Update board button texts and colors
        for i in range(3):
            for j in range(3):
                val = self.board[i][j]
                if val == "X":
                    self.buttons[i][j].config(text="X", fg=self.theme["x"], bg=self.theme["board"])
                elif val == "O":
                    self.buttons[i][j].config(text="O", fg=self.theme["o"], bg=self.theme["board"])
                else:
                    self.buttons[i][j].config(text="", fg=self.theme["fg"], bg=self.theme["board"])
                self.buttons[i][j].config(relief=tk.RAISED)

    def highlight_winner(self, win_line):
        if not win_line:
            return
        for (i, j) in win_line:
            self.buttons[i][j].config(bg=self.theme["hl"], relief=tk.SUNKEN)

    def update_stats_ui(self):
        stats_txt = f"Wins: {self.stats['Wins']}   Losses: {self.stats['Losses']}   Draws: {self.stats['Draws']}"
        self.stats_label.config(text=stats_txt)

    # ---------------- BOT -----------------------
    def bot_move(self):
        if self.game_over or self.replay_mode:
            return
        row, col = self.choose_bot_move()
        self.make_move(row, col, self.bot_symbol)
        if not self.game_over:
            self.turn = "player"
            self.update_turn_ui()

    def choose_bot_move(self):
        """Choose bot's move based on difficulty."""
        empty = [(i, j) for i in range(3) for j in range(3) if not self.board[i][j]]
        if self.difficulty == "easy":
            move = self.try_win_or_block()
            if move is not None:
                return move
            return random.choice(empty)
        elif self.difficulty == "medium":
            move = self.try_win_or_block()
            if move is not None:
                return move
            # Prefer center, then corners
            if self.board[1][1] == "":
                return (1, 1)
            for (i, j) in [(0,0),(0,2),(2,0),(2,2)]:
                if self.board[i][j] == "":
                    return (i, j)
            return random.choice(empty)
        elif self.difficulty == "hard":
            if self.move_count < 2:
                return self.find_best_move(self.bot_symbol)
            move = self.try_win_or_block()
            if move is not None:
                return move
            if self.board[1][1] == "":
                return (1, 1)
            for (i, j) in [(0,0),(0,2),(2,0),(2,2)]:
                if self.board[i][j] == "":
                    return (i, j)
            return random.choice(empty)
        elif self.difficulty == "impossible":
            return self.find_best_move(self.bot_symbol)
        return random.choice(empty)

    def try_win_or_block(self):
        """Try to win, else block the player."""
        # Try to win
        for i, j in [(x, y) for x in range(3) for y in range(3) if self.board[x][y] == ""]:
            temp = [row[:] for row in self.board]
            temp[i][j] = self.bot_symbol
            if self.check_winner(temp) == self.bot_symbol:
                return (i, j)
        # Try to block player
        for i, j in [(x, y) for x in range(3) for y in range(3) if self.board[x][y] == ""]:
            temp = [row[:] for row in self.board]
            temp[i][j] = self.player_symbol
            if self.check_winner(temp) == self.player_symbol:
                return (i, j)
        return None

    def find_best_move(self, symbol):
        """Minimax algorithm for perfect play. Returns (row, col)."""
        board = copy.deepcopy(self.board)
        best_score = -float('inf')
        best_move = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = symbol
                    score = self.minimax(board, 0, False)
                    board[i][j] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        return best_move

    def minimax(self, board, depth, is_max):
        winner = self.check_winner(board)
        if winner == self.bot_symbol:
            return 10 - depth
        elif winner == self.player_symbol:
            return depth - 10
        elif all(board[i][j] != "" for i in range(3) for j in range(3)):
            return 0

        if is_max:
            max_eval = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.bot_symbol
                        eval = self.minimax(board, depth + 1, False)
                        board[i][j] = ""
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.player_symbol
                        eval = self.minimax(board, depth + 1, True)
                        board[i][j] = ""
                        min_eval = min(min_eval, eval)
            return min_eval

    # ---------------- HINTS -----------------------
    def show_hint(self):
        if self.turn != "player" or self.game_over or self.replay_mode:
            return
        move = self.find_best_move(self.player_symbol)
        if move:
            i, j = move
            self.buttons[i][j].config(bg="#6afd6a")
            self.root.after(700, lambda: self.reset_hint(i, j))

    def reset_hint(self, i, j):
        val = self.board[i][j]
        if val == "X":
            self.buttons[i][j].config(bg=self.theme["board"], fg=self.theme["x"])
        elif val == "O":
            self.buttons[i][j].config(bg=self.theme["board"], fg=self.theme["o"])
        else:
            self.buttons[i][j].config(bg=self.theme["board"], fg=self.theme["fg"])

    # ---------------- UNDO -----------------------
    def undo_move(self):
        """Undo the last player+bot move (if possible)."""
        if not self.move_stack or self.replay_mode:
            return
        # Undo bot move (if present)
        if self.turn == "player" and len(self.move_stack) > 0:
            self.board, _ = self.move_stack.pop()
            self.move_count = sum(1 for row in self.board for cell in row if cell != "")
            if self.replay_moves:
                self.replay_moves.pop()
        # Undo player move (if present)
        if len(self.move_stack) > 0:
            self.board, _ = self.move_stack.pop()
            self.move_count = sum(1 for row in self.board for cell in row if cell != "")
            if self.replay_moves:
                self.replay_moves.pop()
        self.game_over = False
        self.turn = "player"
        self.update_board_ui()
        self.update_turn_ui()
        # Remove highlights
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(relief=tk.RAISED, bg=self.theme["board"])

    # ---------------- CHECK WINNER AND HIGHLIGHT -----------------------
    def check_winner(self, board=None, return_line=False):
        """Return 'X', 'O', 'draw', or None. If return_line: also return winning line."""
        if board is None:
            board = self.board
        lines = []
        for i in range(3):
            lines.append([(i, 0), (i, 1), (i, 2)])
            lines.append([(0, i), (1, i), (2, i)])
        lines.append([(0, 0), (1, 1), (2, 2)])
        lines.append([(0, 2), (1, 1), (2, 0)])
        for line in lines:
            vals = [board[x][y] for (x, y) in line]
            if vals[0] and vals.count(vals[0]) == 3:
                return (vals[0], line) if return_line else vals[0]
        if all(board[i][j] != "" for i in range(3) for j in range(3)):
            return ("draw", []) if return_line else "draw"
        return (None, []) if return_line else None

    # ---------------- REPLAY -----------------------
    def start_replay(self):
        if not self.replay_moves:
            messagebox.showinfo("Replay", "No game to replay yet!")
            return
        self.replay_index = 0
        self.replay_mode = True
        self.clear_window()
        self.apply_theme()
        top = tk.Frame(self.root, bg=self.theme["bg"])
        top.pack(pady=(15, 0), fill=tk.X)
        tk.Label(top, text="Replay Game", font=("Arial", 15, "bold"),
                 fg=self.theme["fg"], bg=self.theme["bg"]).pack(side=tk.LEFT, padx=10)
        tk.Button(top, text="Back", command=self.end_replay, font=("Arial", 10, "bold"),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"]).pack(side=tk.RIGHT, padx=10)
        board_frame = tk.Frame(self.root, bg=self.theme["bg"])
        board_frame.pack(pady=18)
        self.replay_buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(
                    board_frame, text="", width=5, height=2, font=("Arial", 32, "bold"),
                    bg=self.theme["board"], fg=self.theme["fg"], relief=tk.RAISED, state=tk.DISABLED
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.replay_buttons.append(row)
        control = tk.Frame(self.root, bg=self.theme["bg"])
        control.pack()
        tk.Button(control, text="⏮ Prev", command=self.prev_replay, font=("Arial", 12, "bold"),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"]).pack(side=tk.LEFT, padx=8)
        tk.Button(control, text="⏭ Next", command=self.next_replay, font=("Arial", 12, "bold"),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"]).pack(side=tk.LEFT, padx=8)
        self.replay_status = tk.Label(self.root, text="", font=("Arial", 13, "italic"),
                                      fg=self.theme["fg"], bg=self.theme["bg"])
        self.replay_status.pack(pady=8)
        self.show_replay_state()

    def end_replay(self):
        self.replay_mode = False
        self.create_menu()

    def show_replay_state(self):
        # Show moves up to replay_index
        board = [["" for _ in range(3)] for _ in range(3)]
        for idx in range(self.replay_index):
            i, j, sym = self.replay_moves[idx]
            board[i][j] = sym
        for i in range(3):
            for j in range(3):
                val = board[i][j]
                if val == "X":
                    self.replay_buttons[i][j].config(text="X", fg=self.theme["x"], bg=self.theme["board"])
                elif val == "O":
                    self.replay_buttons[i][j].config(text="O", fg=self.theme["o"], bg=self.theme["board"])
                else:
                    self.replay_buttons[i][j].config(text="", fg=self.theme["fg"], bg=self.theme["board"])
                self.replay_buttons[i][j].config(relief=tk.RAISED)
        # Highlight win if at game end
        winner, win_line = self.check_winner(board, return_line=True)
        if winner and winner != "draw":
            for (i, j) in win_line:
                self.replay_buttons[i][j].config(bg=self.theme["hl"], relief=tk.SUNKEN)
        self.replay_status.config(text=f"Move {self.replay_index}/{len(self.replay_moves)}")

    def next_replay(self):
        if self.replay_index < len(self.replay_moves):
            self.replay_index += 1
            self.show_replay_state()

    def prev_replay(self):
        if self.replay_index > 0:
            self.replay_index -= 1
            self.show_replay_state()

    # ---------------- END SCREEN -----------------------
    def show_end_screen(self, winner):
        if self.replay_mode:
            return
        if winner == self.player_symbol:
            msg = "🎉 You win!"
        elif winner == self.bot_symbol:
            msg = "😢 Bot wins!"
        else:
            msg = "It's a draw."
        def restart():
            self.start_game(self.difficulty)
        def back():
            self.create_menu()
        msgbox = tk.Toplevel(self.root)
        msgbox.title("Game Over")
        msgbox.grab_set()
        msgbox.geometry("+%d+%d" % (self.root.winfo_rootx()+100, self.root.winfo_rooty()+100))
        tk.Label(msgbox, text=msg, font=("Arial", 20, "bold"),
                 fg=self.theme["x"] if winner==self.player_symbol else self.theme["o"], pady=20).pack()
        tk.Button(msgbox, text="Play Again", width=15, font=("Arial", 12, "bold"),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"],
                  command=lambda: [msgbox.destroy(), restart()]).pack(pady=7)
        tk.Button(msgbox, text="Back to Menu", width=15, font=("Arial", 12),
                  bg=self.theme["turn_bg"], fg=self.theme["turn_fg"],
                  command=lambda: [msgbox.destroy(), back()]).pack(pady=(0,14))

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()