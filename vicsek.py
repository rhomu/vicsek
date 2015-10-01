################################################################################
#                                                                              #
# Copyright (c) 2014 Romain Mueller                                            #
#                                                                              #
# Distributed under the GNU GPL v2. For full terms see the file LICENSE.       #
#                                                                              #
################################################################################

import pygame, copy, random
from math import pi, cos, sin, atan2, fabs

# some constants
def dist(p1, p2):
  return fabs(p1[0]-p2[0]) + fabs(p1[1]-p2[1])

def sign(v):
  return v/abs(v)

class bird:
  """Flies.
    
    """
  def __init__(self, app, pos, phi, speed):
    self.pos  = pos
    self.tail  = [ copy.deepcopy(self.pos) ]
    self.phi   = phi
    self.speed = speed
    self.color = [ 0, 0, 0 ]
    self.size  = 7
    self.app = app

  def draw_tail(self, screen):
    # tail (decreasing gradient)
    c = 1.
    l = len(self.tail)
    for i in range(l-1):
      if ( abs( self.tail[i][0] - self.tail[i+1][0] )>=app.width/2. or 
           abs( self.tail[i][1] - self.tail[i+1][1] )>=app.height/2. 
         ):
        continue
      color = [ 255 - float(l-1-i)/float(l-1)*(255-c) for c in self.color ] 
      pygame.draw.line(screen, color, self.tail[i], self.tail[i+1])

  def move(self):
    self.pos = map(sum, zip(self.pos, [ self.speed*cos(self.phi), self.speed*sin(self.phi) ]))
    # periodic boundary conditions
    self.pos = [ self.pos[0]%app.width, self.pos[1]%app.height ] 
       
    # grow tail
    self.tail.insert(0, copy.deepcopy( self.pos ))
    while len(self.tail)>self.size:
      self.tail.pop()

class flock:
  """Many of those things

    """
  def __init__(self, app, N, r, n, speed):
    self.N = N
    self.r = r
    self.n = n
    self.app = app
    self.speed = speed
    self.draw_circles = False
    # create birds
    self.birds = [ bird(self.app, 
                        [ random.random()*app.width, random.random()*app.height ], 
                        2*pi*random.random(), 
                        self.speed
                       ) for i in range(self.N) ]

  def add_bird(self):
    self.birds.append( bird(self.app, [ random.random()*app.width, random.random()*app.height ], 2*pi*random.random(), self.speed) )
    self.N = self.N+1

  def kill_bird(self):
    if self.birds != []:
      self.birds.pop( int( random.random()*len(self.birds) ) )
    self.N = self.N-1

  def set_temp(self, n):
    self.n = n
    for b in self.birds:
      b.n = n

  def draw(self, screen):
    # just draw those birds
    for b in self.birds:
      b.draw_tail(screen)
      # draw circle of radius r around the bird
      if self.draw_circles:
        pygame.draw.circle(screen, b.color, [ int(i) for i in b.pos ], self.r, 1)

  def move(self):
    # update the angles
    for b in self.birds:
      sin_tot = 0.
      cos_tot = 0.
      counter = 0
      for bb in self.birds:
        if dist(b.pos, bb.pos)<self.r:
          sin_tot += sin(bb.phi)
          cos_tot += cos(bb.phi)
          counter += 1
      # update
      if counter>0:
        b.phi = atan2(sin_tot, cos_tot) + self.n/2.*(1-2.*random.random())

    # move them
    for b in self.birds:
      b.move()

class game:
  """Fly, baby, fly.

    """
  def __init__(self):
    pygame.init()
    self.clock = pygame.time.Clock()
    self.width, self.height = 512, 512
    self.screen = pygame.display.set_mode( (self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    self.bkg_color = (255, 255, 255)
    self.N = 250
    self.r = 10
    self.n = 0.5
    self.v = 3.
    self.fps = 30

    self.flock = flock(self, self.N, self.r, self.n, self.v)

    print "Controls:"
    print "  (w) add 10 birds"
    print "  (a) delete 10 birds"
    print "  (e) heat"
    print "  (s) cool"
    print "  (p) toggle drawing interaction circles"
    print "Press Esc to quit."

  def run(self):
    running = True
    time = 0

    while running:
      # ultimate time control
      self.clock.tick(self.fps)

      # events handler
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        # keyboard
        if event.type == pygame.KEYDOWN:
          # controls
          if event.key == pygame.K_w:
            for i in range(10):
              self.flock.add_bird()
          elif event.key == pygame.K_a:
            for i in range(10):
              self.flock.kill_bird()
          elif event.key == pygame.K_e:
            self.n = ( self.n + 0.1 ) % (4*pi)
            self.flock.set_temp(self.n)
          elif event.key == pygame.K_s:
            self.n = max( self.n - 0.1, 0. ) % (4*pi)
            self.flock.set_temp(self.n)
          elif event.key == pygame.K_p:
            self.flock.draw_circles = not self.flock.draw_circles
          # esc
          if event.key == pygame.K_ESCAPE:
            running = False
        # resize window
        if event.type == pygame.VIDEORESIZE:
          self.size = self.width, self.height = event.dict['size']
          self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
 
      # moving
      self.flock.move()

      # drawing
      self.screen.fill(self.bkg_color)
      self.flock.draw(self.screen)
      pygame.display.flip()

if __name__ == "__main__":
  app = game() 
  app.run()
