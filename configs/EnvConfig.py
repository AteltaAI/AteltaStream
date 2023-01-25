import os 

DATADIR='.data/'

if not os.path.isdir(DATADIR):
    os.mkdir(DATADIR)
else:
    print("=> DATADIR already exists")