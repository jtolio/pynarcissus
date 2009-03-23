#!/usr/bin/python2.5

import sys, os, subprocess
sys.path.append(os.path.join(os.pardir, os.pardir))
import jsparser as js

def main(argv):
    try:
        diffcmd = argv[1]
    except:
        diffcmd = "diff" # or tkdiff

    failures = 0

    testfiles = [os.path.join("source", x) for x in os.listdir("source")
                                           if x[-3:] == ".js"]
    for testfile in testfiles:
        failed = False
        py_proc = subprocess.Popen(["./parse_mjsunit.py", testfile],
                stdout=subprocess.PIPE)
        py_parse_tree = py_proc.communicate()[0]
        if py_proc.returncode != 0:
            print "Python parsing failed for %s" % testfile
            failed = True
        js_proc = subprocess.Popen(["./parse_mjsunit.js", testfile],
                stdout=subprocess.PIPE)
        js_parse_tree = js_proc.communicate()[0]
        if js_proc.returncode != 0:
            print "Javascript parsing failed for %s" % testfile
            failed = True
        if failed:
            failures += 1
            continue
        if js_parse_tree != py_parse_tree:
            print "Parse tree mismatch for %s" % testfile
            file("/tmp/js-parse-tree-%d.out" % os.getpid(), 'w').write(
                    js_parse_tree)
            file("/tmp/py-parse-tree-%d.out" % os.getpid(), 'w').write(
                    py_parse_tree)
            subprocess.call([diffcmd, "/tmp/js-parse-tree-%d.out" % os.getpid(),
                    "/tmp/py-parse-tree-%d.out" % os.getpid()])
            failures += 1
            continue

    if failures == 0:
        print "All %d tests passed!" % len(testfiles)
        return 0

    print "%d of %d tests passed" % (len(testfiles) - failures, len(testfiles))
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
