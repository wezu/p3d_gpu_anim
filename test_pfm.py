from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
import json

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        model = "smiley"

        # Load the model.
        self.actor=loader.load_model(model)
        #self.actor = Actor(model, {"walk": anim})
        self.actor.reparent_to(self.render)
        dummy=self.actor.copy_to(render)
        #dummy.set_pos(2,0,0)
        #self.actor.setBlend(frameBlend = True)
        #self.actor.loop("walk")

        ## Load the shader to perform the skinning.
        ## Also tell Panda that the shader will do the skinning, so
        ## that it won't transform the vertices on the CPU.
        shader=Shader.load(Shader.SLGLSL, "test_v.glsl", "anim_f.glsl")
        attr = ShaderAttrib.make(shader)
        #attr = attr.set_flag(ShaderAttrib.F_hardware_skinning, True)
        self.actor.set_attrib(attr)

        tex=Texture()
        pfm=PfmFile()
        pfm.clear(x_size=8, y_size=8, num_channels=4)
        n=render.attach_new_node('n')
        n.set_pos(1, 2, 4)
        n.set_hpr(90, 0, 0)
        n.set_scale(2.0)
        pfm.setPoint4(0, 0, Point4(0,0,1,0))
        for i in range(4):
            pfm.setPoint4(0, i, n.get_mat().get_row(i))
        tex.load(pfm)
        tex.setWrapU(SamplerState.WM_clamp)
        tex.setWrapV(SamplerState.WM_clamp)
        tex.setMagfilter(SamplerState.FT_nearest)
        tex.setMinfilter(SamplerState.FT_nearest)
        tex.setFormat(Texture.F_rgba32)

        self.actor.set_shader_input('pfm', tex)

app = MyApp()
app.trackball.node().setPos(0, 50, -5)
app.run()
