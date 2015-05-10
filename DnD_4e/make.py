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

def fn_eq_po2(x, y):
    """Evaluates to 1 if x == y, 0 otherwise. x and y must be powers of 2"""
    return "(floor((%s) / (%s)) %% 2)" % (x, y)

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

def in_select(attr):
    return (("<select name='attr_%s'>\n" % attr.name) +
            "\n".join("<option value='%s'>%s</option>" % (val,label) for val,label in attr.options) +
            "\n</select>")

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

    def __init__(self, name, value="", minimum=0, dynamic=False, options=None):
        self.name = name
        self.value = value
        self.minimum = minimum
        self.options = options or []
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

    def attr(self, name, value="", minimum=0, options=None):
        att = Attr(self.prefix + name + self.suffix, value=value, minimum=minimum,
                   dynamic=self.dynamic, options=options)
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
Attr("xp", value=0)
Attr("xp_next_level")

Attr("HP")
Attr("HP_max", minimum=1)
Attr("temp_HP")

Attr("healing_surge_value")
Attr("healing_surges")
Attr("healing_surges_per_day")

Attr("action_points")

Attr("base_speed")
Attr("speed", value=fn_sum(atts.base_speed, ref("misc_speed_bonus")))
Attr("initiative", value=fn_sum(atts.half_level, ref("dexterity_mod"), ref("misc_initiative_bonus")))
Attr("AC", value=ref("armor_AC_bonus"))

Roll("roll_init", " ".join(["&{template:5eDefault}",
                            "{{title=Initiative}}",
                            "{{subheader=@{character_name}}}",
                            "{{rollname=Initiative}}",
                            # This sends the computed initiative directly to the tracker.
                            "{{roll=[[ 1d20 + @{selected|initiative} [Initiative Mod] &{tracker} ]]}}"
                        ]))

ability_groups = []
for abil in ["strength", "constitution", "dexterity", "intelligence", "wisdom", "charisma"]:
    g = Group(prefix=(abil + "_"))
    g.attr("base", minimum=1)
    g.attr("mod", value=fn_floor(fn_div(fn_quant(fn_sum(g.base, fn_quant(-10))), 2)))
    g.set('roll', Roll("roll_%s_Check" % abil.capitalize(),
        " ".join(["&{template:5eDefault}",
                  "{{character_name=@{character_name}}}",
                  "{{save=1}}",
                  "{{title=%s Check}}" % abil.capitalize(),
                  "{{subheader=%s}}" % atts.character_name,
                  "{{rollname=Result}}",
                  "{{roll=[[ 1d20 + [[%s]]]]}}" % fn_sum(atts.half_level, g.mod),
              ])))
    g.set('label', abil[0:3].upper())
    g.set('uniqued_mod', fn_sum(g.mod, len(ability_groups) * 0.001))
    ability_groups.append(g)

