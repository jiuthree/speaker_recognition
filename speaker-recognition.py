#!/usr/bin/env python3

import os
import sys
import itertools
import glob
import argparse
from utils import read_wav
from interface import ModelInterface
import test

def get_args():
    desc = "Speaker Recognition Command Line Tool"
    epilog = """
Wav files in each input directory will be labeled as the basename of the directory.
Note that wildcard inputs should be *quoted*, and they will be sent to glob.glob module.
Examples:
    Train (enroll a list of person named person*, and mary, with wav files under corresponding directories):
    ./speaker-recognition.py -t enroll -i "/tmp/person* ./mary" -m model.out
    Predict (predict the speaker of all wav files):
    ./speaker-recognition.py -t predict -i "./*.wav" -m model.out
"""
    parser = argparse.ArgumentParser(description=desc,epilog=epilog,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-t', '--task',
                       help='Task to do. Either "enroll" or "predict"',
                       required=True)

    parser.add_argument('-i', '--input',
                       help='Input Files(to predict) or Directories(to enroll)',
                       required=True)

    parser.add_argument('-m', '--model',
                       help='Model file to save(in enroll) or use(in predict)',
                       required=True)

    ret = parser.parse_args()
    return ret

def task_enroll(input_dirs, output_model):

    dict_temp=test.prehelp3();

    m = ModelInterface()
    input_dirs = [os.path.expanduser(k) for k in input_dirs.strip().split()]
    dirs = itertools.chain(*(glob.glob(d) for d in input_dirs))
    dirs = [d for d in dirs if os.path.isdir(d)]

    files = []
    if len(dirs) == 0:
        print ("No valid directory found!")
        sys.exit(1)

    for d in dirs:
     #   label = os.path.basename(d.rstrip('/'))    #把这个label给改了
        wavs = glob.glob(d + '/*.flac')

        if len(wavs) == 0:
            print ("No wav file found in %s"%(d))
            continue
        for wav in wavs:
            try:
                (path, filename) = os.path.split(wav)
              #  print(filename)
                basename, ext = os.path.splitext(filename)
                print(basename)
               # print(path)
                label = dict_temp.get(basename)
                print(label)

                fs, signal = read_wav(wav)
                m.enroll(label, fs, signal)
                print("wav %s has been enrolled"%(wav))
            except Exception as e:
                print(wav + " error %s"%(e))

    m.train()
    m.dump(output_model)

def task_predict(input_files, input_model):
    m = ModelInterface.load(input_model)
    dict_temp2 = test.prehelp2();
    count = 0;
    res = 0;
    dict_temp_res = {}
    for f in glob.glob(os.path.expanduser(input_files)):
        count=count+1
        (path, filename) = os.path.split(f)
        print(filename)
        basename, ext = os.path.splitext(filename)
        print(123)
        print(basename)

        fs, signal = read_wav(f)
        label, score = m.predict(fs, signal)

        dict_temp_res[basename]=label

        if label == dict_temp2.get(basename) :
            res=res+1
        print (f, '->', label, ", score->", score)
    print(res)
    print(count)
    print(res*1.00/count)

    test.reshelp(dict_temp_res)

if __name__ == "__main__":
    global args
    args = get_args()

    task = args.task
    if task == 'enroll':
        task_enroll(args.input, args.model)
    elif task == 'predict':
        task_predict(args.input, args.model)
