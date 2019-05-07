from os import makedirs
from os.path import isdir

if __name__ == '__main__':
    if not isdir('./Assets/Resources'):
        makedirs('Assets/Resources')

    if not isdir('./Assets/Resources/Levels'):
        makedirs('Assets/Resources/Levels')
        makedirs('./Assets/Resources/Levels/Templates')
    
    if not isdir('./Assets/Resources/Sprites'):
        makedirs('./Assets/Resources/Sprites')

    if not isdir('./Assets/Data'):
        makedirs('Assets/Data')