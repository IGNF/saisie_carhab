from pyspatialite import dbapi2 as db
import os.path

path = 'db/empty.sqlite'

if os.path.exists(path):
    os.remove(path)

conn = db.connect(path) # Database creation

cur = conn.cursor() # Creating a Cursor

cur.execute("PRAGMA synchronous = OFF") # To run faster DB changes execution, less secure...

# Initializing Spatial MetaData : this will automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
sql = 'SELECT InitSpatialMetadata()'
cur.execute(sql)

# Execute DB populating script
sql_db_script = open('db/db_script.sql')
cur.executescript(sql_db_script.read())

conn.commit()
conn.close()