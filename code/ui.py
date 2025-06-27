from settings import *

class UI:
    def __init__(self, monster):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2 - 100
        self.top = WINDOW_HEIGHT / 2 + 50
        self.monster = monster

        self.rows = 2
        self.cols = 2
        

        # control
        self.general_options = ["attack", "heal", "switch", "escape"]
        self.general_index = {"col": 0, "row": 0}
        self.attack_index = {"col": 0, "row": 0}
        self.state = "general"

    def update(self):
        self.handle_input()

    def draw(self):
        match self.state:
            case "general":
                self.handle_selection(self.general_index, self.general_options)
            case "attack":
                self.handle_selection(self.attack_index, self.monster.abilities)

    def handle_selection(self, index, options):
        # background
        rect = pygame.FRect(self.left + 40, self.top + 60, 400, 200)
        pygame.draw.rect(self.display_surface, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS["gray"], rect, 4, 4)

        # menu
        for col in range(self.cols):
            for row in range(self.rows):
                x = rect.left + rect.width / (2 * self.cols) + (rect.width / self.cols) * col
                y = rect.top + rect.height / (2 * self.rows) + (rect.height / self.rows) * row
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
                print(self.monster.abilities[self.attack_index["col"] + self.cols * self.attack_index["row"]])