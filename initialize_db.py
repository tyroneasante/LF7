import sqlite3
con = sqlite3.connect("hydro_alert.db")
cur = con.cursor()
cur.execute("CREATE TABLE weather_data(timestamp int, temperature int, humidity int, water_level int)")
