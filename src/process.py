import os

from src import main


dataDir = "data"


def process(dirname):
    for file in os.listdir(dirname):
        main.main(dirname + '/' + file)

if __name__ == "__main__":
    process(dataDir)