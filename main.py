from panda3d.core import *
loadPrcFileData("", "show-frame-rate-meter 1")
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
import random

from crowd import Crowd
from camera import *

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.disable_mouse()
        self.cc=CameraControler(pos=(0,0,50.0), offset=(0, 250, 250), speed=1.0, zoom_speed=10.0)

        model = loader.load_model("m_rocket1.egg")
        model.reparent_to(render)
        pfm=PfmFile()
        pfm.read("rocket.pfm")
        anim_texture=Texture()
        anim_texture.load(pfm)

        addInstructions(0.06, "WASD or mouse1 to move the camera, mouse3 to rotate")
        addInstructions(0.12, "1-9 to make a row of characters play 'walk' once in sync")
        addInstructions(0.18, "0 to make the first row of characters loop 'walk' out of sync")


        self.crowd=Crowd(model=model,
                        anim_texture=anim_texture,
                        animations={'walk':[1, 34]},
                        num_actors=50,
                        frame_blend=False)#set to True for a big slowdown

        for actor in self.crowd:
            actor.pose(1)

        #hack, because else I'm to stupid to make 10 rows of 5 models, ignore pls
        crowd_iterator=iter(self.crowd)
        for x in range(5):
            for y in range(10):
                crowd_iterator.__next__().set_pos(x*30,y*40, 0)

        for i in range(10):
            self.accept(str(i), self.play_for_row, [i])


    def play_for_row(self, id):
        for i, actor in enumerate(self.crowd):
            if i%10==id:
                if id == 0:
                    actor.loop('walk', 30.0, False)
                else:
                    actor.play('walk', 30.0, True)

app = MyApp()
app.run()
