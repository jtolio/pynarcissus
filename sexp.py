#!/usr/bin/python2.5

"""
 PyNarcissus S-expression converter.

 Converts a PyNarcissus parse tree into S-expressions.
"""

__author__ = "JT Olds"
__author_email__ = "jtolds@xnet5.com"
__date__ = "2009-03-24"
__all__ = ["convert", "UnknownNode", "OtherError", "ProgrammerError", "Error_"]

class Error_(Exception): pass
class UnknownNode(Error_): pass
class OtherError(Error_): pass
class ProgrammerError(OtherError): pass

import jsparser as js

def o(n, i, handledattrs=[]):
    attrs_ = {}
    for attr in handledattrs:
        attrs_[attr] = True
    subnodes_ = []
    had_error = False
    def check(attrs=[], optattrs=[], subnodes=0):
        if not (type(attrs) == list and type(optattrs) == list and
                type(subnodes) == int):
            raise ProgrammerError, "Wrong arguments to check(...)!"
        for attr in attrs: attrs_[attr] = True
        for attr in optattrs:
            if hasattr(n, attr): attrs_[attr] = True
        for i in xrange(subnodes):
            subnodes_.append(True)
    try:
        check(attrs=["append", "count", "extend", "filename", "getSource",
                    "indentLevel", "index", "insert", "lineno", "pop",
                    "remove", "reverse", "sort", "tokenizer", "type", "type_"],
                    optattrs=["end", "start", "value"])

        if n.type == "ARRAY_INIT":
            check(subnodes=len(n))
            s = "(array_init"
            for x in n:
                if x is not None:
                    s += " " + o(x,i)
                else:
                    s += " null"
            return s + ")"

        elif n.type == "ASSIGN":
            check(subnodes=2)
            s = "("
            if getattr(n[0],"assignOp", None) is not None:
                s += "update " + js.tokens[n[0].assignOp]
            else:
                s += "assign"
            return s + " %s %s)" % (o(n[0], i, handledattrs=["assignOp"]),
                    o(n[1], i))

        elif n.type == "BLOCK":
            check(subnodes=len(n))
            if len(n) > 0:
                return "(block\n  "+ i + ("\n  "+i).join((o(x,i+"  ")
                        for x in n)) + ")"
            return "(block)"

        elif n.type in ("BREAK", "CONTINUE"):
            check(attrs=["target"], optattrs=["label"])
            if hasattr(n,"label"):
                return "(%s %s)" % (n.value, n.label)
            return "(%s)" % n.value

        elif n.type == "CALL":
            check(subnodes=2)
            return "(call %s%s)" % (o(n[0], i), o(n[1], i))

        elif n.type == "CASE":
            check(attrs=["caseLabel","statements"])
            return "(case %s %s)" % (o(n.caseLabel,i), o(n.statements,i))

        elif n.type == "CATCH":
            check(attrs=["block","guard","varName"])
            if n.guard is not None:
                return "(guarded-catch %s %s %s)" % (n.varName, o(n.guard,i),
                        o(n.block,i))
            return "(catch %s %s)" % (n.varName, o(n.block,i))

        elif n.type == "COMMA":
            check(subnodes=2)
            return "(comma %s %s)" % (o(n[0],i), o(n[1],i))

        elif n.type == "DEBUGGER":
            return "(debugger)"

        elif n.type == "DEFAULT":
            check(attrs=["statements"])
            return "(default %s)" % o(n.statements,i)

        elif n.type in ("DELETE", "TYPEOF", "NEW", "UNARY_MINUS", "NOT",
                "VOID", "BITWISE_NOT", "UNARY_PLUS"):
            check(subnodes=1)
            return "(%s %s)" % (n.value, o(n[0],i))

        elif n.type == "DO":
            check(attrs=["body", "condition", "isLoop"])
            assert n.isLoop
            return "(do-while %s %s)" % (o(n.condition,i), o(n.body,i))

        elif n.type == "DOT":
            check(subnodes=2)
            return "(attribute %s %s)" % (o(n[0],i), o(n[1],i))

        elif n.type == "FUNCTION":
            check(attrs=["functionForm","params","body"],
                    optattrs=["name"])
            if n.functionForm == 0:
                return "(def-function (%s%s) %s)" % (n.name,
                        "".join(" " + param for param in n.params), o(n.body,i))
            else:
                return "(function (%s) %s)" % (" ".join(n.params), o(n.body,i))

        elif n.type == "FOR":
            check(attrs=["body","setup","condition","update","isLoop"])
            assert n.isLoop
            if n.setup is not None: setup = o(n.setup,i)
            else: setup = "(skip)"
            if n.condition is not None: condition = o(n.condition,i)
            else: condition = "(skip)"
            if n.update is not None: update = o(n.update,i)
            else: update = "(skip)"
            if n.body is not None: body = o(n.body,i)
            else: body = "(skip)"
            return "(for %s %s %s\n  %s%s)" % (setup, condition, update, i,
                    body)

        elif n.type == "FOR_IN":
            check(attrs=["body","iterator","object","isLoop","varDecl"])
            assert n.isLoop
            s = "(for-in"
            if n.varDecl:
                assert n.varDecl.type == "VAR"
                assert len(n.varDecl) == 1
                assert n.varDecl[0].type == "IDENTIFIER"
                assert n.varDecl[0].value == n.iterator.value
                s += "-var"
            return s + " %s %s %s)" % (o(n.iterator,i), o(n.object,i),
                    o(n.body,i))

        elif n.type == "GROUP":
            check(subnodes=1)
            return o(n[0],i)

        elif n.type == "HOOK":
            check(subnodes=3)
            return "(ternary %s %s %s)" % (o(n[0],i),o(n[1],i),o(n[2],i))

        elif n.type == "IDENTIFIER":
            check(optattrs=["initializer","name","readOnly"])
