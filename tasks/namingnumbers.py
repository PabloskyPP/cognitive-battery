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
    PART1_PRACTICE_AMOUNTS = (2, 5, 8, 4)
    PART1_EXPERIMENTAL_AMOUNTS = (
        1, 4, 7, 2, 9, 5, 3, 8,
        6, 2, 5, 9, 1, 7, 4, 8,
        3, 6, 1, 5, 8, 2, 9, 4,
        7, 3, 6, 9, 2, 8, 4, 1,
    )
    PART2_PRACTICE_STIMULI = ((3, 7), (5, 2), (2, 9), (4, 4))
    PART2_EXPERIMENTAL_STIMULI = (
        (3, 7), (5, 2), (2, 9), (7, 4), (4, 1), (6, 8), (1, 5), (8, 3),
        (9, 6), (2, 4), (5, 7), (3, 1), (6, 9), (4, 8), (7, 5), (1, 2),
        (8, 6), (2, 3), (9, 4), (5, 1), (3, 8), (6, 2), (4, 7), (7, 9),
        (1, 6), (8, 5), (2, 1), (9, 7), (5, 4), (3, 2), (6, 3), (4, 9),
    )
    PART3_PRACTICE_STIMULI = ((2, 6), (6, 3), (4, 8), (7, 5))
    PART3_EXPERIMENTAL_STIMULI = (
        (2, 6), (7, 3), (4, 8), (9, 2), (5, 7), (3, 1), (8, 4), (6, 9),
        (1, 5), (4, 2), (7, 8), (2, 3), (9, 6), (5, 4), (3, 7), (8, 1),
        (6, 5), (1, 9), (4, 3), (7, 2), (2, 8), (9, 1), (5, 6), (3, 4),
        (8, 7), (6, 2), (1, 4), (4, 9), (7, 5), (2, 1), (9, 8), (5, 3),
    )
    PART4_PRACTICE_STIMULI = (
        (2, 7), (5, 3), (4, 8), (6, 2),
        (3, 9), (7, 4), (1, 5), (5, 6),
    )
    PART4_EXPERIMENTAL_STIMULI = (
        (2, 7), (5, 3), (4, 8), (6, 2), (3, 9), (7, 4), (1, 5), (8, 6),
        (9, 1), (2, 4), (5, 7), (4, 3), (6, 8), (3, 2), (7, 9), (1, 4),
        (8, 5), (9, 6), (2, 1), (5, 8), (4, 7), (6, 3), (3, 5), (7, 2),
        (1, 9), (8, 4), (9, 7), (2, 6), (5, 1), (4, 9), (6, 5), (3, 8),
    )

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background
        self.font = pygame.font.SysFont("arial", 30)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.font_title = pygame.font.SysFont("arial", 36)
        self.font_label = pygame.font.SysFont("arial", 20)
        self.font_response = pygame.font.SysFont("arial", 42)
        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()
        self.background.fill((255, 255, 255))
        pygame.display.set_caption("NamingNumbers")
        pygame.mouse.set_visible(1)
        self.rows = []

    def _dots_stimulus(self, amount):
        return {"kind": "dots", "amount": amount, "identity": None}

    def _numbers_stimulus(self, amount, identity):
        return {"kind": "numbers", "amount": amount, "identity": identity}

    def _draw_stimulus(self, stimulus, is_red=False, center=None, size=200, surface=None):
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
            line_spacing = min(
                44,
                (2 * size - digit.get_height()) / max(1, stimulus["amount"] - 1),
            )
            for row in range(stimulus["amount"]):
                y = cy - (stimulus["amount"] - 1) * line_spacing / 2 + row * line_spacing
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
        stimulus_center = (self.screen_x // 2, self.screen_y // 2 - 90)
        stimulus_size = 230
        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_small, f"Parte {part}", 40, 30)
        self._draw_stimulus(trial, is_red=trial.get("is_red", False),
                            center=stimulus_center, size=stimulus_size)
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
        self._draw_stimulus(trial, is_red=trial.get("is_red", False),
                            center=stimulus_center, size=stimulus_size)
        response_color = (0, 180, 0) if is_correct else (220, 40, 40)
        response_surface = self.font_response.render(str(response), True, response_color)
        response_y = min(
            stimulus_center[1] + stimulus_size + 15,
            self.screen_y - response_surface.get_height() - 15,
        )
        self.screen.blit(response_surface, (stimulus_center[0] - response_surface.get_width() // 2,
                                            response_y))
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
        return [
            dict(self._dots_stimulus(amount), trial_type="experimental", target="amount")
            for amount in self.PART1_EXPERIMENTAL_AMOUNTS
        ]

    def _create_part2_experimental(self):
        return [
            dict(self._numbers_stimulus(amount, identity), trial_type="experimental", target="identity")
            for amount, identity in self.PART2_EXPERIMENTAL_STIMULI
        ]

    def _create_part3_experimental(self):
        return [
            dict(self._numbers_stimulus(amount, identity), trial_type="experimental", target="amount")
            for amount, identity in self.PART3_EXPERIMENTAL_STIMULI
        ]

    def _create_part4_experimental(self):
        trials = []
        for position, (amount, identity) in enumerate(self.PART4_EXPERIMENTAL_STIMULI, start=1):
            is_red = position in self.RED_POSITIONS
            trials.append(
                dict(
                    self._numbers_stimulus(amount, identity),
                    is_red=is_red,
                    switch_before=is_red,
                    trial_type="experimental",
                )
            )
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
        stim_size = 115
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
            footer_reserve = 150
            row_gap = 55 if two_rows else 30
            total_stimulus_height = len(rows) * (2 * stim_size) + (len(rows) - 1) * row_gap
            stimulus_top = max(
                y + 20,
                (self.screen_y - footer_reserve - total_stimulus_height) // 2,
            )
            for row_i, row_trials in enumerate(rows):
                cy = stimulus_top + stim_size + row_i * (2 * stim_size + row_gap)
                section_w = self.screen_x // n_per_row
                for col_i, trial in enumerate(row_trials):
                    idx = row_i * n_per_row + col_i
                    cx = section_w // 2 + col_i * section_w
                    self._draw_stimulus(trial, trial.get("is_red", False), (cx, cy), stim_size)
                    if responses[idx] is not None:
                        color = (0, 180, 0) if correct_flags[idx] else (220, 40, 40)
                        text = self.font_response.render(str(responses[idx]), True, color)
                        self.screen.blit(text, (cx - text.get_width() // 2, cy + stim_size + 8))
            if show_footer:
                footer_y = self.screen_y - 75 - (len(footer_lines) - 1) * 28
                for line in footer_lines:
                    if line:
                        display.text(self.screen, self.font_small, line, "center", footer_y)
                    footer_y += 28
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
            "",
            "",
            "",
            "Esta prueba consta de 4 partes, en las que las instrucciones sobre el estímulo ",
            "a atender y responder (puntos o agrupaciones de cifras) cambian en cada parte.", 
            "En algunos casos tienes que indicar el número de cifras que aparecen ",
            "y en otros el nombre de las cifras presentadas. ",
            "Para responder utiliza las teclas numéricas del teclado, del 1 al 9.",
            "Tras responder a un estímulo se pasa al siguiente y así hasta completar toda la serie de cada parte.",
            "Al empezar cada nueva parte se presentan primero las nuevas instrucciones.",
            "Responde de la forma más rápida y precisa posible.",
        ], title="NamingNumbers")

        part1_practice = [
            dict(self._dots_stimulus(amount), trial_type="practice", target="amount")
            for amount in self.PART1_PRACTICE_AMOUNTS
        ]
        self._show_practice_integrated_screen(
            ["Primera parte", "", "En esta parte tienes que indicar el número de puntos que aparecen en cada caso",
             "", "Como ejemplo de práctica indica para los siguientes 4 casos cuántos puntos se están a mostrar en cada uno."],
            part1_practice, 1, "amount",
            ["Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación. Si no:"])
        self._run_trials(self._create_part1_experimental(), 1, "amount")

        part2_practice = [
            dict(self._numbers_stimulus(amount, identity), trial_type="practice", target="identity")
            for amount, identity in self.PART2_PRACTICE_STIMULI
        ]
        self._show_practice_integrated_screen(
            [
                "La parte 1 ha terminado.",
                "",
                "A continuación empieza la parte 2.",
                "",
                "La tarea cambia, ahora en vez de puntos aparecerán agrupaciones de una misma cifra.",
                "",
                "En esta segunda parte tu tarea es indicar la cifra que aparece. Utiliza las teclas de tu teclado 1-9 para esto.",
                "",
                "Como ejemplo de práctica indica para los siguientes 4 casos qué cifra se está a mostrar en cada uno.",
            ],
            part2_practice, 2, "identity",
                ["Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación. Si no:"])
        self._run_trials(self._create_part2_experimental(), 2, "identity")

        part3_practice = [
            dict(self._numbers_stimulus(amount, identity), trial_type="practice", target="amount")
            for amount, identity in self.PART3_PRACTICE_STIMULI
        ]
        self._show_practice_integrated_screen(
            ["La parte 2 ha terminado.",
                "",
                "A continuación empieza la parte 3.",
                "",
                "De nuevo, se van a mostrar agrupaciones de cifras.",
                "",
                "Esta vez tu tarea es contar e indicar el número de veces que esta misma cifra aparece en cada caso.",
                "",
                "Como ejemplo de práctica indica para los siguientes 4 casos cuántas cifras se están a mostrar.",],
            part3_practice, 3, "amount",
                ["Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación. Si no:"])
        self._run_trials(self._create_part3_experimental(), 3, "amount")

        part4_practice = [
            dict(
                self._numbers_stimulus(amount, identity),
                trial_type="practice",
                is_red=idx in (3, 5),
                switch_before=idx in (3, 5),
            )
            for idx, (amount, identity) in enumerate(self.PART4_PRACTICE_STIMULI, start=1)
        ]
        self._show_practice_integrated_screen(
            ["La parte 3 ha terminado.",
                "",
                "A continuación empieza la parte 4.",
                "De nuevo, se van a mostrar agrupaciones de cifras.",
                "En esta parte final, empiezas indicando la cifra que se muestra. ",
                "Sin embargo, de vez en cuando estas cifras se mostrarán en color rojo.",
                "Esto indica un cambio de objetivo para el caso rojo actual y en adelante hasta el siguiente caso rojo.",
                "Así por ejemplo, después del primer caso rojo y en este incluído, tienes que cambiar ",
                "de indicar la cifra que aparece, al número de cifras que aparecen. ",
                "Y así cambiando sucesivamente el objetivo de tu respuesta con cada caso rojo que aparezca.",
                "Como ejemplo de práctica indica para los siguientes 8 casos el número que proceda.",],
            part4_practice, 4, "identity",
                ["Revisa tus respuestas en este ejemplo, el color verde indica respuesta acertada y el rojo respuesta errónea.",
                "Si tienes alguna duda sobre esta tarea pregunta ahora a la persona responsable de la evaluación. Si no:"],
            two_rows=True)
        self._run_trials(self._create_part4_experimental(), 4, "amount")

        self._show_text_screen(["Fin de la tarea.", "", "Pulsa la barra espaciadora para continuar."])
        print("- NamingNumbers complete")
        return pd.DataFrame(self.rows)
