from settings import *
from support import *
from custom_timer import Timer
from monster import Creature, Monster, Opponent
from ui import PlayerUI, OpponentUI, ActionHistory
from attack import AttackAnimationSprite
from statuses import *
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
        self.player_monster = self.player_monsters[0]
        self.all_sprites.add(self.player_monster)

        random_monster = choice(list(MONSTER_DATA.keys()))
        self.opponent_monster = Opponent(self.all_sprites, self.front_surfs[random_monster], random_monster)

        # UI
        self.player_ui = PlayerUI(self.player_monster, self.simple_surfs, self.player_monsters, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent_monster)
        self.action_history = ActionHistory()

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
            self.action_history.draw()
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
        if self.opponent_monster.health > 0:
            self.update_statuses(self.opponent_monster)

        if self.opponent_monster.health <= 0:
            old_monster = self.opponent_monster
            self.player_active = True
            self.opponent_monster.kill()
            random_monster = choice(list(MONSTER_DATA.keys()))
            self.opponent_monster = Opponent(self.all_sprites, self.front_surfs[random_monster], random_monster)
            self.opponent_ui.current_monster = self.opponent_monster
            self.action_history.add_action(f"{old_monster.name} fainted! Wild {self.opponent_monster.name} appears!")
        else:
            if not self.opponent_monster.stunned:
                random_attack = choice(self.opponent_monster.abilities)
                self.apply_attack(self.opponent_monster, self.player_monster, random_attack)
            self.timers["opponent turn end"].activate()

    def take_player_turn(self):
        self.player_active = True
        
        if self.player_monster.health > 0:
            self.update_statuses(self.player_monster)

        if self.player_monster.health <= 0:
            old_monster = self.player_monster
            available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
            if available_monsters:
                self.player_monster.kill()

                # switch to the next available
                for i in range(len(self.player_monsters)):
                    next_monster = self.player_monsters[self.player_monsters.index(self.player_monster) + i]
                    if next_monster in available_monsters:
                        self.player_monster = next_monster
                        break

                self.all_sprites.add(self.player_monster)
                self.player_ui.current_monster = self.player_monster
                self.action_history.add_action(f"{old_monster.name} fainted! You summon {self.player_monster.name}!")
            else:
                self.running = False
            
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_input(self, state, data = None):
        if state == "attack":
            self.apply_attack(self.player_monster, self.opponent_monster, data)
        elif state == "heal":
            heal_amount = 50
            self.player_monster.health += heal_amount
            AttackAnimationSprite(self.all_sprites, self.player_monster, self.attack_frames["green"])
            self.audio["green"].play()
            self.action_history.add_action(f"You use heal on {self.player_monster.name}! {self.player_monster.name} is healed for {heal_amount} HP!")
        elif state == "switch":
            old_monster = self.player_monster
            self.player_monster.kill()
            self.player_monster = data
            self.all_sprites.add(self.player_monster)
            self.player_ui.current_monster = self.player_monster
            self.action_history.add_action(f"You send away {old_monster.name} and summon {self.player_monster.name}!")
        elif state == "escape":
            self.running = False

        self.player_active = False
        self.timers["player turn end"].activate()

    def apply_attack(self, user, target, attack):
        attack_data = ABILITIES_DATA[attack]
        damage_multiplier = ELEMENT_DATA[attack_data["element"]][target.element]
        damage = int(attack_data["damage"] * damage_multiplier)
        target.health -= damage
        AttackAnimationSprite(self.all_sprites, target, self.attack_frames[attack_data["animation"]])
        self.audio[attack_data["animation"]].play()
        self.action_history.add_action(f"{user.name} uses {attack} on {self.opponent_monster.name}. {target.name} suffers {damage} damage!")

        if "status" in attack_data:
            status = attack_data["status"]
            self.apply_status(user, target, status)
            self.action_history.add_action(f"{target.name} suffers {status}!")

    def apply_status(self, user, target, status):
        match status:
            case "bleed":
                if not any(status.name == "bleed" for status in target.statuses):
                    target.statuses.append(Bleed(target, self.action_history.add_action))
            case "paralysis":
                if not any(status.name == "paralysis" for status in target.statuses):
                    target.statuses.append(Paralysis(target, self.action_history.add_action))
            case "drain":
                if not any(status.name == "drain" for status in target.statuses):
                    target.statuses.append(Drain(user, target, self.action_history.add_action))

    def update_statuses(self, monster):
        for status in monster.statuses:
            status.apply()
            if status.remaining_duration == 0:
                monster.statuses.remove(status)
                self.action_history.add_action(f"{status.name.capitalize()} times out on {monster.name}!")
                if status.name == "paralysis":
                    monster.stunned = False

if __name__ == '__main__':
    game = Game()
    game.run()