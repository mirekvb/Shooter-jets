import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Jets")

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
    img = pygame.image.load('menu.png')
    screen.blit(img,(0, 0))
    
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
        self.inicial = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.inicial, (110, 100))
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
    def __init__(self, type):
        self.type = type
        self.health = 100
        self.max_health = 100
        self.image = self.load_sprite(f"enemy{type}.png")  # Load enemy sprite
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -50)
        self.speed = random.randint(2, 5)
        self.bullets = []
        self.shoot_delay = 900  # Shoot every x milliseconds
        self.last_shot_time = pygame.time.get_ticks()
        self.angle = 0  # For circular movement
        self.amplitude = random.randint(50, 100)  # For sine wave movement

    def load_sprite(self, path):
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(sprite, (100, 80))

    def move(self):
        if self.type == 1:  # Straight down
            self.rect.y += self.speed
        elif self.type == 2:  # Zigzag
            self.rect.y += self.speed
            self.rect.x += math.sin(self.angle) * 3
            self.angle += 0.1
        elif self.type == 3:  # Circular
            self.rect.y += self.speed
            self.rect.x += math.cos(self.angle) * 3
            self.angle += 0.1

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
                for angle in [-15, 0, 15]:
                    bullet = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                    bullet.speed_x = math.sin(math.radians(angle)) * 3
                    bullet.speed_y = bullet.speed
                    self.bullets.append(bullet)
            elif self.type == 3:  # Targeted shot
                bullet = Bullet(self.rect.centerx, self.rect.bottom, "enemy")
                self.bullets.append(bullet)
            self.last_shot_time = current_time

# Bullet class
class Bullet:
    def __init__(self, x, y, shooter):
        self.speed = 8
        self.inicial = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale(self.inicial, (25, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.shooter = shooter  # "player" or "enemy"
        self.speed_x = 0  # For spread shots

    def move(self):
        if self.shooter == "player":
            self.rect.y -= self.speed  # Move upward
        elif self.shooter == "enemy":
            self.rect.y += self.speed  # Move downward
            self.rect.x += self.speed_x  # For spread shots

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def off_screen(self):
        return self.rect.y < 0 or self.rect.y > HEIGHT

    def collides_with(self, target):
        return self.rect.colliderect(target.rect)
    
def end_screen(score):
    screen.fill(BLUE)
    img = pygame.image.load('end.png')
    screen.blit(img, (0, 0))
    
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
                return False  # Exit the function
            
            if play_again_button.is_clicked(mouse_pos, event):
                end_running = False
                return True  # Signal to play again
            
            if quit_button.is_clicked(mouse_pos, event):
                end_running = False
                pygame.quit()
                return False  # Signal to quit
        
        # Update button states
        play_again_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Draw buttons
        play_again_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
    
    return False  # Default case

def game_loop():
    player = Player()
    enemies = []
    spawn_delay = 1000  
    last_spawn_time = pygame.time.get_ticks()
    score = 0  # Initialize score

    run = True
    clock = pygame.time.Clock()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Don't play again, quit entirely

        # Spawn new enemies
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time > spawn_delay:
            enemy_type = random.randint(1, 3)  # Random enemy type
            enemies.append(Enemy(enemy_type))
            last_spawn_time = current_time

        # Move player
        player.move()
        player.shoot()

        # Move and check collisions for enemies
        enemies_to_remove = []
        for enemy in enemies[:]:
            enemy.move()
            enemy.shoot()

            if enemy.collides_with(player):
                player.take_damage(50)
                enemies_to_remove.append(enemy)

            # Check enemy bullets
            bullets_to_remove = []
            for bullet in enemy.bullets[:]:
                bullet.move()
                if bullet.collides_with(player):
                    player.take_damage(25)
                    bullets_to_remove.append(bullet)
                elif bullet.off_screen():
                    bullets_to_remove.append(bullet)
            
            # Remove marked bullets
            for bullet in bullets_to_remove:
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)

            if enemy.off_screen():
                enemies_to_remove.append(enemy)

        # Remove marked enemies
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        # Player bullets collision
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
                        # Add score based on enemy type
                        if enemy.type == 1:
                            score += 25
                        elif enemy.type == 2:
                            score += 75
                        elif enemy.type == 3:
                            score += 50
            if not bullet_removed and bullet.off_screen():
                bullets_to_remove.append(bullet)
        
        # Remove marked bullets and enemies
        for bullet in bullets_to_remove:
            if bullet in player.bullets:
                player.bullets.remove(bullet)
        
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        # Draw everything
        screen.fill(BLUE)
        img = pygame.image.load('bg.png')
        screen.blit(img,(0,0))
        player.draw(screen)
        for bullet in player.bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
            for bullet in enemy.bullets:
                bullet.draw(screen)
        
        # Draw score
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if player.health <= 0:
            run = False

        pygame.display.flip()
        clock.tick(60)

    # Game over, show end screen with final score
    return end_screen(score)

def main():
    pygame.init()

    if not main_menu():  # Show menu first
        return
    
    # Keep playing until the player chooses to quit
    play_again = True
    while play_again:
        play_again = game_loop()

if __name__ == "__main__":
    main()