import pygame


class PygameRenderer:
    def __init__(self, world, tile_size=32, panel_width=220, fps=10):
        pygame.init()
        pygame.font.init()

        self.tile_size = tile_size
        self.panel_width = panel_width
        self.fps = fps
        self.running = True

        self.map_width_px = world.map_width * tile_size
        self.map_height_px = world.map_height * tile_size
        self.screen = pygame.display.set_mode((self.map_width_px + panel_width, self.map_height_px))
        pygame.display.set_caption("Humanoid Project")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 18)

        self.colors = {
            "#": (45, 45, 45),
            ".": (215, 215, 215),
            "key": (235, 190, 60),
            "door_locked": (175, 50, 50),
            "door_open": (60, 155, 90),
            "agent": (50, 120, 220),
            "panel_bg": (20, 20, 20),
            "panel_text": (235, 235, 235),
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def render(self, world):
        self.handle_events()
        if not self.running:
            return

        for row in range(world.map_height):
            for col in range(world.map_width):
                tile = world.grid_rows[row][col]
                color = self.colors["#"] if tile == "#" else self.colors["."]
                x = col * self.tile_size
                y = row * self.tile_size
                pygame.draw.rect(self.screen, color, (x, y, self.tile_size, self.tile_size))

        if not world.has_key:
            x = world.key_position.col * self.tile_size + 8
            y = world.key_position.row * self.tile_size + 8
            s = self.tile_size - 16
            pygame.draw.rect(self.screen, self.colors["key"], (x, y, s, s))

        dx = world.door_position.col * self.tile_size + 2
        dy = world.door_position.row * self.tile_size + 2
        ds = self.tile_size - 4
        door_color = self.colors["door_open"] if world.door_open else self.colors["door_locked"]
        pygame.draw.rect(self.screen, door_color, (dx, dy, ds, ds))

        ax = world.agent_position.col * self.tile_size + self.tile_size // 2
        ay = world.agent_position.row * self.tile_size + self.tile_size // 2
        pygame.draw.circle(self.screen, self.colors["agent"], (ax, ay), max(6, self.tile_size // 3))

        panel_x = self.map_width_px
        pygame.draw.rect(self.screen, self.colors["panel_bg"], (panel_x, 0, self.panel_width, self.map_height_px))

        lines = [
            f"Step: {world.step_count}",
            f"Has key: {world.has_key}",
            f"Door open: {world.door_open}",
            world.last_action_result[:28],
        ]

        y = 16
        for line in lines:
            text = self.font.render(line, True, self.colors["panel_text"])
            self.screen.blit(text, (panel_x + 10, y))
            y += 24

        pygame.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        pygame.quit()