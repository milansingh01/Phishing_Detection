import sqlite3
import time

conn = sqlite3.connect('alertshield.db')
c = conn.cursor()
c.execute("SELECT count(*) FROM email_cases")
print("Total rows:", c.fetchone()[0])
conn.close()
