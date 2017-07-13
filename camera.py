from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

__all__ = ['CameraControler']

class CameraControler (DirectObject):
    def __init__(self, pos=(0,0,3.0), offset=(0, 12, 12), speed=1.0, zoom_speed=1.0):
        self.node  = render.attach_new_node("node")
        self.node.set_pos(pos)
        self.gimbal  = self.node.attach_new_node("gimbal")
        base.camera.set_pos(render, offset)
        base.camera.look_at(self.node)
        base.camera.wrt_reparent_to(self.gimbal)

        self.initial_pos=pos
        self.initial_offset=offset

        self.last_mouse_pos=Vec2(0,0)
        self.speed=speed*600.0
        self.move_speed=100.0*speed
        self.zoom_speed=zoom_speed*5.0
        self.zoom = 0.0
        self.last_delta=Point2(0,0)
        self.limits=[8.0, 350.0]

        self.key_map = {'rotate': False, 'forward':False, 'back':False, 'left':False, 'right':False, 'move':False}
        taskMgr.add(self.update, "camcon_update")

        self.bind_keys()

    def bind_keys(self):
        self.ignoreAll()
        self.accept('mouse3', self.key_map.__setitem__, ['move', True])
        self.accept('mouse3-up', self.key_map.__setitem__, ['move', False])
        self.accept('mouse1', self.key_map.__setitem__, ['rotate', True])
        self.accept('mouse1-up', self.key_map.__setitem__, ['rotate', False])
        self.accept('wheel_up', self.zoom_control,[1.0])
        self.accept('wheel_down',self.zoom_control,[-1.0])

        self.accept('a', self.key_map.__setitem__, ['left', True])
        self.accept('a-up', self.key_map.__setitem__, ['left', False])
        self.accept('d', self.key_map.__setitem__, ['right', True])
        self.accept('d-up', self.key_map.__setitem__, ['right', False])
        self.accept('w', self.key_map.__setitem__, ['forward', True])
        self.accept('w-up', self.key_map.__setitem__, ['forward', False])
        self.accept('s', self.key_map.__setitem__, ['back', True])
        self.accept('s-up', self.key_map.__setitem__, ['back', False])


    def reset(self):
        self.node.set_pos(self.initial_pos)
        self.node.set_hpr(0,0,0)
        self.gimbal.set_hpr(0,0,0)
        base.camera.set_pos(render, self.initial_offset)
        base.camera.look_at(self.node)

    def set_speed(self, speed):
        self.speed=speed*6000.0

    def set_zoom_speed(self, speed):
        self.zoom_speed=speed*5.0

    def zoom_control(self, amount):
        self.zoom+=amount*self.zoom_speed
        self.zoom=min(max(self.zoom, -6.0*self.zoom_speed), 6.0*self.zoom_speed)

    def update(self, task):
        dt = globalClock.getDt()
        if self.key_map['forward']:
            self.node.set_y(self.node,-self.move_speed*dt)
        elif self.key_map['back']:
            self.node.set_y(self.node,self.move_speed*dt)
        if self.key_map['left']:
            self.node.set_x(self.node,self.move_speed*dt)
        elif self.key_map['right']:
            self.node.set_x(self.node,-self.move_speed*dt)

        if base.mouseWatcherNode.has_mouse():
            if self.zoom != 0.0:
                distance=base.camera.get_distance(self.node)
                if (distance > self.limits[0] and self.zoom >0.0) or (distance < self.limits[1] and self.zoom < 0.0):
                    zoom_speed=self.zoom*dt
                    base.camera.set_y(base.camera, zoom_speed)
                    zoom_speed*=4.0
                    if self.zoom > 0.1:
                        self.zoom-=zoom_speed
                    elif self.zoom < -0.1:
                        self.zoom-=zoom_speed
                    else:
                        self.zoom=0.0
            m_pos=base.mouseWatcherNode.get_mouse()
            delta = m_pos- self.last_mouse_pos
            self.last_mouse_pos = Vec2(m_pos)
            if not self.key_map['rotate'] and not self.key_map['move']:
                delta=self.last_delta*0.9
                if abs(delta[0])<0.001:
                    delta[0]=0
                if abs(delta[1])<0.001:
                    delta[1]=0
            self.last_delta=delta
                #print(delta)
            if self.key_map['rotate']:
                p=self.gimbal.get_p()- delta[1]*self.speed*0.5
                self.gimbal.set_p(min(max(p, -40.0), 40.0))
                self.node.set_h(self.node.get_h()- delta[0]*self.speed)
            if self.key_map['move']:
                self.node.set_y(self.node,delta[1]*self.move_speed*10.0)
                self.node.set_x(self.node,delta[0]*self.move_speed*10.0)

        return task.again
