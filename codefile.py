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
menu_background = pygame.image.load("Menu1600.png").convert()
zombs_image = pygame.image.load("zombs.png").convert_alpha()
ggs_image = pygame.image.load("GGs.png").convert_alpha()





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

def draw_gate(surface, rect, is_open):
    pygame.draw.rect(surface, (90, 90, 90), rect)

    if not is_open:
        for y in range(rect.top + 8, rect.bottom - 8, 20):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))
    else:
        for y in range(rect.top + 5, rect.top + 20, 12):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))
        for y in range(rect.bottom - 20, rect.bottom - 5, 12):
            pygame.draw.rect(surface, (20, 20, 20), (rect.left + 5, y, rect.width - 10, 4))


# definition of reset game
def reset_game():
    global square, room
    room = 1
    all_sprites_list.empty() # clear all the sprites
    zombies_group.empty()    # clear previous zombies
    
    square = Player()        # again to be a player
    square.rect.x = 100
    square.rect.y = 100
    #manual centering hitbox of player
    square.hitbox.center = square.rect.center 
    all_sprites_list.add(square)
    spawn_zombies(3,2)#spawn 3 normal zombie and 2 fast zombie

 

    
# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #Load player image
        player_size = (100,100)  # Changed to 100x100 for better collision
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
        self.hitbox = self.rect.inflate(-20, -20)  # 100x100 -> 80x80 hitbox
        
        self.health = 100
        self.stamina = 100
        self.last_regen_time = pygame.time.get_ticks()
        self.regen_delay = 1000
        
        self.is_blocking = False #Track if player is holding the block button
    

    def regen_stamina(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_regen_time >= self.regen_delay:
            if self.stamina < 100:
                self.stamina += 10
                print("Stamina", self.stamina)
            self.last_regen_time = current_time
                

    def moveRight(self, pixels):
        if self.is_blocking: return #Freeze position if blocking
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

        #Damage zombie in range - Use hitbox for better combat
        for zombie in zombies_group:
            if slash.rect.colliderect(zombie.rect):
                zombie.health -= 10
                print("Zombie hit! Health", zombie.health)
    
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
        self.update_image() #make sure every frame of block have been updated

    def update_image(self):        
        base_img = self.images[self.facing].copy()
        
        #2. hold b will have a semi-transparent circular shield
        if self.is_blocking:
            #create a canvas the same size
            shield_surface = pygame.Surface(base_img.get_size(), pygame.SRCALPHA)
            
            #Draw a semi-transparent sky blue circular cover inner ring (Color: Sky Blue, Opacity: 100)
            pygame.draw.circle(shield_surface, (0, 191, 255, 100), (50, 50), 48)  
            # Draw the edge boundary of a bright purple circle (Color: bright purple, Line width: 4)
            pygame.draw.circle(shield_surface, (138, 43, 226, 225), (50, 50), 48, 4) 
            
            # Blit the shield canvas onto the character layer
            base_img.blit(shield_surface, (0, 0))
            
        
        self.image = base_img
            

class Zombie(pygame.sprite.Sprite):
    def __init__(self, image_file, scale=(100,100), speed=2, player=None):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.player = player
        self.health = 100

        #Cooldown for attacks
        self.attack_cooldown = 1000
        self.last_attack_time = 0
        
        # Hitbox for zombie (slightly smaller for better movement)
        self.hitbox = self.rect.inflate(-20, -20)
    
    def update(self):
        # If zombie is dead, remove it
        if self.health <= 0:
            self.kill()
            return

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
                #1. Try moving in X direction first
                self.hitbox.x += int(self.speed * dx/distance)
                # Check collision with obstacles
                if check_collision_with_obstacles(self):
                    self.hitbox.x = old_x # Undo X movement
                    
                
                #2. Try moving in Y direction
                self.hitbox.y += int(self.speed * dy/distance)
                
                
                # Check collision with obstacles
                if check_collision_with_obstacles(self):
                    self.hitbox.y = old_y  # Undo Y movement
                    
                #3. Apply position to render image
                self.rect.center = self.hitbox.center

            # Attack if touching player
            if self.rect.colliderect(self.player.rect):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    if self.player.is_blocking:
                        damage_taken = 10 * 0.10  # 10% of 10 base damage = 1 damage
                        self.player.health -= damage_taken
                        print(f"Attack Blocked! Only took 10% damage ({damage_taken}). Player Health: {self.player.health}")
                    else:
                        self.player.health -= 10
                        print("Player hit! Full damage taken. Health:", self.player.health)
                    self.last_attack_time = current_time

class FasterZombie(Zombie):
    def __init__(self,image_file,scale=(90,90),speed=5,player=None):
        super().__init__(image_file,scale,speed,player)
        self.health = 60

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

#special skill for player class
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=15, damage=30):
        super().__init__()
        base_image = pygame.image.load("fireball.png").convert_alpha()
        base_image = pygame.transform.scale(base_image, (100,100))  # Smaller fireball

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

        #if collison with wall it will gone
        if check_collision_with_obstacles(self):
            self.kill()
            return
        
        #Check collision with zombies
        for zombie in zombies_group:
            if self.rect.colliderect(zombie.rect):
                zombie.health -= self.damage
                print("Zombie hit by fireball! Health:", zombie.health)
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

