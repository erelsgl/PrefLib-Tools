#!python3
"""
Procedures for fair item assignment.

Author: Erel Segai-Halevi
Date:   2017-02
"""

from Pref import Pref
from PrefProfile import PrefProfile
from partitions import equalPartitions
import copy
import itertools
from operator import itemgetter



def findNDDProportionalAllocation(prefProfile):
    """
    INPUT:
    prefProfile: a PrefProfile object.

    OUTPUT:
    If an NDDPR allocation exists - it is returned as a dictionary that maps agents to their bundles.
    Otherwise - None is returned.

    >>> prefProfile = PrefProfile({"Alice":Pref([6,5,4,3,2,1]), "Bob":Pref([6,5,4,3,2,1]), "Carl":Pref([6,5,4,3,2,1])})
    >>> findNDDProportionalAllocation(prefProfile) is None
    True

    >>> prefProfile = PrefProfile({"Alice":Pref([6,5,4,3,2,1]), "Bob":Pref([5,6,4,3,2,1]), "Carl":Pref([4,5,6,3,2,1])})
    >>> allocation = findNDDProportionalAllocation(prefProfile)
    >>> sorted(allocation.items(),  key=lambda t: t[0])
    [('Alice', [6, 1]), ('Bob', [5, 2]), ('Carl', [4, 3])]
    """
    itemsPerAgent = prefProfile.itemCount // prefProfile.agentCount

    # First necessary condition for NDDPR allocation:  it is possible to give each agent the same num of items:
    if itemsPerAgent * prefProfile.agentCount < prefProfile.itemCount:
        return None

    # Second necessary condition for NDDPR allocation: it is possible to give each agent its best item.
    bestItems = {pref.bestItem() for pref in prefProfile.prefs}
    if len(bestItems) < prefProfile.agentCount:
        return None

    allocation = {agent:list() for agent in prefProfile.agents}
    prefProfile = copy.deepcopy(prefProfile)
    for iteration in range(itemsPerAgent):
        for agent in prefProfile.agents:
            item = prefProfile.agentsToPrefs[agent].bestItem()
            allocation[agent].append(item)
            prefProfile.removeItem(item)
        prefProfile.agents.reverse()
    return allocation

def findABCCBAAllocation(prefProfile):
    """
    INPUT:
    prefProfile: a PrefProfile object.

    OUTPUT:
    An allocation where the agents pick in sequence A B C C B A A B C ...

    >>> prefProfile = PrefProfile({"Alice":Pref([6,5,4,3,2,1]), "Bob":Pref([6,5,4,3,2,1]), "Carl":Pref([6,5,4,3,2,1])})
    >>> allocation = findABCCBAAllocation(prefProfile)
    >>> sorted(allocation.items(),  key=lambda t: t[0])
    [('Alice', [6, 1]), ('Bob', [5, 2]), ('Carl', [4, 3])]

    >>> prefProfile = PrefProfile({"Alice":Pref([6,5,4,3,2,1]), "Bob":Pref([5,6,4,3,2,1]), "Carl":Pref([4,5,6,3,2,1])})
    >>> allocation = findABCCBAAllocation(prefProfile)
    >>> sorted(allocation.items(),  key=lambda t: t[0])
    [('Alice', [6, 1]), ('Bob', [5, 2]), ('Carl', [4, 3])]
    """
    itemsPerAgent = prefProfile.itemCount // prefProfile.agentCount
    allocation = {agent:list() for agent in prefProfile.agents}
    prefProfile = copy.deepcopy(prefProfile)
    for iteration in range(itemsPerAgent):
        for agent in prefProfile.agents:
            item = prefProfile.agentsToPrefs[agent].bestItem()
            allocation[agent].append(item)
            prefProfile.removeItem(item)
        prefProfile.agents.reverse()
    return allocation


