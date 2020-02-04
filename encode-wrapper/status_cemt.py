from utilsm import *






def main(args):
	def k(x):
		try:
			return  x.split()[0]
		except:
			return '-'
	def v(x):
		try:
			return x.split()[1]
		except:
			return '-'


	def is_cruft(e):
		e = e.strip()
		return not e or any([e.startswith(x) for x in ['sambamba 0.7.1', 'by Artem', 'LDC 1.17.0']])

	log = by_keyvalue([x for x in linesf(args[0]) if not is_cruft(x)], k, v)
	print(jdumpf("./discovered_md5s.json", log))
	expected = jloadf(args[1]) 
	n_fails = 0
	for k in expected:
		if not k in log:
			n_fails += 1
			print2('missing', k)
		else:
			found = log[k]
			assert len(found) == 1, 'non unique md5: '+ str(k, found)
			if not  found[0] == expected[k][0]:
				n_fails += 1
			else:
				print2( 'ok', k, expected[k][0])
	
	result = {
		"failures":n_fails
	}
	print2(jsonp(result))


if __name__ == '__main__':	
	import sys
	main(sys.argv[1:])