defense_groups = []
for defense in ["ac", "fort", "reflex", "will"]:
    g = Group(prefix=(defense + "_"))
    if defense == "ac":
        g.attr("ability_bonus", value=ref("armor_AC_bonus"))
    elif defense == "fort":
        g.attr("ability_bonus", value=fn_max(atts.strength_mod, atts.constitution_mod))
    elif defense == "reflex":
        g.attr("ability_bonus", value=fn_sum(fn_max(atts.dexterity_mod, atts.intelligence_mod), ref("armor_prof_penalty"),
                                             ref("shield_reflex_bonus")))
    elif defense == "will":
        g.attr("ability_bonus", value=fn_max(atts.wisdom_mod, atts.charisma_mod))
    g.attr("misc_bonus", value=ref("misc_" + defense + "_bonus"))
    g.set('label', defense.upper())
    g.attr("total", value=fn_sum(g.ability_bonus, g.misc_bonus, 10, atts.half_level))
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
    g.attr("ability_mod", value=ref(abil + "_mod"))
    g.attr("misc_bonus", ref("misc_" + skill + "_bonus"))
    g.attr("total", value=fn_sum(g.is_trained,
                                 atts.half_level,
                                 g.ability_mod,
                                 ref("armor_check_penalty"),
                                 g.misc_bonus))
    g.attr("passive", value=fn_sum(10, g.total))
    g.set('roll', Roll("roll_%s_Check" % skill.capitalize(),
               " ".join(["&{template:5eDefault}",
                         "{{ability=1}}",
                         "{{title=%s (%s)}}" % (skill.capitalize(), abil),
                         "{{subheader=@{character_name}}}",
                         "{{subheaderright=Skill check}}",
                         "{{rollname=Result}}",
                         "{{roll=[[ 1d20 + [[%s]]]]}}" % g.total
                     ])))
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
    g.attr("armourtype", value=0, options=[
        (0, "n/a"),
        (LIGHT_ARMOR, "Light"),
        (HEAVY_ARMOR, "Heavy"),
        (LIGHT_SHIELD, "Light Shield"),
        (HEAVY_SHIELD, "Heavy Shield")])
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
WEAPON_TYPE_STR_BASED = 0
WEAPON_TYPE_DEX_BASED = 1
for i in range(1, NUM_WEAPONS+1):
    g = Group(suffix=str(i))
    g.attr("weapon_name")
    g.attr("weapon_worn", value=1)
    g.attr("weapon_offhand", value=1)
    g.attr("weapon_prof", value=1)
    g.attr("weapon_prof_bonus", value=0)
    g.attr("weapon_type", value=0, options=[(WEAPON_TYPE_STR_BASED, "Melee/Heavy thrown (str)"),
                                            (WEAPON_TYPE_DEX_BASED, "Ranged/Light thrown (dex)")])
    g.attr("weapon_dmg_dice_count", value=1)
    g.attr("weapon_dmg_dice_type", value=6)
    g.attr("weapon_enhancement_bonus", value=0) # Magic or other bonus
    
    # Note this attribute not actually used anywhere a.t.m, as each power already has a 'base attack bonus'
    # factored into its roll. Keep this just for display I guess.
    g.attr("weapon_ability_bonus", value=fn_sum(fn_prod(fn_eq(g.weapon_type, WEAPON_TYPE_STR_BASED),
                                                        fn_sum(atts.half_level, atts.strength_mod)),
                                                fn_prod(fn_eq(g.weapon_type, WEAPON_TYPE_DEX_BASED),
                                                        fn_sum(atts.half_level, atts.dexterity_mod))))

    g.attr("weapon_total_hit_bonus", value=fn_sum(g.weapon_enhancement_bonus, fn_prod(g.weapon_prof, g.weapon_prof_bonus)))
    g.attr("weapon_notes")
    weapon_groups.append(g)

# Aggregate weapon effects
Attr("weapon_dmg_dice_count", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_dmg_dice_count) for g in weapon_groups]))
Attr("weapon_dmg_dice_type", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_dmg_dice_type) for g in weapon_groups]))
Attr("weapon_total_hit_bonus", value=fn_sum(*[fn_prod(g.weapon_worn, g.weapon_total_hit_bonus) for g in weapon_groups]))

Attr("weapon_offhand_dmg_dice_count", value=fn_sum(*[fn_prod(g.weapon_offhand, g.weapon_dmg_dice_count) for g in weapon_groups]))
Attr("weapon_offhand_dmg_dice_type", value=fn_sum(*[fn_prod(g.weapon_offhand, g.weapon_dmg_dice_type) for g in weapon_groups]))
Attr("weapon_offhand_total_hit_bonus", value=fn_sum(*[fn_prod(g.weapon_offhand, g.weapon_total_hit_bonus) for g in weapon_groups]))

def make_action_roll(action, offhand=False):
    return Roll("roll_" + action.prefix,
                     " ".join(["&{template:5eDefault}",
                               "{{attack=1}}",
                               "{{keywords=%s}}" % action.keywords,
                               "{{target=%s}}" % action.attacktarget,
                               "{{attacktype=%s}}" % action.attacktype if action.has_attr('attacktype') else "",
                               "{{defense=%s}}" % action.attackee,
                               "{{miss=%s}}" % action.on_miss if action.has_attr('on_miss') else "",
                               "{{secondary=%s}}" % action.secondary_attack if action.has_attr('secondary_attack') else "", 
                               "{{title=%s}}" % (action.name),
                               "{{subheader=@{character_name}}}",
                               "{{rollname=Result}}",
                               "{{roll=[[ 1d20 + [[%s]]]]}}" % (
                                   fn_sum(action.total_bonus,
                                          fn_prod(action.is_weapon,
                                                  atts.weapon_total_hit_bonus))
                                   if not offhand else
                                   fn_sum(action.total_bonus,
                                          fn_prod(action.is_weapon,
                                                  atts.weapon_total_offhand_hit_bonus))
                               )
                           ]))

