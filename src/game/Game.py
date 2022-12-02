import random
import string
import time
from utils.logger import log

class StrangeGame:
        def __init__(self, game_id, game_complexity):
                self.word_seed = random.seed(game_id + time.time())
                self.game_complexity = game_complexity
                self.long_strange_word = None
                self.character_to_find = None
                self.occurrence = None        

        def generate_word(self):
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

                return self.long_strange_word

        def choose_character(self):
                try:
                        self.character_to_find = random.choice(self.long_strange_word)
                        self.occurrence = self.long_strange_word.count(self.character_to_find)
                        log(type="INFO", msg=f"Choose the character to find and calculated its occurrence.")
                except Exception as e:
                        log(type="ERROR", msg=f"Can't choose caractert to find, {e}")
        
                return self.character_to_find, self.occurrence

        def configure_game(self):
                log(type="INFO", msg=f"Started a new game configuration")
                self.generate_word()
                self.choose_character()
                game_details = {
                        'game_complexity': self.game_complexity,
                        'long_strange_word': self.long_strange_word,
                        'character_to_find': self.character_to_find,
                        'occurrence': self.occurrence,       
                }
                return game_details
