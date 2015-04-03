from bottle import route, run, request
import random, time
from threading import Thread

SERVERS = {}

def timeoutServers():
	while True:
		time.sleep(10)
		for key,server in SERVERS.items():
			print "time", server['ping'], time.time()
			if server['ping'] + 10 < time.time():
				print "del"
				del SERVERS[key]
timeoutTimer = Thread(target=timeoutServers)
timeoutTimer.start()
	

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
    
	serverid = generate_id()
	while serverid in SERVERS:
		serverid = generate_id()

	SERVERS[serverid] = {
        'ip':ip, 
        'port':port, 
        'map':mapname, 
        'ping':time.time()
    }

	print "Registering " + ip + ":" + port, "as", serverid
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
    #TODO: Spool up a server running that map
	return {'status':'we do not have a server running that map yet'}

@route('/server/id/<name>/ping', method='GET')
def server_ping(name):
	if name in SERVERS:
		SERVERS[name]['ping'] = time.time()
		return {'status': 'ok'}
	else:
		return {'status': 'wtf dude'}

run(host='', port=27071, debug=True)

