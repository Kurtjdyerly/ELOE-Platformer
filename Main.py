# intial Code from https://docs.replit.com/tutorials/python/2d-platform-game
import pygame, numpy, sound, sys
from map import Tile, TileMap, Spritesheet, Map
WIDTH = 800
HEIGHT = 600
BACKGROUND = (0, 0, 0)
INVISIBLE_WALL_WIDTH = 10



class Sprite(pygame.sprite.Sprite): # Superclass for Sprites
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite): # Player Sprite
    def __init__(self, startx, starty):
        super().__init__("./Assets/p1_front.png", startx, starty) # Initiliazes with starting image
        height = 70
        width = 70
        self.is_alive = True
        self.has_won = False
        self.image = pygame.transform.scale(self.image, (width, height))
        self.stand_image = pygame.image.load("./Assets/p1_front.png")
        self.stand_image = pygame.transform.scale(self.stand_image, (width, height)) # Scale down the image

        self.jump_image = pygame.image.load("./assets/p1_front.png")
        self.jump_image = pygame.transform.scale(self.jump_image, (width, height)) # Scale down the image

        self.walk_cycle = [pygame.image.load(f"./assets/p1_walk{i:0>2}.png") for i in range(1, 12)]
        self.walk_cycle = [pygame.transform.scale(image, (width, height)) for image in self.walk_cycle]
        
        self.animation_index = 0
        self.facing_left = False

        self.rect = self.stand_image.get_rect()
        
        self.rect.center = (startx, starty)

        self.speed = 10
        self.jumpspeed = 20
        self.vsp = 0 # Vertical Speed
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False) # Transforms the images to face left

        if self.animation_index < len(self.walk_cycle)-1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, environment, enemies, goal):
        hsp = 0 # Horizontal Speed
        onground = self.check_collision(0, 1, environment)
        
        # check keys
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.facing_left = True
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:
            self.facing_left = False
            self.walk_animation()
            hsp = self.speed
        else:
            self.image = self.stand_image

        if key[pygame.K_UP] and onground:
            self.vsp = -self.jumpspeed

        # variable height jumping
        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.vsp < -self.min_jumpspeed:
                self.vsp = -self.min_jumpspeed

        self.prev_key = key

        # gravity
        if self.vsp < 10 and not onground:  # 9.8 rounded up
            self.jump_animation()
            self.vsp += self.gravity

        if onground and self.vsp > 0: # Cancels vertical movement when landing
            self.vsp = 0


        # movement
        self.move(hsp, self.vsp, environment, enemies, goal)
        
        enemy_collision = pygame.sprite.spritecollideany(self, enemies)
        goal_collision = pygame.sprite.spritecollideany(self, goal)
        if enemy_collision: # Kills player on collision with enemy sprite
            self.is_alive = False
            print("Player died!")
        
        if goal_collision:
            self.has_won = True
        

    def move(self, x, y, environment, enemies, goal):
        dx = x
        dy = y
        dxPlayer = 0
        
        if (dx > 0 and self.rect.x < (WIDTH - (WIDTH / 2))):
            dxPlayer = dx
            dx = 0 
        elif (dx < 0 and self.rect.x > WIDTH / 4):
            dxPlayer = dx
            dx = 0
        

        while self.check_collision(0, dy, environment):
            dy -= numpy.sign(dy)

        
        while self.check_collision((dxPlayer + dx), dy, environment):
            dx -= numpy.sign(dx)
            dxPlayer -= numpy.sign(dxPlayer)

        for sprite in environment.sprites(): # Iterate through sprites to move them
            sprite.rect.x -= dx
            sprite.rect.y -= dy
        for sprite in enemies.sprites():
            sprite.rect.x -= dx
            sprite.rect.y -= dy
        for sprite in goal.sprites(): # Iterate through sprites to move them
            sprite.rect.x -= dx
            sprite.rect.y -= dy
        # dxPlayer = (dx * (numpy.sin( self.rect.x *((4 * numpy.pi) / WIDTH))))
        # if(WIDTH / 4 < self.rect.x < (3 * WIDTH / 4)):
        #     dxPlayer = -(dx * (numpy.sin( self.rect.x/WIDTH *(4 * numpy.pi))))
        # else:
        #     dxPlayer = (dx * (numpy.sin( self.rect.x/WIDTH *((4 * numpy.pi) / WIDTH))))
        self.rect.move_ip([dxPlayer, 0])  

       
    def check_collision(self, x, y, grounds):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, grounds)
        self.rect.move_ip([-x, -y])
        return collide
    
class Goal(Sprite):
    def __init__(self, image, startx, starty, width = 70, height = 70):
        super().__init__(image, startx, starty)
        self.image = pygame.transform.scale(self.image, (width, height))
    
