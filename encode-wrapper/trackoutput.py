from utilsm import *
import os
import sys



def findfiles(base, pattern):
	cmd = "find {0} -name '{1}'".format(base, pattern)
	print cmd
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return [e.strip() for e in p.stdout.readlines()]


def flistsize(fs):
	return {e : os.stat(e).st_size for e in fs}

def byino(fs):
	hashed = dict()
	for e in fs:
		ino = os.stat(e).st_ino 
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

def md5script(hashed):
	def cmd(f):
		if f.strip().endswith('bam'):
			return 'echo "{1} $(./headlessbam_md5 {0})"'.format(f, os.path.basename(f))
		else:
			return 'echo "{1} $(md5sum {0})"'.format(f, os.path.basename(f))
			
	return [cmd(v) for v in sorted(hashed.values(), key= lambda x: os.path.basename(x))]

def trackoutput(base, i, filereport):
	logerr('# looking in {0}\n'.format(base))
	bams = findfiles(base, '*.bam')
	narrowpeaks = findfiles(base, '*narrow*gz')
	(bamsbyino, bams_flist) = byino(bams)
	(peaksbyino, peaks_flist) = byino(narrowpeaks)

	if not filereport:
		print writef('./computemd5s_{0}'.format(i),  ['#!/bin/bash'] + md5script(bamsbyino) + md5script(peaksbyino)) 
	
	qc = findfiles(base, 'qc.html')	
	print qc

	return { 'bams' : bams_flist, 'peaks' : peaks_flist, 'qc' : qc   }



def make_filereport(patterns, base):
	logerr('# looking in {0}\n'.format(base))
	fbyino, flist = dict(), dict()
	for p in patterns:
		found = findfiles(base, p)
		(a, b) = byino(found)
		fbyino[p] = a
		flist[p] = b	
	return {'byino' : fbyino, 'flist':flist}	


def main(args):
	filereport = '-filereport' in args
	args = [e for e in  args if not e in ['-filereport'] ]
	assert len(args) == 1
	targets = ['.'] if len(args) == 0 else args
	output = list()
	keep = list()
	
	patterns = jloadf('patterns.json')
	for i, arg in enumerate(targets):
		if filereport:
			record = make_filereport(patterns, arg) 
			output.append(record)
			for p in patterns:
				print p, sum(flistsize(record['flist'][p]).values())/10**9,  'GB approx'
				keep.extend(record['flist'][p])
		else:
			record = trackoutput(arg, i, filereport)
			output.append(record)
			keep.extend(record['bams'])
			keep.extend(record['peaks'])
		
	print jdumpf('./filereport.json', output)
	print writef('./keep.filelist', keep)	
	print 'size',  sum(flistsize(keep).values())
	
	

if __name__ == '__main__':
	main(sys.argv[1:])



