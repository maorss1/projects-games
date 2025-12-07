import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Button, Frame, Entry, Text, Scrollbar
import socket
import threading
import time
import subprocess
import os
import copy

# Chess piece Unicode symbols
PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}


class StockfishEngine:
    """Interface to Stockfish chess engine."""

    def __init__(self, difficulty='medium'):
        self.process = None
        self.difficulty = difficulty

        # Skill levels (0-20, where 20 is strongest)
        self.skill_levels = {
            'easy': 5,
            'medium': 12,
            'hard': 20
        }

        self.skill = self.skill_levels.get(difficulty, 12)

        # Try to find and start Stockfish
        self.start_engine()

    def start_engine(self):
        """Start the Stockfish engine process."""
        stockfish_paths = [
            'stockfish.exe',  # Windows, same directory
            'stockfish',  # Linux/Mac, same directory
            './stockfish.exe',
            './stockfish',
            'stockfish-windows-x86-64-avx2.exe',
            os.path.join(os.getcwd(), 'stockfish.exe'),
            os.path.join(os.getcwd(), 'stockfish'),
            '/usr/local/bin/stockfish',  # Mac/Linux common install
            '/usr/bin/stockfish',
            'C:\\Program Files\\Stockfish\\stockfish.exe',  # Windows common install
        ]

        for path in stockfish_paths:
            try:
                self.process = subprocess.Popen(
                    path,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )

                # Test if it's working
                self._send_command('uci')
                response = self._read_until('uciok')
                if 'uciok' in response:
                    print(f"[STOCKFISH] Engine started from: {path}")

                    # Set skill level
                    self._send_command(f'setoption name Skill Level value {self.skill}')
                    self._send_command('isready')
                    self._read_until('readyok')
                    return True
            except Exception as e:
                if self.process:
                    try:
                        self.process.kill()
                    except:
                        pass
                    self.process = None
                continue

        print("[STOCKFISH] Engine not found. AI will use fallback logic.")
        return False

    def _send_command(self, command):
        """Send command to engine."""
        if self.process:
            try:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
            except:
                pass

    def _read_until(self, marker, timeout=5):
        """Read output until marker is found."""
        if not self.process:
            return ""

        start_time = time.time()
        output = []

        while time.time() - start_time < timeout:
            try:
                line = self.process.stdout.readline().strip()
                output.append(line)
                if marker in line:
                    break
            except:
                break

        return '\n'.join(output)

    def get_best_move(self, fen, movetime=1000):
        """Get best move from current position."""
        if not self.process:
            return None

        try:
            # Set position
            self._send_command(f'position fen {fen}')

            # Calculate move
            self._send_command(f'go movetime {movetime}')

            # Read bestmove
            output = self._read_until('bestmove')

            for line in output.split('\n'):
                if line.startswith('bestmove'):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]  # Return UCI move (e.g., "e2e4")

            return None
        except Exception as e:
            print(f"[STOCKFISH] Error: {e}")
            return None

    def close(self):
        """Close the engine."""
        if self.process:
            try:
                self._send_command('quit')
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None


