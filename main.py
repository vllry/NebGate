from bottle import route, run, request
import random, time
from threading import Thread



SERVERS = {}
MAPQUEUE = {}
WHITELIST = {'192.168.0.*'}
PINGTIME = 15



def in_whitelist(ip):
	pieces_of_ip = ip.split('.')
	for item in WHITELIST:
		match = True
		for i,octet in enumerate(item.split('.')):
			if octet != pieces_of_ip[i] and octet != '*':
				match = False
		if match:
			return True
	return False



def timeoutServers():
	while True:
		time.sleep(PINGTIME)
		for key,server in SERVERS.items():
			if server['ping'] + PINGTIME*2.5 < time.time():
				print "Removing inactive server", key
				del SERVERS[key]
timeoutTimer = Thread(target=timeoutServers)
timeoutTimer.start()



def set_server_map(mapname, callingserver):
	lowest_server = ''
	lowest_pop = 99
	for key,server in SERVERS.items():
		if key != callingserver and server['players'] < lowest_pop and ('changemap' not in server or server['changemap']['map'] == mapname):
			lowest_server = key
			lowest_pop = server['players']
	delay = 0
	if lowest_pop and lowest_pop < 3:
		delay = 60
	else:
		delay = 90
	SERVERS[lowest_server]['changemap'] = {'delay':delay, 'map':mapname}
	MAPQUEUE.get(SERVERS[lowest_server]['map'], []).append({
		'event': 'mapchange',
		'map': mapname,
		'delay': delay,
	})



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
	mapname = request.forms.get('map').lower()
	ip = request.remote_addr
	players = request.forms.get('playercount')
    
	serverid = generate_id()
	while serverid in SERVERS:
		serverid = generate_id()

	SERVERS[serverid] = {
		'ip': ip, 
		'port': port,
		'map': mapname,
		'players': int(players),
		'ping': time.time(),
	}

	print "Registering " + ip + ":" + port + " (running with " + players + " on " + mapname +") as " + serverid
	return {
		'id': str(serverid),
		'status': 'ok',
		'interval': PINGTIME,
	}



@route('/server/map/<name>', method='GET')
def get_server_running_map(name):
	name = name.lower()
	for key,server in SERVERS.items():
		if server['map'] == name and 'changemap' not in server: #Ignore servers that are running this map but due to change
			return {
				'status': 'ok',
				'ip': server['ip'],
				'port': server['port'],
			}
		elif 'changemap' in server and server['changemap']['map'] == name:
			return {
				'status':'no server yet',
			}
	set_server_map(name, request.forms.get('id'))
	return {
		'status': 'no server yet',
	}



@route('/server/id/<name>/ping', method='POST')
def get_server_ping(name):
	if name in SERVERS:
		SERVERS[name]['ping'] = time.time()
		SERVERS[name]['players'] = int(request.forms.get('playercount'))
		mapname = request.forms.get('map').lower()
		SERVERS[name]['map'] = mapname

		return {
			'status': 'ok',
			'events': MAPQUEUE.pop(mapname, []),
		}
	else:
		return {
			'status': 'wtf dude',
		}



@route('/server/id/<name>/dupe', method='GET')
def get_dupe(name):
	dupe = request.forms.get('dupe')
	dest = request.forms.get('dest')
	pos = request.forms.get('pos')
	ang = request.forms.get('ang')
	vel = request.forms.get('vel')
	angvel = request.forms.get('angvel')
	dupetime = request.forms.get('time')
	MAPQUEUE.get(SERVERS[name]['map'], []).append({
		'event': 'dupe',
		'dupe': dupe,
		'pos': pos,
		'ang': ang,
		'vel': vel,
		'angvel': angvel,
		'time': dupetime,
	})
	print "Got dupe from " + name



@route('/server/map/<mapname>/player', method='GET')
def player_going_to_map(mapname):
	player = request.forms.get('player')
	MAPQUEUE.get(mapname, []).append({
		'event': 'player',
		'player': player,
	})



run(host='', port=27071, debug=True)

