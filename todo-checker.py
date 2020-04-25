#!/usr/bin/env python

import os
import subprocess
from datetime import datetime

# 1. Open and write to readme.md file
outfile = open('readme.md', 'r+')
outfile.truncate(0)
outfile.write('## Personal Learning Weekly Snippet\n\n')
outfile.write('### Overview\n')
outfile.write(r'This is a personal snippet for weekly recap and self-improvement only. Cannot guarantee 100% correct.')
outfile.write('\n\n### TODO Debt\n')
# 2. Find all TODOs in the weekly snippet.
# 3. Do word counting
def processOneMonth(path):
    counts = 0
    todos = [[],[],[]]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files.sort(key = lambda file: int(file.split('-')[1][:-3]))
    for f in files:
        count, todo = processOneFile(os.path.join(path, f))
        counts += count
        todos[0].extend(todo[0])
        todos[1].extend(todo[1])
        todos[2].extend(todo[2])
    return counts, todos

def processOneFile(file):
    totalWords = 0
    todos = [[],[],[]]
    with open(file) as f:
        for line in f:
            if line and line.strip():
                # not counting reference
                if line.startswith('reference'):
                    break
                totalWords += countLine(line)
                if line.startswith('TODO'):
                    order = int(line[6])
                    todos[order].append(line.split(':')[1].strip())
    return totalWords, todos

def countLine(text):
    for char in '-.,\n`()/':
        text = text.replace(char,' ')
    text = text.lower()
    return len(text.split())

def writeOneTypeTODO(file, todos):
    for todo in todos:
        file.write('- ' + todo + '\n')

def writeWordCountAndOtherInfo(file, count):
    file.write('### Other Info\n')
    file.write('Total words: ' + str(count) + '\n')
    file.write('P0: will do in the following weeks\n')
    file.write('P1: will do before starting to learn other topics\n')
    file.write('P2: one potential new topic\n')

totalWords = 0
totalTODOs = [[],[],[]]
for root, dirs, files in os.walk(".", topdown=True):
    dirs[:] = [d for d in dirs if not d[0] == '.']
    for name in dirs:
        one_month_dir = os.path.join(root, name)
        words, todos = processOneMonth(one_month_dir)
        totalWords += words
        totalTODOs[0].extend(todos[0])
        totalTODOs[1].extend(todos[1])
        totalTODOs[2].extend(todos[2])
outfile.write('#### P0\n')
writeOneTypeTODO(outfile, totalTODOs[0])
outfile.write('#### P1\n')
writeOneTypeTODO(outfile, totalTODOs[1])
outfile.write('#### P2\n')
writeOneTypeTODO(outfile, totalTODOs[2])
writeWordCountAndOtherInfo(outfile, totalWords)
# 4. commit changes in Git
subprocess.run(["git", "add", "."])
now = datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M:%S")
subprocess.run(["git", "commit", "-m", "auto-refresh TODO Debt " + timeString])
subprocess.run(["git", "push", "origin", "master"])