#            if getattr(n,"readOnly",False): assert hasattr(n,"initializer")
            if hasattr(n,"name"): assert n.name == n.value
            if hasattr(n,"initializer"):
                return "(initvar %s %s)" % (n.value, o(n.initializer, i))
            return str(n.value)

        elif n.type == "IF":
            check(attrs=["condition","thenPart","elsePart"])
            if n.elsePart:
                return "(if-else %s\n  %s%s\n  %s%s)" % (o(n.condition,i), i,
                        o(n.thenPart,i+"  "), i, o(n.elsePart, i+"  "))
            return "(if_ %s\n  %s%s)" % (o(n.condition,i), i, o(n.thenPart,
                    i+"  "))

        elif n.type in ("INCREMENT", "DECREMENT"):
            check(optattrs=["postfix"], subnodes=1)
            if getattr(n, "postfix", False):
                return "(_%s %s)" % (n.value, o(n[0], i))
            return "(%s_ %s)" % (n.value, o(n[0], i))

        elif n.type == "INDEX":
            check(subnodes=2)
            return "(array-index %s %s)" % (o(n[0],i), o(n[1],i))

        elif n.type == "LABEL":
            check(attrs=["label","statement"])
            return "(labeled-stmt %s\n  %s%s)" % (n.label, i, o(n.statement,
                    i+"  "))

        elif n.type == "LIST":
            check(subnodes=len(n))
            return ''.join((' ' + o(x, i) for x in n))

        elif n.type in ("NUMBER", "TRUE", "FALSE", "THIS", "NULL"):
            return str(n.value)

        elif n.type == "OBJECT_INIT":
            check(subnodes=len(n))
            if len(n) > 0:
                return ("(object_init\n  " + i + ("\n  "+i).join(o(x,i+"  ")
                        for x in n) + ")")
            return "(object_init)"

        elif n.type in ("PLUS", "LT", "EQ", "AND", "OR", "MINUS", "MUL", "LE",
                "NE", "STRICT_EQ", "DIV", "GE", "INSTANCEOF", "IN", "GT",
                "NEW_WITH_ARGS", "BITWISE_OR", "BITWISE_AND", "BITWISE_XOR",
                "STRICT_NE", "LSH", "RSH", "URSH", "MOD"):
            check(subnodes=2)
            return "(%s %s %s)" % (n.value, o(n[0],i), o(n[1],i))

        elif n.type == "PROPERTY_INIT":
            check(subnodes=2)
            return "(property %s %s)" % (o(n[0],i), o(n[1],i))

        elif n.type == "REGEXP":
            return "(regexp %r %r)" % (n.value["regexp"], n.value["modifiers"])

        elif n.type == "RETURN":
            if type(n.value) == str:
                return "(return %r)" % n.value
            return "(return %s)" % o(n.value, i)

        elif n.type == "SCRIPT":
            check(attrs=["funDecls","varDecls"], subnodes=len(n))