def make_damage_roll(action, offhand=False):
    return Roll("roll_" + action.prefix + "damage",
                     " ".join(["&{template:5eDefault}",
                               "{{title=Damage}}",
                               "{{subheader=@{character_name}}}",
                               "{{effect=%s}}" % action.effect if action.has_attr('effect') else "",
                               "{{rollname=Result}}",
                               "{{roll=[[ [[%s]]d[[%s]] + [[%s]]d[[%s]] + [[%s]] + [[%s]] + [[%s]]]]}}" % (
                                   # Weapon damage
                                   fn_prod(action.is_weapon,
                                           fn_prod(action.dmg_dice_multiplier,
                                                   atts.weapon_dmg_dice_count)
                                           if not offhand else
                                           fn_prod(action.dmg_dice_multiplier,
                                                   atts.weapon_offhand_dmg_dice_count)
                                       ),
                                   atts.weapon_dmg_dice_type
                                   if not offhand else
                                   atts.weapon_offhand_dmg_dice_type,

                                   # Non-weapon damage
                                   fn_prod(fn_neg(action.is_weapon), action.dmg_dice_multiplier),
                                   action.dmg_dice_type,

                                   # Power modifier to damage.
                                   action.dmg_modifier,

                                   # General ability bonus to damage.
                                   fn_floor(action.dmg_ability_bonus),
                                   fn_floor(action.dmg_ability_bonus2))
                               
                           ]))


basic_actions = []

action = Group(prefix="meleebasic_")
action.attr("name", value="Melee Basic Attack")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("is_weapon", value=1)
action.attr("attacktarget", value="One creature")
action.attr("ability_mod", value=atts.strength_mod)
action.attr("power_modifier", value=0)
action.attr("total_bonus", value=fn_sum(atts.half_level, action.ability_mod, action.power_modifier))
action.attr("attackee", value="AC")
action.attr("dmg_dice_multiplier", value="1")
action.attr("dmg_dice_type", value="0")
action.attr("dmg_ability_bonus", value=atts.strength_mod)
action.attr("dmg_ability_bonus2", value=0)
action.attr("dmg_modifier", value=0)
action.set('roll', make_action_roll(action))
action.set('damage_roll', make_damage_roll(action))
action.set('offhand_roll', make_action_roll(action))
action.set('offhand_damage_roll', make_damage_roll(action))
basic_actions.append(action)

action = Group(prefix="rangedbasic_")
action.attr("name", value="Ranged Basic Attack")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("is_weapon", value=1)
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("ability_mod", value=atts.dexterity_mod)
action.attr("power_modifier", value=0)
action.attr("total_bonus", value=fn_sum(atts.half_level, action.ability_mod, action.power_modifier))
action.attr("attackee", value="AC")
action.attr("dmg_dice_multiplier", value="1")
action.attr("dmg_dice_type", value="0")
action.attr("dmg_ability_bonus", value=atts.dexterity_mod)
action.attr("dmg_ability_bonus2", value=0)
action.attr("dmg_modifier", value=0)

action.set('roll', make_action_roll(action))
action.set('damage_roll', make_damage_roll(action))
action.set('offhand_roll', make_action_roll(action))
action.set('offhand_damage_roll', make_damage_roll(action))
basic_actions.append(action)

