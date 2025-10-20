import pygame
import random
import sys
import os
import json
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Полноэкранный режим
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Runic Row")

# Загрузка музыки
def load_music():
    try:
        if os.path.exists("music.mp3"):
            mixer.music.load("music.mp3")
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)
    except:
        pass

# Константы
GRID_SIZE = 8
CELL_SIZE = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 12
MARGIN_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
MARGIN_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2
SWIPE_THRESHOLD = 20

# Цвета
DARK_BLUE = (13, 17, 23)
DARK_PURPLE = (30, 25, 45)
GOLD = (212, 175, 55)
SILVER = (192, 192, 192)
EMERALD = (80, 200, 120)
RUBY = (220, 60, 80)
AMETHYST = (153, 102, 204)
AMBER = (255, 191, 0)

RUNIC_COLORS = [
    (231, 76, 60), (52, 152, 219), (46, 204, 113),
    (155, 89, 182), (241, 196, 15), (230, 126, 34)
]

# Шрифты
try:
    title_font = pygame.font.Font(None, 72)
    header_font = pygame.font.Font(None, 48)
    normal_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
except:
    title_font = pygame.font.SysFont('arial', 72, bold=True)
    header_font = pygame.font.SysFont('arial', 48, bold=True)
    normal_font = pygame.font.SysFont('arial', 36)
    small_font = pygame.font.SysFont('arial', 28)

SCORES_FILE = "runic_row_scores.json"

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=GOLD):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, GOLD, self.rect, 3, border_radius=15)
        
        text_surf = normal_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Rune:
    def __init__(self, row, col, color_idx):
        self.row = row
        self.col = col
        self.color_idx = color_idx
        self.color = RUNIC_COLORS[color_idx]
        self.x = MARGIN_X + col * CELL_SIZE
        self.y = MARGIN_Y + row * CELL_SIZE
        self.target_x = self.x
        self.target_y = self.y
        self.selected = False
        self.matched = False
        self.scale = 1.0
        self.pulse_direction = 0.02
        
    def draw(self):
        if self.selected:
            self.scale += self.pulse_direction
            if self.scale >= 1.2 or self.scale <= 0.8:
                self.pulse_direction *= -1
        
        current_size = int(CELL_SIZE * self.scale)
        offset = (CELL_SIZE - current_size) // 2
        
        rect = pygame.Rect(self.x + offset, self.y + offset, current_size, current_size)
        
        if self.matched:
            glow_rect = pygame.Rect(self.x - 5, self.y - 5, CELL_SIZE + 10, CELL_SIZE + 10)
            pygame.draw.rect(screen, GOLD, glow_rect, border_radius=12)
        
        pygame.draw.rect(screen, self.color, rect, border_radius=10)
        
        inner_rect = pygame.Rect(self.x + offset + 8, self.y + offset + 8, 
                               current_size - 16, current_size - 16)
        pygame.draw.rect(screen, DARK_PURPLE, inner_rect, border_radius=6)
        
        center_x, center_y = self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2
        symbol_size = current_size // 3
        
        if self.color_idx == 0:
            pygame.draw.line(screen, self.color, (center_x - symbol_size, center_y),
                           (center_x + symbol_size, center_y), 3)
            pygame.draw.line(screen, self.color, (center_x, center_y - symbol_size),
                           (center_x, center_y + symbol_size), 3)
        elif self.color_idx == 1:
            pygame.draw.circle(screen, self.color, (center_x, center_y), symbol_size, 3)
        elif self.color_idx == 2:
            points = [(center_x, center_y - symbol_size), (center_x - symbol_size, center_y + symbol_size),
                     (center_x + symbol_size, center_y + symbol_size)]
            pygame.draw.polygon(screen, self.color, points, 3)
        elif self.color_idx == 3:
            pygame.draw.rect(screen, self.color, (center_x - symbol_size, center_y - symbol_size,
                            symbol_size * 2, symbol_size * 2), 3)
        elif self.color_idx == 4:
            points = []
            for i in range(5):
                angle = i * 4 * 3.14159 / 5 - 3.14159 / 2
                x = center_x + symbol_size * 0.8 * math.cos(angle)
                y = center_y + symbol_size * 0.8 * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.color, points, 3)
        else:
            points = [(center_x, center_y - symbol_size), (center_x + symbol_size, center_y),
                     (center_x, center_y + symbol_size), (center_x - symbol_size, center_y)]
            pygame.draw.polygon(screen, self.color, points, 3)
        
        if self.selected:
            pygame.draw.rect(screen, GOLD, (self.x - 2, self.y - 2, CELL_SIZE + 4, CELL_SIZE + 4), 
                           4, border_radius=12)
    
    def update(self):
        if abs(self.x - self.target_x) > 0.5:
            self.x += (self.target_x - self.x) * 0.3
        else:
            self.x = self.target_x
            
        if abs(self.y - self.target_y) > 0.5:
            self.y += (self.target_y - self.y) * 0.3
        else:
            self.y = self.target_y

