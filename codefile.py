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

# definition of reset game
def reset_game():
    global square, zombie, all_sprites_list, room
    room = 1

    # Reset sprite groups
    all_sprites_list = pygame.sprite.Group()

    # New player
    square = Player(RED, 100, 100)
    square.rect.x = 200
    square.rect.y = 300
    all_sprites_list.add(square)

    # New zombie
    zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
    zombie.rect.x = 600
    zombie.rect.y = 600
    all_sprites_list.add(zombie)

# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(SURFACE_COLOR)
        self.image.set_colorkey(GREEN)
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, height))
        self.rect = self.image.get_rect()
        self.health = 100 #player health


    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveForward(self, speed):
        self.rect.y -= speed   # up

    def moveBack(self, speed):
        self.rect.y += speed   # down
    
    def attack(self, zombies_group, all_sprites_list):
        #spawn visible slash
        slash = Attack(self)
        all_sprites_list.add(slash)
         
        #Damge zombie in range 
        for zombie in zombies_group:
              if self.rect.colliderect(zombie.rect):
                   zombie.health -=10
                   print("Zombie hit! Health",zombie.health)
    
    def die(self):
        print("Player dead")
        self.kill() # remove player sprite

         
 
class Zombie(pygame.sprite.Sprite):
    def __init__(self, image_file, scale=(50,50), speed=2, player=None):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale) #resize
        self.rect = self.image.get_rect()
        self.speed = speed
        self.player = player
        self.health = 100

        #Cooldown in millisecond (eg. 2000ms = 2 second)
        self.attack_cooldown = 1000
        self.last_attack_time = 0
    def update(self):
        # If zombie is dead,remove it
        if self.health <= 0:
             self.kill()
             return
        
        #move toward player
        #Calculate direction(player-zombie)
        if self.player:
            dx = self.player.rect.x - self.rect.x
            dy = self.player.rect.y - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance != 0: #avoid division by zero
               #Normalize vector and move zombie
                self.rect.x += self.speed * dx/distance
                self.rect.y += self.speed  * dy/distance
            
            #attack if touching player
            if self.rect.colliderect(self.player.rect):
                 current_time = pygame.time.get_ticks()
                 if current_time - self.last_attack_time >= self.attack_cooldown:
                      self.player.health -= 10
                      print("Player hit! Heath:", self.player.health)
                      self.last_attack_time = current_time
                 

class Attack(pygame.sprite.Sprite):
     def __init__(self, player, duration=10):
          super().__init__()
          #Load slash      
          self.image= pygame.image.load("slash2.png").convert_alpha()
          
          #Scale the image
          self.image = pygame.transform.scale(self.image,(120,120))

          #Position the slash just in front of the player
          self.rect = self.image.get_rect(midleft=player.rect.midright)
          
          #Track time
          self.spawn_time = pygame.time.get_ticks()
          self.duration = duration
    
     def update(self):
          
         #Remove slash after duration
         if pygame.time.get_ticks() - self.spawn_time >= self.duration:
              self.kill()

          

# Create sprite(Player)
all_sprites_list = pygame.sprite.Group()
square = Player(RED, 100, 100)
square.rect.x = 200
square.rect.y = 300
all_sprites_list.add(square)

#Create zombie sprite
zombie = Zombie("Zombie1.png", scale=(100,100),player=square)
zombie.rect.x = 600
zombie.rect.y = 600
all_sprites_list.add(zombie)



# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        
        #keyboard event
        if event.type == pygame.QUIT:
            running = False
        
        #mouse event
        if event.type == pygame.MOUSEBUTTONDOWN:
             if event.button == 1: #in python left click value = 1
                square.attack([zombie], all_sprites_list)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and square.rect.x > 1: #move left 
        square.moveLeft(10)
    if keys[pygame.K_RIGHT] : #move right 
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

    if square.rect.x >= 1500 - square.rect.width:
            room += 1
            square.rect.x = 0

    if room == 1:
            background.fill(GREEN)
    elif room == 2:
            background.fill(blue)    
    elif room == 3:
            background.fill(black)
    
    #Check if player id dead or not
    if square.health <= 0:
         print("Player died! Restarting game...")
         reset_game()
    
    
            





    #Update all sprites
    all_sprites_list.update()
    
    # Clear background each frame
    background.fill(GREEN)
    if room == 2:
        background.fill(blue)

    # Draw sprites
    all_sprites_list.update()
    all_sprites_list.draw(background)
    pygame.display.flip()
    clock.tick(60)

#testing git lmao 

pygame.quit()