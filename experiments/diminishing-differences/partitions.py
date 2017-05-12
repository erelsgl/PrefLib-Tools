#!python3
"""
This unit contains functions that loop over all possible partitions of items to agents.

Author: Erel Segai-Halevi
Date:   2017-02
"""

import itertools

from itertools import combinations

def equalPartitions(agents, items):
	"""
	Generates all partitions of 'items' that give each agent in 'agents' an equal number of items.

	INPUT: agents (list), items (list).
	Currently, at most 3 agents are supported.

	OUTPUT: partitions (dictionaries that map agents to item-lists)

	CODE: Zero Piraeus, http://stackoverflow.com/a/42304815/827927

	>>> for p in equalPartitions(["A","B"], [1,2,3,4]): pprint(p)
	{'A': {1, 2}, 'B': [3, 4]}
	{'A': {1, 3}, 'B': [2, 4]}
	{'A': {1, 4}, 'B': [2, 3]}
	{'A': {2, 3}, 'B': [1, 4]}
	{'A': {2, 4}, 'B': [1, 3]}
	{'A': {3, 4}, 'B': [1, 2]}

	>>> for p in equalPartitions(["A","B","C"], [1,2,3,4,5,6]): pprint(p)
	{'A': {1, 2}, 'B': {3, 4}, 'C': [5, 6]}
	{'A': {1, 2}, 'B': {3, 5}, 'C': [4, 6]}
	{'A': {1, 2}, 'B': {3, 6}, 'C': [4, 5]}
	{'A': {1, 2}, 'B': {4, 5}, 'C': [3, 6]}
	{'A': {1, 2}, 'B': {4, 6}, 'C': [3, 5]}
	{'A': {1, 2}, 'B': {5, 6}, 'C': [3, 4]}
	{'A': {1, 3}, 'B': {2, 4}, 'C': [5, 6]}
	{'A': {1, 3}, 'B': {2, 5}, 'C': [4, 6]}
	{'A': {1, 3}, 'B': {2, 6}, 'C': [4, 5]}
	{'A': {1, 3}, 'B': {4, 5}, 'C': [2, 6]}
	{'A': {1, 3}, 'B': {4, 6}, 'C': [2, 5]}
	{'A': {1, 3}, 'B': {5, 6}, 'C': [2, 4]}
	{'A': {1, 4}, 'B': {2, 3}, 'C': [5, 6]}
	{'A': {1, 4}, 'B': {2, 5}, 'C': [3, 6]}
	{'A': {1, 4}, 'B': {2, 6}, 'C': [3, 5]}
	{'A': {1, 4}, 'B': {3, 5}, 'C': [2, 6]}
	{'A': {1, 4}, 'B': {3, 6}, 'C': [2, 5]}
	{'A': {1, 4}, 'B': {5, 6}, 'C': [2, 3]}
	{'A': {1, 5}, 'B': {2, 3}, 'C': [4, 6]}
	{'A': {1, 5}, 'B': {2, 4}, 'C': [3, 6]}
	{'A': {1, 5}, 'B': {2, 6}, 'C': [3, 4]}
	{'A': {1, 5}, 'B': {3, 4}, 'C': [2, 6]}
	{'A': {1, 5}, 'B': {3, 6}, 'C': [2, 4]}
	{'A': {1, 5}, 'B': {4, 6}, 'C': [2, 3]}
	{'A': {1, 6}, 'B': {2, 3}, 'C': [4, 5]}
	{'A': {1, 6}, 'B': {2, 4}, 'C': [3, 5]}
	{'A': {1, 6}, 'B': {2, 5}, 'C': [3, 4]}
	{'A': {1, 6}, 'B': {3, 4}, 'C': [2, 5]}
	{'A': {1, 6}, 'B': {3, 5}, 'C': [2, 4]}
	{'A': {1, 6}, 'B': {4, 5}, 'C': [2, 3]}
	{'A': {2, 3}, 'B': {1, 4}, 'C': [5, 6]}
	{'A': {2, 3}, 'B': {1, 5}, 'C': [4, 6]}
	{'A': {2, 3}, 'B': {1, 6}, 'C': [4, 5]}
	{'A': {2, 3}, 'B': {4, 5}, 'C': [1, 6]}
	{'A': {2, 3}, 'B': {4, 6}, 'C': [1, 5]}
	{'A': {2, 3}, 'B': {5, 6}, 'C': [1, 4]}
	{'A': {2, 4}, 'B': {1, 3}, 'C': [5, 6]}
	{'A': {2, 4}, 'B': {1, 5}, 'C': [3, 6]}
	{'A': {2, 4}, 'B': {1, 6}, 'C': [3, 5]}
	{'A': {2, 4}, 'B': {3, 5}, 'C': [1, 6]}
	{'A': {2, 4}, 'B': {3, 6}, 'C': [1, 5]}
	{'A': {2, 4}, 'B': {5, 6}, 'C': [1, 3]}
	{'A': {2, 5}, 'B': {1, 3}, 'C': [4, 6]}
	{'A': {2, 5}, 'B': {1, 4}, 'C': [3, 6]}
	{'A': {2, 5}, 'B': {1, 6}, 'C': [3, 4]}
	{'A': {2, 5}, 'B': {3, 4}, 'C': [1, 6]}
	{'A': {2, 5}, 'B': {3, 6}, 'C': [1, 4]}
	{'A': {2, 5}, 'B': {4, 6}, 'C': [1, 3]}
	{'A': {2, 6}, 'B': {1, 3}, 'C': [4, 5]}
	{'A': {2, 6}, 'B': {1, 4}, 'C': [3, 5]}
	{'A': {2, 6}, 'B': {1, 5}, 'C': [3, 4]}
	{'A': {2, 6}, 'B': {3, 4}, 'C': [1, 5]}
	{'A': {2, 6}, 'B': {3, 5}, 'C': [1, 4]}
	{'A': {2, 6}, 'B': {4, 5}, 'C': [1, 3]}
	{'A': {3, 4}, 'B': {1, 2}, 'C': [5, 6]}
	{'A': {3, 4}, 'B': {1, 5}, 'C': [2, 6]}
	{'A': {3, 4}, 'B': {1, 6}, 'C': [2, 5]}
	{'A': {3, 4}, 'B': {2, 5}, 'C': [1, 6]}
	{'A': {3, 4}, 'B': {2, 6}, 'C': [1, 5]}
	{'A': {3, 4}, 'B': {5, 6}, 'C': [1, 2]}
	{'A': {3, 5}, 'B': {1, 2}, 'C': [4, 6]}
	{'A': {3, 5}, 'B': {1, 4}, 'C': [2, 6]}
	{'A': {3, 5}, 'B': {1, 6}, 'C': [2, 4]}
	{'A': {3, 5}, 'B': {2, 4}, 'C': [1, 6]}
	{'A': {3, 5}, 'B': {2, 6}, 'C': [1, 4]}
	{'A': {3, 5}, 'B': {4, 6}, 'C': [1, 2]}
	{'A': {3, 6}, 'B': {1, 2}, 'C': [4, 5]}
	{'A': {3, 6}, 'B': {1, 4}, 'C': [2, 5]}
	{'A': {3, 6}, 'B': {1, 5}, 'C': [2, 4]}
	{'A': {3, 6}, 'B': {2, 4}, 'C': [1, 5]}
	{'A': {3, 6}, 'B': {2, 5}, 'C': [1, 4]}
	{'A': {3, 6}, 'B': {4, 5}, 'C': [1, 2]}
	{'A': {4, 5}, 'B': {1, 2}, 'C': [3, 6]}
	{'A': {4, 5}, 'B': {1, 3}, 'C': [2, 6]}
	{'A': {4, 5}, 'B': {1, 6}, 'C': [2, 3]}
	{'A': {4, 5}, 'B': {2, 3}, 'C': [1, 6]}
	{'A': {4, 5}, 'B': {2, 6}, 'C': [1, 3]}
	{'A': {4, 5}, 'B': {3, 6}, 'C': [1, 2]}
	{'A': {4, 6}, 'B': {1, 2}, 'C': [3, 5]}
	{'A': {4, 6}, 'B': {1, 3}, 'C': [2, 5]}
	{'A': {4, 6}, 'B': {1, 5}, 'C': [2, 3]}
	{'A': {4, 6}, 'B': {2, 3}, 'C': [1, 5]}
	{'A': {4, 6}, 'B': {2, 5}, 'C': [1, 3]}
	{'A': {4, 6}, 'B': {3, 5}, 'C': [1, 2]}
	{'A': {5, 6}, 'B': {1, 2}, 'C': [3, 4]}
	{'A': {5, 6}, 'B': {1, 3}, 'C': [2, 4]}
	{'A': {5, 6}, 'B': {1, 4}, 'C': [2, 3]}
	{'A': {5, 6}, 'B': {2, 3}, 'C': [1, 4]}
	{'A': {5, 6}, 'B': {2, 4}, 'C': [1, 3]}
	{'A': {5, 6}, 'B': {3, 4}, 'C': [1, 2]}
	"""
	if len(agents) == 1:
		yield {agents[0]: items}
	else:
		quota = len(items) // len(agents)
		for indexes in combinations(range(len(items)), quota):
			remainder = items[:]
			selection = {remainder.pop(i) for i in reversed(indexes)}
			for result in equalPartitions(agents[1:], remainder):
				result[agents[0]] = selection
				yield result


if __name__ == "__main__":
	from pprint import pprint
	import doctest
	doctest.testmod()