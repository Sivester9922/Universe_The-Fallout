import cProfile, pstats

import pygame
from pygame.locals import *

import paths
import gummworld2
from gummworld2 import Engine, State, View, SuperMap, MapHandler, TiledMap, Statf
from gummworld2 import context, data, toolkit, model, supermap


COLLAPSE_KEYS = range(K_1, K_9+1)



class App(Engine):
    
    def __init__(self):
        resolution = 800,600
#        resolution = 640,480
#        resolution = 800,600
        self.movex = 0
        self.movey = 0
        self.visible_tiles = {}
        
        # Init Engine, no map or world.
        Engine.__init__(self,
            resolution=resolution, #display_flags=DOUBLEBUF,
            camera_target=model.Object(),
            frame_speed=0,
        )
        # Create the supermap and world.
        make_supermap(self)
        self.camera.init_position(self.map.current.rect.center)
        
        # Show me da goods.
        toolkit.make_hud()
        State.hud.add('Current', Statf(State.hud.next_pos(),
            'Current Map %s', callback=lambda:'%s'%str(State.map.current.name), interval=.5))
        State.hud.add('Visible', Statf(State.hud.next_pos(),
            'Visible %s', callback=lambda:str(len(State.map.visible_maps)), interval=.5))
        State.hud.add('History', Statf(State.hud.next_pos(),
            'History %s', callback=lambda:'%s/%s'%(str(len(State.map.history)),str(State.map.max_maps)), interval=.5))
        State.hud.add('Collapse Level', Statf(State.hud.next_pos(),
            'Collapse %s', callback=lambda:'%s'%str(State.map.current.collapse_level), interval=.5))
        
        State.speed = 5

       
    
    def update(self, dt):
        if self.movex or self.movey:
            r = State.camera.rect.move(self.movex,self.movey)
            r.clamp_ip(State.map.rect)
            State.camera.position = r.center
        State.camera.update(dt)
        State.map.update(dt)
        State.hud.update(dt)
    
    def draw(self, dt):
        State.screen.clear()
        State.map.draw()
        State.hud.draw()
        State.screen.flip()
    
    def on_key_down(self, unicode, key, mod):
        if key == K_DOWN: self.movey += State.speed
        elif key == K_UP: self.movey += -State.speed
        elif key == K_RIGHT: self.movex += State.speed
        elif key == K_LEFT: self.movex += -State.speed
        elif key in (COLLAPSE_KEYS):
            clevel = key - K_0
            for mh in State.map.handlers.values():
                mh.collapse(clevel)
        elif key == K_ESCAPE: context.pop()
    
    def on_key_up(self, key, mod):
        if key == K_DOWN: self.movey -= State.speed
        elif key == K_UP: self.movey -= -State.speed
        elif key == K_RIGHT: self.movex -= State.speed
        elif key == K_LEFT: self.movex -= -State.speed
    
    def on_quit(self):
        context.pop()


class TiledMapHandler(MapHandler):
    
    # 4 gives better FPS at resolution 320x320, but can cause loading hiccups
    # 2 gives smoothest loading, highest cache hits
    collapse_level = (4,4)
    
    def load(self):
        self.map = TiledMap(
            data.filepath('map',self.map_file), collapse=self.collapse_level)
    
    def collapse(self, clevel):
        if clevel > (1,1):
            self.collapse_level = clevel
            # self.map could be None if the map isn't loaded or has been
            # unloaded.
            if self.map:
                self.map.collapse(clevel)


def make_supermap(app):
    # Make a 9x9 supermap, using the same map file for each.
    #map_filename = 'Gumm multi layer.tmx'
    map_filename = 'Gumm super desert.tmx'
    app.map = State.map = SuperMap()
    for n in ((0,0),) + supermap.NEIGHBORS:
        app.map.add_handler(TiledMapHandler(n, map_filename))
    app.world = State.world = model.NoWorld(app.map.rect)


def main():
    app = App()
    gummworld2.run(app)


if __name__ == '__main__':
    if False:
        cProfile.run('main()', 'prof.dat')
        p = pstats.Stats('prof.dat')
        p.sort_stats('time').print_stats()
    else:
        main()
