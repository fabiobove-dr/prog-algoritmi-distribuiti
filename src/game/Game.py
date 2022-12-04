"""
Fabio Bove | 216219@studenti.unimore.it | fabio.bove.dr@gmail.com
This Class implements the StrangeGame which is the core for a match between two players of the "Strange Multiplayer Game".
"""

import random
import string
import time
from utils.logger import log

class StrangeGame:
        def __init__(self, game_number: int, game_id: str, game_complexity: int):
                self.word_seed = random.seed(game_number + time.time()) # Seed generated based on current time and game number
                self.game_complexity = game_complexity # Complexity of the game -> How long the word will be
                self.game_id = game_id # Identifier of the game
                self.long_strange_word = None
                self.character_to_find = None
                self.occurrence = None
                     
        def generate_word(self) -> None:
                """
                generate_word method, creates a random word of <game_complexity> char

                param: None
                return: Nothing
                """
                try:
                        base_word = list(''.join(random.choices(string.ascii_uppercase + string.digits, k=self.game_complexity)))
                        log(type="INFO", msg=f"Base word generated with game_complexity: {self.game_complexity}")
                except Exception as e:
                        log(type="ERROR", msg=f"Can't generate the base word, {e}")
           
                try:
                        random.shuffle(base_word)
                        self.long_strange_word = ''.join(base_word)
                        log(type="INFO", msg=f"Long Strange Word created.")
                except Exception as e:
                        log(type="ERROR", msg=f"Can't generate the Long Strange Word, {e}")

        def choose_character(self) -> None:
                """
                choose_character method, select a random character of the long_strange_word and counts its occurence
                
                param: None
                return: Nothing
                """
                try:
                        self.character_to_find = random.choice(self.long_strange_word)
                        self.occurrence = self.long_strange_word.count(self.character_to_find)
                        log(type="INFO", msg=f"Choosen the character to find and calculated its occurrence.")
                except Exception as e:
                        log(type="ERROR", msg=f"Can't choose caractert to find, {e}")
        
        def configure_game(self) -> dict:
                """
                configure_game method, returns a dict with the details for a new game.

                param: None
                return: game_details: Is a dict that containes the parameter for the game between two players
                """
                log(type="INFO", msg=f"Started a new game configuration")
                self.generate_word() # Generate a new word based on the parameter given when a new Game object is created
                self.choose_character() # Choose a random char in the string
                game_details = {
                        'game_complexity': self.game_complexity,
                        'long_strange_word': self.long_strange_word,
                        'character_to_find': self.character_to_find,
                        'occurrence': self.occurrence, # Occurrence of character_to_find in the string
                }
                return game_details
