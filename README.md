[![Build Status](https://travis-ci.org/andypohl/build-chtc.svg?branch=master)](https://travis-ci.org/andypohl/build-chtc)
# build-chtc
Build sandboxed tarballs for portable software use at CHTC.  

## Goals
  * Produce script/submit file to make compiled and tarballed executable for use on HTCondor.
  * The specific commands in the build script are mostly left to the JSON file.  The Python program `build_chtc.py` mostly checks for errors in the JSON file and allows some options.

## What it does
`build_chtc.py` makes two things:
   1. A shell script to compile/build one or more software packages described in a JSON file.
   2. A corresponding HTCondor submit file so that the shell script will run in the HTCondor Pool.
A few minutes after running `condor_submit`, you should have your tarball.  

## What it doesn't do
   * This script builds the software only.  It does not provide you with another submit file or script to run that software through HTCondor.  Example scripts and pipelines will be provided through documentation, Gists, blog posts, etc.  Hints about where to go to find relevant examples should be found in the "Comments" field of a software entry in the JSON file.  

## How do I use this?
Before using the program, look at the [`software.json` file](https://github.com/andypohl/build-chtc/blob/master/software.json) to get a sense of the structure and how different entries are linked together.  Then, log into an HTCondor submit node, clone this repository, and run the program as you need to:

```
[me@laptop:~$ ssh submit
[me@submit:~$ git clone https://github.com/andypohl/build-chtc
[me@submit:~$ cd build-chtc/
[me@submit:~/build-chtc$ ./build_chtc.py R 3.3.2
[me@submit:~/build-chtc$ condor_submit R-3.3.2.submit
```
