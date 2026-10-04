import sys
import time
import pygame
import pandas as pd

from pygame.locals import *
from utils import display


class DigitsMemorization(object):
    MAX_FAILED_TRIALS = 2
    RESPONSE_TIMEOUT_MULTIPLIER = 2
    COUNTDOWN_SECONDS = 10
    FEEDBACK_DURATION = 500
    BORDER_WIDTH = 10
    TEXT_MARGIN = 80

    PRACTICE_SUCCESS_TEXT = (
        "Correcto. \n"
        "Ahora, si hubiese alguna duda sobre la tarea pregúntale al supervisor. \n"
        "Si ya entiendes la tarea y estás preparado, \n"
        "pulsa <barra espaciadora> para empezar."
    )
    PRACTICE_FORWARD_SPAN_FAILURE_TEXT = (
        "Fallaste, puede que no hayas entendido bien las instrucciones. \n"
        "Fíjate, en la pantalla anterior se mostraban las cifras 5 2. \n"
        "De seguido tienes que repetir las cifras en el mismo orden, \n"
        "en este caso, 5 2. \n"
        "Si aún tienes dudas sobre como hacer la tarea avisa al supervisor.\n"
        "Si, por el contrario, ya entiendes la tarea y estás preparado, \n"
        "pulsa <barra espaciadora> para empezar."
    )
    PRACTICE_BACKWARD_SPAN_FAILURE_TEXT = (
        "Fallaste, puede que no hayas entendido bien las instrucciones. \n"
        "Fíjate, ahora tienes que escribir las cifras mostradas \n"
        "en orden inverso, empezando por la última y hacia la primera. \n"
        "Así, si se muestran las cifras 7 2. \n"
        "De seguido tienes que escribir 2 7. \n"
        "Si aún tienes dudas sobre como hacer la tarea avisa al supervisor. \n"
        "Si, por el contrario, ya entiendes la tarea y estás preparado \n"
        "pulsa <barra espaciadora> para empezar."
    )
    PRACTICE_CALCULATION_FAILURE_TEXT = (
        "Fallaste, puede que no hayas entendido bien las instrucciones. \n"
        "Fíjate, ahora tienes que calcular cada operación, memorizar su resultado \n"
        "y escribir cada resultado en el mismo orden directo. \n"
        "Por ejemplo, mostrándose (2+4); (1+1); (3-1) \n"
        "tienes que responder 6 2 2. \n"
        "Si aún tienes dudas sobre como hacer la tarea avisa al supervisor.\n"
        "Si, por el contrario, ya entiendes la tarea y estás preparado, \n"
        "pulsa <barra espaciadora> para empezar."
    )

    SECTIONS = (
        {
            "result_key": "forward_span",
            "parte": "directo",
            "instruction": (
                "En esta siguiente tarea tienes unos segundos para memorizar distintas listas de números. \n"
                "Terminado este tiempo tienes que escribir la misma serie de números anteriormente presentada. \n"
                "Para esto utiliza los números del teclado.\n"
                "Si erras el número que sigue la ronda termina, registrándose como ronda fallada.\n"
                "Cuidado, el número que se escribe no se puede borrar.\n"
                "Esta prueba consta de 3 partes. En esta primera parte tienes que repetir la lista \n"
                "de números anterior en el mismo orden que se presenta. \n"
                "Como ejemplo, prueba a recordar y escribir la siguiente lista en orden directo:"
            ),
            "practice_sequence": (5, 2),
            "mode": "forward",
            "sequences": (
                (3, 7),
                (4, 1),
                (1, 6, 3),
                (9, 8, 4),
                (6, 4, 3, 5),
                (2, 5, 9, 8),
                (1, 2, 7, 3, 6),
                (8, 2, 9, 7, 4),
                (4, 3, 6, 5, 9, 1),
                (2, 4, 7, 1, 8, 3),
                (5, 7, 8, 2, 1, 4, 9),
                (6, 3, 5, 9, 8, 2, 7),
                (1, 4, 8, 3, 7, 9, 2, 5),
                (8, 5, 2, 6, 9, 1, 7, 3),
                (2, 8, 5, 7, 3, 4, 9, 6, 1),
                (7, 6, 9, 3, 5, 1, 8, 3, 2),
            ),
        },
        {
            "result_key": "backward_span",
            "parte": "inverso",
            "instruction": (
                "La parte uno ha terminado. \n"
                "A continuación empieza la parte dos.\n"
                "Aquí tienes que repetir los números que aparecen,\n"
                "pero ahora en orden inverso, del último hacia atrás.\n"
                "Como ejemplo, prueba a recordar y escribir la siguiente lista en orden inverso:"
            ),
            "practice_sequence": (7, 2),
            "mode": "backward",
            "sequences": (
                (4, 5),
                (2, 9),
                (5, 9, 4),
                (6, 7, 2),
                (1, 3, 8, 5),
                (7, 6, 9, 3),
                (2, 4, 7, 5, 9),
                (8, 3, 2, 1, 4),
                (4, 9, 3, 6, 8, 1),
                (3, 5, 4, 1, 9, 8),
                (6, 7, 1, 2, 8, 3, 4),
                (5, 2, 7, 8, 3, 9, 6),
                (2, 1, 8, 3, 9, 4, 6, 7),
                (3, 8, 9, 6, 1, 7, 2, 5),
                (6, 1, 5, 7, 8, 9, 2, 3, 4),
                (3, 7, 4, 9, 2, 1, 5, 6, 8),
            ),
        },
        {
            "result_key": "calculation_span",
            "parte": "calculo",
            "instruction": (
                "La parte dos ha terminado. \n"
                "A continuación empieza la parte tres.\n"
                "Ahora verás una lista de operaciones. Calcula mentalmente cada suma o resta, \n"
                "memoriza los resultados y repítelos en el mismo orden. \n"
                "Como ejemplo, prueba a recordar y escribir los siguientes resultados en orden directo:"
            ),
            "practice_sequence": ((2, "+", 4), (1, "+", 1), (3, "-", 1)),
            "mode": "calculation",
            "sequences": (
                ((2, "+", 4), (1, "+", 1)),
                ((8, "-", 3), (3, "+", 5)),
                ((3, "+", 4), (9, "-", 5), (2, "+", 6)),
                ((7, "-", 2), (1, "+", 8), (6, "-", 3)),
                ((1, "+", 3), (9, "-", 2), (4, "+", 4), (8, "-", 5)),
                ((6, "-", 2), (5, "+", 3), (9, "-", 7), (2, "+", 5)),
                ((2, "+", 6), (8, "-", 4), (3, "+", 5), (7, "-", 1), (9, "-", 3)),
                ((4, "+", 5), (7, "-", 3), (1, "+", 8), (6, "-", 2), (5, "+", 2)),
                ((1, "+", 7), (9, "-", 4), (3, "+", 6), (8, "-", 5), (2, "+", 4), (7, "-", 2)),
                ((5, "+", 4), (6, "-", 1), (2, "+", 5), (9, "-", 6), (3, "+", 3), (8, "-", 2)),
                ((2, "+", 3), (8, "-", 4), (1, "+", 6), (7, "-", 5), (4, "+", 5), (9, "-", 3), (3, "+", 2)),
                ((9, "-", 2), (3, "+", 5), (6, "-", 4), (2, "+", 7), (8, "-", 6), (1, "+", 4), (7, "-", 3)),
                ((1, "+", 5), (9, "-", 7), (4, "+", 3), (8, "-", 2), (2, "+", 6), (7, "-", 4), (3, "+", 4), (6, "-", 5)),
                ((5, "+", 2), (8, "-", 3), (1, "+", 7), (9, "-", 5), (4, "+", 4), (7, "-", 6), (2, "+", 5), (6, "-", 1)),
            ),
        },
    )

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font = pygame.font.SysFont("arial", 30)
        self.stimulus_font = pygame.font.SysFont("arial", 90)
        self.countdown_font = pygame.font.SysFont("arial", 96)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption("Digits Memorization")
        pygame.mouse.set_visible(0)

    @staticmethod
    def _transform_sequence(mode, sequence):
        if mode == "forward":
            return tuple(sequence)
        if mode == "backward":
            return tuple(reversed(sequence))
        if mode == "ascending":
            return tuple(sorted(sequence))
        if mode == "calculation":
            return tuple(
                left + right if operator == "+" else left - right
                for left, operator, right in sequence
            )
        raise ValueError("Unknown mode: {}".format(mode))

    @staticmethod
    def build_results(trials):
        return pd.DataFrame(
            trials,
            columns=["parte", "serie", "num_digits", "correct"],
        )

    def _format_sequence(self, sequence, mode=None):
        if mode == "calculation":
            return "; ".join(
                f"({left}{operator}{right})"
                for left, operator, right in sequence
            )
        return " - ".join(str(digit) for digit in sequence)

    def _wrap_text(self, text_string, font, max_width):
        lines = []
        for paragraph in text_string.splitlines():
            words = paragraph.split()
            current_line = []

            for word in words:
                proposed = " ".join(current_line + [word])
                if font.size(proposed)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append((" ".join(current_line), True))
                    current_line = [word]

            if current_line:
                lines.append((" ".join(current_line), False))
            elif not paragraph:
                lines.append(("", False))

        return lines

    def _draw_wrapped_text(self, text_string, start_y, colour=(0, 0, 0)):
        max_width = self.screen_x - (self.TEXT_MARGIN * 2)
        lines = self._wrap_text(text_string, self.font, max_width)
        for line_index, (line, _) in enumerate(lines):
            y = start_y + (line_index * 40)
            surface = self.font.render(line, True, colour)
            x = (self.screen_x - surface.get_width()) // 2
            self.screen.blit(surface, (x, y))
        return start_y + (len(lines) * 40)

    def _draw_sequence_line(self, digits, y, wrong_index=None):
        digit_surfaces = []
        for digit_index, digit in enumerate(digits):
            colour = (255, 0, 0) if digit_index == wrong_index else (0, 0, 0)
            digit_surfaces.append(self.stimulus_font.render(str(digit), True, colour))

        separator_surface = self.stimulus_font.render(" - ", True, (0, 0, 0))

        total_width = 0
        for digit_index, surface in enumerate(digit_surfaces):
            total_width += surface.get_width()
            if digit_index < len(digit_surfaces) - 1:
                total_width += separator_surface.get_width()

        current_x = (self.screen_x - total_width) / 2
        for digit_index, surface in enumerate(digit_surfaces):
            self.screen.blit(surface, (current_x, y))
            current_x += surface.get_width()
            if digit_index < len(digit_surfaces) - 1:
                self.screen.blit(separator_surface, (current_x, y))
                current_x += separator_surface.get_width()

    def _draw_border(self, colour):
        pygame.draw.rect(self.screen, colour, (0, 0, self.screen_x, self.BORDER_WIDTH))
        pygame.draw.rect(
            self.screen,
            colour,
            (0, self.screen_y - self.BORDER_WIDTH, self.screen_x, self.BORDER_WIDTH),
        )
        pygame.draw.rect(self.screen, colour, (0, 0, self.BORDER_WIDTH, self.screen_y))
        pygame.draw.rect(
            self.screen,
            colour,
            (self.screen_x - self.BORDER_WIDTH, 0, self.BORDER_WIDTH, self.screen_y),
        )

    def _extract_digit(self, event):
        if event.type != KEYDOWN:
            return None

        if event.key == K_F12:
            sys.exit(0)

        if event.unicode and event.unicode.isdigit():
            return event.unicode

        return None

    def _draw_practice_screen(self, instruction, example_sequence, mode, entered_digits, wrong_index=None, countdown=None):
        self.screen.blit(self.background, (0, 0))

        is_section_transition = instruction.startswith((
            "La parte uno ha terminado",
            "La parte dos ha terminado",
        ))
        if is_section_transition:
            title_font = pygame.font.SysFont("arial", 38, bold=True)
            display.text(
                self.screen,
                title_font,
                "CAMBIAMOS TAREA",
                "center",
                80,
                (0, 0, 0),
            )

        instruction_y = 160 if is_section_transition else 160
        y_position = self._draw_wrapped_text(instruction, instruction_y)

        display.text(
            self.screen,
            self.stimulus_font,
            self._format_sequence(example_sequence, mode),
            "center",
            max(y_position + 60, self.screen_y / 2 - 80),
        )

        if entered_digits:
            self._draw_sequence_line(entered_digits, self.screen_y / 2 + 20, wrong_index=wrong_index)

        if countdown is not None:
            display.text(
                self.screen,
                self.countdown_font,
                str(countdown),
                "center",
                self.screen_y - 180,
                (255, 0, 0),
            )

    def _draw_response_screen(self, entered_digits, wrong_index=None, countdown=None):
        self.screen.blit(self.background, (0, 0))
        display.text(
            self.screen,
            self.font,
            "Repite la secuencia anterior:",
            "center",
            self.screen_y / 4,
            (128, 128, 128),
        )

        if entered_digits:
            self._draw_sequence_line(entered_digits, self.screen_y / 2 - 40, wrong_index=wrong_index)

        if countdown is not None:
            display.text(
                self.screen,
                self.countdown_font,
                str(countdown),
                "center",
                self.screen_y - 180,
                (255, 0, 0),
            )

    def _show_feedback_message(self, message):
        self.screen.blit(self.background, (0, 0))
        self._draw_wrapped_text(message, self.screen_y / 2 - 180)
        pygame.display.flip()
        display.wait_for_space()

    def _collect_response(self, expected_sequence, draw_callback, no_countdown=False):
        expected_digits = [str(digit) for digit in expected_sequence]
        entered_digits = []
        response_start = time.time()
        countdown_delay = len(expected_digits) * self.RESPONSE_TIMEOUT_MULTIPLIER
        timeout_limit = countdown_delay + self.COUNTDOWN_SECONDS
        clock = pygame.time.Clock()

        pygame.event.clear()

        while True:
            elapsed = time.time() - response_start
            countdown = None
            if not no_countdown and elapsed >= countdown_delay:
                countdown = max(0, self.COUNTDOWN_SECONDS - int(elapsed - countdown_delay))

            for event in pygame.event.get():
                digit = self._extract_digit(event)
                if digit is None:
                    continue

                entered_digits.append(digit)
                digit_index = len(entered_digits) - 1

                if digit != expected_digits[digit_index]:
                    draw_callback(entered_digits, wrong_index=digit_index, countdown=countdown)
                    self._draw_border((255, 0, 0))
                    pygame.display.flip()
                    display.wait(self.FEEDBACK_DURATION)
                    return False

                if len(entered_digits) == len(expected_digits):
                    draw_callback(entered_digits, countdown=countdown)
                    self._draw_border((0, 255, 0))
                    pygame.display.flip()
                    display.wait(self.FEEDBACK_DURATION)
                    return True

            if not no_countdown and elapsed >= timeout_limit:
                draw_callback(entered_digits, countdown=0)
                self._draw_border((255, 0, 0))
                pygame.display.flip()
                display.wait(self.FEEDBACK_DURATION)
                return False

            draw_callback(entered_digits, countdown=countdown)
            pygame.display.flip()
            clock.tick(60)

    def _show_presentation(self, sequence, mode=None):
        self.screen.blit(self.background, (0, 0))
        display.text(
            self.screen,
            self.stimulus_font,
            self._format_sequence(sequence, mode),
            "center",
            "center",
        )
        pygame.display.flip()
        seconds_per_item = 2 if mode == "calculation" else 1
        display.wait(len(sequence) * seconds_per_item * 1000)

    def _run_section(self, section):
        consecutive_failed = 0
        trial_results = []

        for series, sequence_template in enumerate(section["sequences"], start=1):
            sequence = sequence_template
            expected_sequence = self._transform_sequence(section["mode"], sequence)
            self._show_presentation(sequence, section["mode"])

            success = self._collect_response(
                expected_sequence,
                lambda entered_digits, wrong_index=None, countdown=None: self._draw_response_screen(
                    entered_digits,
                    wrong_index=wrong_index,
                    countdown=countdown,
                ),
            )

            trial_results.append({
                "parte": section["parte"],
                "serie": series,
                "num_digits": len(sequence),
                "correct": "sí" if success else "no",
            })

            if success:
                consecutive_failed = 0
            else:
                consecutive_failed += 1
                if consecutive_failed >= self.MAX_FAILED_TRIALS:
                    break

        return trial_results

    def _run_practice(self, section):
        expected_sequence = self._transform_sequence(section["mode"], section["practice_sequence"])
        practice_success = self._collect_response(
            expected_sequence,
            lambda entered_digits, wrong_index=None, countdown=None: self._draw_practice_screen(
                section["instruction"],
                section["practice_sequence"],
                section["mode"],
                entered_digits,
                wrong_index=wrong_index,
                countdown=countdown,
            ),
            no_countdown=True,
        )

        if practice_success:
            self._show_feedback_message(self.PRACTICE_SUCCESS_TEXT)
        else:
            failure_text_map = {
                "forward_span": self.PRACTICE_FORWARD_SPAN_FAILURE_TEXT,
                "backward_span": self.PRACTICE_BACKWARD_SPAN_FAILURE_TEXT,
                "calculation_span": self.PRACTICE_CALCULATION_FAILURE_TEXT,
            }
            self._show_feedback_message(failure_text_map[section["result_key"]])

    def run(self):
        trial_results = []

        for section in self.SECTIONS:
            self._run_practice(section)
            trial_results.extend(self._run_section(section))

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font, "Fin de la tarea", "center", "center")
        pygame.display.flip()
        display.wait(1000)

        print("- Digits Memorization complete")

        return self.build_results(trial_results)
    
