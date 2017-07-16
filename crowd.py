from panda3d.core import *
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func
from direct.interval.FunctionInterval import Wait
from random import random
from math import floor
import json

__author__ = "wezu"
__copyright__ = "Copyright 2017"
__license__ = "ISC"
__version__ = "0.13"
__email__ = "wezu.dev@gmail.com"
__all__ = ['Crowd']


class Crowd(object):
    """Class allows to make multiple hardware animated and instanced actors.
    For custom use one probably needs to alter the shaders (included):
    shaders/anim_v.glsl and shaders/anim_f.glsl

    Once a Crowd is created you can controll individual actors by index
    my_crowd=Crowd(...)
    my_crowd[12].set_pos(...)
    my_crowd[7].set_hpr(...)
    my_crowd[1].play(...)

    The object retured by __getitem__ ( [] brackets) is a CrowdActor,
    it uses NodePath methods (and has a NodePath inside if you need it
    eg. my_crowd[0].node), it also has play(), loop(), pose(), stop(),
    and get_current_frame() functions.

    You Should never create a CrowdActor by yourself, it will do nothing
    without a Crowd controling it.

    model        - a loaded model (with the proper joint and weight vertex attributes)
    anim_texture - a loaded texture with the animation data
    animations   - a dict with the names of animations as keys and [start_frame, number_of_frames] as value
    num_actors   -initial number of actor instances
    frame_blend  -True/False should inter frame blending be used
    """
    def __init__(self, model, anim_texture=None, animations=None, num_actors=1, frame_blend=False):
        #load the model, instance it and set omni bounds
        if isinstance(model, NodePath):
            self.model=model
        else:
            self.model=loader.load_model(model)
        self.model.set_instance_count(num_actors)
        self.model.node().set_bounds(OmniBoundingVolume())
        self.model.node().set_final(True)

        #make sure the animation texture is set up right
        if anim_texture is not None:
            self.anim_texture=anim_texture
        else:
            tex_name=self._find_first_tag(self.model, 'anim_tex')
            self.anim_texture=loader.load_texture(tex_name)
        self.anim_texture.set_wrap_u(SamplerState.WM_clamp)
        self.anim_texture.set_wrap_v(SamplerState.WM_clamp)
        self.anim_texture.set_magfilter(SamplerState.FT_nearest)
        self.anim_texture.set_minfilter(SamplerState.FT_nearest)
        self.anim_texture.set_format(Texture.F_rgba32)

        #set the shader
        shader_define={'NUM_ACTORS':num_actors,
                       'MAX_Y':self.anim_texture.get_y_size()-1}
        self.frame_blend=frame_blend
        if frame_blend:
            shader_define['FRAME_BLEND']=1
        self.model.set_shader(self._load_shader(v_shader='shaders/anim_v.glsl',
                                                f_shader='shaders/anim_f.glsl',
                                                define=shader_define))


        #send the tex to the shader
        self.model.set_shader_input('anim_texture', self.anim_texture)

        #make an array of mat4 for each actor
        self.matrix_data=PTALMatrix4f()
        for i in range(num_actors):
            self.matrix_data.push_back(Mat4())
        self.model.set_shader_input('matrix_data', self.matrix_data)

        #make an array of vec4 for each actor
        self.anim_data=PTALVecBase4f()
        for i in range(num_actors):
            self.anim_data.push_back(Vec4(0.0, 1.0, 30.0, 0.0)) #start_frame, num_frame, fps, time_offset
        self.model.set_shader_input('anim_data', self.anim_data)

        #dict of named animations
        if animations is not None:
            self.animations=animations
        else:
            _anim_names=self._find_first_tag(self.model, 'anim_names').replace('\n', ' ').split()
            _anim_numbers=self._find_first_tag(self.model, 'anim_range').replace('\n', ' ').split()
            _anim_numbers=[[int(i) for i in j.split(":")] for j in _anim_numbers]
            self.animations=dict(zip(_anim_names,_anim_numbers))

        #list of actor nodes, so one can use crowd[12].play('some_anim')
        self.actors=[CrowdActor(i, self.animations) for i in range(num_actors)]

        self.task=taskMgr.add(self._update, "crowd_update", sort=-50)

    def set_count(self, target_actors):
        """Set the number of actor instances to target_actors
        """
        current_actors=len(self.actors)
        #add actors if needed
        while current_actors < target_actors:
            self.actors.append(CrowdActor(current_actors, self.animations))
            current_actors=len(self.actors)
        #remove actors if needed
        self.actors=self.actors[:target_actors]
        self.model.set_instance_count(target_actors)

    def reparent_to(self, node):
        """Reparents the Crowd to a node for rendering (usually render)
        No transformations are used.
        """
        self.model.reparent_to(node)

    def set_frame_blend(self, state=True):
        """ If state is True turns inter frame blending on, else turns it off
        """
        self.frame_blend=state
        shader_define={'NUM_ACTORS':len(self.actors),
                       'MAX_Y':self.anim_texture.get_y_size()-1}
        if state:
            shader_define['FRAME_BLEND']=1
        self.model.set_shader(self._load_shader(v_shader='shaders/anim_v.glsl',
                                                f_shader='shaders/anim_f.glsl',
                                                define=shader_define))
    def _find_first_tag(self, node, tag):
        for child in node.get_children():
            if child.has_tag(tag):
                return child.get_tag(tag)
            else:
                child_tag=self.find_tag(child, tag)
                if child_tag:
                    return child_tag
        return None

    def _update(self, task):
        for n, actor in enumerate(self.actors):
            self.matrix_data.set_element(n, actor.node.get_mat())
            self.anim_data.set_element(n, actor.anim_data)
        return task.again

    def _load_shader(self, v_shader, f_shader, define=None, version='#version 140'):
        # load the shader text
        with open(getModelPath().find_file(v_shader).to_os_specific()) as f:
            v_shader_txt = f.read()
        with open(getModelPath().find_file(f_shader).to_os_specific()) as f:
            f_shader_txt = f.read()
        # make the header
        if define:
            header = version + '\n'
            for name, value in define.items():
                header += '#define {0} {1}\n'.format(name, value)
            # put the header on top
            v_shader_txt = v_shader_txt.replace(version, header)
            f_shader_txt = f_shader_txt.replace(version, header)
        # make the shader
        shader = Shader.make(Shader.SL_GLSL, v_shader_txt, f_shader_txt)
        try:
            shader.set_filename(Shader.ST_vertex, v_shader)
            shader.set_filename(Shader.ST_fragment, f_shader)
        except:
            print('Shader filenames will not be available')
        return shader

    def __getitem__(self, index):
        return self.actors[index]

    def __iter__(self):
        for actor in self.actors:
            yield actor

    def remove(self):
        """Remove the whole thing
        """
        taskMgr.remove(self.task)
        self.model.remove_node()
        self.actors=None
        self.matrix_data=None
        self.anim_data=None

