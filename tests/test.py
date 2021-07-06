
from fstop import Runner

if __name__ == '__main__':
    with open("tests/test.fstop") as ft:
        string = ft.read()

    run = Runner()
    print(run.execute(string))