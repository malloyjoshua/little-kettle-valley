#!/usr/bin/env python3
"""feasibility.py — can a player actually obtain every task item, in book order?

The playthrough harness force-completes quests; it never proved that q06's soup could be
cooked from what q01-q05 hand out (it could not: the recipe wanted beetroot). This walks the
quest graph in dependency order, keeping a set of OBTAINABLE items: first-join grants, every
reward of every completed quest, everything reachable from those through the shipped recipes
(server/local/kubejs/export: shaped/shapeless/machine recipes, tags resolved), plus a curated
list of NATURAL sources (ores, crops, drops, fish, wood, nether basics). A task item that is
not obtainable when its quest becomes startable is reported with the quest that asks for it.

Usage: feasibility.py <story/quests dir> [--export server/local/kubejs/export] [--json out]
Exit 1 if any task item is unobtainable.
"""
import sys, json, glob, os, collections, pathlib, argparse

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('--export', default='server/local/kubejs/export'); ap.add_argument('--json', default=None)
ap.add_argument('--why', default=None, help='explain why an item is (un)obtainable at the end of the book')
ap.add_argument('--first-join', default='valley:letter,ftbquests:book,valley:deed,herbalbrews:kettle,minecraft:compass,patchouli:guide_book')
a = ap.parse_args()

# ---------------------------------------------------------------- tags
TAGS = {}
for p in glob.glob(f'{a.export}/tags/minecraft/item/**/*.json', recursive=True):
    rel = os.path.relpath(p, f'{a.export}/tags/minecraft/item')
    ns, path = rel.split('/', 1)
    tag = f'{ns}:{path[:-5]}'
    try:
        j = json.load(open(p)); vals = j if isinstance(j, list) else j.get('values', [])
    except Exception: continue
    TAGS[tag] = [v['id'] if isinstance(v, dict) else v for v in vals]
def tag_items(t, seen=None):
    seen = seen or set()
    out = []
    for v in TAGS.get(t, []):
        if v.startswith('#'):
            if v[1:] not in seen: seen.add(v[1:]); out += tag_items(v[1:], seen)
        else: out.append(v)
    return out

# ---------------------------------------------------------------- recipes -> (needs, makes)
MACHINE = {
    'minecraft:smelting': 'minecraft:furnace', 'minecraft:blasting': 'minecraft:blast_furnace', 'minecraft:smoking': 'minecraft:smoker',
    'minecraft:campfire_cooking': 'minecraft:campfire', 'minecraft:stonecutting': 'minecraft:stonecutter', 'minecraft:smithing_transform': 'minecraft:smithing_table',
    'farmersdelight:cooking': 'farmersdelight:cooking_pot', 'farmersdelight:cutting': 'farmersdelight:cutting_board',
    'create:milling': 'create:millstone', 'create:crushing': 'create:crushing_wheel', 'create:pressing': 'create:mechanical_press',
    'create:mixing': 'create:mechanical_mixer', 'create:compacting': 'create:mechanical_press', 'create:cutting': 'create:mechanical_saw',
    'create:deploying': 'create:deployer', 'create:filling': 'create:spout', 'create:emptying': 'create:item_drain', 'create:splashing': 'create:encased_fan',
    'create:haunting': 'create:encased_fan', 'create:sandpaper_polishing': 'create:sand_paper', 'create:mechanical_crafting': 'create:mechanical_crafter',
    'create:sequenced_assembly': 'create:mechanical_press', 'create:item_application': 'minecraft:air',
    'thermal:pulverizer': 'thermal:machine_pulverizer', 'thermal:smelter': 'thermal:machine_smelter', 'thermal:sawmill': 'thermal:machine_sawmill',
    'thermal:centrifuge': 'thermal:machine_centrifuge', 'thermal:furnace': 'thermal:machine_furnace', 'thermal:insolator': 'thermal:machine_insolator',
    'thermal:press': 'thermal:machine_press', 'thermal:crucible': 'thermal:machine_crucible', 'thermal:chiller': 'thermal:machine_chiller',
    'thermal:refinery': 'thermal:machine_refinery', 'thermal:pyrolyzer': 'thermal:machine_pyrolyzer', 'thermal:brewer': 'thermal:machine_brewer',
    'thermal:bottler': 'thermal:machine_bottler', 'thermal:crystallizer': 'thermal:machine_crystallizer', 'thermal:tree_extractor': 'thermal:device_tree_extractor',
    'ae2:inscriber': 'ae2:inscriber', 'ae2:charger': 'ae2:charger', 'ae2:transform': 'minecraft:air', 'ae2:entropy': 'ae2:entropy_manipulator',
    'vinery:wood_aging': 'vinery:wine_press', 'vinery:fermentation_barrel': 'vinery:fermentation_barrel', 'vinery:apple_press': 'vinery:apple_press',
    'bakery:baking': 'bakery:bakery_oven' if False else 'minecraft:air', 'candlelight:cooking_pot': 'candlelight:cooking_pot', 'herbalbrews:brewing': 'herbalbrews:kettle',
    'cookingforblockheads:toaster': 'cookingforblockheads:toaster', 'sophisticatedstorage:upgrade_next_tier': 'minecraft:air',
    'createaddition:rolling': 'createaddition:rolling_mill', 'createaddition:liquid_burning': 'minecraft:air', 'createaddition:charging': 'minecraft:air',
}
SKIP = ('result', 'results', 'output', 'outputs', 'type', 'group', 'category', 'experience', 'cookingtime', 'processingTime',
        'energy', 'fluid_result', 'transitionalItem', 'transitional_item', 'pattern', 'count', 'chance', 'nbt')
