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
menu_background = pygame.image.load("Menu.png").convert()

# Colors
GREEN = (0,100,0)
SURFACE_COLOR = (167, 255, 100)
RED = (200, 0, 0)
black = (0,0,0)
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
        # Add a red lock indicator when zombies are present
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
    global square, room, inside_obstacles
    room = 1
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

# Sprite Class
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

    def update_image(self):        
        base_img = self.images[self.facing].copy()
        
        # Flash effect when invincible
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            base_img.set_alpha(128)
        
        # hold b will have a semi-transparent circular shield
        if self.is_blocking:
            shield_surface = pygame.Surface(base_img.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 191, 255, 100), (50, 50), 48)  
            pygame.draw.circle(shield_surface, (138, 43, 226, 225), (50, 50), 48, 4) 
            base_img.blit(shield_surface, (0, 0))
        
        self.image = base_img

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

        #Cooldown for attacks
        self.attack_cooldown = 1000
        self.last_attack_time = 0
        
        # Hitbox for zombie (slightly smaller for better movement)
        self.hitbox = self.rect.inflate(-15, -15)
        self.hit_effect = 0
    
    def update(self):
        # If zombie is dead, remove it
        if self.health <= 0:
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
                            self.player.health -= 10
                            print(f"Player hit! Health: {self.player.health}")
                        self.player.make_invincible(1000)
                        self.last_attack_time = current_time

class FasterZombie(Zombie):
    def __init__(self, image_file, scale=(90,90), speed=5, player=None):
        super().__init__(image_file, scale, speed, player)
        self.health = 60

class Attack(pygame.sprite.Sprite):
    def __init__(self, player, duration=200):
        super().__init__()
        #Load slash      
        self.original_image = pygame.image.load("slash2.png").convert_alpha()
        #Scale the image
        self.original_image = pygame.transform.scale(self.original_image, (120,120))

        #Position of the slash based on player facing
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

#special skill for player class
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

# Create sprite groups
all_sprites_list = pygame.sprite.Group()
zombies_group = pygame.sprite.Group()

# Create sprite (Player)
square = Player()
square.rect.x = 100
square.rect.y = 100
all_sprites_list.add(square)

# Function to spawn multiple zombies with better position checking
def spawn_zombies(num_normal=3, num_fast=0):
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
        fast_zombie = FasterZombie("Zombie1.png", scale=(90,90), speed=5, player=square)
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

# Spawn initial zombies (3 normal, 0 fast in first room)
spawn_zombies(3, 0)

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
        
        # Title (centered)
        title = font_large.render("ZOMBIE SLAYER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(750, 200))
        background.blit(title, title_rect)
        
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

# Font for on-screen messages
message_font = pygame.font.Font(None, 36)
message_text = ""
message_timer = 0

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                square.attack(zombies_group, all_sprites_list)

    keys = pygame.key.get_pressed()
    
    # Store old position for collision
    old_x = square.rect.x
    old_y = square.rect.y
    old_hitbox_x = square.hitbox.x
    old_hitbox_y = square.hitbox.y

    speed = 10
    # tap B to block
    if keys[pygame.K_b]:
        square.is_blocking = True
        square.update_image()
    else:
        square.is_blocking = False
        square.update_image()
    
    # Fireball key
    if keys[pygame.K_f]:
        square.cast_fireball(all_sprites_list)
    
    # Sprint handling
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        if square.stamina > 0:
            speed = 20
            square.stamina -= 1
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
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(3, 0)
            elif room == 2:
                inside_obstacles.extend(original_inside_obstacles_room2)
                message_text = "Entering Room 2"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
                        sprite.kill()
                spawn_zombies(5, 2)
            elif room == 3:
                inside_obstacles.extend(original_inside_obstacles_room3)
                message_text = "Entering Room 3 - No obstacles!"
                zombies_group.empty()
                for sprite in all_sprites_list:
                    if isinstance(sprite, (Zombie, FasterZombie, Attack, Fireball)):
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
    if square.health <= 0:
        print("Player died! Restarting game...")
        reset_game()
        message_text = "Game Reset! Defeat all zombies to proceed!"
        message_timer = pygame.time.get_ticks()
    
    # Update all sprites
    all_sprites_list.update()
    
    # Clear background based on room
    if room == 1:
        background.fill(GREEN)
    elif room == 2:
        background.fill(blue)    
    elif room == 3:
        background.fill(RED)  # Room 3 has RED background
    elif room >= 4:
        background.fill((255, 100, 100))  # Lighter red for rooms beyond 3
    else:
        background.fill((50, 50, 100))
    
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
    
    # Draw on-screen message if active
    if message_timer > 0 and pygame.time.get_ticks() - message_timer < 2000:
        message_surface = message_font.render(message_text, True, (255, 255, 0))
        message_rect = message_surface.get_rect(center=(game_width // 2, 50))
        background.blit(message_surface, message_rect)
    else:
        message_timer = 0
    
    # Draw sprites
    all_sprites_list.draw(background)
    
    window.blit(background, (0, 0)) 
    pygame.display.flip()
    clock.tick(60)

pygame.quit()