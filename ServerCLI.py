import cmd, sys
import ServerFunctionCLI

class ServerCLI(cmd.Cmd):
    intro = "Welcome admin, type help or ? to list command.\n"
    prompt = '>>'
    
    def do_discover(selft,hostname):
        if hostname == "":
            print("Hostname parameter is empty: please enter hostname\n")
            return
        argumentList = hostname.split()
        if len(argumentList) != 1:
            print("Only accept 1 parameter\n")
            return
        ServerFunctionCLI.DiscoverHostname(hostname=hostname)
    def do_ping(self,hostname):
        if hostname == "":
            print("Hostname parameter is empty: please enter hostname\n")
            return
        argumentList = hostname.split()
        if len(argumentList) != 1:
            print("Only accept 1 parameter\n")
            return
        ServerFunctionCLI.PingHostname(hostname=hostname)
    def do_show(self,arg):
        if (len(arg)!=0):
            print("This command does not allow any argument\n")
            return
        ServerFunctionCLI.ShowAllUser()
    def default(self, line):
        if line == "q" or line == "EOF" or line == "exit" or line == "quit":
            return True

        return super().default(line)
    def help_discover(self):
        print("syntax: discover [hostname]\n")
        print("discover the list of local files of the host named hostname\n")
    def help_ping(self):
        print("syntax: ping [hostname]\n")
        print("live check the host named hostname\n")
    def help_show(self):
        print("syntax: show\n")
        print("Show all information of all hostname\n")
    def help_exit(self):
        print("To exit the program, simply type \"exit\"\n")

ServerCLI().cmdloop()