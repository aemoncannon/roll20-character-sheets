import pyratemp

def fn_sum(*args):
    return " + ".join([str(x) for x in args])

def fn_prod(*args):
    return " * ".join(["(" + str(x) + ")" for x in args])

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

def fn_lteq(x, y):
    """Evaluates to 1 if x <= y, 0 otherwise."""
    return "( floor( ( (%s) - (%s) ) / ( abs( (%s) - (%s) ) + 0.001 ) ) + 1 )" % (y,x,y,x)

def fn_eq(x, y):
    """Evaluates to 1 if x == y, 0 otherwise."""
    return "abs((((1 + abs((%s)-(%s))) - abs(1 - abs((%s)-(%s)))) / 2) - 1)" % (x,y,x,y)

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
        self.extras = {}
        self.dynamic = dynamic

    def __getattr__(self, name):
        return self.attrs[name]

    def attr(self, name, value="", minimum=0):
        att = Attr(self.prefix + name + self.suffix, value=value, minimum=minimum, dynamic=self.dynamic)
        self.attrs[name] = att
        return att

    def has_attr(self, key):
        return key in self.attrs

    def set(self, key, value):
        self.extras[key] = value

    def get(self, key):
        return self.extras.get(key, None)

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
    g.attr("mod_plus_half_level", value=fn_sum(g.mod, atts.half_level))
    g.set('roll', Roll("roll_%s_Check" % abil.capitalize(),
        " ".join(["&{template:4eDefault}",
                  "{{character_name=@{character_name}}}",
                  "{{save=1}}",
                  "{{title=%s check}}" % abil,
                  "{{subheader=%s}}" % atts.character_name,
                  "{{rollname=%s check}}" % abil,
                  "{{roll=[[ 1d20 + %s + (%s) ]]}}" % (g.mod_plus_half_level, atts.global_saving_bonus),
                  "{{rolladv=[[ 1d20 + %s + (%s) ]]}}" % (g.mod_plus_half_level, atts.global_saving_bonus)])))
    g.set('label', abil[0:3].upper())
    g.set('uniqued_mod', fn_sum(g.mod_plus_half_level, len(ability_groups) * 0.001))
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
    g.set('label', defense.upper())
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
    g.set('label', "%s (%s)" % (skill.capitalize(), abil[0:3]))
    g.attr("is_trained", value=5)
    if abil in ['strength', 'dexterity', 'constitution']:
        g.attr("armor_check_penalty", value=ref("armor_check_penalty"))
    else:
        g.attr("armor_check_penalty", value=0)
    g.attr("ability_mod_plus_half_level", value=ref(abil + "_mod_plus_half_level"))
    g.attr("total", value=fn_sum(g.is_trained, g.ability_mod_plus_half_level, ref("armor_check_penalty")))
    g.attr("passive", value=fn_sum(10, g.total))
    g.set('roll', Roll("roll_%s_Check" % skill.capitalize(),
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
LIGHT_ARMOR = 1
HEAVY_ARMOR = 2
LIGHT_SHIELD = 3
HEAVY_SHIELD = 4
armor_groups = []
for i in range(1, NUM_ARMORS+1):
    g = Group(suffix=str(i))
    g.attr("armor_worn", value=1)
    g.attr("armor_prof", value=1)
    g.attr("armourname")
    g.attr("armourACbase", value=0)
    g.attr("armourtype", value=0)
    g.attr("armor_is_armor", value=fn_sum(fn_eq(LIGHT_ARMOR, g.armourtype), fn_eq(HEAVY_ARMOR, g.armourtype)))
    g.attr("armor_is_shield", value=fn_sum(fn_eq(LIGHT_SHIELD, g.armourtype), fn_eq(HEAVY_SHIELD, g.armourtype)))
    g.attr("light_armour_bonus",
           value=fn_prod(fn_eq(1, g.armourtype), fn_max(atts.dexterity_mod, atts.intelligence_mod)))
    g.attr("armourmagicbonus", value=0)
    g.attr("armourtotalAC", value=fn_sum(g.armourACbase, g.armourmagicbonus, g.light_armour_bonus))
    g.attr("armor_check_penalty", value=0, minimum=-10)
    g.attr("armor_worn_bonus", value=fn_prod(g.armor_worn, g.armourtotalAC))
    g.attr("shield_worn_reflex_bonus", value=fn_prod(g.armor_is_shield, g.armor_prof, g.armor_worn, g.armourtotalAC))
    g.attr("armor_worn_check_penalty", value=fn_prod(g.armor_worn, g.armor_check_penalty))
    g.attr("armor_worn_prof_penalty", value=fn_prod(g.armor_is_armor, g.armor_worn, fn_neg(g.armor_prof), fn_quant(-2)))
    armor_groups.append(g)

# Aggregate armor effects
Attr("armor_AC_bonus", value=fn_sum(*[g.armor_worn_bonus for g in armor_groups]))
Attr("shield_reflex_bonus", value=fn_sum(*[g.shield_worn_reflex_bonus for g in armor_groups]))
Attr("armor_check_penalty", value=fn_sum(*[g.armor_worn_check_penalty for g in armor_groups]))
Attr("armor_prof_penalty", value=fn_max(fn_quant(-2), fn_sum(*[g.armor_worn_prof_penalty for g in armor_groups])))

NUM_WEAPONS = 10
weapon_groups = []
for i in range(1, NUM_WEAPONS+1):
    g = Group(suffix=str(i))
    g.attr("weapon_name")
    g.attr("weapon_worn", value=1)
    g.attr("weapon_prof", value=1)
    g.attr("weapon_prof_bonus", value=0)
    g.attr("weapon_type", value=0)
    g.attr("weapon_dmg_dice_count", value=1)
    g.attr("weapon_dmg_dice_type", value=6)
    g.attr("weapon_enhancement_bonus", value=0) # Magic or other bonus
    g.attr("weapon_total_hit_bonus", value=fn_sum(g.weapon_enhancement_bonus, fn_prod(g.weapon_prof, g.weapon_prof_bonus)))
    g.attr("weapon_notes")
    weapon_groups.append(g)

# Aggregate weapon effects
Attr("weapon_dmg_dice_count", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_dmg_dice_count) for g in weapon_groups]))
Attr("weapon_dmg_dice_type", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_dmg_dice_type) for g in weapon_groups]))
Attr("weapon_total_hit_bonus", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_total_hit_bonus) for g in weapon_groups]))

