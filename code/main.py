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
        self.player_active = True

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
        self.ui = UI(self.simple_surfs, self.current_monster, self.player_monsters, self.get_input)

        # Timers
        self.timers = {
            "player turn end": Timer(1000, func = self.take_opponent_turn),
            "opponent turn end": Timer(1000, func = self.take_player_turn)
        }

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active:
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

    def take_opponent_turn(self):
        random_attack = choice(self.opponent.abilities)
        self.apply_attack(self.current_monster, random_attack)
        self.timers["opponent turn end"].activate()

    def take_player_turn(self):
        self.player_active = True

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_input(self, state, data = None):
        if state == "attack":
            self.apply_attack(self.opponent, data)
        elif state == "heal":
            pass
        elif state == "switch":
            pass
        elif state == "escape":
            self.running = False

        self.player_active = False
        self.timers["player turn end"].activate()

    def apply_attack(self, target, attack):
        damage_multiplier = ELEMENT_DATA[ABILITIES_DATA[attack]["element"]][target.element]
        target.health = max(0, target.health - ABILITIES_DATA[attack]["damage"] * damage_multiplier)

if __name__ == '__main__':
    game = Game()
    game.run()