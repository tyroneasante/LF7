import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import sqlite3
import matplotlib.pyplot as plt

# data visualization labels
plt.xlabel('Zeitpunkt')
plt.ylabel('Temperatur (C)')
plt.title('Temperaturverlauf')

# connect to database
con = sqlite3.connect("hydro_alert.db")
cur = con.cursor()

# display pins
LCD_RS = 4
LCD_E  = 17
LCD_DATA4 = 12
LCD_DATA5 = 22
LCD_DATA6 = 23
LCD_DATA7 = 16

LCD_WIDTH = 16         # Zeichen je Zeile
LCD_LINE_1 = 0x80     # Adresse der ersten Display Zeile
LCD_LINE_2 = 0xC0     # Adresse der zweiten Display Zeile
LCD_CHR = GPIO.HIGH
LCD_CMD = GPIO.LOW
E_PULSE = 0.0005
E_DELAY = 0.0005

# distance pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# buzzer pin
GPIO_BUZZER = 21

#temp sensor pins
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 26
#GPIO Modus (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#setup display pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_DATA4, GPIO.OUT)
GPIO.setup(LCD_DATA5, GPIO.OUT)
GPIO.setup(LCD_DATA6, GPIO.OUT)
GPIO.setup(LCD_DATA7, GPIO.OUT)

#setup distance pins
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#setup buzzer pin
GPIO.setup(GPIO_BUZZER, GPIO.OUT)

def lcd_send_byte(bits, mode):
    # Pins auf LOW setzen
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits & 0x10 == 0x10:
      GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits & 0x20 == 0x20:
      GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits & 0x40 == 0x40:
      GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits & 0x80 == 0x80:
      GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits&0x01==0x01:
      GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits&0x02==0x02:
      GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits&0x04==0x04:
      GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits&0x08==0x08:
      GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)

def display_init():
    lcd_send_byte(0x33, LCD_CMD)
    lcd_send_byte(0x32, LCD_CMD)
    lcd_send_byte(0x28, LCD_CMD)
    lcd_send_byte(0x0C, LCD_CMD)
    lcd_send_byte(0x06, LCD_CMD)
    lcd_send_byte(0x01, LCD_CMD)

def lcd_message(message):
    message = message.ljust(LCD_WIDTH," ")
    for i in range(LCD_WIDTH):
        lcd_send_byte(ord(message[i]),LCD_CHR)
def measure_distance():
    # setze Trigger auf HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # setze Trigger nach 0.01ms aus LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartZeit = time.time()
    StopZeit = time.time()

    # speichere Startzeit
    while GPIO.input(GPIO_ECHO) == 0:
        StartZeit = time.time()

    # speichere Ankunftszeit
    while GPIO.input(GPIO_ECHO) == 1:
        StopZeit = time.time()

    # Zeit Differenz zwischen Start und Ankunft
    TimeElapsed = StopZeit - StartZeit
    # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
    # und durch 2 teilen, da hin und zurueck
    distanz = (TimeElapsed * 34300) / 2

    return distanz

if __name__ == '__main__':
    display_init()
    try:
        while True:
            # get data from temperature/humidty sensor only if new data is available
            try:
                humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            except:
                print("no new data")
                temperature = None
                humidity = None
            # get data from ultra sonic sensor
            distance = measure_distance()
            print ("Abstand zum Wasser: %.1f cm" % distance)
            if distance < 5:
                lcd_send_byte(LCD_LINE_1, LCD_CMD)
                lcd_message("Gefahr!!!")
                lcd_send_byte(LCD_LINE_2, LCD_CMD)
                lcd_message("Hochwasser!!!")

                GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(GPIO_BUZZER, GPIO.LOW)
                time.sleep(0.2)
            elif humidity is not None and temperature is not None:
                print('Temperatur: ' + str(temperature) + "*C")
                print("Luftfeuchtigkeit: " + str(humidity)  +  "%")
                lcd_send_byte(LCD_LINE_1, LCD_CMD)
                lcd_message("Temperatur: " + str(temperature) + "C")
                lcd_send_byte(LCD_LINE_2, LCD_CMD)
                lcd_message("Humidity: " + str(humidity) + "%")

            # insert into database
            data = [
                (int(time.time()), temperature, humidity, distance,)
            ]
            cur.executemany("INSERT INTO weather_data VALUES(?, ?, ?, ?)", data)
            con.commit()

            time.sleep(1)

        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        display_init()
        GPIO.cleanup()
        con.close()
