import os, sys
from fileinput import FileInput
import json
model_file='m_box.egg'

#first run, get the joint names
joints=set()
with open(model_file, 'r') as f:
    for line in f:
        if line.strip().startswith('//'):
            joints.update(set([item.split(":")[0] for item in line.strip().split(' ') if ':' in item]))

#now we need an index for each joint
joints=list(joints)
#run #2 get membership and index
write_here=False
membership={}
with FileInput(model_file, inplace=True) as f:
        for line in f:
            if line.strip().startswith('//'):
                write_here=True
                membership.update({joints.index(key):float(value) for (key, value) in [item.split(":") for item in line.split(' ') if ':' in item]})
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

with open('m_box.json', 'w') as outfile:
    json.dump(joints, outfile)