def make_action_roll(action):
    return Roll("roll_" + action.prefix,
                     " ".join(["&{template:5eDefault}",
                               "{{attack=%s}}" % action.ability_name,
                               "{{title=%s}}" % (action.name),
                               "{{subheader=@{character_name}}}",
                               "{{subheaderright=Basic Action}}",
                               "{{rollname=Result}}",
                               "{{roll=[[ 1d20 + %s]]}}" % (fn_sum(action.total_bonus,
                                                                   atts.weapon_total_hit_bonus))
                           ]))

def make_damage_roll(action):
    return Roll("roll_" + action.prefix + "damage",
                     " ".join(["&{template:5eDefault}",
                               "{{title=Damage}}",
                               "{{rollname=Result}}",
                               "{{roll=[[ (%s)d(%s) ]]}}" % (fn_prod(action.dmg_dice_multiplier,
                                                                 atts.weapon_dmg_dice_count),
                                                         atts.weapon_dmg_dice_type)
                           ]))


basic_actions = []

action = Group(prefix="meleebasic_")
action.attr("name", value="Melee Basic Attack")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("attacker", value=atts.strength_mod_plus_half_level)
action.attr("ability_name", value="Strength")
action.attr("attackbonus", value=0)
action.attr("total_bonus", value=fn_sum(action.attacker, action.attackbonus))
action.attr("attackee", value="AC")
action.attr("dmg_dice_multiplier", value="1")
action.set('roll', make_action_roll(action))
action.set('damage_roll', make_damage_roll(action))
basic_actions.append(action)

