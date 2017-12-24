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
from preflibtools import inversions
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

def getLevel1Consensus(profile: dict, flexible: bool=False) -> tuple:
	"""
		Checks whether the given profile exhibits level-1 consensus.
		
		INPUT:
		profile: dict that represents a preference-profile. Maps tuples that represent strict rankings to their frequency in the profile.
		flexible:    boolean. True means that the criterion for level-1 consensus is weaker (more lenient). EXPERIMENTAL
		
		OUTPUT: a tuple which represents the ranking around which there is consensus; or None if there is no consensus.

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):2})
		(1, 2, 3)

		>>> getLevel1Consensus({(1,2,3):4, (1,3,2):4, (3,1,2):4, (2,1,3):2, (3,2,1):2})
		(1, 3, 2)

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):1}) is None
		True

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2, (2,1,3):1}, flexible=True)
		(1, 2, 3)

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2}) is None
		True

		>>> getLevel1Consensus({(1,2,3):3, (1,3,2):2}, flexible=True)
		(1, 2, 3)
	"""
	prefsFreqsDists = [__PrefFreqDist(pf[0], pf[1]) for pf in profile.items()]
	prefsFreqsDists.sort(key=operator.attrgetter("freq"), reverse=True)  # sort the rankings from most frequent to least frequent
	maxFreq = prefsFreqsDists[0].freq
	for pfd in prefsFreqsDists:
		if pfd.freq<maxFreq: 
			# The current preference-relation, and those below it, cannot be an axis of a level-1 consensus, since their frequency is not maximal.
			break
		else:
			# The current preference-relation is a candidate for being an axis of a level-1 consensus
			potentialAxis = pfd.pref    # A preference-relation that is the current 
			if isCondition1Satisfied(prefsFreqsDists, potentialAxis, flexible):
				return potentialAxis
	return None

def isCondition1Satisfied(prefsFreqsDists: list, potentialAxis: tuple, flexible: bool=False):
	"""
		Subroutine of getLevel1Consensus.
		check whether the condition for level-1 consensus holds for a given preference-relation, potentialAxis.
	"""
	for pfd in prefsFreqsDists:
		pfd.dist = inversions.inversionDistance(pfd.pref, potentialAxis)
		
	# Sort the list of distinct preferences by frequency, then by distance from potentialAxis:
	prefsFreqsDists.sort(key=operator.attrgetter("dist"))  # Sort by the secondary key first...
	prefsFreqsDists.sort(key=operator.attrgetter("freq"), reverse=True)  #.... then by the primary key (sort is stable).
	if __DEBUG__: print(prefsFreqsDists)

	# Handle the preference-relations with positive frequencies:
	previous = prefsFreqsDists[0]
	for current in prefsFreqsDists[1:]:
		if previous.freq>current.freq:
			requirement = previous.dist<=current.dist if flexible else previous.dist<current.dist
			if not requirement: return False
		previous = current

	# Handle the preference-relations with zero frequencies:
	largestDistanceWithPositiveFrequency = previous.dist
	numOfAlternatives = len(previous.pref)
	if not flexible:
		#expectedNumOfDistinctPrefs = inversions.numNPermutationsWithAtMostKInversions(numOfAlternatives,largestDistanceWithPositiveFrequency)
		numOfDistinctPrefs = len(prefsFreqsDists)
		for k in range(largestDistanceWithPositiveFrequency+1):
			numPermutations = inversions.numNPermutationsWithKInversions(numOfAlternatives,k)
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
