import pygame
import random

pygame.init()

#=======Display window=========#
#default screen size
game_width = 1500
game_height = 1000

#make it resizable
window = pygame.display.set_mode((game_width,game_height),pygame.RESIZABLE)
pygame.display.set_caption("Zombie Slayer: Blade Survival") #menu

#background
background = pygame.Surface((game_width,game_height))
#======================================#

# Load UI images
healthui_image = pygame.image.load("healthui.png").convert_alpha()
staminaui_image = pygame.image.load("staminaui.png").convert_alpha()
fireui_image = pygame.image.load("fireui.png").convert_alpha()
waveui_image = pygame.image.load("waveui.png").convert_alpha()
menu_background = pygame.image.load("Menu1600.png").convert()
zombs_image = pygame.image.load("zombs.png").convert_alpha()
ggs_image = pygame.image.load("GGs.png").convert_alpha()




menu_background = pygame.image.load("Menu1600.png").convert()

# Colors
GREEN = (0,100,0)
SURFACE_COLOR = (167, 255, 100)
RED = (200, 0, 0)
black = (0,0,0)
blue = (0,0,150)
purple = (100,0,100)
room = 1
zombies_killed = 0

#still obstacles 
obstacles = [
     # obstacle (X position, Y position, obstacle WIDTH, obstacle HEIGHT)
     pygame.Rect(0, 1, 30, 1000),# left wall
     pygame.Rect(1, 60, 1500, 30),# top wall 
     pygame.Rect(10, 900, 1500, 30 ), #bottom wall 
     pygame.Rect(1480, 600, 30, 700), #right bottom wall
     pygame.Rect(1480, 80, 30, 350), # right top wall     
]

#obstacle inside the wall/ small obstacles in the map for ROOM 1
inside_obstacles_room1 =[
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

#obstacle inside the wall/ small obstacles in the map for ROOM 2 (black obstacles)
inside_obstacles_room2 =[
    # Different layout for room 2 - all in black
     pygame.Rect(200, 150, 100, 100),   # Square block
     pygame.Rect(600, 300, 150, 50),    # Horizontal bar
     pygame.Rect(900, 500, 50, 200),    # Vertical bar
     pygame.Rect(400, 700, 200, 50),    # Horizontal bar bottom
     pygame.Rect(1100, 200, 80, 80),    # Square block top right
     pygame.Rect(1200, 600, 100, 150),  # Rectangle bottom right
     pygame.Rect(300, 400, 60, 150),    # Vertical bar left
     pygame.Rect(800, 150, 200, 40),    # Top horizontal bar
     pygame.Rect(100, 500, 80, 80),     # Square left side
     pygame.Rect(1300, 400, 80, 100),   # Rectangle right side
]

# Room 3 has NO obstacles (empty list)
inside_obstacles_room3 = []  # Empty list - no obstacles in room 3

# Current obstacles based on room
inside_obstacles = inside_obstacles_room1.copy()

# Store original obstacles for reset
original_inside_obstacles_room1 = inside_obstacles_room1.copy()
original_inside_obstacles_room2 = inside_obstacles_room2.copy()
original_inside_obstacles_room3 = inside_obstacles_room3.copy()

# COLLISION HELPER FUNCTION
def check_collision_with_obstacles(sprite):
    """Check if a sprite collides with any obstacle"""
    for obstacle in obstacles:
        if sprite.hitbox.colliderect(obstacle):
            return True
    for inside_obstacle in inside_obstacles:
        if sprite.hitbox.colliderect(inside_obstacle):
            return True
    return False

gate_is_open = False

# Gate position (right side)
gate_rect = pygame.Rect(1420, 360, 60, 300)

def are_zombies_in_room():
    """Check if there are any zombies alive in the current room"""
    return len(zombies_group) > 0

def draw_gate(surface, rect, is_open):
    pygame.draw.rect(surface, (90, 90, 90), rect)

    if not is_open:
        # Draw locked gate pattern
        for y in range(rect.top + 8, rect.bottom - 8, 20):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))
        # Add a red lock indicator when zombies are present damage
        if are_zombies_in_room():
            pygame.draw.circle(surface, (255, 0, 0), (rect.centerx, rect.centery - 30), 15)
            pygame.draw.rect(surface, (255, 0, 0), (rect.centerx - 5, rect.centery - 15, 10, 20))
    else:
        # Draw open gate pattern
        for y in range(rect.top + 5, rect.top + 20, 12):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))
        for y in range(rect.bottom - 20, rect.bottom - 5, 12):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))