#            print "WARNING: skipping funDecls and varDecls"
            return ("(script\n  " + i + ("\n  "+i).join((o(x,i+"  ")
                    for x in n)) + ")")

        elif n.type == "SEMICOLON":
            check(attrs=["expression"])
            if not n.expression: return "(skip)"
            return o(n.expression, i)

        elif n.type == "STRING":
            return repr(n.value)

        elif n.type == "SWITCH":
            check(attrs=["cases", "defaultIndex", "discriminant"])
            assert (n.defaultIndex == -1 or
                    n.cases[n.defaultIndex].type == "DEFAULT")
            return "(switch %s\n  %s%s)" % (o(n.discriminant,i), i,
                    ("\n  "+i).join(o(x,i+"  ") for x in n.cases))

        elif n.type == "THROW":
            check(attrs=["exception"])
            return "(throw %s)" % o(n.exception,i)

        elif n.type == "TRY":
            check(attrs=["catchClauses","tryBlock"], optattrs=["finallyBlock"])
            if hasattr(n,"finallyBlock"):
                return "(try-finally\n  " + i + ("\n  "+i).join(
                        [o(n.tryBlock,i+"  ")] + [o(x,i+"  ")
                        for x in n.catchClauses] + [o(n.finallyBlock,i+"  ")]) \
                        + ")"
            return "(try\n  " + i + ("\n  "+i).join(
                    [o(n.tryBlock,i+"  ")] + [o(x,i+"  ")
                    for x in n.catchClauses]) + ")"

        elif n.type in ("VAR", "CONST"):
            check(subnodes=len(n))
            return ("(%s " % n.value) + " ".join((o(x,i) for x in n)) + ")"

        elif n.type == "WITH":
            check(attrs=["body", "object"])
            print "WARNING: A bad person wrote the code being parsed. Don't " \
                    "use 'with'!"
            return "(with %s %s)" % (o(n.object,i), o(n.body,i))

        elif n.type == "WHILE":
            check(attrs=["condition","body","isLoop"])
            assert n.isLoop
            return "(while %s\n  %s%s)" % (o(n.condition,i), i, o(n.body,
                    i+"  "))

        else:
            raise UnknownNode, "Unknown type %s" % n.type
    except Exception, e:
        had_error = True
        raise OtherError("%s\nException in node %s on line %s" % (e, n.type,
                getattr(n, "lineno", None)))
    finally:
        if not had_error:
            realkeys = [x for x in dir(n) if x[:2] != "__"]
            for key in realkeys:
                if key not in attrs_:
                    raise ProgrammerError, "key '%s' unchecked on node %s!" % (
                            key, n.type)
            if len(realkeys) != len(attrs_):
                for key in attrs_:
                    if key not in realkeys:
                        raise ProgrammerError, ("key '%s' checked "
                                "unnecessarily on node %s!" % (key, n.type))
            if len(subnodes_) != len(n):
                raise ProgrammerError, ("%d subnodes out of %d checked on node "
                        "%s" % (len(subnodes_), len(n), n.type))

def convert(parsetree):
    """Takes a PyNarcissus parse tree and returns a string of S-expressions

    Args:
        parsetree: the PyNarcissus parse tree
    Returns:
        string
    Raises:
        UnknownNode: if a node hasn't been properly accounted for in the
            conversion
        ProgrammerError: if the conversion routine wasn't written with the best
            understanding of the parse tree
        OtherError: if some other error happened we didn't understand.
    """

    return o(parsetree, "") + "\n"

if __name__ == "__main__":
    import sys
    sys.stdout.write(convert(js.parse(sys.stdin.read())))
