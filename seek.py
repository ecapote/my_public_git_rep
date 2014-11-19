#!/usr/bin/python

from sys import argv

script, input_file = argv

#open a file
open_file = open(input_file, "rw+")

print "name of the file: ", open_file.name

line = open_file.readline()
print "Readline is %s" % (line)

pos = open_file.tell()

print "The pos value is %s at start of code" % (pos)

open_file.seek(20)


print "Readline is %s after seek to pos 20" % (line)

print 'POS should be 20 now: %s' % (open_file.tell())
print 'Readline is %s after moving to POS 20. Last LINE' % (open_file.readline())


open_file.seek(40)


print 'POS should be 40 now: %s' % (open_file.tell())
print "Readline is %s after seek to pos 40" % (open_file.readline())