# definition of reset game
def reset_game():
    global square, room, inside_obstacles, zombies_killed
    room = 1
    zombies_killed = 0
    # Reset inside obstacles to room 1 obstacles
    inside_obstacles.clear()
    inside_obstacles.extend(original_inside_obstacles_room1)
    
    all_sprites_list.empty() # clear all the sprites
    zombies_group.empty()    # clear previous zombies
    
    square = Player()        # again to be a player
    square.rect.x = 100
    square.rect.y = 100
    #manual centering hitbox of player
    square.hitbox.center = square.rect.center 
    all_sprites_list.add(square)
    spawn_zombies(3, 0) #spawn 3 zombies only

#============================== Sprite Class for player=============================================#
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #Load player image
        player_size = (100,100)
        self.images = {
            "up": pygame.transform.scale(pygame.image.load("player_up.png").convert_alpha(), player_size),
            "down": pygame.transform.scale(pygame.image.load("player_down.png").convert_alpha(), player_size),
            "left": pygame.transform.scale(pygame.image.load("player_left.png").convert_alpha(), player_size),
            "right": pygame.transform.scale(pygame.image.load("player_right.png").convert_alpha(), player_size),
        }
        
        self.fireball_cooldown = 500
        self.last_fireball_time = 0
        self.shockwave_cooldown = 1000
        self.last_shockwave_time = 0
        self.facing = "right"
        self.image = self.images[self.facing]

        #Stats
        self.rect = self.image.get_rect() 
        self.hitbox = self.rect.inflate(-15, -15)  # 85x85 hitbox - balanced
        
        self.health = 100
        self.stamina = 100
        self.last_regen_time = pygame.time.get_ticks()
        self.regen_delay = 1000
        
        self.is_blocking = False #Track if player is holding the block button
        self.invincible = False
        self.invincible_time = 0
    
    def regen_stamina(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_regen_time >= self.regen_delay:
            if self.stamina < 100:
                self.stamina += 10
            self.last_regen_time = current_time
    
    def make_invincible(self, duration=1000):
        self.invincible = True
        self.invincible_time = pygame.time.get_ticks() + duration

    def moveRight(self, pixels):
        if self.is_blocking: return
        self.rect.x += pixels
        self.hitbox.x += pixels
        self.facing = "right"
        self.update_image()

    def moveLeft(self, pixels):
        if self.is_blocking: return
        self.rect.x -= pixels
        self.hitbox.x -= pixels
        self.facing = "left"
        self.update_image()

    def moveForward(self, speed):
        if self.is_blocking: return
        self.rect.y -= speed
        self.hitbox.y -= speed
        self.facing = "up"
        self.update_image()

    def moveBack(self, speed):
        if self.is_blocking: return
        self.rect.y += speed
        self.hitbox.y += speed
        self.facing = "down"
        self.update_image()

    def attack(self, zombies_group, all_sprites_list):
        #spawn visible slash
        slash = Attack(self)
        all_sprites_list.add(slash)

        #Damage zombie in range
        for zombie in zombies_group:
            if slash.rect.colliderect(zombie.rect) or slash.rect.colliderect(zombie.hitbox):
                zombie.health -= 10
                print(f"Zombie hit! Health: {zombie.health}")
                # Visual feedback
                zombie.hit_effect = 5 #flicker 5 frames
    
    def cast_fireball(self, all_sprites_list):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_fireball_time >= self.fireball_cooldown:
            self.last_fireball_time = current_time

            #Direction based on facing
            if self.facing == "right":
                dx, dy = 1, 0
            elif self.facing == "left":
                dx, dy = -1, 0
            elif self.facing == "up":
                dx, dy = 0, -1
            elif self.facing == "down":
                dx, dy = 0, 1
            
            fireball = Fireball(self.rect.centerx, self.rect.centery, (dx, dy))
            all_sprites_list.add(fireball)
            print("Fireball cast")
        else:
            print("Fireball on cooldown!")
    
    def cast_shockwave(self, all_sprites_list):
        current_time = pygame.time.get_ticks()

        #check player have enoght cooldown and stamina or not?
        if current_time - self.last_shockwave_time >= self.shockwave_cooldown:
            if self.stamina >= 30:
                self.stamina -= 30
                self.last_shockwave_time = current_time

                #create the wave at the center of player
                #noted to make the wave wave bigger just increase max_radius
                wave = Shockwave(self.rect.centerx, self.rect.centery, max_radius=250, speed=6, damage=50 )#this is the place that truely can change damage and every thing
                all_sprites_list.add(wave)
                print("Shockwave cast!")
            else:
                print("Not enough stamina for Shockwave!")
        else:
            print("Shockwave on cooldown!")




    def die(self):
        print("Player dead")
        self.kill()

    def update(self):
        # Keep hitbox centered on visual sprite
        self.hitbox.center = self.rect.center
        self.regen_stamina()
        self.update_image()
        
        # Handle invincibility frames
        if self.invincible and pygame.time.get_ticks() > self.invincible_time:
            self.invincible = False

#=================shield/block(in update_image)=================#
    def update_image(self):        
        base_img = self.images[self.facing].copy()
        
        # Flash effect when invincible
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            base_img.set_alpha(128)
        
        # hold b will have a semi-transparent circular shield
        if self.is_blocking:
            #create a canvas the same size with the player
            
            
            #Draw a semi-transparent sky blue circular cover inner ring (Color: Sky Blue, Transparency: 100)
            shield_surface = pygame.Surface(base_img.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 191, 255, 100), (50, 50), 48)  
            pygame.draw.circle(shield_surface, (138, 43, 226, 225), (50, 50), 48, 4) 
            
            # Blit the shield canvas on the character layer
            base_img.blit(shield_surface, (0, 0))
        
        self.image = base_img
