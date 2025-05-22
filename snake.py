import tkinter as tk
import random
import os

try:
    from pygame import mixer
    mixer.init()
    SOUND_ENABLED = True
    def play_sound(path):
        if SOUND_ENABLED and os.path.exists(path):
            try:
                mixer.Sound(path).play()
            except Exception:
                pass
except Exception:
    SOUND_ENABLED = False
    def play_sound(path):
        pass

class SnakeGame:
    """Snake Game supporting classic and effects mode with sound, pause, and restart."""

    COLORS = {
        'background': '#202020',
        'snake_head': '#9eff3b',
        'snake_body': '#60b000',
        'food_score': '#ffcc33',
        'food_slow': '#00d6e6',
        'food_fast': '#de5ceb',
        'food_shrink': '#ffe100',
        'score_text': '#f7fafc',
        'game_over': '#fafafa',
        'pause_overlay': '#444444'
    }
    FOOD_EFFECTS = [
        ('score', '🍎'),
        ('slow', '🐢'),
        ('fast', '🐇'),
        ('shrink', '✂️')
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Snake Game")

        self.width = 600
        self.height = 400
        self.cell_size = 20

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg=self.COLORS['background'], highlightthickness=0)
        self.canvas.pack()

        self.info_frame = tk.Frame(root)
        self.info_frame.pack(fill=tk.X, pady=(0,4))
        self.score_label = tk.Label(self.info_frame, text="Score: 0", fg=self.COLORS['score_text'], bg='#242424', font=("Arial", 12))
        self.score_label.pack(side=tk.LEFT, padx=(12,0))
        self.pause_label = tk.Label(self.info_frame, text="", fg="#ffca00", bg='#242424', font=("Arial", 12))
        self.pause_label.pack(side=tk.RIGHT, padx=12)

        self.root.bind('<KeyPress>', self.handle_keys)

        self.running = False
        self.paused = False
        self.speed = 100
        self.score = 0
        self.best_score = 0
        self.direction = 'Right'
        self.snake = []
        self.foods = []
        self.food_effects = []
        self.pulse = 0
        self.pulse_dir = 5
        self.difficulty_frame = None
        self.effects_mode = False

        self.show_main_menu()

    def show_main_menu(self):
        """Show the main menu with Classic and Effects mode."""
        self.canvas.delete("all")
        if self.difficulty_frame:
            self.difficulty_frame.destroy()
        self.difficulty_frame = tk.Frame(self.root, bg="#181818")
        self.difficulty_frame.pack(pady=30)
        tk.Label(self.difficulty_frame, text="Snake Game - Choose Mode", font=('Arial', 16, 'bold'), fg="#eee", bg="#181818").pack(side=tk.TOP, padx=8, pady=(0,12))
        tk.Button(self.difficulty_frame, text="Classic Mode", font=('Arial', 13), width=18,
                  command=self.show_classic_menu).pack(side=tk.TOP, pady=6)
        tk.Button(self.difficulty_frame, text="Effects Mode", font=('Arial', 13), width=18,
                  command=self.show_effects_menu).pack(side=tk.TOP, pady=6)
        if self.best_score > 0:
            tk.Label(self.difficulty_frame, text=f"Best Score: {self.best_score}", fg="#fafafa", bg="#181818", font=("Arial", 11, "italic")).pack(side=tk.TOP, pady=(16,3))

    def show_classic_menu(self):
        """Show the classic (no effects) difficulty menu."""
        self.effects_mode = False
        self.show_difficulty_menu("Classic Mode: Just Score", [("Easy 🟢", 150), ("Medium 🟠", 100), ("Hard 🔴", 50)])

    def show_effects_menu(self):
        """Show the effects mode difficulty menu."""
        self.effects_mode = True
        self.show_difficulty_menu("Effects Mode: Powerups!", [("Easy 🟢", 150), ("Medium 🟠", 100), ("Hard 🔴", 50)])

    def show_difficulty_menu(self, title, choices):
        """Show the difficulty selection menu with the given choices."""
        self.canvas.delete("all")
        if self.difficulty_frame:
            self.difficulty_frame.destroy()
        self.difficulty_frame = tk.Frame(self.root, bg="#181818")
        self.difficulty_frame.pack(pady=30)
        tk.Label(self.difficulty_frame, text=title, font=('Arial', 14, 'bold'), fg="#eee", bg="#181818").pack(side=tk.LEFT, padx=8)
        for text, spd in choices:
            tk.Button(self.difficulty_frame, text=text, font=('Arial', 11), width=9,
                      command=lambda s=spd: self.start_game(s)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.difficulty_frame, text="Back", font=('Arial', 11), width=7, command=self.show_main_menu).pack(side=tk.LEFT, padx=(18,5))

    def start_game(self, speed):
        """Start a new snake game with the given speed (difficulty)."""
        self.speed = speed
        if self.difficulty_frame:
            self.difficulty_frame.destroy()
            self.difficulty_frame = None
        self.running = True
        self.paused = False
        self.direction = 'Right'
        self.snake = [(100, 100), (80, 100), (60, 100)]
        if self.effects_mode:
            self.foods = [self.place_food() for _ in range(4)]
            self.food_effects = [random.choice([e[0] for e in self.FOOD_EFFECTS]) for _ in self.foods]
        else:
            self.foods = [self.place_food()]
            self.food_effects = ['score']
        self.score = 0
        self.update_score()
        self.pause_label.config(text="")
        self.canvas.delete("all")
        self.update_game()

    def restart_game(self):
        """Restart the game and show the main menu."""
        self.running = False
        self.paused = False
        self.snake.clear()
        self.canvas.delete("all")
        self.show_main_menu()

    def handle_keys(self, event):
        """Handle key events for control."""
        k = event.keysym.lower()
        if k in ['r']:
            if not self.running:
                self.restart_game()
        elif k == 'space':
            if self.running:
                self.toggle_pause()
        else:
            self.change_direction(event)

    def toggle_pause(self):
        """Pause or unpause the game."""
        self.paused = not self.paused
        if self.paused:
            self.pause_label.config(text="Paused (Space to resume)")
        else:
            self.pause_label.config(text="")

    def place_food(self):
        """Place a food item not overlapping with snake or other food."""
        attempts = 0
        while True:
            x = random.randint(0, (self.width - self.cell_size) // self.cell_size) * self.cell_size
            y = random.randint(0, (self.height - self.cell_size) // self.cell_size) * self.cell_size
            if (x, y) not in self.snake and (x, y) not in self.foods:
                return (x, y)
            attempts += 1
            if attempts > 100:
                break
        return (x, y)

    def change_direction(self, event):
        """Change the direction unless it's the opposite."""
        key_map = {
            'Up': 'Up', 'Down': 'Down', 'Left': 'Left', 'Right': 'Right',
            'w': 'Up', 's': 'Down', 'a': 'Left', 'd': 'Right',
            'W': 'Up', 'S': 'Down', 'A': 'Left', 'D': 'Right'
        }
        if event.keysym in key_map:
            new_direction = key_map[event.keysym]
            opposites = {'Up': 'Down', 'Down': 'Up', 'Left': 'Right', 'Right': 'Left'}
            if new_direction != opposites.get(self.direction):
                self.direction = new_direction

    def move_snake(self):
        """Move the snake forward and handle collision and food effects."""
        head_x, head_y = self.snake[0]
        move = {'Up': (0, -self.cell_size), 'Down': (0, self.cell_size),
                'Left': (-self.cell_size, 0), 'Right': (self.cell_size, 0)}
        dx, dy = move[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Wall or self collision
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.running = False
            play_sound("game_over.wav")
            self.best_score = max(self.best_score, self.score)
            return

        self.snake.insert(0, new_head)
        ate_food = False

        for i, food in enumerate(self.foods):
            if new_head == food:
                effect = self.food_effects[i]
                if effect == 'score':
                    self.score += 5
                elif effect == 'slow':
                    self.speed = min(300, self.speed + 30)
                elif effect == 'fast':
                    self.speed = max(30, self.speed - 30)
                elif effect == 'shrink' and len(self.snake) > 3:
                    self.snake.pop()
                self.foods[i] = self.place_food()
                self.food_effects[i] = random.choice([e[0] for e in self.FOOD_EFFECTS]) if self.effects_mode else 'score'
                play_sound("eat.wav")
                self.update_score()
                ate_food = True
                break

        if not ate_food:
            self.snake.pop()

    def draw_elements(self):
        """Draw the snake, foods, and score."""
        self.canvas.delete("snake")
        self.canvas.delete("food")
        # Draw snake body
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                color = self.COLORS['snake_head']
            else:
                shade = 220 - min(i * 12, 180)
                color = f'#{shade:02x}e0{shade:02x}'
            self.canvas.create_rectangle(x, y, x+self.cell_size, y+self.cell_size,
                                        fill=color, tags="snake", outline="#141414" if i==0 else "")

        self.pulse += self.pulse_dir
        if self.pulse > 60 or self.pulse < 0:
            self.pulse_dir *= -1
            self.pulse += self.pulse_dir

        def clamp(val):
            return max(0, min(255, val))

        # Draw foods
        for (fx, fy), effect in zip(self.foods, self.food_effects):
            if effect == 'score':
                v = clamp(200 + self.pulse)
                color = f'#ff{v:02x}{100:02x}'
                emoji = '🍎'
            elif effect == 'slow':
                color = self.COLORS['food_slow']
                emoji = '🐢'
            elif effect == 'fast':
                color = self.COLORS['food_fast']
                emoji = '🐇'
            elif effect == 'shrink':
                color = self.COLORS['food_shrink']
                emoji = '✂️'
            self.canvas.create_oval(fx, fy, fx+self.cell_size, fy+self.cell_size,
                                   fill=color, outline="", tags="food")
            self.canvas.create_text(fx+self.cell_size//2, fy+self.cell_size//2, text=emoji, font=("Arial", 14), tags="food")

    def update_score(self):
        """Update score label."""
        self.score_label.config(text=f"Score: {self.score}")

    def update_game(self):
        """Main game loop."""
        if self.running:
            if not self.paused:
                self.move_snake()
                self.draw_elements()
            self.root.after(self.speed, self.update_game)
        else:
            self.draw_elements()
            self.canvas.create_text(self.width//2, self.height//2 - 30,
                text=f"Game Over!\nScore: {self.score}", fill=self.COLORS['game_over'], font=("Arial", 25, "bold"))
            self.canvas.create_text(self.width//2, self.height//2 + 15,
                text="Press R to Restart", fill="#ffcc33", font=("Arial", 15, "bold"))
            if self.best_score > 0:
                self.canvas.create_text(self.width//2, self.height//2 + 46,
                    text=f"Best: {self.best_score}", fill="#888", font=("Arial", 11, "italic"))

if __name__ == '__main__':
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()