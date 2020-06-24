import utilsm
import sys
sys.path.append("..")
import time
import postprocess # import post processing module



def logerr(args):
	print(*args)

def checkreadcounts(log):
	nodupflagstats = utilsm.jloadf(log['files']['qc.json'][0])
	return -1



def tag():
	current = time.ctime().split()
	return ('-'.join(current[1:3] + [current[-1], current[-2]])).replace(':', '.')

# singularity image to use for post processing
image =  '/projects/edcc_new/e/chip-may20/integrative_analysis_chip/encode-wrapper/images/chip_seq_pipeline_v1_1_4-sambamba-0_7_1-rev1.sif'
encode = postprocess.ENCODEChIP(image)
encode.dryrun = False # set this to False to run the analysis, otherwise this will just echo the command it will run
#encode.dryrun = True



def analyze(analysis_dir, ctl):
	"""
		Args:
			analysis_dir: analysis directory to post process
			ctl: `True` if control is to be processed

		Returns:
			A hash containing tracked fileslist and process status and output
	"""
	cromwell = analysis_dir + '/cromwell_dir' # set cromwell directory
	cfg = utilsm.jloadf(analysis_dir + '/config.json') # pull config
	pair_end = cfg['chip.paired_end'] # get paired end status
	assert pair_end in [True, False]
	logerr([cromwell, pair_end])
	out = encode.postprocess(cromwell, ctl=ctl, pet=pair_end) # call post processing
	out['files'] = encode.files(cromwell) # get list of filesi
	if not out["postprocess.sh"]['return'] in [0]:
		print('#__failed__', analysis_dir)
	return out



def utils(args):
	vals = [e for e in args if not e[0] in '-']
	if '-cromwelldir' in args:
		for e in vals:
			cromwell =  encode.cromwelldir(e,opts= {'checkok':True})
			print('#', e, cromwell)
			files = encode.files(cromwell)
			if "-rename" in args:
				localutils.rename(files, "./bamstrip/nodupbams")
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


def main(args, tagname=None):
	tagname = '' if not tagname else '.{0}'.format(tagname) 
	tasktag = tag() + tagname

	logfile = "./{0}.json".format(tasktag)
	log = dict()
	for i, e in enumerate(args):
		e = e.strip()
		assert not e in log
		log[e] = dict()
		log[e]['ctl'] = analyze(e, ctl=True)	
		log[e]['assay'] = analyze(e, ctl=False)
		print(utilsm.jdumpf("./logs/{1}.{0}.json".format(i, tasktag), log[e]) )
	print(utilsm.jdumpf(logfile, log))
	
def cfg(args):
	flags = [e for e in args if e[0] in '-']
	values = [e for e in args if not e[0] in '-']
	tag = None if not '-tag' in args else args[args.index('-tag') + 1]
	if '-testpath' in flags:
		flist = [args[0]]
	else:
		flist = utilsm.linesf(args[0])
	return (flist, tag)

if __name__ == '__main__':
	args = sys.argv[1:]
	if '-utils' in args:
		utils(args)
	else:
		flist, tagname = cfg(args) 
		main(flist, tagname = tagname)

