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
black = (0,0,0)
blue = (0,0,150)
purple = (100,0,100)
room = 1

# FUNCTION TO GET ROOM-SPECIFIC OBSTACLES
def get_room_obstacles(room_number):
    """Return obstacles based on current room number"""
    
    # Walls that exist in every room (boundary walls)
    walls = [
        pygame.Rect(0, 1, 30, 1000),      # left wall
        pygame.Rect(1, 60, 1500, 30),     # top wall 
        pygame.Rect(10, 900, 1500, 30),   # bottom wall 
        pygame.Rect(1480, 600, 30, 700),  # right bottom wall
        pygame.Rect(1480, 80, 30, 350),   # right top wall     
    ]
    
    # Different inner obstacles for each room
    if room_number == 1:
        # Room 1: Original obstacles (full of obstacles)
        inner = [
            pygame.Rect(380, 200, 50, 300),
            pygame.Rect(500, 600, 300, 50),
            pygame.Rect(715, 650, 85, 70),
            pygame.Rect(1000, 410, 95, 470),
            pygame.Rect(820, 830, 200, 50),
            pygame.Rect(795, 400, 300, 80),
            pygame.Rect(410, 200, 530, 50),
            pygame.Rect(1100, 200, 150, 40),
            pygame.Rect(1250, 200, 40, 150),
            pygame.Rect(1250, 700, 90, 100),
        ]
    elif room_number == 2:
        # Room 2: NO OBSTACLES (empty room!)
        inner = []
    elif room_number == 3:
        # Room 3: Different obstacle pattern
        inner = [
            pygame.Rect(500, 500, 500, 30),   # horizontal platform
            pygame.Rect(800, 300, 30, 400),   # vertical pillar
            pygame.Rect(200, 700, 100, 100),  # small box
            pygame.Rect(1200, 200, 100, 100), # top right box
            pygame.Rect(1100, 750, 150, 50),  # bottom platform
        ]
    else:
        # Any additional rooms default to empty
        inner = []
    
    return walls, inner

# Initialize obstacles from room 1
obstacles, inside_obstacles = get_room_obstacles(room)

# COLLISION HELPER FUNCTION
def check_collision_with_obstacles(sprite):
    """Check if a sprite collides with any obstacle"""
    for obstacle in obstacles:
        if sprite.rect.colliderect(obstacle):
            return True
    for inside_obstacle in inside_obstacles:
        if sprite.rect.colliderect(inside_obstacle):
            return True
    return False

