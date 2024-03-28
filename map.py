import pygame, csv, os, random


script_dir = os.path.dirname(os.path.realpath(__file__))

# Change the working directory to the script's directory
os.chdir(script_dir)

class Map:
    def __init__(self, filename):
        self.chunk_map = []
        self.read_csv(filename)
        self.completed_map = self.stitch_map()
        self.start_x = 0
        self.start_y = 0


    def read_csv(self, filename):
        chunk_data = []

        with open(os.path.join(filename)) as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                if row[-1].endswith('.'):
                    row[-1] = row[-1][:-1]
                    chunk_data.append(row)
                    self.chunk_map.append(chunk_data.copy())  # Append a copy of chunk_data
                    chunk_data.clear()  # Clear chunk_data for the next chunk
                else:
                    chunk_data.append(row)

        return

    
    # Gets the beginning maps (first 5) from the total list 
    def get_beg(self):
        beginning_maps = []
        for item in self.chunk_map[:10]:
            beginning_maps.append(item)
        return beginning_maps
    
    # Get the middle section maps (between the first 5 and the last 5) from the total list
    def get_mid(self):
        middle_maps = []
        for item in self.chunk_map[10:-11]:
            middle_maps.append(item)
        return middle_maps
    
    # Gets the last map sections from the last 5
    def get_end(self):
        end_maps = []
        for item in self.chunk_map[-11:]:
            end_maps.append(item)
        return end_maps
    
    # Makes the final map between a random beginning map section, 25 middle map sections, and 1 end map section.
    def stitch_map(self):
        completed_map = []

        beginning_maps = self.get_beg()
        middle_maps = self.get_mid()
        end_maps = self.get_end()

        random_number = random.randint(0, 9)
        beginning_maps[random_number].reverse()
        completed_map.extend(beginning_maps[random_number])
        beginning_maps[random_number].reverse()

        length = len(middle_maps)
        for i in range(25):
            random_number = random.randint(0, length - 1)
            middle_maps[random_number].reverse()
            completed_map.extend(middle_maps[random_number])
            middle_maps[random_number].reverse()

        random_number = random.randint(0, 10)
        end_maps[random_number].reverse()
        completed_map.extend(end_maps[random_number])
        end_maps[random_number].reverse()

        return completed_map
    
    #Debugging to print what the completed map looks like. 
    def print_completed_map(self):
        for chunk in self.completed_map:
            print(chunk)


class Spritesheet:
    def __init__(self):
        self.sprite_sheet = None


    def get_sprite_from_file(self, filename):
        sprite = pygame.image.load(filename).convert()
        return sprite

    
class Tile:
    def __init__(self, sprite, x, y, target_size=(70, 70)):
        # Resize the image to the target size
        self.image = pygame.transform.scale(sprite, target_size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
       surface.blit(self.image, (self.rect.x, self.rect.y))

    
class TileMap:
    def __init__(self, spritesheet, completed_map):
        self.tile_size = 70
        self.spritesheet = spritesheet  # Added this line to store the spritesheet
        self.completed_map = completed_map
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.edge = pygame.sprite.Group()
        self.end_goal = pygame.sprite.Group()
        self.load_map()

    def load_map(self):
        # self.tiles.clear()  # Clear existing tiles

        x, y = 0, 0
        tile_size = self.tile_size

        region_mapping = {
            -3: "lava.jpg",
            0: "tile000.png",
            1: "tile001.png",
            2: "tile002.png",
            3: "tile003.png",
            4: "tile004.png",
            5: "tile005.png",
            6: "tile006.png",
            7: "tile007.png",
            8: "tile008.png",
            9: "tile009.png",
            10: "tile010.png",
            11: "tile011.png",
            12: "tile012.png",
            13: "tile013.png",
            14: "tile014.png",
            15: "tile015.png",
            16: "tile016.png",
            17: "tile017.png",
            18: "tile018.png",
            19: "tile019.png",
            20: "tile020.png",
            21: "tile021.png",
            22: "tile022.png",
            23: "tile023.png",
            24: "tile024.png",
            25: "tile025.png",
            26: "tile026.png",
            27: "tile027.png",
            28: "tile028.png",
            29: "tile029.png",
            30: "tile030.png",
        }

        base_path = os.path.abspath("assets")
        x_counter = 0
        y_counter = 5
        for row in self.completed_map:
            if y_counter <0:
                y_counter =5
                x_counter = x_counter +25

            x = x_counter
            for i in row:
                i = int(i)
                if i == -1:
                    x+=1
                    

                else:
                    y = y_counter
                    filename = os.path.join(base_path, region_mapping[i])
                    # sprite = self.spritesheet.get_sprite_from_file(filename)
                    startx = x * tile_size
                    starty = y * tile_size + 600
                    tile = Tile(filename, startx, starty)

                    if i == -2:
                        self.enemies.add(tile)
                    else:
                        if i == 17:
                            self.end_goal.add(tile)
                        else if i == -2"
                            self.edge.add(tile)
                        else:
                            self.tiles.add(tile)

                    x +=1
            y_counter -= 1

    def draw_map(self, surface):
        for tile in self.tiles:
            surface.blit(tile.image, tile.rect.topleft)
    def return_spawns(self):
        return self.spawns
    def return_bottom(self):
        return self.edge


pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 350
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Your Game Title")
map_filename = "test.csv"
spritesheet = Spritesheet()  # Create an instance of Spritesheet
my_map = Map(map_filename)


tile_map = TileMap(spritesheet, my_map.stitch_map())

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    tile_map.load_map()

    # Drawing
    screen.fill((255, 255, 255))  # Set background color (adjust as needed)

    tile_map.draw_map(screen)

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame properly
pygame.quit()

    
        

