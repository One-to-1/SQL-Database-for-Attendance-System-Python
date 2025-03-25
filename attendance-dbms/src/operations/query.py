from .database.connection import DatabaseConnection

def execute_query(query, params=None):
    connection = DatabaseConnection()
    connection.connect()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.disconnect()

def fetch_results(cursor):
    return cursor.fetchall()