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
        """
        game_is_active method, returns if a game is active

        param: game_id: the string that identifies a game
        return: True or False depending on the fact that the game is active or not
        """
        log(type="INFO", msg=f"Check the status of game {game_id}")
        return True if game_id in self.active_games else False

    def player_exists(self, name: str) -> bool:
        """
        player_exists method, return if a player is active thus is ready for a match

        param: name: A string which is unique and identifies a player
        return: True or False depending on the fact that the player is active
        """
        return True if name in self.players else False

    def add_player(self, name: str) -> None: 
        """
        add_player method, adds a new player to the players list asserts that a given can't be in the list already
        once the new player is added the number of active players is incremented by one unit.
        remember that the players list length is different from the number of active players.

        param: name: A string which is unique and identifies a player
        returns: nothing
        """
        try:
            self.players.append(name)
            self.active_players += 1 # Important to note that players list length is different from the number of active players
            log(type="INFO", msg=f"Player [{name}] added to server")
        except Exception as e:
            log(type="ERROR", msg=f"Can't add player [{name}], {e}")
    
    def activate_player(self, name: str) -> None:
        """
        activate_player method, reactivate a player which may was deactivated because its opponent left or he won the game
        simply increments the number of active players

        param: name:  A string which is unique and identifies a player, used only for logging purpose
        returns: Nothing
        """
        self.active_players += 1
        log(type="INFO", msg=f"Player [{name}] re-activated")

    def remove_player(self, name: str):
        """
        remove_player method, remove a player from the server

        param: name: A string which is unique and identifies the player that needs to be removed
        return: Nothing
        """
        try:
            self.players.remove(name) # Remove the player name
            self.active_players -= 1 # Decrease the number of active players
            log(type="INFO", msg=f"Player [{name}] removed from server")
        except Exception as e:
           log(type="ERROR", msg=f"Can't remove player [{name}], {e}")
    
    def get_players_of_game(self, game_id: str) -> list() or None:
        """
        get_players_of_game method, returns the list of players names (max length 2) that joined the game with given game_id 

        param: game_id: The identifier of the game
        return: players: The list of players names of the game
        """
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    # log(type="INFO", msg=f"Player of game {game_id} are: {game['players']}")
                    return game['players']
        except Exception as e:
                log(type="ERROR", msg=f" Can't get player of game {game_id}, {e}")
                return None

    def search_for_game(self) -> str or None:
        """
        search_for_game method, search for games with players waiting for an opponent if found
        returns the game_id of the first game found, if none of the game has one available slot returns None

        param: None
        return: game_id: The identifier of the game with only one connected player
        """
        for game in self.games_details:
                if len(game['players']) == 1:
                    return game['game_id']
        return None

    def add_player_to_game(self, game_id: str, name: str) -> None:
        """
        add_player_to_game method, add a new player to a game

        param: game_id: The identifier of the game
        param: name: The name of the player we want to add
        return: Nothing
        """
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

    def get_game_details(self, game_id:str):
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    #log(type="INFO", msg=f"Game details found for game [{game_id}]")
                    return game       
        except Exception as e:
            log(type="INFO", msg=f"Can't get Game details found for game [{game_id}], {e}")
            return None

    def initialize_game(self, game_id: str, name: str):
        log(type="INFO", msg=f"Active Games: {self.active_games}")
        details = None
        while details is None:
            try: 
                details  = self.get_game_details(game_id)
                log(type="INFO", msg=f"Details for game [{game_id}] obtained for player [{name}]")
            except Exception as e:
                pass
        return details

    def both_player_answered(self, game_id:str) -> bool:
        player_1, player_2 = self.get_players_of_game(game_id)
        return self.player_answered(player_1, game_id) and self.player_answered(player_2, game_id) 
    
    def player_answered(self, name: str, game_id:str) -> bool:
        return True if name in self.get_game_details(game_id) else False

    def store_player_answer(self, game_id: str, name: str, data: dict) -> None:
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    game[name] = data
                    #flog(type="INFO", msg=f"Player answer stored for [{game_id}], player [{name}]")
                    break
        except Exception as e:
            log(type="INFO", msg=f"Can't store player [{name}] answer, for game [{game_id}], {e}")

    def remove_game_details(self, game_id: str) -> None:
        try:
            for game in self.games_details:
                if game['game_id'] == game_id:
                    del game
                    break
            log(type="INFO", msg=f"Game details removed for game [{game_id}]")
        except Exception as e:
            log(type="INFO", msg=f"Can't remove Game details for game [{game_id}], {e}")

    def validate_answer(self, game_id: str, name: str, data: dict) -> list() or None:
        """
        validate_answer method, store player answer -> wich is a dict {'answer': answer, 'total_time': total_time}

        param: game_id: The indentifier of the game, wich is a string
        param: name: The name of the player that gave the answer
        param: data: A dict That contains the player answer -> {'answer': answer, 'total_time': total_time}
        return: answer_is_valid: A boolean that clarify if the player answer is valid (True) or not (False)
        return: answer_time: The time it took to the player to give the answer, set to float('inf') if the answer is not valid
        """
        if data: 
            try:
                self.store_player_answer(game_id, name, data)
                log(type="INFO", msg=f"Player [{name}] stored correctly")
            except Exception as e:
                log(type="ERROR", msg=f"Error storing information for player [{name}] answer, {e}")
        # Validate player answer
        answer_is_valid = False
        answer_time = float('inf')

        # Get Game details 
        game_details = self.get_game_details(game_id)

        if game_details:
            # Get the correct answer
            occurrence =  int(game_details['details']['occurrence'])
            try:
                player_answer = int(game_details[name]['answer'])
            except Exception as e:
                player_answer = None
            if player_answer == occurrence: # If the player gave a correct answer
                answer_is_valid = True 
                answer_time = game_details[name]['total_time']
                log(type="INFO", msg=f"Player [{name}] answer is valid")
            log(type="INFO", msg=f"Player [{name}] answer validity checked -> [{occurrence}, {player_answer}] ")
        return answer_is_valid, answer_time
        
    def find_winner(self, game_id: str) -> list() or None:
        """
        find_winner method, find the winner of a game.
        Wait for the answer of both players and than check for the time of the answer.
        The fastest player who gave the correct solution wins the game. If it's a tie then no one wins

        param: game_id:  A string that identifies the game
        return: winner: A list that contains the name of the winner or that is empty if no one won. Returns None if a player answer is missing
        """
        winner = None
        player_1, player_2 = self.get_players_of_game(game_id) # Get players names for logging purpose
        if self.both_player_answered(game_id): # If both players gave an answer
            # Check if their answer are valid
            player_1_answer_is_valid, player_1_time = self.validate_answer(game_id, player_1, data=None)
            player_2_answer_is_valid, player_2_time = self.validate_answer(game_id, player_2, data=None)
            # If only one of the answer is valid than is obivious which player has won
            if not player_1_answer_is_valid and not player_2_answer_is_valid:
                return winner
            if player_1_time == player_2_time: # if its a tie then no one won, the winner list is empty
                winner = [] # Can't be None, also a list makes it easier to understant the code
            else: # Otherwhise we check for the fastes
                winner = [player_1] if player_1_time < player_2_time else [player_2]
                log(type="INFO", msg=f"Times [{player_1_time} vs {player_2_time}]")
        return winner

       