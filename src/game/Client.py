"""
Fabio Bove | 216219@studenti.unimore.it | fabio.bove.dr@gmail.com
This Class implements a StrangeClient and its functionalities for the "Strange Multiplayer Game".
"""

import Pyro4
import time
import os
from utils.logger import log

class StrangeClient:
        def __init__(self):
                self.server = None
                self.name = None
                self.game_id = None
                self.game_details = None
                self.player_id = None
                self.connected = False
                self.opponent = None

        def connect_to_server(self, server_uri:str) -> None:
                """
                connect_to_server, method that allow the client to search for an active StrangeGameServer identified by the given uri
                
                param: server_uri: A Pyroname string that allow to connect to the server e.g. "PYRONAME:StrangeGameServer"
                returns: none
                """
                server_is_active, msg_printed = False, False
                log(type="GAME_MSG", msg=f"Connecting to StrangeGameServer...")
                while not server_is_active: # Search for the server until gets an answer
                        try:
                                self.server = Pyro4.Proxy(server_uri) # Use name server object lookup uri shortcut
                                server_is_active = self.server.check_status() #Check the status of the server
                        except Exception as e:
                                if not msg_printed:
                                        msg_printed = True
                                        log(type="GAME_MSG", msg=f"Waiting for StrangeGameServer...")
                                self.server = None
                log(type="GAME_MSG", msg=f"Connected to StrangeGameServer...")
                
        def is_connected(self) -> bool:
                """
                is_connected, method that returns if a client is connected to server 
                
                param: None
                returns: self.connected: Boolean that specify if the client is connect or not
                """
                return self.connected

        def leave_game(self):
                self.connected = False
                self.server.close_game(self.game_id, self.name)
                log(type="GAME_MSG", msg=f"Bye [{self.name}], game left!")

        def welcome(self) -> list([str, int]):
                if not self.connected:
                        self.name = input("What is your name?").strip()
                        while self.server.player_exists(self.name):
                                self.name = input("This nickname is already in use, try again: ").strip()
                        self.player_id = self.server.add_player(self.name)
                        self.connected = True
                return self.name, self.player_id
        
        def load_game(self):
                old_message = None
                while self.game_id == None:
                        self.opponent, self.game_id = self.server.start_game(self.name)
                        message = f"Hey [{self.name}], your opponent is [{self.opponent}] - Game: [{self.game_id}]" if self.opponent else f"Hey [{self.name}], wait for your opponent."
                        if message != old_message:
                                log(type="GAME_MSG", msg=message)
                        old_message = message

        def play(self):
                while self.server.game_is_active(self.game_id):
                        log(type="GAME_MSG", msg="Playing :)")
                        
                        game = self.server.initialize_game(self.game_id, self.name)  
                        self.game_details = game['details']
                        log(type="GAME_MSG", msg=f"Long Strange Word: {self.game_details['long_strange_word']}")
                        
                        # Finds the winner of the game 
                        winner, answer_is_valid = None, None
                        while winner is None: # While there's no winner
                                self.server.get_game_details(self.game_id)
                                if answer_is_valid is None: # If The player has't given an answer yet
                                        answer_is_valid = self.send_answer()
                                
                                if self.server.both_player_answered(self.game_id): # If both player have answered we can check if ther is a winner
                                        winner = self.server.find_winner(self.game_id) # Finds the winner or check for tie
                                        if winner is not None:
                                                if self.name in winner: # If the player is the winner of the game
                                                        log(type="GAME_MSG", msg=f"Congratulations [{winner}] - Your Won! ;)")  
                                                        return # Returns so other action can be performed
                                                else: # If the player is not the winner - close the game leaves
                                                        log(type="GAME_MSG", msg=f"Oops [{self.name}] you lost! :(")  
                                                        self.leave_game()
                                        else: # Both answer are not valid or its a tie, we reset the answer_is_valid so player can anwer again
                                                 answer_is_valid = None 
                                

        def send_answer(self) -> bool:
                os.system('cls') # Clean the screen from previous messages
                log(type="GAME_MSG", msg=f"Type the number of occurrence for character: '{self.game_details['character_to_find']}'")
                
                time_start = time.time() # Timer is started for performance evaluation and see which player is the fastest
                answer = input(">> ") # Takes the player answer
                time_end = time.time() # Time is stopped
                total_time =  round(time_end - time_start, 4) # We round the time results to the forth decimal, should be enought 

                player_answer = {'answer': answer, 'total_time': total_time} # Creates a dict with the player answer details: time and given number of occurrence
                log(type="GAME_MSG", msg=f"You said in {total_time}s that the word has {player_answer['answer']} occurence for char {self.game_details['character_to_find']}")
                
                # Check the validity of the player answer and print a message depending on the validity
                answer_is_valid, _ = self.server.validate_answer(self.game_id, self.name, data=player_answer)
                log(type="GAME_MSG", msg=f"Sorry, you provide a wrong number of occurrence...")  if not answer_is_valid else log(type="GAME_MSG", msg=f"Yeah, you provide the correct number of occurrence - Let's see if fast enought...") 
                        
                return answer_is_valid

        def reset_player_status(self) -> None:
                """
                reset_player_status, method that reset the attribute of a player that is connect to the server,
                used when a player has won a match or its opponent leaves the game

                param: None
                returns: None
                """
                if self.connected: # If the player is connected to the server
                        self.game_id,  self.player_id = None, None # Reset the player and game ids
                        input("Previous Game is over - press ENTER to play again.") # Remains in pause waiting for the player response
                        self.player_id = self.server.get_player_id(self.name) # Get a new id for player
                        self.server.activate_player(self.name) # Re-activate the player so if a new opponents is found a new match can start
                        log(type="GAME_MSG", msg=f"Hey [{self.name}], ready for another match! - Your new id is {self.player_id}")

                