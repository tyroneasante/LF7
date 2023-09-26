import Adafruit_DHT
import time

# Sensor-Typ und Pin festlegen
sensor = Adafruit_DHT.DHT11
pin = 26

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            print('Temperatur: ' + str(temperature) + "*C")
            #print('Luftfeuchtigkeit: ', humidity)
            print("Luftfeuchtigkeit: " + str(humidity)  +  "%")
        else:
            print('Fehler beim Auslesen des Sensors. ueberprfe die Verkabelung.')

        time.sleep(1)

except KeyboardInterrupt:
    print('\nProgramm wurde beendet.')