def findNecessarilyFairAllocation(prefProfile:PrefProfile, isFair:bool):
    """
    INPUT:
    prefProfile: a PrefProfile with ordinal rankings.
    Currently, at most 3 agents are supported.
    isFair: a boolean-valued function that checks whether an allocation is fair  (prop/ef)

    OUTPUT:
    A necessarily-fair allocation (map of agents to bundles), if it exists.

    EXAMPLES: see below, findNecessarilyProportionalAllocation
    """

    agentCount = prefProfile.agentCount
    if agentCount>3:
        raise ValueError("Currently findNecessarilyFairAllocation works only for at most three agents")
    itemCount = prefProfile.itemCount
    itemsPerAgent = itemCount // agentCount

    # First necessary condition for necessarily-fair allocation:  it is possible to give each agent the same num of items:
    if itemsPerAgent * agentCount < itemCount:
        return None

    # Second necessary condition for necessarily-fair allocation: it is possible to give each agent its best item.
    bestItems = {agent:prefProfile.agentsToPrefs[agent].bestItem() for agent in prefProfile.agents}
    if len(set(bestItems.values())) < agentCount:
        return None

    prof = copy.deepcopy(prefProfile)
    for agent in prof.agents:
        prof.removeItem(bestItems[agent])

    itemsPerAgent -= 1

    agents = prof.agents;
    # Try all combinations of the other items:
    agent0 = agents[0]
    agent1 = agents[1]
    if prof.agentCount>=3: agent2 = agents[2]
    for p in equalPartitions(agents, prof.items):
        allocation = {
            agent0: [bestItems[agent0]] + p[agent0],
            agent1: [bestItems[agent1]] + p[agent1]
            }
        if prof.agentCount>=3:
            allocation[agent2] = [bestItems[agent2]] + p[agent2]
        if isFair(prefProfile,allocation):
            return allocation
    return None

def findNecessarilyProportionalAllocation(prefProfile):
    """
    INPUT:
    prefProfile: a PrefProfile with ordinal ranking.
    Currently, at most 3 agents are supported.

    OUTPUT:
    A necessarily-proportional allocation (map of agents to bundles), if it exists.

    >>> prefProfile = PrefProfile({"Alice":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1}), "Bob":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1})})
    >>> findNecessarilyProportionalAllocation(prefProfile) is None
    True

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[6,5,4,3,2,1]), "Bob":Pref(ordinal=[5,6,3,4,1,2])})
    >>> allocation = findNecessarilyProportionalAllocation(prefProfile)
    >>> allocation['Alice']
    [6, 4, 2]
    >>> allocation['Bob']
    [5, 1, 3]

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[2,1,3,4,6,5]), "Bob":Pref(ordinal=[4,3,6,5,2,1])})
    >>> allocation = findNecessarilyProportionalAllocation(prefProfile)
    >>> allocation['Alice']
    [2, 3, 1]
    >>> allocation['Bob']
    [4, 5, 6]
    """
    return findNecessarilyFairAllocation(prefProfile, isNecessarilyProportional)

def findNecessarilyEnvyFreeAllocation(prefProfile):
    """
    INPUT:
    prefProfile: a PrefProfile with ordinal ranking.
    Currently, at most 3 agents are supported.

    OUTPUT:
    A necessarily-envy-free allocation (map of agents to bundles), if it exists.

    >>> prefProfile = PrefProfile({"Alice":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1}), "Bob":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1})})
    >>> findNecessarilyEnvyFreeAllocation(prefProfile) is None
    True

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[6,5,4,3,2,1]), "Bob":Pref(ordinal=[5,6,3,4,1,2])})
    >>> allocation = findNecessarilyEnvyFreeAllocation(prefProfile)
    >>> allocation['Alice']
    [6, 4, 2]
    >>> allocation['Bob']
    [5, 1, 3]

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[2,1,3,4,6,5]), "Bob":Pref(ordinal=[4,3,6,5,2,1])})
    >>> allocation = findNecessarilyEnvyFreeAllocation(prefProfile)
    >>> allocation['Alice']
    [2, 3, 1]
    >>> allocation['Bob']
    [4, 5, 6]
    """
    return findNecessarilyFairAllocation(prefProfile, isNecessarilyEnvyFree)