#====================================================#            
#=============================================================================#


#==========================Class for zombie=======================================#
class Zombie(pygame.sprite.Sprite):
    def __init__(self, image_file, scale=(100,100), speed=2, player=None):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.player = player
        self.health = 100
        self.max_health = self.health
        self.damage = 10

        #Cooldown for attacks
        self.attack_cooldown = 1000
        self.last_attack_time = 0
        
        # Hitbox for zombie (slightly smaller for better movement)
        self.hitbox = self.rect.inflate(-15, -15)
        self.hit_effect = 0
    
    def update(self):
        # If zombie is dead, remove it
        if self.health <= 0:
            global zombies_killed
            zombies_killed += 1
            self.kill()
            return
        
        # Handle hit effect
        if self.hit_effect > 0:
            self.image.set_alpha(128)
            self.hit_effect -= 1
        else:
            self.image.set_alpha(255)

        # Move toward player
        if self.player and self.player.health > 0:
            # Store old position
            self.hitbox.center = self.rect.center
            
            old_x = self.hitbox.x
            old_y = self.hitbox.y
            
            # Calculate direction to player
            dx = self.player.rect.x - self.rect.x
            dy = self.player.rect.y - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 0:
                # Try moving in X direction first
                self.hitbox.x += int(self.speed * dx/distance)
                if check_collision_with_obstacles(self):
                    self.hitbox.x = old_x
                
                # Try moving in Y direction
                self.hitbox.y += int(self.speed * dy/distance)
                if check_collision_with_obstacles(self):
                    self.hitbox.y = old_y
                    
                # Apply position to render image
                self.rect.center = self.hitbox.center

            # Attack if touching player
            if self.rect.colliderect(self.player.rect):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    if not self.player.invincible:
                        if self.player.is_blocking:
                            damage_taken = 1
                            self.player.health -= damage_taken
                            print(f"Attack Blocked! Health: {self.player.health}")
                        else:
                            self.player.health -= self.damage
                            print(f"Player hit! Health: {self.player.health}")
                        self.player.make_invincible(1000)
                        self.last_attack_time = current_time

class FasterZombie(Zombie):
    def __init__(self, image_file, scale=(90,90), speed=5, player=None):
        super().__init__(image_file, scale, speed, player)
        self.health = 60
        self.max_health = self.health
        self.damage = 10