# definition of reset game
def reset_game():
    global square, all_sprites_list, zombies_group, room, obstacles, inside_obstacles
    room = 1
    
    # Reset obstacles for room 1
    obstacles, inside_obstacles = get_room_obstacles(room)

    # Reset sprite groups
    all_sprites_list = pygame.sprite.Group()
    zombies_group = pygame.sprite.Group()

    # New player
    square = Player()
    square.rect.x = 100
    square.rect.y = 100
    all_sprites_list.add(square)

    # Spawn new zombies
    spawn_zombies(3)

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
        
        # HITBOX SYSTEM - Smaller than visual sprite for better movement
        self.hitbox = self.rect.inflate(-20, -20)  # 100x100 -> 80x80 hitbox
        
        self.health = 100
        self.stamina = 100
        self.last_regen_time = pygame.time.get_ticks()
        self.regen_delay = 1000

    def update(self):
        # Keep hitbox centered on visual sprite
        self.hitbox.center = self.rect.center
        self.regen_stamina()

    def regen_stamina(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_regen_time >= self.regen_delay:
            if self.stamina < 100:
                self.stamina += 10
            self.last_regen_time = current_time

    def moveRight(self, pixels):
        self.rect.x += pixels
        self.hitbox.x += pixels
        self.facing = "right"
        self.update_image()

    def moveLeft(self, pixels):
        self.rect.x -= pixels
        self.hitbox.x -= pixels
        self.facing = "left"
        self.update_image()

    def moveForward(self, speed):
        self.rect.y -= speed
        self.hitbox.y -= speed
        self.facing = "up"
        self.update_image()

    def moveBack(self, speed):
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
            if self.hitbox.colliderect(zombie.rect):
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

    def update_image(self):
        self.image = self.images[self.facing]

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
        self.hitbox = self.rect.inflate(-10, -10)
    
    def update(self):
        # If zombie is dead, remove it
        if self.health <= 0:
            self.kill()
            return

        # Move toward player
        if self.player:
            # Store old position
            old_x = self.rect.x
            old_y = self.rect.y
            
            # Calculate direction to player
            dx = self.player.rect.x - self.rect.x
            dy = self.player.rect.y - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance != 0:
                # Try moving in X direction first
                self.rect.x += self.speed * dx/distance
                self.hitbox.x = self.rect.x
                
                # Check collision with obstacles
                if check_collision_with_obstacles(self):
                    self.rect.x = old_x  # Undo X movement
                    self.hitbox.x = old_x
                
                # Try moving in Y direction
                self.rect.y += self.speed * dy/distance
                self.hitbox.y = self.rect.y
                
                # Check collision with obstacles
                if check_collision_with_obstacles(self):
                    self.rect.y = old_y  # Undo Y movement
                    self.hitbox.y = old_y

            # Attack if touching player
            if self.rect.colliderect(self.player.rect):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    self.player.health -= 10
                    print("Player hit! Health:", self.player.health)
                    self.last_attack_time = current_time

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

    def update(self):
        #move fireball
        self.rect.x += int(self.direction[0] * self.speed)
        self.rect.y += int(self.direction[1] * self.speed)

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
def spawn_zombies(num_zombies=5):
    for i in range(num_zombies):
        zombie = Zombie("Zombie1.png", scale=(100,100), player=square)
        # Spawn in valid positions (not inside obstacles)
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 50:
            zombie.rect.x = random.randint(100, 1400)
            zombie.rect.y = random.randint(100, 900)
            zombie.hitbox.x = zombie.rect.x
            zombie.hitbox.y = zombie.rect.y
            if not check_collision_with_obstacles(zombie):
                valid_position = True
            attempts += 1
        
        zombies_group.add(zombie)
        all_sprites_list.add(zombie)

# Spawn initial zombies
spawn_zombies(3)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
    
    # Room transition (right edge)
    if square.rect.x >= 1500 - square.rect.width:
        room += 1
        square.rect.x = 100
        square.rect.y = 100
        # Load new room's obstacles
        obstacles, inside_obstacles = get_room_obstacles(room)
        print(f"Entered Room {room}")  # Debug message
    
    # Room transition (left edge)
    if square.rect.x < 1:
        room -= 1 
        square.rect.x = 1300
        square.rect.y = 100
        # Load new room's obstacles
        obstacles, inside_obstacles = get_room_obstacles(room)
        print(f"Entered Room {room}")  # Debug message
    
    # Check if player is dead
    if square.health <= 0:
        print("Player died! Restarting game...")
        reset_game()
    
    # Update all sprites
    all_sprites_list.update()
    
    # Clear background based on room
    if room == 1:
        background.fill(GREEN)
    elif room == 2:
        background.fill(blue)    
    elif room == 3:
        background.fill(purple)
    else:
        background.fill(black)  # Default for other rooms
    
    # Draw obstacles (walls)
    for obstacle in obstacles:
        pygame.draw.rect(background, (0, 0, 0), obstacle)
    
    # Draw inside obstacles
    for inside_obstacle in inside_obstacles:
        pygame.draw.rect(background, (0, 0, 150), inside_obstacle)
    
    # Draw sprites
    all_sprites_list.draw(background)
    
    # DEBUG: Draw hitboxes (uncomment if needed)
    # pygame.draw.rect(background, (255, 0, 0), square.hitbox, 2)  # Player hitbox (red)
    # for zombie in zombies_group:
    #     pygame.draw.rect(background, (255, 255, 0), zombie.rect, 2)  # Zombie hitbox (yellow)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()