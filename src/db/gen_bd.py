# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from db_manager import *
from config import *
from recorder import *
import os
import sys

db_version = sys.argv[1]
folder = os.path.dirname(__file__)
db = 'empty.sqlite'
init_script = 'init_db.sql'
trigger_script = 'triggers.sql'

if os.path.exists(os.path.join(folder, db)):
    os.remove(os.path.join(folder, db))

db = DbManager(os.path.join(folder, db))

db.executeScript(os.path.join(folder, init_script))
db.set_version(db_version)
db.createTables(Config.DB_STRUCTURE)
db.executeScript(os.path.join(folder, trigger_script))

db.commit()
db.close()
