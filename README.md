# Strange Multiplayer Game
Algoritmi Distribuiti - Multiplayer game with Pyro <br>
Fabio Bove | fabio.bove.dr@gmail.com | 216219@studenti.unimore.it<br>

A Simple, but strange, multiplayer game.<br>
In this game two players can challenge each other trying to find the number of occurrence of a given character in a word.<br>
Seems easy, but the word is made from randomly chosen and shuffled characters. The length of a word makes a game easier or harder.<br>

The fastest player wins and can continue to play - loser is kicked out from the server.<br>

# Enviroment Configuration
Go to the main directory and activate the /pad-venv, wich is the virtual enviroment of the project.

# How to start the server 
Go to the /src directory.<br>
Just open a new terminal and type the following commands:<br>
>> python -m Pyro4.naming<br>
>> python run_server.py<br>

# How to start the client
Go to the /src directory.<br>
To run type the following command on the terminal:<br>
>> python run_client.py<br>

# Project Requests 
All'esame deve essere mostrata l'applicazione in esecuzione e deve essere presentata una relazione che descrive il progetto realizzato e deve comprendere: <br>
- Descrizione dei requisiti, ed in particolare delle funzionalità messe a disposizione (ad es. tramite SRS);
- Descrizione dell'architettura (ad es. tramite diagramma a blocchi o UML);
- Descrizione dei protocolli usati (client-server o peer-to-peer, ad es. tramite diagrammi UML).
