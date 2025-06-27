from settings import *

class UI:
    def __init__(self, monster_surfs, monster, player_monsters):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2 - 100
        self.top = WINDOW_HEIGHT / 2 + 50
        self.monster_surfs = monster_surfs
        self.current_monster = monster
        self.player_monsters = player_monsters

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
        self.handle_input()

    def draw(self):
        match self.state:
            case "general":
                self.handle_selection(self.general_index, self.general_options)
            case "attack":
                self.handle_selection(self.attack_index, self.current_monster.abilities)
            case "switch":
                self.switch()

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
                print(self.current_monster.abilities[self.attack_index["col"] + self.cols * self.attack_index["row"]])

        elif self.state == "switch":
            self.switch_index = (self.switch_index + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % len(self.available_monsters)
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                print(self.available_monsters[self.switch_index])

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
