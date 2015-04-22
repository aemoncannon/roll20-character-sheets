import pyratemp

def fn_sum(*args):
    return " + ".join([str(x) for x in args])

def fn_prod(*args):
    return " * ".join([str(x) for x in args])

def fn_div(arg1, arg2):
    return str(arg1) + " / " + str(arg2)

def fn_quant(arg):
    return "(" + str(arg) + ")"

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

def fn_floor(x):
    """Built in."""
    return "floor(%s)" % x

def fn_ceil(x):
    """Built in."""
    return "ceil(%s)" % x

def fn_round(x):
    """Built in."""
    return "round(%s)" % x

def ref(attr_name):
    """Forward reference to an attribute not yet defined."""
    return "@{%s}" % attr_name

def el_in(attr, tpe="text", cls="", extra=""):
    return "<input class=\"%s\" type=\"%s\" name=\"%s\" value=\"%s\" %s/>" % (cls, tpe, "attr_" + attr.name, attr.value, extra)

def in_check(attr, checked=False, cls=""):
    if checked:
        return el_in(attr, tpe="checkbox", cls=cls, extra="checked=\"checked\"")
    else:
        return el_in(attr, tpe="checkbox", cls=cls)

def in_text(attr, cls=""):
    return el_in(attr, cls=cls)

def in_num(attr, cls="", step="1"):
    return el_in(attr, tpe="number", cls=cls, extra="min=\"%s\" step=\"%s\"" % (attr.minimum, step))

def out_hidden(attr):
    return el_in(attr, tpe="hidden", extra="disabled=\"disabled\"")

def out_text(attr, cls=""):
    return el_in(attr, cls=cls, extra="disabled=\"disabled\"")

def out_num(attr, cls=""):
    return el_in(attr, tpe="number", cls=cls, extra="disabled=\"disabled\"")

class Attr(object):

    def __init__(self, name, value="", minimum=0, dynamic=False):
        self.name = name
        self.value = value
        self.minimum = minimum
        if not dynamic:
            atts.add_attr(self)

    def __str__(self):
        return "@{" + self.name + "}"

class Roll(object):

    def __init__(self, name, value=""):
        self.name = name
        self.value = value
        atts.add_attr(self)

    def __str__(self):
        return self.name

class Group(object):

    def __init__(self, prefix="", suffix="", dynamic = False):
        self.prefix = prefix
        self.suffix = suffix
        self.attrs = {}
        self.dynamic = dynamic

    def __getattr__(self, name):
        return self.attrs[name]

    def attr(self, name, value="", minimum=0):
        att = Attr(self.prefix + name + self.suffix, value=value, minimum=minimum, dynamic=self.dynamic)
        self.attrs[name] = att
        return att

    def set_label(self, name):
        self.label = name

    def set_roll(self, roll):
        self.roll = roll

    def add_attr(self, attr):
        self.attrs[attr.name] = attr
        return attr

    def get_dict(self):
        return self.attrs

atts = Group()

Attr("is_npc", value=1)
Attr("char_class")
Attr("race")
Attr("character_name")
Attr("level", value=1)
Attr("half_level", value=fn_floor(fn_div(atts.level, 2)))
Attr("ten_plus_half_level", value=fn_sum(10, atts.half_level))
Attr("xp", value=0)
Attr("xp_next_level")

Attr("HP")
Attr("HP_max", minimum=1)
Attr("temp_HP")
Attr("speed")
Attr("initiative")
Attr("initiative_overall", value=fn_sum(ref("dexterity_mod"), atts.initiative))
Attr("AC", value=ref("armor_AC_bonus"))

# TODO
Attr("global_saving_bonus")

Roll("roll_init", " ".join(["&{template:5eDefault}",
                            "{{title=Initiative}}",
                            "{{subheader=@{character_name}}}",
                            "{{rollname=Initiative}}",
                            "{{roll=[[ 1d20 + @{selected|initiative_overall} [Initiative Mod] &{tracker} ]]}}",
                            "@{classactioninitiative}"]))

ability_groups = []
for abil in ["strength", "constitution", "dexterity", "intelligence", "wisdom", "charisma"]:
    g = Group(prefix=(abil + "_"))
    g.attr("base", minimum=1)
    g.attr("mod", value=fn_floor(fn_div(fn_quant(fn_sum(g.base, fn_quant(-10))), 2)))
    g.attr("mod_plus_half_lev", value=fn_sum(g.mod, atts.half_level))
    g.set_roll(Roll("roll_%s_Check" % abil.capitalize(),
        " ".join(["&{template:4eDefault}",
                  "{{character_name=@{character_name}}}",
                  "{{save=1}}",
                  "{{title=%s check}}" % abil,
                  "{{subheader=%s}}" % atts.character_name,
                  "{{rollname=%s check}}" % abil,
                  "{{roll=[[ 1d20 + %s + (%s) ]]}}" % (g.mod, atts.global_saving_bonus),
                  "{{rolladv=[[ 1d20 + %s + (%s) ]]}}" % (g.mod, atts.global_saving_bonus)])))
    g.set_label(abil[0:3].upper())
    ability_groups.append(g)