def alt(o):
    """one ingredient dict -> ('item', id) / ('tag', tag) or None"""
    if isinstance(o, dict):
        if isinstance(o.get('item'), str) and ':' in o['item']: return ('item', o['item'])
        if isinstance(o.get('tag'), str): return ('tag', o['tag'])
    return None
def group(o):
    """an ingredient position -> list of alternatives (OR); [] if not an ingredient"""
    a = alt(o)
    if a: return [a]
    if isinstance(o, list):
        out = []
        for x in o:
            a = alt(x)
            if a: out.append(a)
        return out
    return []
def ingredients(o, acc):
    """acc gets one OR-group (list of alternatives) per required ingredient position"""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP: continue
            if k in ('ingredients', 'inputs', 'sequence'):
                if isinstance(v, list):
                    for e in v:
                        g = group(e)
                        if g: acc.append(g)
                        else: ingredients(e, acc)
                else: ingredients(v, acc)
            elif k in ('ingredient', 'input', 'base', 'addition', 'template', 'container', 'catalyst'):
                g = group(v)
                if g: acc.append(g)
                else: ingredients(v, acc)
            elif k == 'key' and isinstance(v, dict):
                for sym, e in v.items():
                    g = group(e)
                    if g: acc.append(g)
            else:
                g = group(v) if isinstance(v, dict) else []
                if g and (k in ('item', 'tag')): pass
                ingredients(v, acc)
    elif isinstance(o, list):
        for v in o: ingredients(v, acc)
