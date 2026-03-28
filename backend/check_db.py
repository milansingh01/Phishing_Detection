import sqlite3

conn = sqlite3.connect('alertshield.db')
c = conn.cursor()
c.execute("SELECT sender, subject FROM email_cases")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
