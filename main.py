import pygame
import random
import math


# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Jets")

# Game icon
icon = pygame.image.load("gameicon.png")
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (15, 161, 246)

# Fonts
font_large = pygame.font.SysFont('Arial', 50)
font_medium = pygame.font.SysFont('Arial', 30)
font_small = pygame.font.SysFont('Arial', 20)

# Pre-load images with error handling
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        # Create a placeholder surface
        surf = pygame.Surface(size or (100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 0), (0, 0, size[0] if size else 100, size[1] if size else 100))
        return surf

# Load all game images
try:
    menu_img = load_image('menu.png', (WIDTH, HEIGHT))
    bg_img = load_image('bg.png', (WIDTH, HEIGHT))
    end_img = load_image('end.png', (WIDTH, HEIGHT))
    player_img = load_image('player.png', (125, 115))
    bullet_img = load_image('bullet.png', (25, 50))
    enemy_imgs = {
        1: load_image('enemy1.png', (110, 90)),
        2: load_image('enemy2.png', (110, 90)),
        3: load_image('enemy3.png', (145, 95))
    }
except Exception as e:
    print(f"Error loading game assets: {e}")
    pygame.quit()
    exit()

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)  # White border
        
        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def main_menu():
    screen.blit(menu_img, (0, 0))
    
    start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 25, 200, 50, "START", BLUE, (0, 100, 200))
    quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "QUIT", BLUE, (0, 100, 200))
    
    menu_running = True
    while menu_running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            
            if start_button.is_clicked(mouse_pos, event):
                return True  # Start game
            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                return False
        
        # Update button hover states
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        start_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
    
    return False

# Player class
class Player:
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.bullets = []
        self.shoot_delay = 450  # Shoot every x milliseconds
        self.last_shot_time = pygame.time.get_ticks()

    def move(self):
        self.rect.x, self.rect.y = pygame.mouse.get_pos()
        self.rect.x -= 50
        self.rect.y -= 50

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        bar_length = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_length
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 20, bar_length, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 20, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            bullet = Bullet(self.rect.centerx, self.rect.top, "player")
            self.bullets.append(bullet)
            self.last_shot_time = current_time

# Enemy class
class Enemy:
    def __init__(self, type, speed_multiplier=1.0):
        self.type = type
        self.health = 100
        self.max_health = 100
        self.image = enemy_imgs[type]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -50)
        self.base_speed = random.randint(2, 5)
        self.speed = self.base_speed * speed_multiplier
        self.bullets = []
        self.shoot_delay = 900
        self.last_shot_time = pygame.time.get_ticks()
        self.direction = 1
        self.steps = 0
        self.start_x = self.rect.x


    def move(self):
        if self.type == 1:  # Straight down
            self.rect.y += self.speed
        elif self.type == 2:  # Square
            self.rect.y += self.speed
            self.steps +=1

            if self.steps % 30 == 0:
                self.direction *= -1
        elif self.type == 3:  # Zigzag
            self.rect.y += self.speed
            self.steps += 1
            
            # Move left and right in a triangular pattern
            progress = (self.steps % 60) / 60  # 0 to 1
            if progress < 0.5:
                # First half: move right
                self.rect.x = self.start_x + progress * 100
            else:
                # Second half: move left
                self.rect.x = self.start_x + (1 - progress) * 100
            

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        bar_length = 50
        bar_height = 5
        fill = (self.health / self.max_health) * bar_length
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def off_screen(self):
        return self.rect.y > HEIGHT

    def collides_with(self, player):
        return self.rect.colliderect(player.rect)

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            if self.type == 1:  # Straight down
                bullet = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                self.bullets.append(bullet)
            elif self.type == 2:  # Spread shot
                    bullet = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                    self.bullets.append(bullet)

            elif self.type == 3:  # Targeted shot
                
                bullet = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                self.bullets.append(bullet)
                
                # Left angled bullet
                bullet_left = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                bullet_left.speed_x = -1.5 # Movement to the side
                bullet_left.speed = bullet_left.speed * 0.9  # Slightly slower vertical speed
                self.bullets.append(bullet_left) 
                
                # Right angled bullet
                bullet_right = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                bullet_right.speed_x = 1.0 # Movement to the side
                bullet_right.speed = bullet_right.speed * 0.9  # Slightly slower vertical speed
                self.bullets.append(bullet_right)

            self.last_shot_time = current_time
            

