[![Build Status](https://travis-ci.org/andypohl/build-chtc.svg?branch=master)](https://travis-ci.org/andypohl/build-chtc)
# build-chtc
Build sandboxed tarballs for portable software use at CHTC.  

## Why? 
Automating the process of compiling software from source code isn't the primary goal here.  Proficient use of this program makes the process fairly automatic, but I think it's more important to be easy to use.  But a program that's easy to use might also have no features or complexity.  Therefore, the emphasis is on having just a few features that are easy to remember vs having the kitchen sink in there.

Another goal is to not to have to start from scratch every single time you make one of these sandboxed tarballs.  For example, if we've already conquered the task of making a tarball with R installed inside, why not just start from this tarball when building a new tarball with more R packages installed?

Reproducibility is important and `build_chtc.py` establishes a framework with this in mind from the get-go.  The JSON file is a human-readable database of open source software including versions, dates, download URLs, and which versions of what libraries are used to build an executable.  

## What it does
`build_chtc.py` makes two things:
   1. A shell script to compile/build one or more software packages described in a JSON file.
   2. A corresponding HTCondor submit file so that the shell script will run in the HTCondor Pool.
A few minutes after running `condor_submit`, you should have your tarball.  

## What it doesn't do
   * This script builds the software only.  It does not provide you with another submit file or script to run that software through HTCondor.  Example scripts and pipelines will be provided through documentation, Gists, blog posts, etc.  Hints about where to go to find relevant examples should be found in the "Comments" field of a software entry in the JSON file.  

## How do I use this?
Before using the program, study the [`software.json` file](https://github.com/andypohl/build-chtc/blob/master/software.json) to get a sense of the structure and how different entries are linked together.  Then, log into an HTCondor submit node, clone this repository, and run the program as you need to:

```
[me@laptop:~$ ssh submit-5.chtc.wisc.edu
[me@submit-5.chtc.wisc.edu:~$ git clone https://github.com/andypohl/build-chtc
[me@submit-5.chtc.wisc.edu:~$ cd build-chtc/
[me@submit-5.chtc.wisc.edu:~/build-chtc$ ./build_chtc.py R 3.3.2
[me@submit-5.chtc.wisc.edu:~/build-chtc$ condor_submit R-3.3.2.submit
```
