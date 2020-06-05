import glob
import sys
import os
import subprocess
import json

from . import utilsm
from . import localutils


def logerr(args):
	print(*args)


def uniq(es):
	assert len(es) == 1, es
	return es[0]

def shell(cmd):  
	shell_command = None 
	try:
		shell_command = subprocess.Popen(cmd, shell=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		[stdout, stderr] = shell_command.communicate() 
		return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, stdout.decode("utf-8"), stderr.decode("utf-8"), shell_command.returncode, shell_command.pid])) 
	except Exception as err: 
		if not shell_command:  
			raise err        
	shell_command.terminate() 
	return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, '', 'EXCEPTION:{0}'.format(str(err)), -1, -1]))	



class ENCODEChIP:	
	def __init__(self, image):
		"""
			Args:
				image: The ENCODE ChIP container image to use
		"""
		self.dryrun =  True
		self.commands = list()
		self.base = os.path.dirname(os.path.realpath(__file__))
		self.fasta = 'GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta.tar'
		self.image = image 
	def nodupbam(self, base, ctl=False):
		tag = 'call-filter' if not ctl else 'call-filter_ctl'
		pattern = '{0}/{1}/*/execution/*nodup.bam'.format(base, tag)
		return glob.glob(pattern)

	def files(self, base):
		"""Function to list tracked files in `base` dircetory

        Args:
            base: Target directory

        Returns:
            A hash containing a list of tracked files by filetype. If post processed files are not prosent then the relevant keys are set to `None`

		"""

		hashed =  self.postprocessedfiles(base)
		hashed['qc.html'] = glob.glob('{0}/call-qc_report/execution/qc.html'.format(base))
		hashed['qc.json'] = glob.glob('{0}/call-qc_report/execution/qc.json'.format(base))
		hashed['pval.signal.bigwig'] = glob.glob('{0}/call-macs2/*/execution/*pval.signal.bigwig'.format(base))
		hashed['fc.signal.bigwig'] = glob.glob('{0}/call-macs2/*/execution/*fc.signal.bigwig'.format(base))
		hashed['pval0.01.500K.narrowPeak.gz'] = glob.glob('{0}/call-macs2/*/execution/*merged.nodup_x_ctl_for_rep1*pval0.01.500K.narrowPeak.gz'.format(base))
		hashed['pval0.01.500K.bfilt.narrowPeak.gz'] = glob.glob('{0}/call-macs2/*/execution/*merged.nodup_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.gz'.format(base))
		return hashed

	def postprocessedfiles(self, base, ctl=False):
		bam = uniq(self.nodupbam(base, ctl))
		noseq = bam[0:-3] + 'noseq.bam'
		sig = bam[0:-3] + 'raw.bigwig'
		if not os.path.exists(sig): sig = None
		if not os.path.exists(noseq): noseq = None
		return {'merged.nodup.bam' : [bam], 'raw.bigwig':[sig],  'noseq.bam':[noseq]}

	def cromwelldir(self, log, opts=None):
		if not opts: opts = dict()
		lines = utilsm.linesf(log)
		fasta = uniq([e for e in lines if e.find(self.fasta) != -1 and e.find('/call-bwa/') != -1]) 
		tags = fasta.strip().split('/call-bwa/')      
		if 'checkok'  in opts:
			assert lines[-1].strip() == "return:0" 
		return tags[0] 


	def fragment_size_log(self, base):
		target = '{0}/call-xcor/*/*/*fraglen.txt'.format(base)
		logs = glob.glob(target)
		return uniq(logs)

	def postprocess(self, cromwell, ctl=False, pet=True):
		"""Function to post process analysis in `cromwell` dircetory

		Args: 
			cromwell: directory containing analysis
			ctl: `True` if control bam is to be post processed else `False`
			pet: `True` if PET else False
		
		Returns:
			A hash containing the post processing process stderr, stdout and exits status

		"""

		out = dict()
		bam = uniq(self.nodupbam(cromwell, ctl))
		fragment_logfile =  self.fragment_size_log(cromwell)
		fragment = int(uniq(utilsm.linesf(   fragment_logfile   )))
		logerr(["__info__", bam,  fragment_logfile,  fragment, "pet =", pet, "ctl =" , ctl])
		return self.postprocessing_tasks(bam, pet=pet, fragment=fragment)

	def postprocessing_tasks(self, bam, pet, fragment):
		out = dict()
		for script in ['postprocess.sh']:
			args = {
				'script' : self.base + '/' +  script,
				'bam' : os.path.realpath(bam),
				'additional' : ''
			}
			if not pet and script in ['postprocess.sh']: 
				args['additional'] = fragment
			args['binds'] = self.base + ',' + os.path.dirname(args['bam']) 
			args['image'] = self.image 
			cmd = 'singularity exec -B {binds} {image} {script} {bam} {additional}'.format(**args)	
			out[script] = shell(cmd) if not self.dryrun else shell('echo ' + cmd)
			out[script]['outfile'] = ''
			self.commands.append(cmd + '\n\n')
		return out	






if __name__ == '__main__':
	main(sys.argv[1:])
