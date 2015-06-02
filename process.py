import os

import main


def test(dirname):
    for file in os.listdir(dirname):
        main.process(dirname + '/' + file)

if __name__=="__main__":
    test("data")