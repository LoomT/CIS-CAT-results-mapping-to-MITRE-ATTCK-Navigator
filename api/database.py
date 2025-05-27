import sqlite3

from flask import Flask, g
from .sql_querries import (ADD_FILE, GET_FILE_BY_ID, GET_ALL_FILES,
                           ADD_TAG_TO_FILE)


class FileMetadata:
    """Class representing file metadata.\n
    host_name, time and result are extracted from file_name;
    id is generated, ip_address is the IP address of the client
    and tags are added manually"""

    def __init__(self,
                 id: str,
                 ip_address: str,
                 host_name: str,
                 file_name: str,
                 time_created: str,
                 result: str,
                 tags: list[str]
                 ):

        self.id = id
        self.ip_address = ip_address
        self.host_name = host_name
        self.file_name = file_name
        self.time_created = time_created
        self.result = result
        self.tags = tags

    def __repr__(self):
        return (f"FileMetadata(id={self.id}, ip_address={self.ip_address}, "
                f"host_name={self.host_name}, file_name={self.file_name}, "
                f"time_created={self.time_created}, result={self.result}, "
                f"tags={self.tags})")


# TODO: Move path of db to config
DATABASE = 'database.db'    # Path to database
# Cannot use in memory, as would also need to delete uploaded files on exit


# Setup and database management

def get_db():
    """Returns a database connection from g or creates a new one."""

    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db


def close_db(e=None):
    """Closes the database connection if it exists."""

    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app: Flask) -> None:
    """Initializes the database by creating tables from schema.sql
    if they don not exist. Also adds a default tag to tags table."""

    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            try:
                db.executescript(f.read().decode('utf8'))
            except sqlite3.Error as e:
                print(f"Error while executing schema.sql: {e}")
                return
        db.commit()
    app.teardown_appcontext(close_db)


# Data handling functions

def db_save_file(fmd: FileMetadata) -> None:
    """Saves a file metadata object (without tags) to the database."""
    # TODO: Add tags handling, right now it only adds a default tag

    db = get_db()
    cursor = db.cursor()
    print("Saving file to database")
    print(fmd)
    try:
        cursor.execute(ADD_FILE, (fmd.id,
                                  fmd.ip_address,
                                  fmd.host_name,
                                  fmd.file_name,
                                  fmd.time_created,
                                  fmd.result))
        cursor.execute(ADD_TAG_TO_FILE, (fmd.id, 1))
    except sqlite3.Error as e:
        print(f"Error while executing ADD_FILE: {e}")
        return
    db.commit()


def db_get_file_by_id(file_id: str) -> FileMetadata | None:
    """Returns a FileMetadata object by its ID from the database.
    Returns None if the file is not found."""

    db = get_db()
    cursor = db.cursor()
    cursor.execute(GET_FILE_BY_ID, (file_id,))
    rows = cursor.fetchall()

    if rows:
        fmd = FileMetadata(id=rows[0][0],
                           ip_address=rows[0][1],
                           host_name=rows[0][2],
                           file_name=rows[0][3],
                           time_created=rows[0][4],
                           result=rows[0][5],
                           tags=[])
        for row in rows:
            if row[6] and row[7]:
                fmd.tags.append({row[6]: row[7]})
        return fmd
    return None


def db_get_all_files() -> list[FileMetadata]:
    """Returns all files in the database."""

    db = get_db()
    cursor = db.cursor()
    cursor.execute(GET_ALL_FILES)
    rows = cursor.fetchall()
    file_metadata_list = []
    for row in rows:
        # If last ID is not the same or list is empty,
        if ((len(file_metadata_list) == 0) or
                (file_metadata_list[-1].id != row[0])):

            file_metadata_list.append(
                FileMetadata(id=row[0],
                             ip_address=row[1],
                             host_name=row[2],
                             file_name=row[3],
                             time_created=row[4],
                             result=row[5],
                             tags=[{row[6]: row[7]}]
                             if row[6] and row[7] else []))
        else:
            # If last ID is the same, append tag to last file metadata
            if row[6] and row[7]:
                file_metadata_list[-1].tags.append({row[6]: row[7]})
    return file_metadata_list
