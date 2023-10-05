import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import time

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect('hydro_alert.db')
cursor = conn.cursor()

current_time = int(time.time())
yesterday = current_time - 84600 

# SQL-Abfrage zum Abrufen der initialen Daten aus der Datenbank
cursor.execute('SELECT timestamp, water_level FROM weather_data ORDER BY timestamp DESC LIMIT 10')

# Daten aus der Abfrage abrufen
data = cursor.fetchall()
data.reverse()

# Die Daten in separate Listen für x und y aufteilen
x = [datetime.datetime.utcfromtimestamp(row[0]).strftime('%H:%M:%S') for row in data]
y = [row[1] for row in data]

# Plot initialisieren
fig, ax = plt.subplots(figsize=(16, 12))
line, = ax.plot(x, y, label='Wasserstand nach Uhrzeit')
ax.set_xlabel('Uhrzeit')
ax.set_ylabel('Wasserstand')
ax.set_title('Wasserstand')
ax.legend()
plt.style.use('grayscale')


# Funktion zum Aktualisieren des Plots
def update(frame):
    cursor.execute('SELECT timestamp, water_level FROM weather_data ORDER BY timestamp DESC LIMIT 10')
    new_data = cursor.fetchall()
    new_data.reverse()
    
    
    new_x = [datetime.datetime.utcfromtimestamp(row[0]).strftime('%H:%M:%S') for row in new_data]
    new_y = [row[1] for row in new_data]
    print(len(new_x))
    ax.set_xticks(new_x)
    ax.set_xlim(new_x[0], new_x[9])
    ax.set_ylim(0, 1200)
    line.set_data(new_x, new_y)
    
    plt.pause(0.01)
    return line,

# Animationsobjekt erstellen
ani = FuncAnimation(fig, update, blit=True, interval=1000)

def switch_view(event):
    print(event)
    print(event.key) 
fig.canvas.mpl_connect('key_press_event', switch_view)
# Plot anzeigen
plt.show()

# Verbindung zur Datenbank schließen (nachdem die Animation beendet wurde)
conn.close()
