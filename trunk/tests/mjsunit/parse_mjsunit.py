#!/usr/bin/python2.5

import sys, os
sys.path.append(os.path.join(os.pardir, os.pardir))
import jsparser as js

def main(argv):
    try:
        filename = argv[1]
        source = file(filename, "r").read()
    except:
        print "Usage: %s <source.js>" % argv[0]

    print str(js.parse(source, filename))

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
