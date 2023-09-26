import RPi.GPIO as GPIO
import time

# Define the GPIO pin number to which the buzzer is connected
BUZZER_PIN = 21

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set up the buzzer pin as an output
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    # Loop to make the buzzer sound like an alarm
    while True:
        # Turn on the buzzer
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        
        # Wait for a short duration (you can adjust this to change the alarm sound)
        time.sleep(0.5)
        
        # Turn off the buzzer
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        
        # Wait for a short duration
        time.sleep(0.5)

except KeyboardInterrupt:
    # Gracefully exit the program on Ctrl+C
    pass

finally:
    # Clean up GPIO settings
    GPIO.cleanup()

