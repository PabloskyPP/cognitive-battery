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
        self.ROW_DURATION = 120000  # 20 seconds per row in milliseconds
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
            [154, 165], [173, 186], [195, 207], [216, 228], [237, 250], [258, 271],  
            [279, 292], [301, 313], [321, 335], [343, 356], [364, 377], [386, 399],
            [406, 421], [427, 441], [450, 462], [470, 484], [493, 506], [512, 527],
            [534, 547], [554, 569], [575, 590], [597, 611]
        ]
        
        # Main task row coordinates (47 letters per row, 14 rows total)
        # Format: {row_number: [[x_start, x_end], [x_start, x_end], ...], ...}
        self.ROW_POSITIONS = {
            1: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],   #6
            [185, 198], [207, 220], [229, 242], [252, 264], [274, 287], [296, 309], #12
            [318, 331], [340, 353], [360, 374], [383, 396], [405, 419], [427, 441], #18
            [451, 463], [470, 484], [494, 507], [516, 529],   #22
            [539, 553], [561, 572], [583, 597], [607, 620], [628, 640], [650, 664],  #28
            [673, 685], [693, 707], [717, 729], [737, 750], [760, 771], [780, 793],#34
            [804, 817], [825,839], [847, 861], [870, 885], [892, 905], [912, 927],#40
            [936, 947], [959, 971], [981, 995], [1002, 1015], #44
            [1025, 1037], [1047, 1060], [1068, 1080]
        ],
            2: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [185, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [340, 353], [361, 374], [383, 396], [405, 419], [427, 441],#18
            [450, 462], [471, 485], [494, 507], [515, 528],   #22
            [541, 555], [561, 572], [583, 596], [605, 619], [627, 640], [650, 664],  #28
            [673, 685], [693, 707], [717, 729], [737, 750], [760, 771], [780, 793],#34
            [804, 818], [825,839], [847, 861], [870, 885], [892, 905], [912, 927],#40
            [936, 947], [957, 971], [979, 993], [1002, 1015],#44
            [1024, 1037], [1046, 1060], [1068, 1082]
        ],
            3: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [184, 197], [207, 220], [227, 240], [252, 263], [273, 285], [296, 309],#12
            [318, 331], [340, 353], [360, 373], [383, 396], [405, 419], [427, 441],#18
            [450, 462], [470, 484], [493, 506], [514, 527],   #22
            [539, 553], [560, 572], [583, 596], [605, 619], [627, 641], [649, 664],  #28
            [673, 686], [693, 707], [717, 729], [737, 750], [760, 771], [781, 791],#34
            [804, 817], [825,839], [847, 861], [870, 884], [892, 904], [912, 927],#40
            [936, 947], [957, 971], [979, 993], [1002, 1015], #44
            [1023, 1037], [1046, 1060], [1068, 1082]
        ],  
            4: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [185, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [340, 353], [360, 373], [383, 396], [405, 419], [427, 441],#18
            [450, 462], [470, 484], [493, 506], [512, 527],   #22
            [539, 554], [560, 572], [583, 596], [604, 621], [627, 641], [648, 664],  #28
            [673, 686], [692, 707], [717, 729], [737, 750], [760, 771], [781, 791],#34
            [804, 818], [824,839], [847, 861], [870, 885], [892, 905], [912, 931],#40
            [936, 947], [957, 971], [979, 993], [1002, 1018], #44
            [1022, 1037], [1045, 1060], [1066, 1083]
        ],
            5: [
            [54, 68], [77, 89], [98, 110], [120, 134], [144, 156], [166, 178],  #6
            [188, 201], [209, 223], [232, 248], [257, 269], [278, 290], [300, 313],#12
            [321, 333], [344, 357], [364, 377], [387, 400], [409, 422], [431, 445],#18
            [455, 468], [476, 488], [497, 510], [522, 531],   #22
            [541, 556], [565, 577], [587, 600], [608, 621], [630, 643], [653, 665],  #28
            [674, 686], [692, 707], [717, 729], [738, 751], [762, 775], [784, 795],#34
            [807, 820], [829,840], [848, 862], [874, 888], [896, 908], [915, 934],#40
            [940, 953], [961, 974], [983, 996], [1006, 1021], #44
            [1026, 1040], [1049, 1062], [1072, 1086]
        ],
            6: [
            [54, 67], [78, 90], [98, 109], [120, 133], [143, 156], [166, 178],  #6
            [188, 201], [210, 223], [232, 245], [254, 266], [276, 288], [299, 312],#12
            [321, 334], [343, 356], [363, 376], [386, 399], [408, 422], [430, 444],#18
            [453, 467], [477, 489], [499, 513], [522, 533],   #22
            [541, 556], [563, 575], [585, 598], [608, 622], [629, 642], [653, 665],  #28
            [673, 687], [694, 707], [717, 731], [740, 752], [763, 774], [784, 797],#34
            [807, 820], [828,841], [849, 863], [872, 887], [894, 907], [914, 933],#40
            [938, 950], [961, 974], [983, 997], [1005, 1018],#44
            [1026, 1037], [1048, 1061], [1069, 1083]
        ],
            7: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [185, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [340, 353], [362, 373], [383, 396], [406, 417], [427, 441],#18
            [450, 462], [471, 484], [493, 506], [514, 527],   #22
            [539, 553], [561, 572], [583, 596], [606, 620], [628, 638], [648, 664],  #28
            [673, 686], [694, 707], [716, 728], [737, 750], [760, 771], [782, 794],#34
            [805, 818], [828,839], [848, 861], [871, 885], [894, 904], [915, 927],#40
            [936, 949], [959, 971], [980, 993], [1004, 1014],#44
            [1025, 1037], [1047, 1060], [1069, 1083]
        ],
            8: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [186, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [340, 353], [363, 375], [386, 398], [409, 421], [432, 444],#18
            [453, 465], [475, 486], [497, 510], [520, 533],   #22
            [542, 555], [564, 574], [584, 596], [608, 621], [630, 644], [652, 664],  #28
            [673, 686], [695, 707], [717, 729], [738, 750], [760, 772], [781, 793],#34
            [805, 818], [829,839], [848, 861], [871, 885], [895, 907], [917, 931],#40
            [940, 953], [962, 973], [984, 995], [1004, 1018], #44
            [1027, 1038], [1048, 1060], [1070, 1083]
        ],
            9: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [185, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [341, 353], [362, 373], [383, 396], [406, 419], [428, 441],#18
            [450, 462], [472, 484], [495, 506], [515, 527],   #22
            [539, 553], [563, 572], [583, 596], [606, 618], [627, 640], [649, 663],  #28
            [672, 683], [692, 707], [717, 729], [737, 750], [760, 772], [781, 793],#34
            [804, 818], [826,839], [848, 861], [870, 883], [892, 904], [912, 929],#40
            [937, 947], [958, 971], [980, 993], [1002, 1014],#44
            [1024, 1037], [1047, 1060], [1072, 1086]
        ],
            10: [
            [54, 68], [76, 88], [97, 109], [119, 132], [142, 155], [165, 177],  #6
            [187, 200], [209, 222], [233, 244], [255, 267], [276, 288], [298, 311],#12
            [320, 333], [342, 355], [362, 375], [384, 398], [408, 421], [430, 443],#18
            [453, 465], [473, 487], [496, 509], [515, 530],   #22
            [542, 557], [563, 575], [583, 596], [606, 623], [628, 640], [651, 660],  #28
            [670, 684], [694, 706], [717, 729], [737, 750], [760, 772], [785, 795],#34
            [804, 818], [829,839], [849, 862], [870, 885], [892, 907], [917, 931],#40
            [940, 951], [961, 975], [985, 996], [1002, 1018],#44
            [1028, 1038], [1046, 1058], [1071, 1083]
        ],
            11: [
            [55, 69], [78, 89],  [97, 109], [119, 132], [142, 155], [165, 177],    #6
            [187, 200], [209, 222], [233, 244], [255, 267], [276, 288], [298, 311],#12
            [320, 333], [342, 355], [363, 375], [385, 398], [407, 420], [430, 443],#18
            [453, 465], [474, 487], [496, 509], [520, 531],   #22
            [543, 556], [564, 575], [584, 596], [606, 620], [630, 642], [651, 663],  #28
            [676, 687], [697, 709], [718, 729], [739, 752], [763, 776], [785, 797],#34
            [808, 822], [831,842], [852, 865], [875, 886], [896, 908], [918, 931],#40
            [940, 951], [961, 973], [983, 996], [1006, 1018],#44
            [1028, 1039], [1050, 1062], [1071, 1084]
        ],
            12: [
            [62, 74], [84, 96], [105, 117], [127, 140], [150, 163], [173, 185],  #6
            [195, 208], [217, 230], [240, 252], [263, 275], [284, 297], [306, 318],#12
            [328, 341], [350, 362], [371, 383], [393, 406], [416, 429], [439, 451],#18
            [462, 474], [483, 496], [505, 517], [527, 540],   #22
            [551, 564], [572, 582], [593, 606], [616, 628], [637, 651], [660, 672],  #28
            [683, 696], [705, 717], [727, 741], [749, 760], [770, 781], [791, 803],#34
            [814, 827], [837,849], [858, 871], [881, 895], [903, 915], [926, 938],#40
            [948, 959], [968, 981], [991, 1003], [1014, 1025],#44
            [1036, 1047], [1057, 1070], [1079, 1093]
        ],
            13: [
            [55, 69], [78, 90], [100, 110], [120, 134], [144, 156], [166, 178],  #6
            [187, 200], [212, 223], [233, 245], [256, 267], [277, 289], [299, 312],#12
            [321, 334], [343, 356], [364, 376], [386, 399], [410, 422], [431, 444],#18
            [453, 466], [477, 488], [498, 511], [520, 533],   #22
            [541, 554], [564, 574], [585, 600], [608, 621], [630, 643], [653, 665],  #28
            [676, 688], [699, 712], [722, 731], [743, 753], [761, 773], [785, 798],#34
            [808, 821], [831,843], [851, 863], [874, 887], [896, 910], [918, 932],#40
            [942, 954], [964, 977], [987, 998], [1008, 1020],#44
            [1031, 1041], [1051, 1064], [1072, 1085]
        ],
            14: [
            [51, 65], [74, 86], [95, 107], [117, 130], [140, 153], [163, 175],  #6
            [185, 198], [207, 220], [229, 242], [253, 264], [274, 286], [296, 309],#12
            [318, 331], [340, 353], [361, 373], [383, 396], [405, 419], [427, 441],#18
            [450, 462], [470, 484], [493, 505], [515, 527],   #22
            [539, 549], [560, 572], [583, 596], [604, 615], [627, 640], [650, 664],  #28
            [673, 686], [694, 707], [717, 729], [737, 750], [760, 771], [781, 791],#34
            [804, 818], [826,839], [848, 861], [871, 885], [893, 903], [913, 925],#40
            [935, 947], [957, 971], [979, 993], [1002, 1016], #44
            [1024, 1037], [1046, 1058], [1068, 1079]
        ]
        }

        # Get image path - FIX: Navigate to project root
        self.base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.image_path = os.path.join(self.base_dir, "images", "D2")

        # Create output dataframe for all rows
        self.all_data = pd.DataFrame()
        
        # Define target stimuli based on (row, letter_num) combinations
        # These are the combinations where target = "si"
        # Note: These mappings come from the D2 test specifications.
        # Row 10 intentionally has 28 instead of 29 (compared to rows 1, 7, 13).
        # Row 4 is not defined in the specifications, so it has no targets.
        self.TARGET_STIMULI = {
            1: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            2: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            3: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            4: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            5: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            6: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            7: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
            8: [2, 5, 8, 13, 14, 16, 19, 21, 23, 24, 29, 30, 33, 35, 37, 39, 40, 41, 42, 44, 46, 47],
            9: [3, 4, 7, 9, 13, 14, 16, 18, 21, 23, 26, 28, 32, 34, 37, 39, 41, 42, 43, 45, 47],
            10: [1, 5, 6, 9, 11, 12, 13, 15, 19, 24, 25, 27, 29, 33, 34, 37, 38, 40, 43, 45, 46],
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
            # Scale the example image to a reasonable size (keep it moderate since it's just an example)
            scale_factor = 3  # Fixed scale for the small example image
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

        # Calculate dynamic scale factor to fit 100% of screen width
        # This maintains aspect ratio while filling the full width
        original_width = img_prueba.get_width()
        original_height = img_prueba.get_height()
        
        # Validate image dimensions to prevent division by zero
        if original_width <= 0 or original_height <= 0:
            display.text(
                self.screen, self.font,
                "Error: Invalid training image dimensions",
                "center", "center", (255, 0, 0)
            )
            pygame.display.flip()
            display.wait(3000)
            return []
        
        scale_factor = self.screen_x / original_width
        
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        img_prueba = pygame.transform.scale(img_prueba, (new_width, new_height))

        img_width = img_prueba.get_width()
        img_height = img_prueba.get_height()
        
        # Position image at full width (x=0)
        img_x = 0
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
        # Use black background for trial screens
        black_background = pygame.Surface(self.screen.get_size())
        black_background = black_background.convert()
        black_background.fill((0, 0, 0))
        self.screen.blit(black_background, (0, 0))
        
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

        # Calculate dynamic scale factor to fit 100% of screen width
        # This maintains aspect ratio while filling the full width
        original_width = img_row.get_width()
        original_height = img_row.get_height()
        
        # Validate image dimensions to prevent division by zero
        if original_width <= 0 or original_height <= 0:
            display.text(
                self.screen, self.font,
                f"Error: Invalid dimensions for 'fila{row_num}.png'",
                "center", "center", (255, 0, 0)
            )
            pygame.display.flip()
            display.wait(2000)
            
            # Return DataFrame with expected structure
            row_data = []
            for i in range(self.ROW_LETTERS):
                letter_num = i + 1
                is_target = "si" if letter_num in self.TARGET_STIMULI.get(row_num, []) else "no"
                row_data.append({
                    'row': row_num,
                    'letter_num': letter_num,
                    'selected': False,
                    'timestamp': 0,
                    'target': is_target
                })
            return pd.DataFrame(row_data)
        
        scale_factor = self.screen_x / original_width
        
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        img_row = pygame.transform.scale(img_row, (new_width, new_height))

        img_width = img_row.get_width()
        img_height = img_row.get_height()

        # Position image at full width (x=0) and center vertically
        img_x = 0
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
                            self.screen.blit(black_background, (0, 0))
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
