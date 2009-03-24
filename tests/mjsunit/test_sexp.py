#!/usr/bin/python2.5

import sys, os, subprocess
sys.path.append(os.path.join(os.path.pardir, os.path.pardir))
import sexp, jsparser as js

def main(argv):
    try:
        testfiles = [argv[1]]
    except:
        testfiles = [os.path.join("source", x) for x in os.listdir("source")
                                               if x[-3:] == ".js"]

    for testfile in testfiles:
        try:
            sexp.convert(js.parse(file(testfile, 'r').read()))
        except Exception, e:
            print "Failure in converting %s to s-expressions\n%s" % (testfile,
                    e)
            return 1
        sys.stdout.write(".")
        sys.stdout.flush()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
