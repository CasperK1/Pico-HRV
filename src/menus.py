from src.components.save_measurements import Measurements
from src.bitmaps import wifi, sig_low, sig_mid, sig_high, measure_hr, hrv_analysis, history, settings, kubios
import framebuf
import uasyncio
from src.components.HRV import HRVAnalysis
from src.components.HR import Detect_peaks
from time import ticks_ms, ticks_diff, time, localtime
from machine import Pin
from src.wifi import PicoConnection
import json

class BaseMenu:
    def __init__(self, oled, pico_conn: PicoConnection, items = []):
        self.oled = oled
        self.items = items
        self.pico_conn = pico_conn
        self.wlan = pico_conn.wlan
        self.wifi_conn = False
        self.font_width = 8
        self.line_height = 15
        self.selector_pos_y = 0
        self.spacing = 15
        self.scroll_offset = 0
        self.max_visible_items = 4
        self.wifi = framebuf.FrameBuffer(
            bytearray(wifi), 15, 12, framebuf.MONO_HLSB)
        self.signal_strength_bitmaps = {
            "Great": framebuf.FrameBuffer(bytearray(sig_high), 19, 14, framebuf.MONO_HLSB),
            "Mid": framebuf.FrameBuffer(bytearray(sig_mid), 19, 14, framebuf.MONO_HLSB),
            "Low": framebuf.FrameBuffer(bytearray(sig_low), 18, 14, framebuf.MONO_HLSB)
        }
        self.save = Measurements()


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

    def disable_rotary(self):
        """Disable rotary encoder interrupts"""
        self.rot.a.irq(None)  
        self.rot.sw.irq(None)  
        while self.rot.fifo.has_data():
            self.rot.fifo.get()

    def enable_rotary(self):
        self.rot.a.irq(handler=self.rot.rotary_handler, trigger=Pin.IRQ_RISING, hard=True)
        self.rot.sw.irq(handler=self.rot.switch_handler, trigger=Pin.IRQ_RISING, hard=True)

    def draw_scroll_indicators(self, optional_amount=None):
        line_x = 126
        line_start_y = 20
        line_end_y = 56
        box_height = 8

        self.oled.vline(line_x, line_start_y, line_end_y - line_start_y, 1)

        # Calculate box position based on current selection
        if optional_amount:
            total_items = optional_amount
        else:
            total_items = len(self.items)
        scroll_range = line_end_y - line_start_y - box_height
        box_y = line_start_y + int((self.selector_pos_y / (total_items - 1)) * scroll_range)
        self.oled.fill_rect(line_x - 1, box_y, 3, box_height, 1)

    def draw_wifi_status(self):
        """Draw WiFi status icon"""
        if self.wifi_conn:
            self.oled.blit(self.wifi, 85, 0)
        else:
            self.oled.blit(self.wifi, 105, 0)
            self.oled.text("!", 117, 0)  

    def draw_signal_strength(self, x_coord=103):
        """Draw WiFi signal strength icon"""
        if self.wifi_conn == True:
            signal_strength = "Great"
            if self.wifi_conn:
                rssi = self.wlan.status("rssi")
                if rssi > -60:
                    signal_strength = "Great"
                elif rssi > -70:
                    signal_strength = "Mid"
                elif rssi > -90:
                    signal_strength = "Low"
                else:
                    signal_strength = "Low"

            self.oled.blit(self.signal_strength_bitmaps[signal_strength], x_coord, -1)

