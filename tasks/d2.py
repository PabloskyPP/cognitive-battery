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
        self.font = pygame.font.SysFont("arial", 32)
        self.font_small = pygame.font.SysFont("arial", 30)

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
        
        # Customizable hitbox coordinate system
        # These coordinates define the exact x-position boundaries [x_start, x_end] for each letter
        # in the ORIGINAL (unscaled) images. They will be automatically scaled during runtime.
        # 
        # How to measure and add coordinates:
        # 1. Open the original image (prueba.png or fila{N}.png) in an image editor
        # 2. For each letter, note the x-coordinate where the letter starts and ends
        # 3. Add these as [x_start, x_end] pairs in pixels
        # 4. The system will automatically apply scaling when displaying
        # 
        # If coordinates are empty or incomplete, the system falls back to uniform spacing.
        
        # Training image coordinates (22 letters in prueba.png)
        # Format: [[x_start, x_end], [x_start, x_end], ...]
        self.TRAINING_POSITIONS = [
            # Add 22 coordinate pairs here, one for each letter in prueba.png
            # Example: [10, 45], [50, 85], [90, 125], ...
        ]
        
        # Main task row coordinates (47 letters per row, 14 rows total)
        # Format: {row_number: [[x_start, x_end], [x_start, x_end], ...], ...}
        self.ROW_POSITIONS = {
            # Add coordinate pairs for each row's 47 letters
            # Example:
            # 1: [[x1, x2], [x3, x4], ..., [x93, x94]],  # 47 pairs for fila1.png
            # 2: [[x1, x2], [x3, x4], ..., [x93, x94]],  # 47 pairs for fila2.png
            # ... up to row 14
        }

        # Get image path - FIX: Navigate to project root
        self.base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.image_path = os.path.join(self.base_dir, "images", "D2")

        # Create output dataframe for all rows
        self.all_data = pd.DataFrame()
        
        # Define target stimuli based on (row, letter_num) combinations
        # These are the combinations where target = "si"
        self.TARGET_STIMULI = {
            1: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            2: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            3: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            5: [2, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            6: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            7: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            8: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            9: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            10: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 28, 33, 34, 37, 38, 40, 43, 45, 46],
            11: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            12: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            13: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            14: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47]
        }

    def display_instructions(self):
        """Screen 1: Display task instructions with example image"""
        self.screen.blit(self.background, (0, 0))
        
        # Main instruction text
        y_pos = self.screen_y / 2 - 350
        
        lines = [
            "Esta prueba trata de conocer tu capacidad de concentración en una tarea determinada.",
            "En esta página se te presenta un ejemplo y una línea de entrenamiento para que te",
            "familiarices con la tarea."
        ]
        
        for line in lines:
            display.text(self.screen, self.font, line, "center", y_pos, (0, 0, 0))
            y_pos += 35

        # Display example image if it exists
        ejemplo_path = os.path.join(self.image_path, "ejemplo.png")
        if os.path.exists(ejemplo_path):
            img_ejemplo = pygame.image.load(ejemplo_path)
            # Escalar la imagen (por ejemplo, 1.5x = 150% del tamaño original)
            scale_factor = 2  # Cambia este valor para ajustar el tamaño
            new_width = int(img_ejemplo.get_width() * scale_factor)
            new_height = int(img_ejemplo.get_height() * scale_factor)
            img_ejemplo = pygame.transform.scale(img_ejemplo, (new_width, new_height))
            
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
            "En la página siguiente se te mostrará un caso de entrenamiento antes de empezar con la tarea."
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
            "letras d con dos rayitas que encuentres.",
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

        # Escalar la imagen
        scale_factor = 2  # Cambia este valor
        new_width = int(img_prueba.get_width() * scale_factor)
        new_height = int(img_prueba.get_height() * scale_factor)
        img_prueba = pygame.transform.scale(img_prueba, (new_width, new_height))

        img_width = img_prueba.get_width()
        img_height = img_prueba.get_height()
        
        # Center the image
        img_x = (self.screen_x - img_width) / 2
        img_y = y_pos + 40
        
        self.screen.blit(img_prueba, (img_x, img_y))

        # Create hitboxes for 22 letters
        # Use custom coordinates if available, otherwise fall back to uniform spacing
        hitboxes = []
        selections = [False] * self.TRAINING_LETTERS
        
        for i in range(self.TRAINING_LETTERS):
            # Check if custom coordinates are defined for this letter
            if i < len(self.TRAINING_POSITIONS) and len(self.TRAINING_POSITIONS[i]) == 2:
                # Use custom coordinates (from original image) and scale them
                x_start, x_end = self.TRAINING_POSITIONS[i]
                x_start_scaled = x_start * scale_factor
                x_end_scaled = x_end * scale_factor
                hitbox = pygame.Rect(
                    img_x + x_start_scaled,
                    img_y,
                    x_end_scaled - x_start_scaled,
                    img_height
                )
            else:
                # Fallback: uniform spacing calculation
                letter_width = img_width / self.TRAINING_LETTERS
                hitbox_margin = letter_width * 0.005
                actual_hitbox_width = letter_width * 0.6
                hitbox = pygame.Rect(
                    img_x + (i * letter_width) + hitbox_margin,
                    img_y,
                    actual_hitbox_width,
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
            "letras d con dos rayitas que encuentres.",
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
                letter_num = i + 1
                # Determine if this stimulus is a target based on (row, letter_num)
                is_target = "si" if letter_num in self.TARGET_STIMULI.get(row_num, []) else "no"
                
                row_data.append({
                    'row': row_num,
                    'letter_num': letter_num,
                    'selected': False,
                    'timestamp': 0,
                    'target': is_target
                })
            return pd.DataFrame(row_data)

        img_row = pygame.image.load(row_image_path)

        # Escalar la imagen
        scale_factor = 1.18  # Cambia este valor para ajustar el tamaño
        new_width = int(img_row.get_width() * scale_factor)
        new_height = int(img_row.get_height() * scale_factor)
        img_row = pygame.transform.scale(img_row, (new_width, new_height))

        img_width = img_row.get_width()
        img_height = img_row.get_height()

        # Center the image
        img_x = (self.screen_x - img_width) / 2
        img_y = (self.screen_y - img_height) / 2
        
        self.screen.blit(img_row, (img_x, img_y))

        # Create hitboxes for 47 letters
        # Use custom coordinates if available, otherwise fall back to uniform spacing
        hitboxes = []
        selections = [False] * self.ROW_LETTERS
        selection_times = [None] * self.ROW_LETTERS
        
        # Check if custom coordinates are defined for this row
        has_custom_coords = (row_num in self.ROW_POSITIONS and 
                            len(self.ROW_POSITIONS[row_num]) >= self.ROW_LETTERS)
        
        for i in range(self.ROW_LETTERS):
            # Check if custom coordinates are defined for this letter in this row
            if (has_custom_coords and 
                i < len(self.ROW_POSITIONS[row_num]) and 
                len(self.ROW_POSITIONS[row_num][i]) == 2):
                # Use custom coordinates (from original image) and scale them
                x_start, x_end = self.ROW_POSITIONS[row_num][i]
                x_start_scaled = x_start * scale_factor
                x_end_scaled = x_end * scale_factor
                hitbox = pygame.Rect(
                    img_x + x_start_scaled,
                    img_y,
                    x_end_scaled - x_start_scaled,
                    img_height
                )
            else:
                # Fallback: uniform spacing calculation
                letter_width = img_width / self.ROW_LETTERS
                hitbox_margin = letter_width * 0.1
                actual_hitbox_width = letter_width * 0.5
                hitbox = pygame.Rect(
                    img_x + (i * letter_width) + hitbox_margin,
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
            letter_num = i + 1
            # Determine if this stimulus is a target based on (row, letter_num)
            is_target = "si" if letter_num in self.TARGET_STIMULI.get(row_num, []) else "no"
            
            row_data.append({
                'row': row_num,
                'letter_num': letter_num,
                'selected': selections[i],
                'timestamp': selection_times[i] if selection_times[i] is not None else 0,
                'target': is_target
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