class ChessBoard:
    """Complete chess board with all rules."""

    def __init__(self):
        self.reset_board()

    def reset_board(self):
        """Reset to starting position."""
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self.current_turn = 'white'
        self.move_history = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_kingside_moved = False
        self.white_rook_queenside_moved = False
        self.black_rook_kingside_moved = False
        self.black_rook_queenside_moved = False
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def get_fen(self):
        """Get FEN string of current position."""
        fen_parts = []

        # 1. Piece placement
        for row in self.board:
            empty = 0
            row_str = ""
            for piece in row:
                if piece == '.':
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += piece
            if empty > 0:
                row_str += str(empty)
            fen_parts.append(row_str)

        fen = '/'.join(fen_parts)

        # 2. Active color
        fen += ' w ' if self.current_turn == 'white' else ' b '

        # 3. Castling rights
        castling = ""
        if not self.white_king_moved:
            if not self.white_rook_kingside_moved:
                castling += 'K'
            if not self.white_rook_queenside_moved:
                castling += 'Q'
        if not self.black_king_moved:
            if not self.black_rook_kingside_moved:
                castling += 'k'
            if not self.black_rook_queenside_moved:
                castling += 'q'
        fen += castling if castling else '-'
        fen += ' '

        # 4. En passant
        if self.en_passant_target:
            row, col = self.en_passant_target
            fen += chr(97 + col) + str(8 - row)
        else:
            fen += '-'

        # 5. Halfmove clock
        fen += f' {self.halfmove_clock}'

        # 6. Fullmove number
        fen += f' {self.fullmove_number}'

        return fen

    def get_piece(self, row, col):
        """Get piece at position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row, col, piece):
        """Set piece at position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def is_white_piece(self, piece):
        """Check if piece is white."""
        return piece.isupper()

    def is_black_piece(self, piece):
        """Check if piece is black."""
        return piece.islower()

    def get_valid_moves_for_piece(self, row, col):
        """Get all valid moves for piece at position."""
        valid_moves = []
        piece = self.get_piece(row, col)

        if piece == '.':
            return valid_moves

        # Check turn
        if self.current_turn == 'white' and not self.is_white_piece(piece):
            return valid_moves
        if self.current_turn == 'black' and not self.is_black_piece(piece):
            return valid_moves

        # Check all possible destinations
        for to_row in range(8):
            for to_col in range(8):
                if self.is_valid_move(row, col, to_row, to_col):
                    valid_moves.append((to_row, to_col))

        return valid_moves

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        """Check if move is valid."""
        piece = self.get_piece(from_row, from_col)
        if piece == '.':
            return False

        # Check turn
        if self.current_turn == 'white' and not self.is_white_piece(piece):
            return False
        if self.current_turn == 'black' and not self.is_black_piece(piece):
            return False

        # Check destination
        target = self.get_piece(to_row, to_col)
        if target != '.':
            if self.current_turn == 'white' and self.is_white_piece(target):
                return False
            if self.current_turn == 'black' and self.is_black_piece(target):
                return False

        # Check castling
        if piece.lower() == 'k' and abs(to_col - from_col) == 2:
            return self._is_valid_castling(from_row, from_col, to_row, to_col)

        # Check piece-specific moves
        if not self._is_legal_piece_move(piece.lower(), from_row, from_col, to_row, to_col):
            return False

        # Check if move puts own king in check
        if self._move_causes_check(from_row, from_col, to_row, to_col):
            return False

        return True

    def _is_valid_castling(self, from_row, from_col, to_row, to_col):
        """Check if castling is valid."""
        piece = self.get_piece(from_row, from_col)

        if piece.lower() != 'k':
            return False

        if self.current_turn == 'white' and self.white_king_moved:
            return False
        if self.current_turn == 'black' and self.black_king_moved:
            return False

        if from_row != to_row or abs(to_col - from_col) != 2:
            return False

        # Kingside
        if to_col > from_col:
            if self.current_turn == 'white' and self.white_rook_kingside_moved:
                return False
            if self.current_turn == 'black' and self.black_rook_kingside_moved:
                return False

            for col in range(from_col + 1, 7):
                if self.get_piece(from_row, col) != '.':
                    return False

            for col in range(from_col, from_col + 3):
                if self._is_square_attacked(from_row, col, self.current_turn):
                    return False

            return True

        # Queenside
        else:
            if self.current_turn == 'white' and self.white_rook_queenside_moved:
                return False
            if self.current_turn == 'black' and self.black_rook_queenside_moved:
                return False

            for col in range(1, from_col):
                if self.get_piece(from_row, col) != '.':
                    return False

            for col in range(from_col - 2, from_col + 1):
                if self._is_square_attacked(from_row, col, self.current_turn):
                    return False

            return True

    def _is_legal_piece_move(self, piece, from_row, from_col, to_row, to_col):
        """Check piece-specific move rules."""
        dr = to_row - from_row
        dc = to_col - from_col

        if piece == 'p':
            return self._is_legal_pawn_move(from_row, from_col, to_row, to_col, dr, dc)
        elif piece == 'n':
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]
        elif piece == 'b':
            return abs(dr) == abs(dc) and self._is_path_clear(from_row, from_col, to_row, to_col)
        elif piece == 'r':
            return (dr == 0 or dc == 0) and self._is_path_clear(from_row, from_col, to_row, to_col)
        elif piece == 'q':
            return (dr == 0 or dc == 0 or abs(dr) == abs(dc)) and self._is_path_clear(from_row, from_col, to_row,
                                                                                      to_col)
        elif piece == 'k':
            return abs(dr) <= 1 and abs(dc) <= 1
        return False

    def _is_legal_pawn_move(self, from_row, from_col, to_row, to_col, dr, dc):
        """Check pawn move rules."""
        piece = self.get_piece(from_row, from_col)
        direction = -1 if self.is_white_piece(piece) else 1
        start_row = 6 if self.is_white_piece(piece) else 1

        if dc == 0:
            if dr == direction and self.get_piece(to_row, to_col) == '.':
                return True
            if from_row == start_row and dr == 2 * direction:
                if self.get_piece(to_row, to_col) == '.' and self.get_piece(from_row + direction, from_col) == '.':
                    return True
        elif abs(dc) == 1 and dr == direction:
            target = self.get_piece(to_row, to_col)
            if target != '.':
                if self.is_white_piece(piece) and self.is_black_piece(target):
                    return True
                if self.is_black_piece(piece) and self.is_white_piece(target):
                    return True
            if self.en_passant_target == (to_row, to_col):
                return True
        return False

    def _is_path_clear(self, from_row, from_col, to_row, to_col):
        """Check if path is clear."""
        dr = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        dc = 0 if to_col == from_col else (1 if to_col > from_col else -1)

        r, c = from_row + dr, from_col + dc
        while (r, c) != (to_row, to_col):
            if self.get_piece(r, c) != '.':
                return False
            r += dr
            c += dc
        return True

    def _move_causes_check(self, from_row, from_col, to_row, to_col):
        """Check if move puts own king in check."""
        temp_board = copy.deepcopy(self.board)
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = '.'

        king = 'K' if self.current_turn == 'white' else 'k'
        king_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        in_check = self._is_square_attacked(king_pos[0], king_pos[1], self.current_turn)
        self.board = temp_board
        return in_check

    def _is_square_attacked(self, row, col, by_color):
        """Check if square is attacked."""
        opponent = 'black' if by_color == 'white' else 'white'

        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece == '.':
                    continue
                if opponent == 'white' and not self.is_white_piece(piece):
                    continue
                if opponent == 'black' and not self.is_black_piece(piece):
                    continue

                old_turn = self.current_turn
                self.current_turn = opponent

                can_attack = False
                if piece.lower() != 'k':
                    can_attack = self._is_legal_piece_move(piece.lower(), r, c, row, col)
                else:
                    dr, dc = abs(row - r), abs(col - c)
                    can_attack = dr <= 1 and dc <= 1

                self.current_turn = old_turn

                if can_attack:
                    return True
        return False

    def is_in_check(self):
        """Check if current player is in check."""
        king = 'K' if self.current_turn == 'white' else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    return self._is_square_attacked(r, c, self.current_turn)
        return False

    def has_legal_moves(self):
        """Check if current player has legal moves."""
        for from_r in range(8):
            for from_c in range(8):
                piece = self.get_piece(from_r, from_c)
                if piece == '.':
                    continue
                if self.current_turn == 'white' and not self.is_white_piece(piece):
                    continue
                if self.current_turn == 'black' and not self.is_black_piece(piece):
                    continue

                for to_r in range(8):
                    for to_c in range(8):
                        if self.is_valid_move(from_r, from_c, to_r, to_c):
                            return True
        return False

    def is_checkmate(self):
        """Check if checkmate."""
        if not self.is_in_check():
            return False
        return not self.has_legal_moves()

    def is_stalemate(self):
        """Check if stalemate."""
        if self.is_in_check():
            return False
        return not self.has_legal_moves()

    def make_move(self, from_row, from_col, to_row, to_col, promotion_piece=None):
        """Make a move."""
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False

        piece = self.get_piece(from_row, from_col)
        captured = self.get_piece(to_row, to_col)

        # Castling
        if piece.lower() == 'k' and abs(to_col - from_col) == 2:
            if to_col > from_col:
                rook = self.get_piece(from_row, 7)
                self.set_piece(from_row, 7, '.')
                self.set_piece(from_row, to_col - 1, rook)
            else:
                rook = self.get_piece(from_row, 0)
                self.set_piece(from_row, 0, '.')
                self.set_piece(from_row, to_col + 1, rook)

        # En passant
        if piece.lower() == 'p' and self.en_passant_target == (to_row, to_col):
            capture_row = from_row
            self.set_piece(capture_row, to_col, '.')
            captured = 'p' if self.current_turn == 'white' else 'P'

        # Update en passant
        self.en_passant_target = None
        if piece.lower() == 'p' and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)

        # Make move
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, '.')

        # Promotion
        if piece.lower() == 'p':
            if (self.is_white_piece(piece) and to_row == 0) or (self.is_black_piece(piece) and to_row == 7):
                if promotion_piece:
                    self.set_piece(to_row, to_col, promotion_piece)
                else:
                    self.set_piece(to_row, to_col, 'Q' if self.is_white_piece(piece) else 'q')

        # Update king position
        if piece.lower() == 'k':
            if self.is_white_piece(piece):
                self.white_king_pos = (to_row, to_col)
                self.white_king_moved = True
            else:
                self.black_king_pos = (to_row, to_col)
                self.black_king_moved = True

        # Update rook flags
        if piece.lower() == 'r':
            if self.is_white_piece(piece):
                if from_row == 7 and from_col == 7:
                    self.white_rook_kingside_moved = True
                elif from_row == 7 and from_col == 0:
                    self.white_rook_queenside_moved = True
            else:
                if from_row == 0 and from_col == 7:
                    self.black_rook_kingside_moved = True
                elif from_row == 0 and from_col == 0:
                    self.black_rook_queenside_moved = True

        # Halfmove clock
        if piece.lower() == 'p' or captured != '.':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Move notation
        move_notation = self._get_move_notation(piece, from_row, from_col, to_row, to_col, captured)
        self.move_history.append({
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece,
            'captured': captured,
            'notation': move_notation
        })

        # Switch turn
        if self.current_turn == 'black':
            self.fullmove_number += 1
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        return True

    def _get_move_notation(self, piece, from_row, from_col, to_row, to_col, captured):
        """Generate algebraic notation."""
        notation = ""

        if piece.lower() == 'k' and abs(to_col - from_col) == 2:
            return "O-O" if to_col > from_col else "O-O-O"

        if piece.lower() != 'p':
            notation += piece.upper()

        if piece.lower() == 'p' and captured != '.':
            notation += chr(97 + from_col)

        if captured != '.':
            notation += "x"

        notation += chr(97 + to_col) + str(8 - to_row)

        return notation


