import urllib, tarfile, gzip, os, shutil, pandas as pd
dataname = 'abalone.pickle'
if not os.path.exists(dataname):
    filename = 'abalone.tar.gz'
    # Download tmp data:
    urllib.urlretrieve('ftp://ftp.cs.toronto.edu/pub/neuron/delve/data/tarfiles/abalone.tar.gz', filename)
    # Extract data folder:
    with tarfile.open(filename, mode='r:gz') as t:
        t.extract('abalone/Dataset.data.gz')
        t.extract('abalone/Dataset.spec')    # Extract data
    with gzip.open('abalone/Dataset.data.gz') as t:
        data = pd.read_csv(t, sep=' ', header=None)
    with open('abalone/Dataset.spec') as f:
        start_reading = False
        columns = []
        for line in f.readlines():
            if start_reading:
                columns.append(line[6:26].strip(' '))
            if 'Attributes:' in line:
                start_reading = True
    data.columns = columns
    data.to_pickle('abalone.pickle')
    os.removedirs('abalone')
    os.remove(filename)
else:
    data = pd.read_pickle('abalone.pickle')