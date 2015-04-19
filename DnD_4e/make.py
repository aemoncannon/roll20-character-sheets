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

def template_sum_range(attr, i, j):
    """Evaluates to the sum of attr[i] + attr[i+1]... atr[j]."""
    return "+".join([("@{%s%s}" % (attr, ea)) for ea in range(i, j+1)])

def el_in(attr, tpe="text", cls="", extra=""):
    return "<input class='%s' type='%s' name='%s' value='%s' %s/>" % (cls, tpe, "attr_" + attr.name, attr.value, extra)

def in_check(attr, checked=False, cls=""):
    if checked:
        return el_in(attr, tpe="checkbox", cls=cls, extra="checked='checked'")
    else:
        return el_in(attr, tpe="checkbox", cls=cls)

def in_text(attr, cls=""):
    return el_in(attr, cls=cls)

def in_num(attr, cls="", minimum="0", step="1"):
    return el_in(attr, tpe="number", cls=cls, extra="min='%s' step='%s'" % (minimum, step))

def out_text(attr, cls=""):
    return el_in(attr, cls=cls, extra="disabled='disabled'")

def out_num(attr, cls=""):
    return el_in(attr, tpe="number", cls=cls, extra="disabled='disabled'")

all_attrs = {}

class Attr(object):

    def __init__(self, name, value=""):
        self.name = name
        self.value = value
        all_attrs[self.name] = self

    def __str__(self):
        return self.name

class Roll(object):

    def __init__(self, name, value=""):
        self.name = name
        self.value = value
        all_attrs[self.name] = self

    def __str__(self):
        return self.name

class Group(object):

    def __init__(self, name, attrs):
        self.attrs = attrs
        all_attrs[name] = self

    def __getattr__(self, name):
        return self.attrs[name]

# Inputs
Attr("is_npc", value="2")
Attr("char_class")
Attr("race")
Attr("character_name")
for abil in ["strength", "constitution", "dexterity", "intelligence", "wisdom", "charisma"]:
    a = Attr(abil)
    b = Attr(abil + "_mod", value="(floor((@{%s}-10)/2))" % abil)
    c = Attr(abil + "_mod_plus_half_lev", value="@{%s_mod} + floor(@{level}/2)" % abil)
    d = Roll("roll_%s_Check" % abil.capitalize(),
             "&{template:4eDefault} {{character_name=@{character_name}}} {{save=1}} {{title=%s check}} {{subheader=@{character_name}}} {{rollname=%s check}} {{roll=[[ 1d20 + @{%s_mod} + (@{global_saving_bonus}) ]]}} {{rolladv=[[ 1d20 + @{%s_mod} + (@{global_saving_bonus}) ]]}} @{classactionstrengthsave}" % (abil, abil, abil, abil))
    Group("grp_" + abil[0:3], {'ability': a, 'mod': b, 'mod_plus_half_lev': c, 'roll': d, 'label': abil[0:3].upper()})
    
t = pyratemp.Template(filename="DnD_4e.html.template")

vars = {}
vars.update(all_attrs)
vars.update(
    dict(max=template_max,
         min=template_min,
         gteq=template_gteq,
         lt=template_lt,
         lteq=template_lteq,
         gt=template_gt,
         eq=template_eq,
         neg=template_neg,
         sum_range=template_sum_range,
         in_check=in_check,
         in_num=in_num,
         in_text=in_text,
         out_num=out_num,
         out_text=out_text
     ))
result = t(**vars)
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

