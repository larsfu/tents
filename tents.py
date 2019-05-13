"""
A set partitioning model of a tent allocation problem

Lars Funke 2019, adapted from Stuart Mitchell 2009
"""

import pulp
from pulp import lpSum
import collections

# key: tent capacity, value: tent count
# ascending size is required! (maybe sorting should be put in place)
tents = collections.OrderedDict(((4, 2), (6, 4))) 
participants = (tuple(range(18)), tuple(range(18, 30))) # two disjunct sets
preferences = ( # like and dislike list for every participant
	((1,2,3), (6,6,6)), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ()),
	((), ()), ((), ())
)

assert sum([i*j for i,j in zip(tents.keys(), tents.values())]) >= sum([len(p) for p in participants]), "Not enough beds."

possible_tents = [tuple(c) for p in participants for c in pulp.allcombinations(p, max(tents.keys()))]

def happiness(tent):
    """
    Find the happiness of the tent
    """
    like = sum([(i in tent) for p in tent for i in preferences[p][0]])
    dislike = sum([(i in tent) for p in tent for i in preferences[p][1]]) * 1.01 # dislike is stronger than like (when tie)
    return like - dislike # + len(tent) maybe?

#create a binary variable to state that a tent setting is used
x = pulp.LpVariable.dicts("tent", possible_tents, lowBound = 0, upBound = 1, cat = pulp.LpInteger)

tent_model = pulp.LpProblem("Tent Partitioning Model", pulp.LpMaximize)

tent_model += lpSum([happiness(tent) * x[tent] for tent in possible_tents])

# specify the maximum number of tents
tent_model += lpSum([x[tent] for tent in possible_tents]) <= sum(tents.values())

# limit tent capacity
tentlist = tents.items()
for index, (tent_type, tent_count) in enumerate(tentlist):
	above = sum(dict(list(tentlist)[index+1:]).values()) # number of tents with capacities larger than the current tent
	tent_model += lpSum([x[tent] for tent in possible_tents if len(tent) > tent_type]) <= above

# A participant must be in one tent
for participant in [ps for t in participants for ps in t]:
	tent_model += lpSum([x[tent] for tent in possible_tents if participant in tent]) == 1

solver = pulp.solvers.COIN_CMD("cbc", threads=4, msg=1)
tent_model.solve(solver)

print(f"The chosen tents are out of a total of {len(possible_tents)}")
for tent in possible_tents:
    if x[tent].value() == 1.0:
        print(tent)
