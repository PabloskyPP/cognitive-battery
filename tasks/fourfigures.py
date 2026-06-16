import os
import random
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

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font = pygame.font.SysFont("arial", 30)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.font_title = pygame.font.SysFont("arial", 36)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption("FourFigures")
        pygame.mouse.set_visible(1)

        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.figure_image_path = os.path.join(self.base_dir, "images", "FourFigures", "figura.png")

        self.rows = []

    def _draw_shape(self, shape, center, size, color=(0, 0, 0), width=0):
        cx, cy = center
        if shape == "circle":
            pygame.draw.circle(self.screen, color, (int(cx), int(cy)), int(size), width)
        elif shape == "square":
            rect = pygame.Rect(int(cx - size), int(cy - size), int(2 * size), int(2 * size))
            pygame.draw.rect(self.screen, color, rect, width)
        elif shape == "triangle":
            points = [
                (int(cx), int(cy - size)),
                (int(cx - size), int(cy + size)),
                (int(cx + size), int(cy + size)),
            ]
            pygame.draw.polygon(self.screen, color, points, width)
        elif shape == "cross":
            thickness = max(4, int(size / 3)) if width == 0 else max(3, width)
            pygame.draw.line(
                self.screen,
                color,
                (int(cx - size), int(cy - size)),
                (int(cx + size), int(cy + size)),
                thickness,
            )
            pygame.draw.line(
                self.screen,
                color,
                (int(cx + size), int(cy - size)),
                (int(cx - size), int(cy + size)),
                thickness,
            )

    def _draw_hierarchical_figure(self, contour, content, is_red=False):
        fig_color = (200, 0, 0) if is_red else (0, 0, 0)
        center = (self.screen_x // 2, self.screen_y // 2 - 90)

        self._draw_shape(contour, center, 170, fig_color, width=6)

        offsets = (-70, 0, 70)
        for oy in offsets:
            for ox in offsets:
                self._draw_shape(content, (center[0] + ox, center[1] + oy), 16, fig_color, width=0)

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

    def _show_text_screen(self, lines, wait_for_space=True, title=None, show_figure_image=False):
        self.screen.blit(self.background, (0, 0))

        y = 100
        if title:
            display.text(self.screen, self.font_title, title, "center", y)
            y += 70

        for line in lines:
            if line:
                display.text(self.screen, self.font, line, "center", y)
                y += 45
            else:
                y += 22

        if show_figure_image and os.path.exists(self.figure_image_path):
            try:
                img = pygame.image.load(self.figure_image_path)
                max_w = min(420, int(self.screen_x * 0.35))
                max_h = min(320, int(self.screen_y * 0.3))
                w, h = img.get_size()
                scale = min(max_w / float(w), max_h / float(h), 1.0)
                img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
                self.screen.blit(img, (self.screen_x // 2 - img.get_width() // 2, self.screen_y - img.get_height() - 140))
            except Exception:
                pass

        if wait_for_space:
            display.text_space(self.screen, self.font, "center", self.screen_y - 70)

        pygame.display.flip()

        if wait_for_space:
            display.wait_for_space()

    def _run_trial(self, trial, part, target_rule, trial_type):
        contour = trial["contour"]
        content = trial["content"]
        is_red = trial.get("is_red", False)

        correct_response = contour if target_rule == "contour" else content

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        if part == 4:
            regla = "contorno" if target_rule == "contour" else "contenido"
            display.text(self.screen, self.font_small, f"Norma: {regla}", self.screen_x - 260, 30)
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
        trials = []
        for shape in self.SHAPES:
            for _ in range(8):
                trials.append({"contour": shape, "content": shape, "trial_type": "experimental"})
        random.shuffle(trials)
        return trials

    def _create_part2_or_3_experimental(self):
        trials = []
        for contour in self.SHAPES:
            for content in self.SHAPES:
                trials.append({"contour": contour, "content": content, "trial_type": "experimental"})
                trials.append({"contour": contour, "content": content, "trial_type": "experimental"})
        random.shuffle(trials)
        return trials

    def _create_part4_experimental(self):
        contour_pool = []
        content_pool = []
        for contour in self.SHAPES:
            for content in self.SHAPES:
                contour_pool.append((contour, content))
                content_pool.append((contour, content))

        random.shuffle(contour_pool)
        random.shuffle(content_pool)

        switch_indices = {5, 13, 24}
        current_rule = "contour"
        trials = []

        for idx in range(1, 33):
            switch_before = idx in switch_indices
            if switch_before:
                current_rule = "content" if current_rule == "contour" else "contour"

            target = current_rule
            if target == "contour":
                contour, content = contour_pool.pop()
            else:
                contour, content = content_pool.pop()

            trials.append(
                {
                    "contour": contour,
                    "content": content,
                    "is_red": idx in switch_indices,
                    "switch_before": switch_before,
                    "target": target,
                    "trial_type": "experimental",
                }
            )

        return trials

    def run(self):
        self._show_text_screen(
            [
                "Esta prueba consta de 4 partes, en las que las instrucciones sobre el estímulo hacia el que la persona tiene que enfocar su atención y responder cambian.",
                "",
                "En las 4 partes se presentan una serie de estímulos: figuras pequeñas contenidas en un contorno más grande con una forma coincidente o discrepante.",
                "",
                "Para cada estímulo tienes que indicar la forma de la figura que se presenta y sobre la que se está preguntando (diferente en cada parte).",
                "",
                "Tras responder al estímulo actual se pasa al siguiente y así hasta completar toda la serie de cada parte.",
                "",
                "Al empezar una nueva parte se presentarán nuevas instrucciones.",
                "",
                "Tienes que indicar la forma de la figura de la que se pregunta de la forma más rápida y precisa posible.",
                "",
                "Pulsa la barra espaciadora para continuar.",
            ],
            title="FourFigures",
            show_figure_image=True,
        )

        part1_practice = [
            {"contour": "circle", "content": "circle", "trial_type": "practice"},
            {"contour": "square", "content": "square", "trial_type": "practice"},
            {"contour": "triangle", "content": "triangle", "trial_type": "practice"},
            {"contour": "cross", "content": "cross", "trial_type": "practice"},
        ]

        self._show_text_screen(
            [
                "Primera parte",
                "",
                "En esta parte tienes que indicar la forma de las figuras que aparecen, la cual es la misma para el contorno exterior y las figuras pequeñas contenidas en su interior.",
                "",
                "Como ejemplo de práctica indica en las siguientes 4 figuras la forma que corresponde en cada una.",
            ]
        )
        self._run_trials(part1_practice, part=1, initial_rule="contour")
        self._show_text_screen(
            [
                "Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación.",
                "",
                "Si no tienes ninguna duda pulsa la barra espaciadora para empezar.",
            ]
        )
        self._run_trials(self._create_part1_experimental(), part=1, initial_rule="contour")

        part2_practice = [
            {"contour": "square", "content": "cross", "trial_type": "practice"},
            {"contour": "circle", "content": "circle", "trial_type": "practice"},
            {"contour": "cross", "content": "triangle", "trial_type": "practice"},
            {"contour": "triangle", "content": "square", "trial_type": "practice"},
        ]
        self._show_text_screen(
            [
                "La parte 1 ha terminado.",
                "",
                "A continuación empieza la parte 2.",
                "",
                "Aquí la figura del contorno y las del interior pueden no ser la misma.",
                "",
                "Tu tarea es indicar la forma del contorno, la figura más grande y exterior, e ignorar la forma de las figuras pequeñas de su interior.",
            ]
        )
        self._run_trials(part2_practice, part=2, initial_rule="contour")
        self._show_text_screen(["Pulsa la barra espaciadora para empezar la parte experimental."])
        part2_experimental = self._create_part2_or_3_experimental()
        self._run_trials(part2_experimental, part=2, initial_rule="contour")

        part3_practice = [
            {"contour": "circle", "content": "triangle", "trial_type": "practice"},
            {"contour": "square", "content": "square", "trial_type": "practice"},
            {"contour": "cross", "content": "cross", "trial_type": "practice"},
            {"contour": "triangle", "content": "cross", "trial_type": "practice"},
        ]
        self._show_text_screen(
            [
                "La parte 2 ha terminado.",
                "",
                "A continuación empieza la parte 3.",
                "",
                "De nuevo, aquí la figura del contorno y las del interior pueden no ser la misma.",
                "",
                "Esta vez tu tarea es indicar la forma del contenido, las figuras pequeñas del interior, e ignorar la forma del contorno.",
            ]
        )
        self._run_trials(part3_practice, part=3, initial_rule="content")
        self._show_text_screen(["Pulsa la barra espaciadora para empezar la parte experimental."])
        part3_experimental = self._create_part2_or_3_experimental()
        part2_sequence = [(trial["contour"], trial["content"]) for trial in part2_experimental]
        max_attempts = 20
        attempts = 0
        while (
            [
                (trial["contour"], trial["content"]) for trial in part3_experimental
            ]
            == part2_sequence
            and attempts < max_attempts
        ):
            part3_experimental = self._create_part2_or_3_experimental()
            attempts += 1

        if attempts == max_attempts:
            # Keep all trials but force a different sequence if repeated shuffles match.
            part3_experimental = part3_experimental[1:] + part3_experimental[:1]
        self._run_trials(part3_experimental, part=3, initial_rule="content")

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
        self._show_text_screen(
            [
                "La parte 3 ha terminado.",
                "",
                "A continuación empieza la parte 4.",
                "",
                "De nuevo, aquí la figura del contorno y las del interior pueden no ser la misma.",
                "",
                "Además en algunas ocasiones la figura aparecerá en color rojo.",
                "",
                "Esta indica un cambio en la norma de respuesta.",
                "",
                "Al principio empiezas teniendo que indicar la forma del contorno.",
                "",
                "Cuando aparezca una figura roja debes cambiar e indicar la forma contraria a la que estabas indicando.",
                "",
                "Cada nueva figura roja vuelve a invertir la norma de respuesta.",
            ]
        )
        self._run_trials(part4_practice, part=4, initial_rule="contour")
        self._show_text_screen(["Pulsa la barra espaciadora para empezar la parte experimental."])
        self._run_trials(self._create_part4_experimental(), part=4, initial_rule="contour")

        self._show_text_screen(["Fin de la tarea.", "", "Pulsa la barra espaciadora para continuar."], wait_for_space=True)

        print("- FourFigures complete")

        return pd.DataFrame(self.rows)
