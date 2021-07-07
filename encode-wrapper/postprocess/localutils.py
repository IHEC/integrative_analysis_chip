from . import utilsm
import os

def rename(files, out):
    meta = utilsm.jloadf('{0}/meta.json'.format(os.path.dirname(os.path.realpath(__file__))))
    bam = utilsm.uniq(files['merged.nodup.bam'])
    assay = meta[os.path.basename(bam)]
    prefix = meta[assay]
    for ftype, fs in files.items():
        f = utilsm.uniq(fs)
        print(f, '{2}/{0}.{1}'.format(prefix, ftype, out))
        os.symlink(f, '{2}/{0}.{1}'.format(prefix, ftype, out))



