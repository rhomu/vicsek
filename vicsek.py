################################################################################
#                                                                              #
# Copyright (c) 2014 Romain Mueller                                            #
#                                                                              #
# Distributed under the GNU GPL v2. For full terms see the file LICENSE.       #
#                                                                              #
################################################################################

import pygame, copy, random, time, datetime
from math import pi, cos, sin, atan2, fabs, floor, ceil, sqrt

# wrapping distance
def dist(p1, p2):
  return sqrt(fabs(p1[0]-p2[0])**2 + fabs(p1[1]-p2[1])**2)

def sign(v):
  return v/abs(v)

class bucket_grid:
  """Fixed radius nearest neighbour search using a grid of buckets of size r.
     Width and height are needed to wrap around (periodic boundary conditions).
    """
  def __init__(self, points, width, height, n, m):
    self.width = width
    self.height = height
    self.n = n
    self.m = m
    # here are your buckets (dict)
    self.buckets = {}
    # put all points into them
    for p in points:
      self.buckets.setdefault(self.get_index(p), []).append(p)

  def get_index(self, p):
    return ( int(floor(p[0]/self.width*self.n)), int(floor(p[1]/self.height*self.m)) )

  def neighbours(self, p, r):
    # position of the central bucket
    i, j = self.get_index(p)
    # this is the number of adjacent buckets we need to check
    cx = int(ceil(float(r)/self.width*self.n))
    cy = int(ceil(float(r)/self.height*self.m))
    neighbours = []
    # check all neighbouring buckets
    for a in range(-cx, 1+cx):
      for b in range(-cy, 1+cy):
        # add points
        neighbours += filter(
          lambda q: dist(p, q) < r,
          self.buckets.setdefault( ( (i+a)%self.n, (j+b)%self.m ), [])
          )
    return neighbours

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

  def __getitem__(self, index):
    """Return position
      """
    return self.pos[index]

  def draw_tail(self, screen):
    # tail (decreasing gradient)
    c = 1.
    l = len(self.tail)
    for i in range(l-1):
      if ( 
           abs( self.tail[i][0] - self.tail[i+1][0] )>=app.width/2. or 
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
    # create the buckets
    grid = bucket_grid(self.birds, self.app.width, self.app.height, self.app.width/self.r, self.app.height/self.r)
    # update the angles
    for b in self.birds:
      sin_tot = 0.
      cos_tot = 0.
      counter = 0
      # loop over neighbours
      neighbours = grid.neighbours(b, self.r)
      for n in neighbours:
          sin_tot += sin(n.phi)
          cos_tot += cos(n.phi)
      counter = len(neighbours)
      # update
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
    print "  (l) save screenshot to file"
    print "Press Esc to quit."

  def run(self):
    running = True

    while running:
      # ultimate time control
      self.clock.tick(self.fps)

      # events handler
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        # keyboard
        if event.type == pygame.KEYDOWN:
          # add birds
          if event.key == pygame.K_w:
            for i in range(10):
              self.flock.add_bird()
          # kill birds
          elif event.key == pygame.K_a:
            for i in range(10):
              self.flock.kill_bird()
          # heat
          elif event.key == pygame.K_e:
            self.n = ( self.n + 0.1 ) % (4*pi)
            self.flock.set_temp(self.n)
          # cool
          elif event.key == pygame.K_s:
            self.n = max( self.n - 0.1, 0. ) % (4*pi)
            self.flock.set_temp(self.n)
          # draw circles
          elif event.key == pygame.K_p:
            self.flock.draw_circles = not self.flock.draw_circles
          # screenshot
          elif event.key == pygame.K_l:
            stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d.%H%M%S')
            pygame.image.save(self.screen, "screenshot"+stamp+".jpeg")
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


def test_bucket():
  """Small test function of the bucket grid
    """
  import matplotlib.pyplot as plt
  points = [ ( random.random()*512, random.random()*512 ) for i in range(400) ]
  bnn = bucket_grid(points, 512, 512, 10, 10)
  neighbours = bnn.neighbours(points[0], 10)

  print points[0]
  print neighbours

  fig = plt.figure()
  ax = fig.add_subplot(111, aspect='equal')
  plt.plot([ points[0][0] ], [ points[0][1] ], 'r^')
  circ = plt.Circle(points[0], 10, fill=False)
  ax.add_patch(circ)

  for p in points[1:]:
    if p in neighbours:
      style = 'ro'
    else:
      style = 'bo'
    plt.plot([ p[0] ], [ p[1] ], style)

  plt.xlim(0, 512)
  plt.ylim(0, 512)
  plt.show()


if __name__ == "__main__":
  app = game() 
  app.run()
