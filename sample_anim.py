from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
import json
import sys

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        model = "gpu_rocket.egg"
        anim = {'walk':'a_rocket_walk1.egg',
                'kneel':'a_rocket_kneel.egg'}
        self.save_pfm_as='rocket_anim.pfm'


        # Load the model.
        self.actor = Actor(model, anim)
        self.actor.reparent_to(render)

        tag=self.actor.get_child(0).get_tag('joint_names')
        self.joint_names=json.loads(tag.replace('\n', '"'))

        num_joint=len(self.actor.getJoints())
        total_frames=0
        self.anim_dict={}
        for anim_name in anim:
            num_frames=self.actor.getNumFrames(anim_name)
            self.anim_dict[anim_name]=[total_frames, num_frames]
            total_frames+=num_frames
        #make the pfm file, add a bit of padding to get power-of-2 size
        self.pfm=PfmFile()
        x_size=2**(num_joint-1).bit_length()
        y_size=2**((total_frames*4)-1).bit_length()
        self.pfm.clear(x_size=x_size, y_size=y_size, num_channels=4)

        self.current_anim=list(self.anim_dict)[0]
        self.current_anim_index=0
        self.last_anim_length=0
        self.current_anim_length=self.actor.getNumFrames(self.current_anim)
        self.current_frame=0
        self.joints=self.actor.getJoints()
        taskMgr.add(self.sample, "sample_task")


    def sample(self, task):
        self.actor.pose(self.current_anim, self.current_frame)
        offset=self.current_anim_index*self.last_anim_length*4

        for id, joint in enumerate(self.joints):
            if joint.get_name() in self.joint_names:
                joint_id=self.joint_names.index(joint.get_name())
                vt = JointVertexTransform(joint)
                mat = Mat4()
                vt.get_matrix(mat)
                for i in range(4):
                    self.pfm.setPoint4(joint_id,(self.current_frame*4)+i+offset,mat.get_row(i))

        self.current_frame+=1
        if self.current_frame > self.current_anim_length:
            self.last_anim_length=self.current_anim_length
            self.current_anim_index+=1
            if self.current_anim_index >= len(self.anim_dict):
                self.pfm.write(self.save_pfm_as)
                print('all done')
                sys.exit()
            else:
                self.current_anim=list(self.anim_dict)[self.current_anim_index]
                self.current_anim_length=self.actor.getNumFrames(self.current_anim)
                self.current_frame=0
        return task.again


app = MyApp()
app.run()
