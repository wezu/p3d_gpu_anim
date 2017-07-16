from direct.actor.Actor import Actor
from panda3d.core import *
from direct.showbase.Loader import Loader
from shutil import copyfile
import os, sys
from fileinput import FileInput

from sample_anim import AnimSampler

###### Setup here! ######
model_file = 'm_rocket.egg'
output_file = 'gpu_rocket.egg'
output_pfm ='rocket_anim.pfm'
write_data_to_egg_group = '<Group> character {'
bam_file_name = 'gpu_rocket.bam'
animations = {'walk':'a_rocket_walk1.egg',
            'kneel':'a_rocket_kneel.egg'}
###### Setup here! ######


#first run, get the joint names
print('Creating joint list...')
joint_names=set()
with open(model_file, 'r') as f:
    for line in f:
        if line.strip().startswith('//'):
            joint_names.update(set([item.split(":")[0] for item in line.strip().split(' ') if ':' in item]))

#now we need an index for each joint
joint_names=list(joint_names)

#Sample the animations
print('Looking up actor information...')
actor=Actor(model_file, animations)
joints=actor.getJoints()
num_joint=len(joints)
total_frames=1
anim_dict={}
for anim_name in animations:
    num_frames=actor.getNumFrames(anim_name)
    anim_dict[anim_name]=[total_frames, num_frames-1]
    total_frames+=num_frames
##Process the egg

#should we work on a copy?
if model_file != output_file:
    print('Creating egg file copy...')
    copyfile(model_file, output_file)
    model_file=output_file

#run #2 get membership and index
print('Writing vertex attributes...')
write_here=False
membership={}
with FileInput(model_file, inplace=True) as f:
        for line in f:
            if line.strip().startswith(write_data_to_egg_group) and write_data_to_egg_group:
                print(line, end = '')
                print('  <Tag> joint_names {{ {} }}'.format(' '.join(joint_names)))
                print('  <Tag> anim_tex {{ {} }}'.format(output_pfm))
                print('  <Tag> anim_names {{ {} }}'.format(' '.join(anim_dict)))
                print('  <Tag> anim_range {{ {} }}'.format( ' '.join([':'.join([str(n) for n in i]) for i in anim_dict.values()]) ) )
                print('  <Tag> anim_source {{ {} }}'.format(' '.join([animations[i] for i in anim_dict])))
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

if bam_file_name:
    print('Writing bam file...')
    loader=Loader(None)
    egg=loader.load_model(model_file)
    egg.write_bam_file(bam_file_name)
    output_file=bam_file_name

if output_pfm:
    print('Starting animation sampling...')
    app=AnimSampler(output_file)
    app.run()
