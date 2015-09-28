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
L = 512
N = 250
r = 10
n = 0.4
v = 3.
fps = 50

def dist(p1, p2):
  return fabs(p1[0]-p2[0]) + fabs(p1[1]-p2[1])

def sign(v):
  return v/abs(v)

class bird:
  """Flies.
    
    """
  def __init__(self, pos, phi, speed):
    self.pos  = pos
    self.tail  = [ copy.deepcopy(self.pos) ]
    self.phi   = phi
    self.speed = speed
    self.color = [ 0, 0, 0 ]
    self.size  = 7

  def draw_head(self, screen):
    # head
    #pygame.draw.circle(screen, self.color, [ int(i) for i in self.pos ], .5)
    pass

  def draw_tail(self, screen):
    # tail (decreasing gradient)
    c = 1.
    l = len(self.tail)
    for i in range(l-1):
      if dist(self.tail[i], self.tail[i+1])>=L/2.: continue
      color = [ 255 - float(l-1-i)/float(l-1)*(255-c) for c in self.color ] 
      pygame.draw.line(screen, color, self.tail[i], self.tail[i+1])

  def move(self):
    self.pos = map(sum, zip(self.pos, [ self.speed*cos(self.phi), self.speed*sin(self.phi) ]))
    # periodic boundary conditions
    self.pos = [ i%L for i in self.pos ] 
       
    # grow tail
    self.tail.insert(0, copy.deepcopy( self.pos ))
    while len(self.tail)>self.size:
      self.tail.pop()

class flock:
  """Many of those things

    """
  def __init__(self, N, r, n):
    self.N = N
    self.r = r
    self.n = n
    # create birds
    self.birds = [ bird([ random.random()*L, random.random()*L ], 2*pi*random.random(), v) for i in range(self.N) ]

  def draw(self, screen):
    # just draw those birds
    for b in self.birds:
      b.draw_tail(screen)
      b.draw_head(screen)

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
    self.size = self.width, self.height = L, L
    self.screen = pygame.display.set_mode(self.size)
    self.bkg_color = (255, 255, 255)
    self.flock = flock(N, r, n)
    print "Press Esc to quit."

  def run(self):
    running = True
    time = 0

    while running:
      # ultimate time control
      self.clock.tick(fps)

      # keyboard
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        if event.type == pygame.KEYDOWN:
          # esc
          if event.key == pygame.K_ESCAPE:
            running = False
 
      # moving
      self.flock.move()

      # drawing
      self.screen.fill(self.bkg_color)
      self.flock.draw(self.screen)
      pygame.display.flip()

if __name__ == "__main__":
  app = game() 
  app.run()
