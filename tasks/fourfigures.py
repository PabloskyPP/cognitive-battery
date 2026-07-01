import sys

import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class FourFigures(object):
    SHAPES = ("circle", "square", "triangle", "cross")
    RESPONSE_OPTIONS = (
        ("square", "Cuadrado"),
        ("circle", "Círculo"),
        ("triangle", "Triángulo"),
        ("cross", "Cruz"),
    )

    # Fixed predefined sequence for part 1 (32 trials: 8 of each shape, all contour==content)
    _PART1_SEQUENCE = [
        "circle", "square", "triangle", "cross",
        "circle", "triangle", "square", "cross",
        "triangle", "circle", "cross", "square",
        "square", "circle", "cross", "triangle",
        "cross", "triangle", "circle", "square",
        "triangle", "cross", "square", "circle",
        "circle", "cross", "triangle", "square",
        "square", "triangle", "cross", "circle",
    ]

    # Fixed predefined sequence for part 2 (32 trials: 2 of each 4x4 contour-content pair)
    _PART2_SEQUENCE = [
        ("square", "cross"), ("circle", "circle"), ("cross", "triangle"), ("triangle", "square"),
        ("square", "triangle"), ("circle", "cross"), ("cross", "circle"), ("triangle", "triangle"),
        ("square", "square"), ("circle", "triangle"), ("cross", "cross"), ("triangle", "cross"),
        ("square", "circle"), ("circle", "square"), ("cross", "square"), ("triangle", "circle"),
        ("triangle", "circle"), ("cross", "cross"), ("circle", "square"), ("square", "circle"),
        ("triangle", "triangle"), ("cross", "square"), ("circle", "cross"), ("square", "triangle"),
        ("triangle", "square"), ("cross", "circle"), ("circle", "triangle"), ("square", "cross"),
        ("triangle", "cross"), ("cross", "triangle"), ("circle", "circle"), ("square", "square"),
    ]

    # Fixed predefined sequence for part 3 (different order from part 2)
    _PART3_SEQUENCE = [
        ("circle", "square"), ("triangle", "triangle"), ("cross", "circle"), ("square", "cross"),
        ("circle", "circle"), ("triangle", "cross"), ("cross", "square"), ("square", "triangle"),
        ("circle", "cross"), ("triangle", "circle"), ("cross", "cross"), ("square", "square"),
        ("circle", "triangle"), ("triangle", "square"), ("cross", "triangle"), ("square", "circle"),
        ("square", "circle"), ("cross", "triangle"), ("triangle", "square"), ("circle", "triangle"),
        ("square", "square"), ("cross", "cross"), ("triangle", "circle"), ("circle", "cross"),
        ("square", "triangle"), ("cross", "square"), ("triangle", "cross"), ("circle", "circle"),
        ("square", "cross"), ("cross", "circle"), ("triangle", "triangle"), ("circle", "square"),
    ]

    # Fixed predefined sequence for part 4 (32 trials: 2 of each 4x4 pair; red at positions 5, 13, 14)
    # Each pair (contour, content) appears exactly twice.
    _PART4_SEQUENCE = [
        # pos 1-4: rule=contour
        ("circle", "triangle"),    # 1
        ("square", "square"),      # 2
        ("triangle", "cross"),     # 3
        ("cross", "circle"),       # 4
        # pos 5: switch to content (is_red)
        ("circle", "cross"),       # 5  RED
        # pos 6-12: rule=content
        ("triangle", "triangle"),  # 6
        ("square", "circle"),      # 7
        ("cross", "square"),       # 8
        ("circle", "circle"),      # 9
        ("triangle", "square"),    # 10
        ("square", "cross"),       # 11
        ("cross", "triangle"),     # 12
        # pos 13: switch to contour (is_red)
        ("triangle", "circle"),    # 13 RED
        # pos 14: switch to content (is_red)
        ("cross", "cross"),        # 14 RED
        # pos 15-32: rule=content
        ("square", "triangle"),    # 15
        ("circle", "square"),      # 16
        ("triangle", "circle"),    # 17
        ("cross", "cross"),        # 18
        ("circle", "triangle"),    # 19
        ("square", "square"),      # 20
        ("cross", "circle"),       # 21
        ("triangle", "cross"),     # 22
        ("square", "triangle"),    # 23
        ("circle", "square"),      # 24
        ("cross", "square"),       # 25
        ("triangle", "triangle"),  # 26
        ("circle", "cross"),       # 27
        ("square", "circle"),      # 28
        ("cross", "triangle"),     # 29
        ("triangle", "square"),    # 30
        ("circle", "circle"),      # 31
        ("square", "cross"),       # 32
    ]

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font = pygame.font.SysFont("arial", 30)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.font_title = pygame.font.SysFont("arial", 36)
        self.font_label = pygame.font.SysFont("arial", 20)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption("FourFigures")
        pygame.mouse.set_visible(1)

        self.rows = []

    def _draw_shape(self, surface, shape, center, size, color=(0, 0, 0), width=0):
        """Draw a shape on the given surface at center with given size."""
        cx, cy = center
        if shape == "circle":
            pygame.draw.circle(surface, color, (int(cx), int(cy)), int(size), width)
        elif shape == "square":
            rect = pygame.Rect(int(cx - size), int(cy - size), int(2 * size), int(2 * size))
            pygame.draw.rect(surface, color, rect, width)
        elif shape == "triangle":
            points = [
                (int(cx), int(cy - size)),
                (int(cx - size), int(cy + size)),
                (int(cx + size), int(cy + size)),
            ]
            pygame.draw.polygon(surface, color, points, width)
        elif shape == "cross":
            # Filled plus (+) shape as a single continuous polygon (no seam at the intersection)
            bar_t = max(6, int(size * 0.42))
            half_t = bar_t // 2
            s = size
            h = half_t

            points = [
                (cx - h, cy - s),  # top of vertical arm, left
                (cx + h, cy - s),  # top of vertical arm, right
                (cx + h, cy - h),  # inner corner
                (cx + s, cy - h),  # right arm, top
                (cx + s, cy + h),  # right arm, bottom
                (cx + h, cy + h),  # inner corner
                (cx + h, cy + s),  # bottom of vertical arm, right
                (cx - h, cy + s),  # bottom of vertical arm, left
                (cx - h, cy + h),  # inner corner
                (cx - s, cy + h),  # left arm, bottom
                (cx - s, cy - h),  # left arm, top
                (cx - h, cy - h),  # inner corner
            ]
            points = [(int(px), int(py)) for px, py in points]

            if width == 0:
                pygame.draw.polygon(surface, color, points)
            else:
                pygame.draw.polygon(surface, color, points, width)

    def _draw_hierarchical_figure(self, contour, content, is_red=False,
                                   center=None, outer_size=170, inner_size=18,
                                   surface=None):
        """Draw a hierarchical figure (outer contour + single centered inner) on surface."""
        if surface is None:
            surface = self.screen
        fig_color = (200, 0, 0) if is_red else (0, 0, 0)
        if center is None:
            center = (self.screen_x // 2, self.screen_y // 2 - 90)

        self._draw_shape(surface, contour, center, outer_size, fig_color, width=6)
        self._draw_shape(surface, content, center, inner_size, fig_color, width=0)

    def _draw_response_buttons(self, selected_idx=None, is_correct=None):
        button_width = 220
        button_height = 60
        spacing = 25
        total_width = len(self.RESPONSE_OPTIONS) * button_width + (len(self.RESPONSE_OPTIONS) - 1) * spacing
        start_x = (self.screen_x - total_width) // 2
        y = self.screen_y - 170

        button_rects = []
        for idx, (_, label) in enumerate(self.RESPONSE_OPTIONS):
            x = start_x + idx * (button_width + spacing)
            rect = pygame.Rect(x, y, button_width, button_height)
            button_rects.append(rect)

            fill_color = (230, 230, 230)
            if selected_idx == idx and is_correct is not None:
                fill_color = (0, 200, 0) if is_correct else (220, 40, 40)

            pygame.draw.rect(self.screen, fill_color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
            label_surface = self.font_small.render(label, True, (0, 0, 0))
            self.screen.blit(
                label_surface,
                (
                    rect.centerx - label_surface.get_width() // 2,
                    rect.centery - label_surface.get_height() // 2,
                ),
            )

        return button_rects

    def _wrap_lines(self, text, font, max_width):
        """Return list of wrapped line strings."""
        words = text.split()
        lines = []
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines if lines else [""]

    def _draw_arrow(self, start, end, color=(0, 0, 0)):
        """Draw an arrow from start to end with an arrowhead."""
        pygame.draw.line(self.screen, color, start, end, 2)
        # Arrowhead
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(1, (dx * dx + dy * dy) ** 0.5)
        ux, uy = dx / length, dy / length
        # Perpendicular
        px, py = -uy, ux
        head_len = 12
        head_w = 6
        p1 = (int(end[0] - ux * head_len + px * head_w),
              int(end[1] - uy * head_len + py * head_w))
        p2 = (int(end[0] - ux * head_len - px * head_w),
              int(end[1] - uy * head_len - py * head_w))
        pygame.draw.polygon(self.screen, color, [end, p1, p2])

    def _show_text_screen(self, lines, wait_for_space=True, title=None,
                           show_examples=False):
        """Show a screen with text lines, optional title, optional inline examples."""
        self.screen.blit(self.background, (0, 0))

        y = 60
        if title:
            display.text(self.screen, self.font_title, title, "center", y)
            y += 60

        for line in lines:
            if line:
                wrapped = self._wrap_lines(line, self.font, self.screen_x - 100)
                for wline in wrapped:
                    display.text(self.screen, self.font, wline, "center", y)
                    y += 40
            else:
                y += 20

        if show_examples:
            y = self._draw_intro_examples(y)

        if wait_for_space:
            display.text_space(self.screen, self.font, "center", self.screen_y - 70)

        pygame.display.flip()

        if wait_for_space:
            display.wait_for_space()

    def _draw_intro_examples(self, y_start):
        """Draw two example stimuli (Coincidente and Discrepante) with labels and arrows."""
        stim_size = 90   # outer radius
        inner_size = 18  # inner radius
        gap = 60         # gap between label arrows and next block

        # Horizontal positions: split screen into left/right halves
        left_cx = self.screen_x // 4
        right_cx = 3 * self.screen_x // 4

        stim_y = y_start + stim_size + 20

        # Check if we have room; if not, compact slightly
        needed_bottom = stim_y + stim_size + 60 + 70  # stim + label + press space
        if needed_bottom > self.screen_y - 80:
            stim_size = 70
            inner_size = 14
            stim_y = y_start + stim_size + 10

        # Draw left example: circle (outer) + circle (inner) → Coincidente
        self._draw_hierarchical_figure(
            "circle", "circle",
            center=(left_cx, stim_y),
            outer_size=stim_size,
            inner_size=inner_size,
        )
        coin_surf = self.font.render("Coincidente", True, (0, 0, 0))
        self.screen.blit(coin_surf, (left_cx - coin_surf.get_width() // 2, stim_y + stim_size + 12))

        # Draw right example: square (outer) + triangle (inner) → Discrepante
        self._draw_hierarchical_figure(
            "square", "triangle",
            center=(right_cx, stim_y),
            outer_size=stim_size,
            inner_size=inner_size,
        )
        disc_surf = self.font.render("Discrepante", True, (0, 0, 0))
        self.screen.blit(disc_surf, (right_cx - disc_surf.get_width() // 2, stim_y + stim_size + 12))

        # Draw arrows on the right example: one pointing to outer, one to inner
        arrow_color = (60, 60, 180)
        label_font = self.font_label

        # Arrow for outer figure (from right side, pointing to the outer edge)
        outer_tip = (right_cx + stim_size - 5, stim_y)
        arrow_ext_start = (right_cx + stim_size + 70, stim_y - 30)
        self._draw_arrow(arrow_ext_start, outer_tip, arrow_color)
        ext_surf = label_font.render("Figura externa", True, arrow_color)
        self.screen.blit(ext_surf, (arrow_ext_start[0] - 5, arrow_ext_start[1] - ext_surf.get_height() - 2))

        # Arrow for inner figure (from below-right, pointing to center)
        inner_tip = (right_cx + inner_size + 4, stim_y + inner_size + 4)
        arrow_int_start = (right_cx + stim_size + 70, stim_y + 40)
        self._draw_arrow(arrow_int_start, inner_tip, arrow_color)
        int_surf = label_font.render("Figura interna", True, arrow_color)
        self.screen.blit(int_surf, (arrow_int_start[0] - 5, arrow_int_start[1]))

        return stim_y + stim_size + coin_surf.get_height() + gap

    def _run_trial(self, trial, part, target_rule, trial_type):
        contour = trial["contour"]
        content = trial["content"]
        is_red = trial.get("is_red", False)

        correct_response = contour if target_rule == "contour" else content

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        if part == 4:
            regla = "contorno" if target_rule == "contour" else "contenido"
        self._draw_hierarchical_figure(contour, content, is_red=is_red)
        button_rects = self._draw_response_buttons()
        pygame.display.flip()

        selected_idx = None
        selected_shape = None

        while selected_idx is None:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_F12:
                    sys.exit(0)
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    for idx, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            selected_idx = idx
                            selected_shape = self.RESPONSE_OPTIONS[idx][0]
                            break

        is_correct = selected_shape == correct_response

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        if part == 4:
            regla = "contorno" if target_rule == "contour" else "contenido"
            display.text(self.screen, self.font_small, f"Norma: {regla}", self.screen_x - 260, 30)
        self._draw_hierarchical_figure(contour, content, is_red=is_red)
        self._draw_response_buttons(selected_idx=selected_idx, is_correct=is_correct)
        pygame.display.flip()

        display.wait(200)

        self.rows.append(
            {
                "part": part,
                "trial_type": trial_type,
                "contour": contour,
                "content": content,
                "discrepancy": "yes" if contour != content else "no",
                "response_given": "yes" if selected_shape is not None else "no",
                "correct_response": correct_response,
                "correct": "yes" if is_correct else "no",
            }
        )

    def _run_trials(self, trials, part, initial_rule):
        rule = initial_rule
        for trial in trials:
            if trial.get("switch_before", False):
                rule = "content" if rule == "contour" else "contour"

            target_rule = trial.get("target", rule)
            self._run_trial(trial, part, target_rule, trial["trial_type"])

    def _create_part1_experimental(self):
        return [
            {"contour": s, "content": s, "trial_type": "experimental"}
            for s in self._PART1_SEQUENCE
        ]

    def _create_part2_experimental(self):
        return [
            {"contour": c, "content": n, "trial_type": "experimental"}
            for c, n in self._PART2_SEQUENCE
        ]

    def _create_part3_experimental(self):
        return [
            {"contour": c, "content": n, "trial_type": "experimental"}
            for c, n in self._PART3_SEQUENCE
        ]

    def _create_part4_experimental(self):
        RED_POSITIONS = {5, 13, 14}  # 1-indexed
        trials = []
        for idx, (contour, content) in enumerate(self._PART4_SEQUENCE, start=1):
            is_red = idx in RED_POSITIONS
            trials.append(
                {
                    "contour": contour,
                    "content": content,
                    "is_red": is_red,
                    "switch_before": is_red,
                    "trial_type": "experimental",
                }
            )
        return trials

    # ------------------------------------------------------------------ #
    #  Practice integrated screen helpers                                  #
    # ------------------------------------------------------------------ #

    def _compute_practice_rules(self, trials, initial_rule):
        """Return list of (target_rule, correct_response) for each practice trial."""
        rule = initial_rule
        result = []
        for trial in trials:
            if trial.get("switch_before", False):
                rule = "content" if rule == "contour" else "contour"
            target = trial.get("target", rule)
            correct = trial["contour"] if target == "contour" else trial["content"]
            result.append((target, correct))
        return result

    def _show_practice_integrated_screen(self, instruction_lines, practice_trials,
                                          part, initial_rule, footer_lines,
                                          two_rows=False):
        """
        Show instruction text, inline practice stimuli with interactive response buttons,
        persistent feedback, and a footer.  The practice stimuli and buttons are rendered
        at the bottom of the screen.
        """
        rules_info = self._compute_practice_rules(practice_trials, initial_rule)
        n = len(practice_trials)

        # Layout constants
        STIM_OUTER = 60     # outer radius of practice stimulus
        STIM_INNER = 12     # inner radius
        BTN_W = 72
        BTN_H = 26
        BTN_SP = 4          # spacing between buttons
        STIM_BTN_GAP = 10   # gap between stim bottom and buttons
        ROW_GAP = 18        # gap between two stimulus rows (part4)
        FOOTER_LINE_H = 34
        BOTTOM_MARGIN = 60  # space for press-space text at very bottom

        n_per_row = 4
        if two_rows:
            rows_data = [practice_trials[:4], practice_trials[4:]]
            rules_rows = [rules_info[:4], rules_info[4:]]
        else:
            rows_data = [practice_trials]
            rules_rows = [rules_info]

        # Total height of one stimulus+button row
        single_row_h = (STIM_OUTER * 2) + STIM_BTN_GAP + BTN_H

        # Height of footer block
        footer_total_h = len(footer_lines) * FOOTER_LINE_H + 10

        # Height of ALL stim rows
        n_rows = len(rows_data)
        stims_total_h = n_rows * single_row_h + (n_rows - 1) * ROW_GAP

        # Bottom section total height
        bottom_h = stims_total_h + 20 + footer_total_h + BOTTOM_MARGIN

        # Y where bottom section starts
        bottom_start_y = self.screen_y - bottom_h

        # Compute stimulus center Y positions
        stim_center_ys = []
        y_cursor = bottom_start_y
        for _ in range(n_rows):
            stim_center_ys.append(y_cursor + STIM_OUTER)
            y_cursor += single_row_h + ROW_GAP

        # Compute X positions for each row (4 per row, evenly spaced)
        section_w = self.screen_x // n_per_row
        stim_center_xs = [section_w // 2 + i * section_w for i in range(n_per_row)]

        # Response state
        responses = [None] * n       # selected shape index (0-3)
        correct_flags = [None] * n   # True/False

        def draw_screen(show_footer):
            self.screen.blit(self.background, (0, 0))

            # --- Instruction text ---
            y = 50
            for line in instruction_lines:
                if line:
                    wrapped = self._wrap_lines(line, self.font, self.screen_x - 100)
                    for wline in wrapped:
                        surf = self.font.render(wline, True, (0, 0, 0))
                        self.screen.blit(surf, ((self.screen_x - surf.get_width()) // 2, y))
                        y += 38
                else:
                    y += 18

            # --- Stimuli and response buttons ---
            btn_rects_all = []   # flat list of Rect, one per button per stimulus
            for row_i, (row_trials, row_rules) in enumerate(zip(rows_data, rules_rows)):
                scx_y = stim_center_ys[row_i]
                for col_i, (trial, (_, _correct)) in enumerate(zip(row_trials, row_rules)):
                    stim_idx = row_i * n_per_row + col_i
                    cx = stim_center_xs[col_i]
                    cy = scx_y

                    # Draw stimulus
                    is_red = trial.get("is_red", False)
                    color = (200, 0, 0) if is_red else (0, 0, 0)
                    self._draw_shape(self.screen, trial["contour"], (cx, cy),
                                     STIM_OUTER, color, width=4)
                    self._draw_shape(self.screen, trial["content"], (cx, cy),
                                     STIM_INNER, color, width=0)

                    # Draw 4 response buttons below stimulus
                    total_btn_w = len(self.RESPONSE_OPTIONS) * BTN_W + (len(self.RESPONSE_OPTIONS) - 1) * BTN_SP
                    btn_start_x = cx - total_btn_w // 2
                    btn_y = cy + STIM_OUTER + STIM_BTN_GAP

                    row_btn_rects = []
                    for btn_i, (shape, label) in enumerate(self.RESPONSE_OPTIONS):
                        bx = btn_start_x + btn_i * (BTN_W + BTN_SP)
                        rect = pygame.Rect(bx, btn_y, BTN_W, BTN_H)
                        row_btn_rects.append(rect)

                        fill = (230, 230, 230)
                        if responses[stim_idx] == btn_i and correct_flags[stim_idx] is not None:
                            fill = (0, 200, 0) if correct_flags[stim_idx] else (220, 40, 40)

                        pygame.draw.rect(self.screen, fill, rect)
                        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                        lbl = self.font_label.render(label, True, (0, 0, 0))
                        self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                                               rect.centery - lbl.get_height() // 2))
                    btn_rects_all.append(row_btn_rects)

            # --- Footer ---
            if show_footer:
                footer_y = self.screen_y - BOTTOM_MARGIN - footer_total_h + 10
                for fline in footer_lines:
                    if fline:
                        wrapped = self._wrap_lines(fline, self.font_small, self.screen_x - 100)
                        for wline in wrapped:
                            fs = self.font_small.render(wline, True, (0, 0, 0))
                            self.screen.blit(fs, ((self.screen_x - fs.get_width()) // 2, footer_y))
                            footer_y += FOOTER_LINE_H
                    else:
                        footer_y += 12
                display.text_space(self.screen, self.font, "center", self.screen_y - 45)

            pygame.display.flip()
            return btn_rects_all

        all_answered = False
        btn_rects_all = draw_screen(show_footer=False)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    elif event.key == K_SPACE and all_answered:
                        waiting = False
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    for stim_idx, btn_row in enumerate(btn_rects_all):
                        for btn_i, rect in enumerate(btn_row):
                            if rect.collidepoint(pos) and responses[stim_idx] is None:
                                selected_shape = self.RESPONSE_OPTIONS[btn_i][0]
                                _, correct_shape = rules_info[stim_idx]
                                responses[stim_idx] = btn_i
                                correct_flags[stim_idx] = (selected_shape == correct_shape)
                                all_answered = all(r is not None for r in responses)
                                btn_rects_all = draw_screen(show_footer=all_answered)
                                break

        # Record practice trial results
        for stim_idx, (trial, (target_rule, correct_shape)) in enumerate(
                zip(practice_trials, rules_info)):
            resp_idx = responses[stim_idx]
            selected_shape = self.RESPONSE_OPTIONS[resp_idx][0] if resp_idx is not None else None
            self.rows.append(
                {
                    "part": part,
                    "trial_type": "practice",
                    "contour": trial["contour"],
                    "content": trial["content"],
                    "discrepancy": "yes" if trial["contour"] != trial["content"] else "no",
                    "response_given": "yes" if selected_shape is not None else "no",
                    "correct_response": correct_shape,
                    "correct": "yes" if correct_flags[stim_idx] else "no",
                }
            )

    def run(self):
        # ---- Intro screen with inline examples ----
        self._show_text_screen(
            [
                "Esta prueba consta de 4 partes, en las que las instrucciones sobre el estímulo hacia el que la persona tiene que enfocar su atención y responder (figuras internas o externa) cambian en cada parte.",
                "",
                "En las 4 partes se presentan una serie de estímulos: una figura pequeña interna contenida en una figura externa más grande (contorno) con una forma coincidente o discrepante.",
                "",
                "Ejemplo de estímulos:",
            ],
            title="FourFigures",
            show_examples=True,
        )
        # Continue to the next page of intro instructions.
        self._show_text_screen(
            [
                "Para cada estímulo tienes que indicar la forma de la figura que se presenta y sobre la que se está preguntando.",
                "",
                "Tras responder al estímulo actual se pasa al siguiente y así hasta completar toda la serie de cada parte.",
                "",
                "Al empezar cada nueva parte primero se presentan las nuevas instrucciones.",
                "",
                "Tienes que indicar la forma de la figura de la que se pregunta de la forma más rápida y precisa posible.",
                "",
                "Pulsa <<barra espaciadora>> para continuar.",
            ],
        )

        # ---- Part 1 ----
        part1_practice = [
            {"contour": "circle", "content": "circle", "trial_type": "practice"},
            {"contour": "square", "content": "square", "trial_type": "practice"},
            {"contour": "triangle", "content": "triangle", "trial_type": "practice"},
            {"contour": "cross", "content": "cross", "trial_type": "practice"},
        ]
        self._show_practice_integrated_screen(
            instruction_lines=[
                "Primera parte",
                "",
                "En esta parte tienes que indicar la forma de las figuras que aparecen, la cual es la misma para la figura exterior y la figura pequeña interna.",
                "",
                "Como ejemplo de práctica indica para las siguientes 4 figuras la forma que corresponde en cada una.",
            ],
            practice_trials=part1_practice,
            part=1,
            initial_rule="contour",
            footer_lines=[
                "Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación.",
                "",
                "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar.",
            ],
        )
        self._run_trials(self._create_part1_experimental(), part=1, initial_rule="contour")

        # ---- Part 2 ----
        part2_practice = [
            {"contour": "square", "content": "cross", "trial_type": "practice"},
            {"contour": "circle", "content": "circle", "trial_type": "practice"},
            {"contour": "cross", "content": "triangle", "trial_type": "practice"},
            {"contour": "triangle", "content": "square", "trial_type": "practice"},
        ]
        self._show_practice_integrated_screen(
            instruction_lines=[
                "La parte 1 ha terminado.",
                "",
                "A continuación empieza la parte 2.",
                "",
                "Aquí la figura del contorno y la del interior pueden no ser la misma.",
                "",
                "Tu tarea es indicar la forma del contorno, la figura más grande y exterior, e ignorar la forma de la figura pequeña de su interior.",
                "",
                "Como ejemplo de práctica indica para las siguientes 4 figuras la forma que corresponde en cada una.",
            ],
            practice_trials=part2_practice,
            part=2,
            initial_rule="contour",
            footer_lines=[
                "Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación.",
                "",
                "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar.",
            ],
        )
        self._run_trials(self._create_part2_experimental(), part=2, initial_rule="contour")

        # ---- Part 3 ----
        part3_practice = [
            {"contour": "circle", "content": "triangle", "trial_type": "practice"},
            {"contour": "square", "content": "square", "trial_type": "practice"},
            {"contour": "cross", "content": "cross", "trial_type": "practice"},
            {"contour": "triangle", "content": "cross", "trial_type": "practice"},
        ]
        self._show_practice_integrated_screen(
            instruction_lines=[
                "La parte 2 ha terminado.",
                "",
                "A continuación empieza la parte 3.",
                "",
                "De nuevo, aquí la figura del contorno y la del interior pueden no ser la misma.",
                "",
                "Esta vez tu tarea es indicar la forma del contenido, la figura pequeña del interior, e ignorar la forma del contorno.",
                "",
                "Como ejemplo de práctica indica para las siguientes 4 figuras la forma que corresponde en cada una.",
            ],
            practice_trials=part3_practice,
            part=3,
            initial_rule="content",
            footer_lines=[
                "Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación.",
                "",
                "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar.",
            ],
        )
        self._run_trials(self._create_part3_experimental(), part=3, initial_rule="content")

        # ---- Part 4 ----
        part4_practice = [
            {"contour": "circle", "content": "triangle", "is_red": False, "switch_before": False, "trial_type": "practice"},
            {"contour": "square", "content": "square", "is_red": False, "switch_before": False, "trial_type": "practice"},
            {"contour": "circle", "content": "triangle", "is_red": True, "switch_before": True, "trial_type": "practice"},
            {"contour": "triangle", "content": "cross", "is_red": False, "switch_before": False, "trial_type": "practice"},
            {"contour": "cross", "content": "cross", "is_red": True, "switch_before": True, "trial_type": "practice"},
            {"contour": "circle", "content": "circle", "is_red": False, "switch_before": False, "trial_type": "practice"},
            {"contour": "triangle", "content": "cross", "is_red": False, "switch_before": False, "trial_type": "practice"},
            {"contour": "cross", "content": "square", "is_red": False, "switch_before": False, "trial_type": "practice"},
        ]
        self._show_practice_integrated_screen(
            instruction_lines=[
                "La parte 3 ha terminado.",
                "",
                "A continuación empieza la parte 4.",
                "",
                "De nuevo, aquí la figura del contorno y la del interior pueden no ser la misma.",
                "",
                "Además en algunas ocasiones la figura aparecerá en color rojo. Esta indica un cambio en la norma de respuesta.",
                "",
                "Al principio empiezas teniendo que indicar la forma del contorno.",
                "",
                "Cuando aparezca una figura roja debes cambiar e indicar la forma contraria. Cada nueva figura roja vuelve a invertir la norma.",
                "",
                "Como ejemplo de práctica indica para las siguientes 8 figuras la forma que corresponde en cada una.",
            ],
            practice_trials=part4_practice,
            part=4,
            initial_rule="contour",
            footer_lines=[
                "Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación.",
                "",
                "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar.",
            ],
            two_rows=True,
        )
        self._run_trials(self._create_part4_experimental(), part=4, initial_rule="contour")

        self._show_text_screen(["Fin de la tarea.", "", "Pulsa la barra espaciadora para continuar."])

        print("- FourFigures complete")

        return pd.DataFrame(self.rows)
