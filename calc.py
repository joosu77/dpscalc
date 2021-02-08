from osrsbox import items_api
from osrsbox import monsters_api
import math

items = items_api.load()
monsters = monsters_api.load()

# Levels
atkLvl = 81
strLvl = 96
defLvl = 80
rangeLvl = 92
mageLvl = 91

# Boosts
supStr = False
supAtk = False
rangePot = True
magePot = False
piety = False
eagleEye = False
mysticMight = False

class Set:
    it = {"head":{},"cape":{},"neck":{},"ammo":{},"weapon":{},"body":{},"shield":{},"legs":{},"hands":{},"feet":{},"ring":{}}
    def __init__(self, preset=[{},{},{},{},{},{},{},{},{},{},{}]):
        ctr = 0
        for i in self.it:
            if preset[ctr]:
                self.it[i] = findItem(preset[ctr])
            ctr+=1
    def getAtk(self, style):
        sum = 0
        for slot in self.it:
            if self.it[slot]:
                sum += eval("self.it[slot].equipment.attack_"+style)
        return sum
    def getStr(self, style):
        sum = 0
        for slot in self.it:
            if self.it[slot]:
                if style == "mage":
                    sum += self.it[slot].equipment.magic_damage
                elif style == "range":
                    sum += self.it[slot].equipment.range_strength
                else:
                    sum += self.it[slot].equipment.melee_strength
        return sum
    def toString(self):
        res = ""
        for slot in self.it:
            if self.it[slot]:
                res+=self.it[slot].name +", "
        return res


def findItem(name):
    li = [i for i in items if i.name.lower() == name.lower() and i.duplicate == False]
    if len(li) == 0:
        print(f"Error in find item: no item matching name {name}")
        return 0
    elif len(li) > 1:
        print(f"Error in find item: found {len(li)} matches for name {name}")
    return li[0]

def findMonster(name):
    li = [i for i in monsters if i.duplicate == False and i.name == name]
    while len(li) == 0:
        print(f"Could not find monster, try again:")
        name = input()
        li = [i for i in monsters if i.duplicate == False and i.name == name]
    if len(li) > 1:
        print(f"Multiple monsters found, choose from:")
        for i in range(len(li)):
            print(f"[{i}] {li[i].wiki_url}")
        return li[getInp(range(len(li)))]
    return li[0]

def getInp(validVals, checkForPrefix = False):
    inp = input()
    if checkForPrefix:
        while list(filter(inp.startswith, validVals)) == []:
            print(f"Entered value prefix not within {validVals}, try again")
            inp = input()
    else:
        while inp not in validVals:
            print(f"Entered value not within {validVals}, try again")
            inp = input()
    return inp

presets = [i.strip().split(";") for i in open("presets","r").readlines() if i[0] != '#']
print ("Choose preset:")
print ("[0] Empty")
for i in range(len(presets)):
    print (f"[{i+1}] {presets[i][0]}")
inp = int(getInp(map(str,range(len(presets)+1))))

set = Set()
if inp == 0:
    print ("Selected preset: empty")
else:
    set = Set(presets[inp-1][1:])
    print (f"Selected preset: {set.toString()}")
print ("Replace or remove items using +item name and -slot name, start calculations using !") # TODO: add preset command
inp = ""
while inp != "!":
    inp = getInp(["+","-","!"], True)
    if inp[0] == "+":
        item = findItem(inp[1:])
        if item and item.equipable_by_player:
            if item.equipment.slot == "2h":
                set.it["weapon"] = item
                set.it["shield"] = {}
            else:
                set.it[item.equipment.slot] = item
        else:
            print ("Invlaid item")
            
    elif inp[0] == "-":
        slot = inp[1:]
        if slot in set.it:
            set.it[slot] = {}
        else:
            print ("Invalid slot name")
print("Enter attack style (mage,range,slash,stab,crush)")
style = getInp(["mage","range","slash","stab","crush"])
strBon = set.getStr(style)
atkBon = set.getAtk(style)
aggressiveStyle = True #TODO: check style
accurateStyle = False
controlledStyle = False

print(atkBon)

# Maxhit and max attack roll calc:
if style in ["slash","stab","crush"]:
    # Melee
    effectiveStr = strLvl+supStr*(strLvl*15/100+5)
    effectiveAtk = atkLvl+supAtk*(atkLvl*15/100+5)
    if piety:
        effectiveStr *= 1.23
        effectiveAtk *= 1.2
    effectiveStr = math.floor(effectiveStr)+1*controlledStyle+3*aggressiveStyle+8
    effectiveAtk = math.floor(effectiveAtk)+1*controlledStyle+3*accurateStyle+8
    if (set.it["head"] and set.it["head"].name.endswith("oid melee helm")) and set.it["body"] and (set.it["body"].name == "Void knight top" or set.it["body"].name == "Elite void top") and set.it["legs"] and (set.it["legs"].name == "Void knight robe" or set.it["legs"].name == "Elite void robe"):
        effectiveStr = math.floor(effectiveStr*1.1)
        effectiveAtk = math.floor(effectiveAtk*1.1)
    maxhit = math.floor((effectiveStr*(strBon+64)+320)/640)
    maxAtkRoll = effectiveAtk*(atkBon+64)
    if set.it["head"] and set.it["head"].name.startswith("Slayer helm") or set.it["neck"] and set.it["neck"].name == "Salve amulet":
        maxhit = math.floor(maxhit*7/6)
        maxAtkRoll = math.floor(maxAtkRoll*7/6)
    elif set.it["neck"] and set.it["neck"].name == "Salve amulet (e)" or set.it["neck"] and set.it["neck"].name == "Salve amulet(ei)":
        maxhit = math.floor(maxhit*1.2)
        maxAtkRoll = math.floor(maxAtkRoll*1.2)
    maxAtkRoll = effectiveAtk*(atkBon+64)
elif style == "mage":
    # Mage
    maxhit = 1
else:
    # Range
    maxhit = 1
print (f"Max hit is {maxhit}, max atk roll is {maxAtkRoll}")
print ("Enter enemy:")
monsName = input()
monster = findMonster(monsName)

# Max def roll calc:
if style == "slash":
    maxDefRoll = (monster.defence_level+9)*(monster.defence_slash+64)
elif style == "stab":
    maxDefRoll = (monster.defence_level+9)*(monster.defence_stab+64)
elif style == "crush":
    maxDefRoll = (monster.defence_level+9)*(monster.defence_crush+64)
#TODO: add mage and range

if maxAtkRoll > maxDefRoll:
    hitChance = 1-(maxDefRoll+2)/(2*maxAtkRoll+1)
else:
    hitChance = maxAtkRoll/(2*maxDefRoll+1)

DPH = maxhit*hitChance/2
if set.it["weapon"]:
    speed = set.it["weapon"].weapon.attack_speed
else:
    speed = 4
DPS = DPH/(speed*0.6)
print (f"DPS is {DPS} and hit chance is {hitChance}")
