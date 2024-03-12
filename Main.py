# intial Code from https://docs.replit.com/tutorials/python/2d-platform-game
import pygame, numpy

WIDTH = 800
HEIGHT = 600
BACKGROUND = (0, 0, 0)
INVISIBLE_WALL_WIDTH = 10


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite):
    def __init__(self, startx, starty):
        super().__init__("./Assets/p1_front.png", startx, starty)
        self.stand_image = self.image
        self.jump_image = pygame.image.load("./assets/p1_front.png")
        self.is_alive = True

        self.walk_cycle = [pygame.image.load(f"./assets/p1_walk{i:0>2}.png") for i in range(1,12)]
        self.animation_index = 0
        self.facing_left = False

        self.speed = 4
        self.jumpspeed = 20
        self.vsp = 0
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle)-1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, environment, enemies):
        hsp = 0
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

        if onground and self.vsp > 0:
            self.vsp = 0


        # movement
        self.move(hsp, self.vsp, environment, enemies)
        
        enemy_collision = pygame.sprite.spritecollideany(self, enemies)
        
        if enemy_collision:
            self.is_alive = False
            print("Player died!")
        

    def move(self, x, y, environment, enemies):
        dx = x
        dy = y
        dxPlayer = 0
        
        if (dx > 0 and self.rect.x < (WIDTH - (WIDTH / 4))):
            dxPlayer = dx
        elif (dx < 0 and self.rect.x > WIDTH / 4):
            dxPlayer = dx
        

        while self.check_collision(0, dy, environment):
            dy -= numpy.sign(dy)

        
        while self.check_collision((dxPlayer + dx), dy, environment):
            dx -= numpy.sign(dx)
            dxPlayer -= numpy.sign(dxPlayer)

        for sprite in environment.sprites():
            sprite.rect.x -= dx
            sprite.rect.y -= dy
        for sprite in enemies.sprites():
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
    
class Enemy(Sprite):
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


class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("./assets/box.png", startx, starty)



def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player(WIDTH / 2, HEIGHT / 2)

    enemies = pygame.sprite.Group()
    enemy = Enemy(600, 200)
    enemies.add(enemy)

    environment = pygame.sprite.Group()
    for bx in range(-10000, 10000, 70):
        environment.add(Box(bx, 400))

    environment.add(Box(330, 230))
    environment.add(Box(400, 70))

    while True:
        pygame.event.pump()
        player.update(environment, enemies)
        enemy.update(environment)
        
        if not player.is_alive:
            player = Player(WIDTH / 2, HEIGHT / 2)

            enemies = pygame.sprite.Group()
            enemy = Enemy(200, 100)
            enemies.add(enemy)

            environment = pygame.sprite.Group()
            for bx in range(-10000, 10000, 70):
                environment.add(Box(bx, 400))

            environment.add(Box(330, 230))
            environment.add(Box(400, 70))



        # Draw loop
        screen.fill(BACKGROUND)
        player.draw(screen)
        enemies.draw(screen)
        environment.draw(screen)
        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    main()