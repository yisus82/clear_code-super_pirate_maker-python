import pygame
import pygame_gui
from pygame_gui.windows import UIConfirmationDialog, UIFileDialog, UIMessageWindow


class UIManager:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.gui_manager = pygame_gui.UIManager((window_width, window_height))
        self.gui_manager.preload_fonts(
            [
                {
                    "name": "noto_sans",
                    "point_size": 14,
                    "style": "bold",
                    "antialiased": "1",
                }
            ]
        )
        self.opened_dialog = None

    def process_event(self, event):
        if (
            event.type == pygame_gui.UI_WINDOW_CLOSE
            and event.ui_element == self.opened_dialog
        ):
            self.opened_dialog = None
        self.gui_manager.process_events(event)

    def prompt_file(self):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.opened_dialog = UIFileDialog(
            pygame.Rect(window_width // 2 - 200, window_height // 2 - 200, 400, 400),
            self.gui_manager,
            window_title="Load grid...",
            initial_file_path="../levels",
            allow_picking_directories=True,
            allow_existing_files_only=True,
            allowed_suffixes={"txt": "Text files"},
        )

    def show_information_dialog(self, title="Info", message=""):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.opened_dialog = UIMessageWindow(
            rect=pygame.Rect(
                window_width // 2 - 200, window_height // 2 - 200, 400, 200
            ),
            manager=self.gui_manager,
            window_title=title,
            html_message=message,
        )

    def show_confirmation_dialog(
        self,
        title="Confirmation",
        message="",
        button_text="Confirm",
        object_id="confirmation_dialog",
        blocking=True,
    ):
        window_width = self.display_surface.get_width()
        window_height = self.display_surface.get_height()
        self.opened_dialog = UIConfirmationDialog(
            rect=pygame.Rect(
                window_width // 2 - 200, window_height // 2 - 200, 400, 200
            ),
            manager=self.gui_manager,
            window_title=title,
            action_long_desc=message,
            action_short_name=button_text,
            blocking=blocking,
            object_id=object_id,
        )

    def display(self):
        self.gui_manager.draw_ui(self.display_surface)

    def update(self, dt):
        self.gui_manager.update(dt)
