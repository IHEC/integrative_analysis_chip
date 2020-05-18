import glob
import sys
import os
import subprocess
import json

from . import utilsm


def uniq(es):
	assert len(es) == 1, es
	return es[0]

def shell(cmd):  
	shell_command = None 
	try:
		shell_command = subprocess.Popen(cmd, shell=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		[stdout, stderr] = shell_command.communicate() 
		return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, stdout, stderr, shell_command.returncode, shell_command.pid])) 
	except Exception as err: 
		if not shell_command:  
			raise err        
	shell_command.terminate() 
	return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, '', 'EXCEPTION:{0}'.format(str(err)), -1, -1]))	




class ENCODEChIP:	
	def __init__(self):
		self.base = os.path.realpath(__file__)
		self.bamcoverage = '{0}/bamcoverage'.format(self.base)
		self.bamstrip = '{0}/bamstrip'.format(self.base) 
		self.fasta = 'GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta.tar'
	def nodupbam(self, base, ctl=False):
		tag = 'call-filter' if not ctl else 'call-filter_ctl'
		pattern = '{0}/{1}/*/execution/*nodup.bam'.format(base, tag)
		return glob.glob(pattern)

	def files(self, base):
		hashed = dict()
		hashed['qc'] = glob.glob('{0}/call-qc_report/execution/qc.*'.format(base))
		hashed['pval.signal.bigwig'] = glob.glob('{0}/call-macs2/*/execution/*pval.signal.bigwig'.format(base))
		hashed['fc.signal.bigwig'] = glob.glob('{0}/call-macs2/*/execution/*fc.signal.bigwig'.format(base))
		hashed['macs'] = glob.glob('{0}/call-macs2/*/execution/*merged.nodup_x_ctl_for_rep1*pval0.01.500K.narrowPeak.gz'.format(base))
		hashed['macs-filt'] = glob.glob('{0}/call-macs2/*/execution/*merged.nodup_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.gz'.format(base))
		return hashed

	def cromwelldir(self, log, opts=None):
		if not opts: opts = dict()
		lines = utilsm.linesf(log)
		fasta = uniq([e for e in lines if e.find(self.fasta) != -1 and e.find('/call-bwa/') != -1]) 
		tags = fasta.strip().split('/call-bwa/')      
		if 'checkok'  in opts:
			assert lines[-1].strip() == "return:0" 
		return tags[0] 

	def postprocess(self, base, ctl=False):
		cromwell = base + '/cromwell_dir'
		bam = self.nodupbam(cromwell, ctl)
		cfg = jsonloadf(base + '/config.json')
		

__encode__ = ENCODEChIP()


def main(args):
	encode = __encode__ 
	vals = [e for e in args if not e[0] in '-']
	if '-cromwelldir' in args:
		for e in vals:
			cromwell =  encode.cromwelldir(e,opts= {'checkok':True})
			print(os.path.basename(e), cromwell, encode.nodupbam(cromwell))
			files = encode.files(cromwell)
			print(utilsm.jsonp(files))
	elif '-nodupbam' in args:
		for e in vals:
			print(encode.nodupbam(e))



if __name__ == '__main__':
	main(sys.argv[1:])
