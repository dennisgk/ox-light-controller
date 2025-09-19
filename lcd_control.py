import threading
import time

EARG_COLOR = "COLOR"
EARG_STROBE = "STROBE"
EARG_SECTION_WIPE = "SECTION_WIPE"
EARG_THEATER_CHASE = "THEATER_CHASE"
EARG_COLOR_WIPE = "COLOR_WIPE"
EARG_CHRISTMAS = "CHRISTMAS"
EARG_POLICE = "POLICE"

IARG_RESERVED = "RESERVED"
IARG_STOP = "STOP"
IARG_STROBE_RUN = "STROBE_RUN"
IARG_SECTION_WIPE_RUN = "SECTION_WIPE_RUN"
IARG_THEATER_CHASE_RUN = "THEATER_CHASE_RUN"
IARG_COLOR_WIPE_RUN = "COLOR_WIPE_RUN"
IARG_CHRISTMAS_RUN = "CHRISTMAS_RUN"
IARG_POLICE_RUN = "POLICE_RUN"

import os
import traceback

if os.name == "nt":
    class LcdControl():
        def __init__(self):
            self.action = IARG_RESERVED
            self.adata = None

        def dispatch(self, action, data = None):
            print(action)
            print(data)

        def stop():
            pass
else:
    from rpi_ws281x import PixelStrip, Color

    class LcdControl():
        def __init__(self):
            # LED strip configuration:
            LED_COUNT = 387        # Number of LED pixels.
            # LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
            LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
            LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
            LED_DMA = 10          # DMA channel to use for generating signal (try 10)
            LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
            LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
            LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

            # Create NeoPixel object with appropriate configuration.
            self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
            # Intialize the library (must be called once before other functions).
            self.strip.begin()

            self.action = IARG_RESERVED
            self.adata = None
            self.bcall = None

            self.thread = threading.Thread(target=self.thr)
            self.thread.start()

        def thr(self):
            while self.action != IARG_STOP:
                try:
                    if self.bcall is not None:
                        scall = self.bcall
                        self.bcall = None
                        scall()

                    if self.action == IARG_RESERVED:
                        continue

                    if self.action == EARG_COLOR:
                        if self.adata is not True:
                            self.strip_fill(Color(*self.adata))
                            self.adata = True

                        continue

                    if self.action == EARG_STROBE:
                        self.adata = [0, *self.adata]
                        self.action = IARG_STROBE_RUN

                    if self.action == IARG_STROBE_RUN:
                        col = Color(*self.adata[2]) if self.adata[0] % 2 == 0 else Color(*self.adata[1])

                        self.strip_fill(col)
                        time.sleep(0.04)

                        self.adata[0] = self.adata[0] + 1
                        continue

                    if self.action == EARG_SECTION_WIPE:
                        self.adata = [0, *self.adata]
                        self.action = IARG_SECTION_WIPE_RUN

                    if self.action == IARG_SECTION_WIPE_RUN:
                        self.strip_section_wipe(Color(*self.adata[1]), self.adata[0], 5)
                        time.sleep(0.050)

                        self.adata[0] = self.adata[0] + 1
                        continue

                    if self.action == EARG_THEATER_CHASE:
                        self.adata = 0
                        self.action = IARG_THEATER_CHASE_RUN
                    
                    if self.action == IARG_THEATER_CHASE_RUN:
                        self.strip_theater_chase_rainbow(self.adata)
                        
                        time.sleep(0.200)

                        self.adata = self.adata + 1
                        continue

                    if self.action == EARG_COLOR_WIPE:
                        self.adata = [(0, 0), *self.adata]
                        self.action = IARG_COLOR_WIPE_RUN

                    if self.action == IARG_COLOR_WIPE_RUN:
                        skip = 1

                        if self.adata[0][0] == 0:
                            self.color_wipe(Color(*self.adata[1]), self.adata[1], skip)
                            self.adata[0] = (1, 0) if self.adata[0][1] + skip >= self.strip.numPixels() else (0, self.adata[0][1] + skip)
                            time.sleep(0.001)
                        else:
                            self.color_wipe(Color(*self.adata[2]), self.adata[0][1], skip)
                            self.adata[0] = (0, 0) if self.adata[0][1] + skip >= self.strip.numPixels() else (1, self.adata[0][1] + skip)
                            time.sleep(0.001)

                        continue

                    if self.action == EARG_CHRISTMAS:
                        self.adata = [0, *self.adata]
                        self.action = IARG_CHRISTMAS_RUN
                    
                    if self.action == IARG_CHRISTMAS_RUN:
                        skip = 1

                        self.color_wipe(Color(*self.adata[1]), self.adata[0] % self.strip.numPixels(), skip)
                        self.color_wipe(Color(*self.adata[2]), (self.adata[0] + int(self.strip.numPixels() / 2)) % self.strip.numPixels(), skip)
                        self.adata[0] = self.adata[0] + skip
                        time.sleep(0.010)

                        continue
                    
                    if self.action == EARG_POLICE:
                        self.adata = [0, *self.adata]
                        self.action = IARG_POLICE_RUN

                    if self.action == IARG_POLICE_RUN:
                        sec = 5

                        col = None
                        if self.adata[0] % 3 == 0:
                            col = Color(*self.adata[1])
                        elif self.adata[0] % 3 == 1:
                            col = Color(*self.adata[2])
                        else:
                            col = Color(*self.adata[3])
                        
                        self.strip_section_wipe(col, self.adata[0], sec)

                        time.sleep(0.04)

                        self.adata[0] = self.adata[0] + 1
                        continue

                except Exception as e:
                    self.action = IARG_RESERVED
                    self.adata = None

                    print(e)
                    traceback.print_exc()

        """START INTERNAL FUNCTIONS"""
        
        def strip_fill(self, col):
            for x in range(self.strip.numPixels()):
                self.strip.setPixelColor(x, col)

            self.strip.show()

        def strip_section_wipe(self, color, it, total):
            num_pixels = int(self.strip.numPixels() / total)

            for x in range(self.strip.numPixels()):
                self.strip.setPixelColor(x, Color(0, 0, 0))

            for x in range(num_pixels * (it % total), num_pixels * ((it % total) + 1)):
                self.strip.setPixelColor(x, color)

            self.strip.show()

        def wheel(self, pos):
            """Generate rainbow colors across 0-255 positions."""
            if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

        def strip_theater_chase_rainbow(self, it):
            """Rainbow movie theater light style chaser animation."""
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.wheel((i + it) % 255))
                self.strip.show()
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

        def color_wipe(self, color, start, skip):
            """Wipe color across display a pixel at a time."""
            for x in range(skip):
                if start + x >= self.strip.numPixels():
                    break

                self.strip.setPixelColor(start + x, color)
            self.strip.show()

        """END INTERNAL FUNCTIONS"""

        def dispatch(self, action, data = None):
            print(action)
            print(data)
            caction = self.action
            cdata = self.adata

            def nbcall():
                self.action = action
                self.adata = data

            self.bcall = nbcall

            return caction, cdata

        def stop(self):        
            self.action = "STOP"
            self.thread.join()
