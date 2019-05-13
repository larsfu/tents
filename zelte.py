
"""
A set partitioning model of a wedding seating problem

Authors: Stuart Mitchell 2009
"""

import pulp
import collections

tents = collections.OrderedDict(((6, 4), (4, 2))) #ascending size is required! (maybe sorting should be put in place)
participants = (tuple(range(18)), tuple(range(18, 30)))

assert sum([i*j for i,j in zip(tents.keys(), tents.values())]) >= sum([len(p) for p in participants]), "Not enough beds."

possible_tents = [tuple(c) for p in participants for c in pulp.allcombinations(p, max(tents.keys()))]

def happiness(tent):
    """
    Find the happiness of the table
    - by calculating the maximum distance between the letters
    """
    return len(tent)

#print([happiness(tent) for tent in possible_tents])

#create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts('tent', possible_tents, 
                            lowBound = 0,
                            upBound = 1,
                            cat = pulp.LpInteger)

tent_model = pulp.LpProblem("Tent Partitioning Model", pulp.LpMaximize)

tent_model += sum([happiness(tent) * x[tent] for tent in possible_tents])

# specify the maximum number of tents
tent_model += sum([x[tent] for tent in possible_tents]) <= sum(tents.values()), "Maximum_number_of_tents"

# limit tent capacity
tentlist = tents.items()
for index, (tent_type, tent_count) in enumerate(tentlist):
	above = sum(dict(list(tentlist)[index+1:]).values()) # number of tents with capacities larger than the current tent
	tent_model += sum([x[tent] for tent in possible_tents if len(tent) > tent_type]) <= above, f"Tent_{tent_type}"

# A participant be in one tent
for participant in [ps for t in participants for ps in t]:
	tent_model += sum([x[tent] for tent in possible_tents if participant in tent]) == 1, f"Must_accomodate_{participant}"


solver = pulp.solvers.COIN_CMD('cbc', threads=4, msg=1, fracGap = 0.01)
tent_model.solve(solver)

print("The choosen tables are out of a total of %s:"%len(possible_tents))
for tent in possible_tents:
    if x[tent].value() == 1.0:
        print(tent)
