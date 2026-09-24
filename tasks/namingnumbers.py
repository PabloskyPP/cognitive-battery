import random
import sys
import time

import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class NamingNumbers(object):
    DIGITS = tuple(range(1, 10))
    KEY_TO_DIGIT = {getattr(pygame, f"K_{digit}"): digit for digit in DIGITS}
    RED_POSITIONS = {5, 10, 14, 19, 23, 29}

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
        pygame.display.set_caption("NamingNumbers")
        pygame.mouse.set_visible(1)
        self.rows = []

    def _generate_stimulus(self, kind):
        """Return one random dots or repeated-numbers stimulus."""
        if kind == "dots":
            return {"kind": kind, "amount": random.randint(1, 9), "identity": None}
        if kind == "numbers":
            return {
                "kind": kind,
                "amount": random.randint(1, 9),
                "identity": random.randint(1, 9),
            }
        raise ValueError(f"Unknown stimulus kind: {kind}")

    def _draw_stimulus(self, stimulus, is_red=False, center=None, size=170, surface=None):
        if surface is None:
            surface = self.screen
        if center is None:
            center = (self.screen_x // 2, self.screen_y // 2 - 90)
        cx, cy = center
        color = (200, 0, 0) if is_red else (0, 0, 0)
        rect = pygame.Rect(int(cx - size), int(cy - size), int(2 * size), int(2 * size))
        pygame.draw.rect(surface, color, rect, 6)
        if stimulus["kind"] == "dots":
            dot_radius = max(5, int(size * 0.07))
            positions = [
                (-0.5, -0.5), (0, -0.5), (0.5, -0.5),
                (-0.5, 0), (0, 0), (0.5, 0),
                (-0.5, 0.5), (0, 0.5), (0.5, 0.5),
            ]
            for px, py in positions[:stimulus["amount"]]:
                pygame.draw.circle(surface, color,
                                   (int(cx + px * size), int(cy + py * size)), dot_radius)
        else:
            digit = self.font_title.render(str(stimulus["identity"]), True, color)
            for row in range(stimulus["amount"]):
                y = cy - (stimulus["amount"] - 1) * 18 + row * 36
                surface.blit(digit, (cx - digit.get_width() // 2,
                                     int(y - digit.get_height() // 2)))

    def _wrap_lines(self, text, font, max_width):
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

    def _show_text_screen(self, lines, wait_for_space=True, title=None):
        self.screen.blit(self.background, (0, 0))
        y = 60
        if title:
            display.text(self.screen, self.font_title, title, "center", y)
            y += 60
        for line in lines:
            if line:
                for wrapped in self._wrap_lines(line, self.font, self.screen_x - 100):
                    display.text(self.screen, self.font, wrapped, "center", y)
                    y += 40
            else:
                y += 20
        if wait_for_space:
            display.text_space(self.screen, self.font, "center", self.screen_y - 70)
        pygame.display.flip()
        if wait_for_space:
            display.wait_for_space()

    def _target_value(self, trial, target_rule):
        return trial["amount"] if target_rule == "amount" else trial["identity"]

    def _run_trial(self, trial, part, target_rule, trial_type):
        correct_response = self._target_value(trial, target_rule)
        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        self._draw_stimulus(trial, is_red=trial.get("is_red", False))
        pygame.display.flip()
        response = None
        response_start_time = time.time()
        while response is None:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                if event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    response = self.KEY_TO_DIGIT.get(event.key)
        response_latency = round((time.time() - response_start_time) * 1000)
        is_correct = response == correct_response
        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        self._draw_stimulus(trial, is_red=trial.get("is_red", False))
        response_color = (0, 180, 0) if is_correct else (220, 40, 40)
        response_surface = self.font_title.render(str(response), True, response_color)
        self.screen.blit(response_surface, (self.screen_x // 2 - response_surface.get_width() // 2,
                                            self.screen_y - 120))
        pygame.display.flip()
        display.wait(200)
        self.rows.append({
            "part": part,
            "trial_type": trial_type,
            "target_type": target_rule,
            "stimulus_digit": trial["identity"],
            "stimulus_count": trial["amount"],
            "response": response,
            "response_given": "yes",
            "correct_response": correct_response,
            "correct": "yes" if is_correct else "no",
            "rt": response_latency,
            "is_switch_trial": "yes" if trial.get("is_red", False) else "no",
        })

    def _run_trials(self, trials, part, initial_rule):
        rule = initial_rule
        for trial in trials:
            if trial.get("switch_before", False):
                rule = "identity" if rule == "amount" else "amount"
            target_rule = trial.get("target", rule)
            self._run_trial(trial, part, target_rule, trial["trial_type"])

    def _create_part1_experimental(self):
        return [dict(self._generate_stimulus("dots"), trial_type="experimental", target="amount")
                for _ in range(32)]

    def _create_part2_experimental(self):
        return [dict(self._generate_stimulus("numbers"), trial_type="experimental", target="identity")
                for _ in range(32)]

    def _create_part3_experimental(self):
        return [dict(self._generate_stimulus("numbers"), trial_type="experimental", target="amount")
                for _ in range(32)]

    def _create_part4_experimental(self):
        trials = []
        for position in range(1, 33):
            is_red = position in self.RED_POSITIONS
            trials.append(dict(self._generate_stimulus("numbers"), is_red=is_red,
                               switch_before=is_red, trial_type="experimental"))
        return trials

    def _compute_practice_rules(self, trials, initial_rule):
        rule = initial_rule
        result = []
        for trial in trials:
            if trial.get("switch_before", False):
                rule = "identity" if rule == "amount" else "amount"
            target = trial.get("target", rule)
            result.append((target, self._target_value(trial, target)))
        return result

    def _show_practice_integrated_screen(self, instruction_lines, practice_trials,
                                          part, initial_rule, footer_lines, two_rows=False):
        rules_info = self._compute_practice_rules(practice_trials, initial_rule)
        responses = [None] * len(practice_trials)
        correct_flags = [None] * len(practice_trials)
        stim_size = 60
        n_per_row = 4
        rows = [practice_trials[:4], practice_trials[4:]] if two_rows else [practice_trials]

        def draw(show_footer=False):
            self.screen.blit(self.background, (0, 0))
            y = 45
            for line in instruction_lines:
                if line:
                    for wrapped in self._wrap_lines(line, self.font, self.screen_x - 100):
                        display.text(self.screen, self.font, wrapped, "center", y)
                        y += 38
                else:
                    y += 18
            for row_i, row_trials in enumerate(rows):
                cy = self.screen_y - (150 if two_rows else 95) + row_i * 125
                section_w = self.screen_x // n_per_row
                for col_i, trial in enumerate(row_trials):
                    idx = row_i * n_per_row + col_i
                    cx = section_w // 2 + col_i * section_w
                    self._draw_stimulus(trial, trial.get("is_red", False), (cx, cy), stim_size)
                    if responses[idx] is not None:
                        color = (0, 180, 0) if correct_flags[idx] else (220, 40, 40)
                        text = self.font_label.render(str(responses[idx]), True, color)
                        self.screen.blit(text, (cx - text.get_width() // 2, cy + stim_size + 8))
            if show_footer:
                footer_y = self.screen_y - 75
                for line in footer_lines:
                    if line:
                        display.text(self.screen, self.font_small, line, "center", footer_y)
                        footer_y -= 28
                display.text_space(self.screen, self.font, "center", self.screen_y - 35)
            pygame.display.flip()

        draw()
        next_idx = 0
        while next_idx < len(practice_trials):
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                if event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    response = self.KEY_TO_DIGIT.get(event.key)
                    if response is not None:
                        responses[next_idx] = response
                        correct_flags[next_idx] = response == rules_info[next_idx][1]
                        next_idx += 1
                        draw(next_idx == len(practice_trials))
                        break
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                if event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    if event.key == K_SPACE:
                        waiting = False
        for idx, trial in enumerate(practice_trials):
            target_rule, correct_response = rules_info[idx]
            self.rows.append({
                "part": part,
                "trial_type": "practice",
                "target_type": target_rule,
                "stimulus_digit": trial["identity"],
                "stimulus_count": trial["amount"],
                "response": responses[idx],
                "response_given": "yes" if responses[idx] is not None else "no",
                "correct_response": correct_response,
                "correct": "yes" if correct_flags[idx] else "no",
                "rt": None,
                "is_switch_trial": "yes" if trial.get("is_red", False) else "no",
            })

    def run(self):
        """Run the four-part NamingNumbers task and return trial data."""
        self._show_text_screen([
            "Esta prueba consta de 4 partes. En cada una tendrás que responder atendiendo a una característica distinta de los estímulos.",
            "", "Los estímulos serán cuadrados que contienen puntos o agrupaciones de una misma cifra.",
        ], title="NamingNumbers")
        self._show_text_screen([
            "Para responder utiliza las teclas numéricas del teclado, del 1 al 9.", "",
            "Responde de la forma más rápida y precisa posible.", "",
            "Pulsa <<barra espaciadora>> para continuar.",
        ])

        part1_practice = [dict(self._generate_stimulus("dots"), trial_type="practice", target="amount")
                          for _ in range(4)]
        self._show_practice_integrated_screen(
            ["Primera parte", "", "Indica cuántos puntos aparecen dentro de cada cuadrado.",
             "", "Responde a los siguientes 4 ejemplos con las teclas 1-9."],
            part1_practice, 1, "amount",
            ["El color verde indica una respuesta acertada y el rojo una respuesta errónea.", "",
             "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar."])
        self._run_trials(self._create_part1_experimental(), 1, "amount")

        part2_practice = [dict(self._generate_stimulus("numbers"), trial_type="practice", target="identity")
                          for _ in range(4)]
        self._show_practice_integrated_screen(
            ["La parte 1 ha terminado.", "", "En esta parte aparecerán agrupaciones de una misma cifra.",
             "", "Indica qué cifra aparece en cada cuadrado."],
            part2_practice, 2, "identity",
            ["El color verde indica una respuesta acertada y el rojo una respuesta errónea.", "",
             "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar."])
        self._run_trials(self._create_part2_experimental(), 2, "identity")

        part3_practice = [dict(self._generate_stimulus("numbers"), trial_type="practice", target="amount")
                          for _ in range(4)]
        self._show_practice_integrated_screen(
            ["La parte 2 ha terminado.", "", "Indica cuántas veces aparece repetida la cifra dentro de cada cuadrado."],
            part3_practice, 3, "amount",
            ["El color verde indica una respuesta acertada y el rojo una respuesta errónea.", "",
             "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar."])
        self._run_trials(self._create_part3_experimental(), 3, "amount")

        part4_practice = [dict(self._generate_stimulus("numbers"), trial_type="practice",
                               is_red=idx in (3, 5), switch_before=idx in (3, 5))
                          for idx in range(1, 9)]
        self._show_practice_integrated_screen(
            ["La parte 3 ha terminado.", "", "Al principio indica cuántas cifras aparecen.", "",
             "Cada estímulo rojo cambia el objetivo: desde ese estímulo debes indicar la cifra, y el objetivo vuelve a cambiar en el siguiente estímulo rojo."],
            part4_practice, 4, "amount",
            ["El color verde indica una respuesta acertada y el rojo una respuesta errónea.", "",
             "Si no tienes ninguna duda pulsa <<barra espaciadora>> para empezar."], two_rows=True)
        self._run_trials(self._create_part4_experimental(), 4, "amount")

        self._show_text_screen(["Fin de la tarea.", "", "Pulsa la barra espaciadora para continuar."])
        print("- NamingNumbers complete")
        return pd.DataFrame(self.rows)
