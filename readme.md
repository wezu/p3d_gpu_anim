This is Work in Progress, but working at the moment.

The basic idea is to to use the default Panda3D Actor to sample all the animations and put them into one floating point texture.

The shader doing the animations will have access to all the animation frames so each instance can play it's own animation.

Files of interest:

main.py - demo showing 50 instances

crowd.py - main interface
