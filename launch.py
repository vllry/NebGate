import bottle
import main

try:
	import win32file
	import win32con
	from threading import Thread
	import os, time
	from twisted.python.rebuild import rebuild
except ImportError:
	print "Dynamically reloading the script requires Windows + twisted, not enabling"
else:
	def doScriptReload():
		print "Script change detected; performing reload"
		savedvars = (main.SERVERS, main.MAPQUEUE) # Persist these vars through reloads
		main.timeoutTimer.stop() # Kill the old timeoutTimer since we'll start a new one
		rebuild(main)
		(main.SERVERS, main.MAPQUEUE) = savedvars # Restore those vars

	def watchForScriptUpdates():
		path_to_watch = "."
		file_to_watch = "main.py"
		
		hDir = win32file.CreateFile (
			path_to_watch,
			0x0001, #FILE_LIST_DIRECTORY,
			win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
			None,
			win32con.OPEN_EXISTING,
			win32con.FILE_FLAG_BACKUP_SEMANTICS,
			None
		)

		lastRebuildTime = 0
		while 1:
			# Wait for a change to occur
			results = win32file.ReadDirectoryChangesW (
				hDir,
				1024,
				False,
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
				None,
				None
			)
			for action, file in results:
				if file == file_to_watch and lastRebuildTime < (time.time() - 1):
					lastRebuildTime = time.time()
					time.sleep(0.25)
					doScriptReload()

	timeoutTimer = Thread(target=watchForScriptUpdates)
	timeoutTimer.start()


bottle.run(host='', port=27071, debug=True)
print "Got past bottle.run?!"
