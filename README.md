# Trenches
A 2D tower defence game developed using Python and pygame

# TRENCHES

The game TRENCHES is a tower defence game with some new flavours added to
the game play, most notably, unlike in conventional tower defence games where
incoming enemies are unable to attack and destroy the defending units, the
player's defences are at constant risks, like real soldiers in battle field
trenches.

Another major change to the game play is defending units are not strictly
static: once a soldier runs out of ammo, he will move to a nearby ammobox
and reload; should a army doctor find a wounded fellow, he will come over
and heal the wound. After reload, soldier will return back to his original
slot, and army doctor will just stay where he is, until next medic care
call is issued.

Consistent with most tower defence games, the goal of the game is to eliminate
threats to the protected target (HQ in this case), by placing defencing units
along the path of incoming attacks. Valid locations for defence deployment
are inside the trenches (hence comes the title). Incoming enemies will come
from one or multiple directions. If certain number of enemies pass across
your defence lines, the mission is failed.

Defence units the player can deploy include:

    - Rifle men,
    - Machinegun men,
    - Grenadiers,
    - Mortars,
    - Artilleries,
    - Snipers,
    - Medics, to heal wounded soldiers,
    - Ammoboxes, to provide ammo to all other units except Medics.

Enemy team may have all above units except Medics and Ammoboxes.

Some tips/features:

    - Firing accuracy will drop when wounded, so will moving speed.
    - Certain chance the enemy's firing will miss, thus mimicking the effect
      of extra cover provided by the trenches.
    - Explosive weapons have areal damage.
    - The in-game intel-bar shows intels about incoming attacks, as well as
      some shouts from your men.
    - Some other tips are shown in the game.


The game has got its basic shape: a working game play, a set of GUI, some
option settings, and a relatively easy level design system to facilitate
quick level designs. However, there are still some features that I haven't
got the time to fully implement, like map-scrolling to allow for larger maps,
a grid-system that allows for units of different sizes, the ability to
control movement and firing of defencing units, weathers, more units,
and of cause better graphics.

I may come back to implement some of these, but I kind of prefer leaving it
for now and starting to learn a more powerful game engine, perhaps Unity.
So if anyone finds this game interesting and would like to mod it, please
go ahead, and I'd appreciate it if you could also share with me your own
re-creations.

Author: Guangzhi XU (xugzhi1987@gmail.com, guangzhi.xu@outlook.com)


# Download:

    - Windows (tested in 7 and 10 64bit): https://drive.google.com/open?id=0B8wpnLHH0j1hXy1md3BPd2xwYlE
    - Linux (tested in Manjaro 17.0.2 64bit): https://drive.google.com/open?id=0B8wpnLHH0j1hUTl5NGtJWTFmWlk
    - For both of above, download the package, unzip, and run "Trenches"
    - No Mac version at the moment
    - You can of cause obtain the source and run the main python script "Trenches.py", to do that: 
        - Required python modules:
            - pygame (mine is 1.9.3).
            - numpy



# Screenshots

![Screenshot1](ui/Screenshot1.png?raw=true "Screenshot1")

![Screenshot2](ui/Screenshot2.png?raw=true "Screenshot2")

![Screenshot3](ui/Screenshot3.png?raw=true "Screenshot3")