class SwipeHandler:
    def __init__(self):
        self.swipe_start = None
        self.swipe_end = None
        self.is_swiping = False
        self.selected_rune = None
        
    def handle_event(self, event, grid):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.start_swipe(event.pos, grid)
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_swiping:
            return self.end_swipe(event.pos, grid)
            
        elif event.type == pygame.MOUSEMOTION and self.is_swiping:
            self.update_swipe(event.pos)
            
        return False
    
    def start_swipe(self, pos, grid):
        col = (pos[0] - MARGIN_X) // CELL_SIZE
        row = (pos[1] - MARGIN_Y) // CELL_SIZE
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.swipe_start = pos
            self.selected_rune = grid[row][col]
            self.selected_rune.selected = True
            self.is_swiping = True
    
    def update_swipe(self, pos):
        self.swipe_end = pos
    
    def end_swipe(self, pos, grid):
        self.swipe_end = pos
        self.is_swiping = False
        
        if self.selected_rune and self.swipe_start and self.swipe_end:
            dx = self.swipe_end[0] - self.swipe_start[0]
            dy = self.swipe_end[1] - self.swipe_start[1]
            
            target_row = self.selected_rune.row
            target_col = self.selected_rune.col
            
            if abs(dx) > abs(dy) and abs(dx) > SWIPE_THRESHOLD:
                if dx > 0 and self.selected_rune.col < GRID_SIZE - 1:
                    target_col += 1
                elif dx < 0 and self.selected_rune.col > 0:
                    target_col -= 1
            elif abs(dy) > abs(dx) and abs(dy) > SWIPE_THRESHOLD:
                if dy > 0 and self.selected_rune.row < GRID_SIZE - 1:
                    target_row += 1
                elif dy < 0 and self.selected_rune.row > 0:
                    target_row -= 1
            
            if (target_row != self.selected_rune.row or target_col != self.selected_rune.col):
                target_rune = grid[target_row][target_col]
                valid_move = self.swap_runes(self.selected_rune, target_rune, grid)
                
                self.selected_rune.selected = False
                self.selected_rune = None
                return valid_move
            
            self.selected_rune.selected = False
            self.selected_rune = None
            
        return False
    
    def swap_runes(self, rune1, rune2, grid):
        grid[rune1.row][rune1.col], grid[rune2.row][rune2.col] = rune2, rune1
        
        rune1.row, rune2.row = rune2.row, rune1.row
        rune1.col, rune2.col = rune2.col, rune1.col
        
        rune1.target_x = MARGIN_X + rune1.col * CELL_SIZE
        rune1.target_y = MARGIN_Y + rune1.row * CELL_SIZE
        rune2.target_x = MARGIN_X + rune2.col * CELL_SIZE
        rune2.target_y = MARGIN_Y + rune2.row * CELL_SIZE
        
        if not self.check_matches(grid):
            grid[rune1.row][rune1.col], grid[rune2.row][rune2.col] = rune2, rune1
            rune1.row, rune2.row = rune2.row, rune1.row
            rune1.col, rune2.col = rune2.col, rune1.col
            
            rune1.target_x = MARGIN_X + rune1.col * CELL_SIZE
            rune1.target_y = MARGIN_Y + rune1.row * CELL_SIZE
            rune2.target_x = MARGIN_X + rune2.col * CELL_SIZE
            rune2.target_y = MARGIN_Y + rune2.row * CELL_SIZE
            return False
        else:
            return True
    
    def check_matches(self, grid):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (grid[row][col].color_idx == grid[row][col+1].color_idx == 
                    grid[row][col+2].color_idx):
                    return True
        
        for row in range(GRID_SIZE - 2):
            for col in range(GRID_SIZE):
                if (grid[row][col].color_idx == grid[row+1][col].color_idx == 
                    grid[row+2][col].color_idx):
                    return True
        return False

