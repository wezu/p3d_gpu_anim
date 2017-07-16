from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
import sys

class AnimSampler(ShowBase):
    def __init__(self, model):
        ShowBase.__init__(self)

        _model=loader.load_model(model)
        _anim_names=self._find_first_tag(_model, 'anim_names').replace('\n', ' ').split()
        #_anim_numbers=self._find_first_tag(self.actor, 'anim_range').replace('\n', ' ').split()
        #_anim_numbers=[[int(i) for i in j.split(":")] for j in _anim_numbers]
        _anim_source=self._find_first_tag(_model, 'anim_source').replace('\n', ' ').split()
        anim=dict(zip(_anim_names,_anim_source))
        #anim = {'walk':'a_rocket_walk1.egg',
        #        'kneel':'a_rocket_kneel.egg'}

        # Load the model.
        self.actor = Actor(model, anim)
        self.actor.reparent_to(render)

        self.save_pfm_as=self._find_first_tag(self.actor, 'anim_tex')
        self.joint_names=self._find_first_tag(self.actor, 'joint_names').replace('\n', ' ').split()

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
        print ('Sampling animation:', self.current_anim)
        self.current_frame=0
        self.joints=self.actor.getJoints()
        taskMgr.add(self.sample, "sample_task")

    def _find_first_tag(self, node, tag):
        for child in node.get_children():
            if child.has_tag(tag):
                return child.get_tag(tag)
            else:
                child_tag=self.find_tag(child, tag)
                if child_tag:
                    return child_tag
        return None
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
                #add padding, with frameblending it may sample outside the range
                for id, joint in enumerate(self.joints):
                    if joint.get_name() in self.joint_names:
                        joint_id=self.joint_names.index(joint.get_name())
                        vt = JointVertexTransform(joint)
                        mat = Mat4()
                        vt.get_matrix(mat)
                        for i in range(4):
                            self.pfm.setPoint4(joint_id,(self.current_frame*4)+i+offset,mat.get_row(i))
                #write
                self.pfm.write(self.save_pfm_as)
                print('All done!')
                sys.exit()
            else:
                self.current_anim=list(self.anim_dict)[self.current_anim_index]
                print ('Sampling animation:', self.current_anim)
                self.current_anim_length=self.actor.getNumFrames(self.current_anim)
                self.current_frame=0
        return task.again

if __name__ == "__main__":

    if len(sys.argv)>1:
        model = sys.argv[1]
    else:
        model = "gpu_rocket.egg"

    app = AnimSampler(model)
    app.run()
