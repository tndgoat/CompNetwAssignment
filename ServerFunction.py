import tkinter
import sqlite3

databaseDirectory = 'directory.db'

def DiscoverHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()
        print("Successfully connect to the database\n")

        queryString = "SELECT A.username, F.file_md5, F.file_name FROM peers_account AS A, peers AS P, files AS F, files_peers AS R WHERE A.session_id=P.session_id AND P.session_id=R.session_id AND F.file_md5=R.file_md5 AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        for row in outputRows:
            print(row)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()
            print("The SQLite connection is closed\n")

def PingHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()
        print("Successfully connect to the database\n")

        queryString = "SELECT A.username, P.state_on_off FROM peers_account AS A, peers AS P WHERE A.session_id = P.session_id AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        for row in outputRows:
            print(row)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()
            print("The SQLite connection is closed\n")

def ShowAllUser():
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()
        print("Successfully connect to the database\n")

        queryString ="SELECT P.session_id, P.ip, P.your_name, P.port, P.state_on_off, F.file_md5, F.file_name, F.download_count FROM peers AS P, files AS F, files_peers AS R WHERE P.session_id=R.session_id AND F.file_md5=R.file_md5"
        cursor.execute(queryString)
        outputRows = cursor.fetchall()
        for row in outputRows:
            print(row)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()
            print("The SQLite connection is closed\n")
