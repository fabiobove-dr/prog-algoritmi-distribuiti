"""
Fabio Bove - 216219@studenti.unimore.it
Note - 
"""

from utils.logger import log
from game.Game import StrangeGame
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class StrangeGameServer:
    def __init__(self):
        self.players_names = []
        self.active_games_id = []
        self.games_details = []
        self.active_players = 0

    def check_status(self):
        return True

    def game_is_active(self, game_id: int) -> bool:
        log(type="INFO", msg=f"Check the status of game {game_id}")
        if game_id in self.active_games_id:
            return True
        return False

    def player_exists(self, name: str) -> bool:
        if name in self.players_names:
            return True
        return False

    def add_player(self, name: str) -> int or None:
        try:
            self.players_names.append(name)
            self.active_players += 1
            player_id = self.active_players
            log(type="INFO", msg=f"Player [{name}] added to server")
            return player_id
        except Exception as e:
            log(type="ERROR", msg=f"Can't add player [{name}], {e}")
            return None()
    
    def activate_player(self, name):
        self.active_players += 1
        player_id = self.active_players
        log(type="INFO", msg=f"Player [{name}] re-activated")
        return player_id

    def remove_player(self, name: str):
        try:
            self.players_names.remove(name)
            self.active_players -= 1
            log(type="INFO", msg=f"Player [{name}] removed from server")
        except Exception as e:
           log(type="ERROR", msg=f"Can't remove player [{name}], {e}")

    def get_players_name_from_game_id(self, game_id): 
        # If at least two players are connected, otherwhise an error will occure
        # because we try to access an element of the list which doesn't exists (in case we have only one player)
        # if len(self.active_players) > 1 and game_id is not None:
        try:
            player_1_id = (game_id * 2) - 2
            player_2_id = (game_id * 2) - 1
            player_1 = self.players_names[player_1_id]  
            player_2 = self.players_names[player_2_id]
            return player_1, player_2
        except Exception as e:
            log(type="ERROR", msg=f"Can't get players id, {e}")
            return None, None

    def get_player_id(self, name):
        return self.players_names.index(name)

    def start_game(self, name):
        # If we have an even number of active players on the server we can start a new game
        if self.active_players % 2 == 0 and self.active_players != 0:
            new_game_id = (self.active_players % 2) + 1
            player_1 = self.players_names[-1]  
            player_2 = self.players_names[-2]
            opponent = player_2 if name == player_1 else player_1
            # This prevent to be start two time a new game with the same id
            if new_game_id not in self.active_games_id:
                log(type="INFO", msg=f"New Game [{new_game_id}] Started between [{player_1}] vs [{player_2}]")
                self.active_games_id.append(new_game_id)
                # Configure the game 
                game = StrangeGame(new_game_id, game_complexity=50)
                self.games_details.append({new_game_id :  game.configure_game()})
                log(type="INFO", msg=f"Game details: {self.games_details[-1]}")
            return  opponent, new_game_id
        else:
            return None, None

    def close_game(self, game_id, name):
        # If a player leaves before the opponent joined than the "game_id" is going to be "None"
        if game_id is None: 
            log(type="INFO", msg=f"Player [{name}] has left")
            self.remove_player(name)
        else:
            try:
                # Get the opponents names from the game_id
                player_1, player_2 = self.get_players_name_from_game_id(game_id)
                # Remove both players from the active players count
                self.active_players -=2
                self.players_names.remove(player_1)
                self.players_names.remove(player_2)
                # The player which is still connected gets reinserted in the palyers on the server
                self.players_names.append(player_1) if player_1 != name else self.players_names.append(player_2) 
                # The game_id is removed from the active games on the server
                self.active_games_id.remove(game_id)
                del self.games_details[game_id -1]
                log(type="INFO", msg=f"Player [{name}] has left - Game {game_id} | [{player_1}] vs [{player_2}] Closed")
                log(type="INFO", msg=f"Active Players: {self.active_players}, Connected Players: {len(self.players_names)}, Active Games: {len(self.active_games_id)}")
            except Exception as e:
                log(type="ERROR", msg=f" Can't close game {game_id}, {e}")

    def initialize_game(self, game_id, name):
        log(type="INFO", msg=f"Active Games: {self.active_games_id}")
        details = None
        while details is None:
            try: 
                details  = self.games_details[game_id -1][1]
                log(type="INFO", msg=f"Details for game [{game_id}] obtained for player [{name}]")
            except Exception as e:
                pass
        return details

    def both_player_answered(self, game_id):
        player_1, player_2 = self.get_players_name_from_game_id(game_id)
        return self.player_answered(player_1, game_id) and self.player_answered(player_2, game_id) 
    
    def player_answered(self, name, game_id):
        return True if name in self.games_details[game_id -1][1] else False

    def validate_answer(self, game_id, name, data):
        # Store player answer -> wich is a dict {'answer': answer, 'total_time': total_time}
        if data: 
            try:
                self.games_details[game_id -1][1][name] = data
                log(type="INFO", msg=f"Player [{name}] stored correctly")
            except Exception as e:
                log(type="ERROR", msg=f"Error storing information for player [{name}] answer, {e}")
        # Validate player answer
        answer_is_valid = False
        answer_time = float('inf')
        
        occurrence =  int(self.games_details[game_id -1][1]['occurrence'])
        try:
            player_answer = int(self.games_details[game_id -1][1][name]['answer'])
        except Exception as e:
            player_answer = None
        
        if player_answer == occurrence:
            answer_is_valid = True 
            answer_time = self.games_details[game_id -1][1][name]['total_time']
            log(type="INFO", msg=f"Player [{name}] answer is valid")
        log(type="INFO", msg=f"Player [{name}] answer validity checked -> [{occurrence}, {player_answer}] ")

        return answer_is_valid, answer_time
        
    def find_winner(self, game_id):
        # Gets the players name
        winner = None
        player_1, player_2 = self.get_players_name_from_game_id(game_id)
        # If both players have given an answer
        if self.both_player_answered(game_id):
            # Check if their answer are valid
            player_1_answer_is_valid, player_1_time = self.validate_answer(game_id, player_1, data=None)
            player_2_answer_is_valid, player_2_time = self.validate_answer(game_id, player_2, data=None)
            if not player_1_answer_is_valid and not player_2_answer_is_valid:
                return winner
            if player_1_time == player_2_time:
                winner = []
            else:
                winner = [player_1] if player_1_time < player_2_time else [player_2]
                log(type="INFO", msg=f"Times [{player_1_time} vs {player_2_time}]")
        return winner

       