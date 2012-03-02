from datetime import datetime


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print "[ICANHASJAVASCRIPT][" + timestamp + "] " + message
