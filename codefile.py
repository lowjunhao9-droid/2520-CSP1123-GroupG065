import pygame
import random

pygame.init()

# Display window
background = pygame.display.set_mode((1500, 800))
pygame.display.set_caption("Zombie Slayer: Blade Survival")

# Colors
GREEN = (0,100,0)
SURFACE_COLOR = (167, 255, 100)
RED = (200, 0, 0)
black = (0,0,0,)
blue = (0,0,150)
purple = (100,0,100)
light_green = (144,238,144)

# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        self.image.set_colorkey(GREEN)
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveForward(self, speed):
        self.rect.y -= speed   # up

    def moveBack(self, speed):
        self.rect.y += speed   # down
class Zombie(pygame.sprite.Sprite):
    def __init__(self, image_file, scale=(50,50), speed=2, player=None):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale) #resize
        self.rect = self.image.get_rect()
        self.speed = speed
        self.player = player
    
    def update(self):
        #Calculate direction(player-zombie)
        if self.player:
            dx = self.player.rect.x - self.rect.x
            dy = self.player.rect.y - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance != 0: #avoid division by zero
               #Normalize vector and move zombie
                self.rect.x += self.speed * dx/distance
                self.rect.y += self.speed  * dy/distance

# Create sprite(Player)
all_sprites_list = pygame.sprite.Group()
square = Player(RED, 100, 100)
square.rect.x = 200
square.rect.y = 300
all_sprites_list.add(square)

#Create zombie sprite
zombie = Zombie("Zombie1.webp", scale=(100,100),player=square)
zombie.rect.x = 600
zombie.rect.y = 600
all_sprites_list.add(zombie)



# Game loop
clock = pygame.time.Clock()
running = True
damage_timer = 0.0
game_over = False
menu_state = "menu"
sprint_cooldown = 0.0
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if menu_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            start_button_rect = pygame.Rect(1500 // 2 - 100, 800 // 2 - 50, 200, 50)
            quit_button_rect = pygame.Rect(1500 // 2 - 100, 800 // 2 + 50, 200, 50)
            if start_button_rect.collidepoint(mouse_pos):
                menu_state = "playing"
            elif quit_button_rect.collidepoint(mouse_pos):
                running = False
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            button_center = (1500 // 2, 800 // 2 + 100)
            button_rect = pygame.Rect(button_center[0] - 100, button_center[1] - 25, 200, 50)
            if button_rect.collidepoint(mouse_pos):
                # Reset game
                square.health = 100
                square.stamina = 100
                square.rect.x = 200
                square.rect.y = 300
                zombie.rect.x = 600
                zombie.rect.y = 600
                damage_timer = 0.0
                sprint_cooldown = 0.0
                game_over = False

    if menu_state == "playing" and not game_over:
        keys = pygame.key.get_pressed()
        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and square.stamina > 0 and sprint_cooldown <= 0
        speed = 12 if sprinting else 6
        moving = False
        if keys[pygame.K_LEFT] and square.rect.x > 1: #move left 
            square.moveLeft(speed)
            moving = True
        if keys[pygame.K_RIGHT] and square.rect.x < 1500 - square.rect.width: #move right 
            square.moveRight(speed)
            moving = True
        if keys[pygame.K_UP] and square.rect.y > 1:     # move upward 
            square.moveForward(speed)
            moving = True
        if keys[pygame.K_DOWN] and square.rect.y < 1000 - square.rect.height: #move down 
            square.moveBack(speed)
            moving = True
        if keys[pygame.K_a] and square.rect.x > 1:  # A = left 
            square.moveLeft(speed)
            moving = True
        if keys[pygame.K_d] and square.rect.x < 1500 - square.rect.height: # D = Right 
            square.moveRight(speed)
            moving = True
        if keys[pygame.K_w] and square.rect.y > 1: # W = Up 
            square.moveForward(speed)
            moving = True
        if keys[pygame.K_s] and square.rect.y < 1000 - square.rect.height:  # S = down 
            square.moveBack(speed)
            moving = True

        # Stamina logic
        if sprinting:
            square.stamina -= 30 * dt  # faster depletion when sprinting
        if square.stamina < square.max_stamina:
            square.stamina += 10 * dt  # regenerate stamina
        square.stamina = max(0, min(square.max_stamina, square.stamina))
        
        # Sprint cooldown
        if square.stamina <= 0 and sprint_cooldown <= 0:
            sprint_cooldown = 3.0
        sprint_cooldown = max(0, sprint_cooldown - dt)
        
        #Update all sprites
        all_sprites_list.update()
        
        # Check collision with zombie and lose health
        if pygame.sprite.collide_rect(square, zombie):
            damage_timer += dt
            if damage_timer >= 1.0:
                square.health -= 10
                damage_timer = 0.0
                square.health = max(0, square.health)
                if square.health <= 0:
                    game_over = True
        else:
            damage_timer = 0.0  # reset timer if not colliding
    
    # Clear background each frame
    background.fill(GREEN)

    if menu_state == "menu":
        # Draw main menu
        title_font = pygame.font.Font(None, 74)
        title_text = title_font.render("Zombie Slayer", True, RED)
        title_rect = title_text.get_rect(center=(1500 // 2, 800 // 2 - 150))
        background.blit(title_text, title_rect)

        button_font = pygame.font.Font(None, 36)
        
        # Start Game button
        start_button_rect = pygame.Rect(1500 // 2 - 100, 800 // 2 - 50, 200, 50)
        pygame.draw.rect(background, light_green, start_button_rect)
        start_text = button_font.render("Start Game", True, black)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        background.blit(start_text, start_text_rect)
        
        # Quit Game button
        quit_button_rect = pygame.Rect(1500 // 2 - 100, 800 // 2 + 50, 200, 50)
        pygame.draw.rect(background, light_green, quit_button_rect)
        quit_text = button_font.render("Quit Game", True, black)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        background.blit(quit_text, quit_text_rect)
        
    elif menu_state == "playing":
        if not game_over:
            # Draw sprites
            all_sprites_list.update()
            all_sprites_list.draw(background)

            # health bar
            health_bar_width = 200
            health_bar_height = 20
            health_ratio = square.health / square.max_health
            pygame.draw.rect(background, RED, (10, 10, health_bar_width, health_bar_height))
            pygame.draw.rect(background, light_green, (10, 10, health_bar_width * health_ratio, health_bar_height))

            # stamina bar
            stamina_bar_width = 200
            stamina_bar_height = 20
            stamina_ratio = square.stamina / square.max_stamina
            pygame.draw.rect(background, black, (10, 40, stamina_bar_width, stamina_bar_height))
            pygame.draw.rect(background, blue, (10, 40, stamina_bar_width * stamina_ratio, stamina_bar_height))
        else:
            # game over screen
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, RED)
            text_rect = text.get_rect(center=(1500 // 2, 800 // 2))
            background.blit(text, text_rect)

            # restart button
            button_center = (1500 // 2, 800 // 2 + 100)
            button_rect = pygame.Rect(button_center[0] - 100, button_center[1] - 25, 200, 50)
            pygame.draw.rect(background, light_green, button_rect)
            button_font = pygame.font.Font(None, 36)
            button_text = button_font.render("Restart", True, black)
            button_text_rect = button_text.get_rect(center=button_center)
            background.blit(button_text, button_text_rect)

    pygame.display.flip()

#testing git lmao 

pygame.quit()