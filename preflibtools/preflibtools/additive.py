#!python3
"""
Generate all ordinal preferences over bundles that are compatible with an additive value function.

Author:  Erel Segal-Halevi
Date:    2017-06
*******  UNDER CONSTRUCTION   *******
"""

def positiveAdditivePreferences(items: string):
	"""
		Generate all strict ordinal preferences over bundles that are compatible with a positive additive value function.

		INPUT:
		items: a string in which each char is an item name.

		OUTPUT: 
		a generator that generates lists of strings; each list is a preference-ranking.

		>>> list(positiveAdditivePreferences("x"))
		[["","x"]]

		>>> list(positiveAdditivePreferences("xy"))
		[["","x","y","xy"],["","y","x","xy"]]
	"""
	if len(items)==1:  # recursion base
		return [["",items]]
	else:              # recursion step
		firstItems = items[:-1]
		lastItem = items[-1]
		for prefWithoutNewItem in positiveAdditivePreferences(firstItems):
			prefWithNewItem = [bundle+lastItem for bundle in prefWithoutNewItem]
			

if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print("Doctest OK!\n")
