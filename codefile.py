import pygame
import random

pygame.init()

# Display window
background = pygame.display.set_mode((1500, 1000))
green = (0, 100, 0)
pygame.display.set_caption("Zombie Slayer: Blade Survival")

# Colors
COLOR = green
SURFACE_COLOR = (167, 255, 100)
RED = (200, 0, 0)
black = (0,0,0,)
blue = (0,0,150)

# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        self.image.set_colorkey(COLOR)
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveForward(self, speed):
        self.rect.y -= speed   # up

    def moveBack(self, speed):
        self.rect.y += speed   # down

# Create sprite
all_sprites_list = pygame.sprite.Group()
square = Player(RED, 100, 100)
square.rect.x = 200
square.rect.y = 300
all_sprites_list.add(square)

clock = pygame.time.Clock()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and square.rect.x > 1: #move left 
        square.moveLeft(10)
    if keys[pygame.K_RIGHT] and square.rect.x < 1500 - square.rect.width: #move right 
        square.moveRight(10)
    if keys[pygame.K_UP] and square.rect.y > 1:     # move upward 
        square.moveForward(10)
    if keys[pygame.K_DOWN] and square.rect.y < 1000 - square.rect.height: #move down 
        square.moveBack(10)
    if keys[pygame.K_a] and square.rect.x > 1:  # A = left 
        square.moveLeft(10)
    if keys[pygame.K_d] and square.rect.x < 1500 - square.rect.height: # D = Right 
        square.moveRight(10)
    if keys[pygame.K_w] and square.rect.y > 1: # W = Up 
        square.moveForward(10)
    if keys[pygame.K_s] and square.rect.y < 1000 - square.rect.height:  # S = down 
        square.moveBack(10)

    # Clear background each frame
    background.fill(green)

    # Draw sprites
    all_sprites_list.update()
    all_sprites_list.draw(background)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
            
        

      

