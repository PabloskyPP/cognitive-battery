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
        "Correcto. Si hubiese alguna duda sobre la tarea pregúntale ahora al "
        "supervisor. Si ya entiendes la tarea y estás preparado para empezar "
        "pulsa espacio."
    )
    PRACTICE_FAILURE_TEXT = (
        "Fallaste, puede que no hayas entendido bien las instrucciones. Si es "
        "así avisa al supervisor antes de seguir con esta tarea. Si ya "
        "entiendes la tarea y estás preparado para empezar pulsa espacio."
    )

    SECTIONS = (
        {
            "result_key": "forward_span",
            "instruction": (
                "En esta siguiente tarea tienes que memorizar listas de números, "
                "teniendo para ello tantos segundos como números contenga cada "
                "lista. Las listas de números se alargan cada dos rondas. Al "
                "terminar este tiempo, tendrás que escribir en el orden indicado "
                "en cada parte la lista de números justo anteriormente "
                "presentada. Para recordar y escribir con los números del "
                "teclado la lista tienes tiempo suficiente, aunque si tardas "
                "demasiado aparecerá una cuenta regresiva de 10 segundos "
                "avisándote de que tu tiempo para responder se está acabando. "
                "Si este tiempo se acaba tu respuesta en esa ronda se "
                "registrará como fallo. También si erras el número que sigue "
                "en la lista la ronda termina registrándose como ronda fallada. "
                "Cuidado, el número que se escribe no se puede borrar. Tras 2 "
                "rondas falladas la sección se termina. Esta prueba tiene 3 "
                "secciones. En la primera sección tienes que repetir la lista "
                "de números justa anterior en el mismo orden que se presenta. "
                "Como ejemplo, prueba a recordar y escribir la siguiente lista "
                "en orden directo."
            ),
            "practice_sequence": (5, 2),
            "mode": "forward",
            "sequences": (
                (3, 7),
                (5, 2),
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
            "instruction": (
                "La parte uno ha terminado. A continuación empieza la parte "
                "dos. Aquí tienes que repetir las listas de números que "
                "aparecen pero ahora en orden inverso. Como ejemplo, prueba a "
                "recordar y escribir la siguiente lista en orden inverso."
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
            "result_key": "ascending_span",
            "instruction": (
                "La parte dos ha terminado. A continuación empieza la parte "
                "tres. Aquí tienes que repetir las listas de números que "
                "aparecen pero ahora en orden creciente (de menor a mayor). "
                "Como ejemplo, prueba a recordar y escribir la siguiente lista "
                "en orden creciente."
            ),
            "practice_sequence": (3, 1, 9),
            "mode": "ascending",
            "sequences": (
                (4, 7),
                (9, 5),
                (2, 5, 4),
                (1, 3, 2),
                (6, 7, 1, 3),
                (1, 8, 7, 2),
                (8, 5, 2, 1, 9),
                (4, 9, 5, 1, 6),
                (3, 6, 8, 4, 2, 1),
                (2, 7, 9, 5, 1, 4),
                (5, 6, 2, 4, 8, 1, 7),
                (6, 9, 8, 7, 2, 3, 1),
                (4, 2, 1, 9, 7, 6, 3, 8),
                (9, 1, 4, 8, 2, 3, 5, 6),
                (4, 7, 8, 9, 1, 6, 2, 5, 3),
                (7, 8, 2, 5, 3, 1, 9, 4, 6),
            ),
        },
    )

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font = pygame.font.SysFont("arial", 30)
        self.stimulus_font = pygame.font.SysFont("arial", 80)
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
        raise ValueError("Unknown mode: {}".format(mode))

    @staticmethod
    def build_results(forward_span, backward_span, ascending_span):
        return pd.DataFrame(
            [
                {
                    "forward_span": forward_span,
                    "backward_span": backward_span,
                    "ascending_span": ascending_span,
                }
            ]
        )

    def _format_sequence(self, sequence):
        return " - ".join(str(digit) for digit in sequence)

    def _wrap_text(self, text_string, font, max_width):
        words = text_string.split()
        lines = []
        current_line = []

        for word in words:
            proposed = " ".join(current_line + [word])
            if font.size(proposed)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _draw_wrapped_text(self, text_string, start_y, colour=(0, 0, 0)):
        lines = self._wrap_text(text_string, self.font, self.screen_x - (self.TEXT_MARGIN * 2))
        for line_index, line in enumerate(lines):
            display.text(
                self.screen,
                self.font,
                line,
                self.TEXT_MARGIN,
                start_y + (line_index * 40),
                colour,
            )
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

    def _draw_practice_screen(self, instruction, example_sequence, entered_digits, wrong_index=None, countdown=None):
        self.screen.blit(self.background, (0, 0))
        y_position = self._draw_wrapped_text(instruction, 60)

        display.text(
            self.screen,
            self.font,
            self._format_sequence(example_sequence),
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
        self._draw_wrapped_text(message, self.screen_y / 2 - 80)
        pygame.display.flip()
        display.wait_for_space()

    def _collect_response(self, expected_sequence, draw_callback):
        expected_digits = [str(digit) for digit in expected_sequence]
        entered_digits = []
        response_start = time.time()
        countdown_start = len(expected_digits) * self.RESPONSE_TIMEOUT_MULTIPLIER
        timeout_limit = countdown_start + self.COUNTDOWN_SECONDS
        clock = pygame.time.Clock()

        pygame.event.clear()

        while True:
            elapsed = time.time() - response_start
            countdown = None
            if elapsed >= countdown_start:
                countdown = max(0, self.COUNTDOWN_SECONDS - int(elapsed - countdown_start))

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

            if elapsed >= timeout_limit:
                draw_callback(entered_digits, countdown=0)
                self._draw_border((255, 0, 0))
                pygame.display.flip()
                display.wait(self.FEEDBACK_DURATION)
                return False

            draw_callback(entered_digits, countdown=countdown)
            pygame.display.flip()
            clock.tick(60)

    def _show_presentation(self, sequence):
        self.screen.blit(self.background, (0, 0))
        display.text(
            self.screen,
            self.stimulus_font,
            self._format_sequence(sequence),
            "center",
            "center",
        )
        pygame.display.flip()
        display.wait(len(sequence) * 1000)

    def _run_section(self, section):
        failed_trials = 0
        last_correct_length = 0

        for sequence in section["sequences"]:
            expected_sequence = self._transform_sequence(section["mode"], sequence)
            self._show_presentation(sequence)

            success = self._collect_response(
                expected_sequence,
                lambda entered_digits, wrong_index=None, countdown=None: self._draw_response_screen(
                    entered_digits,
                    wrong_index=wrong_index,
                    countdown=countdown,
                ),
            )

            if success:
                last_correct_length = len(sequence)
            else:
                failed_trials += 1
                if failed_trials == self.MAX_FAILED_TRIALS:
                    break

        return last_correct_length

    def _run_practice(self, section):
        expected_sequence = self._transform_sequence(section["mode"], section["practice_sequence"])
        practice_success = self._collect_response(
            expected_sequence,
            lambda entered_digits, wrong_index=None, countdown=None: self._draw_practice_screen(
                section["instruction"],
                section["practice_sequence"],
                entered_digits,
                wrong_index=wrong_index,
                countdown=countdown,
            ),
        )

        if practice_success:
            self._show_feedback_message(self.PRACTICE_SUCCESS_TEXT)
        else:
            self._show_feedback_message(self.PRACTICE_FAILURE_TEXT)

    def run(self):
        section_spans = {}

        for section in self.SECTIONS:
            self._run_practice(section)
            section_spans[section["result_key"]] = self._run_section(section)

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font, "Fin de la tarea", "center", "center")
        pygame.display.flip()
        display.wait(1000)

        print("- Digits Memorization complete")

        return self.build_results(
            section_spans["forward_span"],
            section_spans["backward_span"],
            section_spans["ascending_span"],
        )
