from os import makedirs
from os.path import isdir

if __name__ == '__main__':
    if not isdir('./Levels'):
        makedirs('Levels')
        makedirs('Levels/Templates')
    
    if not isdir('./Sprites'):
        makedirs('Sprites')

    if not isdir('./Data'):
        makedirs('Data')