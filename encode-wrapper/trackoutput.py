from utilsm import *
import os
import re
import sys
from config import Config


def check_extraneous(patterns, flist):
	regex = [re.compile(e) for e in patterns]
	def matched(x):
		for e in regex:
			if e.findall(x): return True
		return False
	unexpected = [f for f in flist if not matched(os.path.basename(f))]  
	return unexpected

def check_fileskept(keep):
	for f in keep:
		stats =  os.stat(f) # this fill choke if there are issue with resolving hardlinking
		print2('#keeping... ', os.path.basename(f), 'size', stats.st_size , 'ino', stats.st_ino)

def findfiles(base, pattern):
	cmd = "find {0} -iname '{1}'".format(base, pattern)
	print2(cmd)
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#assert p.returncode == 0
	found = [e.strip() for e in p.stdout.readlines()]
	for e in found: assert len(e.split()) == 1
	return found

def listfiles(base):
	p = subprocess.Popen("find {0} -type f".format(base), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#assert p.returncode == 0
	found = [e.strip() for e in p.stdout.readlines()]
	for e in found: assert len(e.split()) == 1
	return found

def flistsize(fs):
	return {e : os.stat(e).st_size for e in fs}

def byino(fs):
	hashed = dict()
	negino = -1
	for e in fs:
		try:
			ino = os.stat(e).st_ino
		except OSError as err:
			logerr('# WARN.. {0}\n'.format(str(err))) 
			ino = negino # use a new negative ino for each unresolved ino
			negino = negino - 1
			
		if not ino in hashed: hashed[ino] = list()
		hashed[ino].append(e)
	hashed2 = dict()
	full_flist = dict()
	for k,v in hashed.items():
		sortedfiles = sorted(v, key = lambda x: (len(x),  os.path.basename(x)) )
		hashed2[k] =  sortedfiles[0]
		assert not sortedfiles[0] in full_flist
		full_flist[sortedfiles[0]] = sortedfiles[1:]
	return (hashed2, full_flist)


def make_filereport(patterns, base):
	logerr('# looking in {0}\n'.format(base))
	fbyino, flist = dict(), dict()
	for p in patterns:
		found = findfiles(base, p)
		(a, b) = byino(found)
		fbyino[p] = a
		flist[p] = b	
	return {'byino' : fbyino, 'flist':flist}	


def main(cfg):
	args = cfg.get_values()

	filereport = True
	assert len(args) == 1, '__only_pass_one_target_directory_at_a_time__'

	arg = args[0]
	print2('# analyzing:', arg)
	

		
	config = jloadf(cfg.or_else("-cleanup",   './cleanup.json'))
	outdir = cfg.option('-outdir')

	try:
		os.mkdir(outdir)
	except Exception as err:
		print2('#__could not create__' + outdir)

	patterns = config["patterns"]
	assert not "extra" in patterns
	output = make_filereport(patterns, arg) 
	short_out = {k: sorted(output['flist'][k].keys()) for k in output['flist']}
	allfiles = listfiles(arg)

	
	
	patternfiles = list()
	unresolvedlinks = list()
	for p in patterns:
		record = output
		#print p, sum(flistsize(record['flist'][p]).values())/10**9,  'GB approx'
		patternfiles.extend(record['flist'][p].keys() +  [e for k in record['flist'][p]  for e in record['flist'][p][k]]    ) 
		unresolvedlinks.extend([record['byino'][p][z] for z in record['byino'][p] if z < 0]) 
	
	extra = [f for f in allfiles if not f in patternfiles]

	print2(jdumpf(outdir + '/filereport.json', output))
	print2(jdumpf(outdir + '/file_shortreport.json', short_out))
	
	rmlist = list()
	rmsize = 0
	for ftype in config["delete"]:
		for k in record['flist'][ftype]:
			rmlist.extend(record['flist'][ftype][k])
			rmlist.append(k)
			try:
				rmsize = rmsize + os.stat(k).st_size
			except Exception as err:
				print2('WARNING: __cannot_read_filesize__:', k, err)

	
	keep, redundant = list(), list()
	for k in record['flist']:
		if not k in config['delete']:
			keeping = [e for e in  record['flist'][k].keys() if not e in rmlist]
			keep.extend(keeping)
			for z in keeping:
				redundant.extend(record['flist'][k][z]) 

		
	keep = sorted(list(set(keep)))

	unexpected = check_extraneous(config["extraneous"], extra)

	print2(dumpf(outdir + '/delete.list', '\n'.join(rmlist) + '\n'))
	print2(dumpf(outdir + '/masterfiles.list', '\n'.join(keep) + '\n'))
	print2(dumpf(outdir + '/extraneous_cromwell.list', '\n'.join(extra) + '\n'))
	print2(dumpf(outdir + '/unresolvedfiles.list', '\n'.join(unresolvedlinks) + '\n'))
	print2(dumpf(outdir + '/unexpectedfiles.list', '\n'.join(unexpected) + '\n'))
	print2(dumpf(outdir + '/redundantlinks.list', '\n'.join(redundant) + '\n'))

	check_fileskept(keep)

	print2("unexpected files?", len(unexpected) > 0 )
	print2( "unresolved files?", len(unresolvedlinks) > 0)
	#print 'size',  sum(flistsize(keep).values())
	
	print2( 'delete.list = ', rmsize)
	print2( '# analyzed:', arg)


if __name__ == '__main__':
	main(Config.sys())


