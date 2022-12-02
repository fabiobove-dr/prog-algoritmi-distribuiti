"""
Fabio Bove | 216219@studenti.unimore.it | fabio.bove.dr@gmail.com

This module runs the server of the "Strange Multiplayer Game".

Before running open a new terminale and type the following command on the terminal: 
>> python -m Pyro4.naming
"""

import Pyro4
import os
from utils.logger import log # For logging and debug purpose
from game.Server import StrangeGameServer # The StrangeGameServer class

def main():
    os.system('cls') # Clean the screen from previous stuff adnd print a message
    log(type="GAME_MSG", msg="StrangeGameServer - server started.") 
    
    Pyro4.Daemon.serveSimple( # Finds the name server 
        {StrangeGameServer: "StrangeGameServer"}, 
        ns = Pyro4.locateNS(), 
        verbose = False
    )  

if __name__=="__main__":
    main()