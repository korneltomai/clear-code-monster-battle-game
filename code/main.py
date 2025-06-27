from settings import *
from support import *
from custom_timer import Timer
from monster import Creature, Monster, Opponent
from ui import PlayerUI, OpponentUI
from attack import AttackAnimationSprite
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
        self.player_ui = PlayerUI(self.current_monster, self.simple_surfs, self.player_monsters, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)

        # Timers
        self.timers = {
            "player turn end": Timer(1000, func = self.take_opponent_turn),
            "opponent turn end": Timer(1000, func = self.take_player_turn)
        }

    def run(self):
        self.audio["music"].play(-1)

        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active:
                self.player_ui.update()

            # draw  
            self.display_surface.blit(self.bg_surfs["bg"], (0,0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            self.player_ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()
        
        pygame.quit()

    def import_assets(self):
        self.bg_surfs = folder_importer("images", "other")
        self.back_surfs = folder_importer("images", "back")
        self.front_surfs = folder_importer("images", "front")
        self.simple_surfs = folder_importer("images", "simple")
        self.attack_frames = tile_importer(4, "images", "attacks")
        self.audio = audio_importer("audio")

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surfs["floor"].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surfs["floor"], floor_rect)

    def take_opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            random_monster = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(self.all_sprites, self.front_surfs[random_monster], random_monster)
            self.opponent_ui.current_monster = self.opponent

        else:
            random_attack = choice(self.opponent.abilities)
            self.apply_attack(self.current_monster, random_attack)
            self.timers["opponent turn end"].activate()

    def take_player_turn(self):
        self.player_active = True
        if self.current_monster.health <= 0:
            available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
            if available_monsters:
                self.current_monster.kill()

                # switch to the next available
                for i in range(len(self.player_monsters)):
                    next_monster = self.player_monsters[self.player_monsters.index(self.current_monster) + i]
                    if next_monster in available_monsters:
                        self.current_monster = next_monster
                        break

                self.all_sprites.add(self.current_monster)
                self.player_ui.current_monster = self.current_monster
            else:
                self.running = False

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_input(self, state, data = None):
        if state == "attack":
            self.apply_attack(self.opponent, data)
        elif state == "heal":
            self.current_monster.health += 50
            AttackAnimationSprite(self.all_sprites, self.current_monster, self.attack_frames["green"])
            self.audio["green"].play()
        elif state == "switch":
            self.current_monster.kill()
            self.current_monster = data
            self.all_sprites.add(self.current_monster)
            self.player_ui.current_monster = self.current_monster
        elif state == "escape":
            self.running = False

        self.player_active = False
        self.timers["player turn end"].activate()

    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        damage_multiplier = ELEMENT_DATA[attack_data["element"]][target.element]
        target.health -= attack_data["damage"] * damage_multiplier
        AttackAnimationSprite(self.all_sprites, target, self.attack_frames[attack_data["animation"]])
        self.audio[attack_data["animation"]].play()

if __name__ == '__main__':
    game = Game()
    game.run()