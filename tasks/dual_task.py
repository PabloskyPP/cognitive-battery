import sys
import time
import math
import heapq
import random
import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class DualTask(object):
    """Dual task: continuous motor tracking + visual stimulus response.

    The participant must:
    1. Follow a moving blue point with the mouse cursor.
    2. Press the A key as fast as possible whenever a RED square appears.
       Blue squares are distractors – do NOT press A for them.

    Structure:
    - Practice trial : 20 seconds (4 stimuli: 2 red targets, 2 blue distractors)
    - Main task      : 120 seconds (24 stimuli: 12 red targets, 12 blue distractors)

    Data recorded:
    - Tracking distance at 0.2, 0.4, 1.5, 2.5 s after each stimulus onset → "tracking" DataFrame
    - Response latency / accuracy for each stimulus                        → "responses" DataFrame
    """

    # Procedural trajectory generation (reference resolution: 1920×1080).
    # Designed to mix short/medium displacements, sharp turns (~90° / ~180°),
    # and smooth curves while keeping constant speed through arc-length
    # parameterisation.
    REF_WIDTH = 1920
    REF_HEIGHT = 1080
    PATH_MARGIN = 120
    PATH_EDGE_ZONE = 220
    PATH_POINT_COUNT = 78
    PATH_MIN_SEGMENT = 80
    PATH_MAX_SEGMENT = 250
    PATH_LOOP_DURATION = 95.0  # seconds per full loop (faster than before)

    # Main task stimulus events (24 total): (onset_s, x_ref, y_ref, stimulus_type).
    # 12 target_red  → participant must press A.
    # 12 distractor_blue → participant must NOT press A.
    # ISI ranges from 3.5 to 7.5 seconds.
    # Positions are placed in peripheral screen areas to minimise
    # spatial overlap with the tracking-point path.
    STIMULUS_EVENTS = [
        ( 4.0,  180,  920, "target_red"),
        ( 9.0, 1720,  820, "distractor_blue"),
        (12.5,  280,  480, "target_red"),
        (18.0, 1620,  180, "distractor_blue"),
        (24.5, 1000,  960, "target_red"),
        (29.5, 1760,  580, "distractor_blue"),
        (33.0,  480, 1000, "target_red"),
        (38.5, 1380,  280, "distractor_blue"),
        (43.5,  820,  870, "target_red"),
        (50.0, 1670,  720, "distractor_blue"),
        (55.0,  380,  240, "target_red"),
        (58.5, 1560,  980, "distractor_blue"),
        (64.0,  920,  100, "target_red"),
        (69.0,  230,  740, "distractor_blue"),
        (75.5, 1710,  440, "target_red"),
        (80.5,  580,  990, "distractor_blue"),
        (84.0, 1460,  640, "target_red"),
        (89.5,  340,  340, "distractor_blue"),
        (94.5, 1210,  890, "target_red"),
        (99.5, 1820,  190, "distractor_blue"),
        (103.5,  680,  510, "target_red"),
        (108.0, 1520,  910, "distractor_blue"),
        (111.5,  260,  120, "target_red"),
        (116.0, 1060,  930, "distractor_blue"),
    ]

    # Practice trial stimulus events (4 total): (onset_s, x_ref, y_ref, stimulus_type).
    # 2 target_red, 2 distractor_blue; ISI ~5 s; total duration 20 s.
    PRACTICE_EVENTS = [
        ( 3.0,  300,  920, "target_red"),
        ( 8.5, 1600,  800, "distractor_blue"),
        (13.5,  900,  850, "target_red"),
        (18.0, 1400,  250, "distractor_blue"),
    ]

    TASK_DURATION     = 120.0  # seconds (main task)
    PRACTICE_DURATION =  20.0  # seconds (practice trial)
    STIMULUS_DURATION =   0.3  # seconds (visual display of the square)
    RESPONSE_WINDOW   =   1.0  # seconds after onset during which A is accepted
    POINT_RADIUS      = 12
    SQUARE_SIZE       = 40
    COLOUR_POINT      = (30,  80, 220)   # blue – tracking point
    COLOUR_TARGET     = (220, 50,  50)   # red  – target (press A)
    COLOUR_DISTRACTOR = (50, 100, 220)   # blue – distractor (ignore)

    # Minimum safe pixel distance between tracking point and stimulus centre.
    MIN_STIMULUS_DISTANCE = 80

    # Path arc-length parameterisation settings.
    # More raw samples → more accurate arc-length estimate → smoother constant speed.
    PATH_RAW_SAMPLES_PER_SEG = 300   # sub-samples used for arc-length computation
    PATH_OUTPUT_POINTS_PER_SEG = 60  # arc-length-uniform output points per segment

    # Tracking measurement offsets after stimulus onset: (seconds, phase_label).
    TRACKING_OFFSETS = [
        (0.2, "concurrent"),
        (0.4, "after"),
        (1.5, "unrelated"),
        (2.5, "unrelated"),
    ]

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
        self.scale_x = self.screen_x / self.REF_WIDTH
        self.scale_y = self.screen_y / self.REF_HEIGHT

        # Randomise stimulus-type assignment: balanced 12 target_red / 12 distractor_blue.
        stimulus_types = ["target_red"] * 12 + ["distractor_blue"] * 12
        random.shuffle(stimulus_types)
        shuffled_events = [
            (t, x, y, stype)
            for (t, x, y, _), stype in zip(self.STIMULUS_EVENTS, stimulus_types)
        ]
        self._stimuli = [
            (t, int(x * self.scale_x), int(y * self.scale_y), stype)
            for t, x, y, stype in shuffled_events
        ]
        self._practice_stimuli = [
            (t, int(x * self.scale_x), int(y * self.scale_y), stype)
            for t, x, y, stype in self.PRACTICE_EVENTS
        ]

        # Pre-compute smooth path and regenerate if any event starts too close.
        self._path_points_ref = []
        self._path = []
        max_attempts = 12
        path_ready = False
        for _ in range(max_attempts):
            self._path_points_ref = self._generate_path_points_ref()
            self._path = self._build_smooth_path()
            main_overlaps = self._count_overlaps(self._stimuli)
            practice_overlaps = self._count_overlaps(self._practice_stimuli)
            if main_overlaps == 0 and practice_overlaps == 0:
                path_ready = True
                break
        if not path_ready:
            print(
                "  [DualTask] WARNING: no zero-overlap path found after "
                f"{max_attempts} attempts (main={main_overlaps}, practice={practice_overlaps})"
            )

        self._validate_no_overlap(self._stimuli, "main")
        self._validate_no_overlap(self._practice_stimuli, "practice")

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

    @staticmethod
    def _normalize_angle_diff(angle):
        """Normalize angle to [-180, 180)."""
        return (angle + 180.0) % 360.0 - 180.0

    def _generate_path_points_ref(self):
        """Generate varied trajectory control points in 1920×1080 coordinates."""
        min_x = self.PATH_MARGIN
        max_x = self.REF_WIDTH - self.PATH_MARGIN
        min_y = self.PATH_MARGIN
        max_y = self.REF_HEIGHT - self.PATH_MARGIN
        center_x = self.REF_WIDTH / 2.0
        center_y = self.REF_HEIGHT / 2.0

        x = center_x + random.uniform(-220, 220)
        y = center_y + random.uniform(-150, 150)
        heading = random.uniform(0.0, 360.0)
        points = [(x, y)]

        curve_steps_left = 0
        curve_sign = 1
        total_steps = self.PATH_POINT_COUNT - 1
        forced_count = max(12, int(total_steps * 0.58))
        turn_90_count = max(4, int(forced_count * 0.42))
        turn_180_count = max(2, int(forced_count * 0.23))
        curve_count = max(4, forced_count - turn_90_count - turn_180_count)
        forced_turns = (
            ["turn_90"] * turn_90_count
            + ["turn_180"] * turn_180_count
            + ["curve_start"] * curve_count
        )
        random.shuffle(forced_turns)

        for i in range(self.PATH_POINT_COUNT - 1):
            if curve_steps_left > 0:
                delta = curve_sign * random.uniform(12.0, 24.0)
                curve_steps_left -= 1
            else:
                if i < len(forced_turns):
                    mode = forced_turns[i]
                else:
                    mode = random.choices(
                        ["turn_90", "turn_180", "curve_start", "angled"],
                        weights=[0.28, 0.18, 0.32, 0.22],
                        k=1,
                    )[0]

                if mode == "turn_90":
                    delta = random.choice([-1, 1]) * random.uniform(80.0, 100.0)
                elif mode == "turn_180":
                    delta = random.choice([-1, 1]) * random.uniform(165.0, 195.0)
                elif mode == "curve_start":
                    curve_sign = random.choice([-1, 1])
                    curve_steps_left = random.randint(2, 4)
                    delta = curve_sign * random.uniform(10.0, 20.0)
                    curve_steps_left -= 1
                else:
                    delta = random.choice([-1, 1]) * random.uniform(30.0, 70.0)

            heading = (heading + delta) % 360.0

            distance_to_edge = min(x - min_x, max_x - x, y - min_y, max_y - y)
            segment = random.uniform(self.PATH_MIN_SEGMENT, self.PATH_MAX_SEGMENT)
            if distance_to_edge < self.PATH_EDGE_ZONE:
                segment = random.uniform(self.PATH_MIN_SEGMENT, self.PATH_MAX_SEGMENT * 0.7)
                center_heading = math.degrees(math.atan2(center_y - y, center_x - x))
                steer = self._normalize_angle_diff(center_heading - heading)
                heading = (heading + steer * 0.55) % 360.0

            success = False
            trial_heading = heading
            trial_segment = segment
            for _ in range(8):
                nx = x + math.cos(math.radians(trial_heading)) * trial_segment
                ny = y + math.sin(math.radians(trial_heading)) * trial_segment
                if min_x <= nx <= max_x and min_y <= ny <= max_y:
                    x, y = nx, ny
                    heading = trial_heading
                    success = True
                    break
                center_heading = math.degrees(math.atan2(center_y - y, center_x - x))
                steer = self._normalize_angle_diff(center_heading - trial_heading)
                trial_heading = (trial_heading + steer * 0.65) % 360.0
                trial_segment *= 0.8

            if not success:
                x = min(max(x, min_x), max_x)
                y = min(max(y, min_y), max_y)
                heading = math.degrees(math.atan2(center_y - y, center_x - x)) % 360.0

            points.append((x, y))

        return [(int(round(px)), int(round(py))) for px, py in points]

    def _build_smooth_path(self):
        """Return a dense list of (x, y) positions using Catmull-Rom splines,
        arc-length parameterised so the tracking point moves at constant speed."""
        if not self._path_points_ref:
            return [(self.screen_x // 2, self.screen_y // 2)]

        pts = [
            (int(x * self.scale_x), int(y * self.scale_y))
            for x, y in self._path_points_ref
        ]
        # Close the loop: return to the first point
        pts_loop = pts + [pts[0]]
        n = len(pts_loop) - 1

        # Use many sub-samples per segment for accurate arc-length estimation
        points_per_seg = self.PATH_RAW_SAMPLES_PER_SEG
        raw_path = []
        for i in range(n):
            p0 = pts_loop[max(i - 1, 0)]
            p1 = pts_loop[i]
            p2 = pts_loop[i + 1]
            p3 = pts_loop[min(i + 2, n)]
            for j in range(points_per_seg):
                t = j / points_per_seg
                x = self._catmull_rom_val(t, p0[0], p1[0], p2[0], p3[0])
                y = self._catmull_rom_val(t, p0[1], p1[1], p2[1], p3[1])
                raw_path.append((x, y))

        # Compute cumulative arc lengths along the raw path
        arc_lengths = [0.0]
        for i in range(1, len(raw_path)):
            dx = raw_path[i][0] - raw_path[i - 1][0]
            dy = raw_path[i][1] - raw_path[i - 1][1]
            arc_lengths.append(arc_lengths[-1] + math.sqrt(dx * dx + dy * dy))
        total_length = arc_lengths[-1]

        if total_length == 0:
            # Defensive: can only happen if all PATH_POINTS collapse to a single pixel.
            return [(int(raw_path[0][0]), int(raw_path[0][1]))] if raw_path else [
                (self.screen_x // 2, self.screen_y // 2)
            ]

        # Resample to n_out equally arc-length-spaced points so that
        # equal elapsed-time steps map to equal distances (constant speed).
        n_out = n * self.PATH_OUTPUT_POINTS_PER_SEG
        path = []
        j = 0
        for k in range(n_out):
            target_s = total_length * k / n_out
            while j < len(arc_lengths) - 1 and arc_lengths[j + 1] < target_s:
                j += 1
            if j >= len(raw_path) - 1:
                path.append((int(raw_path[-1][0]), int(raw_path[-1][1])))
            else:
                s0, s1 = arc_lengths[j], arc_lengths[j + 1]
                alpha = (target_s - s0) / (s1 - s0) if s1 > s0 else 0.0
                x = raw_path[j][0] + alpha * (raw_path[j + 1][0] - raw_path[j][0])
                y = raw_path[j][1] + alpha * (raw_path[j + 1][1] - raw_path[j][1])
                path.append((int(x), int(y)))

        return path

    def _get_point_position(self, elapsed):
        """Return the (x, y) of the moving point at *elapsed* seconds."""
        n = len(self._path)
        if n == 0:
            return self.screen_x // 2, self.screen_y // 2
        idx = int(((elapsed / self.PATH_LOOP_DURATION) % 1.0) * n) % n
        return self._path[idx]

    # ------------------------------------------------------------------
    # Overlap validation
    # ------------------------------------------------------------------

    def _count_overlaps(self, stimuli):
        """Count stimuli that are too close to the tracking point at onset."""
        threshold = self.MIN_STIMULUS_DISTANCE
        overlap_count = 0
        for t, sx, sy, _ in stimuli:
            px, py = self._get_point_position(t)
            dist = math.sqrt((px - sx) ** 2 + (py - sy) ** 2)
            if dist < threshold:
                overlap_count += 1
        return overlap_count

    def _validate_no_overlap(self, stimuli, block_name):
        """Log a warning when the tracking point is too close to a stimulus at onset."""
        threshold = self.MIN_STIMULUS_DISTANCE
        for t, sx, sy, stype in stimuli:
            px, py = self._get_point_position(t)
            dist = math.sqrt((px - sx) ** 2 + (py - sy) ** 2)
            if dist < threshold:
                print(
                    "  [DualTask] WARNING ({block_name}): stimulus '{stype}' at "
                    "t={t:.1f}s position ({sx},{sy}) is only {dist:.1f}px from "
                    "tracking point ({px},{py}) — below threshold {thr}px".format(
                        block_name=block_name, stype=stype, t=t,
                        sx=sx, sy=sy, dist=dist, px=px, py=py, thr=threshold,
                    )
                )

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self):
        self._show_instructions()
        self._show_pre_practice_screen()
        self._run_task_block(self._practice_stimuli, self.PRACTICE_DURATION, is_practice=True)
        self._show_post_practice_screen()
        tracking_data, response_data = self._run_task_block(
            self._stimuli, self.TASK_DURATION, is_practice=False
        )
        self._show_end_screen()

        print("- Dual Task complete")

        tracking_df = (
            pd.DataFrame(tracking_data)
            if tracking_data
            else pd.DataFrame(
                columns=[
                    "stimulus", "stimulus_type", "measurement_phase",
                    "time_s", "cursor_x", "cursor_y",
                    "point_x", "point_y", "distance_px",
                ]
            )
        )
        response_df = (
            pd.DataFrame(response_data)
            if response_data
            else pd.DataFrame(
                columns=[
                    "stimulus", "stimulus_type",
                    "stimulus_time_s", "latency_s", "responded",
                ]
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
        y = self.screen_y // 2 - 320
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
            "2. Cuando aparezca un cuadrado ROJO en la pantalla,",
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
            "   CUIDADO. Cuando aparezca un cuadrado AZUL, NO presiones ninguna tecla.",
            cx, y,
        )
        y += 50
        display.text(
            self.screen, self.font,
            "La tarea dura 2 minutos y finaliza automáticamente.",
            cx, y,
        )
        y += 80
        display.text_space(self.screen, self.font, "center", y)
        pygame.display.flip()
        display.wait_for_space()

    def _show_pre_practice_screen(self):
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))
        cy = self.screen_y // 2 - 60
        display.text(
            self.screen, self.font,
            "En la siguiente pantalla (tras pulsar la barra espaciadora)",
            "center", cy,
        )
        cy += 45
        display.text(
            self.screen, self.font,
            "comenzará un ensayo de práctica.",
            "center", cy,
        )
        cy += 80
        display.text_space(self.screen, self.font, "center", cy)
        pygame.display.flip()
        display.wait_for_space()

    def _show_post_practice_screen(self):
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0, 0))
        cy = self.screen_y // 2 - 80
        display.text(
            self.screen, self.font,
            "Ensayo de práctica finalizado.",
            "center", cy,
        )
        cy += 50
        display.text(
            self.screen, self.font,
            "Si tienes alguna duda, consulta al examinador antes de continuar.",
            "center", cy,
        )
        cy += 50
        display.text(
            self.screen, self.font,
            "Si no tienes dudas sobre la tarea, pulsa la barra espaciadora para continuar.",
            "center", cy,
        )
        cy += 80
        display.text_space(self.screen, self.font, "center", cy)
        pygame.display.flip()
        display.wait_for_space()

    @staticmethod
    def _record_miss(active_stim, response_data):
        """Append a missed-response record for the active target stimulus.

        Parameters
        ----------
        active_stim : dict
            Must contain keys ``idx`` (0-based), ``stype`` (stimulus type string),
            and ``onset_elapsed`` (task-relative onset time in seconds).
        response_data : list
            Accumulator list; the miss record is appended in place.
        """
        response_data.append({
            "stimulus": active_stim["idx"] + 1,
            "stimulus_type": active_stim["stype"],
            "stimulus_time_s": active_stim["onset_elapsed"],
            "latency_s": None,
            "responded": False,
        })

    def _run_task_block(self, stimuli, duration, is_practice=False):
        """Run one task block (practice or main).

        Parameters
        ----------
        stimuli : list of (onset_s, x, y, stype) tuples (already scaled).
        duration : float – block length in seconds.
        is_practice : bool – if True the returned data are discarded by the caller.

        Returns
        -------
        tracking_data, response_data : lists of dicts.
        """
        pygame.event.clear()
        pygame.mouse.set_visible(1)

        task_start = time.time()
        tracking_data = []
        response_data = []

        active_stim = None   # dict with display/response timing and state
        stim_idx = 0
        clock = pygame.time.Clock()

        # Priority queue of pending tracking measurements.
        # Each entry: (scheduled_absolute_time, counter, stim_num, stype, phase)
        pending_meas = []
        meas_counter = 0

        while True:
            now = time.time()
            elapsed = now - task_start

            if elapsed >= duration:
                # Record any unanswered stimulus at block end
                if (
                    active_stim is not None
                    and not active_stim["responded"]
                ):
                    self._record_miss(active_stim, response_data)
                break

            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    elif event.key == K_a:
                        if active_stim is not None and not active_stim["responded"]:
                            if now <= active_stim["response_end"]:
                                latency = now - active_stim["onset_time"]
                                response_data.append({
                                    "stimulus": active_stim["idx"] + 1,
                                    "stimulus_type": active_stim["stype"],
                                    "stimulus_time_s": active_stim["onset_elapsed"],
                                    "latency_s": round(latency, 4),
                                    "responded": True,
                                })
                                active_stim["responded"] = True

            # --- Activate new stimuli ---
            while (
                stim_idx < len(stimuli)
                and elapsed >= stimuli[stim_idx][0]
            ):
                # Record preceding unanswered stimulus (miss or correct rejection)
                if (
                    active_stim is not None
                    and not active_stim["responded"]
                ):
                    self._record_miss(active_stim, response_data)

                t_ev, sx, sy, stype = stimuli[stim_idx]
                active_stim = {
                    "onset_time":    now,
                    "onset_elapsed": round(elapsed, 4),
                    "display_end":   now + self.STIMULUS_DURATION,
                    "response_end":  now + self.RESPONSE_WINDOW,
                    "x": sx,
                    "y": sy,
                    "idx": stim_idx,
                    "stype": stype,
                    "responded": False,
                }

                # Schedule the four tracking measurements for this stimulus
                for offset, phase in self.TRACKING_OFFSETS:
                    heapq.heappush(
                        pending_meas,
                        (now + offset, meas_counter, stim_idx + 1, stype, phase),
                    )
                    meas_counter += 1

                stim_idx += 1

            # --- Expire stimulus response window ---
            if active_stim is not None and now >= active_stim["response_end"]:
                if not active_stim["responded"]:
                    self._record_miss(active_stim, response_data)
                active_stim = None

            # --- Process due tracking measurements ---
            while pending_meas and now >= pending_meas[0][0]:
                _, _, stim_num, stim_type, phase = heapq.heappop(pending_meas)
                pt_x, pt_y = self._get_point_position(elapsed)
                mx, my = pygame.mouse.get_pos()
                dist = math.sqrt((mx - pt_x) ** 2 + (my - pt_y) ** 2)
                tracking_data.append({
                    "stimulus":          stim_num,
                    "stimulus_type":     stim_type,
                    "measurement_phase": phase,
                    "time_s":            round(elapsed, 3),
                    "cursor_x":          mx,
                    "cursor_y":          my,
                    "point_x":           pt_x,
                    "point_y":           pt_y,
                    "distance_px":       round(dist, 2),
                })

            # --- Render ---
            pt_x, pt_y = self._get_point_position(elapsed)
            self.screen.blit(self.background, (0, 0))

            # Moving point
            pygame.draw.circle(
                self.screen, self.COLOUR_POINT, (pt_x, pt_y), self.POINT_RADIUS
            )

            # Stimulus square (only during its visual display window)
            if active_stim is not None and now < active_stim["display_end"]:
                colour = (
                    self.COLOUR_TARGET
                    if active_stim["stype"] == "target_red"
                    else self.COLOUR_DISTRACTOR
                )
                rect = pygame.Rect(
                    active_stim["x"] - self.SQUARE_SIZE // 2,
                    active_stim["y"] - self.SQUARE_SIZE // 2,
                    self.SQUARE_SIZE,
                    self.SQUARE_SIZE,
                )
                pygame.draw.rect(self.screen, colour, rect)

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