# Function to spawn multiple zombies
def spawn_zombies(num_normal=3,num_faster=2):
    for i in range(num_normal):
        zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
        # Spawn in valid positions (not inside obstacles)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 50:
            zombie.rect.x = random.randint(100, 1400)
            zombie.rect.y = random.randint(100, 900)
            zombie.hitbox.center = zombie.rect.center
            if not check_collision_with_obstacles(zombie):
                valid_position = True
            attempts += 1
        
        zombies_group.add(zombie)
        all_sprites_list.add(zombie)
    
    for i in range(num_faster):
        fast_zombie = FasterZombie("FastZombie.png", scale=(90,90), speed=5, player=square)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 50:
            fast_zombie.rect.x = random.randint(100,1400)
            fast_zombie.rect.y = random.randint(100,900)
            fast_zombie.hitbox.center = fast_zombie.rect.center
            if not check_collision_with_obstacles(fast_zombie):
                valid_position = True
            attempts += 1
        
        zombies_group.add(fast_zombie)
        all_sprites_list.add(fast_zombie)

# Spawn initial zombies
spawn_zombies(3,2)

# Main Menu
def show_menu():
    global window,background
    font_large = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 50)
    
    menu_running = True
    while menu_running:
        w_size = window.get_size()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 
                real_x, real_y = event.pos
                virtual_x = int(real_x * (game_width / w_size[0]))
                virtual_y = int(
                    real_y * (game_height / w_size[1])
                )
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
        
        #put menu on the screen
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


# Show menu first
if not show_menu():
    pygame.quit()
    exit()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)

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
    
    # Room transition
    if square.rect.x >= 1500 - square.rect.width:
        room += 1
        square.rect.x = 100
        square.rect.y = 100
    if square.rect.x < 1:
        room -= 1 
        square.rect.x = 1300
        square.rect.y = 100
    
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
    
    for inside_obstacle in inside_obstacles:
        pygame.draw.rect(background, (0, 0, 150), inside_obstacle)
    
    draw_gate(background, gate_rect, gate_is_open)

    # Draw UI
    background.blit(healthui_image, (0, 85))
    background.blit(staminaui_image, (260,101))
    fireui_x = 260 + staminaui_image.get_width() + 10
    # Hide fire UI while a fireball exists
    has_fireball = any(isinstance(s, Fireball) for s in all_sprites_list)
    if not has_fireball:
        background.blit(fireui_image, (fireui_x, 101))
    
    # Draw sprites
    all_sprites_list.draw(background)
    
    # Draw GGs and buttons if player is dead
    if player_dead:
        ggs_scaled = pygame.transform.scale(ggs_image, (600, 400))
        ggs_rect = ggs_scaled.get_rect(center=(750, 350))
        background.blit(ggs_scaled, ggs_rect)
        
        # Draw death screen buttons
        font_button = pygame.font.Font(None, 40)
        pygame.draw.rect(background, (0, 200, 0), death_restart_button)
        restart_text = font_button.render("RESTART", True, (0, 0, 0))
        restart_text_rect = restart_text.get_rect(center=death_restart_button.center)
        background.blit(restart_text, restart_text_rect)
        
        pygame.draw.rect(background, (200, 0, 0), death_quit_button)
        quit_text = font_button.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=death_quit_button.center)
        background.blit(quit_text, quit_text_rect)
    
    #able to scale window
    window.blit(background, (0, 0)) 
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()