# Bullet class
class Bullet:
    def __init__(self, x, y, shooter):
        self.speed = 8
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.shooter = shooter
        self.speed_x = 0

    def move(self):
        if self.shooter == "player":
            self.rect.y -= self.speed
        elif self.shooter == "enemy":
            self.rect.y += self.speed
            self.rect.x += self.speed_x

    def draw(self, surface):
        if self.shooter == "enemy":
            # Rotate 180 degrees for enemy bullets
            rotated_img = pygame.transform.rotate(self.image, 180)
            surface.blit(rotated_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

    def off_screen(self):
        return self.rect.y < 0 or self.rect.y > HEIGHT

    def collides_with(self, target):
        return self.rect.colliderect(target.rect)
    
def end_screen(score):
    screen.blit(end_img, (0, 0))
    
    # Display final score
    score_text = font_large.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 90))
    
    play_again_button = Button(WIDTH//2 - 100, HEIGHT - 190, 200, 50, "PLAY AGAIN", BLUE, (0, 100, 200))
    quit_button = Button(WIDTH//2 - 100, HEIGHT - 120, 200, 50, "QUIT", BLUE, (0, 100, 200))

    end_running = True
    while end_running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_running = False
                pygame.quit()
                return False
            
            if play_again_button.is_clicked(mouse_pos, event):
                end_running = False
                return True
            
            if quit_button.is_clicked(mouse_pos, event):
                end_running = False
                pygame.quit()
                return False
        
        play_again_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        play_again_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
    
    return False

def game_loop():
    player = Player()
    enemies = []
    spawn_delay = 1000
    last_spawn_time = pygame.time.get_ticks()
    score = 0
    speed_multiplier = 1.0
    last_threshold = 0

    run = True
    clock = pygame.time.Clock()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        if score // 300 > last_threshold:
            last_threshold = score // 300
            speed_multiplier += 0.2
            print(f"Difficulty increased! Speed multiplier: {speed_multiplier}")

        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time > spawn_delay:
            enemy_type = random.randint(1, 3)
            enemies.append(Enemy(enemy_type, speed_multiplier))
            last_spawn_time = current_time

        player.move()
        player.shoot()

        enemies_to_remove = []
        for enemy in enemies[:]:
            enemy.move()
            enemy.shoot()

            if enemy.collides_with(player):
                player.take_damage(50)
                enemies_to_remove.append(enemy)

            bullets_to_remove = []
            for bullet in enemy.bullets[:]:
                bullet.move()
                if bullet.collides_with(player):
                    player.take_damage(25)
                    bullets_to_remove.append(bullet)
                elif bullet.off_screen():
                    bullets_to_remove.append(bullet)
            
            for bullet in bullets_to_remove:
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)

            if enemy.off_screen():
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        bullets_to_remove = []
        enemies_to_remove = []
        
        for bullet in player.bullets[:]:
            bullet.move()
            bullet_removed = False
            for enemy in enemies[:]:
                if not bullet_removed and bullet.collides_with(enemy):
                    enemy.take_damage(50)
                    bullets_to_remove.append(bullet)
                    bullet_removed = True
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                        if enemy.type == 1:
                            score += 25
                        elif enemy.type == 2:
                            score += 75
                        elif enemy.type == 3:
                            score += 50
            if not bullet_removed and bullet.off_screen():
                bullets_to_remove.append(bullet)
        
        for bullet in bullets_to_remove:
            if bullet in player.bullets:
                player.bullets.remove(bullet)
        
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        screen.blit(bg_img, (0, 0))
        player.draw(screen)
        for bullet in player.bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
            for bullet in enemy.bullets:
                bullet.draw(screen)
        
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if player.health <= 0:
            run = False

        pygame.display.flip()
        clock.tick(60)

    return end_screen(score)

def main():
    pygame.init()

    if not main_menu():
        return
    
    play_again = True
    while play_again:
        play_again = game_loop() 

if __name__ == "__main__":
    main()