class CrowdActor(object):
    """CrowdActor is a helper class for the Crowd class.
    You Should never create a CrowdActor by yourself, it will do nothing
    without a Crowd controling it.

    You can use NodePath methods on a CrowdActor (not recomended to use remove_node())
    or get the NodePath directly (eg. my_crowd[0].node).
    """
    def __init__(self, id, animations):
        self.animations=animations
        self.id=id
        self.node=NodePath('CrowdActor_'+str(id))
        self.anim_data=Vec4(0.0, 1.0, 30.0, 0.0) #start_frame, num_frame, fps, time_offset
        self.seq=None
        self.time=globalClock.get_frame_time()

    def __getattr__(self,attr):
        """Delegate the function call to the internal NodePath
        """
        return self.node.__getattribute__(attr)

    def loop(self, name, fps=30.0, sync=True):
        """Play the 'name' animation in a loop at 'fps' frames per second speed.
        if sync is False the animation will start at a random frame
        """
        if self.seq:
            self.seq.finish()
            self.seq=None
        if sync:
            sync=0.0
        else:
            sync=random()
        self.time=sync-globalClock.get_frame_time()
        self.anim_data=Vec4(self.animations[name][0],
                            self.animations[name][1],
                            fps,
                            self.time)

    def play(self, name, fps=30.0, sync=True):
        """Play the 'name' animation ONCE at 'fps' frames per second speed.
        if sync is False the animation will start at a random frame
        """
        self.loop(name, fps, sync)
        time= float(self.animations[name][1])/float(fps)
        self.seq=Sequence(Wait(time), Func(self.stop))
        self.seq.start()

    def pose(self, frame_number):
        """Pause the playback on frame_number
        """
        self.anim_data=Vec4(frame_number, 1.0, 0.0, 0.0)

    def get_current_frame(self):
        """Returns the currently played frame (if a animation is playing/looping)
        """
        start_frame=self.anim_data[0]
        num_frame=self.anim_data[1]
        fps=self.anim_data[2]
        offset_time=self.anim_data[3]
        time=globalClock.get_frame_time()
        return int(start_frame + floor((time+offset_time)*fps)%num_frame)

    def stop(self):
        """Pause the playback, there's no 'resume' so the function name is not 'pause'
        """
        self.pose(self.get_current_frame())

    def __del__(self):
        """Clean up"""
        try:
            if self.seq:
                self.seq.finish()
            self.seq=None
            self.node.remove_node()
        except:
            pass