class ArmoredZombie(Zombie):
    def __init__(self, image_file, scale=(110,110), speed=1, player=None):
        super().__init__(image_file, scale, speed, player)
        self.health = 200 
        self.max_health = self.health
        self.damage = 15
class BossZombie(Zombie):
    def __init__(self, image_file, scale=(200,200), speed =5 , player=None):
        super().__init__(image_file, scale, speed,player)
        self.health = 500 
        self.max_health = self.health
        self.damage = 40       
##===================================================================================##  


class Attack(pygame.sprite.Sprite):
    def __init__(self, player, duration=200):
        super().__init__()
        #Load slash      
        self.original_image = pygame.image.load("slash2.png").convert_alpha()
        #Scale the image
        self.original_image = pygame.transform.scale(self.original_image, (120,120))

        #Position of the slash based on player facing zombs.png
        if player.facing == "right":
            self.image = self.original_image
            self.rect = self.image.get_rect(midleft=player.rect.midright)
        elif player.facing == "left":
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.rect = self.image.get_rect(midright=player.rect.midleft)
        elif player.facing == "up":
            self.image = pygame.transform.rotate(self.original_image, 90)
            self.rect = self.image.get_rect(midbottom=player.rect.midtop)
        elif player.facing == "down":
            self.image = pygame.transform.rotate(self.original_image, -90)
            self.rect = self.image.get_rect(midtop=player.rect.midbottom)
        
        self.hitbox = self.rect
        #Track time
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        #Remove slash after duration
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()

#=======================special skill for player class==============================================
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=15, damage=30):
        super().__init__()
        base_image = pygame.image.load("fireball.png").convert_alpha()
        base_image = pygame.transform.scale(base_image, (100,100))

        #Rotate or flip based on direction
        if direction == (1, 0):  # right
            self.image = base_image
        elif direction == (-1, 0):  # left
            self.image = pygame.transform.flip(base_image, True, False)
        elif direction == (0, -1):  # up
            self.image = pygame.transform.rotate(base_image, 90)
        elif direction == (0, 1):  # down
            self.image = pygame.transform.rotate(base_image, -90)

        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed
        self.damage = damage

        self.hitbox = self.rect

    def update(self):
        #move fireball
        self.rect.x += int(self.direction[0] * self.speed)
        self.rect.y += int(self.direction[1] * self.speed)

        #if collision with wall it will gone
        if check_collision_with_obstacles(self):
            self.kill()
            return
        
        #Check collision with zombies
        for zombie in zombies_group:
            if self.rect.colliderect(zombie.rect):
                zombie.health -= self.damage
                print(f"Zombie hit by fireball! Health: {zombie.health}")
                zombie.hit_effect = 5
                self.kill()
                break

        #Remove if off screen
        if (self.rect.right < 0 or self.rect.left > 1500 or 
            self.rect.bottom < 0 or self.rect.top > 1000):
            self.kill()

