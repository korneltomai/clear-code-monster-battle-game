from settings import *

class UI:
    def __init__(self, pos, monster):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = pos[0]
        self.top = pos[1]
        self.current_monster = monster

    def draw(self):
        self.draw_stats()

    def draw_stats(self):
        # background
        menu_rect = pygame.FRect((self.left, self.top), (250, 80))
        pygame.draw.rect(self.display_surface, COLORS["white"], menu_rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], menu_rect, 4, 4)

        # text
        name_surf = self.font.render(self.current_monster.name, True, COLORS["black"])
        name_rect = name_surf.get_frect(topleft = menu_rect.topleft + pygame.Vector2(menu_rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        for i in range(len(self.current_monster.statuses)):
            status = self.current_monster.statuses[i]
            status_color = COLORS["black"]
            match status.name:
                case "bleed":
                    status_color = "red"
                case "paralysis":
                    status_color = "yellow"
                case "drain":
                    status_color = "green"
            
            pygame.draw.aacircle(self.display_surface, status_color, (name_rect.right + 20 + i * 30 , name_rect.centery), 12)

        # health bar
        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, menu_rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surface, COLORS["gray"], health_rect)
        self.draw_bar(health_rect, self.current_monster.health, self.current_monster.max_health)

    def draw_bar(self, rect, value, max_value):
        ratio = rect.width / max_value
        progress_rect = pygame.FRect(rect.topleft, (value * ratio, rect.height))
        pygame.draw.rect(self.display_surface, COLORS["red"], progress_rect)

class PlayerUI(UI):
    def __init__(self, monster, monster_surfs, player_monsters, get_input):
        super().__init__((WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 50), monster)
        self.monster_surfs = monster_surfs
        self.player_monsters = player_monsters
        self.get_input = get_input

        # control
        self.general_options = ["attack", "heal", "switch", "escape"]
        self.general_index = {"col": 0, "row": 0}
        self.attack_index = {"col": 0, "row": 0}
        self.switch_index = 0
        self.state = "general"

        self.rows = 2
        self.cols = 2
        self.visible_monsters = 4
        self.available_monsters = [monster for monster in self.player_monsters if monster != self.current_monster and monster.health > 0]

    def update(self):
        if self.current_monster.stunned:
            self.get_input("stunned")
        else:
            self.handle_input()

        self.available_monsters = [monster for monster in self.player_monsters if monster != self.current_monster and monster.health > 0]

    def draw(self):
        match self.state:
            case "general":
                self.handle_selection(self.general_index, self.general_options)
            case "attack":
                self.handle_selection(self.attack_index, self.current_monster.abilities)
            case "switch":
                self.switch()

        if self.state != "switch":
            self.draw_stats()

    def handle_selection(self, index, options):
        # background
        menu_rect = pygame.FRect(self.left + 40, self.top + 60, 400, 200)
        pygame.draw.rect(self.display_surface, COLORS["white"], menu_rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], menu_rect, 4, 4)

        # menu
        for col in range(self.cols):
            for row in range(self.rows):
                x = menu_rect.left + menu_rect.width / (2 * self.cols) + (menu_rect.width / self.cols) * col
                y = menu_rect.top + menu_rect.height / (2 * self.rows) + (menu_rect.height / self.rows) * row
                i = col + self.cols * row
                option_color = COLORS["gray"] if col == index["col"] and row == index["row"] else COLORS["black"]

                text_surf = self.font.render(options[i], True, option_color)
                text_rect = text_surf.get_frect(center = (x, y))
                self.display_surface.blit(text_surf, text_rect)

    def handle_input(self):
        keys = pygame.key.get_just_pressed()

        if self.state == "general":
            self.general_index["row"] = (self.general_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.general_index["col"] = (self.general_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.state = self.general_options[self.general_index["col"] + self.cols * self.general_index["row"]]

        elif self.state == "attack":
            self.attack_index["row"] = (self.attack_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.attack_index["col"] = (self.attack_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) % self.cols
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                attack = self.current_monster.abilities[self.attack_index["col"] + self.cols * self.attack_index["row"]]
                self.get_input(self.state, attack)
                self.state = "general"
                self.general_index = {"col": 0, "row": 0}

        elif self.state == "switch":
            if self.available_monsters:
                self.switch_index = (self.switch_index + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % len(self.available_monsters)
                if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                    self.get_input(self.state, self.available_monsters[self.switch_index])
                    self.state = "general"
                    self.general_index = {"col": 0, "row": 0}

        elif self.state == "heal":
            self.get_input("heal")
            self.state = "general"

        elif self.state == "escape":
            self.get_input("escape")

        if keys[pygame.K_ESCAPE]:
            self.state = "general"
            self.attack_index = {"col": 0, "row": 0}
            self.switch_index = 0

    def switch(self):
        # background
        menu_rect = pygame.FRect(self.left + 40, self.top - 140, 400, 400)
        pygame.draw.rect(self.display_surface, COLORS["white"], menu_rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], menu_rect, 4, 4)

        # menu
        v_offset = 0 if self.switch_index < self.visible_monsters else -(self.switch_index - self.visible_monsters + 1) * menu_rect.height / self.visible_monsters
        for i in range(len(self.available_monsters)):
            x = menu_rect.centerx
            y = menu_rect.top + menu_rect.height / (self.visible_monsters * 2) + menu_rect.height / self.visible_monsters * i + v_offset
            option_color = COLORS["gray"] if i == self.switch_index else COLORS["black"]

            name = self.available_monsters[i].name
            text_surf = self.font.render(name, True, option_color)
            text_rect = text_surf.get_frect(midleft = (x, y))

            monster_surf = self.monster_surfs[name]
            monster_rect = monster_surf.get_frect(midleft = (menu_rect.left + 60, y))

            if menu_rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(monster_surf, monster_rect)

class OpponentUI(UI):
    def __init__(self, monster):
        super().__init__((WINDOW_WIDTH / 2 - 50, WINDOW_HEIGHT / 2 - 200), monster)

class ActionHistory():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = 25
        self.top = 25
        self._actions = []
        self.maximum_length = 10

    def draw(self):
        for i in range(len(self._actions)):
            action_surf = self.font.render(self._actions[i], True, COLORS["black"])
            action_rect = action_surf.get_frect(topleft = (self.left, self.top + i * action_surf.get_height()))
            self.display_surface.blit(action_surf, action_rect)

    def add_action(self, string):
        self._actions.append(string)
        if len(self._actions) > self.maximum_length:
            self._actions.pop(0)