action = Group(prefix="rangedbasic_")
action.attr("name", value="Ranged Basic Attack")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("attacker", value=atts.dexterity_mod_plus_half_level)
action.attr("ability_name", value="Dexterity")
action.attr("attackbonus", value=0)
action.attr("total_bonus", value=fn_sum(action.attacker, action.attackbonus))
action.attr("attackee", value="AC")
action.attr("dmg_dice_multiplier", value="1")
action.set('roll', make_action_roll(action))
action.set('damage_roll', make_damage_roll(action))
basic_actions.append(action)

action = Group(prefix="aidanother_")
action.attr("name", value="Aid another")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("attacker", value=atts.strength_mod_plus_half_level)
action.attr("ability_name", value="Strength")
action.attr("attackbonus", value=0)
action.attr("total_bonus", value=fn_sum(action.attacker, action.attackbonus))
action.attr("attackee", value="ac")
action.attr("effect", value="If you succeed, deal no damage, but choose one ally. That ally gets a +2 bonus to his or her next attack roll against the target or to all defenses against the target's next attack. This bonus ends if not used by the end of your next turn.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)

action = Group(prefix="bullrush_")
action.attr("name", value="Bull Rush")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("attacker", value=atts.strength_mod_plus_half_level)
action.attr("ability_name", value="Strength")
action.attr("attackbonus", value=0)
action.attr("total_bonus", value=fn_sum(action.attacker, action.attackbonus))
action.attr("attackee", value="fort")
action.attr("effect", value="You push the target 1 square and then shift 1 square into the space it left.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)

action = Group(prefix="grab_")
action.attr("name", value="Grab")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Ranged")
action.attr("attacktarget", value="One creature")
action.attr("attacker", value=atts.strength_mod_plus_half_level)
action.attr("ability_name", value="Strength")
action.attr("attackbonus", value=0)
action.attr("total_bonus", value=fn_sum(action.attacker, action.attackbonus))
action.attr("attackee", value="reflex")
action.attr("effect", value="You grab the target until the end of your next turn. You can end the grab as a free action.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)


# Note: We handle groups in html with a <fieldset> tag, so the group prefix
# is unknowable until runtime.
powers = Group(dynamic=True)
# See PHB page 55 for power card description.
powers.attr("name")
powers.attr("type")
powers.attr("level")
powers.attr("is_available")
powers.attr("is_weapon", value=1)
powers.attr("keywords")
powers.attr("actiontype")
powers.attr("attacktype")
powers.attr("attacktarget")
powers.attr("attacker")
powers.attr("ability_bonus", value=0)
powers.attr("attackbonus")
powers.attr("total_bonus", value=fn_sum(fn_floor(powers.ability_bonus), powers.attackbonus,
                                        fn_quant(fn_prod(powers.is_weapon, atts.weapon_total_hit_bonus))))
powers.attr("attackee")
powers.attr("requirements")
powers.attr("on_miss")
powers.attr("secondary_attack")
powers.attr("effect")
powers.attr("sustain")
powers.attr("notes")
action.set('roll', make_action_roll(powers))
action.set('damage_roll', make_damage_roll(powers))


t = pyratemp.Template(filename="DnD_4e.html.template")

template_vars = {}
template_vars.update(atts.get_dict())
template_vars.update(
    dict(max=fn_max,
         min=fn_min,
         gteq=fn_gteq,
         lteq=fn_lteq,
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
         weapon_groups=weapon_groups,
         ability_groups=ability_groups,
         powers=powers,
         basic_actions=basic_actions
     ))

for _, attr in sorted(atts.get_dict().items()):
    print attr.name + " = " + str(attr.value)

result = t(**template_vars)
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

