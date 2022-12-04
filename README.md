# Strange Multiplayer Game
Algoritmi Distribuiti - Multiplayer game with Pyro
Fabio Bove | fabio.bove.dr@gmail.com 216219@studenti.unimore.it

A Simple, but strange, multiplayer game.
In this game two players can challenge each other trying to find the number of occurrence of a given character in a word.
Seems easy, but the word is made from randomly chosen and shuffled characters. The length of a word makes a game easier or harder.

The fastest player wins and can continue to play - loser is kicked out from the server.

# How to start the server
Go to the /src directory.
Just open a new terminal and type the following commands: 
>> python -m Pyro4.naming
>> python run_server.py

# How to start the client
Go to the /src directory. 
To run type the following command on the terminal: 
>> python run_client.py

# Have fun ;)