from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
import json

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        model = "m_rocket1.egg"
        anim="rocket.pfm"
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

        self.actor.set_instance_count(20)
        self.actor.node().set_bounds(OmniBoundingVolume())
        self.actor.node().set_final(True)

        tex=Texture()
        pfm=PfmFile()
        pfm.read(anim)
        tex.load(pfm)
        tex.setWrapU(SamplerState.WM_clamp)
        tex.setWrapV(SamplerState.WM_clamp)
        tex.setMagfilter(SamplerState.FT_nearest)
        tex.setMinfilter(SamplerState.FT_nearest)
        tex.setFormat(Texture.F_rgba32)

        fps=30.0
        start_frame=1.0
        num_frame=35.0
        offset_frame=0.0
        self.actor.set_shader_input('frame', Vec4(fps, start_frame, num_frame, offset_frame))
        self.actor.set_shader_input('animation', tex)

app = MyApp()
app.trackball.node().setPos(0, 50, -5)
app.run()
