"""
Fabio Bove | 216219@studenti.unimore.it | fabio.bove.dr@gmail.com

This module runs the client of the "Strange Multiplayer Game".

To run type the following command on the terminal: 
>> python run_client.py
"""

import os
import win32api # To manage the exit action of the client
from utils.logger import log # For logging and debug purpose
from game.Client import StrangeClient # The StrangeClient class

# Global object needed to manage the exit functionality
my_client = None

def main():
    """
    main function, manages the event that generates client side
    
    param: None
    returns: nothing
    """
    global client
    
    os.system('cls') # Clean the screen
    client = StrangeClient()  # Initialize the client, connecting to the server of the game
    client.connect_to_server(server_uri="PYRONAME:StrangeGameServer") 
    name = client.welcome() # Print the welcome message and register the player on the server asking for an username
    log(type="GAME_MSG", msg=f"Hello {name}, welcome to the Strange Game")

    while client.is_connected(): # Until the player remains connected or don't lose a match
        client.load_game() # Try to create a match between two users
        client.play() # Activate the game
        client.reset_player_status() # If the opponents leave or the player won the previous match
    
def exit(signal):
    """
    exit function, this function allow to manage the event generated when a player leaves the game

    param: signal: The event that called the function
    returns: nothing
    """
    global client
    client.leave_game()

if __name__=="__main__":
    win32api.SetConsoleCtrlHandler(exit, True) # Handle the exit event
    main()
    
    