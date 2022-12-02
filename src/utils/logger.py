from datetime import date

DEBUG = True # If set to False only GAME_MSG will be printed
MSG_TYPE = ['ERROR', 'GAME_MSG', 'INFO'] # Valid type of message
LOG_DIR = '..\logs'

def log(type:str, msg:str):
    """
    log function, simply prints the given message on the terminal.

    :param type1: the type of log message -> valid types are in the list MSG_TYPE
    :param msg: the message that needs to be printed
    :return: nothing
    """ 
    if type in MSG_TYPE: # If message type is valid
        
        if DEBUG or type == 'GAME_MSG': # If DEBUG is set to False will print only messages of type 'GAME_MSG'
            print(f"{type} - {msg}")
            
            today = date.today() # Get current date to give name to the log file

            with open(f"{LOG_DIR}\{today}.txt", "a") as f: # Appends the log message to a file in the LOG_DIR
                f.write(f"{type} - {msg} \n")