class Enemy(Sprite): # Enemy Sprites
    def __init__(self, startx, starty, width = 50, height = 50):
        super().__init__("./Assets/enemy_sprite.png", startx, starty)
        self.image = pygame.transform.scale(self.image, (width,height))
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left

    def create_invisible_walls(self, environment):
    # Check if there are no visible walls or screen edges within 5 spaces of enemy's spawn point
        if not any(isinstance(sprite, Box) for sprite in environment.sprites()) or \
                self.rect.left > WIDTH - 5 or self.rect.right < 5:
            # Create invisible walls
            invisible_wall_left = Box(self.rect.left - INVISIBLE_WALL_WIDTH, self.rect.top,
                                        INVISIBLE_WALL_WIDTH, self.rect.height)
            invisible_wall_right = Box(self.rect.right, self.rect.top,
                                        INVISIBLE_WALL_WIDTH, self.rect.height)
            environment.add(invisible_wall_left)
            environment.add(invisible_wall_right)

    def update(self, boxes):
        self.rect.x += self.speed * self.direction
        # Reverse direction if reaching boundaries
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
        
        collision_list = pygame.sprite.spritecollide(self, boxes, False)
        for box in collision_list:
            # Collision handling
            # For example, you can change the enemy's direction upon collision
            self.direction *= -1  # Reverse direction


        
def game_loop(screen, clock):
    player = Player(WIDTH / 2, HEIGHT / 2)
    enemies = pygame.sprite.Group()

    map_filename = "map.csv"
    spritesheet = Spritesheet()  # Create an instance of Spritesheet
    my_map = Map(map_filename)
    tile_map = TileMap(spritesheet, my_map.stitch_map())
    tile_map.load_map()
    environment = tile_map.tiles
    goal = tile_map.end_goal


    # environment = pygame.sprite.Group()
    # for bx in range(-10000, 10000, 70):
    #     environment.add(Box(bx, 400))
 
    # environment.add(Box(330, 230))
    # environment.add(Box(400, 70))

    sound.sound()
    print("Game initialized!")

    while True:
        pygame.event.pump()
                # Handle pause key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
                pause_menu(screen)




        player.update(environment, enemies, goal)
        enemies.update(environment)
        goal.update()

        if not player.is_alive:
            if game_over_screen(screen):
                # Restart the game
                player.is_alive = True
                player.rect.center = [WIDTH / 2, HEIGHT / 2]
            else:
                return  
        
        if player.has_won:
            if win_screen(screen):
                player.has_won = False
                player.rect.center = [WIDTH / 2, HEIGHT / 2]
            else:
                return
        
        screen.fill(BACKGROUND)
        player.draw(screen)
        enemies.draw(screen)
        environment.draw(screen)
        goal.draw(screen)

        pygame.display.flip()

        clock.tick(60)

def title_screen(screen):
    screen.fill(BACKGROUND)
    font = pygame.font.Font(None, 36)
    title_text = font.render("E.L.O.E.", True, (255, 255, 255))
    start_text = font.render("Press 'S' to start", True, (255, 255, 255))
    controls_text = font.render("Press 'C' for controls", True, (255, 255, 255))
    quit_text = font.render("Press 'Q' to quit", True, (255, 255, 255))

    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))
    screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 350))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 400))

    pygame.display.flip()

def pause_menu(screen):
    screen.fill(BACKGROUND)
    font = pygame.font.Font(None, 36)
    pause_text = font.render("Game Paused", True, (255, 255, 255))
    resume_text = font.render("Press 'R' to resume", True, (255, 255, 255))
    try_again_text = font.render("Press 'T' to try again", True, (255, 255, 255))
    quit_text = font.render("Press 'Q' to quit", True, (255, 255, 255))

    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 200))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, 300))
    screen.blit(try_again_text, (WIDTH // 2 - try_again_text.get_width() // 2, 350))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 400))

    pygame.display.flip()

    while True:
        pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_t:
                    clock = pygame.time.Clock()
                    game_loop(screen, clock)
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                
def show_controls(screen):
    font = pygame.font.Font(None, 36)
    title_text = font.render("Controls", True, (255, 255, 255))
    back_text = font.render("Press 'B' to go back", True, (255, 255, 255))
    controls_text = [
        font.render("Arrow keys: Move", True, (255, 255, 255)),
        font.render("Up arrow: Jump", True, (255, 255, 255)),
        font.render("S: Start game", True, (255, 255, 255)),
        font.render("Q: Quit game", True, (255, 255, 255))
    ]

    screen.fill(BACKGROUND)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    y_offset = 200
    for text in controls_text:
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 50

    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 500))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    # Go back to the title screen
                    title_screen(screen)
                    return

def game_over_screen(screen):
    screen.fill(BACKGROUND)
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    try_again_text = font.render("Press 'T' to try again", True, (255, 255, 255))
    quit_text = font.render("Press 'Q' to quit", True, (255, 255, 255))

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(try_again_text, (WIDTH // 2 - try_again_text.get_width() // 2, 300))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 350))

    pygame.display.flip()

    while True:
        pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    clock = pygame.time.Clock()
                    game_loop(screen, clock)
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def win_screen(screen):
    screen.fill(BACKGROUND)
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("You Win", True, (255, 0, 0))
    try_again_text = font.render("Press 'T' to try again", True, (255, 255, 255))
    quit_text = font.render("Press 'Q' to quit", True, (255, 255, 255))

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(try_again_text, (WIDTH // 2 - try_again_text.get_width() // 2, 300))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 350))

    pygame.display.flip()

    while True:
        pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    clock = pygame.time.Clock()
                    game_loop(screen, clock)
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    title_screen(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # Start the game
                    game_loop(screen, clock)
                elif event.key == pygame.K_c:
                    # Show controls (you can implement this part)
                    show_controls(screen)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()



if __name__ == "__main__":
    main()