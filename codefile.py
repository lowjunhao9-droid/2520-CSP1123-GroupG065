import pygame
import random

pygame.init()

# Display window
background = pygame.display.set_mode((1500, 1000))
pygame.display.set_caption("Zombie Slayer: Blade Survival")

# Colors
GREEN = (0,100,0)
SURFACE_COLOR = (167, 255, 100)
RED = (200, 0, 0)
black = (0,0,0,)
blue = (0,0,150)
purple = (100,0,100)
room = 1

#still obstacles 
obstacles = [
     pygame.Rect(1, 1, 30, 1000),# obstacle (X position, Y position, obstacle width, obstacle height)
     pygame.Rect(700, 800, 1000, 70),
     pygame.Rect(350, 450, 300, 50),
     pygame.Rect(1450, 200, 50, 400),
     pygame.Rect(1000, 200, 50, 100),
]

# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        self.image.set_colorkey(GREEN)
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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #move player          
    keys = pygame.key.get_pressed()
    old_x = square.rect.x
    old_y = square.rect.y 
    if keys[pygame.K_LEFT] and square.rect.x > 1: #move left 
        square.moveLeft(10)
    if keys[pygame.K_RIGHT] and square.rect.x < 1500 - square.rect.width or square.rect.y < 00 : #move right 
        square.moveRight(10)
    if keys[pygame.K_UP] and square.rect.y > 1:     # move upward 
        square.moveForward(10)
    if keys[pygame.K_DOWN] and square.rect.y < 1000 - square.rect.height: #move down 
        square.moveBack(10)
    if keys[pygame.K_a] and square.rect.x > 1:  # A = left 
        square.moveLeft(10)
    if keys[pygame.K_d] : # D = Right 
        square.moveRight(10)
    if keys[pygame.K_w] and square.rect.y > 1: # W = Up 
        square.moveForward(10)
    if keys[pygame.K_s] and square.rect.y < 1000 - square.rect.height:  # S = down 
        square.moveBack(10)

    if square.rect.x > 1500:
            room += 1
            square.rect.x = 0

    if room == 1:
            background.fill(GREEN)
    elif room == 2:
            background.fill(blue)    
    elif room == 3:
            background.fill(black)

    #check collision with still obstacles
    for obstacle in obstacles:
         if square.rect.colliderect(obstacle):
              square.rect.x, square.rect.y = old_x, old_y 
              
  #Update all sprites
    all_sprites_list.update()
    
    # Clear background each frame
    background.fill(GREEN)
    if room == 2:
        background.fill(blue)

    # Draw obstacles After background but BEFORE SPRITES   
    for obstacle in obstacles:
         pygame.draw.rect(background, (0, 0, 0), obstacle)
           

    # Draw sprites
    all_sprites_list.update()
    all_sprites_list.draw(background)
    pygame.display.flip()
    clock.tick(60)

#testing git lmao 
#git is not working T-T
#im mentally unstable
pygame.quit()

