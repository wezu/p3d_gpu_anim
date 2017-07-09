This is Work in Progress, nothing is working at the moment.

The basic idea is to to use the default Panda3D Actor to sample all the animations and put them into one floating point texture.

The shader doing the animations will have access to all the animation frames so each instance can play it's own animation.

What works? What works not?
model_process.py - this will take a model and write extra vertex attributes with joint weights and index and also output a json file with a list of joint names.

sample_anim.py - this uses a p3d Actor to make a pfm of all (em.. one at the moment) animations and put them in a pfm file.
For each frame in the animation it will write 4x Point4 values making up a matrix for each joint and each frame (wip: the matrix may be wrong)

test_pfm.py - testing how to pack a mat4 into a texture from python and unpack it in a vertex shader

run_test.py - this should load a model and run (or pose) the animation saved in the pfm file from sample_anim.py, currently is broken and displays nothing, nix, null, nada

