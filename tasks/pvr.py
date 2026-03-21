import sys
import math
import time
import pygame
import pandas as pd

from pygame.locals import *
from utils import display


class PVR(object):
    """Relative Verticality Perception Task (Percepción de la Verticalidad Relativa).

    The participant rotates a line until they perceive it as perfectly vertical.
    Vertical orientation corresponds to 90.0 degrees.
    """

    def __init__(self, screen, background):
        # Get the pygame display window
        self.screen = screen
        self.background = background

        # Fonts
        self.font = pygame.font.SysFont("arial", 28)
        self.font_small = pygame.font.SysFont("arial", 20)

        # Get screen info
        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        # Fill background
        self.background.fill((255, 255, 255))
        pygame.display.set_caption("Percepción de la Verticalidad Relativa (PVR)")
        pygame.mouse.set_visible(1)

        # Line properties
        self.LINE_LENGTH = min(self.screen_x, self.screen_y) // 4
        self.LINE_COLOUR = (0, 0, 0)
        self.LINE_WIDTH = 4

        # Decorative frame properties (slightly tilted from vertical)
        self.FRAME_WIDTH = self.screen_x // 4
        self.FRAME_HEIGHT = self.screen_y // 2
        self.FRAME_COLOUR = (0, 0, 0)
        self.FRAME_BORDER = 4
        self.FRAME_TILT = 3.0  # degrees tilt of the frame from vertical

        # Mouse sensitivity: degrees of rotation per pixel of horizontal mouse movement
        self.SENSITIVITY = 0.3

        # Initial angle in degrees: 0 = horizontal, 90 = vertical
        self.initial_angle = 0.0

    def _draw_frame(self):
        """Draw the slightly-tilted decorative rectangle frame."""
        cx = self.screen_x // 2
        cy = self.screen_y // 2
        hw = self.FRAME_WIDTH // 2
        hh = self.FRAME_HEIGHT // 2

        tilt_rad = math.radians(self.FRAME_TILT)

        # Rotate the four corners of the rectangle by FRAME_TILT degrees
        corners_local = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        corners = []
        for lx, ly in corners_local:
            rx = lx * math.cos(tilt_rad) - ly * math.sin(tilt_rad)
            ry = lx * math.sin(tilt_rad) + ly * math.cos(tilt_rad)
            corners.append((cx + rx, cy + ry))

        pygame.draw.polygon(self.screen, self.FRAME_COLOUR, corners, self.FRAME_BORDER)

    def _draw_line(self, angle_deg):
        """Draw the rotatable line at the given angle.

        angle_deg: 0.0 = horizontal (pointing left-right),
                   90.0 = vertical (pointing up-down).
        """
        cx = self.screen_x // 2
        cy = self.screen_y // 2
        angle_rad = math.radians(angle_deg)
        half_len = self.LINE_LENGTH / 2

        dx = math.cos(angle_rad) * half_len
        # Negate dy because pygame y-axis increases downward
        dy = -math.sin(angle_rad) * half_len

        start = (int(cx - dx), int(cy - dy))
        end = (int(cx + dx), int(cy + dy))

        pygame.draw.line(self.screen, self.LINE_COLOUR, start, end, self.LINE_WIDTH)

    def _show_instructions(self):
        """Display the task instructions screen."""
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))

        instructions = [
            "A continuación se va a presentar una línea recta.",
            "Tu tarea consiste en girar la línea hasta dejarla completamente vertical.",
            "",
            "Para girar la línea tienes que clicar en ella y girarla",
            "moviendo tu ratón hacia la derecha o izquierda.",
            "",
            "Cuando consideres que la línea está totalmente en vertical",
            "pulsa en el teclado el botón Enter.",
            "",
            "Pulsa la barra espaciadora para continuar.",
        ]

        line_height = 40
        total_height = len(instructions) * line_height
        start_y = (self.screen_y - total_height) // 2

        for i, line in enumerate(instructions):
            y = start_y + i * line_height
            display.text(self.screen, self.font, line, "center", y)

        pygame.display.flip()
        display.wait_for_space()

    def _run_task(self):
        """Run the main interactive rotation loop.

        Returns:
            tuple: (final_angle_deg, rotation_time_ms)
        """
        current_angle = self.initial_angle
        dragging = False
        last_mouse_x = 0
        start_time = int(round(time.time() * 1000))

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    elif event.key in (K_RETURN, K_KP_ENTER):
                        running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        dragging = True
                        last_mouse_x, _ = event.pos
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False
                elif event.type == MOUSEMOTION:
                    if dragging:
                        mouse_x, _ = event.pos
                        delta = mouse_x - last_mouse_x
                        current_angle += delta * self.SENSITIVITY
                        last_mouse_x = mouse_x

            # Redraw scene
            self.background.fill((255, 255, 255))
            self.screen.blit(self.background, (0, 0))
            self._draw_frame()
            self._draw_line(current_angle)

            hint = "Pulsa Enter cuando la línea esté vertical"
            display.text(self.screen, self.font_small, hint, "center", self.screen_y - 60)

            pygame.display.flip()
            clock.tick(60)

        end_time = int(round(time.time() * 1000))
        rotation_time_ms = end_time - start_time

        # Normalize angle to [0, 360) for consistent output
        normalized_angle = current_angle % 360.0

        return normalized_angle, rotation_time_ms

    def _show_end_screen(self):
        """Display the end-of-task screen."""
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))

        display.text(
            self.screen,
            self.font,
            "Tarea terminada. Gracias por tu participación.",
            "center",
            "center",
        )
        pygame.display.flip()
        display.wait_for_space()

    def run(self):
        """Execute the full PVR task sequence.

        Returns:
            pd.DataFrame: Results with columns:
                - task_name
                - initial_angle_deg
                - final_angle_deg
                - rotation_time_ms
        """
        self._show_instructions()
        final_angle, rotation_time_ms = self._run_task()
        self._show_end_screen()

        data = pd.DataFrame(
            data=[
                (
                    "PVR",
                    round(self.initial_angle, 6),
                    round(final_angle, 6),
                    rotation_time_ms,
                )
            ],
            columns=[
                "task_name",
                "initial_angle_deg",
                "final_angle_deg",
                "rotation_time_ms",
            ],
        )

        return data
