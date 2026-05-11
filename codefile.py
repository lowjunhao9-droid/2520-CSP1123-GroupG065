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
     # obstacle (X position, Y position, obstacle WIDTH, obstacle HEIGHT)
     pygame.Rect(0, 1, 30, 1000),# left wall
     pygame.Rect(1, 60, 1500, 30),# top wall 
     pygame.Rect(10, 900, 1500, 30 ), #bottom wall 
     pygame.Rect(1480, 600, 30, 700), #right bottom wall
     pygame.Rect(1480, 80, 30, 350), # right top wall     
]

#obstacle inside the wall/ small obstacles in the map 
inside_obstacles =[
    #pygame.rect(x position, y position, width, height)
     pygame.Rect(380, 200, 50, 300),
     pygame.Rect(500, 600, 300, 50),
     pygame.Rect(715, 650, 85, 70),
     pygame.Rect(1000, 410, 95, 470),
     pygame.Rect(820, 830, 200, 50),
     pygame.Rect(795, 400, 300, 80),
     pygame.Rect(410, 200, 530, 50),
     pygame.Rect(1100, 200, 150, 40),
     pygame.Rect(1250, 200, 40, 150),
     pygame.Rect(1250, 700, 110, 130),
     
]

# definition of reset game
def reset_game():
    global square, zombie, all_sprites_list, room
    room = 1

    # Reset sprite groups
    all_sprites_list = pygame.sprite.Group()

    # New player
    square = Player()
    #spawn point
    square.rect.x = 100
    square.rect.y = 100
    all_sprites_list.add(square)

    # New zombie
    zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
    zombie.rect.x = 600
    zombie.rect.y = 600
    all_sprites_list.add(zombie)

    

# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #Load player image
        self.image = pygame.image.load("player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100,100))
        self.fireball_cooldown = 500 #0.5s cooldown
        self.last_fireball_time = 0

        #Stats
        self.rect = self.image.get_rect()
        self.health = 100 #player health
        self.stamina = 100 #stamina player
        self.last_regen_time = pygame.time.get_ticks()
        self.regen_delay = 1000 #wait 1 second before next regen

    def regen_stamina(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_regen_time >= self.regen_delay:
            if self.stamina < 100:
                  self.stamina += 10
                  print("Stamina",self.stamina)
            self.last_regen_time = current_time



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
    
    def cast_fireball(self,all_sprites_list):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_fireball_time >= self.fireball_cooldown:
            self.last_fireball_time = current_time

            #Direction (simple:always right for now)
            dx,dy = 1,0
            fireball = Fireball(self.rect.centerx,self.rect.centery,(dx,dy))
            all_sprites_list.add(fireball)
            print("Fireball cast")
        
        else:
             print("Fireball on cooldown!")
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
     def __init__(self, player, duration=200):
          super().__init__()
          #Load slash      
          self.image= pygame.image.load("slash2.png").convert_alpha()

          #Scale the image
          self.image = pygame.transform.scale(self.image,(120,120))

          #Position the slash just in front of the player
          self.rect = self.image.get_rect()
          self.rect.midleft = (player.rect.midright[0] - 100, player.rect.midright[1])


          #Track time
          self.spawn_time = pygame.time.get_ticks()
          self.duration = duration

     def update(self):

         #Remove slash after duration
         if pygame.time.get_ticks() - self.spawn_time >= self.duration:
              self.kill()

#special skill for player class
class Fireball(pygame.sprite.Sprite):
    def __init__(self,x,y,direction,speed=15,damage=30):
        super().__init__()
        self.image = pygame.image.load("fireball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(200,200))

        self.rect = self.image.get_rect(center=(x,y))
        self.direction = direction #(dc,dy) normalized vector
        self.speed = speed
        self.damage = damage

    def update(self):
        #move fireball
        self.rect.x += int(self.direction[0]*self.speed)
        self.rect.y += int(self.direction[1]*self.speed)

        #Check collision with zombies
        for zombie in zombies_group:
            if self.rect.colliderect(zombie.rect):
                 zombie.health -= self.damage
                 print("Zombie hit by fireball! Health:",zombie.health)
                 self.kill()#remove fire ball after hit
                 break

        #Remove if off screen
        if(self.rect.right < 0 or self.rect.left > 1500 or self.rect.bottom < 0 or self.rect.top > 1000):
             self.kill()

# Create sprite groups
all_sprites_list = pygame.sprite.Group()
zombies_group = pygame.sprite.Group()

# Create sprite(Player)
square = Player()
square.rect.x = 100
square.rect.y = 100
all_sprites_list.add(square)

#Function to spawn multiple zombies
def spawn_zombies(num_zombies=5):
     for i in range(num_zombies):
        zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
        zombie.rect.x = random.randint(100, 1400)  # random X
        zombie.rect.y = random.randint(100, 900)   # random Y
        zombies_group.add(zombie)
        all_sprites_list.add(zombie)
# Spawn 10 zombies at start
spawn_zombies(3)





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
                square.attack(zombies_group, all_sprites_list)


    keys = pygame.key.get_pressed()
    old_x = square.rect.x 
    old_y = square.rect.y 

    speed = 10
    #Fireball key
    if keys[pygame.K_f]:
         square.cast_fireball(all_sprites_list)
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        if square.stamina > 0:
            speed = 20              # sprint speed
            square.stamina -= 1     # drain stamina each frame
            print("stamina",round(square.stamina))
    else:
        square.regen_stamina()
    if keys[pygame.K_LEFT] and square.rect.x > 30: #move left 
        square.moveLeft(speed)
    if keys[pygame.K_RIGHT]  and square.rect.x < 1500 - square.rect.width - 30 : #move right 
        square.moveRight(speed)
    if keys[pygame.K_UP]  and square.rect.y > 60:     # move upward 
        square.moveForward(speed)
    if keys[pygame.K_DOWN] and square.rect.y < 1000 - square.rect.height - 30 : #move down 
        square.moveBack(speed)
    if keys[pygame.K_a] and square.rect.x  > 30:  # A = left 
        square.moveLeft(speed)
    if keys[pygame.K_d] and square.rect.x < 1500 - square.rect.width - 30: # D = Right 
        square.moveRight(speed)
    if keys[pygame.K_w] and square.rect.y > 60 : # W = Up 
        square.moveForward(speed)
    if keys[pygame.K_s] and square.rect.y < 1000 - square.rect.height -30 :  # S = down 
        square.moveBack(speed)

    if square.rect.x >= 1500 - square.rect.width:
            room += 1
            square.rect.x = 0
    if square.rect.x < 1:
         room -= 1 
         square.rect.x = 1       


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

    collision = False

    #check collision with still obstacles (the wall)
    for obstacle in obstacles:
         if square.rect.colliderect(obstacle):
              square.rect.x, square.rect.y = old_x, old_y 

    #check collision with small obstacles inside the wall
    for inside_obstacle in inside_obstacles:
         if square.rect.colliderect(inside_obstacle):
              square.rect.x, square.rect.y = old_x, old_y


    if not collision:
         for inside_obstacle in inside_obstacles:
              if square.rect.colliderect(inside_obstacle):
                   collision = True 
                   break
              
    if collision:
         square.rect.x = old_x
         square.rect.y = old_y          


    if room == 1:
            background.fill(GREEN)
    elif room == 2:
            background.fill(blue)    
    elif room == 3:
            background.fill(black)
 
 
 
 
  #Update all sprites
    all_sprites_list.update()

    # Clear background each frame
    background.fill(GREEN)
    if room == 2:
        background.fill(blue)

    # Draw obstacles After background but BEFORE SPRITES   
    for obstacle in obstacles:
         pygame.draw.rect(background, (0, 0, 0), obstacle)

    for inside_obstacle in inside_obstacles:
         pygame.draw.rect(background, (0, 0, 150), inside_obstacle )     

    for inside_obstacle in inside_obstacles:
         pygame.draw.rect(background, (0, 0, 150), inside_obstacle )     
           

    # Draw sprites
    all_sprites_list.update()
    all_sprites_list.draw(background)
    pygame.display.flip()
    clock.tick(60)

    # Draw obstacles After background but BEFORE SPRITES   
    for obstacle in obstacles:
         pygame.draw.rect(background, (0, 0, 0), obstacle)
#testing git lmao 

pygame.quit()