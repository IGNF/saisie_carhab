# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from db_manager import *
import os
import sys

db_version = sys.argv[1]
folder = os.path.dirname(__file__)
db = 'empty.sqlite'
init_script = 'db/init_db.sql'
trigger_script = 'db/triggers.sql'

if os.path.exists(os.path.join(folder, db)):
    os.remove(os.path.join(folder, db))

db = Db(os.path.join(folder, db))

db.executeScript(os.path.join(folder, init_script))
db.set_version(db_version)
db.createTables()
db.executeScript(os.path.join(folder, trigger_script))

db.commit()
db.close()
