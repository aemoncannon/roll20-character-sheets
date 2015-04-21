import pyratemp

def fn_sum(*args):
    return " + ".join(args)

def fn_prod(*args):
    return " * ".join(args)

def fn_div(arg1, arg2):
    return arg1 + " / " + arg2

def fn_quant(arg):
    return "(" + arg + ")"

def fn_min(x, y):
    """Evaluates to the min of the two inputs."""
    return "((((%s) + (%s)) - abs((%s) - (%s))) / 2)" % (x,y,x,y)

def fn_max(x, y):
    """Evaluates to the max of the two inputs."""
    return "((((%s) + (%s)) + abs((%s) - (%s))) / 2)" % (x,y,x,y)

def fn_gteq(x, y):
    """Evaluates to 1 if x >= y, 0 otherwise."""
    return "( 1 - (floor(((%s) - 1 - (%s) ) / ( abs((%s) - 1 - (%s) ) + 0.001 ) ) + 1 ))" % (y,x,y,x)

def fn_lt(x, y):
    """Evaluates to 1 if x < y, 0 otherwise."""
    return fn_gteq(y, x)

def fn_lteq(x, y):
    """Evaluates to 1 if x <= y, 0 otherwise."""
    return "( floor( ( (%s) - (%s) ) / ( abs( (%s) - (%s) ) + 0.001 ) ) + 1 )" % (y,x,y,x)

def fn_gt(x, y):
    """Evaluates to 1 if x > y, 0 otherwise."""
    return fn_lteq(y, x)

def fn_eq(x, y):
    """Evaluates to 1 if x == y, 0 otherwise."""
    return fn_lteq(y, x) + "*" + fn_gteq(y, x)

def fn_neg(x):
    """Evaluates to 1 if x == 0, 0 if x == 1."""
    return fn_eq(x, "0")

def el_in(attr, tpe="text", cls="", extra=""):
    return "<input class='%s' type='%s' name='%s' value='%s' %s %s/>" % (cls, tpe, "attr_" + attr.name, attr.value, extra)

def in_check(attr, checked=False, cls=""):
    if checked:
        return el_in(attr, tpe="checkbox", cls=cls, extra="checked='checked'")
    else:
        return el_in(attr, tpe="checkbox", cls=cls)

def in_text(attr, cls=""):
    return el_in(attr, cls=cls)

def in_num(attr, cls="", step="1"):
    return el_in(attr, tpe="number", cls=cls, extra="min='%s' step='%s'" % (attr.minimum, step))

def out_hidden(attr):
    return el_in(attr, tpe="hidden", cls=cls, extra="disabled='disabled'", hidden=hidden)

def out_text(attr, cls=""):
    return el_in(attr, cls=cls, extra="disabled='disabled'", hidden=hidden)

def out_num(attr, cls=""):
    return el_in(attr, tpe="number", cls=cls, extra="disabled='disabled'", hidden=hidden)

atts = Group()

class Attr(object):

    def __init__(self, name, value="", minimum=0):
        self.name = name
        self.value = value
        self.minimum = 0
        atts.add_attr(self)

    def __str__(self):
        return "@{" + self.name + "}"

class Roll(object):

    def __init__(self, name, value=""):
        self.name = name
        self.value = value
        atts[self.name] = self

    def __str__(self):
        return self.name

class Group(object):

    def __init__(self, prefix="", suffix=""):
        self.prefix = prefix
        self.suffix = suffix
        self.attrs = {}

    def __getattr__(self, name):
        return self.attrs[name]

    def attr(self, name, value="", minimum=0):
        att = Attr(prefix + name + suffix, value=value, minimum=minimum)
        self.attrs[name] = att
        return att

    def set_label(self, name):
        self.label = label

    def set_roll(self, roll):
        self.roll = roll

    def add_attr(self, attr):
        self.attrs[attr.name] = attr
        return attr

    def get_dict():
        return self.attrs

Attr("is_npc", value="2")
Attr("char_class")
Attr("race")
Attr("character_name")
for abil in ["strength", "constitution", "dexterity", "intelligence", "wisdom", "charisma"]:
    a = Attr(abil, minimum=1)
    b = Attr(abil + "_mod", value="(floor((@{%s}-10)/2))" % abil)
    c = Attr(abil + "_mod_plus_half_lev", value="@{%s_mod} + floor(@{level}/2)" % abil)
    d = Roll("roll_%s_Check" % abil.capitalize(),
             "&{template:4eDefault} {{character_name=@{character_name}}} {{save=1}} {{title=%s check}} {{subheader=@{character_name}}} {{rollname=%s check}} {{roll=[[ 1d20 + @{%s_mod} + (@{global_saving_bonus}) ]]}} {{rolladv=[[ 1d20 + @{%s_mod} + (@{global_saving_bonus}) ]]}} @{classactionstrengthsave}" % (abil, abil, abil, abil))
    Group("grp_" + abil[0:3], {'ability': a, 'mod': b, 'mod_plus_half_lev': c, 'roll': d, 'label': abil[0:3].upper()})

