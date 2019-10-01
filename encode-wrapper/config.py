import utilsm
import sys

class Config:
	def __init__(self, args):
		keyargs = dict()
		def argtype(x):
			if x.strip()[0] != '-': return 'values'
			else:
				tokens = x.split(':')
				t = len(tokens)
				if t == 2:
					if tokens[0] in keyargs: raise Exception('malformed arguments '+ str(args) )
					else: keyargs[tokens[0]] = tokens[1]
				elif t == 1: return 'flags'
				else: raise Exception('malformed arguments '+ str(x))
		
		parsed = utilsm.by_keyvalue(args, k = lambda x: argtype(x), v = lambda x: x)
		self.values, self.keys, self.flags = parsed.get('values', []), keyargs, parsed.get('flags', [])

	def __getitem__(self, k):
		if k in self.keys: return self.keys[k]
		elif k in self.flags: return True
		else:
			raise Exception('__MISSING__')

	def get_values(self):
		return self.values

	def get(self, k, defaultvalue = None):
		if not defaultvalue: return self.keys[k]
		else: return self.keys.get(k, defaultvalue)

	def or_else(self, k, defaultValue):
		return self.keys.get(k, defaultValue) 

	def has(self, flag):
		return flag in self.flags or flag in self.keys.keys()

	def option(self, field):
		return self.keys[field] 

	def __str__(self):
		return '#config = -flags:{0} -keys:{1} values:{2}'.format(self.flags, self.keys, self.values)



	@staticmethod
	def sys():
		return Config(sys.argv[1:]) 
