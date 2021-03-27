# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


# Custom error for us to throw
class DatabaseError(BaseException):
    pass


def select(connectionString, sql, parameters):
    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, parameters)
        rows = cursor.fetchall()

        # Clean-up and return
        cursor.close()
        connection.close()
        return rows

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError


# Executes provided INSERT statement, and returns result of the operation
#def insert_returning(connectionString, sql, parameters):
#    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
#        connection = psycopg2.connect(connectionString, connect_timeout=1)
#        cursor = connection.cursor()

        # Execute the query, note the rows
#        cursor.execute(sql, (parameters['Name'],))
#        returnValue = cursor.fetchone()[0]

        # Clean-up and return
#        connection.commit()
#        cursor.close()
#        return returnValue

 #   except psycopg2.OperationalError as err:
 #       sys.stderr.write(f'An error occurred connecting to the database: {err}')
 #       raise DatabaseError

 #   except psycopg2.DatabaseError as err:
 #       sys.stderr.write(f'A general database error occurred: {err}')
 #       raise DatabaseError


#def delete(connectionString, sql, parameters):
#    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
#        connection = psycopg2.connect(connectionString, connect_timeout=1)
#        cursor = connection.cursor()

        # Execute the query, note the rows
#        cursor.execute(sql, (parameters['id'],))

#        connection.commit()
        # check if the study exists
        #if cursor.rowcount:
        #    print("Study deleted successfully")
        #else:
        #    print("Study does not exist")

        # Clean-up and return
#        cursor.close()
#        return cursor.rowcount


#    except psycopg2.OperationalError as err:
#        sys.stderr.write(f'An error occurred connecting to the database: {err}')
#        raise DatabaseError

#    except psycopg2.DatabaseError as err:
#        sys.stderr.write(f'A general database error occurred: {err}')
#        raise DatabaseError

#    except psycopg2.Error as err:
#        sys.stderr.write(f'An error occurred: {type(err)} {err}')
#        raise DatabaseError


#def update(connectionString, sql, parameters):
#    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
#        connection = psycopg2.connect(connectionString, connect_timeout=1)
#        cursor = connection.cursor()

        # Execute the query, note the rows
#        cursor.execute(sql, (parameters['name'], parameters['id'],))

#        connection.commit()
        # check if the study exists
#        if cursor.rowcount:
#            print("Study renamed successfully")
#        else:
#            print("Study does not exist")

        # Clean-up and return
#        cursor.close()

#    except psycopg2.OperationalError as err:
#        sys.stderr.write(f'An error occurred connecting to the database: {err}')
#        raise DatabaseError

#    except psycopg2.DatabaseError as err:
#        sys.stderr.write(f'A general database error occurred: {err}')
#        raise DatabaseError

#    except psycopg2.Error as err:
#        sys.stderr.write(f'An error occurred: {type(err)} {err}')
#        raise DatabaseError


def operation(flag, connectionString, sql, parameters):
    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()
        returnValue = ""
        if (flag == 1):  # insert
            cursor.execute(sql, (parameters['Name'],))
            returnValue = str(cursor.fetchone()[0])

        if (flag == 2):  # remove
            cursor.execute(sql, (parameters['id'],))
            #if cursor.rowcount:
            #    returnValue = "Study deleted successfully"
            #else:
            #    returnValue = "Study does not exist"
            returnValue = cursor.rowcount

        if (flag == 3):  # update
            cursor.execute(sql, (parameters['name'], parameters['id'],))

            #if cursor.rowcount:
            #    returnValue = "Study renamed successfully"
            #else:
            #    returnValue = "Study does not exist"
            returnValue = cursor.rowcount

        connection.commit()
        cursor.close()
        return returnValue

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError

    except psycopg2.Error as err:
        sys.stderr.write(f'An error occurred: {type(err)} {err}')
        raise DatabaseError
