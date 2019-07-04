from map import Map
from player import Player
import loader
import time, random

class Game:
	
	def __init__(self):
		self.UIDcounter = 0
		self.players = []
		self.maxPlayers = 6
		self.closed = False
		self.cycle = 0
		self.started = False
		self.map = Map(self)
		Message.game = self
		self.story = ""
		self.orders = []
		self.masterPlayer = None
		self.entities = []
		self.races = []
	
	def onLoad(self):
		Message.game = self
	
	def initGame(self):
		self.map.initTiles(-4, 4, -4, 4)
		
		defaultMasterPassword = "insecure"
		master = Player(self, None, defaultMasterPassword, "", "", "", uber=True)
		self.masterPlayer = master
	
	def getPlayer(self, secret):
		if self.masterPlayer.secret == secret:
			return self.masterPlayer
		for player in self.players:
			if player.secret == secret:
				return player
		return None
	
	def getPlayerByUID(self, UID):
		for player in self.players:
			if player.UID == UID:
				return player
		return None
	
	def addOrder(self, player, order):
		self.orders.append([player, order])
		player.addOrder(order)
	
	def sendMessage(self, sender, receiverUID, content):
		mask = str(sender)
		message = Message(mask, content, receiverUID)
		self.getEntity(receiverUID).message(message)
		return 0
	
	def sendGameMessage(self, receiverUID, content):
		mask = "Game"
		message = Message(mask, content, receiverUID)
		self.getEntity(receiverUID).message(message)
	
	def addStory(self, line):
		if not line in self.story: # SO that multiple things being created can just have the same story, which is only added once- duplication of story should never be done deliberately.
			line = "[%s] %s" % (time.ctime(), line) # Add time stamp to beginning
			self.story += line + "\n"
	
	def vote(self, player, value):
		if not self.started: return
		
		self.votes[player] = value
		if sum(self.votes.values()) >= len(self.players):
			self.advanceCycle()
	
	def resetVotes(self):
		self.votes = {player:False for player in self.players if not player.uber}
	
	def initCycle(self):
		self.resetVotes()
		for entity in self.map.entities:
			entity.preCycle()
		for player in self.players:
			player.initCycle()
		for entity in self.map.entities:
			entity.initCycle()
		# Not sure if order will matter- since player.initCycle has already been called, players no longer remember their orders, even if the game does
		for order in self.orders:
			player, order = order
			response = player.interpret(order)
			formattedString = "The order %s has produced result code %s" % (str(order), response)
			self.sendGameMessage(player.UID, formattedString)
		self.orders = []
		self.save()
	
	def save(self):
		loader.save(self)
	
	def startGame(self):
		print "\n----------------------------STARTING GAME----------------------------\n"
		self.closed = True
		self.started = True
		self.initCycle()
		for i in xrange(len(self.players)):
			self.players[i].gameIndex = i
	
	def advanceCycle(self):
		# Maybe rename this function to _advanceCycle, and make an adavanceCycle function to spin this function off as a thread- so as not to block server-client thread.
		self.cycle += 1
		print "\n----------------------------CYCLE %s----------------------------\n" % (self.cycle,)
		self.initCycle()
	
	def addPlayer(self, player):
		if self.closed:
			raise Exception()
		self.players.append(player)
		if len(self.players) == self.maxPlayers:
			self.closed = True
	
	def generateUID(self, thing): # TODO: change so that it takes the object being assigned a UID, then appends it to a list, so it doesn't need to use a class property
		temp = self.UIDcounter
		self.UIDcounter += 1
		self.entities.append(thing)
		return temp
	
	def getEntity(self, UID):
		for entity in self.entities:
			if entity.UID == UID:
				return entity
		return None
	
	def load(self):
		pass
	
	def fight(self, entity1, entity2):
		if entity1.parent != entity2.parent:
			return 1
		strength1 = sum([thing._fightStrength() for thing in self.map.getLocationArray(entity1)])
		strength2 = sum([thing._fightStrength() for thing in self.map.getLocationArray(entity2)])
		value1 = sum([random.randint(1, strength1) for _ in xrange(2)]) - 1
		value2 = sum([random.randint(1, strength2) for _ in xrange(2)]) - 1
		entity1.hurt(value2)
		entity2.hurt(value1)
		
		return 0

class Message:
	
	game = None
	
	def __init__(self, mask, content, UID):
		self.mask = mask
		self.content = content
		self.receiverUID = UID
		self.receiver = Message.game.getEntity(UID)
	
	def __str__(self):
		return "From: %s; To: %s; Content: %s" % (self.mask, self.receiver, self.content)

