
from util.sockets import ServerSocket
from util.message import Message
import threading
from handler import handle
import os
from game import Game

SAVEFILE = "game.save"

print "Checking for savefile..."

game = None

if os.path.isfile(SAVEFILE):
	# Do some loading stuff
	pass
else:
	game = Game()


print "Starting server..."

socket = ServerSocket('localhost', 5050)

try:
	while 1:
		client = socket.getClientObject()
		t = threading.Thread(target=handle, args=(client,game))
		t.daemon = True
		t.start()
except KeyboardInterrupt:
	import sys
	sys.exit(0)
