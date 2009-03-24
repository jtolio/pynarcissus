#!/usr/bin/python2.5

import sys, os, subprocess

def main(argv):
    try:
        diffcmd = argv[1]
    except:
        diffcmd = "diff" # or tkdiff
    try:
        testfiles = [argv[2]]
    except:
        testfiles = [os.path.join("source", x) for x in os.listdir("source")
                                               if x[-3:] == ".js"]
    failures = 0

    for testfile in testfiles:
        py_proc = subprocess.Popen(["./parse_mjsunit.py", testfile],
                stdout=subprocess.PIPE)
        js_proc = subprocess.Popen(["./parse_mjsunit.js", testfile],
                stdout=subprocess.PIPE)

        failed = False

        py_parse_tree = py_proc.communicate()[0]
        if py_proc.returncode != 0:
            sys.stdout.write("Python parsing failed for %s\n" % testfile)
            failed = True

        js_parse_tree = js_proc.communicate()[0]
        if js_proc.returncode != 0:
            sys.stdout.write("Javascript parsing failed for %s\n" % testfile)
            failed = True

        if failed:
            return 1

        if js_parse_tree != py_parse_tree:
            sys.stdout.write("Parse tree mismatch for %s\n" % testfile)
            file("/tmp/js-parse-tree-%d.out" % os.getpid(), 'w').write(
                    js_parse_tree)
            file("/tmp/py-parse-tree-%d.out" % os.getpid(), 'w').write(
                    py_parse_tree)
            subprocess.call([diffcmd, "/tmp/js-parse-tree-%d.out" % os.getpid(),
                    "/tmp/py-parse-tree-%d.out" % os.getpid()])
            failures += 1

        else:
            sys.stdout.write(".")
            sys.stdout.flush()

    if failures == 0:
        sys.stdout.write("All %d tests passed!\n" % len(testfiles))
        return 0

    sys.stdout.write("%d of %d tests passed.\n" % (len(testfiles) - failures,
            len(testfiles)))
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