class Game:
    def __init__(self):
        self.grid = []
        self.swipe_handler = SwipeHandler()
        self.score = 0
        self.moves = 25
        self.high_score = self.load_high_score()
        self.combo = 0
        self.initialize_grid()
        
    def load_high_score(self):
        try:
            if os.path.exists(SCORES_FILE):
                with open(SCORES_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            data = {'high_score': max(self.high_score, self.score)}
            with open(SCORES_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def initialize_grid(self):
        self.grid = []
        for row in range(GRID_SIZE):
            self.grid.append([])
            for col in range(GRID_SIZE):
                color_idx = random.randint(0, len(RUNIC_COLORS) - 1)
                self.grid[row].append(Rune(row, col, color_idx))
        
        while self.find_matches():
            self.remove_matches()
            self.fill_empty_cells()
    
    def draw(self):
        screen.fill(DARK_BLUE)
        
        board_rect = pygame.Rect(MARGIN_X - 20, MARGIN_Y - 20, 
                               GRID_SIZE * CELL_SIZE + 40, 
                               GRID_SIZE * CELL_SIZE + 40)
        pygame.draw.rect(screen, (20, 25, 35), board_rect, border_radius=20)
        pygame.draw.rect(screen, GOLD, board_rect, 4, border_radius=20)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].draw()
        
        self.draw_ui()
        
        if self.swipe_handler.is_swiping and self.swipe_handler.swipe_start and self.swipe_handler.swipe_end:
            pygame.draw.line(screen, GOLD, self.swipe_handler.swipe_start, 
                           self.swipe_handler.swipe_end, 3)
    
    def draw_ui(self):
        title = title_font.render("RUNIC ROW", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        score_text = header_font.render(f"Счет: {self.score}", True, EMERALD)
        moves_text = header_font.render(f"Ходы: {self.moves}", True, AMBER)
        high_score_text = header_font.render(f"Рекорд: {self.high_score}", True, RUBY)
        
        screen.blit(score_text, (50, 120))
        screen.blit(moves_text, (SCREEN_WIDTH - 200, 120))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 120))
        
        if self.combo > 1:
            combo_text = normal_font.render(f"КОМБО: x{self.combo}!", True, AMETHYST)
            screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 170))
        
        instruction = small_font.render("Свайпайте руны для их перемещения", True, SILVER)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 80))
        
        exit_text = small_font.render("ESC - Выход", True, SILVER)
        screen.blit(exit_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50))
    
    def handle_event(self, event):
        if self.swipe_handler.handle_event(event, self.grid):
            self.moves -= 1
            return True
        return False
    
    def find_matches(self):
        found_match = False
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].matched = False
        
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE - 2:
                if (self.grid[row][col].color_idx == self.grid[row][col+1].color_idx == 
                    self.grid[row][col+2].color_idx):
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.grid[row][col].color_idx == self.grid[row][col+match_length].color_idx:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row][col+i].matched = True
                    found_match = True
                    col += match_length
                else:
                    col += 1
        
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE - 2:
                if (self.grid[row][col].color_idx == self.grid[row+1][col].color_idx == 
                    self.grid[row+2][col].color_idx):
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.grid[row][col].color_idx == self.grid[row+match_length][col].color_idx:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row+i][col].matched = True
                    found_match = True
                    row += match_length
                else:
                    row += 1
        
        return found_match
    
    def remove_matches(self):
        matches_found = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].matched:
                    self.grid[row][col] = None
                    matches_found += 1
        
        points = matches_found * 10 * (1 + self.combo // 3)
        self.score += points
        
        if matches_found > 3:
            self.combo += 1
        else:
            self.combo = 0
    
    def fill_empty_cells(self):
        for col in range(GRID_SIZE):
            runes_in_column = []
            for row in range(GRID_SIZE):
                if self.grid[row][col] is not None:
                    runes_in_column.append(self.grid[row][col])  # ИСПРАВЛЕНО: append вместо apend
            
            for row in range(GRID_SIZE):
                if row < len(runes_in_column):
                    rune = runes_in_column[row]
                    rune.row = row
                    rune.target_y = MARGIN_Y + row * CELL_SIZE
                    self.grid[row][col] = rune
                else:
                    color_idx = random.randint(0, len(RUNIC_COLORS) - 1)
                    self.grid[row][col] = Rune(row, col, color_idx)
                    self.grid[row][col].y = MARGIN_Y - (GRID_SIZE - row) * CELL_SIZE
                    self.grid[row][col].target_y = MARGIN_Y + row * CELL_SIZE
    
    def update(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].update()
        
        if self.find_matches():
            self.remove_matches()
            self.fill_empty_cells()
    
    def is_game_over(self):
        return self.moves <= 0

class LoadingScreen:
    def __init__(self):
        self.progress = 0
        self.loading_text = "Пробуждение древних рун"
        self.dots = 0
        self.last_update = pygame.time.get_ticks()
        
    def draw(self):
        screen.fill(DARK_BLUE)
        
        title = title_font.render("RUNIC ROW", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        
        bar_width = SCREEN_WIDTH // 2
        bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_width // 2, SCREEN_HEIGHT // 2, bar_width, 20)
        pygame.draw.rect(screen, DARK_PURPLE, bar_rect)
        fill_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_width // 2, SCREEN_HEIGHT // 2, 
                              bar_width * self.progress // 100, 20)
        pygame.draw.rect(screen, EMERALD, fill_rect)
        pygame.draw.rect(screen, GOLD, bar_rect, 2)
        
        dots = "." * (self.dots % 4)
        loading = normal_font.render(f"{self.loading_text}{dots}", True, SILVER)
        screen.blit(loading, (SCREEN_WIDTH // 2 - loading.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        
        percent = normal_font.render(f"{self.progress}%", True, GOLD)
        screen.blit(percent, (SCREEN_WIDTH // 2 - percent.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 500:
            self.dots += 1
            self.last_update = current_time
        
        if self.progress < 100:
            self.progress += 2
            return True
        return False

class MainMenu:
    def __init__(self):
        button_width = 300
        button_height = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        self.buttons = [
            Button(center_x, SCREEN_HEIGHT // 2 - 40, button_width, button_height, 
                  "ИГРАТЬ", DARK_PURPLE, AMETHYST),
            Button(center_x, SCREEN_HEIGHT // 2 + 60, button_width, button_height,
                  "ВЫХОД", DARK_PURPLE, RUBY)
        ]
        
    def draw(self):
        screen.fill(DARK_BLUE)
        
        title = title_font.render("RUNIC ROW", True, GOLD)
        subtitle = header_font.render("Древняя магия в твоих руках", True, SILVER)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 4 + 80))
        
        for button in self.buttons:
            button.draw(screen)
        
        game = Game()
        high_score_text = normal_font.render(f"Максимальный рекорд: {game.high_score}", True, EMERALD)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT - 100))
       2 - high_score_text.get_width() // 2, SCREEN_HEIGHT - 100))
        
        music_text = small_font.render("M - Вкл/Выкл музыку", True, SILVER)
        screen.blit(music_text, (50, SCREEN_HEIGHT - 50))
    
    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(pos)
            
            if button.is_clicked(pos, event):
                if button.text == "ИГРАТЬ":
                    return "play"
                elif button.text == "ВЫХОД":
                    return "exit"
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            if mixer.music.get_busy():
                mixer.music.pause()
            else:
                mixer.music.unpause()
                
        return "menu"

def show_game_over(score, high_score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over = title_font.render("ИГРА ОКОНЧЕНА", True, RUBY)
    score_text = header_font.render(f"Ваш счет: {score}", True, EMERALD)
    high_score_text = header_font.render(f"Рекорд: {high_score}", True, GOLD)
    continue_text = normal_font.render("Нажмите любую клавишу для продолжения", True, SILVER)
    
    screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 150))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

def main():
    load_music()
    
    clock = pygame.time.Clock()
    current_screen = "loading"
    loading_screen = LoadingScreen()
    main_menu = MainMenu()
    game = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen == "game":
                        current_screen = "menu"
                    else:
                        running = False
                elif event.key == pygame.K_m:
                    if mixer.music.get_busy():
                        mixer.music.pause()
                    else:
                        mixer.music.unpause()
            
            if current_screen == "menu":
                result = main_menu.handle_event(event)
                if result == "play":
                    current_screen = "game"
                    game = Game()
                elif result == "exit":
                    running = False
            
            elif current_screen == "game":
                if game.handle_event(event):
                    pass
        
        if current_screen == "loading":
            if loading_screen.update():
                loading_screen.draw()
            else:
                current_screen = "menu"
        
        elif current_screen == "menu":
            main_menu.draw()
        
        elif current_screen == "game":
            game.update()
            game.draw()
            
            if game.is_game_over():
                game.save_high_score()
                show_game_over(game.score, game.high_score)
                current_screen = "menu"
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import math  # Добавлено для math.cos и math.sin
    main()
