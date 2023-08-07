import os 
import json
import shutil #copy & overwrite ops
from subprocess import PIPE, run
import sys

game_dir_pattern = 'game'
gameCodeExt = '.go'
gamecompilecmd = ['go','build']

def find_all_game_paths(src):

    gamePath = []
    
    for root,dirs, files in os.walk(src):   #os.walk traverses through src dir and gives root dir, sub dirs and files
        for directory in dirs:
            if game_dir_pattern in directory.lower():
                path = os.path.join(src, directory)
                gamePath.append(path)
    
        break #only needs to be ran once

    return gamePath



def getNameFromPaths(paths, strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path) # '_' is a var holder for unneeded begging of path
        newDirNames = dir_name.replace(strip, '')
        new_names.append(newDirNames)

    return new_names


def createDir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def copy_and_overwrite(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)     #recursive delete 2 delete all files in path if it exist
    shutil.copytree(src, dest)
    

def makeJSONMetadateFile(path, gamedirs):
    data = {
        'GameNames' : gamedirs,
        'NumberOfGames' : len(gamedirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)




def compileGameCode(path):  #find .go file
    codefilename= None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(gameCodeExt):
                codefilename = file
                break
        break
    if codefilename is None:
        return
    command = gamecompilecmd + [codefilename] 
    runcmd(command, path)



def runcmd(cmd, path):
    cwd = os.getcwd() #code will be run in directly in dir w/ game code
    os.chdir(path)

    result = run(cmd, stdout=PIPE, stdin=PIPE, universal_newlines=True, shell=True) #PIPE is a bridge between py code & process used to run cmd
    print('compile result ', result)

    os.chdir(cwd)






def main(source,tgt):
    
    cwd = os.getcwd()
    srcpath = os.path.join(cwd, source) #full file path by by joinging cwd to src
    tgtpath = os.path.join(cwd, tgt) #full file path by by joining cwd to src

    game_paths = find_all_game_paths(source)
    newGameDirs = getNameFromPaths(game_paths, '_game')
    print(newGameDirs)

    createDir(tgtpath)

    for src, dest in zip(game_paths, newGameDirs): #zip makes tuple of both arrays
        destPath = os.path.join(tgtpath, dest)
        copy_and_overwrite(src, destPath)
        compileGameCode(destPath)

    jsonPath = os.path.join(tgtpath, "metadata.json")
    makeJSONMetadateFile(jsonPath, newGameDirs)

    createDir(tgtpath)




if __name__ == "__main__": #check if program is being run as main program (directly) & not and import (name == module 4 imports)
    args = sys.argv
    #print(args)

    if len(args) != 3:
        raise Exception("Pass a source AND target directory ONLY please. ")
    
    src, tgt = args[1:] # starting from 1 strips of py file name
    main(src,tgt)



