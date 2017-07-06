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
        self.actor = Actor(model, {"walk": anim})
        self.actor.reparent_to(self.render)
        #self.actor.setBlend(frameBlend = True)
        #self.actor.loop("walk")

        ## Load the shader to perform the skinning.
        ## Also tell Panda that the shader will do the skinning, so
        ## that it won't transform the vertices on the CPU.
        attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, "anim_v.glsl", "anim_f.glsl"))
        attr = attr.set_flag(ShaderAttrib.F_hardware_skinning, True)
        self.actor.set_attrib(attr)

        #self.debug_model(self.actor)

        with open('m_rocket.json') as data_file:
            self.joint_names=json.load(data_file)

        self.pfm=PfmFile()
        self.pfm.clear(x_size=128, y_size=1024, num_channels=4)

        self.current_frame=0
        self.anim=[]

        self.joints=self.actor.getJoints()

        self.doMethodLater(self.fps, self.sample, 'sample_tsk')

    def playback(self, task):
        print('playback at',self.current_frame )
        for id, joint in enumerate(self.joints):
            self.actor.freezeJoint("modelRoot", joint.get_name(), transform =  self.anim[self.current_frame][id])
        self.current_frame+=1
        if self.current_frame > self.actor.getNumFrames('walk'):
            self.current_frame=1

        return task.again

    def sample(self, task):
        print('sample at',self.current_frame )
        self.actor.pose("walk", self.current_frame)

        anim={}
        for id, joint in enumerate(self.joints):
            #print(joint.get_name())
            ts=joint.get_transform_state()
            anim[id]=ts
            #pfm stuff
            if joint.get_name() in self.joint_names:
                joint_id=self.joint_names.index(joint.get_name())
                mat=ts.get_mat()
                for i in range(4):
                    self.pfm.setPoint4(joint_id, (self.current_frame*4)+i, mat.get_row(i))
            else:
                print ('Missing:',joint.get_name() )
        self.anim.append(anim)

        self.current_frame+=1
        if self.current_frame > self.actor.getNumFrames('walk'):
            print ('sampling done')
            self.current_frame=1 #the 0 frame is bad for this anim
            self.doMethodLater(self.fps, self.playback, 'playback_tsk')
            self.pfm.write('walk.pfm')
            return task.done
        return task.again

    def debug_model(self, actor):
        """
        [14:24] <rdb> wezu: GeomVertexData has a getTransformTable();
                    TransformTable has a getTransform(n), which returns
                    JointVertexTransform, which has getJoint()
        [14:24] <rdb> The n in getTransform(n) is the index, I think.
        """
        mesh=actor._Actor__geomNode
        #mesh.ls() returns:
        #PandaNode character S:(ShaderAttrib)
        #    Character __Actor_modelRoot
        #        GeomNode  (1 geoms: S:(TextureAttrib TransparencyAttrib))
        #so this is the 'real' geomNode
        geom_node = mesh.get_child(0).get_child(0).node()
        if geom_node.isGeomNode():
            for geom in geom_node.get_geoms():
                vdata = geom.get_vertex_data()

                '''anim_spec = GeomVertexAnimationSpec()
                anim_spec.set_hardware(4, True)
                format = GeomVertexFormat(vdata.get_format())
                format.set_animation(anim_spec)
                new_vdata = vdata.convert_to(GeomVertexFormat.register_format(format))''' #crash???

                table = vdata.get_transfom_table() #always returns None :(
                print (table)
                if table is not None:
                    for id, transform in enumerate(table.get_transforms()):
                        name = transform.get_joint.get_name()
                        print (f'joint {name} {id}')
                else:
                    print ("No transform table!")


app = MyApp()
app.trackball.node().setPos(0, 50, -5)
app.run()