class ChessGame:
    """Main chess game GUI."""

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Chess Game with Stockfish")
        self.parent.geometry("1100x900")
        self.parent.resizable(False, False)

        self.board = ChessBoard()
        self.selected_square = None
        self.valid_moves_highlight = []
        self.game_mode = None
        self.ai_engine = None
        self.online_socket = None
        self.is_white = True
        self.time_control = None
        self.white_time = 600
        self.black_time = 600
        self.last_time_update = None
        self.game_active = False

        self.show_mode_selection()

    def show_mode_selection(self):
        """Show game mode selection."""
        frame = Frame(self.parent, bg='#2c3e50')
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        Label(frame, text="♔ Chess Game ♚", font=("Arial", 32, "bold"),
              bg='#2c3e50', fg='white').pack(pady=30)

        Button(frame, text="Play vs Easy Bot", font=("Arial", 16), width=20, height=2,
               bg='#27ae60', fg='white', command=lambda: self.start_game('bot_easy')).pack(pady=8)
        Button(frame, text="Play vs Medium Bot", font=("Arial", 16), width=20, height=2,
               bg='#f39c12', fg='white', command=lambda: self.start_game('bot_medium')).pack(pady=8)
        Button(frame, text="Play vs Hard Bot", font=("Arial", 16), width=20, height=2,
               bg='#e74c3c', fg='white', command=lambda: self.start_game('bot_hard')).pack(pady=8)
        Button(frame, text="Play Local (2 Players)", font=("Arial", 16), width=20, height=2,
               bg='#3498db', fg='white', command=lambda: self.start_game('local')).pack(pady=8)
        Button(frame, text="Play Online", font=("Arial", 16), width=20, height=2,
               bg='#9b59b6', fg='white', command=lambda: self.start_game('online')).pack(pady=8)

        # Time control
        tc_frame = Frame(frame, bg='#2c3e50')
        tc_frame.pack(pady=15)
        Label(tc_frame, text="Time Control:", font=("Arial", 14), bg='#2c3e50', fg='white').pack()
        Button(tc_frame, text="No Time Limit", font=("Arial", 12), width=15,
               bg='#7f8c8d', fg='white', command=lambda: self.set_time_control(None)).pack(pady=3)
        Button(tc_frame, text="10 Minutes", font=("Arial", 12), width=15,
               bg='#7f8c8d', fg='white', command=lambda: self.set_time_control(600)).pack(pady=3)
        Button(tc_frame, text="5 Minutes", font=("Arial", 12), width=15,
               bg='#7f8c8d', fg='white', command=lambda: self.set_time_control(300)).pack(pady=3)

        Button(frame, text="Exit", font=("Arial", 14), width=15,
               bg='#95a5a6', fg='white', command=self.parent.destroy).pack(pady=15)

    def set_time_control(self, seconds):
        """Set time control."""
        self.time_control = seconds
        if seconds:
            self.white_time = seconds
            self.black_time = seconds
            messagebox.showinfo("Time Control", f"Time set to {seconds // 60} minutes per player")
        else:
            messagebox.showinfo("Time Control", "No time limit set")

    def start_game(self, mode):
        """Start game."""
        self.game_mode = mode
        self.game_active = True

        if mode.startswith('bot'):
            difficulty = mode.split('_')[1]
            self.ai_engine = StockfishEngine(difficulty)
            if not self.ai_engine.process:
                messagebox.showwarning("Stockfish Not Found",
                                       "Stockfish engine not found. Please place stockfish.exe in the same folder.\n\n"
                                       "Download from: https://stockfishchess.org/download/")
                self.back_to_menu()
                return
        elif mode == 'online':
            if not self.connect_online():
                return

        # Clear and create GUI
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.create_gui()

        if self.time_control:
            self.last_time_update = time.time()
            self.update_clocks()

    def connect_online(self):
        """Connect to server."""
        try:
            self.online_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.online_socket.connect(('127.0.0.1', 5001))
            threading.Thread(target=self.receive_online_moves, daemon=True).start()
            messagebox.showinfo("Online", "Connected to game server!")
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect:\n{e}")
            return False

    def receive_online_moves(self):
        """Receive moves from opponent."""
        buffer = b""
        while True:
            try:
                data = self.online_socket.recv(1024)
                if not data:
                    break
                buffer += data

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    msg = line.decode('utf-8')

                    if msg.startswith("CHAT:"):
                        chat_msg = msg[5:]
                        self.parent.after(0, lambda m=chat_msg: self.display_chat_message(m, False))
                    else:
                        parts = msg.split(',')
                        if len(parts) >= 4:
                            from_r, from_c, to_r, to_c = map(int, parts[:4])
                            promotion = parts[4] if len(parts) > 4 and parts[4] else None
                            self.parent.after(0, lambda: self.handle_online_move(from_r, from_c, to_r, to_c, promotion))
            except Exception as e:
                print(f"Online receive error: {e}")
                break

    def handle_online_move(self, from_r, from_c, to_r, to_c, promotion=None):
        """Handle received move."""
        if self.board.make_move(from_r, from_c, to_r, to_c, promotion):
            self.draw_board()
            self.update_move_history()
            self.check_game_over()

    def send_online_move(self, from_r, from_c, to_r, to_c, promotion=None):
        """Send move to opponent."""
        try:
            promo_str = promotion if promotion else ""
            move_str = f"{from_r},{from_c},{to_r},{to_c},{promo_str}\n"
            self.online_socket.sendall(move_str.encode('utf-8'))
        except Exception as e:
            print(f"Online send error: {e}")

    def send_chat_message(self):
        """Send chat message."""
        if not self.online_socket:
            return
        msg = self.chat_entry.get().strip()
        if msg:
            try:
                self.online_socket.sendall(f"CHAT:{msg}\n".encode('utf-8'))
                self.display_chat_message(msg, True)
                self.chat_entry.delete(0, 'end')
            except Exception as e:
                print(f"Chat send error: {e}")

    def display_chat_message(self, msg, is_me):
        """Display chat message."""
        if hasattr(self, 'chat_text'):
            self.chat_text.config(state='normal')
            prefix = "Me: " if is_me else "Opponent: "
            self.chat_text.insert('end', prefix + msg + "\n")
            self.chat_text.see('end')
            self.chat_text.config(state='disabled')

    def create_gui(self):
        """Create game GUI."""
        main_frame = Frame(self.parent, bg='#34495e')
        main_frame.pack(fill='both', expand=True)

        # Left panel
        left_frame = Frame(main_frame, bg='#34495e')
        left_frame.pack(side='left', fill='both', expand=True)

        # Info panel
        info_frame = Frame(left_frame, bg='#34495e', height=60)
        info_frame.pack(fill='x', pady=5)
        info_frame.pack_propagate(False)

        self.turn_label = Label(info_frame, text="White's Turn", font=("Arial", 18, "bold"),
                                bg='#34495e', fg='white')
        self.turn_label.pack(side='left', padx=20)

        # Time display
        if self.time_control:
            time_frame = Frame(info_frame, bg='#34495e')
            time_frame.pack(side='left', padx=20)
            Label(time_frame, text="⏱", font=("Arial", 16), bg='#34495e', fg='white').pack(side='left')
            self.white_time_label = Label(time_frame, text=self.format_time(self.white_time),
                                          font=("Arial", 14, "bold"), bg='#34495e', fg='white')
            self.white_time_label.pack(side='left', padx=5)
            Label(time_frame, text="vs", font=("Arial", 12), bg='#34495e', fg='white').pack(side='left', padx=3)
            self.black_time_label = Label(time_frame, text=self.format_time(self.black_time),
                                          font=("Arial", 14, "bold"), bg='#34495e', fg='white')
            self.black_time_label.pack(side='left', padx=5)

        Button(info_frame, text="New Game", font=("Arial", 12), bg='#3498db', fg='white',
               command=self.reset_game).pack(side='right', padx=5)
        Button(info_frame, text="Main Menu", font=("Arial", 12), bg='#95a5a6', fg='white',
               command=self.back_to_menu).pack(side='right', padx=5)

        # Board canvas
        self.canvas = tk.Canvas(left_frame, width=800, height=800, bg='white')
        self.canvas.pack(pady=5)
        self.canvas.bind('<Button-1>', self.on_square_click)

        # Right panel
        right_frame = Frame(main_frame, bg='#2c3e50', width=280)
        right_frame.pack(side='right', fill='y', padx=5, pady=5)
        right_frame.pack_propagate(False)

        # Move history
        Label(right_frame, text="Move History", font=("Arial", 14, "bold"),
              bg='#2c3e50', fg='white').pack(pady=5)

        history_frame = Frame(right_frame, bg='#2c3e50')
        history_frame.pack(fill='both', expand=True, pady=5)

        scrollbar = Scrollbar(history_frame)
        scrollbar.pack(side='right', fill='y')

        self.history_text = Text(history_frame, width=30, height=20,
                                 font=("Courier", 11), bg='#ecf0f1', fg='#2c3e50',
                                 yscrollcommand=scrollbar.set, state='disabled')
        self.history_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.history_text.yview)

        # Online chat
        if self.game_mode == 'online':
            Label(right_frame, text="Chat", font=("Arial", 14, "bold"),
                  bg='#2c3e50', fg='white').pack(pady=5)

            chat_frame = Frame(right_frame, bg='#2c3e50')
            chat_frame.pack(fill='both', expand=True, pady=5)

            chat_scroll = Scrollbar(chat_frame)
            chat_scroll.pack(side='right', fill='y')

            self.chat_text = Text(chat_frame, width=30, height=10,
                                  font=("Arial", 10), bg='#ecf0f1', fg='#2c3e50',
                                  yscrollcommand=chat_scroll.set, state='disabled')
            self.chat_text.pack(side='left', fill='both', expand=True)
            chat_scroll.config(command=self.chat_text.yview)

            chat_input_frame = Frame(right_frame, bg='#2c3e50')
            chat_input_frame.pack(fill='x', pady=5)

            self.chat_entry = Entry(chat_input_frame, font=("Arial", 11))
            self.chat_entry.pack(side='left', fill='x', expand=True, padx=2)
            self.chat_entry.bind('<Return>', lambda e: self.send_chat_message())

            Button(chat_input_frame, text="Send", font=("Arial", 10),
                   bg='#3498db', fg='white', command=self.send_chat_message).pack(side='right', padx=2)

        self.draw_board()

    def format_time(self, seconds):
        """Format time as MM:SS."""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def update_clocks(self):
        """Update game clocks."""
        if not self.game_active or not self.time_control:
            return

        current_time = time.time()
        if self.last_time_update:
            elapsed = current_time - self.last_time_update

            if self.board.current_turn == 'white':
                self.white_time = max(0, self.white_time - elapsed)
            else:
                self.black_time = max(0, self.black_time - elapsed)

            if self.white_time <= 0:
                self.game_active = False
                messagebox.showinfo("Time Out", "Black wins on time!")
                return
            elif self.black_time <= 0:
                self.game_active = False
                messagebox.showinfo("Time Out", "White wins on time!")
                return

            if hasattr(self, 'white_time_label'):
                self.white_time_label.config(text=self.format_time(int(self.white_time)))
                self.black_time_label.config(text=self.format_time(int(self.black_time)))

        self.last_time_update = current_time
        self.parent.after(100, self.update_clocks)

    def draw_board(self):
        """Draw chess board."""
        self.canvas.delete('all')
        square_size = 100

        for row in range(8):
            for col in range(8):
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size

                color = '#f0d9b5' if (row + col) % 2 == 0 else '#b58863'

                if self.selected_square == (row, col):
                    color = '#baca44'

                if (row, col) in self.valid_moves_highlight:
                    color = '#a0ca44'

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

                # Green dots for valid moves
                if (row, col) in self.valid_moves_highlight:
                    cx, cy = x1 + 50, y1 + 50
                    piece_at_dest = self.board.get_piece(row, col)
                    if piece_at_dest == '.':
                        self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill='#20a020', outline='')
                    else:
                        self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, outline='#20a020', width=4)

                # Draw piece
                piece = self.board.get_piece(row, col)
                if piece != '.':
                    symbol = PIECES.get(piece, '')
                    self.canvas.create_text(x1 + 50, y1 + 50, text=symbol,
                                            font=("Arial", 60), fill='black')

        # Coordinates
        for i in range(8):
            self.canvas.create_text(i * 100 + 50, 810, text=chr(97 + i),
                                    font=("Arial", 14), fill='black')
            self.canvas.create_text(10, i * 100 + 50, text=str(8 - i),
                                    font=("Arial", 14), fill='black')

    def on_square_click(self, event):
        """Handle square click."""
        if not self.game_active:
            return

        if self.game_mode == 'online' and self.board.current_turn == 'black':
            return

        col = event.x // 100
        row = event.y // 100

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        if self.selected_square is None:
            piece = self.board.get_piece(row, col)
            if piece != '.':
                if self.board.current_turn == 'white' and self.board.is_white_piece(piece):
                    self.selected_square = (row, col)
                    self.valid_moves_highlight = self.board.get_valid_moves_for_piece(row, col)
                elif self.board.current_turn == 'black' and self.board.is_black_piece(piece):
                    self.selected_square = (row, col)
                    self.valid_moves_highlight = self.board.get_valid_moves_for_piece(row, col)
        else:
            from_row, from_col = self.selected_square
            piece = self.board.get_piece(from_row, from_col)

            # Check promotion
            promotion_piece = None
            if piece.lower() == 'p':
                if (self.board.is_white_piece(piece) and row == 0) or \
                        (self.board.is_black_piece(piece) and row == 7):
                    promotion_piece = self.ask_promotion(self.board.is_white_piece(piece))

            if self.board.make_move(from_row, from_col, row, col, promotion_piece):
                if self.game_mode == 'online':
                    self.send_online_move(from_row, from_col, row, col, promotion_piece)

                self.selected_square = None
                self.valid_moves_highlight = []
                self.draw_board()
                self.update_turn_label()
                self.update_move_history()

                if not self.check_game_over():
                    if self.game_mode and self.game_mode.startswith('bot'):
                        self.parent.after(500, self.make_ai_move)
            else:
                piece_clicked = self.board.get_piece(row, col)
                if piece_clicked != '.':
                    if (self.board.current_turn == 'white' and self.board.is_white_piece(piece_clicked)) or \
                            (self.board.current_turn == 'black' and self.board.is_black_piece(piece_clicked)):
                        self.selected_square = (row, col)
                        self.valid_moves_highlight = self.board.get_valid_moves_for_piece(row, col)
                    else:
                        self.selected_square = None
                        self.valid_moves_highlight = []
                else:
                    self.selected_square = None
                    self.valid_moves_highlight = []

        self.draw_board()

    def ask_promotion(self, is_white):
        """Ask for promotion piece."""
        dialog = Toplevel(self.parent)
        dialog.title("Pawn Promotion")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        result = [None]

        Label(dialog, text="Choose promotion piece:", font=("Arial", 14, "bold")).pack(pady=15)

        button_frame = Frame(dialog)
        button_frame.pack(pady=10)

        pieces = [('Queen', 'Q'), ('Rook', 'R'), ('Bishop', 'B'), ('Knight', 'N')]

        for name, letter in pieces:
            piece_char = letter if is_white else letter.lower()
            symbol = PIECES[piece_char]
            btn = Button(button_frame, text=f"{symbol}\n{name}", font=("Arial", 16),
                         width=5, height=3,
                         command=lambda p=piece_char: [result.__setitem__(0, p), dialog.destroy()])
            btn.pack(side='left', padx=5)

        dialog.wait_window()
        return result[0] if result[0] else ('Q' if is_white else 'q')

    def make_ai_move(self):
        """Make AI move using Stockfish."""
        if not self.game_active:
            return

        try:
            # Get current position in FEN
            fen = self.board.get_fen()

            # Get best move from Stockfish
            move_time = 500 if self.ai_engine.skill <= 5 else 1000 if self.ai_engine.skill <= 12 else 2000
            best_move_uci = self.ai_engine.get_best_move(fen, move_time)

            if not best_move_uci or len(best_move_uci) < 4:
                print("[AI] No valid move returned")
                return

            # Parse UCI move (e.g., "e2e4" or "e7e8q")
            from_col = ord(best_move_uci[0]) - ord('a')
            from_row = 8 - int(best_move_uci[1])
            to_col = ord(best_move_uci[2]) - ord('a')
            to_row = 8 - int(best_move_uci[3])

            # Check promotion
            promotion_piece = None
            if len(best_move_uci) == 5:
                promo_map = {'q': 'q', 'r': 'r', 'b': 'b', 'n': 'n'}
                promotion_piece = promo_map.get(best_move_uci[4], 'q')
                if self.board.current_turn == 'white':
                    promotion_piece = promotion_piece.upper()

            # Make move
            if self.board.make_move(from_row, from_col, to_row, to_col, promotion_piece):
                self.draw_board()
                self.update_turn_label()
                self.update_move_history()
                self.check_game_over()

        except Exception as e:
            print(f"[AI] Error making move: {e}")
            import traceback
            traceback.print_exc()

    def update_turn_label(self):
        """Update turn label."""
        turn = "White's Turn" if self.board.current_turn == 'white' else "Black's Turn"

        if self.board.is_in_check():
            turn += " - CHECK!"

        self.turn_label.config(text=turn)

    def update_move_history(self):
        """Update move history."""
        if not hasattr(self, 'history_text'):
            return

        self.history_text.config(state='normal')
        self.history_text.delete('1.0', 'end')

        for i, move in enumerate(self.board.move_history):
            if i % 2 == 0:
                move_num = (i // 2) + 1
                self.history_text.insert('end', f"{move_num}. ")

            self.history_text.insert('end', f"{move['notation']} ")

            if i % 2 == 1:
                self.history_text.insert('end', "\n")

        self.history_text.see('end')
        self.history_text.config(state='disabled')

    def check_game_over(self):
        """Check if game is over."""
        if self.board.is_checkmate():
            self.game_active = False
            winner = "Black" if self.board.current_turn == 'white' else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
            return True
        elif self.board.is_stalemate():
            self.game_active = False
            messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
            return True
        elif self.board.halfmove_clock >= 100:
            self.game_active = False
            messagebox.showinfo("Game Over", "Draw by 50-move rule!")
            return True
        elif self.board.is_in_check():
            self.turn_label.config(text=f"{self.board.current_turn.capitalize()} is in CHECK!")

        return False

    def reset_game(self):
        """Reset game."""
        if messagebox.askyesno("New Game", "Start a new game?"):
            self.board.reset_board()
            self.selected_square = None
            self.valid_moves_highlight = []
            self.game_active = True

            if self.time_control:
                self.white_time = self.time_control
                self.black_time = self.time_control
                self.last_time_update = time.time()

            self.draw_board()
            self.update_turn_label()
            self.update_move_history()

    def back_to_menu(self):
        """Return to main menu."""
        if messagebox.askyesno("Exit Game", "Return to main menu?"):
            self.game_active = False

            if self.ai_engine:
                self.ai_engine.close()

            if self.online_socket:
                try:
                    self.online_socket.close()
                except:
                    pass

            for widget in self.parent.winfo_children():
                widget.destroy()

            self.show_mode_selection()


if __name__ == "__main__":
    root = tk.Tk()
    ChessGame(root)
    root.mainloop()