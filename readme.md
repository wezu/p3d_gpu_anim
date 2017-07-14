# Hardware Animation and Instancing for Panda3D

The re-usable code is in crowd.py, main.py is a demo.

To make this work you will need to pre-proces your models. You need to add custom verex attributes with joint numbers and weights (see model_process.py), you will also need to turn all yur animations into 2d table (a texture, see sample_anim.py).
You will also need Panda3D 1.8+ (or probably 1.9+), with either Python2.x or 3.x and a gpu/driver running opengl 3.1 

The Crowd class (in crowd.py) allows to make multiple hardware animated and instanced actors.
For custom use one probably needs to alter the shaders (included):
shaders/anim_v.glsl and shaders/anim_f.glsl

Once a Crowd is created you can controll individual actors by index
```
my_crowd=Crowd(...)
my_crowd[12].set_pos(...)
my_crowd[7].set_hpr(...)
my_crowd[1].play(...)
```
The object retured by __getitem__ ( [] brackets) is a CrowdActor,
it uses NodePath methods (and has a NodePath inside if you need it
eg. my_crowd[0].node), it also has play(), loop(), pose(), stop(),
and get_current_frame() functions.

See crowd.py for more info on the API

The included model/texture is based on a MakeHuman model, CC0
