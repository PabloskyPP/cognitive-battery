import os
import sys
import time
import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class D2(object):
    """
    D2 Test de atención y concentración
    
    A task that measures attention and concentration by having participants
    identify and mark specific target letters (d with exactly two marks)
    among distractors.
    """
    
    def __init__(self, screen, background):
        # Get the pygame display window
        self.screen = screen
        self.background = background

        # Set font and font size
        self.font = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 18)

        # Get screen info
        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        # Fill background
        self.background.fill((255, 255, 255))
        pygame.display.set_caption("D2 - Test de atención y concentración")
        pygame.mouse.set_visible(1)

        # Experiment options (constants)
        self.ROW_DURATION = 20000  # 20 seconds per row in milliseconds
        self.TRAINING_LETTERS = 22  # Number of letters in training
        self.ROW_LETTERS = 47  # Number of letters in each main task row
        self.NUM_ROWS = 14  # Number of main task rows
        
        # Note: Hitbox calculations assume letters are evenly spaced across the image width.
        # If actual letter positions differ, hitbox detection accuracy may be affected.
        # Consider providing precise letter coordinates if available.

        # Get image path
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.image_path = os.path.join(self.base_dir, "images", "D2")

        # Create output dataframe for all rows
        self.all_data = pd.DataFrame()

    def display_instructions(self):
        """Screen 1: Display task instructions with example image"""
        self.screen.blit(self.background, (0, 0))
        
        # Main instruction text
        y_pos = self.screen_y / 2 - 350
        
        lines = [
            "Esta prueba trata de conocer su capacidad de concentración en una tarea determinada.",
            "En esta página se te presenta un ejemplo y una línea de entrenamiento para que te",
            "familiarices con la tarea"
        ]
        
        for line in lines:
            display.text(self.screen, self.font, line, "center", y_pos, (0, 0, 0))
            y_pos += 35

        # Display example image if it exists
        ejemplo_path = os.path.join(self.image_path, "ejemplo.png")
        if os.path.exists(ejemplo_path):
            img_ejemplo = pygame.image.load(ejemplo_path)
            y_pos += 30
            display.image(self.screen, img_ejemplo, "center", y_pos)
            y_pos += img_ejemplo.get_height() + 30
        else:
            y_pos += 50

        # Explanation paragraphs
        explanation_lines = [
            "Observa las tres letras minúsculas del ejemplo. Se trata de la letra d acompañada de dos rayitas.",
            "La primera d tiene las dos rayitas encima, la segunda las tiene debajo y la tercera d tiene una",
            "rayita encima y otra debajo. Observa que en estos casos la letra d va acompañada de dos rayitas.",
            "",
            "Tu tarea consistirá en buscar las letras d iguales a esas tres (con dos rayitas en cualquier posición)",
            "y marcarlas. Fíjate bien, porque hay letras d con más de dos o menos de dos rayitas y letras p,",
            "que NO deberás marcar en ningún caso, independientemente del número de rayitas que tengan.",
            "Si te equivocas y quieres cambiar una respuesta, puedes desmarcar tu respuesta clicando de nuevo",
            "en el estímulo seleccionado.",
            "",
            "En la página siguiente se te mostrará un caso de entrenamiento antes de empezar con la tarea"
        ]
        
        for line in explanation_lines:
            if line == "":
                y_pos += 20
            else:
                display.text(self.screen, self.font_small, line, "center", y_pos, (0, 0, 0))
                y_pos += 28

        # Final instruction
        y_pos += 30
        display.text_space(self.screen, self.font, "center", y_pos, (0, 0, 0))
        
        pygame.display.flip()
        display.wait_for_space()

    def _redraw_training_screen(self, img_prueba, img_x, img_y, img_height, hitboxes, selections):
        """Helper method to redraw training screen with current selections"""
        explanation = "Observa que deberías haber marcado las letras números "
        correct_numbers = "1, 3, 5, 6, 9, 12, 13, 17, 19, 22"
        instructions = [
            "En la siguiente página empezarás la tarea.",
            "Durante la tarea se te presentarán por orden hasta un total de 14 filas similares a la de esta",
            "práctica anterior pero con más letras. En cada una tendrás 20 segundos para señalar todas las",
            "letras d (esta d en azul oscuro) con dos rayitas que encuentres.",
            "Tras los 20 segundos se pasará automáticamente a la siguiente fila.",
            "Trabaja tan rápidamente como puedas sin cometer errores.",
            "Permanece trabajando hasta que el tiempo se acabe y el programa se cierre automáticamente."
        ]
        
        self.screen.blit(self.background, (0, 0))
        
        # Redraw instructions
        y = 100
        display.text(self.screen, self.font, 
            "Recuerda que el objetivo es señalar las letras d con dos rayitas.",
            "center", y, (0, 0, 0))
        y += 40
        display.text(self.screen, self.font, 
            "Prueba a hacerlo con la siguiente serie",
            "center", y, (0, 0, 0))
        
        # Redraw image
        self.screen.blit(img_prueba, (img_x, img_y))
        
        # Draw red rectangles for selected letters
        for j, selected in enumerate(selections):
            if selected:
                pygame.draw.rect(self.screen, (255, 0, 0), hitboxes[j], 3)
        
        # Redraw bottom text
        y = img_y + img_height + 50
        display.text(self.screen, self.font_small, explanation, "center", y, (0, 0, 0))
        y += 30
        display.text(self.screen, self.font_small, correct_numbers, "center", y, (0, 0, 139))
        
        y += 50
        for line in instructions:
            display.text(self.screen, self.font_small, line, "center", y, (0, 0, 0))
            y += 28
        
        y += 30
        display.text_space(self.screen, self.font, "center", y, (0, 0, 0))
        
        pygame.display.flip()

    def display_training(self):
        """Screen 2: Display training screen with 22 clickable letters"""
        self.screen.blit(self.background, (0, 0))
        
        # Instructions
        y_pos = 100
        display.text(
            self.screen, self.font, 
            "Recuerda que el objetivo es señalar las letras d con dos rayitas.",
            "center", y_pos, (0, 0, 0)
        )
        y_pos += 40
        display.text(
            self.screen, self.font, 
            "Prueba a hacerlo con la siguiente serie",
            "center", y_pos, (0, 0, 0)
        )

        # Load and display training image
        prueba_path = os.path.join(self.image_path, "prueba.png")
        if not os.path.exists(prueba_path):
            # Show error message if image doesn't exist
            display.text(
                self.screen, self.font,
                "Error: Image 'prueba.png' not found in images/D2/",
                "center", "center", (255, 0, 0)
            )
            pygame.display.flip()
            display.wait(3000)
            return []

        img_prueba = pygame.image.load(prueba_path)
        img_width = img_prueba.get_width()
        img_height = img_prueba.get_height()
        
        # Center the image
        img_x = (self.screen_x - img_width) / 2
        img_y = y_pos + 40
        
        self.screen.blit(img_prueba, (img_x, img_y))

        # Create hitboxes for 22 letters (assuming evenly spaced)
        # This is a simplified hitbox system - adjust based on actual image layout
        letter_width = img_width / self.TRAINING_LETTERS
        hitboxes = []
        selections = [False] * self.TRAINING_LETTERS
        
        for i in range(self.TRAINING_LETTERS):
            hitbox = pygame.Rect(
                img_x + (i * letter_width),
                img_y,
                letter_width,
                img_height
            )
            hitboxes.append(hitbox)

        # Display explanation text below image
        text_y = img_y + img_height + 50
        explanation = "Observa que deberías haber marcado las letras números "
        correct_numbers = "1, 3, 5, 6, 9, 12, 13, 17, 19, 22"
        
        display.text(self.screen, self.font_small, explanation, "center", text_y, (0, 0, 0))
        text_y += 30
        display.text(self.screen, self.font_small, correct_numbers, "center", text_y, (0, 0, 139))

        # Additional instructions
        text_y += 50
        instructions = [
            "En la siguiente página empezarás la tarea.",
            "Durante la tarea se te presentarán por orden hasta un total de 14 filas similares a la de esta",
            "práctica anterior pero con más letras. En cada una tendrás 20 segundos para señalar todas las",
            "letras d (esta d en azul oscuro) con dos rayitas que encuentres.",
            "Tras los 20 segundos se pasará automáticamente a la siguiente fila.",
            "Trabaja tan rápidamente como puedas sin cometer errores.",
            "Permanece trabajando hasta que el tiempo se acabe y el programa se cierre automáticamente."
        ]
        
        for line in instructions:
            display.text(self.screen, self.font_small, line, "center", text_y, (0, 0, 0))
            text_y += 28

        # Space to continue
        text_y += 30
        display.text_space(self.screen, self.font, "center", text_y, (0, 0, 0))
        
        pygame.display.flip()

        # Interactive loop for training
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    waiting = False
                elif event.type == KEYDOWN and event.key == K_F12:
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # Check if any hitbox was clicked
                    mouse_pos = pygame.mouse.get_pos()
                    for i, hitbox in enumerate(hitboxes):
                        if hitbox.collidepoint(mouse_pos):
                            # Toggle selection
                            selections[i] = not selections[i]
                            
                            # Redraw the screen with highlights
                            self._redraw_training_screen(img_prueba, img_x, img_y, img_height, hitboxes, selections)
                            break

        return selections

    def display_row(self, row_num):
        """
        Display one of the 14 main task rows with 47 clickable letters
        
        Args:
            row_num: Row number (1-14)
            
        Returns:
            DataFrame with selection data for this row
        """
        self.screen.blit(self.background, (0, 0))
        
        # Load row image
        row_image_path = os.path.join(self.image_path, f"fila{row_num}.png")
        if not os.path.exists(row_image_path):
            # Show error message if image doesn't exist
            display.text(
                self.screen, self.font,
                f"Error: Image 'fila{row_num}.png' not found in images/D2/",
                "center", "center", (255, 0, 0)
            )
            pygame.display.flip()
            display.wait(2000)
            
            # Return DataFrame with expected structure (47 letters, all unselected)
            row_data = []
            for i in range(self.ROW_LETTERS):
                row_data.append({
                    'row': row_num,
                    'letter_num': i + 1,
                    'selected': False,
                    'timestamp': 0
                })
            return pd.DataFrame(row_data)

        img_row = pygame.image.load(row_image_path)
        img_width = img_row.get_width()
        img_height = img_row.get_height()
        
        # Center the image
        img_x = (self.screen_x - img_width) / 2
        img_y = (self.screen_y - img_height) / 2
        
        self.screen.blit(img_row, (img_x, img_y))

        # Create hitboxes for 47 letters (assuming evenly spaced)
        letter_width = img_width / self.ROW_LETTERS
        hitboxes = []
        selections = [False] * self.ROW_LETTERS
        selection_times = [None] * self.ROW_LETTERS
        
        for i in range(self.ROW_LETTERS):
            hitbox = pygame.Rect(
                img_x + (i * letter_width),
                img_y,
                letter_width,
                img_height
            )
            hitboxes.append(hitbox)

        pygame.display.flip()

        # Start timer
        start_time = int(round(time.time() * 1000))
        
        # Interactive loop for this row (20 seconds)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_F12:
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # Check if any hitbox was clicked
                    mouse_pos = pygame.mouse.get_pos()
                    current_time = int(round(time.time() * 1000))
                    
                    for i, hitbox in enumerate(hitboxes):
                        if hitbox.collidepoint(mouse_pos):
                            # Toggle selection
                            selections[i] = not selections[i]
                            
                            # Record time if newly selected, clear if deselected
                            if selections[i]:
                                selection_times[i] = current_time - start_time
                            else:
                                selection_times[i] = None
                            
                            # Redraw the screen with highlights
                            # Note: Full screen redraw is acceptable given typical click frequency
                            # and 20-second task duration
                            self.screen.blit(self.background, (0, 0))
                            self.screen.blit(img_row, (img_x, img_y))
                            
                            # Draw red rectangles for selected letters
                            for j, selected in enumerate(selections):
                                if selected:
                                    pygame.draw.rect(self.screen, (255, 0, 0), hitboxes[j], 3)
                            
                            pygame.display.flip()
                            break

            # Check if time is up
            current_time = int(round(time.time() * 1000))
            if current_time - start_time >= self.ROW_DURATION:
                running = False

        # Create DataFrame for this row
        row_data = []
        for i in range(self.ROW_LETTERS):
            row_data.append({
                'row': row_num,
                'letter_num': i + 1,
                'selected': selections[i],
                'timestamp': selection_times[i] if selection_times[i] is not None else 0
            })
        
        return pd.DataFrame(row_data)

    def display_final(self):
        """Screen 17: Display task completion message"""
        self.screen.blit(self.background, (0, 0))
        
        display.text(
            self.screen, self.font,
            "La tarea ha terminado.",
            "center", "center", (0, 0, 0)
        )
        
        display.text_space(
            self.screen, self.font,
            "center", self.screen_y / 2 + 100, (0, 0, 0)
        )
        
        pygame.display.flip()
        display.wait_for_space()

    def run(self):
        """Main task execution sequence"""
        # Screen 1: Instructions
        self.display_instructions()

        # Screen 2: Training
        training_selections = self.display_training()

        # Screens 3-16: Main task (14 rows)
        for row_num in range(1, self.NUM_ROWS + 1):
            row_data = self.display_row(row_num)
            self.all_data = pd.concat([self.all_data, row_data], ignore_index=True)

        # Screen 17: Final
        self.display_final()

        print("- D2 complete")

        return self.all_data
