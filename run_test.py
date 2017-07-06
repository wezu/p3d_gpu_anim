from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
import json

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        model = "m_rocket1.egg"
        anim = "a_rocket_walk1.egg"
        self.fps=1.0/30.0

        # Load the model.
        self.actor=loader.load_model(model)
        #self.actor = Actor(model, {"walk": anim})
        self.actor.reparent_to(self.render)
        #self.actor.setBlend(frameBlend = True)
        #self.actor.loop("walk")

        ## Load the shader to perform the skinning.
        ## Also tell Panda that the shader will do the skinning, so
        ## that it won't transform the vertices on the CPU.
        shader=Shader.load(Shader.SLGLSL, "anim1_v.glsl", "anim_f.glsl")
        attr = ShaderAttrib.make(shader)
        #attr = attr.set_flag(ShaderAttrib.F_hardware_skinning, True)
        self.actor.set_attrib(attr)

        tex=Texture()
        pfm=PfmFile()
        pfm.read('walk.pfm')
        tex.load(pfm)
        tex.setWrapU(SamplerState.WM_clamp)
        tex.setWrapV(SamplerState.WM_clamp)
        tex.setMagfilter(SamplerState.FT_nearest)
        tex.setMinfilter(SamplerState.FT_nearest)
        tex.setFormat(Texture.F_rgba32)

        self.actor.set_shader_input('animation', tex)
        self.actor.set_shader_input('frame', 0.0)

app = MyApp()
app.trackball.node().setPos(0, 50, -5)
app.run()
