"""
A set partitioning model of a tent allocation problem

Lars Funke 2019, adapted from Stuart Mitchell 2009
"""

import pulp
from pulp import lpSum
import collections
import json
import math
from graphviz import Digraph
import numpy as np

# key: tent capacity, value: tent count
# ascending capacity is required! (maybe sorting should be put in place)
#tents = collections.OrderedDict(((3, 1), (4, 2), (5, 1), (6, 1)))
tents = collections.OrderedDict(((4, 2), (6, 4)))
with open('participants.json') as f:
    participant_names = json.load(f)
    #FIXME for more than 2 groups.
    participants = (tuple(range(len(participant_names[0]))), 
        tuple(range(len(participant_names[0]), len(participant_names[0]) + len(participant_names[1]))))

with open('preferences_.json') as f:
    preferences = json.load(f)

# genereate sociograms
counter = 0
for s, pn in enumerate(participant_names):
    dot = Digraph(engine='circo')
    dot.attr(concentrate='true')
    local_counter = 0
    for i, p in enumerate(pn):
        i += counter
        local_counter += 1
        dot.node(str(i), p)
        for j in set(preferences[i][0]):
            dot.edge(str(i), str(j))
        for j in set(preferences[i][1]):
            dot.edge(str(i), str(j), color="red")
    counter += local_counter
    dot.render(f'sociogram{s}')


assert sum([i*j for i,j in zip(tents.keys(), tents.values())]) >= sum([len(p) for p in participants]), "Not enough capacity."

# generate all possible participant combinations up to the maximum tent capacity
possible_tents = [tuple(c) for p in participants for c in pulp.allcombinations(p, max(tents.keys()))]

def happiness(person, tent):
    like = sum([(i in tent) for i in preferences[person][0]])
    dislike = sum([(i in tent) for i in preferences[person][1]])
    return like - (2 * dislike) ** 1.5

def tent_happiness(tent):
    """
    Find the happiness of the tent
    """
    #like = sum([(i in tent) for p in tent for i in preferences[p][0]])
    #dislike = sum([(i in tent) for p in tent for i in preferences[p][1]])
    return sum([happiness(person, tent) for person in tent])

# create a binary variable to state that a tent setting is used
x = pulp.LpVariable.dicts("tent", possible_tents, cat=pulp.LpBinary)

tent_model = pulp.LpProblem("Tent Partitioning Model", pulp.LpMaximize)

# apply happiness
tent_model += lpSum([tent_happiness(tent) * x[tent] for tent in possible_tents])

# specify the maximum number of tents
tent_model += lpSum([x[tent] for tent in possible_tents]) <= sum(tents.values())

# limit tent capacity
tentlist = tents.items()
for index, (tent_type, tent_count) in enumerate(tentlist):
    above = sum(dict(list(tentlist)[index+1:]).values())  # number of tents with capacities larger than the current tent
    tent_model += lpSum([x[tent] for tent in possible_tents if len(tent) > tent_type]) <= above

# A participant must be in one tent
for participant in [ps for t in participants for ps in t]:
    tent_model += lpSum([x[tent] for tent in possible_tents if participant in tent]) == 1

solver = pulp.solvers.COIN_CMD("cbc", threads=4, msg=1)
tent_model.solve(solver)

print(f"The chosen tents are out of a total of {len(possible_tents)}")
flat = participant_names[0] + participant_names[1]

participant_happiness = [0] * len(flat)
for tent in possible_tents:
    if x[tent].value() == 1.0:
        print(list(map(lambda i: flat[i], tent)))
        for p in tent:
            participant_happiness[p] = happiness(p, tent)

for h, p in sorted(zip(participant_happiness, flat)):
    print(f"{p:>10}: {h:>2}")