def outputs(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('result', 'results', 'output', 'outputs'):
                if isinstance(v, str) and ':' in v: acc.append(v)
                elif isinstance(v, dict):
                    for kk in ('item', 'id'):
                        if isinstance(v.get(kk), str) and ':' in v[kk]: acc.append(v[kk])
                    if isinstance(v.get('item'), dict) and isinstance(v['item'].get('item'), str): acc.append(v['item']['item'])
                elif isinstance(v, list):
                    for x in v:
                        if isinstance(x, str) and ':' in x: acc.append(x)
                        elif isinstance(x, dict):
                            for kk in ('item', 'id'):
                                if isinstance(x.get(kk), str) and ':' in x[kk]: acc.append(x[kk])
                            if isinstance(x.get('item'), dict) and isinstance(x['item'].get('item'), str): acc.append(x['item']['item'])
            else: outputs(v, acc)
    elif isinstance(o, list):
        for v in o: outputs(v, acc)

RECIPES = []
for d in ('recipes', 'added_recipes'):
    for p in glob.glob(f'{a.export}/{d}/**/*.json', recursive=True):
        try: j = json.load(open(p))
        except Exception: continue
        t = j.get('type', '')
        needs = []; ingredients({k: v for k, v in j.items() if k not in ('result', 'results', 'output', 'outputs')}, needs)
        makes = []; outputs(j, makes)
        if not makes and isinstance(j.get('item'), str) and ':' in j['item'] and not str(j.get('type','')).startswith('minecraft:crafting'):
            makes = [j['item']]
        if not makes: continue
        m = MACHINE.get(t)
        if m and m != 'minecraft:air': needs.append([('item', m)])
        trans = (j.get('transitionalItem') or j.get('transitional_item') or {})
        trans = trans.get('item') if isinstance(trans, dict) else None
        needs = [g for g in needs if not any(a[0] == 'item' and (a[1] in makes or a[1] == trans) for a in g)]
        RECIPES.append((os.path.relpath(p, a.export), t, needs, sorted(set(makes))))

# ---------------------------------------------------------------- natural sources
NATURAL = set('''
minecraft:oak_log minecraft:birch_log minecraft:spruce_log minecraft:dark_oak_log minecraft:acacia_log minecraft:jungle_log minecraft:cherry_log minecraft:mangrove_log
minecraft:oak_sapling minecraft:birch_sapling minecraft:spruce_sapling minecraft:apple minecraft:stick minecraft:cobblestone minecraft:stone minecraft:dirt minecraft:grass_block minecraft:gravel minecraft:sand minecraft:red_sand minecraft:clay_ball minecraft:clay minecraft:flint minecraft:sandstone minecraft:andesite minecraft:diorite minecraft:granite minecraft:deepslate minecraft:cobbled_deepslate minecraft:tuff minecraft:calcite minecraft:dripstone_block minecraft:pointed_dripstone minecraft:moss_block minecraft:snowball minecraft:ice minecraft:packed_ice minecraft:obsidian minecraft:water_bucket minecraft:lava_bucket minecraft:mud
minecraft:coal minecraft:raw_iron minecraft:raw_copper minecraft:raw_gold minecraft:redstone minecraft:lapis_lazuli minecraft:diamond minecraft:emerald minecraft:coal_ore minecraft:iron_ore minecraft:copper_ore minecraft:gold_ore minecraft:redstone_ore minecraft:lapis_ore minecraft:diamond_ore minecraft:deepslate_iron_ore minecraft:deepslate_copper_ore minecraft:deepslate_gold_ore minecraft:deepslate_diamond_ore minecraft:deepslate_redstone_ore minecraft:deepslate_lapis_ore minecraft:amethyst_shard minecraft:quartz
minecraft:wheat_seeds minecraft:wheat minecraft:beetroot_seeds minecraft:beetroot minecraft:pumpkin_seeds minecraft:pumpkin minecraft:melon_seeds minecraft:melon_slice minecraft:carrot minecraft:potato minecraft:sugar_cane minecraft:cactus minecraft:bamboo minecraft:kelp minecraft:dried_kelp minecraft:sweet_berries minecraft:glow_berries minecraft:cocoa_beans minecraft:brown_mushroom minecraft:red_mushroom minecraft:vine minecraft:lily_pad minecraft:seagrass minecraft:sea_pickle minecraft:honeycomb minecraft:honey_bottle
minecraft:poppy minecraft:dandelion minecraft:cornflower minecraft:blue_orchid minecraft:allium minecraft:azure_bluet minecraft:red_tulip minecraft:orange_tulip minecraft:white_tulip minecraft:pink_tulip minecraft:oxeye_daisy minecraft:lily_of_the_valley minecraft:sunflower minecraft:lilac minecraft:rose_bush minecraft:peony minecraft:fern minecraft:grass minecraft:tall_grass minecraft:dead_bush
minecraft:string minecraft:spider_eye minecraft:bone minecraft:rotten_flesh minecraft:gunpowder minecraft:ender_pearl minecraft:slime_ball minecraft:leather minecraft:feather minecraft:egg minecraft:beef minecraft:porkchop minecraft:chicken minecraft:mutton minecraft:rabbit minecraft:rabbit_hide minecraft:white_wool minecraft:milk_bucket minecraft:ink_sac minecraft:glow_ink_sac minecraft:phantom_membrane minecraft:arrow minecraft:bow minecraft:iron_ingot minecraft:cod minecraft:salmon minecraft:tropical_fish minecraft:pufferfish minecraft:nautilus_shell minecraft:prismarine_shard minecraft:prismarine_crystals minecraft:turtle_egg minecraft:scute minecraft:saddle minecraft:name_tag minecraft:book minecraft:paper minecraft:emerald
minecraft:netherrack minecraft:soul_sand minecraft:soul_soil minecraft:nether_wart minecraft:glowstone_dust minecraft:blaze_rod minecraft:magma_cream minecraft:ghast_tear minecraft:nether_quartz_ore minecraft:quartz minecraft:basalt minecraft:blackstone minecraft:crimson_stem minecraft:warped_stem minecraft:shroomlight minecraft:nether_brick minecraft:wither_skeleton_skull minecraft:ancient_debris minecraft:gold_nugget minecraft:magma_block
minecraft:zombie_head minecraft:skeleton_skull minecraft:totem_of_undying minecraft:enchanted_book minecraft:experience_bottle minecraft:music_disc_13 minecraft:heart_of_the_sea minecraft:echo_shard minecraft:sculk minecraft:sculk_catalyst
create:zinc_ore create:raw_zinc create:deepslate_zinc_ore
thermal:apatite_ore thermal:apatite thermal:cinnabar_ore thermal:cinnabar thermal:niter_ore thermal:niter thermal:sulfur_ore thermal:sulfur thermal:tin_ore thermal:raw_tin thermal:lead_ore thermal:raw_lead thermal:silver_ore thermal:raw_silver thermal:nickel_ore thermal:raw_nickel thermal:oil_sand thermal:oil_red_sand thermal:bitumen
biggerreactors:uranium_ore biggerreactors:deepslate_uranium_ore biggerreactors:uranium_chunk
geolosys:iron_cluster geolosys:copper_cluster geolosys:gold_cluster geolosys:tin_cluster geolosys:silver_cluster geolosys:lead_cluster geolosys:nickel_cluster geolosys:zinc_cluster geolosys:aluminum_cluster geolosys:uranium_cluster geolosys:platinum_cluster geolosys:osmium_cluster geolosys:hematite_ore geolosys:malachite_ore geolosys:coal_ore geolosys:galena_ore geolosys:sphalerite_ore geolosys:cassiterite_ore geolosys:bauxite_ore geolosys:cinnabar_ore geolosys:kimberlite_ore geolosys:lignite_ore geolosys:bituminous_coal_ore geolosys:anthracite_coal_ore geolosys:quartz_ore geolosys:azurite_ore geolosys:lapis_ore geolosys:gold_ore geolosys:autunite_ore geolosys:beryl_ore geolosys:platinum_ore geolosys:limonite_ore geolosys:teallite_ore geolosys:peat
farmersdelight:cabbage farmersdelight:cabbage_seeds farmersdelight:tomato farmersdelight:tomato_seeds farmersdelight:onion farmersdelight:rice farmersdelight:rice_panicle farmersdelight:wild_cabbages farmersdelight:wild_onions farmersdelight:wild_tomatoes farmersdelight:wild_carrots farmersdelight:wild_potatoes farmersdelight:wild_beetroots farmersdelight:wild_rice farmersdelight:brown_mushroom_colony farmersdelight:red_mushroom_colony farmersdelight:ham farmersdelight:minced_beef farmersdelight:straw farmersdelight:sandy_shrub farmersdelight:tree_bark
aquaculture:fish_fillet_raw aquaculture:bluegill aquaculture:perch aquaculture:catfish aquaculture:muskellunge aquaculture:rainbow_trout aquaculture:bass aquaculture:pike aquaculture:trout aquaculture:carp aquaculture:brown_trout aquaculture:goldfish aquaculture:jellyfish aquaculture:sunfish aquaculture:smallmouth_bass aquaculture:largemouth_bass aquaculture:gar aquaculture:tuna aquaculture:cod aquaculture:salmon aquaculture:red_grouper aquaculture:arapaima aquaculture:pollock aquaculture:tambaqui aquaculture:capitaine aquaculture:driftwood aquaculture:message_in_a_bottle aquaculture:neptunium_ingot aquaculture:box aquaculture:lockbox aquaculture:treasure_chest aquaculture:fish_bones aquaculture:frog_legs_raw aquaculture:turtle_soup
vinery:red_grape vinery:white_grape vinery:red_grape_seeds vinery:white_grape_seeds vinery:cherry vinery:apple_leaves vinery:grapevine_leaves
thermal:barley_seeds thermal:barley thermal:tomato_seeds thermal:tomato thermal:strawberry_seeds thermal:strawberry thermal:bell_pepper_seeds thermal:bell_pepper thermal:corn_seeds thermal:corn thermal:coffee_seeds thermal:coffee thermal:hops_seeds thermal:hops thermal:onion_seeds thermal:onion thermal:rice_seeds thermal:rice thermal:sadiroot_seeds thermal:sadiroot thermal:spinach_seeds thermal:spinach thermal:green_bean_seeds thermal:green_bean thermal:peanut_seeds thermal:peanut thermal:eggplant_seeds thermal:eggplant thermal:radish_seeds thermal:radish thermal:amaranth_seeds thermal:amaranth thermal:flax_seeds thermal:flax thermal:tea_seeds thermal:tea_leaf thermal:frost_melon_seeds thermal:frost_melon_slice
bakery:oat_seeds bakery:oat bakery:strawberry_seeds bakery:strawberry candlelight:tomato herbalbrews:mint_seeds herbalbrews:mint herbalbrews:tea_leaves herbalbrews:yerba_mate_leaves herbalbrews:green_tea_leaves herbalbrews:black_tea_leaves herbalbrews:rooibos_leaves herbalbrews:sunflower_leaves
ribbits:red_toadstool ribbits:swamp_lily duckling:duck_egg friendsandfoes:buttercup friendsandfoes:wildflower
deeperdarker:echo_shard deeperdarker:sculk_stone deeperdarker:echo_log deeperdarker:soul_dust
nethersdelight:hoglin_hide nethersdelight:hoglin_loin nethersdelight:stripped_warped_stem
artifacts:cross_necklace artifacts:snorkel artifacts:mystery_box artifacts:everlasting_beef artifacts:umbrella
waystones:waystone waystones:warp_stone
lootr:lootr_chest minecraft:bell
nethersdelight:propelpearl nethersdelight:propelplant_cane nethersdelight:strider_slice nethersdelight:hoglin_loin nethersdelight:hoglin_hide nethersdelight:soul_compound minecraft:warped_fungus minecraft:crimson_fungus minecraft:weeping_vines minecraft:twisting_vines
ae2:silicon_press ae2:logic_processor_press ae2:calculation_processor_press ae2:engineering_processor_press ae2:certus_quartz_crystal ae2:certus_quartz_dust ae2:quartz_block ae2:budding_quartz ae2:flawless_budding_quartz ae2:sky_stone_block ae2:sky_dust ae2:meteorite_compass ae2:sky_stone_chest
valley:token_bram valley:token_marnie valley:token_oda valley:token_nella valley:token_halden valley:token_tobin valley:token_wisp valley:token_pip valley:scrip valley:spring_water valley:lake_sand valley:kettle_plate_a valley:kettle_plate_b valley:turbine_notes valley:courier_parcel valley:bounty_receipt
'''.split())
FIRST = set(a.first_join.split(','))
# Wild plants (Farm & Charm and friends): whatever a wild_* block drops is a natural source.
import re as _re
for _p in glob.glob(f'{a.export}/loot_tables/*/blocks/wild_*.json') + glob.glob(f'{a.export}/loot_tables/minecraft/blocks/*grass*.json') + glob.glob(f'{a.export}/loot_tables/herbalbrews/blocks/*.json'):
    for _m in _re.findall(r'"name":\s*"([a-z0-9_]+:[a-z0-9_/]+)"', open(_p).read()):
        if not _m.endswith('/main') and _m != 'main': NATURAL.add(_m)
ALL_IDS = set(json.load(open('scratch/ids_valid.json'))['items']) if os.path.exists('scratch/ids_valid.json') else set()

# ---------------------------------------------------------------- the book
quests = {}
for f in sorted(glob.glob(f'{a.src}/*.json')):
    d = json.load(open(f))
    for q in d['quests']:
        q['_file'] = os.path.basename(f); quests[q['key']] = q
order, seen = [], set()
def visit(k, stack=()):
    if k in seen: return
    if k in stack: return
    for dep in quests.get(k, {}).get('deps', []): visit(dep, stack + (k,))
    seen.add(k); order.append(k)
for k in quests: visit(k)

have = set(NATURAL) | set(FIRST)
# items whose recipe is stage-gated in valley_gates.js: obtainable once the gate quest is done
STAGED = {'quarryplus:quarry': 'q86'}
def closure(have):
    changed = True
    fired = set()
    while changed:
        changed = False
        for i, (rid, t, needs, makes) in enumerate(RECIPES):
            if i in fired: continue
            ok = True
            for g in needs:
                met = False
                for kind, v in g:
                    if kind == 'item' and v in have: met = True; break
                    if kind == 'tag' and any(x in have for x in tag_items(v)): met = True; break
                if not met: ok = False; break
            if ok:
                fired.add(i)
                for m in makes:
                    if m not in have: have.add(m); changed = True
        # Farmer's Delight feasts and the like: the recipe makes X_block, the player slices X off it
        for m in list(have):
            if m.endswith('_block') and m[:-6] in ALL_IDS and m[:-6] not in have:
                have.add(m[:-6]); changed = True
    return have
have = closure(have)
problems = []
for k in order:
    q = quests[k]
    for t in q.get('tasks', []):
        if t.get('type') == 'item':
            it = t['item']
            if it not in have:
                problems.append((k, q['_file'], q.get('title', ''), it))
    for it, gate in STAGED.items():
        if gate == k: have.add(it)
    for r in q.get('rewards', []):
        if r.get('type') == 'item' and r.get('item'): have.add(r['item'])
        if r.get('type') == 'loot':
            # every table item is a possible drop; treat as obtainable
            for f in glob.glob(f'{a.src}/*.json'):
                for tb in json.load(open(f)).get('reward_tables', []):
                    if tb['key'] == r['table']:
                        for x in tb['rewards']:
                            if x.get('item'): have.add(x['item'])
    have = closure(have)
print(f'quests {len(order)}  recipes {len(RECIPES)}  natural {len(NATURAL)}  obtainable at end {len(have)}')
for k, f, title, it in problems:
    print(f'  UNOBTAINABLE  {it:45s} <- {k} ({f}) "{title}"')
print(f'{len(problems)} unobtainable task items')
if a.why:
    def why(item, depth=0, seen=set()):
        pad='  '*depth
        if item in have: print(f'{pad}{item}: OBTAINABLE' + (' (natural)' if item in NATURAL else '')); return
        rs=[r for r in RECIPES if item in r[3]]
        print(f'{pad}{item}: not obtainable; {len(rs)} recipe(s)')
        for rid,t,needs,makes in rs[:4]:
            missing=[]
            for g in needs:
                if any((k=='item' and v in have) or (k=='tag' and any(x in have for x in tag_items(v))) for k,v in g): continue
                missing.append(' | '.join(('#'+v if k=='tag' else v) for k,v in g[:4]))
            print(f'{pad}  via {rid} [{t}] missing {missing}')
            if depth<3:
                for m in missing[:3]:
                    if not m.startswith('#') and m not in seen: seen.add(m); why(m, depth+1, seen)
    why(a.why)
if a.json: json.dump({'problems': problems, 'obtainable': sorted(have)}, open(a.json, 'w'))
sys.exit(1 if problems else 0)
