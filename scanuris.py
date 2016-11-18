#coding: utf-8

import requests
import urlparse
import Queue
import threading
import argparse
import sys

try:
	import requests.packages.urllib3
	requests.packages.urllib3.disable_warnings()
except:
    pass

reload(sys)
sys.setdefaultencoding('utf-8')

g_recursive = False
g_nogreedy = False
g_queue = Queue.Queue()
g_scannedurls = []
g_dicts = []
g_prefix = ''
g_suffix = ''
g_count = 0
g_content_key = ''
g_status = []
	

def load_targets(_file=None,_target=None):
	if _target:
		g_queue.put(_target)
	elif file:
		for a in [x.strip() for x in file(_file,'r')]:
			g_queue.put(a)
	return g_queue.qsize()

def load_dicts(_file=None,_dir=None):
	if _dir:
		g_dicts.append(g_prefix+_dir+g_suffix)
	if _file:
		for x in file(_file,'r').readlines():
			g_dicts.append(g_prefix+x.strip()+g_suffix)
	return len(g_dicts)


def get_baseurls(weburl):
	_baseUrls = []
	_basePathes = ['']
	_new_weburl = weburl.strip()
	_urlObj = urlparse.urlparse(_new_weburl)
	_urlPath = _urlObj.path
	if _urlPath != '':
		_pathArray = _urlPath.split('/')
		_pathArray.pop()
		_basePath = ''
		for _path in _pathArray:
			if _path != '':
				_basePath = _basePath + '/' + _path
				_basePathes.append(_basePath)
	for _basePath in _basePathes:
		_baseUrl = '%s://%s%s' % (_urlObj.scheme,_urlObj.netloc,_basePath)
		_baseUrls.append(_baseUrl)
	return _baseUrls

def scan_thread():
	global g_count
	while g_queue.qsize()>0:
		_weburl = g_queue.get()
		if _weburl == '':
			continue
		_weburls = get_baseurls(_weburl)
		if not g_recursive:
			_weburls = [get_baseurls(_weburl).pop()]

		_break = False
		for _weburl in _weburls:
			if _break:
				break
			for _dir in g_dicts:
				g_count = g_count + 1
				_url = _weburl.strip('/') + '/' + _dir
				try:
					_resp = requests.get(url=_url, timeout=10, verify=False, allow_redirects=False)
					_status = _resp.status_code
					_content = _resp.content
				except Exception as e:
					try:
						_resp = requests.get(url=_url, timeout=10, verify=False, allow_redirects=False)
						_status = _resp.status_code
						_content = _resp.content
					except Exception as e:
						_status = -1

				_spaces = ' ' * (64-len(_url))
				
				_ret = True
				if _status == -1:
					sys.stdout.write('{0}{1}[{2}] \r'.format(_url, _spaces, _status))
					sys.stdout.flush()
					_break = True
					break
				elif not _status in g_status:
					_ret = False
				if not g_content_key in _content:
					_ret = False

				if _ret:
					sys.stdout.write('{0}{1}[{2}] \n'.format(_url, _spaces, _status))
					sys.stdout.flush()
					if g_nogreedy:
						_break = True
						break
					else:
						continue
				else:
					sys.stdout.write('{0}{1}[{2}] \r'.format(_url, _spaces, _status))
					sys.stdout.flush()


def parser_error(err):
	print '-h for help.'
	sys.exit(0)

def parse_args():
	parser = argparse.ArgumentParser('ptyhon scanuris.py')
	parser.error = parser_error
	parser.add_argument('--recursive', action='store_true')
	parser.add_argument('--nogreedy', action='store_true')	
	parser.add_argument('--status', metavar='STATUS1,STATUS2,...', dest='_status', default=None, required=True, help='指定状态,多种状态用\',\'分隔,默认[301,302]')
	parser.add_argument('--content', metavar='KEYWORD', dest='_content_key', default='', help='返回页面内容包含关键字')
	parser.add_argument('--prefix', metavar='PREFIX', dest='_prefix', default='', help='拼接目录前缀')
	parser.add_argument('--suffix', metavar='SUFFIX', dest='_suffix', default='', help='拼接目录后缀')
	parser.add_argument('--dir', metavar='DIRECTORY', dest='_dir', default=None, help='指定目录')
	parser.add_argument('--target', metavar='TARGET', dest='_target', default=None, help='扫描目标')
	parser.add_argument('--targets', metavar='FILE', dest='_targets', default=None, help='从FILE文件读取扫描目标')
	parser.add_argument('--dict', metavar='FILE', dest='_dict', default=None, help='从FILE文件读取路径字典')
	parser.add_argument('--threads', metavar='COUNT', dest='_threads', default=None, type=int, help='线程数')
	parser.add_argument('--go', action='store_true')
	return parser.parse_args()

if __name__ == '__main__':
	_args = parse_args()
	g_prefix = _args._prefix
	g_suffix = _args._suffix
	g_nogreedy = _args.nogreedy
	g_recursive = _args.recursive
	g_content_key = _args._content_key

	_dics = load_dicts(_file=_args._dict,_dir=_args._dir)
	
	if _args._status:
		g_status = [int(x) for x in _args._status.split(',')]

	if _args._targets:
		_tars = load_targets(_file=_args._targets)
	elif _args._target:
		_tars = load_targets(_target = _args._target)

	print '---- %s targets, %s dirs -----' % (_tars,_dics)

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
