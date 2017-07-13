from panda3d.core import *
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func, Wait
import random
from math import floor

class CrowdActor(object):
    def __init__(self, id, animations):
        self.animations=animations
        self.id=id
        self.node=NodePath('CrowdActor_'+str(id))

        self.anim_data=Vec4(0.0, 1.0, 30.0, 0.0) #start_frame, num_frame, fps, time_offset
        self.seq=None
        self.time=globalClock.get_frame_time()


    def __getattr__(self,attr):
        return self.node.__getattribute__(attr)

    def loop(self, name, fps=30.0, sync=True) :
        if self.seq:
            self.seq.finish()
            self.seq=None
        if sync:
            sync=0.0
        else:
            sync=random.random()
        self.time=sync-globalClock.get_frame_time()
        self.anim_data=Vec4(self.animations[name][0],
                            self.animations[name][1],
                            fps,
                            self.time)

    def play(self, name, fps=30.0, sync=True):
        self.loop(name, fps, sync)
        time= float(self.animations[name][1])/float(fps)
        self.seq=Sequence(Wait(time), Func(self.stop))
        self.seq.start()

    def pose(self, frame_number):
        self.anim_data=Vec4(frame_number, 1.0, 0.0, 0.0)

    def stop(self):
        start_frame=self.anim_data[0]
        num_frame=self.anim_data[1]
        fps=self.anim_data[2]
        offset_time=self.anim_data[3]
        time=globalClock.get_frame_time()
        current_frame=int(start_frame + floor((time+offset_time)*fps)%num_frame)

        self.pose(current_frame)




class Crowd(object):
    def __init__(self, model, anim_texture, animations, num_actors, frame_blend=False):
        #load the model, instance it and set omni bounds
        self.model=model
        self.model.set_instance_count(num_actors)
        self.model.node().set_bounds(OmniBoundingVolume())
        self.model.node().set_final(True)
        #set the shader
        self.shader_cache={}
        shader_define={'NUM_ACTORS':num_actors}
        if frame_blend:
            shader_define['FRAME_BLEND']=1
        self.model.set_shader(self._load_shader(v_shader='shaders/anim_v.glsl',
                                                f_shader='shaders/anim_f.glsl',
                                                define=shader_define))

        #make sure the animation texture is set up right
        self.anim_texture=anim_texture
        self.anim_texture.set_wrap_u(SamplerState.WM_clamp)
        self.anim_texture.set_wrap_v(SamplerState.WM_clamp)
        self.anim_texture.set_magfilter(SamplerState.FT_nearest)
        self.anim_texture.set_minfilter(SamplerState.FT_nearest)
        self.anim_texture.set_format(Texture.F_rgba32)
        #send it to the shader
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
        self.animations=animations

        #list of actor nodes, so one can use crowd[12].play('some_anim')
        self.actors=[CrowdActor(i, animations) for i in range(num_actors)]

        taskMgr.add(self._update, "crowd_update", sort=-50)

    def _update(self, task):
        for n, actor in enumerate(self.actors):
            self.matrix_data.set_element(n, actor.node.get_mat())
            self.anim_data.set_element(n, actor.anim_data)
        return task.again

    def _load_shader(self, v_shader, f_shader, define=None, version='#version 130'):
        # check if we already have a shader like that
        if (v_shader, f_shader, str(define)) in self.shader_cache:
            return self.shader_cache[(v_shader, f_shader, str(define))]
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
        # store it
        self.shader_cache[(v_shader, f_shader, str(define))] = shader
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
