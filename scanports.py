#coding: utf-8

import socket
import Queue
import threading
import argparse
import random
import sys

try:
	import requests.packages.urllib3
	requests.packages.urllib3.disable_warnings()
except:
    pass

reload(sys)
sys.setdefaultencoding('utf-8')

g_queue = Queue.Queue()
g_ports = []
g_count = 0

socket.setdefaulttimeout(10)
	

def load_targets(_file=None,_target=None):
	if _target:
		g_queue.put(_target)
	elif file:
		for a in [x.strip() for x in file(_file,'r')]:
			g_queue.put(a)
	return g_queue.qsize()


def scan_thread():
	global g_count
	while g_queue.qsize()>0:
		_ipaddr = g_queue.get()
		for _port in g_ports:
			_places = ' ' * (18-len(_ipaddr))
			sys.stdout.write('{0}{1}{2}\r'.format(_ipaddr,_places,_port))
			sys.stdout.flush()
			try:
				_s = socket.socket()
				_s.connect((_ipaddr,_port))
				_open = True
			except:
				_open = False
			if _open:
				sys.stdout.write('\n')
			g_count = g_count + 1




def parse_error(err):
	print '-h for help.'
	sys.exit(0)

def parse_args():
	parser = argparse.ArgumentParser('usage: %prog --targets=ipaddrs.txt --port=21,22 --go')
	parser.error = parse_error
	parser.add_argument('--go', action='store_true')
	parser.add_argument('--target', metavar='TARGET', dest='_target', default=None, help='扫描目标')
	parser.add_argument('--targets', metavar='FILE', dest='_targets', default=None, help='从FILE加载多个目标')
	parser.add_argument('--port', metavar='PORT1,PORT2-PORT3,...', dest='_port', default=None, required=True, help='待扫描端口')
	parser.add_argument('--threads', metavar='COUNT', dest='_threads', default=None, type=int, help='')
	return parser.parse_args()

if __name__ == '__main__':
	_args = parse_args()
	

	if _args._targets:
		_tars = load_targets(_file=_args._targets)
	elif _args._target:
		_tars = load_targets(_target = _args._target)
	else:
		parse_error()

	if _args._port:
		for x in _args._port.split(','):
			if '-' in x:
				_locs = x.split('-')
				_a = int(_locs[0])
				_b = int(_locs[1])
				_ports = range(_a,_b)
				random.shuffle(_ports)
				for _port in _ports:
					if not _port in g_ports:
						g_ports.append(_port)
			else:
				_port = int(x.strip())
				if not _port in g_ports:
					g_ports.append(_port)
	else:
		parse_error()

	print '---- %s ipaddrs, %s ports -----' % (_tars, len(g_ports))

	if _args.go:
		_threads = []
		_thread_num = 10
		if _args._threads:
			_thread_num = _args._threads
		for i in range(_thread_num):
			t = threading.Thread(target=scan_thread)
			_threads.append(t)
		for t in _threads:
			t.start()
		for t in _threads:
			t.join()
	else:
		while g_queue.qsize()>0:
			print g_queue.get()
	sys.stdout.write('\r' + '---- %s scans done! ----'%g_count + ' '*60+'\n')

