import os
import sys

import pandas as pd
import pygame

from pygame.locals import *
from utils import display


class Ikigai(object):
    MAX_SELECTIONS = 4

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background

        self.font_title = pygame.font.SysFont("arial", 38)
        self.font = pygame.font.SysFont("arial", 30)
        self.font_small = pygame.font.SysFont("arial", 24)

        self.screen_x = self.screen.get_width()
        self.screen_y = self.screen.get_height()

        self.background.fill((255, 255, 255))
        pygame.display.set_caption("Ikigai")
        pygame.mouse.set_visible(1)

        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.statements_dir = os.path.join(os.path.dirname(self.base_dir), "enunciados")

    def _load_options(self, file_name):
        options_path = os.path.join(self.statements_dir, file_name)
        try:
            with open(options_path, "r", encoding="utf-8") as options_file:
                return [line.strip() for line in options_file if line.strip()]
        except FileNotFoundError:
            print(f"ERROR: Statements file not found: {options_path}")
            sys.exit(1)
        except Exception as exc:
            print(f"ERROR: Failed to load statements file: {exc}")
            sys.exit(1)

    def _wrap_text(self, text, font, max_width):
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

    def _draw_wrapped_text(self, text, font, x, y, max_width, *, center=False, color=(0, 0, 0), line_height=None):
        if line_height is None:
            line_height = font.get_linesize() + 6

        lines = self._wrap_text(text, font, max_width)
        for index, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            draw_x = x
            if center:
                draw_x = x + (max_width - line_surface.get_width()) // 2
            self.screen.blit(line_surface, (draw_x, y + index * line_height))

        return y + len(lines) * line_height

    def _draw_button(self, rect, label, enabled):
        fill_color = (210, 210, 210) if enabled else (235, 235, 235)
        border_color = (0, 0, 0) if enabled else (160, 160, 160)
        text_color = (0, 0, 0) if enabled else (120, 120, 120)

        pygame.draw.rect(self.screen, fill_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, 2)

        label_surface = self.font.render(label, True, text_color)
        self.screen.blit(
            label_surface,
            (
                rect.centerx - label_surface.get_width() // 2,
                rect.centery - label_surface.get_height() // 2,
            ),
        )

    def _draw_scrollbar(self, list_rect, scroll_offset, max_scroll):
        if max_scroll <= 0:
            return

        track_rect = pygame.Rect(list_rect.right - 10, list_rect.y + 10, 6, list_rect.height - 20)
        pygame.draw.rect(self.screen, (220, 220, 220), track_rect)

        visible_ratio = list_rect.height / float(list_rect.height + max_scroll)
        handle_height = max(40, int(track_rect.height * visible_ratio))
        handle_range = track_rect.height - handle_height
        handle_y = track_rect.y
        if handle_range > 0:
            handle_y += int((scroll_offset / float(max_scroll)) * handle_range)

        handle_rect = pygame.Rect(track_rect.x, handle_y, track_rect.width, handle_height)
        pygame.draw.rect(self.screen, (120, 120, 120), handle_rect)

    def _draw_selection_page(self, prompt, options, selected_indices, button_label, scroll_offset):
        self.screen.blit(self.background, (0, 0))

        display.text(self.screen, self.font_title, "Ikigai", "center", 35)

        prompt_y = 100
        prompt_x = 70
        prompt_width = self.screen_x - 140
        prompt_y = self._draw_wrapped_text(
            prompt,
            self.font_small,
            prompt_x,
            prompt_y,
            prompt_width,
            center=False,
            line_height=32,
        )

        counter_text = f"Seleccionadas: {len(selected_indices)} / {self.MAX_SELECTIONS}"
        counter_surface = self.font.render(counter_text, True, (0, 0, 0))
        self.screen.blit(counter_surface, (70, prompt_y + 10))

        help_text = "Usa la rueda del ratón o las flechas arriba/abajo para desplazarte."
        help_surface = self.font_small.render(help_text, True, (110, 110, 110))
        self.screen.blit(help_surface, (70, prompt_y + 55))

        list_rect = pygame.Rect(70, prompt_y + 95, self.screen_x - 140, self.screen_y - (prompt_y + 220))
        pygame.draw.rect(self.screen, (248, 248, 248), list_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), list_rect, 2)

        button_rect = pygame.Rect((self.screen_x - 220) // 2, self.screen_y - 90, 220, 52)

        option_rects = []
        item_gap = 10
        item_y = list_rect.y + 10 - scroll_offset
        inner_width = list_rect.width - 34

        self.screen.set_clip(list_rect)
        for option_index, option_text in enumerate(options):
            wrapped_lines = self._wrap_text(option_text, self.font_small, inner_width - 45)
            option_height = max(48, len(wrapped_lines) * 28 + 18)
            option_rect = pygame.Rect(list_rect.x + 10, item_y, inner_width, option_height)
            option_rects.append((option_index, option_rect))

            if option_rect.bottom >= list_rect.y and option_rect.top <= list_rect.bottom:
                is_selected = option_index in selected_indices
                fill_color = (220, 240, 255) if is_selected else (255, 255, 255)
                border_color = (0, 120, 215) if is_selected else (160, 160, 160)
                pygame.draw.rect(self.screen, fill_color, option_rect)
                pygame.draw.rect(self.screen, border_color, option_rect, 2)

                marker_rect = pygame.Rect(option_rect.x + 12, option_rect.centery - 10, 20, 20)
                pygame.draw.rect(self.screen, (255, 255, 255), marker_rect)
                pygame.draw.rect(self.screen, border_color, marker_rect, 2)
                if is_selected:
                    pygame.draw.line(
                        self.screen,
                        border_color,
                        (marker_rect.x + 4, marker_rect.y + 11),
                        (marker_rect.x + 9, marker_rect.y + 16),
                        3,
                    )
                    pygame.draw.line(
                        self.screen,
                        border_color,
                        (marker_rect.x + 9, marker_rect.y + 16),
                        (marker_rect.x + 17, marker_rect.y + 4),
                        3,
                    )

                text_y = option_rect.y + 10
                for line in wrapped_lines:
                    line_surface = self.font_small.render(line, True, (0, 0, 0))
                    self.screen.blit(line_surface, (option_rect.x + 45, text_y))
                    text_y += 28

            item_y += option_height + item_gap

        self.screen.set_clip(None)

        total_height = item_y - (list_rect.y + 10) + scroll_offset - item_gap
        max_scroll = max(0, total_height - list_rect.height)
        self._draw_scrollbar(list_rect, scroll_offset, max_scroll)

        self._draw_button(button_rect, button_label, len(selected_indices) == self.MAX_SELECTIONS)
        pygame.display.flip()

        return option_rects, list_rect, button_rect, max_scroll

    def _run_selection_page(self, prompt, options, button_label):
        selected_indices = []
        scroll_offset = 0

        while True:
            option_rects, list_rect, button_rect, max_scroll = self._draw_selection_page(
                prompt, options, selected_indices, button_label, scroll_offset
            )

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    if event.key == K_F12:
                        sys.exit(0)
                    elif event.key == K_UP:
                        scroll_offset = max(0, scroll_offset - 40)
                    elif event.key == K_DOWN:
                        scroll_offset = min(max_scroll, scroll_offset + 40)
                    elif event.key in (K_RETURN, K_KP_ENTER) and len(selected_indices) == self.MAX_SELECTIONS:
                        return selected_indices
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        if button_rect.collidepoint(mouse_pos) and len(selected_indices) == self.MAX_SELECTIONS:
                            return selected_indices

                        for option_index, option_rect in option_rects:
                            if option_rect.collidepoint(mouse_pos) and list_rect.collidepoint(mouse_pos):
                                if option_index in selected_indices:
                                    selected_indices.remove(option_index)
                                elif len(selected_indices) < self.MAX_SELECTIONS:
                                    selected_indices.append(option_index)
                                break
                    elif event.button == 4:
                        scroll_offset = max(0, scroll_offset - 40)
                    elif event.button == 5:
                        scroll_offset = min(max_scroll, scroll_offset + 40)
                elif event.type == MOUSEWHEEL:
                    scroll_offset = min(max_scroll, max(0, scroll_offset - event.y * 40))

    def _show_intro(self):
        self.screen.blit(self.background, (0, 0))

        lines = [
            "Para las siguientes 2 preguntas tienes que elegir 4 opciones entre todas, excluyendo las demás.",
            "",
            "Por favor, pulsa la barra espaciadora para proceder.",
        ]

        total_height = 0
        rendered_lines = []
        for line in lines:
            if line:
                wrapped = self._wrap_text(line, self.font, self.screen_x - 180)
                rendered_lines.append(wrapped)
                total_height += len(wrapped) * 40
            else:
                rendered_lines.append([""])
                total_height += 24

        y_pos = max(80, (self.screen_y - total_height) // 2)
        for wrapped_lines in rendered_lines:
            if wrapped_lines == [""]:
                y_pos += 24
                continue
            for line in wrapped_lines:
                display.text(self.screen, self.font, line, "center", y_pos)
                y_pos += 40

        pygame.display.flip()
        display.wait_for_space()

    def _show_end_screen(self):
        self.screen.blit(self.background, (0, 0))
        display.text(self.screen, self.font_title, "Fin de la tarea", "center", "center")
        display.text(
            self.screen,
            self.font_small,
            "Pulsa la barra espaciadora para continuar",
            "center",
            self.screen_y // 2 + 70,
        )
        pygame.display.flip()
        display.wait_for_space()

    def _build_results(self, world_options, world_selected, paid_options, paid_selected):
        rows = []
        trial = 1

        sections = [
            ("Ikigai_WorldNeed", world_options, world_selected),
            ("Ikigai_PaidFor", paid_options, paid_selected),
        ]

        for section_name, options, selected_indices in sections:
            selection_order = {index: order + 1 for order, index in enumerate(selected_indices)}
            for option_index, option_text in enumerate(options, start=1):
                rows.append(
                    {
                        "trial": trial,
                        "pagina": section_name,
                        "numero_del_enunciado": option_index,
                        "opcion": option_text,
                        "respuesta": 1 if option_index - 1 in selected_indices else 0,
                        "orden_seleccion": selection_order.get(option_index - 1, ""),
                    }
                )
                trial += 1

        return pd.DataFrame(rows)

    def run(self):
        self._show_intro()

        world_options = self._load_options("IKIGAI_WorldNeed")
        paid_options = self._load_options("IKIGAI_PaidFor")

        world_prompt = (
            "De los siguientes trabajos selecciona cuáles cuatro consideras son más importantes para el mundo hoy y en los "
            "próximos años. Puedes cambiar tu respuesta clicando de nuevo en la opción seleccionada. Al tener tus 4 "
            "opciones seleccionadas puedes avanzar seleccionando el botón de abajo de avanzar."
        )
        paid_prompt = (
            "De las siguientes habilidades o tendencias comportamentales selecciona las 4 que consideras están más "
            "presentes en tu persona. Cuando hayas terminado pulsa el botón Terminar."
        )

        world_selected = self._run_selection_page(world_prompt, world_options, "Avanzar")
        paid_selected = self._run_selection_page(paid_prompt, paid_options, "Terminar")

        self._show_end_screen()

        print("- Ikigai complete")

        return self._build_results(world_options, world_selected, paid_options, paid_selected)
