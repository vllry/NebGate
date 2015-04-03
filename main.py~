from bottle import route, run, request
import random, time
from threading import Thread



SERVERS = {}



def timeoutServers():
	while True:
		time.sleep(15)
		for key,server in SERVERS.items():
			print "time", server['ping'], time.time()
			if server['ping'] + 15 < time.time():
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
		bosnia = ['bosnia-north', 'bosnia-east', 'bosnia-south', 'bosnia-west']
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
    }

	print "Registering " + ip + ":" + port + " (running with " + players + " on " + mapname +") as" + serverid
	return {
		'id': str(serverid)
		}



@route('/server/map/<name>', method='GET')
def get_server_running_map(name):
	for key,server in SERVERS.items():
		if server['map'] == name:
			return {
				'status':'ok',
				'ip':server['ip'],
				'port':server['port']
				}
	set_server_map(name)
	return {
		'status':'no server yet'
		}



@route('/server/id/<name>/ping', method='GET')
def server_ping(name):
	if name in SERVERS:
		SERVERS[name]['ping'] = time.time()
		SERVERS[name]['players'] = request.forms.get('playercount')
		SERVERS[name]['map'] = request.forms.get('map')
		if 'changemap' in SERVERS[name]:
			return {
				'status': 'ok',
				'changemap': SERVERS[name]['changemap']
				}
		return {
			'status': 'ok'
			}
	else:
		return {
			'status': 'wtf dude'
			}



run(host='', port=27071, debug=True)

