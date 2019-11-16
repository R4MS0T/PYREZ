import os

app_dir = os.path.abspath(os.path.dirname(__file__))
class DiscordConfig(object):
	"""
	docstring for DiscordConfig

	from config import DiscordConfig
	x = DiscordConfig()
	print(x['token'])
	print(x.get('token'))
	print(x.token)
	print(x)
	"""
	def __init__(self, *, _config='data/config.json'):
		#./../config/config.json
		self.load(_config)
	def load(self, path):
		if not os.path.isfile(path):#os.path.isdir(path)
			path = join(path, 'config.json')
		from utils.file import read_file
		self.__kwargs__ = read_file(path, is_json=True)
	def get(self, key, default=None):
		return self.__getitem__(key) or default
	def __getitem__(self, key):
		try:
			return self.__kwargs__[key]
		except KeyError:
			return None
	def __contains__(self, key):
		return key in self.__kwargs__
	def __dir__(self):
		if isinstance(self.__kwargs__, dict):
			return self.__kwargs__.keys()
		return {}
	def __len__(self):
		return len(self.__kwargs__)
	def __iter__(self):
		return (key for key in self.__kwargs__) #return (self.__kwargs__[key] for key in self.__kwargs__)
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		if self.__kwargs__:
			import json
			return json.dumps(self.__kwargs__, ensure_ascii=True, sort_keys=True, indent=2)
		return ''
class Config(object):
	from utils import random, get_env
	from boolify import boolify

	SQLALCHEMY_DATABASE_URI = get_env('DATABASE_URL', default='sqlite:///{}.db'.format('app' or __name__))#'sqlite:///:memory:'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	#SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	_binds = get_env('SQLALCHEMY_BINDS', default=None)
	SQLALCHEMY_BINDS = {}
	if _binds:
		#https://docs.sqlalchemy.org/en/13/core/exceptions.html
		#https://flask-sqlalchemy.palletsprojects.com/en/2.x/binds/
		#https://flask-migrate.readthedocs.io/en/latest/
		for _ in _binds.split(','):
			__ = _.split(':', 1)
			SQLALCHEMY_BINDS.update({__[0].lower() : __[1] if __[1].rfind('://') != -1 else get_env(__[1])})
	else:
		import os
		for _ in os.environ:
			if 'DB_URL' in _.upper():
				SQLALCHEMY_BINDS.update({_.split('_', 1)[0] : get_env(_)})
	print(SQLALCHEMY_BINDS)
	# SECURITY WARNING: don't run with debug turned on in production!
	#Default: True if ENV is 'development', or False otherwise.
	DEBUG = boolify(get_env('DEBUG', default=os.sys.platform == 'win32' or os.name == 'nt'))

	# SECURITY WARNING: keep the secret key used in production secret!
	SECRET_KEY = get_env('SECRET_KEY', default=random(as_string=True, size=65))

	PORT, HOST = get_env('PORT', default=5000), get_env('HOST', default='0.0.0.0')

	DEVELOPMENT = TESTING = False

	LOG_PATH = get_env('LOG_PATH', 'logs')
	LOG_FILENAME = get_env('LOG_FILENAME', 'flask.log')
	LOG_LEVEL = get_env('LOG_LEVEL', 'info')

	@property
	def DATABASE_URI(self):
		return SQLALCHEMY_DATABASE_URI
class Developement(Config):
	DEVELOPMENT, ENV = True, 'development'#dev
	LOG_LEVEL = 'debug'

class Testing(Config):#Staging
	TESTING = DEVELOPMENT = DEBUG = True
	LOG_LEVEL = 'info'

class Production(Config):
	TESTING = DEVELOPMENT = DEBUG = False
	ENV = 'production'
	LOG_LEVEL = 'error'
