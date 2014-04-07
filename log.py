import sys

class LogMessage(object):
    def __init__(self, timestamp, text):
        self.date = sys.time()
        self.timestmap = timestamp
        self.text = text

    def __str__(self):
        return 

class Logger(object):
    def __init__(self, filename):
        self.filename = filename
        
    def log(self, message):
        with open(filename, "a") as file:
            file.write(message + "\n")