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
		return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, stdout.decode("utf-8"), stderr.decode("utf-8"), shell_command.returncode, shell_command.pid])) 
	except Exception as err: 
		if not shell_command:  
			raise err        
	shell_command.terminate() 
	return dict(zip(['cmd', 'out', 'err', 'return', 'pid'], [cmd, '', 'EXCEPTION:{0}'.format(str(err)), -1, -1]))	

def rename(files):
	meta = utilsm.jloadf('./postprocess/meta.json')
	bam = uniq(files['merged.nodup.bam'])
	assay = meta[os.path.basename(bam)]
	prefix = meta[assay]
	for ftype, fs in files.items():
		f = uniq(fs)
		print(f, './postprocess/temp/{0}.{1}'.format(prefix, ftype))
		os.symlink(f, './postprocess/temp/{0}.{1}'.format(prefix, ftype))


class ENCODEChIP:	
	def __init__(self):
		self.echo_only =  True
		self.commands = list()
		self.base = os.path.dirname(os.path.realpath(__file__))
		self.bamcoverage = '{0}/bamcoverage'.format(self.base)
		self.bamstrip = '{0}/bamstrip'.format(self.base) 
		self.fasta = 'GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta.tar'
		self.image = '/projects/edcc_new/e/chip-may20/integrative_analysis_chip/encode-wrapper/images/chip_seq_pipeline_v1_1_4-sambamba-0_7_1-rev1.sif'
	def nodupbam(self, base, ctl=False):
		tag = 'call-filter' if not ctl else 'call-filter_ctl'
		pattern = '{0}/{1}/*/execution/*nodup.bam'.format(base, tag)
		return glob.glob(pattern)

	def files(self, base):
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
		noseq = bam[0:-3] + 'noseq.gz'
		sig = bam[0:-3] + 'raw.bigwig'
		if not os.path.exists(sig): sig = None
		if not os.path.exists(noseq): noseq = None
		return {'merged.nodup.bam' : [bam], 'raw.bigwig':[sig],  'noseq.gz':[noseq]}

	def cromwelldir(self, log, opts=None):
		if not opts: opts = dict()
		lines = utilsm.linesf(log)
		fasta = uniq([e for e in lines if e.find(self.fasta) != -1 and e.find('/call-bwa/') != -1]) 
		tags = fasta.strip().split('/call-bwa/')      
		if 'checkok'  in opts:
			assert lines[-1].strip() == "return:0" 
		return tags[0] 

	def try_cromwell_config(self, cromwell):
		try:
			cfg = utilsm.jloadf(cromwell + '/config.json')
		except:
			cfg = dict()   
		return cfg	

	def fragment_size_log(self, base):
		return glob.glob('{0}/call-xcor/*/*fraglen.txt'.format(base)) 

	def postprocess(self, cromwell, ctl=False):
		out = dict()
		bam = uniq(self.nodupbam(cromwell, ctl))
		cfg = self.try_cromwell_config(cromwell)
		fragment = int(uniq(utilsm.linesf(fragment_size_log(cromwell))))
		return self.postprocess_tasks(bam, pet=True, fragment=fragment)

	def postprocess_tasks(self, bam, pet, fragment):
		for script in ['bamstrip', 'bamcoverage']:
			args = {
				'script' : self.base + '/' +  script,
				'bam' : os.path.realpath(bam),
				'additional' : ''
			}
			if not pet and script in ['bamcoverage']: 
				args['additional'] = fragment
			args['binds'] = self.base + ',' + os.path.dirname(args['bam']) 
			args['image'] = self.image 
			cmd = 'singularity exec -B {binds} {image} {script} {bam} {additional}'.format(**args)	
			out[script] = shell(cmd) if not self.echo_only else shell('echo ' + cmd)
			out[script]['outfile'] = ''
			self.commands.append(cmd + '\n\n')
		return out	



encode = ENCODEChIP()


def main(args):
	vals = [e for e in args if not e[0] in '-']
	if '-cromwelldir' in args:
		for e in vals:
			cromwell =  encode.cromwelldir(e,opts= {'checkok':True})
			#print(os.path.basename(e), cromwell, encode.nodupbam(cromwell))
			print('#', e, cromwell)
			files = encode.files(cromwell)

			#rename(files)
			
			print(utilsm.jsonp(files))
			#out = encode.postprocess(cromwell)
			#print(utilsm.jsonp(out))
		print(utilsm.writef("./commands.sh", encode.commands) )
	elif '-nodupbam' in args:
		for e in vals:
			print('#', e)
			print(encode.postprocessedfiles(e, '-ctl' in args))
	elif '-testprod' in args:
		for e in vals:
			log = encode.postprocess(e, ctl=True)
			files = encode.files(e)
			Json.pp(log)
			Json.pp(files)

if __name__ == '__main__':
	main(sys.argv[1:])
