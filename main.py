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

        #custom camera driver, not important for the demo
        base.disable_mouse()
        self.cc=CameraControler(pos=(0,0,50.0), offset=(0, 250, 250), speed=1.0, zoom_speed=10.0)

        #add some light
        spot = Spotlight("spot")
        spot.set_color((1.0, 1.0, 0.85, 1))
        spot.set_exponent(16)
        spot.get_lens().set_near_far(5, 400)
        spot.get_lens().set_fov(70)
        #spot.show_frustum()
        spot_path = render.attach_new_node(spot)
        spot_path.set_pos(-80, -80, 180)
        spot_path.look_at(Point3(20, 30, 40))
        render.set_shader_input('spot',spot_path)

        #add instractions in the 'good' old p3d sample way ;)
        addInstructions(0.06, "[W][A][S][D] or [mouse3] to move the camera, [mouse1] to rotate, [mouse_wheel] to zoom ")
        addInstructions(0.12, "[1]-[9] to make a row of characters play 'walk' once in sync")
        addInstructions(0.18, "[0] to make the first row of characters loop 'walk' out of sync")
        addInstructions(0.24, "[SPACE] to make them all move")
        addInstructions(0.30, "[TAB] to turn inter frame blending on/off")

        #make the crowd
        self.crowd=Crowd(model="gpu_rocket.bam", num_actors=50)

        #reparent the crowd to render
        self.crowd.reparent_to(render)

        #pose all the CrowdActors, else they might explode
        for actor in self.crowd:
            actor.pose(1)

        #put the actors in 10 rows of 5
        #...in a very stupid way
        i=0
        for x in range(5):
            for y in range(10):
                self.crowd[i].set_pos(x*30,y*40, 0)
                i+=1

        #key binding
        #1-9 (and 0) for playing the walk anim for each row
        for i in range(10):
            self.accept(str(i), self.play_for_row, [i])
        #space for playing the anim on all actors
        self.accept('space', self.play_all)
        #tab to flip inter frame blending
        self.accept('tab', self.flip_frameblend)

    def flip_frameblend(self):
        self.crowd.set_frame_blend(not self.crowd.frame_blend)

    def play_all(self):
        for actor in self.crowd:
            actor.set_h(random.randint(0, 360))
            actor.loop('kneel', random.randrange(30, 60), False)


    def play_for_row(self, id):
        for i, actor in enumerate(self.crowd):
            if i%10==id:
                if id == 0:
                    actor.set_h(0)
                    actor.loop('walk', 30.0, False)
                else:
                    actor.set_h(0)
                    actor.play('walk', 30.0, True)

app = MyApp()
app.run()
