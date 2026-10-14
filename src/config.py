import pygame
import os

from sound import Sound
from theme import Theme

class Config:

    def __init__(self):
        self.themes = []
        self._add_themes()
        self.idx = 0
        self.theme = self.themes[self.idx]
        self.font = pygame.font.SysFont('segoeui,segoe ui,helvetica,arial', 16, bold=True)

        self.move_sound = Sound(
            os.path.join('assets/sounds/move.wav'))
        self.capture_sound = Sound(
            os.path.join('assets/sounds/capture.wav'))

        # Tactical Modern Viewfinder Reticle Colors (Blue, Green, White, Red)
        self.reticle_colors = {
            'blue': (99, 102, 241),    # Indigo / Soft Blue (#6366F1)
            'green': (74, 222, 128),   # Neon Mint Emerald (#4ADE80)
            'white': (255, 255, 255),  # Studio Pure White (#FFFFFF)
            'red': (248, 113, 113)     # Coral Crimson (#F87171)
        }
        self.reticle_color_names = ['blue', 'green', 'white', 'red']
        self.reticle_idx = 0
        self.reticle_color_name = self.reticle_color_names[self.reticle_idx]

    @property
    def reticle_color(self):
        return self.reticle_colors[self.reticle_color_name]

    def change_theme(self):
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = self.themes[self.idx]

    def change_reticle_color(self):
        self.reticle_idx = (self.reticle_idx + 1) % len(self.reticle_color_names)
        self.reticle_color_name = self.reticle_color_names[self.reticle_idx]

    def _add_themes(self):
        # 1. Emerald (Chess.com Signature Green)
        emerald = Theme(
            (238, 238, 210), (118, 150, 86),
            (247, 247, 105), (186, 202, 43),
            '#C86464', '#C84646',
            name="Emerald"
        )
        # 2. Walnut (Classic Warm Wood)
        walnut = Theme(
            (240, 217, 181), (181, 136, 99),
            (205, 210, 106), (170, 162, 58),
            '#C86464', '#C84646',
            name="Walnut"
        )
        # 3. Ocean (Contemporary Oceanic Blue)
        ocean = Theme(
            (235, 237, 240), (110, 142, 168),
            (135, 195, 235), (60, 135, 190),
            '#C86464', '#C84646',
            name="Ocean"
        )
        # 4. Slate (Midnight Minimalist Slate)
        slate = Theme(
            (220, 224, 228), (82, 102, 122),
            (160, 185, 210), (95, 125, 155),
            '#C86464', '#C84646',
            name="Slate"
        )
        # 5. Charcoal (Dark Carbon Tournament)
        charcoal = Theme(
            (175, 175, 175), (78, 78, 78),
            (195, 195, 135), (135, 135, 80),
            '#C86464', '#C84646',
            name="Charcoal"
        )

        self.themes = [emerald, walnut, ocean, slate, charcoal]