defense_groups = []
for defense in ["ac", "fort", "ref", "will"]:
    g = Group(prefix=(defense + "_"))
    g.attr(defense, value=fn_sum(g.bonus, g.class_bonus, g.misc_bonus, atts.10_plus_half_level))
    if defense == "ac":
        g.attr("ability_bonus", value=atts.armor_bonus)
    elif defense == "fort":
        g.attr("ability_bonus", value=fn_max(atts.strength_mod, atts.constitution_mod))
    elif defense == "ref":
        g.attr("ability_bonus", value=fn_sum(fn_max(atts.dexterity_mod, atts.intelligence_mod), atts.armor_prof_penalty))
    elif defense == "will":
        g.attr("ability_bonus", value=fn_max(atts.wisdom_mod, atts.charism_mod))
    g.attr("class_bonus")
    g.set_label(defense.upper()}
    defense_groups.append(g)


skill_groups = []    
for pair in [('acrobatics', 'dexterity'),
              ('arcana', 'intelligence'),
              ('athletics', 'strength'),
              ('bluff', 'charisma'),
              ('diplomacy', 'charisma'),
              ('dungeoneering', 'wisdom'),
              ('endurance', 'constitution'),
              ('heal', 'wisdom'),
              ('history', 'intelligence'),
              ('insight', 'wisdom'),
              ('intimidate', 'charisma'),
              ('nature', 'wisdom'),
              ('perception', 'wisdom'),
              ('religion', 'intelligence'),
              ('stealth', 'dexterity'),
              ('streetwise', 'charisma'),
              ('thievery', 'dexterity')]:
    skill, abil =  pair
    g = Group(prefix=(skill + "_"))
    g.set_roll(Roll("roll_%s_Check" % skill.capitalize(),
                value=" ".join(["&{template:5eDefault}",
                                "{{ability=1}}",
                                "{{title=%s (%s)}}" % (skill.capitalize(), abil),
                                "{{subheader=@{character_name}}}",
                                "{{subheaderright=Ability check}}",
                                "{{rollname=Result}}",
                                "{{roll=[[ 1d20 + %s + (@{global_check_bonus}) ]]}}" % g.total,
                                "{{rolladv=[[ 1d20 + %s + (@{global_check_bonus}) ]]}}" % g.total,
                                "@{classaction%s}"])))
    g.set_label("%s (%s)" % (skill.capitalize(), abil[0:3]))
    g.attr("is_trained", value=5)
    if abil in ['strength', 'dexterity', 'constitution']:
        g.attr("armor_check_penalty", value=atts.armor_check_penalty)
    else:
        g.attr("armor_check_penalty", value=0)
    g.attr("total", value=fn_sum(g.is_trained, atts.mod_plus_half_lev, atts.armor_check_penalty))
    g.attr("passive", value=fn_sum(10, g.skill)
    skill_groups.append(g)
    

Attr("level")
Attr("xp")
Attr("xp_next_level")
Attr("10_plus_half_level", value=fn_sum(10, fn_floor(div(atts.level,2))))

NUM_ARMORS = 10
armor_groups = []
for i in range(1, NUM_ARMORS+1):
    g = Group(suffix=str(i))
    g.attr("armor_worn", value="1")
    g.attr("armor_worn_check_penalty", value=fn_prod(g.armor_worn, g.armor_check_penalty))
    g.attr("armor_worn_prof_penalty", value=fn_prod(g.armor_worn, g.armor_prof, -2))
    g.attr("armor_prof", value="0")
    g.attr("armourname")
    g.attr("armourACbase")
    g.attr("armourtype")
    g.attr("light_armour_bonus",
           value=fn_prod(fn_eq(1, g.armourtype), fn_max(atts.dexterity_mod, atts.intelligence_mod)))
    g.attr("armourmagicbonus")
    g.attr("armourtotalAC", value=fn_sum(g.armourACbase, g.armourmagicbonus, g.light_armour_bonus))
    g.attr("armor_check_penalty")
    g.attr("armor_worn_bonus", value=fn_prod(g.armor_worn, g.armourtotalAC))
    armor_groups.append(g)

Attr("armor_bonus", value=fn_sum([g.armor_worn_bonus for g in armor_groups]))
Attr("armor_check_penalty", value=fn_sum([g.armor_check_penalty for g in armor_groups]))
Attr("armor_prof_penalty", value=fn_sum([g.armor_prof_penalty for g in armor_groups]))

Attr("HP")
Attr("HP_max", minimum=1)
Attr("temp_HP")
Attr("speed")
Attr("initiative")
Attr("initiative_overall", value=sum(atts.dexterity_mod,atts.initiative))
Attr("AC", value=atts.armor_bonus)

Roll("roll_init", " ".join(["&{template:5eDefault}",
                            "{{title=Initiative}}",
                            "{{subheader=@{character_name}}}",
                            "{{rollname=Initiative}}",
                            "{{roll=[[ 1d20 + @{selected|initiative_overall} [Initiative Mod] &{tracker} ]]}}",
                            "@{classactioninitiative}"]))

    
t = pyratemp.Template(filename="DnD_4e.html.template")

vars = {}
vars.update(atts)
vars.update(
    dict(max=fn_max,
         min=fn_min,
         gteq=fn_gteq,
         lt=fn_lt,
         lteq=fn_lteq,
         gt=fn_gt,
         eq=fn_eq,
         neg=fn_neg,
         sum_range=fn_sum_range,
         in_check=in_check,
         in_num=in_num,
         in_text=in_text,
         out_num=out_num,
         out_text=out_text,
         skill_groups=skill_groups,
         NUM_ARMORS=NUM_ARMORS
     ))
result = t(**vars)
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

