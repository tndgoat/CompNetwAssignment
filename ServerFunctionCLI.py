import sqlite3
from prettytable import PrettyTable



databaseDirectory = 'directory.db'

def DiscoverHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()
        print("Successfully connect to the database\n")

        headersTuple = ("Hostname","file_md5","file_name")

        if hostname == "":
            print("Hostname empty","Please enter a hostname")
            return

        queryString = "SELECT A.username, F.file_md5, F.file_name FROM peers_account AS A, peers AS P, files AS F, files_peers AS R WHERE A.session_id=P.session_id AND P.session_id=R.session_id AND F.file_md5=R.file_md5 AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        
        PrintTable(headersTuple,outputRows)
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

        headersTuple = ("Hostname","online_state")

        if hostname == "":
            print("Hostname empty","Please enter a hostname")
            return

        queryString = "SELECT A.username, P.state_on_off FROM peers_account AS A, peers AS P WHERE A.session_id = P.session_id AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        
        PrintTable(headersTuple,outputRows)
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

        headersTuple = ("session_id","ip","client_name","port","online_state","file_md5","file_name","download_count")

        queryString ="SELECT P.session_id, P.ip, P.your_name, P.port, P.state_on_off, F.file_md5, F.file_name, F.download_count FROM peers AS P, files AS F, files_peers AS R WHERE P.session_id=R.session_id AND F.file_md5=R.file_md5"
        cursor.execute(queryString)
        outputRows = cursor.fetchall()
        
        PrintTable(headersTuple,outputRows)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()
            print("The SQLite connection is closed\n")

def PrintTable(headersTuple,outputRows):
    table = PrettyTable()
    table.field_names = headersTuple
    for row in outputRows:
        table.add_row(row)
    print(table)
