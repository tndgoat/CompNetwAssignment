import tkinter
import ServerFunction

def ServerMainMenu():
    menu = tkinter.Tk()
    menu.geometry('280x150')
    menu.title("Server management")
    tkinter.Label(menu, text="Host name").grid(row=0, column=0)
    hostname = tkinter.Entry(menu)
    discoverHostname = tkinter.Button(menu,text="Discover hostname",
                                    command=lambda: ServerFunction.DiscoverHostname(hostname.get()))
    pingHostName = tkinter.Button(menu,text="Ping hostname",
                                command=lambda: ServerFunction.PingHostname(hostname.get()))
    showAllUser = tkinter.Button(menu,text="Show all users",
                                command=lambda: ServerFunction.ShowAllUser())

    hostname.grid(row=0,column=1)
    discoverHostname.grid(row=1,column=0)
    pingHostName.grid(row=1,column=1)
    showAllUser.grid(row=3,column=0)

    menu.mainloop()