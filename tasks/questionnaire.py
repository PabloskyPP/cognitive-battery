import os
import sys
import random
import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class QuestionnaireTask(object):
    def __init__(
        self,
        screen,
        background,
        *,
        title,
        statements_file_name,
        instructions_text,
        response_options,
        expected_statement_count=None,
        keyboard_hint=None,
        item_prompt=None,
    ):
        self.screen = screen
        self.background = background
        self.title = title
        self.instructions_text = instructions_text
        self.response_options = response_options
        self.expected_statement_count = expected_statement_count
        self.keyboard_hint = keyboard_hint
        self.item_prompt = item_prompt

        self.font = pygame.font.SysFont("arial", 32)
        self.font_large = pygame.font.SysFont("arial", 36)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.font_instructions = pygame.font.SysFont("arial", 38)
        self.font_prompt = pygame.font.SysFont("arial", 28)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption(self.title)
        pygame.mouse.set_visible(1)

        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        statements_file = os.path.join(
            os.path.dirname(self.base_dir), "enunciados", statements_file_name
        )

        self.statements = []
        self.statement_numbers = []

        try:
            with open(statements_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(". ", 1)
                        if len(parts) == 2:
                            try:
                                num = int(parts[0])
                                text = parts[1]
                                self.statements.append(text)
                                self.statement_numbers.append(num)
                            except ValueError:
                                print(f"Warning: Skipping malformed line: {line[:50]}...")
                                continue
        except FileNotFoundError:
            print(f"ERROR: Statements file not found: {statements_file}")
            print("Please ensure the file exists in the correct location.")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load statements file: {e}")
            sys.exit(1)

        if (
            self.expected_statement_count is not None
            and len(self.statements) != self.expected_statement_count
        ):
            print(
                f"WARNING: Expected {self.expected_statement_count} statements but loaded {len(self.statements)}"
            )

        indices = list(range(len(self.statements)))
        random.shuffle(indices)

        self.randomized_statements = [self.statements[i] for i in indices]
        self.randomized_numbers = [self.statement_numbers[i] for i in indices]

        self.all_data = pd.DataFrame()
        self.all_data["trial"] = list(range(1, len(self.randomized_statements) + 1))
        self.all_data["numero_del_enunciado"] = self.randomized_numbers
        self.all_data["respuesta"] = ""

        self.key_to_value = {}
        self.normalized_value_by_str = {}
        for option in self.response_options:
            value = option["value"]
            self.normalized_value_by_str[str(value)] = value
            for key in option.get("keys", []):
                self.key_to_value[str(key).lower()] = value

        self.back_button_rect = None
        self.change_button_rect = None

    def draw_instructions(self):
        self.screen.blit(self.background, (0, 0))

        font = self.font_instructions
        line_spacing = 55
        gap_spacing = 22
        max_width = self.screen_x - 140

        instructions = [self.instructions_text, "", "Pulsa la barra espaciadora para comenzar."]

        # Pre-calculate total block height (accounting for text wrapping)
        total_height = 0
        line_heights = []
        for line in instructions:
            if line:
                wrapped = self._wrap_text_with_font(font, line, max_width)
                h = len(wrapped) * line_spacing
                line_heights.append(h)
                total_height += h
            else:
                line_heights.append(gap_spacing)
                total_height += gap_spacing

        # Center the block vertically; always leave at least 60px from top
        y_pos = max(60, (self.screen_y - total_height) // 2)

        for i, line in enumerate(instructions):
            if line:
                wrapped = self._wrap_text_with_font(font, line, max_width)
                for wline in wrapped:
                    surf = font.render(wline, True, (0, 0, 0))
                    x_pos = (self.screen_x - surf.get_width()) // 2
                    self.screen.blit(surf, (x_pos, y_pos))
                    y_pos += line_spacing
            else:
                y_pos += gap_spacing

        pygame.display.flip()

    def draw_statement(self, trial_index, current_response):
        self.screen.blit(self.background, (0, 0))

        back_text = "Volver al enunciado anterior"
        back_surface = self.font.render(back_text, True, (0, 0, 0))
        self.back_button_rect = pygame.Rect(20, 40, back_surface.get_width() + 30, back_surface.get_height() + 20)
        pygame.draw.rect(self.screen, (200, 200, 200), self.back_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.back_button_rect, 2)
        self.screen.blit(back_surface, (35, 50))

        counter_text = f"{trial_index + 1} / {len(self.randomized_statements)}"
        counter_surface = self.font.render(counter_text, True, (0, 0, 0))
        self.screen.blit(counter_surface, (self.screen_x - counter_surface.get_width() - 50, 50))

        # Draw item prompt above the statement (dark grey, centered)
        statement_y = self.screen_y // 3
        if self.item_prompt:
            prompt_surf = self.font_prompt.render(self.item_prompt, True, (80, 80, 80))
            prompt_x = (self.screen_x - prompt_surf.get_width()) // 2
            prompt_y = statement_y - prompt_surf.get_height() - 12
            self.screen.blit(prompt_surf, (prompt_x, prompt_y))

        statement_text = self.randomized_statements[trial_index]
        self.draw_wrapped_text_centered(statement_text, statement_y, self.screen_x - 200)

        scale_y = self.screen_y - 300
        total_width = self.screen_x - 200
        option_count = len(self.response_options)
        spacing = total_width // (option_count + 1)
        start_x = 100 + spacing

        for i, option in enumerate(self.response_options):
            value = option["value"]
            x_pos = start_x + i * spacing

            if current_response == value:
                circle_color = (0, 150, 255)
                text_color = (0, 0, 255)
            else:
                circle_color = (200, 200, 200)
                text_color = (0, 0, 0)

            pygame.draw.circle(self.screen, circle_color, (x_pos, scale_y), 32 if len(option["label"]) > 1 else 25)
            pygame.draw.circle(
                self.screen, (0, 0, 0), (x_pos, scale_y), 32 if len(option["label"]) > 1 else 25, 2
            )

            num_surface = self.font_large.render(option["label"], True, text_color)
            self.screen.blit(
                num_surface, (x_pos - num_surface.get_width() // 2, scale_y - num_surface.get_height() // 2)
            )

            if option.get("desc1"):
                desc1_surface = self.font_small.render(option["desc1"], True, (0, 0, 0))
                self.screen.blit(
                    desc1_surface, (x_pos - desc1_surface.get_width() // 2, scale_y + 45)
                )

            if option.get("desc2"):
                desc2_surface = self.font_small.render(option["desc2"], True, (0, 0, 0))
                self.screen.blit(
                    desc2_surface, (x_pos - desc2_surface.get_width() // 2, scale_y + 72)
                )

        change_text = "Cambiar respuesta"
        change_surface = self.font_small.render(change_text, True, (0, 0, 0))
        button_width = change_surface.get_width() + 40
        button_x = (self.screen_x - button_width) // 2
        button_y = self.screen_y - 170
        self.change_button_rect = pygame.Rect(button_x, button_y, button_width, 40)
        pygame.draw.rect(self.screen, (200, 200, 200), self.change_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.change_button_rect, 2)
        self.screen.blit(change_surface, (button_x + 20, button_y + 10))

        if self.keyboard_hint is None:
            self.keyboard_hint = "Pulsa la barra espaciadora para continuar."
        instr_text = self.keyboard_hint
        instr_surface = self.font_small.render(instr_text, True, (100, 100, 100))
        self.screen.blit(
            instr_surface, ((self.screen_x - instr_surface.get_width()) // 2, self.screen_y - 100)
        )

        pygame.display.flip()

    def draw_wrapped_text(self, text, x, y, max_width, center=False, line_height=35):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surface = self.font.render(test_line, True, (0, 0, 0))

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, (0, 0, 0))
            if center:
                x_pos = (self.screen_x - line_surface.get_width()) // 2
            else:
                x_pos = x
            self.screen.blit(line_surface, (x_pos, y + i * line_height))

    def draw_wrapped_text_centered(self, text, y, max_width):
        self.draw_wrapped_text(text, 0, y, max_width, center=True, line_height=40)

    def _wrap_text_with_font(self, font, text, max_width):
        """Return a list of wrapped line strings using the given font."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [""]

    def run(self):
        self.draw_instructions()
        display.wait_for_space()

        current_trial = 0

        while current_trial < len(self.randomized_statements):
            response_value = self.all_data.at[current_trial, "respuesta"]
            if pd.isna(response_value) or response_value == "" or str(response_value) == "nan":
                current_response = ""
            else:
                current_response = self.normalized_value_by_str.get(str(response_value), response_value)

            self.draw_statement(current_trial, current_response)

            pygame.event.clear()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        sys.exit(0)
                    elif event.type == KEYDOWN:
                        if event.key == K_F12:
                            sys.exit(0)
                        elif event.key == K_SPACE:
                            if current_response:
                                self.all_data.at[current_trial, "respuesta"] = current_response
                                current_trial += 1
                                waiting = False
                        else:
                            key_name = pygame.key.name(event.key).lower()
                            if key_name in self.key_to_value:
                                current_response = self.key_to_value[key_name]
                                self.draw_statement(current_trial, current_response)
                    elif event.type == MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
                            if current_trial > 0:
                                current_trial -= 1
                                waiting = False

                        if self.change_button_rect and self.change_button_rect.collidepoint(mouse_pos):
                            current_response = ""
                            self.draw_statement(current_trial, current_response)

        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_large, "Fin del cuestionario", "center", "center")
        display.text(
            self.screen,
            self.font,
            "Pulsa la barra espaciadora para continuar",
            "center",
            self.screen_y // 2 + 100,
        )
        pygame.display.flip()

        display.wait_for_space()

        print(f"- {self.title} complete")

        return self.all_data
