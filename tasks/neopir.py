import os
import sys
import random
import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class NeoPiR(object):
    def __init__(self, screen, background):
        # Get the pygame display window
        self.screen = screen
        self.background = background

        # Set fonts and font sizes
        self.font = pygame.font.SysFont("arial", 32)
        self.font_large = pygame.font.SysFont("arial", 36)
        self.font_small = pygame.font.SysFont("arial", 24)
        self.font_instructions = pygame.font.SysFont("arial", 30)

        # Get screen info
        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        # Fill background
        self.background.fill((255, 255, 255))
        pygame.display.set_caption("NEO-PI-R")
        pygame.mouse.set_visible(1)

        # Load statements from file
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        statements_file = os.path.join(
            os.path.dirname(self.base_dir), "enunciados NEO-PI-R", "enunciados_neo_pi_r.txt"
        )

        self.statements = []
        self.statement_numbers = []

        try:
            with open(statements_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Parse "1. Text" format
                        parts = line.split(". ", 1)
                        if len(parts) == 2:
                            try:
                                num = int(parts[0])
                                text = parts[1]
                                self.statements.append(text)
                                self.statement_numbers.append(num)
                            except ValueError:
                                # Skip malformed lines that don't have a valid number
                                print(f"Warning: Skipping malformed line: {line[:50]}...")
                                continue
        except FileNotFoundError:
            print(f"ERROR: Statements file not found: {statements_file}")
            print("Please ensure the file exists in the correct location.")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load statements file: {e}")
            sys.exit(1)

        # Verify we loaded the correct number of statements
        if len(self.statements) != 240:
            print(f"WARNING: Expected 240 statements but loaded {len(self.statements)}")

        # Create randomized order while preserving original numbers
        indices = list(range(len(self.statements)))
        random.shuffle(indices)

        self.randomized_statements = [self.statements[i] for i in indices]
        self.randomized_numbers = [self.statement_numbers[i] for i in indices]

        # Create output dataframe
        self.all_data = pd.DataFrame()
        self.all_data["trial"] = list(range(1, len(self.randomized_statements) + 1))
        self.all_data["numero_del_enunciado"] = self.randomized_numbers
        self.all_data["respuesta"] = ""

        # Button rectangles
        self.back_button_rect = None
        self.change_button_rect = None

    def draw_instructions(self):
        """Draw the instruction screen"""
        self.screen.blit(self.background, (0, 0))

        y_pos = 50
        line_spacing = 45

        instructions = [
            "Esto es un cuestionario de personalidad. El cuestionario consta de 240 enunciados",
            "ante los cuales tendrás que indicar tu grado de acuerdo o desacuerdo marcando un número del 1 al 5",
            "que equivalen a:",
            "",
            "1 = En total desacuerdo",
            "2 = En desacuerdo",
            "3 = Neutro",
            "4 = De acuerdo",
            "5 = Totalmente de acuerdo",
            "",
            "Para indicar esto utiliza los números de tu teclado.",
            "Al pulsar uno verás que el número seleccionado se iluminará en pantalla.",
            'Si quieres cambiar tu respuesta pulsa el botón "Cambiar respuesta" y escribe otro número.',
            "Antes de pasar al siguiente enunciado asegúrate de que hay un número seleccionado.",
            "Para pasar al siguiente enunciado pulsa la barra espaciadora.",
            "Si quieres volver al enunciado anterior selecciona con el ratón al botón",
            '"Volver al enunciado anterior".',
            "",
            "Pulsa la barra espaciadora para comenzar.",
        ]

        for line in instructions:
            display.text(self.screen, self.font_instructions, line, 50, y_pos)
            y_pos += line_spacing

        pygame.display.flip()

    def draw_statement(self, trial_index, current_response):
        """Draw a statement screen with rating scale"""
        self.screen.blit(self.background, (0, 0))

        # Draw back button (top left, larger and lower)
        back_text = "Volver al enunciado anterior"
        back_surface = self.font.render(back_text, True, (0, 0, 0))
        self.back_button_rect = pygame.Rect(20, 40, back_surface.get_width() + 30, back_surface.get_height() + 20)
        pygame.draw.rect(self.screen, (200, 200, 200), self.back_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.back_button_rect, 2)
        self.screen.blit(back_surface, (35, 50))

        # Draw counter (top right)
        counter_text = f"{trial_index + 1} / {len(self.randomized_statements)}"
        counter_surface = self.font.render(counter_text, True, (0, 0, 0))
        self.screen.blit(counter_surface, (self.screen_x - counter_surface.get_width() - 50, 50))

        # Draw statement text (wrapped and centered)
        statement_text = self.randomized_statements[trial_index]
        self.draw_wrapped_text_centered(statement_text, self.screen_y // 3, self.screen_x - 200)

        # Draw rating scale (moved up)
        scale_y = self.screen_y - 300
        scale_labels = ["1", "2", "3", "4", "5"]
        scale_descriptions = [
            "En total",
            "En",
            "Neutro",
            "De",
            "Totalmente",
        ]
        scale_descriptions_2 = [
            "desacuerdo",
            "desacuerdo",
            "",
            "acuerdo",
            "de acuerdo",
        ]

        # Calculate spacing for scale items
        total_width = self.screen_x - 200
        spacing = total_width // 6
        start_x = 100 + spacing

        for i, (label, desc1, desc2) in enumerate(zip(scale_labels, scale_descriptions, scale_descriptions_2)):
            x_pos = start_x + i * spacing

            # Highlight selected option
            if current_response == label:
                circle_color = (0, 150, 255)
                text_color = (0, 0, 255)
            else:
                circle_color = (200, 200, 200)
                text_color = (0, 0, 0)

            # Draw circle
            pygame.draw.circle(self.screen, circle_color, (x_pos, scale_y), 25)
            pygame.draw.circle(self.screen, (0, 0, 0), (x_pos, scale_y), 25, 2)

            # Draw number
            num_surface = self.font_large.render(label, True, text_color)
            self.screen.blit(
                num_surface, (x_pos - num_surface.get_width() // 2, scale_y - num_surface.get_height() // 2)
            )

            # Draw description
            desc1_surface = self.font_small.render(desc1, True, (0, 0, 0))
            self.screen.blit(
                desc1_surface, (x_pos - desc1_surface.get_width() // 2, scale_y + 40)
            )

            if desc2:
                desc2_surface = self.font_small.render(desc2, True, (0, 0, 0))
                self.screen.blit(
                    desc2_surface, (x_pos - desc2_surface.get_width() // 2, scale_y + 65)
                )

        # Draw "Change response" button (moved up)
        change_text = "Cambiar respuesta"
        change_surface = self.font_small.render(change_text, True, (0, 0, 0))
        button_width = change_surface.get_width() + 40
        button_x = (self.screen_x - button_width) // 2
        button_y = self.screen_y - 170
        self.change_button_rect = pygame.Rect(button_x, button_y, button_width, 40)
        pygame.draw.rect(self.screen, (200, 200, 200), self.change_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.change_button_rect, 2)
        self.screen.blit(change_surface, (button_x + 20, button_y + 10))

        # Draw instructions at bottom (moved up)
        instr_text = "Usa los números 1-5 del teclado para responder. Pulsa la barra espaciadora para continuar."
        instr_surface = self.font_small.render(instr_text, True, (100, 100, 100))
        self.screen.blit(
            instr_surface, ((self.screen_x - instr_surface.get_width()) // 2, self.screen_y - 100)
        )

        pygame.display.flip()

    def draw_wrapped_text(self, text, x, y, max_width, center=False, line_height=35):
        """Draw text with word wrapping
        
        Args:
            text: The text to display
            x: X position (ignored if center=True)
            y: Y position
            max_width: Maximum width for text wrapping
            center: If True, center the text horizontally
            line_height: Height between lines
        """
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

        # Draw all lines
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, (0, 0, 0))
            if center:
                x_pos = (self.screen_x - line_surface.get_width()) // 2
            else:
                x_pos = x
            self.screen.blit(line_surface, (x_pos, y + i * line_height))

    def draw_wrapped_text_centered(self, text, y, max_width):
        """Draw text with word wrapping, centered horizontally"""
        self.draw_wrapped_text(text, 0, y, max_width, center=True, line_height=40)

    def run(self):
        # Show instructions
        self.draw_instructions()
        display.wait_for_space()

        # Main questionnaire loop
        current_trial = 0

        while current_trial < len(self.randomized_statements):
            # Get current response, handling both empty strings and NaN values
            response_value = self.all_data.at[current_trial, "respuesta"]
            if pd.isna(response_value) or response_value == "" or str(response_value) == "nan":
                current_response = ""
            else:
                current_response = str(response_value)

            self.draw_statement(current_trial, current_response)

            # Clear event queue
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
                            # Only advance if a response has been given
                            if current_response:
                                self.all_data.at[current_trial, "respuesta"] = int(current_response)
                                current_trial += 1
                                waiting = False
                        elif event.key in [K_1, K_2, K_3, K_4, K_5]:
                            # Record response
                            current_response = pygame.key.name(event.key)
                            self.draw_statement(current_trial, current_response)
                    elif event.type == MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        # Check if back button clicked
                        if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
                            if current_trial > 0:
                                current_trial -= 1
                                waiting = False

                        # Check if change button clicked
                        if self.change_button_rect and self.change_button_rect.collidepoint(mouse_pos):
                            current_response = ""
                            self.draw_statement(current_trial, current_response)

        # End screen
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

        print("- NEO-PI-R complete")

        return self.all_data