def isCardinallyProportional(prefProfile, allocation):
    """
    INPUT:
    prefProfile: a PrefProfile with cardinal utilities.
    allocation: a dictionary that maps agents to their bundles.

    OUTPUT:
    True iff the given allocation is proportional according to the agents' cardinal value function

    >>> prefProfile = PrefProfile({"Alice":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1}), "Bob":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1}), "Carl":Pref(cardinal={6:6,5:5,4:4,3:3,2:2,1:1})})

    >>> allocation = {"Alice":[6,1], "Bob":[5,2], "Carl":[4,3]}
    >>> isCardinallyProportional(prefProfile,allocation)
    True

    >>> allocation = {"Alice":[6,2], "Bob":[5,1], "Carl":[4,3]}
    >>> isCardinallyProportional(prefProfile,allocation)
    False

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[2,1,3,4,6,5]), "Bob":Pref(ordinal=[4,3,6,5,2,1])})
    """
    agentCount = prefProfile.agentCount
    for (agent,pref) in prefProfile.agentsToPrefs.items():
        agentsValue = pref.valueOf(allocation[agent])
        totalValue  = pref.valueOf(pref.ordinal) # all items
        if agentsValue * agentCount < totalValue:
            return False
    return True




def duplicateEachItem(bundle,times):
    """
    >>> list(duplicateEachItem([2,1,3],3))
    [2, 2, 2, 1, 1, 1, 3, 3, 3]
    """
    return itertools.chain.from_iterable([item]*times for item in bundle)


def isProportional(prefProfile, allocation, isWeaklyBetter):
    """
    INPUT:
    prefProfile: a dictionary that maps agents to their Pref object.
    allocation: a dictionary that maps agents to their bundles.
    isWeaklyBetter: a boolean function on Pref and two bundles. Returns True iff bundle1 >= bundle2 according to the Pref.ordinal ranking.

    OUTPUT:
    True iff the given allocation is proportional according to the agents' ordinal ranking.

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[6,5,4,3,2,1]), "Bob":Pref(ordinal=[5,6,3,4,1,2])})

    >>> allocation = {"Alice":[6,4,2], "Bob":[5,3,1]}
    >>> isNecessarilyProportional(prefProfile,allocation)
    True
    >>> isNDDProportional(prefProfile,allocation)
    True

    >>> allocation = {"Alice":[6,4], "Bob":[5,3]}
    >>> isNecessarilyProportional(prefProfile,allocation)
    False
    >>> isNDDProportional(prefProfile,allocation)
    False

    >>> allocation = {"Alice":[6,3,2], "Bob":[5,4,1]}
    >>> isNecessarilyProportional(prefProfile,allocation)
    False
    >>> isNDDProportional(prefProfile,allocation)
    True

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[2,1,3,4,6,5]), "Bob":Pref(ordinal=[4,3,6,5,2,1])})

    >>> allocation = {"Alice":[1,2,3], "Bob":[4,5,6]}
    >>> isNecessarilyProportional(prefProfile,allocation)
    True
    >>> isNDDProportional(prefProfile,allocation)
    True

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[6,5,4,3,2,1]), "Bob":Pref(ordinal=[4,3,6,5,2,1]),"Carl":Pref(ordinal=[5,1,3,4,6,2])})

    >>> allocation = {"Alice":[6,2], "Bob":[4,3], "Carl": [5,1]}
    >>> isNecessarilyProportional(prefProfile,allocation)
    False
    >>> isNDDProportional(prefProfile,allocation)
    True
    """
    itemCount = prefProfile.itemCount
    agentCount = prefProfile.agentCount
    for (agent,pref) in prefProfile.agentsToPrefs.items():
        bundle = allocation[agent]
        duplicateBundle = list(duplicateEachItem(bundle, agentCount))
        if not isWeaklyBetter(pref, duplicateBundle, pref.ordinal):
            return False
    return True

def isNecessarilyProportional(prefProfile, allocation):
    return isProportional(prefProfile, allocation, Pref.isNecessarilyWeaklyBetter)

def isNDDProportional(prefProfile, allocation):
    return isProportional(prefProfile, allocation, Pref.isNDDWeaklyBetter)

