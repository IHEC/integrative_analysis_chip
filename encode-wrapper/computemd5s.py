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

	return { 'bams' : bams_flist, 'peaks' : peaks_flist, 'qc' : byino(qc)[1]}





def main(args):
	assert len(args) == 2, '__only_one_target_directory_at_a_time__'
	[targets, tag] = args #['.'] if len(args) == 0 else args
	output = list()
	keep = list()
	
	for i, arg in enumerate([targets]):
		record = trackoutput(arg, tag, False)
		output.append(record)
		keep.extend(record['bams'])
		keep.extend(record['peaks'])
		
	print jdumpf('./filereport.json', output)
	print jdumpf('./file_shortreport.json', map(lambda o: {k: sorted(o[k].keys()) for k in o}, output))
	print 'size',  sum(flistsize(keep).values())
	
	

if __name__ == '__main__':
	main(sys.argv[1:])



