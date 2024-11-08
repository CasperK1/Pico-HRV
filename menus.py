from bitmaps import wifi, no_wifi
from ssd1306 import SSD1306_I2C
from lib.fifo import Fifo
import framebuf

class BaseMenu:
    def __init__(self, oled, items):
        self.oled = oled
        self.items = items
        self.wifi_conn = False
        self.font_width = 8
        self.line_height = 15
        self.selector_pos_y = 0
        self.spacing = 15
        self.scroll_offset = 0
        self.max_visible_items = 4
        # WiFi icons
        self.wifi = framebuf.FrameBuffer(
            bytearray(wifi), 15, 12, framebuf.MONO_HLSB)
        self.no_wifi = framebuf.FrameBuffer(
            bytearray(no_wifi), 17, 16, framebuf.MONO_HLSB)

    def select_next(self):
        if self.selector_pos_y < len(self.items) - 1:
            self.selector_pos_y += 1
            if self.selector_pos_y >= self.scroll_offset + self.max_visible_items:
                self.scroll_offset += 1

    def select_previous(self):
        if self.selector_pos_y > 0:
            self.selector_pos_y -= 1
            if self.selector_pos_y < self.scroll_offset:
                self.scroll_offset -= 1

    def select_item(self):
        return self.items[self.selector_pos_y]

    def _draw_wifi_status(self):
        """Draw WiFi status icon"""
        if self.wifi_conn:
            self.oled.blit(self.wifi, 110, 0)
        else:
            self.oled.blit(self.no_wifi, 110, 0)

    def _draw_scroll_indicators(self):
        """Draw scroll indicators if needed"""
        if self.scroll_offset > 0:
            self.oled.text("^", 120, 20, 1)
            self.oled.text("|", 120, 22, 1)
        if self.scroll_offset + self.max_visible_items < len(self.items):
            self.oled.text("|", 120, 52, 1)
            self.oled.text("v", 120, 56, 1)


class MainMenu(BaseMenu):
    def display(self):
        self.oled.fill(0)
        self._draw_wifi_status()
        self._draw_scroll_indicators()

        # Draw menu items
        for i in range(self.max_visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(self.items):
                break

            item = self.items[item_index]
            item_position_y = i * self.line_height
            text_width = len(item) * self.font_width + 8

            self.oled.text(f'{item}', 4, item_position_y + 3, 1)

            if item_index == self.selector_pos_y:
                self.oled.rect(0, item_position_y, text_width, 12, 1)

        self.oled.show()


class HistoryMenu(BaseMenu):
    def __init__(self, oled, items):
        super().__init__(oled, items)
        self.max_visible_items = 3  # Reduced for header space
        self.header_height = 15

    def display(self):
        self.oled.fill(0)

        # Draw header
        self.oled.fill_rect(0, 0, 56, 10, 1)
        self.oled.text("HISTORY", 0, 1, 0)

        self._draw_wifi_status()
        self._draw_scroll_indicators()

        # Handle empty history
        if len(self.items) <= 1:
            back_button = self.items[0]
            back_button_pos_y = 50
            text_width = len(back_button) * self.font_width + 8

            self.oled.text("Nothing here...", 0, 25, 1)
            self.oled.text(f'{back_button}', 4, back_button_pos_y + 3, 1)
            self.oled.rect(0, back_button_pos_y, text_width, 12, 1)
        else:
            # Draw menu items
            for i in range(self.max_visible_items):
                item_index = self.scroll_offset + i
                if item_index >= len(self.items):
                    break

                item = self.items[item_index]
                item_position_y = i * self.line_height + self.header_height + 5
                text_width = len(item) * self.font_width + 8

                self.oled.text(f'{item}', 4, item_position_y + 3, 1)

                if item_index == self.selector_pos_y:
                    self.oled.rect(0, item_position_y, text_width, 12, 1)

        self.oled.show()


class SettingsMenu(BaseMenu):
    def __init__(self, oled, items):
        super().__init__(oled, items)
        self.max_visible_items = 3  # Reduced for header space
        self.header_height = 15

    def display(self):
        self.oled.fill(0)

        # Draw header
        self.oled.fill_rect(0, 0, 64, 10, 1)
        self.oled.text("SETTINGS", 0, 1, 0)

        self._draw_wifi_status()
        self._draw_scroll_indicators()

        # Draw menu items
        for i in range(self.max_visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(self.items):
                break

            item = self.items[item_index]
            item_position_y = i * self.line_height + self.header_height + 5
            text_width = len(item) * self.font_width + 8

            self.oled.text(f'{item}', 4, item_position_y + 3, 1)

            if item_index == self.selector_pos_y:
                self.oled.rect(0, item_position_y, text_width, 12, 1)

        self.oled.show()