defense_groups = []
for defense in ["ac", "fort", "ref", "will"]:
    g = Group(prefix=(defense + "_"))
    if defense == "ac":
        g.attr("ability_bonus", value=ref("armor_AC_bonus"))
    elif defense == "fort":
        g.attr("ability_bonus", value=fn_max(atts.strength_mod, atts.constitution_mod))
    elif defense == "ref":
        g.attr("ability_bonus", value=fn_sum(fn_max(atts.dexterity_mod, atts.intelligence_mod), ref("armor_prof_penalty"),
                                             ref("shield_reflex_bonus")))
    elif defense == "will":
        g.attr("ability_bonus", value=fn_max(atts.wisdom_mod, atts.charisma_mod))
    g.attr("class_bonus", value=0)
    g.set_label(defense.upper())
    g.attr("total", value=fn_sum(g.ability_bonus, g.class_bonus, atts.ten_plus_half_level))
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
    g.set_label("%s (%s)" % (skill.capitalize(), abil[0:3]))
    g.attr("is_trained", value=5)
    if abil in ['strength', 'dexterity', 'constitution']:
        g.attr("armor_check_penalty", value=ref("armor_check_penalty"))
    else:
        g.attr("armor_check_penalty", value=0)
    g.attr("ability_mod_plus_half_level", value=ref(abil + "_mod_plus_half_lev"))
    g.attr("total", value=fn_sum(g.is_trained, g.ability_mod_plus_half_level, ref("armor_check_penalty")))
    g.attr("passive", value=fn_sum(10, g.total))
    g.set_roll(Roll("roll_%s_Check" % skill.capitalize(),
               " ".join(["&{template:5eDefault}",
                         "{{ability=1}}",
                         "{{title=%s (%s)}}" % (skill.capitalize(), abil),
                         "{{subheader=@{character_name}}}",
                         "{{subheaderright=Ability check}}",
                         "{{rollname=Result}}",
                         "{{roll=[[ 1d20 + %s + (@{global_check_bonus}) ]]}}" % g.total,
                         "{{rolladv=[[ 1d20 + %s + (@{global_check_bonus}) ]]}}" % g.total,
                         "@{classaction%s}"])))
    skill_groups.append(g)
    
NUM_ARMORS = 10
armor_groups = []
for i in range(1, NUM_ARMORS+1):
    g = Group(suffix=str(i))
    g.attr("armor_worn", value=1)
    g.attr("armor_prof", value=1)
    g.attr("armourname")
    g.attr("armourACbase", value=0)
    g.attr("armourtype", value=0)
    g.attr("armor_is_shield", value=fn_sum(fn_eq(3, g.armourtype), fn_eq(4, g.armourtype)))
    g.attr("light_armour_bonus",
           value=fn_prod(fn_eq(1, g.armourtype), fn_max(atts.dexterity_mod, atts.intelligence_mod)))
    g.attr("armourmagicbonus", value=0)
    g.attr("armourtotalAC", value=fn_sum(g.armourACbase, g.armourmagicbonus, g.light_armour_bonus))
    g.attr("armor_check_penalty", value=0, minimum=-10)
    g.attr("armor_worn_bonus", value=fn_prod(g.armor_worn, g.armourtotalAC))
    g.attr("shield_worn_reflex_bonus", value=fn_prod(g.armor_is_shield, g.armor_prof, g.armor_worn, g.armourtotalAC))
    g.attr("armor_worn_check_penalty", value=fn_prod(g.armor_worn, g.armor_check_penalty))
    g.attr("armor_worn_prof_penalty", value=fn_prod(g.armor_worn, fn_neg(g.armor_prof), fn_quant(-2)))
    armor_groups.append(g)

Attr("armor_AC_bonus", value=fn_sum(*[g.armor_worn_bonus for g in armor_groups]))
Attr("shield_reflex_bonus", value=fn_sum(*[g.shield_worn_reflex_bonus for g in armor_groups]))
Attr("armor_check_penalty", value=fn_sum(*[g.armor_worn_check_penalty for g in armor_groups]))
Attr("armor_prof_penalty", value=fn_max(fn_quant(-2), fn_sum(*[g.armor_worn_prof_penalty for g in armor_groups])))

    


# Note: We handle groups in html with a <fieldset> tag, so the group prefix
# is unknowable until runtime.
powers = Group(dynamic=True)

# See PHB page 55 for power card description.
powers.attr("name")
powers.attr("type")
powers.attr("level")
powers.attr("is_available")
powers.attr("keywords")
powers.attr("actiontype")
powers.attr("attacktype")
powers.attr("attacktarget")
powers.attr("attacker")
powers.attr("attackbonus")
powers.attr("attackee")
powers.attr("requirements")
powers.attr("on_miss")
powers.attr("secondary_attack")
powers.attr("effect")
powers.attr("sustain")
powers.attr("notes")


t = pyratemp.Template(filename="DnD_4e.html.template")

template_vars = {}
template_vars.update(atts.get_dict())
template_vars.update(
    dict(max=fn_max,
         min=fn_min,
         gteq=fn_gteq,
         lt=fn_lt,
         lteq=fn_lteq,
         gt=fn_gt,
         eq=fn_eq,
         neg=fn_neg,
         in_check=in_check,
         in_num=in_num,
         in_text=in_text,
         out_num=out_num,
         out_text=out_text,
         out_hidden=out_hidden,
         skill_groups=skill_groups,
         defense_groups=defense_groups,
         armor_groups=armor_groups,
         ability_groups=ability_groups,
         powers=powers
     ))

#for _, attr in sorted(atts.get_dict().items()):
#    print attr.name + " = " + str(attr.value)

result = t(**template_vars)
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

