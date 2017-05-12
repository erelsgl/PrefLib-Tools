#!python3
import numpy as  np
from Pref import Pref

class PrefProfile(object):
	"""
      Represents a profile of preferences (Pref objects) of several agents.

      Author: Erel Segai-Halevi
      Date:   2017-02
	"""

	def __init__(self, agentsToPrefs):
		"""
			agentsToPrefs: a dictionary that maps agents to Pref objects.
		"""
		self.agentsToPrefs = agentsToPrefs
		self.prefs = list(agentsToPrefs.values())
		self.agents = sorted(agentsToPrefs.keys())
		self.items = sorted(next(iter(self.prefs)).ordinal)
		self.itemCount = len(self.items)
		self.agentCount = len(self.agents)
		if self.itemCount<1:
			raise ValueError("no items")
		if self.agentCount<1:
			raise ValueError("no agents")

	def __repr__(self):
		return self.prefs.__repr__()

	def removeItem(self, item):
		if item in self.items:
			self.items.remove(item)
			for pref in self.prefs:
				pref.removeItem(item)
			self.itemCount -= 1
		else:
			raise ValueError("item "+str(item)+" not found")

	def countDiminishingDifferences(self):
		"""
			count the number of profiles with the DD property
		"""
		return sum(map(Pref.isDiminishingDifferences, self.prefs))

	@staticmethod
	def randomCardinal(agents, items, lowMarketValue,highMarketValue,maxNoiseSize):
		marketValues = {
			item: np.random.uniform(lowMarketValue,highMarketValue)
			for item in items
			}
		return PrefProfile({agent:Pref.randomCardinal(marketValues, maxNoiseSize) for agent in agents})


	@staticmethod
	def randomCardinalGaussian(agents, items, lowMarketValue,highMarketValue,stddev):
		marketValues = {
			item: np.random.uniform(lowMarketValue,highMarketValue)
			for item in items
			}
		return PrefProfile({agent:Pref.randomCardinalGaussian(marketValues, stddev) for agent in agents})


if __name__ == "__main__":
	import doctest
	doctest.testmod()

	prof1 = PrefProfile.randomCardinal(["A","B","C"], [1,2,3], 500, 1000, 100)
	print(prof1)
	print (prof1.countDiminishingDifferences())
	prof2 = PrefProfile.randomCardinalGaussian(["A","B","C"], [1,2,3], 500, 1000, 100)
	print(prof2)
	print(prof2.countDiminishingDifferences())
