print("Hello, ESP32-S3!")

from machine import Pin, I2C
import machine
import ssd1306
import dht
import time

DHT_PIN = 4  # DHT11 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Initialize DHT11 sensor
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

# Initialize OLED display
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

pressed = False  # Button state

# Define 8x8 bitmap
TEMP_ICON = [
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00011000,  #    ██    
    0b00111100,  #   ████   
    0b00111100,  #   ████   
    0b00011000   #    ██    
]

HUMIDITY_ICON = [
    0b00001000,  #     █    
    0b00011000,  #    ██    
    0b00111000,  #   ███    
    0b01111000,  #  ████    
    0b01111000,  #  ████    
    0b00111000,  #   ███    
    0b00011000,  #    ██    
    0b00000000   #          
]

def draw_icon(oled, x, y, icon):
    """Draws an 8x8 icon on the OLED at (x, y)."""
    for row in range(8):
        for col in range(8):
            pixel_on = (icon[row] >> (7 - col)) & 1
            oled.pixel(x + col, y + row, pixel_on)

def button_pressed(pin):
    global pressed
    time.sleep_ms(200)  # Software debounce
    
    if button.value() == 0:  # Confirm button is still pressed
        pressed = not pressed  # Toggle state
        
        if pressed:
            oled.poweroff()
        else:
            oled.poweron()
            oled.init_display()  # Reinitialize the display

# Attach the interrupt to the button's falling edge
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Main loop
while True:
    if not pressed:  # Update only if the display is on
        try:
            dht_sensor.measure()
            time.sleep(0.2)
            temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
            print(temp, humidity)
            
            oled.fill(0)
            
            # Draw temperature icon and text
            draw_icon(oled, 0, 0, TEMP_ICON)
            oled.text("{} C".format(temp), 10, 0)
            
            # Draw humidity icon and text
            draw_icon(oled, 0, 16, HUMIDITY_ICON)
            oled.text("{}%".format(humidity), 10, 16)
            
            oled.show()

        except Exception as e:
            print("Error reading DHT11 sensor:", e)
    
    time.sleep(1)  # Update every second
