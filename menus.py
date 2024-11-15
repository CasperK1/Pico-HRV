from bitmaps import wifi, no_wifi
import framebuf
import uasyncio
from time import ticks_ms, ticks_diff

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

    def draw_scroll_indicators(self):
        if self.scroll_offset > 0:
            self.oled.text("^", 120, 20, 1)
            self.oled.text("|", 120, 22, 1)
        if self.scroll_offset + self.max_visible_items < len(self.items):
            self.oled.text("|", 120, 52, 1)
            self.oled.text("v", 120, 56, 1)

    def draw_wifi_status(self):
        """Draw WiFi status icon"""
        if self.wifi_conn:
            self.oled.blit(self.wifi, 110, 0)
        else:
            self.oled.blit(self.no_wifi, 110, 0)



class MainMenu(BaseMenu):
    def __init__(self, oled, items, rot):
        super().__init__(oled, items)
        self.rot = rot


    async def handle_input(self):
        while True: 
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if data == 1:
                    self.select_next()
                elif data == -1:
                    self.select_previous()
                elif data == 0:
                    selected_item = self.select_item()
                    return selected_item

            self.display()
            await uasyncio.sleep_ms(20)
    
    def display(self):
        self.oled.fill(0)
        self.draw_scroll_indicators()
        self.draw_wifi_status()

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
    def __init__(self, oled, items, rot):
        super().__init__(oled, items)
        self.rot = rot
        self.max_visible_items = 3
        self.header_height = 15
    
    async def handle_input(self):
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if data == 1:
                    self.select_next()
                elif data == -1:
                    self.select_previous()
                elif data == 0:
                    selected_item = self.select_item()
                    if selected_item == "Back":
                        self.selector_pos_y = 0
                        self.scroll_offset = 0
                        return "MAIN"
                    
            self.display()
            await uasyncio.sleep_ms(20)


    def display(self):
        self.oled.fill(0)
        self.oled.fill_rect(0, 0, 56, 10, 1)
        self.oled.text("HISTORY", 0, 1, 0)
        self.draw_scroll_indicators()
        self.draw_wifi_status()

        if len(self.items) <= 1:
            back_button = self.items[0]
            back_button_pos_y = 50
            text_width = len(back_button) * self.font_width + 8
            self.oled.text("Nothing here...", 0, 25, 1)
            self.oled.text(f'{back_button}', 4, back_button_pos_y + 3, 1)
            self.oled.rect(0, back_button_pos_y, text_width, 12, 1)
        else:
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
    def __init__(self, oled, items, rot, wlan):
        super().__init__(oled, items)
        self.rot = rot
        self.wlan = wlan
        self.wlan_signal = "Disconnected"
        self.current_submenu = None
        self.max_visible_items = 3
        self.header_height = 15
        self.last_signal_check = 0
        self.signal_check_interval = 5000 


    async def handle_input(self):
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if self.current_submenu == "wifi":
                    if data == 0:
                        self.current_submenu = None
                else:
                    if data == 1:
                        self.select_next()
                    elif data == -1:
                        self.select_previous()
                    elif data == 0:
                        selected_item = self.select_item()
                        if selected_item == "WiFi":
                            self.current_submenu = "wifi"
                        elif selected_item == "MQTT":
                            pass
                        elif selected_item == "Back":
                            self.selector_pos_y = 0
                            return "MAIN"
                        
            # Check WiFi signal strength every 5 seconds            
            current_time = ticks_ms()
            if ticks_diff(current_time, self.last_signal_check) > self.signal_check_interval:
                self.wlan_signal_strength()
                self.last_signal_check = current_time

            self.display()
            await uasyncio.sleep_ms(20)

    def display(self):
        self.oled.fill(0)

        if self.current_submenu == "wifi":
            self.wifi_submenu()
            return
        
        self.oled.fill_rect(0, 0, 64, 10, 1)
        self.oled.text("SETTINGS", 0, 1, 0)
        self.draw_scroll_indicators()
        self.draw_wifi_status()

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


    def wlan_signal_strength(self):
        if not self.wlan.isconnected():
            self.wlan_signal = "Disconnected"
            return

        rssi = self.wlan.status("rssi")
        if rssi > -60:
            self.wlan_signal = "Great"
        elif rssi > -70:
            self.wlan_signal = "Fair"
        elif rssi > -90:
            self.wlan_signal = "Poor"
        else:
            self.wlan_signal = "Very Poor"

            
    def wifi_submenu(self):
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 33, 10, 1)
            self.oled.text("WIFI", 0, 1, 0)
            self.draw_scroll_indicators()
            self.oled.text(f"Signal strength:", 0, 20, 1)
            self.oled.text(f"{self.wlan_signal}", 0, 30, 1)
            self.oled.show()
