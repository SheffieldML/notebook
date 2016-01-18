import urllib2, os, sys

model_path =  'digit_bgplvm_demo.pickle' # local name for model file
status = ""

re = 0
if len(sys.argv) == 2:
    re = 1

if re or not os.path.exists(model_path): # only download the model new, if it was not already
    url = 'http://staffwww.dcs.sheffield.ac.uk/people/J.Hensman/digit_bgplvm_demo.pickle'
    with open(model_path, 'w') as f:
        u = urllib2.urlopen(url)
        f = open(model_path, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s" % (model_path)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buff = u.read(block_sz)
            if not buff:
                break
            file_size_dl += len(buff)
            f.write(buff)
            sys.stdout.write(" "*(len(status)) + "\r")
            status = r"{:7.3f}/{:.3f}MB [{: >7.2%}]".format(file_size_dl/(1.*1e6), file_size/(1.*1e6), float(file_size_dl)/file_size)
            sys.stdout.write(status)
            sys.stdout.flush()
        sys.stdout.write(" "*(len(status)) + "\r")
        print status
else:
    print "Already cached, to reload run with 'reload' as the only argument"