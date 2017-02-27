#!python3
"""
Finding level-1-consensus in a preference-profile.

Level-1-consensus is a new domain-restriction invented by Mahajne and Nitzan and Volij.
See "Level r consensus and stable social choice", Social Choice and Welfare 2015.

Author:  Erel Segal-Halevi
Date:    2017-02
"""

import numpy as  np
from collections import defaultdict,Counter
import inversions
import operator

__DEBUG__ = False

class __PrefFreqDist:
	""" 
	An auxiliary class for getLevel1Consensus. 
	Contains a preference-ranking (list), its frequency (int), and its distance from a fixed ranking (int)
	"""
	def __init__(self, pref: tuple, freq: int, dist: int=None):
		self.pref=pref
		self.freq=freq
		self.dist=dist
	def __repr__(self):
		return str(self.pref)+" "+str(self.freq)+" "+str(self.dist)

def getLevel1Consensus(profile: dict, weak: bool=False) -> tuple:
	"""
		Checks whether the given profile exhibits level-1 consensus.
		
		INPUT:
		profile: dict that represents a preference-profile. Maps tuples that represent strict rankings to their frequency in the profile.
		weak:    boolean. True means that the criterion for level-1 consensus is weaker (more lenient). EXPERIMENTAL
		
		OUTPUT: a tuple which represents the ranking around which there is consensus; or None if there is no consensus.

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):2})
		(1, 2, 3)

		>>> getLevel1Consensus({(1,2,3):4, (1,3,2):4, (3,1,2):4, (2,1,3):2, (3,2,1):2})
		(1, 3, 2)

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):1}) is None
		True

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):1}, weak=True)
		(1, 2, 3)

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2}) is None
		True

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2}, weak=True)
		(1, 2, 3)
	"""
	prefsFreqsDists = [__PrefFreqDist(pf[0], pf[1]) for pf in profile.items()]
	prefsFreqsDists.sort(key=operator.attrgetter("freq"), reverse=True)  # sort the rankings from most frequent to least frequent
	maxFreq = prefsFreqsDists[0].freq
	for pfd in prefsFreqsDists:
		if pfd.freq<maxFreq: break
		potentialAxis = pfd.pref    # A preference-relation that is the current candidate for being an axis of a level-1 consensus
		if isCondition1Satisfied(prefsFreqsDists, potentialAxis, weak):
			return potentialAxis
	return None

def isCondition1Satisfied(prefsFreqsDists: list, potentialAxis: tuple, weak: bool=False):
	"""
		Subroutine of getLevel1Consensus.
		check whether the consensus-condition #1 holds for a given preference-relation, potentialAxis.
	"""
	for pfd in prefsFreqsDists:
		pfd.dist = inversions.inversionDistance(pfd.pref, potentialAxis)
	prefsFreqsDists.sort(key=operator.attrgetter("dist"))
	prefsFreqsDists.sort(key=operator.attrgetter("freq"), reverse=True)
	if __DEBUG__: print(prefsFreqsDists)

	# Handle the preference-relations with positive frequencies:
	previous = prefsFreqsDists[0]
	for current in prefsFreqsDists[1:]:
		if previous.freq>current.freq:
			requirement = previous.dist<=current.dist if weak else previous.dist<current.dist
			if not requirement: return False
		previous = current

	# Handle the preference-relations with zero frequencies:
	largestDistanceWithPositiveFrequency = previous.dist
	numOfAlternatives = len(previous.pref)
	if not weak:
		#expectedNumOfDistinctPrefs = inversions.numNPermutationsWithAtMostKInversions(numOfAlternatives,largestDistanceWithPositiveFrequency)
		numOfDistinctPrefs = len(prefsFreqsDists)
		for i in range(largestDistanceWithPositiveFrequency+1):
			numPermutations = inversions.numNPermutationsWithKInversions(numOfAlternatives,i)
			if numPermutations > numOfDistinctPrefs:
				return False
			numOfDistinctPrefs -= numPermutations
	else:
		#expectedNumOfDistinctPrefs = inversions.numNPermutationsWithAtMostKInversions(numOfAlternatives,largestDistanceWithPositiveFrequency-1)
		numOfDistinctPrefs = sum([p.dist<largestDistanceWithPositiveFrequency for p in 	prefsFreqsDists])
		for i in range(largestDistanceWithPositiveFrequency):
			numPermutations = inversions.numNPermutationsWithKInversions(numOfAlternatives,i)
			if numPermutations > numOfDistinctPrefs:
				return False
			numOfDistinctPrefs -= numPermutations
	return numOfDistinctPrefs==0

if __name__ == "__main__":
	__DEBUG__ = False
	import doctest
	doctest.testmod()
	print("Doctest OK!\n")

	__DEBUG__ = True
	
	from preflibtools import io
	profile = io.read_weighted_preflib_file("../../preflibdata/ED-00004-00000001.soc").get_map_from_order_to_weight()
	print("Profile:", profile)
	print("Level-1 consensus:", getLevel1Consensus(profile))
	print("Weak    consensus:", getLevel1Consensus(profile, weak=True))

	profile = io.read_weighted_preflib_file("../../preflibdata/ED-00011-00000001.soc").get_map_from_order_to_weight()
	print("Profile:", profile)
	print("Level-1 consensus:", getLevel1Consensus(profile))
	print("Weak    consensus:", getLevel1Consensus(profile, weak=True))