action = Group(prefix="aidanother_")
action.attr("name", value="Aid another")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("is_weapon", value=0)
action.attr("attacktype", value="Melee")
action.attr("attacktarget", value="One creature")
action.attr("ability_mod", value=atts.strength_mod)
action.attr("power_modifier", value=0)
action.attr("total_bonus", value=fn_sum(atts.half_level, action.ability_mod, action.power_modifier))
action.attr("attackee", value="AC")
action.attr("effect", value="If you succeed, deal no damage, but choose one ally. That ally gets a +2 bonus to his or her next attack roll against the target or to all defenses against the target's next attack. This bonus ends if not used by the end of your next turn.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)

action = Group(prefix="bullrush_")
action.attr("name", value="Bull Rush")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Melee")
action.attr("is_weapon", value=0)
action.attr("attacktarget", value="One creature")
action.attr("ability_mod", value=atts.strength_mod)
action.attr("power_modifier", value=0)
action.attr("total_bonus", value=fn_sum(atts.half_level, action.ability_mod, action.power_modifier))
action.attr("attackee", value="Fort")
action.attr("effect", value="You push the target 1 square and then shift 1 square into the space it left.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)

action = Group(prefix="grab_")
action.attr("name", value="Grab")
action.attr("keywords", value="At Will")
action.attr("actiontype", value="Standard")
action.attr("attacktype", value="Ranged")
action.attr("is_weapon", value=0)
action.attr("attacktarget", value="One creature")
action.attr("ability_mod", value=atts.strength_mod)
action.attr("power_modifier", value=0)
action.attr("total_bonus", value=fn_sum(atts.half_level, action.ability_mod, action.power_modifier))
action.attr("attackee", value="Reflex")
action.attr("effect", value="You grab the target until the end of your next turn. You can end the grab as a free action.")
action.set('roll', make_action_roll(action))
basic_actions.append(action)


# Note: We handle groups in html with a <fieldset> tag, so the group prefix
# is unknowable until runtime.
powers = Group(dynamic=True)
# See PHB page 55 for power card description.
powers.attr("name")
powers.attr("type", options=[("At will", "At will"), ("Encounter", "Encounter"), ("Daily", "Daily")])
powers.attr("level", options=[(i,i) for i in range(1,30)])
powers.attr("is_available")
powers.attr("is_weapon", value=1)
powers.attr("keywords")
powers.attr("actiontype", options=[
    			      ("Standard", "Standard"),
			      ("Move", "Move"),
			      ("Immediate interrupt", "Immediate interrupt"),
			      ("Immediate reaction", "Immediate reaction"),
			      ("Minor", "Minor"),
			      ("Free", "Free"),
			      ("Trigger(see notes)", "Trigger(see notes)")])
powers.attr("attacktype")
powers.attr("attacktarget")
powers.attr("ability_mod", value=0, options=(
    [(0,"n/a")] + [(a.get('uniqued_mod'),a.get('label')) for a in ability_groups]))

powers.attr("power_modifier")
powers.attr("total_bonus", value=fn_sum(atts.half_level,
                                        fn_floor(powers.ability_mod),
                                        powers.power_modifier,
                                        fn_quant(fn_prod(powers.is_weapon, atts.weapon_total_hit_bonus))))
powers.attr("attackee", options=[(d.get('label').upper(), d.get('label').upper()) for d in defense_groups])

powers.attr("dmg_dice_multiplier")
powers.attr("dmg_dice_type")
powers.attr("dmg_ability_bonus", value=0, options=([(0,"n/a")] + [(a.get('uniqued_mod'),a.get('label')) for a in ability_groups]))
# Some powers list two ability modifiers to damage :-(
powers.attr("dmg_ability_bonus2", value=0, options=(
    [(0,"n/a")] + [(a.get('uniqued_mod'),a.get('label')) for a in ability_groups]))
powers.attr("dmg_modifier")


powers.attr("requirements")
powers.attr("on_miss")
powers.attr("secondary_attack")
powers.attr("effect")
powers.attr("sustain")
powers.attr("notes")
powers.set('roll', make_action_roll(powers))
powers.set('damage_roll', make_damage_roll(powers))
powers.set('offhand_roll', make_action_roll(powers))
powers.set('offhand_damage_roll', make_damage_roll(powers))


bonus_names = ["initiative",
               "speed",
               "ac",
               "fort",
               "reflex",
               "will",
               "acrobatics",
               "arcana",
               "athletics",
               "bluff",
               "diplomacy",
               "dungeoneering",
               "endurance",
               "heal",
               "history",
               "insight",
               "intimidate",
               "nature",
               "perception",
               "religion",
               "stealth",
               "streetwise",
               "thievery"]
bonuses = zip([2**k for k in range(0, len(bonus_names))], bonus_names)

NUM_BONUSES = 10
bonus_groups = []
for i in range(1, NUM_BONUSES+1):
    g = Group(prefix="bonus_", suffix=str(i))
    g.attr("description")
    g.attr("category", value=0, options=([(0, "")] + [(val, name.capitalize()) for val,name in bonuses]))
    g.attr("modifier", value=0)
    bonus_groups.append(g)

# Aggregate bonus effects
for val, name in bonuses:
    Attr("misc_" + name + "_bonus",
         value=fn_sum(*[fn_prod(fn_eq_po2(g.category, val), g.modifier) for g in bonus_groups]))

t = pyratemp.Template(filename="DnD_4e.html.template")

template_vars = {}
template_vars.update(atts.get_dict())
template_vars.update(
    dict(atts=atts,
         max=fn_max,
         min=fn_min,
         gteq=fn_gteq,
         lteq=fn_lteq,
         eq=fn_eq,
         neg=fn_neg,
         sum=fn_sum,
         in_check=in_check,
         in_num=in_num,
         in_text=in_text,
         in_select=in_select,
         out_num=out_num,
         out_text=out_text,
         out_hidden=out_hidden,
         skill_groups=skill_groups,
         defense_groups=defense_groups,
         armor_groups=armor_groups,
         weapon_groups=weapon_groups,
         bonus_groups=bonus_groups,
         bonuses=bonuses,
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

