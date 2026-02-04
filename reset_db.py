import os
import time

db_path = "db.sqlite3"

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Deleted {db_path}")
    except Exception as e:
        print(f"Could not delete {db_path}: {e}")
        print("Please close any programs using the database and try again.")
else:
    print(f"{db_path} does not exist")
