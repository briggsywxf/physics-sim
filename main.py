#!/usr/bin/env python3

import pygame, math, sys
from colours import *
from objects import Vector, Ball, Point, String


def main():
	pygame.init()
	SCREEN_WIDTH = 800
	SCREEN_HEIGHT = 600
	SCALE = 80	# pixels per meter
	WIDTH = SCREEN_WIDTH/SCALE
	HEIGHT = SCREEN_HEIGHT/SCALE

	SCREEN_CENTRE = Point(WIDTH/2, HEIGHT/2)
	CENTRE = SCREEN_CENTRE/SCALE

	DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	CLOCK = pygame.time.Clock()
	totalTime = 0

	GRAVITY = 9.81

	def drawPos(pos):
		return (int(pos.x*SCALE), int((HEIGHT-pos.y)*SCALE))

	def worldPos(pos):
		return (pos.x/SCALE, HEIGHT - pos.y/SCALE)

	def drawVector(v, start, scale=1, showBall=True, colour=PURPLE, width=2):
		'''
		Draws a vector, from
			Vector v
			Point start
			float scale
			bool showBall
		'''
		if v.mag > 0:
			pygame.draw.line(DISPLAY, colour, drawPos(start), drawPos(start + (v/scale).endPos()), width)
			if showBall:
				pygame.draw.circle(DISPLAY, colour, drawPos(start+(v/scale).endPos()), 3, 3)

	v1 = Vector(2, 3/2*math.pi)
	v2 = Vector(3, 1/4*math.pi)

	moveData = {
		"lastPos": Point(),
		"currentPos": Point(CENTRE.x, 0),
		"lastScreenMousePos": Point(),
		"mouseHeld": False
	}

	tickerPoints = []
	MAX_TICKER_POINTS = 100
	TICKER_PERIOD = 0.02
	timeSinceLastTicker = 0

	ball = Ball()
	ball.setPos(Point(WIDTH/2, HEIGHT/2))
	#ball.accelerate(Vector(10, math.pi/2))

	string = String()
	useString = False

	while True:
		DISPLAY.fill(WHITE)
		deltaT = CLOCK.get_time()/1000
		totalTime += deltaT

		moveData["lastPos"] = Point(moveData["currentPos"])
		if not moveData["lastScreenMousePos"] == Point(pygame.mouse.get_pos()):
			moveData["currentPos"] = Point(worldPos(Point(pygame.mouse.get_pos())))

		moveData["lastScreenMousePos"] = Point(pygame.mouse.get_pos())

		heldKeys = pygame.key.get_pressed()
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				pygame.quit()

			elif e.type == pygame.KEYDOWN:
				heldKeys = pygame.key.get_pressed()
				if (heldKeys[pygame.K_RCTRL] or heldKeys[pygame.K_LCTRL]) and\
					(heldKeys[pygame.K_w] or heldKeys[pygame.K_q]):
					pygame.quit()
				if (heldKeys[pygame.K_SPACE]):
					mouseBallDist = moveData["currentPos"].distance(ball.pos)
					if mouseBallDist > 0:
						useString = not useString
						string.length = mouseBallDist

			elif e.type == pygame.MOUSEBUTTONDOWN:
				if e.button == 1:
					moveData["mouseHeld"] = True

			elif e.type == pygame.MOUSEBUTTONUP:
				if e.button == 1:
					moveData["mouseHeld"] = False

		keyboardMoveSpeed = 1
		if heldKeys[pygame.K_a]:
			moveData["currentPos"] = moveData["currentPos"] - Point(keyboardMoveSpeed*deltaT, 0)
		elif heldKeys[pygame.K_d]:
			moveData["currentPos"] = moveData["currentPos"] + Point(keyboardMoveSpeed*deltaT, 0)
		if heldKeys[pygame.K_w]:
			moveData["currentPos"] = moveData["currentPos"] + Point(0, keyboardMoveSpeed*deltaT)
		elif heldKeys[pygame.K_s]:
			moveData["currentPos"] = moveData["currentPos"] - Point(0, keyboardMoveSpeed*deltaT)

		if deltaT > 0:
			mouseVelocity = Vector(((moveData["currentPos"]-moveData["lastPos"])/deltaT).pos())
		else:
			mouseVelocity = Vector()

		if ball.bottom <= 0:
			#if abs(ball.velocity.y) < 0.5:
				#ball.setVelocity(Vector((ball.velocity.x, 0)))
				#ball.setPos(Point(ball.pos.x, ball.radius))
			if ball.velocity.y < 0:
				ball.accelerate(Vector((0, -ball.velocity.y-ball.velocity.y*ball.cor)))
		else:
			ballMouseDistance = ball.pos.distance((moveData["currentPos"]))

			ball.accelerate(Vector((0, -GRAVITY))*deltaT)

			# for debug
			tensionVector = Vector()
			stringVector = Vector()
			mouseAccelTension = Vector()
			antiVelocityVector = Vector()
			if ballMouseDistance >= string.length and useString:
				# String is taut
				# We can work out angle between gravity and tension vector
				# by creating a temporary vector for the string
				stringVector = Vector((ball.pos-moveData["currentPos"]).pos())
				# tension acts on the ball towards the string pivot:
				oppositeStringAngle = stringVector.dir - math.pi

				# calculate tension created by taut string against velocity
				# away from string pivot
				ballVelMag = ball.velocity.mag
				ballVelAngle = ball.velocity.dir
				theta = ballVelAngle - stringVector.dir 
				antiVelocityMag = ballVelMag * math.cos(theta)
				if antiVelocityMag > 0:
					antiVelocityVector = Vector(antiVelocityMag, oppositeStringAngle)
					tensionVector = tensionVector + antiVelocityVector

				# do tension created by movement
				mouseAccelTensionMag = mouseVelocity.mag * math.cos(oppositeStringAngle - mouseVelocity.dir)
				# this tension acts upon the ball along the oppositeStringAngle angle
				mouseAccelTension = Vector(mouseAccelTensionMag, oppositeStringAngle)

				tensionVector = tensionVector + mouseAccelTension

				tensionVector.normalizeDir()
				ball.accelerate(tensionVector)

		if ball.left <= 0:
			if ball.velocity.x < 0:
				ball.accelerate(Vector((-ball.velocity.x-ball.velocity.x*ball.cor, 0)))

		if ball.right >= WIDTH:
			if ball.velocity.x > 0:
				ball.accelerate(Vector((-ball.velocity.x-ball.velocity.x*ball.cor, 0)))

		
		if moveData["mouseHeld"]:
			ball.setPos(moveData["currentPos"])
			ball.setVelocity(mouseVelocity)
		else:
			ball.move(deltaT)

			if ballMouseDistance >= string.length and useString:
				# test scale ball distance
				distanceMod = string.length/ballMouseDistance
				distancePoint = Point(distanceMod*(ball.pos.x-moveData["currentPos"].x), distanceMod*(ball.pos.y-moveData["currentPos"].y))
				ball.setPos(moveData["currentPos"] + distancePoint)

		# draw ticker tape
		if not moveData["mouseHeld"]:
			timeSinceLastTicker += deltaT
			if timeSinceLastTicker >= TICKER_PERIOD:
				tickerPoints.append(Point(ball.pos))
				if len(tickerPoints) > MAX_TICKER_POINTS:
					del tickerPoints[0]
				timeSinceLastTicker = 0
		else:
			tickerPoints = []

		for p in tickerPoints:
			pygame.draw.circle(DISPLAY, BLUE, drawPos(p), 2, 2)

		# draw mouse velocity vector
		drawVector(mouseVelocity, moveData["currentPos"], 20, False, BLUE)

		# velocity vector is scaled so it can be more easily comprehended
		drawVector(ball.velocity, ball.pos, 10, False, GREEN, 1)

		# draw ball
		pygame.draw.circle(DISPLAY, RED, drawPos(ball.pos), int(ball.radius*SCALE), 1)

		if useString:
			pygame.draw.line(DISPLAY, GREEN, drawPos(ball.pos), drawPos(moveData["currentPos"]), 1)

		# draw tension vector
		drawVector(tensionVector, ball.pos, 10)

		font = pygame.font.SysFont("monospace", 15)
		# render text
		ballVelLabel = font.render("Ball velocity: {}ms-1".format(int(ball.velocity.mag)), 1, BLACK)
		DISPLAY.blit(ballVelLabel, (10, 30))
		mouseVelLabel = font.render("Mouse velocity: {}ms-1".format(int(mouseVelocity.mag)), 1, BLACK)
		DISPLAY.blit(mouseVelLabel, (10, 50))
		fps = font.render("{}fps".format(int(CLOCK.get_fps())), 1, BLACK)
		DISPLAY.blit(fps, (10, 10))
		#	pygame.draw.line(DISPLAY, PURPLE, drawPos(moveData["currentPos"]), drawPos(moveData["currentPos"] + stringVector.endPos()), 2)
		#	pygame.draw.circle(DISPLAY, PURPLE, drawPos(moveData["currentPos"]+stringVector.endPos()), 3, 3)

		pygame.display.update()
		CLOCK.tick(120)

if __name__ == "__main__":
	main()