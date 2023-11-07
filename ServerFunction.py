import tkinter
from tkinter import messagebox
from tkinter import ttk
import sqlite3


databaseDirectory = 'directory.db'

def DiscoverHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()
        print("Successfully connect to the database\n")

        headersTuple = ("Hostname","file_md5","file_name")

        queryString = "SELECT A.username, F.file_md5, F.file_name FROM peers_account AS A, peers AS P, files AS F, files_peers AS R WHERE A.session_id=P.session_id AND P.session_id=R.session_id AND F.file_md5=R.file_md5 AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        for row in outputRows:
            print(row)

        DisplayQueryResult(headersTuple,outputRows,"Discovery Hostname")
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

        queryString = "SELECT A.username, P.state_on_off FROM peers_account AS A, peers AS P WHERE A.session_id = P.session_id AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        for row in outputRows:
            print(row)

        DisplayQueryResult(headersTuple,outputRows,"Ping Hostname")
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
        for row in outputRows:
            print(row)

        DisplayQueryResult(headersTuple,outputRows,"Show all user")
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()
            print("The SQLite connection is closed\n")

def DisplayQueryResult(headersTuple, outputRows, functionName):
    resultWindow = tkinter.Tk()
    resultWindow.title(functionName)

    tree = ttk.Treeview(resultWindow,columns=headersTuple,show='headings')
    for header in headersTuple:
        tree.heading(header,text=header.replace("_"," "))
    for row in outputRows:
        tree.insert('',tkinter.END, values=row)
    tree.grid(row=0,column=0,sticky='nsew')
    scrollbar = tkinter.Scrollbar(resultWindow,orient=tkinter.VERTICAL,command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0,column=1,sticky='ns')
    resultWindow.mainloop()
    
