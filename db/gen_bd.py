from pyspatialite import dbapi2 as db
import os.path

path = 'db/empty.sqlite'

if os.path.exists(path):
    os.remove(path)

conn = db.connect(path) # Database creation

cur = conn.cursor() # Creating a Cursor

# Execute DB populating script
sql_db_script = open('db/db_script.sql')
cur.executescript(sql_db_script.read())

conn.commit()
conn.close()