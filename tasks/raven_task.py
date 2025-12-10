import os
import pygame
import pandas as pd
from pygame.locals import *
from sys import exit


class RavenTask(object):
    """
    Raven's Progressive Matrices Task (Standard Scale)
    
    This task presents 60 trials across 5 sets (A, B, C, D, E) with 12 trials each.
    Sets A and B have 6 answer options per trial.
    Sets C, D, and E have 8 answer options per trial.
    """
    
    def __init__(self, screen, background):
        # Get the pygame display window
        self.screen = screen
        self.background = background
        
        # Set font and font size
        self.instructionsFont = pygame.font.SysFont("arial", 20)
        self.titleFont = pygame.font.SysFont("arial", 25, bold=True)
        
        # Get screen info
        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()
        
        # Fill background
        self.background.fill((255, 255, 255))
        pygame.display.set_caption("Test de Matrices Progresivas de Raven")
        pygame.mouse.set_visible(1)
        
        # Get images directory
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.imagePath = os.path.join(
            os.path.dirname(self.directory),
            "images",
            "test  matrices progresivas de Raven escala standard"
        )
        
        # Define trial structure: 60 trials in 5 sets (A, B, C, D, E)
        # Each set has 12 trials
        self.trials = []
        for set_letter in ['A', 'B', 'C', 'D', 'E']:
            for trial_num in range(1, 13):
                # Sets A and B have 6 options, C/D/E have 8 options
                num_options = 6 if set_letter in ['A', 'B'] else 8
                self.trials.append({
                    'set': set_letter,
                    'number': trial_num,
                    'id': f"{set_letter}{trial_num}",
                    'num_options': num_options
                })
        
        # ANSWER_KEY: Dictionary mapping trial ID to correct answer (1-based index)
        # This should be filled manually with the correct answers for each trial.
        # Example: 'A1': 4 means the correct answer for trial A1 is option 4
        # 
        # Instructions for Pablo:
        # Fill in the correct answer for each trial below.
        # The answer should be a number between 1 and 6 for sets A and B,
        # and between 1 and 8 for sets C, D, and E.
        #
        # EDIT THIS SECTION BELOW (lines 68-128):
        self.ANSWER_KEY = {
            # Set A (12 trials, 6 options each)
            'A1': None,   # Fill with correct answer (1-6)
            'A2': None,
            'A3': None,
            'A4': None,
            'A5': None,
            'A6': None,
            'A7': None,
            'A8': None,
            'A9': None,
            'A10': None,
            'A11': None,
            'A12': None,
            # Set B (12 trials, 6 options each)
            'B1': None,   # Fill with correct answer (1-6)
            'B2': None,
            'B3': None,
            'B4': None,
            'B5': None,
            'B6': None,
            'B7': None,
            'B8': None,
            'B9': None,
            'B10': None,
            'B11': None,
            'B12': None,
            # Set C (12 trials, 8 options each)
            'C1': None,   # Fill with correct answer (1-8)
            'C2': None,
            'C3': None,
            'C4': None,
            'C5': None,
            'C6': None,
            'C7': None,
            'C8': None,
            'C9': None,
            'C10': None,
            'C11': None,
            'C12': None,
            # Set D (12 trials, 8 options each)
            'D1': None,   # Fill with correct answer (1-8)
            'D2': None,
            'D3': None,
            'D4': None,
            'D5': None,
            'D6': None,
            'D7': None,
            'D8': None,
            'D9': None,
            'D10': None,
            'D11': None,
            'D12': None,
            # Set E (12 trials, 8 options each)
            'E1': None,   # Fill with correct answer (1-8)
            'E2': None,
            'E3': None,
            'E4': None,
            'E5': None,
            'E6': None,
            'E7': None,
            'E8': None,
            'E9': None,
            'E10': None,
            'E11': None,
            'E12': None,
        }
        # END OF ANSWER_KEY SECTION
        
        # Create output dataframe
        self.allData = pd.DataFrame()
        self.allData['Ensayo'] = [trial['id'] for trial in self.trials]
        self.allData['Respuesta correcta'] = [self.ANSWER_KEY.get(trial['id']) for trial in self.trials]
        self.allData['Respuesta dada'] = [None] * len(self.trials)
        
        # Current trial index
        self.current_trial = 0
        
        # Selected answer for current trial
        self.selected_answer = None
        
        # Path for saving data
        self.dataPath = None
    
    def get_image_path(self, trial_id, image_type):
        """
        Get the full path to an image file.
        
        Args:
            trial_id: Trial identifier (e.g., 'A1', 'B5', 'C2')
            image_type: 0 for reference image, 1-8 for answer options
            
        Returns:
            Full path to the image file
        """
        filename = f"Raven's {trial_id}_{image_type}.png"
        return os.path.join(self.imagePath, filename)
    
    def show_instructions(self):
        """Display the instruction screen"""
        instructions = True
        while instructions:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    instructions = False
                elif event.type == KEYDOWN and event.key == K_F12:
                    pygame.quit()
                    exit()
                elif event.type == QUIT:
                    pygame.quit()
                    exit()
            
            self.screen.blit(self.background, (0, 0))
            
            # Title
            title = self.titleFont.render(
                "Test de Matrices Progresivas de Ravens con escala estándar",
                1, (0, 0, 0)
            )
            titleW = title.get_rect().width
            self.screen.blit(title, (self.screen_x / 2 - titleW / 2, 100))
            
            # Instructions text
            y_offset = 200
            line_spacing = 40
            
            instructions_lines = [
                "Esta prueba consta de 60 ensayos en los que se muestra una imagen más grande",
                "con un patrón de contenido o relleno específico y con un hueco vacío.",
                "Abajo de esta imagen se encuentran otras más pequeñas.",
                "",
                "Como en un rompecabezas, tu tarea es seleccionar aquella imagen que contiene",
                "el mismo patrón de relleno y que por tanto encaja en el hueco de la imagen superior.",
                "",
                "Si quieres cambiar de respuesta puedes deseleccionar una imagen y clicar en otra.",
                "Solo hay una respuesta correcta por ensayo.",
                "",
                "Para avanzar al siguiente ensayo pulsa la barra espaciadora.",
                "",
                "Si estás preparado para empezar la tarea pulsa la barra espaciadora."
            ]
            
            for i, line in enumerate(instructions_lines):
                text = self.instructionsFont.render(line, 1, (0, 0, 0))
                text_w = text.get_rect().width
                self.screen.blit(text, (self.screen_x / 2 - text_w / 2, y_offset + i * line_spacing))
            
            pygame.display.flip()
    
    def display_trial(self):
        """Display a single trial"""
        if self.current_trial >= len(self.trials):
            return False
        
        trial = self.trials[self.current_trial]
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    # Save answer and advance
                    self.allData.at[self.current_trial, 'Respuesta dada'] = self.selected_answer
                    self.save_data_incremental()
                    self.current_trial += 1
                    self.selected_answer = None
                    waiting = False
                elif event.type == KEYDOWN and event.key == K_F12:
                    # Save before quitting
                    self.allData.at[self.current_trial, 'Respuesta dada'] = self.selected_answer
                    self.save_data_incremental()
                    pygame.quit()
                    exit()
                elif event.type == QUIT:
                    # Save before quitting
                    self.allData.at[self.current_trial, 'Respuesta dada'] = self.selected_answer
                    self.save_data_incremental()
                    pygame.quit()
                    exit()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    # Handle click on answer options
                    mouseX, mouseY = pygame.mouse.get_pos()
                    clicked_option = self.check_option_click(mouseX, mouseY, trial)
                    if clicked_option is not None:
                        if self.selected_answer == clicked_option:
                            # Deselect if clicking the same option
                            self.selected_answer = None
                        else:
                            # Select new option
                            self.selected_answer = clicked_option
            
            # Draw the trial
            self.screen.blit(self.background, (0, 0))
            
            # Draw trial identifier at the top
            trial_id_text = self.titleFont.render(f"Ensayo {trial['id']}", 1, (0, 0, 0))
            trial_id_w = trial_id_text.get_rect().width
            self.screen.blit(trial_id_text, (self.screen_x / 2 - trial_id_w / 2, 50))
            
            # Load and display reference image (larger, centered)
            ref_image_path = self.get_image_path(trial['id'], 0)
            ref_image = pygame.image.load(ref_image_path)
            
            # Scale reference image to be larger
            ref_scale = 0.6
            ref_w = int(ref_image.get_width() * ref_scale)
            ref_h = int(ref_image.get_height() * ref_scale)
            ref_image = pygame.transform.smoothscale(ref_image, (ref_w, ref_h))
            
            # Center the reference image
            ref_x = self.screen_x / 2 - ref_w / 2
            ref_y = 150
            self.screen.blit(ref_image, (ref_x, ref_y))
            
            # Display answer options in grid (3x2 or 4x2)
            num_options = trial['num_options']
            cols = 4 if num_options == 8 else 3
            rows = 2
            
            option_scale = 0.35
            spacing_x = 20
            spacing_y = 20
            
            # Calculate starting position to center the grid
            sample_img = pygame.image.load(self.get_image_path(trial['id'], 1))
            option_w = int(sample_img.get_width() * option_scale)
            option_h = int(sample_img.get_height() * option_scale)
            
            grid_width = cols * option_w + (cols - 1) * spacing_x
            grid_start_x = self.screen_x / 2 - grid_width / 2
            grid_start_y = ref_y + ref_h + 50
            
            # Store button positions for click detection
            self.option_buttons = []
            
            for i in range(num_options):
                row = i // cols
                col = i % cols
                
                option_x = grid_start_x + col * (option_w + spacing_x)
                option_y = grid_start_y + row * (option_h + spacing_y)
                
                # Load and scale option image
                option_image = pygame.image.load(self.get_image_path(trial['id'], i + 1))
                option_image = pygame.transform.smoothscale(option_image, (option_w, option_h))
                
                # Draw the image
                self.screen.blit(option_image, (option_x, option_y))
                
                # Store button position for click detection
                self.option_buttons.append({
                    'option': i + 1,
                    'rect': pygame.Rect(option_x, option_y, option_w, option_h)
                })
                
                # Draw blue border if selected
                if self.selected_answer == i + 1:
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 255),
                        (option_x, option_y, option_w, option_h),
                        5
                    )
            
            # Display instruction at bottom
            instruction_text = self.instructionsFont.render(
                "Selecciona una respuesta y pulsa la barra espaciadora para continuar",
                1, (100, 100, 100)
            )
            instruction_w = instruction_text.get_rect().width
            self.screen.blit(instruction_text, (self.screen_x / 2 - instruction_w / 2, self.screen_y - 80))
            
            pygame.display.flip()
        
        return True
    
    def check_option_click(self, mouseX, mouseY, trial):
        """Check if an option was clicked"""
        for button in self.option_buttons:
            if button['rect'].collidepoint(mouseX, mouseY):
                return button['option']
        return None
    
    def save_data_incremental(self):
        """Save data after each trial"""
        if self.dataPath:
            try:
                self.allData.to_excel(self.dataPath, index=False)
            except Exception as e:
                print(f"Error saving data: {e}")
    
    def show_end_screen(self):
        """Display the end screen"""
        end_screen = True
        while end_screen:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    end_screen = False
                elif event.type == KEYDOWN and event.key == K_F12:
                    pygame.quit()
                    exit()
                elif event.type == QUIT:
                    pygame.quit()
                    exit()
            
            self.screen.blit(self.background, (0, 0))
            
            end_text = self.titleFont.render("Tarea completada", 1, (0, 0, 0))
            end_w = end_text.get_rect().width
            self.screen.blit(end_text, (self.screen_x / 2 - end_w / 2, self.screen_y / 2 - 50))
            
            thanks_text = self.instructionsFont.render(
                "Gracias por tu participación",
                1, (0, 0, 0)
            )
            thanks_w = thanks_text.get_rect().width
            self.screen.blit(thanks_text, (self.screen_x / 2 - thanks_w / 2, self.screen_y / 2 + 20))
            
            space_text = self.instructionsFont.render(
                "(Pulsa la barra espaciadora para continuar)",
                1, (100, 100, 100)
            )
            space_w = space_text.get_rect().width
            self.screen.blit(space_text, (self.screen_x / 2 - space_w / 2, self.screen_y / 2 + 100))
            
            pygame.display.flip()
    
    def run(self):
        """Main run method for the task"""
        # Show instructions
        self.show_instructions()
        
        # Run all trials
        for i in range(len(self.trials)):
            if not self.display_trial():
                break
        
        # Show end screen
        self.show_end_screen()
        
        # Final save
        self.save_data_incremental()
        
        print("- Raven's Progressive Matrices Task complete")
        
        return self.allData
