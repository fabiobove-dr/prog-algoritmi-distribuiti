"""
Fabio Bove | 216219@studenti.unimore.it | fabio.bove.dr@gmail.com
This Class implements a StrangeServer and its functionalities for the "Strange Multiplayer Game".
"""


from utils.logger import log
from game.Game import StrangeGame
import Pyro4
import uuid

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class StrangeGameServer:
    def __init__(self):
        self.active_games = [] # List of active games
        self.games_details = [] # List of games details, one dict for each game
        self.active_players = 0 # Number of active player on the server (Note active player != connected player)
        self.players = [] # List of players connected to the server

    def check_status(self) -> bool:
        """
        check_status, simple method to check if the server is reachable 
        prints a log message on the server terminal, if DEBUG is set to True in the logger
        
        param: None
        returns: True (always)
        """
        log(type="INFO", msg=f"I'm a [StrangeGameServer] and i'm available to do strange stuff.")
        return True

    def game_is_active(self, game_id: str) -> bool:
        log(type="INFO", msg=f"Check the status of game {game_id}")
        print(f"p{game_id}")
        print(f"provaaaa {self.active_games}")
        return True if game_id in self.active_games else False

    def player_exists(self, name: str) -> bool:
        return True if name in self.players else False

    def add_player(self, name: str):
        try:
            self.players.append(name)
            self.active_players += 1
            log(type="INFO", msg=f"Player [{name}] added to server")
        except Exception as e:
            log(type="ERROR", msg=f"Can't add player [{name}], {e}")
    
    def activate_player(self, name):
        self.active_players += 1
        log(type="INFO", msg=f"Player [{name}] re-activated")

    def remove_player(self, name: str):
        try:
            self.players.remove(name)
            self.active_players -= 1
            log(type="INFO", msg=f"Player [{name}] removed from server")
        except Exception as e:
           log(type="ERROR", msg=f"Can't remove player [{name}], {e}")
    
    def get_players_of_game(self, game_id):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    #log(type="INFO", msg=f"Player of game {game_id} are: {game['players']}")
                    return game['players']
        except Exception as e:
                log(type="ERROR", msg=f" Can't get player of game {game_id}, {e}")
                return None

    def search_for_game(self):
        for game in self.games_details:
                if len(game['players']) == 1:
                    return game['game_id']
        return None

    def add_player_to_game(self, game_id, name):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    game['players'].append(name)
        except Exception as e:
                log(type="ERROR", msg=f"Can't add new player to game {game_id}, {e}")

    def add_new_game_details(self, game_id, name):
        game = StrangeGame(game_number=len(self.active_games), game_id=game_id, game_complexity=50)
        self.games_details.append({
            'game_id': game_id, 
            'details': game.configure_game(),
            'players': [name],
        })
        log(type="INFO", msg=f"Game details: {self.get_game_details(game_id)}")
    
    def a_game_is_available(self):
        return True if int(self.active_players / 2 ) == len(self.active_games) else False

    def start_game(self, name):
        game_id = None
        if self.active_players % 2 == 0 and self.active_players != 0:
            if self.a_game_is_available(): # This prevent to start two time a new game
                while game_id is None:
                    try:
                        game_id = self.search_for_game()
                    except Exception:
                        pass
                log(type="INFO", msg=f"New Game started for player [{name}]- Game ID: [{game_id}]")
                self.add_player_to_game(game_id, name)
            else:
                game_id = str(uuid.uuid4())
                self.active_games.append(game_id)
                self.add_new_game_details(game_id, name)
        return game_id


    def close_game(self, game_id, name):
        # If a player leaves before the opponent joined than the "game_id" is going to be "None"
        if game_id is None: 
            log(type="INFO", msg=f"Player [{name}] has left")
            self.remove_player(name)
        else:
            try:
                # Remove the player who left list of players, and both players from the active players count
                self.active_players -=2
                self.players.remove(name)
                # The game_id is removed from the active games on the server
                self.active_games.remove(game_id)
                self.remove_game_details(game_id)
                log(type="INFO", msg=f"Player [{name}] has left - Game {game_id} | Closed")
                log(type="INFO", msg=f"Active Players: {self.active_players}, Connected Players: {len(self.players)}, Active Games: {len(self.active_games)}")
            except Exception as e:
                log(type="ERROR", msg=f" Can't close game {game_id}, {e}")

    def initialize_game(self, game_id, name):
        log(type="INFO", msg=f"Active Games: {self.active_games}")
        details = None
        while details is None:
            try: 
                details  = self.get_game_details(game_id)
                log(type="INFO", msg=f"Details for game [{game_id}] obtained for player [{name}]")
            except Exception as e:
                pass
        return details

    def both_player_answered(self, game_id):
        player_1, player_2 = self.get_players_of_game(game_id)
        return self.player_answered(player_1, game_id) and self.player_answered(player_2, game_id) 
    
    def player_answered(self, name, game_id):
        return True if name in self.get_game_details(game_id) else False

    def get_game_details(self, game_id):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    #log(type="INFO", msg=f"Game details found for game [{game_id}]")
                    return game       
        except Exception as e:
            log(type="INFO", msg=f"Can't get Game details found for game [{game_id}], {e}")
            return None

    def store_player_answer(self, game_id, name, data):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    game[name] = data
                    #flog(type="INFO", msg=f"Player answer stored for [{game_id}], player [{name}]")
                    break
        except Exception as e:
            log(type="INFO", msg=f"Can't store player [{name}] answer, for game [{game_id}], {e}")

    def remove_game_details(self, game_id):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    del game
                    break
            log(type="INFO", msg=f"Game details removed for game [{game_id}]")
        except Exception as e:
            log(type="INFO", msg=f"Can't remove Game details for game [{game_id}], {e}")

    def validate_answer(self, game_id, name, data):
        # Store player answer -> wich is a dict {'answer': answer, 'total_time': total_time}
        if data: 
            try:
                self.store_player_answer(game_id, name, data)
                log(type="INFO", msg=f"Player [{name}] stored correctly")
            except Exception as e:
                log(type="ERROR", msg=f"Error storing information for player [{name}] answer, {e}")
        # Validate player answer
        answer_is_valid = False
        answer_time = float('inf')
        game_details = self.get_game_details(game_id)
        if game_details:
            occurrence =  int(game_details['details']['occurrence'])
            try:
                player_answer = int(game_details[name]['answer'])
            except Exception as e:
                player_answer = None
            
            if player_answer == occurrence:
                answer_is_valid = True 
                answer_time = game_details[name]['total_time']
                log(type="INFO", msg=f"Player [{name}] answer is valid")
            log(type="INFO", msg=f"Player [{name}] answer validity checked -> [{occurrence}, {player_answer}] ")

        return answer_is_valid, answer_time
        
    def find_winner(self, game_id):
        # Gets the players name
        winner = None
        player_1, player_2 = self.get_players_of_game(game_id)
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

       