class Shockwave(pygame.sprite.Sprite):
    def __init__(self,x,y,max_radius=200,speed=5,damage=20):
        super().__init__()
        self.max_radius = max_radius
        self.speed = speed 
        self.damage = damage
        self.current_radius = 10

        #create a suitable canva
        self.size = max_radius * 2 + 20
        self.image = pygame.Surface((self.size,self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x,y))
        self.hitbox = self.rect
        
        #to make sure the wave only will damage zombies one time only not five time
        #why: because when it touch zombies will have around 5 time damage so mark it for damge one time only.
        self.hit_zombies = set()

    def update(self):
        #slowly increate the radius to make the wave keep bigger
        self.current_radius += self.speed

        #if the radius bigger than the maximum radius skill disappear
        if self.current_radius >= self.max_radius:
            self.kill()
            return
        
        #clear the canva
        self.image.fill((0,0,0,0))

        #use ratio of (1 - current radius/biggest radius) calculate the transparency of Alpha(0-255) :0 is fully transparency, 255 is no transparency
        # this will make the wave very colourful when it came out and the bigger of the radius it increase the transparent it go
        alpha = max(0,int(255 *(1 - self.current_radius/self.max_radius)))

        #draw the effect for wave : lightblue colour ring (R,G,B, Alpha)
        center_pos = (self.size//2 , self.size//2)
        pygame.draw.circle(self.image, (0,191,255,alpha), center_pos, self.current_radius, 6) #6 is the thickness

        #Damage check
        for zombie in zombies_group:
            # Only calculate if this zombie hasn't been hit by the current wave before
            if zombie not in self.hit_zombies:
                #calculate  distance between the center of zombie and wave
                dx = zombie.rect.centerx - self.rect.centerx
                dy = zombie.rect.centery - self.rect.centery
                distance = (dx**2 + dy**2) ** 0.5
            
               #take damge when the zombie is right on the edge of a wave
                if distance <= self.current_radius + 20 and distance >= self.current_radius - 20:
                    zombie.health -= self.damage
                    print(f"Zombies hit by Shockwave! Health: {zombie.health}")
                    zombie.hit_effect = 5
                    self.hit_zombies.add(zombie) #mark as hit
    
#==============================================================================#
# Create sprite groups
all_sprites_list = pygame.sprite.Group()
zombies_group = pygame.sprite.Group()

# Create sprite (Player)
square = Player()
square.rect.x = 100
square.rect.y = 100
all_sprites_list.add(square)

# Function to spawn multiple zombies with better position checking
def spawn_zombies(num_normal=3, num_fast=0, num_armored=0,num_boss=0):
    # Spawn normal zombies
    for i in range(num_normal):
        zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
        # Spawn in valid positions (not inside obstacles)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 100:
            zombie.rect.x = random.randint(100, 1400)
            zombie.rect.y = random.randint(100, 800)
            zombie.hitbox.center = zombie.rect.center
            
            # Check collision with ALL obstacles
            collision = False
            for obstacle in obstacles:
                if zombie.hitbox.colliderect(obstacle):
                    collision = True
                    break
            if not collision:
                for inside_obstacle in inside_obstacles:
                    if zombie.hitbox.colliderect(inside_obstacle):
                        collision = True
                        break
            
            if not collision:
                valid_position = True
            attempts += 1
        
        zombies_group.add(zombie)
        all_sprites_list.add(zombie)
    
    # Spawn fast zombies
    for i in range(num_fast):
        fast_zombie = FasterZombie("FastZombie.png", scale=(90,90), speed=5, player=square)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 100:
            fast_zombie.rect.x = random.randint(100, 1400)
            fast_zombie.rect.y = random.randint(100, 800)
            fast_zombie.hitbox.center = fast_zombie.rect.center
            
            # Check collision with ALL obstacles
            collision = False
            for obstacle in obstacles:
                if fast_zombie.hitbox.colliderect(obstacle):
                    collision = True
                    break
            if not collision:
                for inside_obstacle in inside_obstacles:
                    if fast_zombie.hitbox.colliderect(inside_obstacle):
                        collision = True
                        break
            
            if not collision:
                valid_position = True
            attempts += 1
        
        zombies_group.add(fast_zombie)
        all_sprites_list.add(fast_zombie)
    
    for i in range(num_armored):
        armored_zombie = ArmoredZombie("Armored_Zombie.png", scale=(110,110), speed=1.5, player= square )
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 100:
            armored_zombie.rect.x = random.randint(100, 1400)
            armored_zombie.rect.y = random.randint(100, 800)
            armored_zombie.hitbox.center = armored_zombie.rect.center
            
            # Check collision with ALL obstacles
            collision = False
            for obstacle in obstacles:
                if armored_zombie.hitbox.colliderect(obstacle):
                    collision = True
                    break
            if not collision:
                for inside_obstacle in inside_obstacles:
                    if armored_zombie.hitbox.colliderect(inside_obstacle):
                        collision = True
                        break
            
            if not collision:
                valid_position = True
            attempts += 1
        
        zombies_group.add(armored_zombie)
        all_sprites_list.add(armored_zombie)


    for i in range(num_boss):
        boss_zombie = BossZombie("BossZombie.png", scale=(200,200), speed=5, player=square)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 100:
            boss_zombie.rect.x = random.randint(100, 1400)
            boss_zombie.rect.y = random.randint(100, 800)
            boss_zombie.hitbox.center = boss_zombie.rect.center
            
            # Check collision with ALL obstacles
            collision = False
            for obstacle in obstacles:
                if boss_zombie.hitbox.colliderect(obstacle):
                    collision = True
                    break
            if not collision:
                for inside_obstacle in inside_obstacles:
                    if boss_zombie.hitbox.colliderect(inside_obstacle):
                        collision = True
                        break
            
            if not collision:
                valid_position = True
            attempts += 1
        
        zombies_group.add(boss_zombie)
        all_sprites_list.add(boss_zombie)


# Spawn initial zombies (3 normal, 0 fast in first room, 1 armored)
spawn_zombies(3, 0, 1, 1)

# Main Menu
def show_menu():
    global window, background
    font_large = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 50)
    
    menu_running = True
    while menu_running:
        w_size = window.get_size()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                real_x, real_y = event.pos
                virtual_x = int(real_x * (game_width / w_size[0]))
                virtual_y = int(real_y * (game_height / w_size[1]))
                mouse_pos = (virtual_x, virtual_y)

                if start_button.collidepoint(mouse_pos):
                    return True
                if quit_button.collidepoint(mouse_pos):
                    return False
        
        background.blit(menu_background, (0, 0))
        
        # Title (centered) replaced with image
        zombs_scaled = pygame.transform.scale(zombs_image, (600, 200))
        zombs_rect = zombs_scaled.get_rect(center=(750, 200))
        background.blit(zombs_scaled, zombs_rect)
        
        # Start Button
        pygame.draw.rect(background, (0, 200, 0), start_button)
        start_text = font_button.render("START", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=start_button.center)
        background.blit(start_text, start_text_rect)
        
        # Quit Button
        pygame.draw.rect(background, (200, 0, 0), quit_button)
        quit_text = font_button.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        background.blit(quit_text, quit_text_rect)
        
        window.blit(background, (0, 0))
        pygame.display.flip()
        clock.tick(60)

