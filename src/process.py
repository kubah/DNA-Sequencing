import os
from datetime import datetime

from src import main

dataDir = "data"


def process(dirname):
    filename = datetime.now().isoformat()
    f = open(dirname + '/' + filename, 'w')
    for file in os.listdir(dirname):
        results = main.main(dirname + '/' + file)
        f.write(file + " : " + results + "\n")
    f.close()


if __name__ == "__main__":
    process(dataDir)
