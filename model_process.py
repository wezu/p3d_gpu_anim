from direct.actor.Actor import Actor
from panda3d.core import *
from shutil import copyfile
import os, sys
from fileinput import FileInput
import json

model_file='m_rocket.egg'
output_file='gpu_rocket.egg'
output_pfm='rocket1.pfm'
write_data_to_egg_group = '<Group> character {'
animations={'walk':'a_rocket_walk1.egg',
            'kneel':'a_rocket_kneel.egg'}


#first run, get the joint names
joint_names=set()
with open(model_file, 'r') as f:
    for line in f:
        if line.strip().startswith('//'):
            joint_names.update(set([item.split(":")[0] for item in line.strip().split(' ') if ':' in item]))

#now we need an index for each joint
joint_names=list(joint_names)

#Sample the animations
actor=Actor(model_file, animations)
joints=actor.getJoints()
num_joint=len(joints)
total_frames=0
anim_dict={}
for anim_name in animations:
    num_frames=actor.getNumFrames(anim_name)
    anim_dict[anim_name]=[total_frames, num_frames]
    total_frames+=num_frames
#make the pfm file, add a bit of padding to get power-of-2 size
pfm=PfmFile()
x_size=2**(num_joint-1).bit_length()
y_size=2**((total_frames*4)-1).bit_length()
pfm.clear(x_size=x_size, y_size=y_size, num_channels=4)

#I think you need to be rendering to make this work, run sample_anim.py
'''for offset, anim_name in enumerate(animations):
    frames_in_anim=actor.getNumFrames(anim_name)
    for current_frame in range(frames_in_anim):
        actor.pose(anim_name, current_frame)

        for joint in joints:
            if joint.get_name() in joint_names:
                joint_id=joint_names.index(joint.get_name())
                vt = JointVertexTransform(joint)
                mat = Mat4()
                vt.get_matrix(mat)
                for i in range(4):
                    pfm.set_point4(joint_id, (current_frame*4)+i+offset*frames_in_anim, mat.get_row(i))
#write the pfm
pfm.write(output_pfm)'''

##Process the egg

#should we work on a copy?
if model_file != output_file:
    copyfile(model_file, output_file)
    model_file=output_file

#run #2 get membership and index
write_here=False
membership={}
with FileInput(model_file, inplace=True) as f:
        for line in f:
            if line.strip().startswith(write_data_to_egg_group) and write_data_to_egg_group:
                print(line, end = '')
                print('  <Tag> joint_names {{ {} }}'.format(json.dumps(joint_names)))
                print('  <Tag> anim_tex {{ {} }}'.format(output_pfm))
                print('  <Tag> anim_names {{ {} }}'.format(json.dumps(list(anim_dict))))
                print('  <Tag> anim_range {{ {} }}'.format(json.dumps(list(anim_dict.values()))))
            elif line.strip().startswith('//'):
                write_here=True
                membership.update({joint_names.index(key):float(value) for (key, value) in [item.split(":") for item in line.split(' ') if ':' in item]})
                print(line, end = '')
            elif write_here:
                write_here = False
                #get 4 most inportant joints
                final_membership=sorted(membership.items(), reverse=True)
                joint=[]
                weight=[]
                for index, value in sorted(membership.items(), reverse=True):
                    joint.append(index)
                    weight.append(value)
                #we need 4 of each
                while len(weight)<4:
                    joint.append(0)
                    weight.append(0)
                weight=weight[:4]
                #sum of weights should be == 1.0
                f=1.0/sum(weight)
                for i, v in enumerate(weight):
                    weight[i]=v*f
                print('        <Aux> joint {{ {0} {1} {2} {3} }}'.format(*joint))
                print('        <Aux> weight {{ {0} {1} {2} {3} }}'.format(*weight))
                print('      }')
            else:
                print(line, end = '')
                write_here = False
                membership = {}