# Button rectangles (centered)
start_button = pygame.Rect(600, 350, 300, 100)
quit_button = pygame.Rect(600, 500, 300, 100)

# Game loop
clock = pygame.time.Clock()
running = True
player_dead = False

# Death screen button rectangles
death_restart_button = pygame.Rect(450, 600, 200, 60)
death_quit_button = pygame.Rect(850, 600, 200, 60)

# Font for on-screen messages
message_font = pygame.font.Font(None, 36)
message_text = ""
message_timer = 0


#=============== while game running =================#
# Show menu first
if not show_menu():
    pygame.quit()
    exit()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                gate_is_open = not gate_is_open

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if player_dead:
                    # Handle death screen button clicks
                    mouse_pos = event.pos
                    if death_restart_button.collidepoint(mouse_pos):
                        player_dead = False
                        reset_game()
                    elif death_quit_button.collidepoint(mouse_pos):
                        running = False
                else:
                    square.attack(zombies_group, all_sprites_list)

    keys = pygame.key.get_pressed()
    
    # Store old position for collision
    old_x = square.rect.x
    old_y = square.rect.y
    old_hitbox_x = square.hitbox.x
    old_hitbox_y = square.hitbox.y

    speed = 10
    #===tap B to block======#
    if keys[pygame.K_b]:
        square.is_blocking = True
        square.update_image()
    else:
        square.is_blocking = False
        square.update_image()
        #put square.update_image() is for python know that I am not holding b so it will not stuck in the situasion keep blocking forever
    #============================#
    # Fireball key
    if keys[pygame.K_f]:
        square.cast_fireball(all_sprites_list)
    
    # Skill shockwave key:press V
    if keys[pygame.K_v]:
        square.cast_shockwave(all_sprites_list)





    # Sprint handling
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        if square.stamina > 0:
            speed = 20
            square.stamina -= 1
            print("stamina", round(square.stamina)) 
    else:
        square.regen_stamina()
    
    # Movement
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        square.moveLeft(speed)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        square.moveRight(speed)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        square.moveForward(speed)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        square.moveBack(speed)
    
    # PLAYER COLLISION DETECTION (using hitbox)
    collision = False
    
    # Check main obstacles with hitbox
    for obstacle in obstacles:
        if square.hitbox.colliderect(obstacle):
            collision = True
            break
    
    # Check inside obstacles with hitbox
    if not collision:
        for inside_obstacle in inside_obstacles:
            if square.hitbox.colliderect(inside_obstacle):
                collision = True
                break
    
    # If collision, revert position
    if collision:
        square.rect.x = old_x
        square.rect.y = old_y
        square.hitbox.x = old_hitbox_x
        square.hitbox.y = old_hitbox_y
    
    # Update gate state based on zombies in room
    gate_is_open = not are_zombies_in_room()
    
    # Room transition - only allow if no zombies in current room
    if square.rect.x >= 1500 - square.rect.width:
        if not are_zombies_in_room():
            room += 1
            square.rect.x = 100
            square.rect.y = 100
            
            # Change obstacles based on room
            inside_obstacles.clear()
            if room == 2:
                inside_obstacles.extend(original_inside_obstacles_room2)
                message_text = "Entering Room 2 - More zombies!"
                # Clear all existing zombies first
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                # Spawn more zombies in room 2: 5 normal, 2 fast
                spawn_zombies(5, 2)
            elif room == 1:
                inside_obstacles.extend(original_inside_obstacles_room1)
                message_text = "Entering Room 1"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(3, 0)
            elif room == 3:
                inside_obstacles.extend(original_inside_obstacles_room3)  # Empty list - no obstacles
                message_text = "Entering Room 3 - No obstacles! More zombies!"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                # Spawn even more zombies in room 3: 7 normal, 3 fast
                spawn_zombies(7, 3)
            else:
                inside_obstacles.extend(original_inside_obstacles_room2)
                message_text = f"Entering Room {room}"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(4, 1)
            
            message_timer = pygame.time.get_ticks()
        else:
            message_text = f"Defeat {len(zombies_group)} zombies before proceeding!"
            message_timer = pygame.time.get_ticks()
            square.rect.x = old_x
            square.hitbox.x = old_hitbox_x
            
    if square.rect.x < 1:
        if not are_zombies_in_room():
            room -= 1 
            square.rect.x = 1300
            square.rect.y = 100
            
            # Change obstacles based on room
            inside_obstacles.clear()
            if room == 1:
                inside_obstacles.extend(original_inside_obstacles_room1)
                message_text = "Returned to Room 1"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, ArmoredZombie,BossZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(3, 0)
            elif room == 2:
                inside_obstacles.extend(original_inside_obstacles_room2)
                message_text = "Entering Room 2"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie,ArmoredZombie,BossZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(5, 2)
            elif room == 3:
                inside_obstacles.extend(original_inside_obstacles_room3)
                message_text = "Entering Room 3 - No obstacles!"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie,ArmoredZombie, BossZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(7, 3)
            else:
                inside_obstacles.extend(original_inside_obstacles_room2)
                message_text = f"Entering Room {room}"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(4, 1)
            
            message_timer = pygame.time.get_ticks()
        else:
            message_text = f"Defeat {len(zombies_group)} zombies before proceeding!"
            message_timer = pygame.time.get_ticks()
            square.rect.x = old_x
            square.hitbox.x = old_hitbox_x
    
    # Check if player is dead
    if square.health <= 0 and not player_dead:
        print("Player died! Showing death screen...")
        player_dead = True
    
    
    # Update all sprites
    all_sprites_list.update()

    # Open gate automatically when all zombies are gone
    if len(zombies_group) == 0:
        gate_is_open = True
    
    # Clear background based on room
    if room == 1:
        background.fill(GREEN)
    elif room == 2:
        background.fill(blue)    
    elif room == 3:
        background.fill(black)
    
    # health and stamina bar  
    health_width = int((square.health / 100) * 196)
    pygame.draw.rect(background, RED, (30, 100, health_width, 35))
    
    stamina_width = int((square.stamina / 100) * 196)
    pygame.draw.rect(background, blue, (290, 108, stamina_width, 20))

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(background, (0, 0, 0), obstacle)
    
    # Draw inside obstacles - BLACK for room 2, NONE for room 3, BLUE for room 1
    for inside_obstacle in inside_obstacles:
        if room == 2:
            pygame.draw.rect(background, black, inside_obstacle)
        elif room == 3:
            # No obstacles to draw in room 3
            pass
        else:
            pygame.draw.rect(background, (0, 0, 150), inside_obstacle)
    
    draw_gate(background, gate_rect, gate_is_open)

    # Draw UI (just the images, no numbers)
    background.blit(healthui_image, (0, 85))
    background.blit(staminaui_image, (260,101))
    # Draw cooldowns for abilities
    current_time = pygame.time.get_ticks()

    fireball_cooldown_remaining = square.fireball_cooldown - (current_time - square.last_fireball_time)
    if fireball_cooldown_remaining > 0:
        fireball_cooldown_text = message_font.render(f"{fireball_cooldown_remaining / 1000:.1f}", True, (255, 255, 255))
        fireball_cooldown_rect = fireball_cooldown_text.get_rect(topleft=(530, 115))
        background.blit(fireball_cooldown_text, fireball_cooldown_rect)
    else:
        background.blit(fireui_image, (525, 101))

    shockwave_cooldown_remaining = square.shockwave_cooldown - (current_time - square.last_shockwave_time)
    if shockwave_cooldown_remaining > 0:
        shockwave_cooldown_text = message_font.render(f"{shockwave_cooldown_remaining / 1000:.1f}", True, (255, 255, 255))
        shockwave_cooldown_rect = shockwave_cooldown_text.get_rect(topleft=(600, 115))
        background.blit(shockwave_cooldown_text, shockwave_cooldown_rect)
    else:
        background.blit(waveui_image, (595, 101))
    
    # Draw on-screen message if active
    if message_timer > 0 and pygame.time.get_ticks() - message_timer < 2000:
        message_surface = message_font.render(message_text, True, (255, 255, 0))
        message_rect = message_surface.get_rect(center=(game_width // 2, 50))
        background.blit(message_surface, message_rect)
    else:
        message_timer = 0
    
    # Draw on-screen message if active
    if message_timer > 0 and pygame.time.get_ticks() - message_timer < 2000:
        message_surface = message_font.render(message_text, True, (255, 255, 0))
        message_rect = message_surface.get_rect(center=(game_width // 2, 50))
        background.blit(message_surface, message_rect)
    else:
        message_timer = 0
    
    # Draw sprites
    all_sprites_list.draw(background)

    # Draw zombie health bars above each zombie
    for zombie in zombies_group:
        if zombie.health > 0 and zombie.max_health > 0:
            bar_width = 60
            bar_height = 6
            bar_x = zombie.rect.centerx - bar_width // 2
            bar_y = zombie.rect.top - 10
            health_ratio = max(0, zombie.health / zombie.max_health)

            pygame.draw.rect(background, (0, 0, 0), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            pygame.draw.rect(background, (220, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(background, (0, 220, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
    
    # Draw GGs and buttons if player is dead
    if player_dead:
        ggs_scaled = pygame.transform.scale(ggs_image, (600, 400))
        ggs_rect = ggs_scaled.get_rect(center=(750, 350))
        background.blit(ggs_scaled, ggs_rect)

        kill_count_text = message_font.render(f"Zombies Killed: {zombies_killed}", True, (255, 255, 255))
        kill_count_rect = kill_count_text.get_rect(midtop=(750, 750))
        background.blit(kill_count_text, kill_count_rect)
        
        # Draw death screen buttons
        ##!!!! Sorry haozheng  for: I need to delete this  and change font_button to message_font  
        # this is what I delete #font_button = pygame.font.Font(None, 40)
        # if after you fix it already and you still want to use font_button you can do it ,this just a temporary change
        pygame.draw.rect(background, (0, 200, 0), death_restart_button)
        restart_text = message_font.render("RESTART", True, (0, 0, 0))
        restart_text_rect = restart_text.get_rect(center=death_restart_button.center)
        background.blit(restart_text, restart_text_rect)
        
        pygame.draw.rect(background, (200, 0, 0), death_quit_button)
        quit_text = message_font.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=death_quit_button.center)
        background.blit(quit_text, quit_text_rect)
    
    #able to scale window
    window.blit(background, (0, 0)) 
    pygame.display.flip()
    clock.tick(60)
#===============================================#
pygame.quit()