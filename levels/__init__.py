import os
import level01
import level02
import level03
import level04
import level05
import level06
import level07

PATH=os.path.dirname(os.path.realpath(__file__))

def listLevels():
    return [name for name in os.listdir(PATH)
            if os.path.isdir(os.path.join(PATH, name))]

#----Get import all levels--------------------------
def getAllLevels():

    all_levels=listLevels()
    level_pack=[]
    all_levels.sort()

    for level_str in all_levels:
        command='import '+level_str+' as current_level'
        exec(command)
        level_info=current_level.LevelInfo()
        level_pack.append(level_info)

    return level_pack


