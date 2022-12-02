from ast import Tuple
import Pyro4
import time
from utils.logger import log

class StrangeClient:
        def __init__(self):
                self.server = None
                self.name = None
                self.game_id = None
                self.player_id = None
                self.connected = False
                self.opponent = None

        def connect_to_server(self, server_uri):
                server_is_active, msg_printed = False, False
                log(type="GAME_MSG", msg=f"Connecting to StrangeGameServer...")
                while not server_is_active:
                        try:
                                self.server = Pyro4.Proxy(server_uri) # Use name server object lookup uri shortcut
                                server_is_active = self.server.check_status()
                        except Exception as e:
                                if not msg_printed:
                                        msg_printed = True
                                        log(type="GAME_MSG", msg=f"Waiting for StrangeGameServer...")
                                self.server = None
                log(type="GAME_MSG", msg=f"Connected to StrangeGameServer...")
                
        def is_connected(self) -> bool:
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
                        message = f"Hey {self.name}, your opponent is {self.opponent} - Game: {self.game_id}" if self.opponent else f"Hey {self.name}, wait for your opponent"
                        if message != old_message:
                                log(type="GAME_MSG", msg=message)
                        old_message = message

        def play(self):
                while self.server.game_is_active(self.game_id):
                        log(type="GAME_MSG", msg="Playing :)")
                        game_details = self.server.initialize_game(self.game_id, self.name)  
                        log(type="GAME_MSG", msg=f"Long Strange Word: {game_details['long_strange_word']}")
                        
                        winner, answer_is_valid = None, None
                        while winner is None:
                                if answer_is_valid is None:
                                        answer_is_valid = self.send_answer(game_details)
                                
                                if self.server.both_player_answered(self.game_id):
                                        winner = self.server.find_winner(self.game_id)
                                
                                        if winner is not None:
                                                log(type="INFO", msg=f"{winner}")
                                                if self.name in winner:
                                                        log(type="GAME_MSG", msg=f"Congratulations {winner} - Your anser is correct!!")  
                                                        printed = True
                                                        return
                                                else:
                                                        # Close the game and makes the opponent leave
                                                        log(type="GAME_MSG", msg=f"Oops you lost :(")  
                                                        self.leave_game()
                                        else:
                                                 answer_is_valid = None 
                                

        def send_answer(self, game_details):
                log(type="GAME_MSG", msg=f"Type the number of occurrence for character: {game_details['character_to_find']}")
                time_start = time.time()
                answer = input(">> ")
                time_end = time.time()
                total_time =  round(time_end - time_start, 3)
                player_answer = {'answer': answer, 'total_time': total_time}
                log(type="GAME_MSG", msg=f"You said in {total_time}s that the word has {player_answer['answer']} occurence for char {game_details['character_to_find']}")
                answer_is_valid, _ = self.server.validate_answer(self.game_id, self.name, data=player_answer)
                if not answer_is_valid:
                        log(type="GAME_MSG", msg=f"Sorry you provide a wrong value of occurrence.") 
                return answer_is_valid

        def reset_player_status(self):
                if self.connected:
                        self.game_id = None
                        self.player_id = None
                        input("Previous Game is over- press ENTER to play again.")
                        self.player_id = self.server.get_player_id(self.name)
                        self.server.activate_player(self.name)
                        log(type="GAME_MSG", msg=f"Hey [{self.name}], we are ready for another match - Your new id is {self.player_id}")

                