class MainMenu(BaseMenu):
    def __init__(self, oled, pico_conn, items, rot):
        super().__init__(oled, pico_conn, items)
        self.rot = rot
        self.max_visible_items = 2
        self.main_menu_bitmaps = {
            "MEASURE HR": (framebuf.FrameBuffer(bytearray(measure_hr), 110, 14, framebuf.MONO_HLSB), 110),
            "HRV ANALYSIS": (framebuf.FrameBuffer(bytearray(hrv_analysis), 117, 17, framebuf.MONO_HLSB), 117),
            "KUBIOS": (framebuf.FrameBuffer(bytearray(kubios), 77, 17, framebuf.MONO_HLSB), 77),
            "HISTORY": (framebuf.FrameBuffer(bytearray(history), 79, 12, framebuf.MONO_HLSB), 79),
            "SETTINGS": (framebuf.FrameBuffer(bytearray(settings), 96, 16, framebuf.MONO_HLSB), 96)
        }
        self.wifi_icon = framebuf.FrameBuffer(
            bytearray(wifi), 15, 12, framebuf.MONO_HLSB)

        self.first_item_y = 20   
        self.second_item_y = 45 

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
        self.oled.blit(self.wifi_icon, 0, -1)
        if self.wifi_conn == False:
            self.oled.text("!", 13, 0) 
        self.draw_scroll_indicators()
        self.draw_signal_strength(20)
        self.oled.hline(0, 11, 128, 1)

        for i in range(self.max_visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(self.items):
                break

            item = self.items[item_index]
            if item not in self.main_menu_bitmaps:
                continue

            bitmap, width = self.main_menu_bitmaps[item]

            x = (125 - width) // 2
            if i == 0:
                y = self.first_item_y
                # Special case for KUBIOS HISTORY page
                if item == "KUBIOS" and self.items[item_index + 1] == "HISTORY":
                    y = 17 
                    x = 23
            else:
                y = self.second_item_y

            self.oled.blit(bitmap, x, y)
            # Draw selection highlight
            if item_index == self.selector_pos_y:
                left_x = x - 3
                right_x = x + width + 1
                line_height = 14
                line_y = y + 1 

                # Draw left line
                self.oled.vline(left_x, line_y, line_height, 1)
                # Draw right line
                self.oled.vline(right_x, line_y, line_height, 1)

        self.oled.show()


class MeasureHRMenu(BaseMenu):
    def __init__(self, oled, pico_conn, rot):
        super().__init__(oled, pico_conn)
        self.rot = rot
        self.header_height = 15
        self.measuring = False
        self.current_hr = 0
        self.last_update = 0
        self.update_interval = 0 
        self.HR = Detect_peaks()

    async def handle_input(self):
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if data == 0:
                    if not self.measuring:
                        self.start_measurement()
                        self.start_time = ticks_ms()
                    else:
                        self.stop_measurement()
                        self.selector_pos_y = 0
                        return "MAIN"

            if not self.measuring:
                self.display()
            else:
                current_time = ticks_ms()
                if ticks_diff(current_time, self.last_update) > self.update_interval:
                    self.current_hr = self.calculate_hr()
                    self.last_update = current_time

    def display(self):
        self.oled.fill(0)
        self.oled.fill_rect(0, 0, 80, 10, 1)
        self.oled.text("MEASURE HR", 0, 1, 0)
        self.draw_wifi_status()
        self.draw_signal_strength()

        if not self.measuring:
            self.oled.text("Press to start", 0, 25, 1)
            self.oled.text("measurement", 0, 35, 1)
        else:
            self.oled.text(f"HR: {self.current_hr} BPM", 0, 25, 1)
            self.oled.text("Press to return to main", 0, 45, 1)

        self.oled.show()

    def start_measurement(self):
        self.measuring = True
        self.current_hr = 0
        self.last_update = ticks_ms()
        # Initialize sensor and measurement here

    def stop_measurement(self):
        self.measuring = False
        self.HR.reset()
        # Cleanup/stop sensor here.

    def calculate_hr(self):
        self.HR.run()


class HRVAnalysisMenu(BaseMenu):
   def __init__(self, oled, pico_conn, rot):
       super().__init__(oled, pico_conn)
       self.rot = rot
       self.items = ["Measure Again", "To Main Menu"]
       self.header_height = 15
       self.measuring = False
       self.done_measuring = False
       self.collection_time = 30000
       self.start_time = 0
       self.HR = Detect_peaks()
       self.HRV = HRVAnalysis()
       self.hrv_results = {
           'PPI (ms)': 0,
           'Mean HR': 0,
           'RMSSD': 0,
           'SDNN': 0
       }
       self.selector_pos_y = 0

   async def handle_input(self):
       while True:
           if self.rot.fifo.has_data():
               data = self.rot.get_last_input()
               if self.measuring:
                   if data == 0:
                       self.measuring = False
                       self.selector_pos_y = 0
                       self.HR.reset()
                       return "MAIN"
               elif self.done_measuring:
                   if data == 1:
                       self.select_next()
                   elif data == -1:
                       self.select_previous()
                   elif data == 0:
                       selected = self.select_item()
                       if selected == "Measure Again":
                           self.measuring = True
                           self.done_measuring = False
                           self.start_time = ticks_ms()
                           self.hrv_results = {}
                       else:
                           return "MAIN"
               else:
                   if data == 0:
                       # hrv_results always returns true so checking for values necessary 
                       if not self.measuring and any(v != 0 for v in self.hrv_results.values()):
                           
                           self.done_measuring = True
                       else:
                           self.measuring = True
                           self.start_time = ticks_ms()
                           self.hrv_results = {}

           if not self.measuring:
               self.display()
           else:
               current_time = ticks_ms()
               elapsed = ticks_diff(current_time, self.start_time)
               remaining = max(0, (self.collection_time - elapsed) // 1000)
               self.HR.run(remaining)
               if elapsed >= self.collection_time:
                   ibi_data = self.HR.ibi_values
                   self.HR.reset()
                   await self.calculate_hrv(ibi_data)
                   self.measuring = False

   async def calculate_hrv(self, ibi):
        self.hrv_results = self.HRV.calculate(ibi)
        self.save.add_to_file(self.hrv_results)
        if self.wlan.isconnected():
            self.disable_rotary()
            self.oled.fill(0)
            self.oled.text("Connecting to", 0, 20, 1)
            self.oled.text("MQTT...", 0, 32, 1)
            self.oled.show()
            await self.pico_conn.connect_mqtt()
            await self.pico_conn.mqtt_publish(self.hrv_results, topic="hr-data")
            if not self.pico_conn.mqtt_client:
                self.oled.fill(0)
                self.oled.text("MQTT connection", 0, 20, 1)
                self.oled.text("failed!!!", 0, 32, 1)
                self.oled.show()
                await uasyncio.sleep(3)
            self.enable_rotary()


   def display(self):
       self.oled.fill(0)
       self.oled.fill_rect(0, 0, 96, 10, 1)
       self.oled.text("HRV ANALYSIS", 0, 1, 0)
       self.draw_wifi_status()
       self.draw_signal_strength()

       if not self.measuring and all(v == 0 for v in self.hrv_results.values()):
           self.oled.text("Press to start", 0, 25, 1)
           self.oled.text("HRV analysis", 0, 35, 1)
           self.oled.text("Measuring 30s", 0, 55, 1)
       elif self.done_measuring:
           menu_y = 25
           for i, item in enumerate(self.items):
               self.oled.text(f"{item}", 4, menu_y + (i * 15), 1)
               if i == self.selector_pos_y:
                   text_width = len(item) * self.font_width + 8
                   self.oled.rect(0, menu_y + (i * 15) - 2, text_width, 12, 1)
       else:
           y = 20
           display_order = ['Mean HR', 'PPI (ms)', 'RMSSD', 'SDNN']
           for key in display_order:
               value = self.hrv_results.get(key, 0)
               self.oled.text(f"{key}: {value:.0f}", 0, y, 1)
               y += 11

       self.oled.show()


class HistoryMenu(BaseMenu):
    def __init__(self, oled, pico_conn, items, rot):
        super().__init__(oled, pico_conn, items)
        self.rot = rot
        self.max_visible_items = 3
        self.header_height = 15
        self.selected_measurement = None
        self.HRV_history = self.save.get_from_file()

    async def handle_input(self):
        self.HRV_history = self.save.get_from_file()
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if self.selected_measurement is not None:
                    if data == 0:
                        self.selected_measurement = None
                else:
                    if data == 1:
                        if self.selector_pos_y < len(self.HRV_history):
                            self.select_next()
                    elif data == -1:
                        self.select_previous()
                    elif data == 0:
                        # Back button selected
                        if self.selector_pos_y >= len(self.HRV_history):
                            selected_item = self.items[self.selector_pos_y -
                                                       len(self.HRV_history)]
                            if selected_item == "Back":
                                self.selector_pos_y = 0
                                self.scroll_offset = 0
                                return "MAIN"
                        else:
                            self.selected_measurement = self.HRV_history[self.selector_pos_y]

            self.display()
            await uasyncio.sleep_ms(20)

    def display(self):
        self.oled.fill(0)
        self.oled.fill_rect(0, 0, 56, 10, 1)
        self.oled.text("HISTORY", 0, 1, 0)
        self.draw_wifi_status()
        self.draw_signal_strength()

        if len(self.HRV_history) == 0:
            self.oled.text("Nothing here...", 0, 25, 1)
            # Draw back button from items
            back_button = self.items[0]  # Assuming "Back" is the first item
            back_button_pos_y = 50
            text_width = len(back_button) * self.font_width + 8
            self.oled.text(f'{back_button}', 4, back_button_pos_y + 3, 1)
            if self.selector_pos_y == 0:
                self.oled.rect(0, back_button_pos_y, text_width, 12, 1)
        elif self.selected_measurement is not None:
            # Display detailed measurement info
            y = 15
            self.oled.text("Measurement:", 0, y, 1)
            y += 12
            display_order = ['Mean HR', 'PPI (ms)', 'RMSSD', 'SDNN']
            for key in display_order:
                value = self.selected_measurement.get(key, 0)
                self.oled.text(f"{key}: {value:.0f}", 0, y, 1)
                y += 10

        else:
            if len(self.HRV_history) > self.max_visible_items:
                self.draw_scroll_indicators(len(self.HRV_history))

            # Display history items
            visible_items = min(len(self.HRV_history), self.max_visible_items)
            for i in range(visible_items):
                item_index = self.scroll_offset + i
                if item_index >= len(self.HRV_history):
                    break

                measurement = self.HRV_history[item_index]
                y_pos = i * self.line_height + self.header_height + 5
                display_text = f"Result: {measurement['Mean HR']:.0f} BPM"
                self.oled.text(display_text, 4, y_pos + 3, 1)

                # Highlight 
                if item_index == self.selector_pos_y:
                    text_width = len(display_text) * self.font_width + 8
                    self.oled.rect(0, y_pos, text_width, 12, 1)

            for i, item in enumerate(self.items):
                item_index = len(self.HRV_history) + i
                if item_index - self.scroll_offset >= self.max_visible_items:
                    continue

                y_pos = (item_index - self.scroll_offset) * \
                    self.line_height + self.header_height + 5
                text_width = len(item) * self.font_width + 8

                self.oled.text(f'{item}', 4, y_pos + 3, 1)
                if item_index == self.selector_pos_y:
                    self.oled.rect(0, y_pos, text_width, 12, 1)

        self.oled.show()

    def select_next(self):
        total_items = len(self.HRV_history) + len(self.items)
        if self.selector_pos_y < total_items - 1:
            self.selector_pos_y += 1
            if self.selector_pos_y >= self.scroll_offset + self.max_visible_items:
                self.scroll_offset += 1


class SettingsMenu(BaseMenu):
    def __init__(self, oled, pico_conn, items, rot):
        super().__init__(oled, pico_conn, items)
        self.rot = rot
        self.wlan_signal = "Disconnected"
        self.current_submenu = None
        self.max_visible_items = 4
        self.header_height = 15
        self.last_signal_check = 0
        self.signal_check_interval = 5000
        self.brightness = 255  # Default brightness
        self.brightness_step = 51  # 8 steps

    async def handle_input(self):
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if self.current_submenu == "wifi":
                    if data == 0:
                        self.current_submenu = None
                elif self.current_submenu == "brightness":
                    if data == 1:
                        self.brightness = min(
                            255, self.brightness + self.brightness_step)
                        self.oled.contrast(self.brightness)
                    elif data == -1:
                        self.brightness = max(
                            0, self.brightness - self.brightness_step)
                        self.oled.contrast(self.brightness)
                    elif data == 0:
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
                        elif selected_item == "Brightness":
                            self.current_submenu = "brightness"
                        elif selected_item == "Back":
                            self.selector_pos_y = 0
                            return "MAIN"

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
        elif self.current_submenu == "brightness":
            self.brightness_submenu()
        else:
            self.settings_main()
        self.oled.show()


    def settings_main(self):
        self.oled.fill_rect(0, 0, 64, 10, 1)
        self.oled.text("SETTINGS", 0, 1, 0)
        self.draw_scroll_indicators()
        self.draw_wifi_status()
        self.draw_signal_strength()

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
            self.oled.fill_rect(0, 0, 33, 8, 1)
            self.oled.text("WIFI", 0, 1, 0)
            self.oled.text(f"SSID: {self.pico_conn.ssid}", 0, 10, 1)
            self.oled.text(f"Signal strength:", 0, 20, 1)
            self.oled.text(f"{self.wlan_signal}", 0, 30, 1)
            self.oled.text("Pico's IP:", 0, 40, 1)
            self.oled.text(f"{self.wlan.ifconfig()[0]}", 0, 50, 1)
            self.oled.show()


    def brightness_submenu(self):
        self.oled.fill_rect(0, 0, 80, 10, 1)
        self.oled.text("BRIGHTNESS", 0, 1, 0)

        # Convert brightness (0-255) to level (0-8)
        level = self.brightness // 32 + 1

        # Draw brightness bar
        bar_width = 100
        current_width = int((self.brightness / 255) * bar_width)
        self.oled.rect(10, 30, bar_width, 10, 1)
        self.oled.fill_rect(10, 30, current_width, 10, 1)

        self.oled.text(f"Level: {level}/8", 10, 45, 1)
        self.oled.text("Press to exit", 10, 55, 1)


class KubiosMenu(BaseMenu):
    def __init__(self, oled, pico_conn, rot):
        super().__init__(oled, pico_conn)
        self.rot = rot
        self.header_height = 15
        self.measuring = False
        self.error_state = False
        self.collection_time = 30000  # 30 sec
        self.start_time = 0
        self.ppi_measurement_array = []
        self.awaiting_response = False
        self.selector_pos_y = 0
        self.scroll_offset = 0
        self.show_results = False
        self.start_menu_items = ["Measure", "Back"]
        self.results_menu_items = ["Measure Again", "To Main Menu"]
        self.current_menu = self.start_menu_items
        self.parameters = [
            ('Mean HR', 'mean_hr_bpm', '{:0.0f} BPM'),
            ('Readiness', 'readiness', '{:0.0f}%'),
            ('SNS Index', 'sns_index', '{:0.2f}'),
            ('PNS Index', 'pns_index', '{:0.2f}'),
            ('Phys. Age', 'physiological_age', '{:0.0f}y'),
            ('Stress Idx', 'stress_index', '{:0.0f}')
        ]
        self.max_visible_items = 3
        self.line_height = 16
        self.HR = Detect_peaks()

    def reset_state(self):
        # Reset all kubios menu states to initial values
        self.measuring = False
        self.error_state = False
        self.awaiting_response = False
        self.selector_pos_y = 0
        self.scroll_offset = 0
        self.show_results = False
        self.pico_conn.latest_kubios_response = None
        self.ppi_measurement_array = []
        if self.HR:
            self.HR.reset()

    def select_next(self):
        if self.show_results:
            if self.selector_pos_y < len(self.results_menu_items) - 1:
                self.selector_pos_y += 1
        elif not self.pico_conn.latest_kubios_response:
            if self.selector_pos_y < len(self.start_menu_items) - 1:
                self.selector_pos_y += 1
        else:
            if self.selector_pos_y < len(self.parameters) - 1:
                self.selector_pos_y += 1
                if self.selector_pos_y >= self.scroll_offset + self.max_visible_items:
                    self.scroll_offset += 1

    def select_previous(self):
        if self.show_results:
            if self.selector_pos_y > 0:
                self.selector_pos_y -= 1
        elif not self.pico_conn.latest_kubios_response:
            if self.selector_pos_y > 0:
                self.selector_pos_y -= 1
        else:
            if self.selector_pos_y > 0:
                self.selector_pos_y -= 1
                if self.selector_pos_y < self.scroll_offset:
                    self.scroll_offset -= 1

    async def handle_input(self):
        while True:
            if self.rot.fifo.has_data():
                data = self.rot.get_last_input()
                if data == 0:
                    if self.error_state:
                        self.error_state = False
                        return "MAIN"
                    
                    if not self.measuring and not self.awaiting_response:
                        if not self.pico_conn.latest_kubios_response:
                            # Handle start menu selection
                            selected = self.start_menu_items[self.selector_pos_y]
                            if selected == "Measure":
                                await self.collect_and_send_data()
                            else:  
                                return "MAIN"
                        elif not self.show_results:
                            self.show_results = True
                            self.selector_pos_y = 0
                        else:
                            # Handle results menu selection
                            selected = self.results_menu_items[self.selector_pos_y]
                            if selected == "Measure Again":
                                self.reset_state()
                            else:
                                self.reset_state()
                                return "MAIN"
                            
                elif not self.measuring and not self.awaiting_response:
                    if data == 1:
                        self.select_next()
                    elif data == -1:
                        self.select_previous()

            if self.measuring:
                current_time = ticks_ms()
                if ticks_diff(current_time, self.start_time) > self.collection_time:
                    self.measuring = False
                    await self.send_to_kubios()
                if self.rot.fifo.has_data():
                    self.rot.get_last_input()

            self.display()
            await uasyncio.sleep_ms(50)

    def display(self):
        if self.wlan.isconnected():
            self.oled.fill(0)
            self.oled.fill_rect(0, 0, 48, 10, 1)
            self.oled.text("KUBIOS", 0, 1, 0)
            self.draw_wifi_status()
            self.draw_signal_strength()

            if not self.measuring and not self.awaiting_response:
                if not self.pico_conn.latest_kubios_response:
                    self.display_menu(self.start_menu_items)
                elif self.show_results:
                    self.display_menu(self.results_menu_items)
                else:
                    self.display_results()
        else:
            self.oled.fill(0)
            self.error_state = True
            self.oled.fill_rect(0, 0, 48, 10, 1)
            self.oled.text("KUBIOS", 0, 1, 0)
            self.draw_wifi_status()
            self.draw_signal_strength()
            self.oled.text("Connect to WIFI", 0, 20, 1)
            self.oled.text("first", 0, 32, 1)
            self.oled.text("Press to return", 0, 50, 1)

        self.oled.show()

    def display_menu(self, items=None):
        menu_start_y = 25
        for i, item in enumerate(items):
            self.oled.text(item, 4, menu_start_y + (i * 15), 1)
            if i == self.selector_pos_y:
                text_width = len(item) * 8 + 8
                self.oled.rect(0, menu_start_y + (i * 15) -
                               2, text_width, 12, 1)

    def display_results(self):
        if not self.pico_conn.latest_kubios_response:
            return

        analysis = self.pico_conn.latest_kubios_response['data']['analysis']
        self.draw_scroll_indicators(6)

        for i in range(self.max_visible_items):
            param_idx = self.scroll_offset + i
            if param_idx >= len(self.parameters):
                break

            label, key, format_str = self.parameters[param_idx]
            y = self.header_height + (i * self.line_height) + 6

            self.oled.text(f"{label}:", 0, y, 1)
            value = analysis.get(key)
            if value is not None:
                formatted_value = format_str.format(value)
                x_pos = len(label) * 8 + 10
                self.oled.text(formatted_value, x_pos, y, 1)

    async def collect_and_send_data(self):
        if not self.pico_conn.mqtt_client:
            self.disable_rotary()
            self.oled.fill(0)
            self.oled.text("Connecting to", 0, 20, 1)
            self.oled.text("MQTT...", 0, 32, 1)
            self.oled.show()
            await self.pico_conn.connect_mqtt()
            self.enable_rotary()
            if not self.pico_conn.mqtt_client:
                self.oled.fill(0)
                self.oled.text("MQTT connection", 0, 20, 1)
                self.oled.text("failed!!!", 0, 32, 1)
                self.oled.show()
                await uasyncio.sleep(5)
                return

        self.measuring = True
        self.start_time = ticks_ms()
        self.ppi_measurement_array.clear()
        

        while ticks_diff(ticks_ms(), self.start_time) < self.collection_time:
            current_time = ticks_ms()
            elapsed = ticks_diff(current_time, self.start_time)
            remaining = max(0, (self.collection_time - elapsed) // 1000)
            self.HR.run(remaining)
            await uasyncio.sleep_ms(100)

        self.ppi_measurement_array = self.HR.get_ibi()
        
        self.HR.reset()
    

    async def send_to_kubios(self):
        if not self.ppi_measurement_array:
                return

        kubios_request = {
            "id": 123,
            "type": "RRI",
            "data": self.ppi_measurement_array,
            "analysis": {"type": "readiness"}
        }

        try:
            self.awaiting_response = True
            json_message = json.dumps(kubios_request)
            await self.pico_conn.mqtt_publish(json_message, self.pico_conn.kubios_request_topic)

            # Wait for Kubios response with timeout
            timeout = 6
            start_time = ticks_ms()

            while self.awaiting_response:
                if ticks_diff(ticks_ms(), start_time) > timeout * 1000:
                    self.oled.fill(0)
                    self.oled.text("No response from", 0, 20, 1)
                    self.oled.text("Kubios!", 0, 32, 1)
                    self.oled.show()
                    self.awaiting_response = False
                    await uasyncio.sleep(5)
                    break

                # Check for new messages
                if self.pico_conn.mqtt_client:
                    self.pico_conn.mqtt_client.check_msg()

                    # If we got a response, pico_conn.latest_kubios_response will be updated
                    if self.pico_conn.latest_kubios_response:
                        self.awaiting_response = False
                        break

                # Clear rotary inputs during waiting
                if self.rot.fifo.has_data():
                    self.rot.get_last_input()

                await uasyncio.sleep_ms(100)

        except Exception as e:
            print(f"Error sending to Kubios: {e}")
            self.oled.fill(0)
            self.oled.text("Error sending to", 0, 20, 1)
            self.oled.text(f"Kubios! {e}", 0, 32, 1)
            await uasyncio.sleep(5)
        finally:
            self.awaiting_response = False
