#!/usr/bin/env python3

import pygame, math, sys, os
from colours import *
from objects import Vector, Ball, Point, String
from helper import Helper

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

	helper = Helper(DISPLAY, SCALE, WIDTH, HEIGHT)
	drawPos = helper.drawPos
	worldPos = helper.worldPos
	drawVector = helper.drawVector

	personImage = pygame.image.load(os.getcwd()+"/person.jpg")
	personRect = personImage.get_rect()
	personImage = pygame.transform.scale(personImage, (int(personRect.width*(int(1.8*SCALE)/personRect.height)), int(1.8*SCALE)))

	moveData = {
		"lastPos": Point(),
		"currentPos": Point(CENTRE.x, 0),
		"lastScreenMousePos": Point(),
		"mouseHeld": False,
		"lastVelocity": Vector()
	}
	mouseVelocity = Vector()

	mouseBall = Ball()
	mouseBall.moveable = False

	tickerPoints = []
	MAX_TICKER_POINTS = 100
	TICKER_PERIOD = 0.02
	timeSinceLastTicker = 0

	ball = Ball()
	ball.setPos(Point(WIDTH/2, HEIGHT/2))

	string = String()
	string.setConnections(mouseBall, ball)
	string.active = False

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
						string.toggle()
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
			moveData["lastVelocity"] = Vector(mouseBall.velocity)
			mouseVelocity = Vector(((moveData["currentPos"]-moveData["lastPos"])/deltaT).pos())
			mouseAcceleration = (mouseVelocity - moveData["lastVelocity"])/deltaT
		else:
			mouseVelocity = Vector()
			mouseAcceleration = Vector()
		mouseBall.setPos(moveData["currentPos"])
		mouseBall.setVelocity(mouseVelocity)


		#gravity adjustment
		if heldKeys[pygame.K_i]:
			GRAVITY = min(30.0,GRAVITY+0.1)
		elif heldKeys[pygame.K_k]:
			GRAVITY  = max(0.0,GRAVITY-0.1)

		#ball radius
		if heldKeys[pygame.K_o]:
			ball.radius = min(4.0,ball.radius+0.01)
		elif heldKeys[pygame.K_l]:
			ball.radius = max(0.1,ball.radius-0.01)

		#string length
		if heldKeys[pygame.K_u]:
			string.length = min(8.0,string.length+0.01)
		elif heldKeys[pygame.K_j]:
			string.length = max(0.01,string.length-0.01)


		#reset all
		if heldKeys[pygame.K_r]:
			GRAVITY = 9.81
			ball.radius = 0.1
			string.length = 2.0



		if ball.bottom <= 0:
			if ball.velocity.y < 0:
				ball.accelerate(Vector((0, -ball.velocity.y-ball.velocity.y*ball.cor)))
		else:
			ball.accelerate(Vector((0, -GRAVITY))*deltaT)

		if ball.left <= 0:
			if ball.velocity.x < 0:
				ball.accelerate(Vector((-ball.velocity.x-ball.velocity.x*ball.cor, 0)))

		if ball.right >= WIDTH:
			if ball.velocity.x > 0:
				ball.accelerate(Vector((-ball.velocity.x-ball.velocity.x*ball.cor, 0)))

		string.applyTension(deltaT)
		
		if moveData["mouseHeld"]:
			ball.setPos(moveData["currentPos"])
			ball.setVelocity(mouseBall.velocity)
		else:
			ball.move(deltaT)

		string.correctPositions()

		# === DRAW

		# draw person
		DISPLAY.blit(personImage, (-(1/3)*personImage.get_rect().width, SCREEN_HEIGHT-personImage.get_rect().height))

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
		drawVector(mouseBall.velocity, moveData["currentPos"], 20, False, BLUE)

		# velocity vector is scaled so it can be more easily comprehended
		drawVector(ball.velocity, ball.pos, 10, False, GREEN, 1)

		# draw ball
		pygame.draw.circle(DISPLAY, RED, drawPos(ball.pos), int(ball.radius*SCALE), 1)

		if string.active:
			pygame.draw.line(DISPLAY, GREEN, drawPos(ball.pos), drawPos(moveData["currentPos"]), 1)

		font = pygame.font.SysFont("monospace", 15)
		# render text
		fps = font.render("{}fps".format(int(CLOCK.get_fps())), 1, BLACK)
		DISPLAY.blit(fps, (10, 10))
		ballVelLabel = font.render("Ball velocity: {:.2f}ms-1".format(ball.velocity.mag), 1, BLACK)
		DISPLAY.blit(ballVelLabel, (10, 30))
		mouseVelLabel = font.render("Mouse velocity: {:.2f}ms-1".format(mouseBall.velocity.mag), 1, BLACK)
		DISPLAY.blit(mouseVelLabel, (10, 50))
		gravityVelLabel = font.render("Gravity: {:.2f}ms-2".format(GRAVITY), 1, BLACK)
		DISPLAY.blit(gravityVelLabel, (10, 70))
		diameterVelLabel = font.render("Ball diameter: {:.2f}m".format(ball.radius*2), 1, BLACK)
		DISPLAY.blit(diameterVelLabel, (10, 90))
		stringVelLabel = font.render("String length: {:.2f}m".format(string.length), 1, BLACK)
		DISPLAY.blit(stringVelLabel, (10, 110))


		#control prompts
		stringConnect = font.render("Connect string:           SPACE", 1, BLACK)
		DISPLAY.blit(stringConnect, (SCREEN_WIDTH-stringConnect.get_rect().width-10, 10))
		stringControl = font.render("String length +/-:        U/J", 1, BLACK)
		DISPLAY.blit(stringControl, (SCREEN_WIDTH-stringConnect.get_rect().width-10, 30))
		gravityControl = font.render("Gravity +/-:              I/K", 1, BLACK)
		DISPLAY.blit(gravityControl, (SCREEN_WIDTH-stringConnect.get_rect().width-10, 50))
		diameterControl = font.render("Ball diameter +/-:        O/L", 1, BLACK)
		DISPLAY.blit(diameterControl, (SCREEN_WIDTH-stringConnect.get_rect().width-10, 70))
		resetAllControl = font.render("Reset all:                R", 1, BLACK)
		DISPLAY.blit(resetAllControl, (SCREEN_WIDTH-stringConnect.get_rect().width-10, 90))
		pygame.display.update()
		CLOCK.tick(120)

if __name__ == "__main__":
	main()