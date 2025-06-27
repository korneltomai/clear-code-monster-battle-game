from settings import *
from support import *
from custom_timer import Timer
from monster import Monster, Opponent
from ui import UI
from random import choice

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True

        self.import_assets()

        # groups 
        self.all_sprites = pygame.sprite.Group()

        # data
        player_monster_list = ["Sparchu", "Cleaf", "Jacana", "Gulfin", "Pouch", "Larvea"]
        self.player_monsters = [Monster(self.back_surfs[name], name) for name in player_monster_list]
        self.current_monster = self.player_monsters[0]
        self.all_sprites.add(self.current_monster)

        random_monster = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(self.all_sprites, self.front_surfs[random_monster], random_monster)

        # UI
        self.ui = UI(self.simple_surfs, self.current_monster, self.player_monsters)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.all_sprites.update(dt)
            self.ui.update()

            # draw  
            self.display_surface.blit(self.bg_surfs["bg"], (0,0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            pygame.display.update()
        
        pygame.quit()

    def import_assets(self):
        self.bg_surfs = folder_importer("images", "other")
        self.back_surfs = folder_importer("images", "back")
        self.front_surfs = folder_importer("images", "front")
        self.simple_surfs = folder_importer("images", "simple")

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            floor_rect = self.bg_surfs["floor"].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
            self.display_surface.blit(self.bg_surfs["floor"], floor_rect)

if __name__ == '__main__':
    game = Game()
    game.run()