def isPDDProportional(prefProfile, allocation):
    return isProportional(prefProfile, allocation, Pref.isPDDWeaklyBetter)

def isPossiblyProportional(prefProfile, allocation):
    return isProportional(prefProfile, allocation, Pref.isPossiblyWeaklyBetter)



def isEnvyFree(prefProfile, allocation, isWeaklyBetter):
    """
    INPUT:
    prefProfile: a PrefProfile object.
    allocation: a dictionary that maps agents to their bundles.
    isWeaklyBetter: a boolean function on Pref and two bundles. Returns True iff bundle1 >= bundle2 according to the Pref.ordinal ranking.

    OUTPUT:
    True iff the given allocation is envy-free according to the agents' ordinal ranking.

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[6,5,4,3,2,1]), "Bob":Pref(ordinal=[5,6,3,4,1,2])})

    >>> allocation = {"Alice":[6,4,2], "Bob":[5,3,1]}
    >>> isNecessarilyEnvyFree(prefProfile,allocation)
    True
    >>> isNDDEnvyFree(prefProfile,allocation)
    True
    >>> isPDDEnvyFree(prefProfile,allocation)
    True
    >>> isPossiblyEnvyFree(prefProfile,allocation)
    True

    >>> allocation = {"Alice":[6,4], "Bob":[5,3]}
    >>> isNecessarilyEnvyFree(prefProfile,allocation)
    True
    >>> isNDDEnvyFree(prefProfile,allocation)
    True
    >>> isPDDEnvyFree(prefProfile,allocation)
    True
    >>> isPossiblyEnvyFree(prefProfile,allocation)
    True

    >>> allocation = {"Alice":[6,3,1], "Bob":[5,4,2]}
    >>> isNecessarilyEnvyFree(prefProfile,allocation)
    False
    >>> isNDDEnvyFree(prefProfile,allocation)
    False
    >>> isPDDEnvyFree(prefProfile,allocation)
    True
    >>> isPossiblyEnvyFree(prefProfile,allocation)
    True

    >>> prefProfile = PrefProfile({"Alice":Pref(ordinal=[2,1,3,4,6,5]), "Bob":Pref(ordinal=[4,3,6,5,2,1])})
    >>> allocation = {"Alice":[1,2,3], "Bob":[4,5,6]}
    >>> isNecessarilyEnvyFree(prefProfile,allocation)
    True
    """
    itemCount = prefProfile.itemCount
    agentCount = prefProfile.agentCount
    for (agent1,pref1) in prefProfile.agentsToPrefs.items():
        bundle1 = allocation[agent1]
        for agent2 in prefProfile.agents:
            if agent2==agent1: continue
            bundle2 = allocation[agent2]
            if not isWeaklyBetter(pref1, bundle1, bundle2):
                return False
    return True


def isNecessarilyEnvyFree(prefProfile, allocation):
    return isEnvyFree(prefProfile, allocation, Pref.isNecessarilyWeaklyBetter)

def isPossiblyEnvyFree(prefProfile, allocation):
    return isEnvyFree(prefProfile, allocation, Pref.isPossiblyWeaklyBetter)

def isNDDEnvyFree(prefProfile, allocation):
    return isEnvyFree(prefProfile, allocation, Pref.isNDDWeaklyBetter)

def isPDDEnvyFree(prefProfile, allocation):
    return isEnvyFree(prefProfile, allocation, Pref.isPDDWeaklyBetter)



if __name__ == "__main__":
    import doctest
    print(doctest.testmod())

    items = [1,2,3,4,5,6]
    agents = ["A","B","C"]
    prefProfile = PrefProfile({agent:Pref.randomOrdinal(items) for agent in agents})
    print (prefProfile)
    allocation = findNDDProportionalAllocation(prefProfile)
    print (allocation)

    agents = ["A","B"]
    prefProfile = PrefProfile({agent:Pref.randomOrdinal(items) for agent in agents})
    print (prefProfile)
    allocation = findNecessarilyProportionalAllocation(prefProfile)
    print (allocation)
