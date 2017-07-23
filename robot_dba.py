import MySQLdb
import os

PATH = "/home/elmaster/project/datawarehouse_model/"


def create_db(db_target):
    """
    Create database and set privilege for a database
    """
    db_engine = MySQLdb.connect(host="localhost", user="root")
    cur = db_engine.cursor()
    print("Creating database for target: {}...".format(db_target))
    sql = """
    CREATE DATABASE {db};
    CREATE USER {db} IDENTIFIED BY '{db}';
    GRANT ALL PRIVILEGES ON {db}.* TO {db};
    """.format(db=db_target)

    # Create database
    cur.execute(sql)
    db_engine.close()
    print("Done!")


def drop_db(db_target):
    """
    Drop database
    """
    db_engine = MySQLdb.connect(host="localhost", user="root")
    cur = db_engine.cursor()
    print("Dropping {}...".format(db_target))
    sql = """DROP DATABASE {db};""".format(db=db_target)

    # Create database
    cur.execute(sql)
    db_engine.commit()
    db_engine.close()
    print("Done!")


def create_tables(script_path, db_target):
    """
    Execute table creation script
    """
    db_engine = MySQLdb.connect(host="localhost",
                                user=db_target,
                                passwd=db_target,
                                db=db_target)
    print("Creating tables for target: {}...".format(db_target))
    with open(os.path.join(script_path, "script", "create_db.sql")) as f:
        sql = f.read().replace('\n', '')

    cur = db_engine.cursor()
    cur.execute(sql)
    db_engine.close()
    print("Done!")


def reset_db(script_path, db_target):
    """
    Drop and reload database
    """
    print("Reseting database: {}...".format(db_target))
    try:
        drop_db(db_target)
    except:
        pass
    create_db(db_target)
    create_tables(script_path, db_target)


def reset_table(db_target, table):
    """
    Drop and reload table for a given db
    """

    db_engine = MySQLdb.connect(host="localhost",
                                user=db_target,
                                passwd=db_target,
                                db=db_target)
    print("Reseting table: {table} in database: {db_target}...".format(table=table, db_target=db_target))
    sql = """
    use {db_target};
    TRUNCATE {table};
    """.format(db_target=db_target, table=table)
    cur = db_engine.cursor()
    cur.execute(sql)
    db_engine.close()
    print("Done!")
