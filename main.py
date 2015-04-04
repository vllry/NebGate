from bottle import route, run, request
import random, time
from threading import Thread



SERVERS = {}
DUPES = {}
PINGTIME = 15



def timeoutServers():
	while True:
		time.sleep(PINGTIME)
		for key,server in SERVERS.items():
			if server['ping'] + PINGTIME*1.5 < time.time():
				print "Removing inactive server", key
				del SERVERS[key]
timeoutTimer = Thread(target=timeoutServers)
timeoutTimer.start()



def set_server_map(mapname):
	lowest_server = ''
	lowest_pop = 99
	for key,server in SERVERS:
		if server['players'] < lowest_pop and 'changemap' not in server:
			lowest_server = key
			lowest_pop = server['players']
	delay = 0
	if lowest_pop and lowest_pop < 3:
		delay = 60
	else:
		delay = 90
	SERVERS[lowest_server]['mapchange'] = {'delay':delay, 'map':mapname}



def generate_id():
	if random.random() < 0.25:
		bosnia = ['bosnia-north', 'bosnia-east', 'bosnia-south', 'bosnia-west', 'bosnia-pole']
		return random.choice(bosnia)
	else:
		greek = ['gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'mu', 'omicron', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega']
		serverid = random.choice(greek)
		if random.random() < 0.1:
			serverid += "-enterprise-edition"
		return serverid



@route('/')
def hello():
    return "Toast"



@route('/server')
def server():
    return str(SERVERS)



@route('/server/register', method='POST')
def register_server():
	port = request.forms.get('port')
	mapname = request.forms.get('map')
	ip = request.remote_addr
	players = request.forms.get('playercount')
    
	serverid = generate_id()
	while serverid in SERVERS:
		serverid = generate_id()

	SERVERS[serverid] = {
        'ip':ip, 
        'port':port, 
        'map':mapname,
	'players':int(players),
        'ping':time.time()

	return {
		'status':'ok',
		'interval':PINGTIME
		}
    }

	print "Registering " + ip + ":" + port + " (running with " + players + " on " + mapname +") as" + serverid
	return {
		'id': str(serverid)
		}



@route('/server/map/<name>', method='GET')
def get_server_running_map(name):
	for key,server in SERVERS.items():
		if server['map'] == name and not server['changemap']['map']: #Ignore servers that are running this map but due to change
			return {
				'status':'ok',
				'ip':server['ip'],
				'port':server['port']
				}
		elif server['changemap']['map'] == name:
			return {
				'status':'no server yet'
				}
	set_server_map(name)
	return {
		'status':'no server yet'
		}



@route('/server/id/<name>/ping', method='GET')
def get_server_ping(name):
	if name in SERVERS:
		SERVERS[name]['ping'] = time.time()
		SERVERS[name]['players'] = request.forms.get('playercount')
		mapname = request.forms.get('map')
		SERVERS[name]['map'] = mapname

		if 'changemap' in SERVERS[name]:
			changemap = SERVERS[name]['changemap']
			if mapname == changemap:
				del SERVERS[name]['changemap'] #Delete the changemap info once the map has been loaded
			return {
				'status': 'ok',
				'changemap': changemap
				}

		elif mapname in DUPES: #If there's dupes at the same time as a changemap, we don't want 'em
			dupes = DUPES[mapname]
			del DUPES[mapname]
			return {
				'status': 'ok',
				'dupes': dupes
				}

		return {
			'status': 'ok'
			}

	else:
		return {
			'status': 'wtf dude'
			}



@route('/server/id/<name>/dupe', method='GET')
def get_dupe(name):
	dupe = request.forms.get(dupe)
	dest = request.forms.get(dest)
	pos = request.forms.get(pos)
	ang = request.forms.get(ang)
	vel = request.forms.get(vel)
	angvel = request.forms.get(angvel)
	dupetime = request.forms.get(time)
	if not dest in DUPES:
		DUPES[dest] = []
	DUPES[dest].append({
			'dupe':dupe,
			'pos':pos,
			'ang':ang,
			'vel':vel,
			'angvel':angvel,
			'time':dupetime
			})
	print "Got dupe from " + name



run(host='', port=27071, debug=True)

