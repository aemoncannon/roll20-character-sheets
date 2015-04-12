import pyratemp

def template_min(x, y):
    """Evaluates to the min of the two inputs."""
    return "((((%s) + (%s)) - abs((%s) - (%s))) / 2)" % (x,y,x,y)

def template_max(x, y):
    """Evaluates to the max of the two inputs."""
    return "((((%s) + (%s)) + abs((%s) - (%s))) / 2)" % (x,y,x,y)

def template_gteq(x, y):
    """Evaluates to 1 if x >= y, 0 otherwise."""
    return "( 1 - (floor(((%s) - 1 - (%s) ) / ( abs((%s) - 1 - (%s) ) + 0.001 ) ) + 1 ))" % (y,x,y,x)

def template_lt(x, y):
    """Evaluates to 1 if x < y, 0 otherwise."""
    return template_gteq(y, x)

def template_lteq(x, y):
    """Evaluates to 1 if x <= y, 0 otherwise."""
    return "( floor( ( (%s) - (%s) ) / ( abs( (%s) - (%s) ) + 0.001 ) ) + 1 )" % (y,x,y,x)

def template_gt(x, y):
    """Evaluates to 1 if x > y, 0 otherwise."""
    return template_lteq(y, x)

def template_eq(x, y):
    """Evaluates to 1 if x == y, 0 otherwise."""
    return template_lteq(y, x) + "*" + template_gteq(y, x)

def template_neg(x):
    """Evaluates to 1 if x == 0, 0 if x == 1."""
    return template_eq(x, "0")

t = pyratemp.Template(filename="DnD_4e.html.template")
result = t(max=template_max, min=template_min, gteq=template_gteq, lt=template_lt, lteq=template_lteq, gt=template_gt, eq=template_eq, neg=template_neg)
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

