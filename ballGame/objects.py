import math

class Vector:
	def __init__(self, *args):
		'''
		Can be constructed from:
			magnitude, direction
			(x, y) [real coords]
			Vector
			[no parameters]
		'''
		constructed = False
		if len(args) > 1:
			if type(args[0]) in (int, float) and type(args[1]) in (int, float):
				self.mag = args[0]
				self.dir = args[1]
				constructed = True
		elif len(args) > 0:
			if type(args[0]) == Vector:
				v = args[0]
				self.mag = v.mag
				self.dir = v.dir
				constructed = True
			elif type(args[0]) == tuple:
				x = args[0][0]
				y = args[0][1]
				self.mag = math.sqrt(x**2 + y**2)
				if self.mag == 0:
					self.dir = 0
				else:
					if y > 0:
						self.dir = math.acos(x/self.mag)	# rearrangment of x() equation
					elif x < 0:
						self.dir = math.asin(-y/self.mag)+math.pi
					else:
						self.dir = math.asin(y/self.mag)	# rearrangment of x() equation
					self.normalizeDir()
				constructed = True
		else:
			self.mag = 0
			self.dir = 0
			constructed = True

		if not constructed:
			raise Exception("Invalid Vector constructor")

	def __add__(self, vector):
		return Vector((self.x + vector.x, self.y + vector.y))

	def __sub__(self, vector):
		return Vector((self.x - vector.x, self.y - vector.y))

	def __mul__(self, mult):
		if type(mult) == Vector:
			return (self.x * mult.x) + (self.y * mult.y)
		else:
			return Vector((self.x * mult, self.y * mult))

	def __rmul__(self, mult):
		return self.__mul__(mult)

	def __floordiv__(self, div):
		if type(div) == Vector:
			raise Exception("can't divide by vector yet")
		else:
			return Vector((self.x // div, self.y // div))

	def __truediv__(self, div):
		if type(div) == Vector:
			raise Exception("can't divide by vector yet")
		else:
			return Vector((self.x / div, self.y / div))

	def __pow__(self, ind):
		toReturn = Vector(self)
		for i in range(ind-1):
			toReturn *= self
		return toReturn

	@property
	def x(self):
		return math.cos(self.dir) * self.mag

	@property
	def y(self):
		return math.sin(self.dir) * self.mag

	def flipY(self):
		self.dir = 2*math.pi-self.dir
		self.normalizeDir()

	def drawEndPos(self):
		return Point(self.x, -self.y)

	def endPos(self):
		return Point(self.x, self.y)

	def rotate(self, angle):
		self.dir += angle
		# for the sake of readability, keep the angle between 0 <= a < 2pi
		self.normalizeDir()

	def normalizeDir(self):
		self.dir = self.dir % (2*math.pi)

	def unit(self):
		mag = self.mag
		mult = 1/mag
		return self * mult

	def __str__(self):
		return "Vector(mag={}, dir={})".format(self.mag, self.dir)


class Point:
	def __init__(self, *args):
		'''
		Can be constructed from:
			x, y
			(x, y)
			Point
			[no parameters]
		'''
		constructed = False
		if len(args) > 1:
			if type(args[0]) in (int, float) and type(args[1]) in (int, float):
				self.x = args[0]
				self.y = args[1]
				constructed = True
		elif len(args) > 0:
			if type(args[0]) == Point:
				p = args[0]
				self.x = p.x
				self.y = p.y
				constructed = True
			elif type(args[0]) == tuple:
				p = args[0]
				self.x = p[0]
				self.y = p[1]
				constructed = True
		else:
			self.x = 0
			self.y = 0
			constructed = True

		if not constructed:
			raise Exception("Invalid Point constructor")

	def translated(self, x, y):
		return Point(self.x+x, self.y+y)

	def __add__(self, p):
		return Point(self.x+p.x, self.y+p.y)

	def __sub__(self, p):
		return Point(self.x-p.x, self.y-p.y)

	def __mul__(self, m):
		return Point(self.x*m, self.y*m)

	def __floordiv__(self, div):
		if type(div) == Point:
			raise Exception("can't divide by point")
		else:
			return Point((self.x // div, self.y // div))

	def __truediv__(self, div):
		if type(div) == Vector:
			raise Exception("can't divide by point")
		else:
			return Point((self.x / div, self.y / div))

	def __eq__(self, p):
		if self.x == p.x and self.y == p.y:
			return True
		return False

	def __str__(self):
		return "Point(x={}, y={})".format(self.x, self.y)

	def distance(self, p):
		return math.sqrt((self.x-p.x)**2 + (self.y-p.y)**2)

	def pos(self):
		return (self.x, self.y)

	def int(self):
		return (int(self.x), int(self.y))

	def pygameToReal(self):
		return Point(self.x, -self.y)

	def realToPygame(self):
		return Point(self.x, -self.y)


class Ball:
	def __init__(self):
		self.velocity = Vector()
		self.pos = Point()
		self.mass = 0.75
		self.radius = 0.1
		self.cor = 0.8

	def accelerate(self, a):
		self.velocity += a

	def applyForce(self, f):
		# a = f/m
		self.accelerate(f/self.mass)

	def move(self, dt):
		self.pos += self.velocity.endPos()*dt

	def translate(self, v):
		self.pos += v.endPos()

	def setPos(self, p):
		self.pos = p

	def setVelocity(self, v):
		self.velocity = v

	def __eq__(self, p):
		if self.x == p.x and self.y == p.y:
			return True
		return False

	@property
	def bottom(self):
		return self.pos.y - self.radius

	@property
	def top(self):
		return self.pos.y + self.radius

	@property
	def left(self):
		return self.pos.x - self.radius

	@property
	def right(self):
		return self.pos.x + self.radius


class String:
	def __init__(self):
		self.forceConstant = 10	# Nm^-1
		self.length = 10

	