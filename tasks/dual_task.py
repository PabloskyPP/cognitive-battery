import sys
import time
import math
import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class DualTask(object):
    """Dual task: continuous motor tracking + visual stimulus response.

    The participant must:
    1. Follow a moving blue point with the mouse cursor.
    2. Press the A key as fast as possible whenever a red square appears.

    Duration: 120 seconds (automatic end).

    Data recorded:
    - Cursor-to-point distance every 7.5 s  → "tracking" DataFrame
    - Response latency for each stimulus     → "responses" DataFrame
    """

    # Waypoints for the moving point (reference resolution: 1920×1080).
    PATH_POINTS = [
        (120, 140), (450, 220), (780, 180), (1100, 260),
        (1500, 200), (1700, 400), (1600, 650), (1300, 720),
        (900, 680), (500, 750), (200, 600), (300, 400),
        (600, 350), (950, 420), (1250, 500), (1550, 480),
        (1800, 300), (1650, 150), (1300, 120), (900, 200),
        (600, 100), (300, 180), (150, 350), (400, 550),
        (750, 600), (1100, 650), (1450, 800), (1750, 900),
        (1500, 1000), (1000, 950), (650, 880), (350, 920),
        (200, 1050), (600, 1020), (1200, 1000), (1700, 950),
    ]

    # Visual stimulus events: (onset_seconds, x_ref, y_ref).
    STIMULUS_EVENTS = [
        (4.8, 300, 900),
        (9.5, 1600, 850),
        (15.2, 250, 500),
        (22.7, 1400, 150),
        (28.9, 1000, 900),
        (34.1, 1750, 600),
        (39.6, 500, 1000),
        (46.3, 1300, 300),
        (52.8, 800, 850),
        (58.4, 1650, 750),
        (63.9, 400, 250),
        (70.2, 1550, 1000),
        (76.6, 900, 120),
        (82.1, 250, 750),
        (88.7, 1700, 450),
        (94.3, 600, 980),
        (100.5, 1450, 650),
        (105.8, 350, 350),
        (110.9, 1200, 880),
        (114.7, 1800, 200),
        (117.9, 700, 500),
        (119.2, 1500, 920),
    ]

    TASK_DURATION = 120.0    # seconds
    STIMULUS_DURATION = 0.3  # seconds (visual display of the square)
    RESPONSE_WINDOW = 1.0    # seconds after onset during which A is accepted
    TRACKING_INTERVAL = 7.5  # seconds between distance samples
    POINT_RADIUS = 12
    SQUARE_SIZE = 40
    COLOUR_POINT = (30, 80, 220)
    COLOUR_SQUARE = (220, 50, 50)

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font = pygame.font.SysFont("arial", 30)
        self.font_title = pygame.font.SysFont("arial", 40, bold=True)
        self.font_small = pygame.font.SysFont("arial", 22)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption("Dual Task")
        pygame.mouse.set_visible(1)

        # Scale factors relative to the 1920×1080 reference resolution
        self.scale_x = self.screen_x / 1920.0
        self.scale_y = self.screen_y / 1080.0

        # Pre-compute smooth path and scaled stimulus positions
        self._path = self._build_smooth_path()
        self._stimuli = [
            (t, int(x * self.scale_x), int(y * self.scale_y))
            for t, x, y in self.STIMULUS_EVENTS
        ]

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _catmull_rom_val(t, v0, v1, v2, v3):
        """Scalar Catmull-Rom spline interpolation."""
        t2 = t * t
        t3 = t2 * t
        return 0.5 * (
            2.0 * v1
            + (-v0 + v2) * t
            + (2.0 * v0 - 5.0 * v1 + 4.0 * v2 - v3) * t2
            + (-v0 + 3.0 * v1 - 3.0 * v2 + v3) * t3
        )

    def _build_smooth_path(self):
        """Return a dense list of (x, y) positions using Catmull-Rom splines."""
        pts = [
            (int(x * self.scale_x), int(y * self.scale_y))
            for x, y in self.PATH_POINTS
        ]
        # Close the loop: return to the first point
        pts_loop = pts + [pts[0]]
        n = len(pts_loop) - 1
        points_per_seg = 60
        path = []
        for i in range(n):
            p0 = pts_loop[max(i - 1, 0)]
            p1 = pts_loop[i]
            p2 = pts_loop[i + 1]
            p3 = pts_loop[min(i + 2, n)]
            for j in range(points_per_seg):
                t = j / points_per_seg
                x = self._catmull_rom_val(t, p0[0], p1[0], p2[0], p3[0])
                y = self._catmull_rom_val(t, p0[1], p1[1], p2[1], p3[1])
                path.append((int(x), int(y)))
        return path

    def _get_point_position(self, elapsed):
        """Return the (x, y) of the moving point at *elapsed* seconds."""
        n = len(self._path)
        if n == 0:
            return self.screen_x // 2, self.screen_y // 2
        idx = int((elapsed / self.TASK_DURATION) % 1.0 * n) % n
        return self._path[idx]

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self):
        self._show_instructions()
        tracking_data, response_data = self._run_main_task()
        self._show_end_screen()

        print("- Dual Task complete")

        tracking_df = (
            pd.DataFrame(tracking_data)
            if tracking_data
            else pd.DataFrame(
                columns=[
                    "interval", "time_s", "cursor_x", "cursor_y",
                    "point_x", "point_y", "distance_px",
                ]
            )
        )
        response_df = (
            pd.DataFrame(response_data)
            if response_data
            else pd.DataFrame(
                columns=["stimulus", "stimulus_time_s", "latency_s", "responded"]
            )
        )

        return {"tracking": tracking_df, "responses": response_df}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _show_instructions(self):
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))

        cx = 80
        y = self.screen_y // 2 - 300
        display.text(self.screen, self.font_title, "Dual Task", "center", y)
        y += 70
        display.text(
            self.screen, self.font,
            "Durante esta tarea deberás realizar dos acciones simultáneamente:",
            cx, y,
        )
        y += 50
        display.text(
            self.screen, self.font,
            "1. Sigue con el cursor el punto azul que se mueve por la pantalla.",
            cx, y,
        )
        y += 40
        display.text(
            self.screen, self.font,
            "   Mantén el cursor lo más cerca posible del punto en todo momento.",
            cx, y,
        )
        y += 50
        display.text(
            self.screen, self.font,
            "2. Cuando aparezca un cuadrado rojo en la pantalla,",
            cx, y,
        )
        y += 40
        display.text(
            self.screen, self.font,
            "   presiona la tecla A lo más rápido posible.",
            cx, y,
        )
        y += 50
        display.text(
            self.screen, self.font,
            "La tarea dura 2 minutos y finalizará automáticamente.",
            cx, y,
        )
        y += 80
        display.text_space(self.screen, self.font, "center", y)
        pygame.display.flip()
        display.wait_for_space()

    @staticmethod
    def _record_miss(active_stim, stimuli, response_data):
        """Append a missed-response record for *active_stim* to *response_data*."""
        response_data.append({
            "stimulus": active_stim["idx"] + 1,
            "stimulus_time_s": stimuli[active_stim["idx"]][0],
            "latency_s": None,
            "responded": False,
        })

    def _run_main_task(self):
        pygame.event.clear()
        pygame.mouse.set_visible(1)

        task_start = time.time()
        next_tracking_time = self.TRACKING_INTERVAL
        tracking_data = []
        response_data = []

        active_stim = None  # dict with display/response timing and state
        stim_idx = 0
        clock = pygame.time.Clock()

        while True:
            now = time.time()
            elapsed = now - task_start

            if elapsed >= self.TASK_DURATION:
                # Record any unanswered active stimulus as a miss
                if active_stim is not None and not active_stim["responded"]:
                    self._record_miss(active_stim, self._stimuli, response_data)
                break

            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    elif event.key == K_a:
                        if (
                            active_stim is not None
                            and not active_stim["responded"]
                            and now <= active_stim["response_end"]
                        ):
                            latency = now - active_stim["onset_time"]
                            response_data.append({
                                "stimulus": active_stim["idx"] + 1,
                                "stimulus_time_s": self._stimuli[active_stim["idx"]][0],
                                "latency_s": round(latency, 4),
                                "responded": True,
                            })
                            active_stim["responded"] = True

            # --- Activate new stimuli ---
            while (
                stim_idx < len(self._stimuli)
                and elapsed >= self._stimuli[stim_idx][0]
            ):
                # Record preceding unanswered stimulus as miss before replacing it
                if active_stim is not None and not active_stim["responded"]:
                    self._record_miss(active_stim, self._stimuli, response_data)
                t_ev, sx, sy = self._stimuli[stim_idx]
                active_stim = {
                    "onset_time": now,
                    "display_end": now + self.STIMULUS_DURATION,
                    "response_end": now + self.RESPONSE_WINDOW,
                    "x": sx,
                    "y": sy,
                    "idx": stim_idx,
                    "responded": False,
                }
                stim_idx += 1

            # --- Expire stimulus response window ---
            if active_stim is not None and now >= active_stim["response_end"]:
                if not active_stim["responded"]:
                    self._record_miss(active_stim, self._stimuli, response_data)
                active_stim = None

            # --- Tracking snapshot ---
            if elapsed >= next_tracking_time:
                pt_x, pt_y = self._get_point_position(elapsed)
                mx, my = pygame.mouse.get_pos()
                dist = math.sqrt((mx - pt_x) ** 2 + (my - pt_y) ** 2)
                tracking_data.append({
                    "interval": len(tracking_data) + 1,
                    "time_s": round(elapsed, 2),
                    "cursor_x": mx,
                    "cursor_y": my,
                    "point_x": pt_x,
                    "point_y": pt_y,
                    "distance_px": round(dist, 2),
                })
                next_tracking_time += self.TRACKING_INTERVAL

            # --- Render ---
            pt_x, pt_y = self._get_point_position(elapsed)
            self.screen.blit(self.background, (0, 0))

            # Moving point
            pygame.draw.circle(
                self.screen, self.COLOUR_POINT, (pt_x, pt_y), self.POINT_RADIUS
            )

            # Stimulus square (only during its visual display window)
            if active_stim is not None and now < active_stim["display_end"]:
                rect = pygame.Rect(
                    active_stim["x"] - self.SQUARE_SIZE // 2,
                    active_stim["y"] - self.SQUARE_SIZE // 2,
                    self.SQUARE_SIZE,
                    self.SQUARE_SIZE,
                )
                pygame.draw.rect(self.screen, self.COLOUR_SQUARE, rect)

            remaining = max(0.0, self.TASK_DURATION - elapsed)
            display.text(
                self.screen, self.font_small,
                "Tiempo: {}s".format(math.ceil(remaining)),
                10, 10, (100, 100, 100),
            )

            pygame.display.flip()
            clock.tick(60)

        return tracking_data, response_data

    def _show_end_screen(self):
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font, "Fin de la tarea", "center", "center")
        display.text_space(self.screen, self.font, "center", self.screen_y // 2 + 80)
        pygame.display.flip()
        display.wait_for_space()
