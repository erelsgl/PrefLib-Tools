#!python3

from collections import OrderedDict
import numpy as np
import itertools

class Pref(object):
	"""
      Represents the preferences of a single agent over a set of items.
      The preferences can be cardinal (a map from item to value)
      or ordinal (an ordered list of items).

      Author: Erel Segai-Halevi
      Date:   2017-02
	"""

	def __init__(self, ordinal=None, cardinal=None):
		"""
			cardinal: a dictionary that maps items to their values. If it is given, it will also determine the ranking.

			ordinal:  a list of items. Will be used only if 	cardinal is not given.

			>>> p = Pref(cardinal={100: 6.2, 200: 1.3, 300: 3.4})
			>>> p
			cardinal=100:6.2 300:3.4 200:1.3 ordinal=100>300>200
			>>> p.borda
			{200: 1, 300: 2, 100: 3}
		"""
		if cardinal:
			# Sort items by decreasing value:
			self.cardinal = OrderedDict(sorted(cardinal.items(), key=lambda item: item[1], reverse=True))

			# Determine the implied item-ranking:
			self.ordinal = [item[0] for item in self.cardinal.items()]
		else:
			self.cardinal = None
			self.ordinal = ordinal

		itemCount = len(self.ordinal)
		self.borda = {self.ordinal[i]:(itemCount-i) for i in range(itemCount)}

	def __repr__(self):
		repr = ""
		if self.cardinal is not None:
			repr += "cardinal=" + " ".join([str(item[0])+":"+str(item[1]) for item in self.cardinal.items()])
		if self.ordinal is not None:
			repr += " ordinal="+">".join([str(item) for item in self.ordinal])
		return repr

	def bestItem(self):
		return self.ordinal[0]

	def removeItem(self, item):
		if item in self.ordinal:
			self.ordinal.remove(item)
			if self.cardinal is not None:
				del self.cardinal[item]
		else:
			raise ValueError("Item "+str(item)+" not found in Pref("+self.__repr__()+")")


	def valueOf(self, bundle):
		"""
			return the sum of values of the items in the given bundle.

			>>> p = Pref(cardinal={1: 6.2, 2: 1.3, 3: 3.4})
			>>> p.valueOf([1,2])
			7.5
		"""
		if self.cardinal is None:
			raise ValueError("Cannot evaluate items since I have no cardinal-value information")
		return sum([self.cardinal[item] for item in bundle])

	def bordasOf(self, bundle):
		"""
			return a list of the Borda scores of the items in the given bundle, in decreasing order.
		"""
		return sorted([self.borda[item] for item in bundle], reverse=True)

	def isDiminishingDifferences(self):
		"""
			return true if the cardinal utilities satisfy the DD condition:
			the differences between subsequent items are decreasing from top to bottom items.

			>>> p = Pref(cardinal={1: 6.2, 2: 1.3, 3: 3.4})
			>>> p.isDiminishingDifferences()
			True

			>>> p = Pref(cardinal={1: 6.2, 2: 0.3, 3: 3.4})
			>>> p.isDiminishingDifferences()
			False
		"""
		cardinal = list(self.cardinal.values())
		diffs = np.diff(cardinal)
		diffsdiffs = np.diff(diffs)
		return True if np.all(diffsdiffs >= 0) else False



	def isNecessarilyWeaklyBetter(self, bundle1, bundle2):
		"""
		INPUT:
		bundle1, bundle2: lists of items.

		OUTPUT:
		True iff bundle1 >= bundle2 necessarily, based on self.ordinal.

		>>> pref = Pref(ordinal=[6,5,4,3,2,1])
		>>> pref.isNecessarilyWeaklyBetter([6,4,2],[5,3,1])
		True
		>>> pref.isNecessarilyWeaklyBetter([6,4,1],[5,3,2])
		False
		>>> pref.isNecessarilyWeaklyBetter([5,4,3],[6,2,1])
		False
		>>> pref.isNecessarilyWeaklyBetter([5,4,2],[5,4,2])
		True
		"""
		if len(bundle1) < len(bundle2):
			return False
		bundle1Bordas = self.bordasOf(bundle1)
		bundle2Bordas = self.bordasOf(bundle2)
		for i in range(len(bundle2Bordas)):
			if bundle1Bordas[i] < bundle2Bordas[i]:
				return False
		return True

	def isNDDWeaklyBetter(self, bundle1, bundle2):
		"""
		INPUT:
		bundle1, bundle2: lists of items.

		OUTPUT:
		True iff bundle1 >= bundle2 necessarily, based on self.ordinal and the Diminishing Differences assumption.

		>>> pref = Pref(ordinal=[6,5,4,3,2,1])
		>>> pref.isNDDWeaklyBetter([6,4,2],[5,3,1])
		True
		>>> pref.isNDDWeaklyBetter([6,4,1],[5,3,2])
		True
		>>> pref.isNDDWeaklyBetter([5,4,3],[6,2,1])
		False
		>>> pref.isNDDWeaklyBetter([5,4,2],[5,4,2])
		True
		"""
		if len(bundle1) < len(bundle2):
			return False
		bundle1Bordas = self.bordasOf(bundle1)
		bundle2Bordas = self.bordasOf(bundle2)
		bundle1Bordas = list(itertools.accumulate(bundle1Bordas))
		bundle2Bordas = list(itertools.accumulate(bundle2Bordas))
		for i in range(len(bundle2Bordas)):
			if bundle1Bordas[i] < bundle2Bordas[i]:
				return False
		return True

	def isPossiblyWeaklyBetter(self, bundle1, bundle2):
		"""
		INPUT:
		bundle1, bundle2: lists of items.

		OUTPUT:
		True iff bundle1 >= bundle2 possibly, based on self.ordinal.

		>>> pref = Pref(ordinal=[6,5,4,3,2,1])
		>>> pref.isPossiblyWeaklyBetter([6,4,1],[5,3,2])
		True
		>>> pref.isPossiblyWeaklyBetter([5,4,3],[6,2,1])
		True
		>>> pref.isNecessarilyWeaklyBetter([5,4,2],[5,4,2])
		True
		>>> pref.isPossiblyWeaklyBetter([5,3,1],[5,3,2])
		False
		"""
		if len(bundle1) > len(bundle2):
			return True
		bundle1Bordas = self.bordasOf(bundle1)
		bundle2Bordas = self.bordasOf(bundle2)
		default = True
		for i in range(len(bundle1Bordas)):
			if bundle1Bordas[i] > bundle2Bordas[i]:
				return True
			if bundle1Bordas[i] < bundle2Bordas[i]:
				default = False
		return default

	def isPDDWeaklyBetter(self, bundle1, bundle2):
		"""
		INPUT:
		bundle1, bundle2: lists of items.

		OUTPUT:
		True iff bundle1 >= bundle2 possibly, based on self.ordinal.

		>>> pref = Pref(ordinal=[6,5,4,3,2,1])
		>>> pref.isPossiblyWeaklyBetter([6,4,1],[5,3,2])
		True
		>>> pref.isPossiblyWeaklyBetter([5,4,3],[6,2,1])
		True
		>>> pref.isNecessarilyWeaklyBetter([5,4,2],[5,4,2])
		True
		>>> pref.isPossiblyWeaklyBetter([5,3,1],[5,3,2])
		False
		"""
		if len(bundle1) > len(bundle2):
			return True
		bundle1Bordas = self.bordasOf(bundle1)
		bundle2Bordas = self.bordasOf(bundle2)
		bundle1Bordas = list(itertools.accumulate(bundle1Bordas))
		bundle2Bordas = list(itertools.accumulate(bundle2Bordas))
		default = True
		for i in range(len(bundle1Bordas)):
			if bundle1Bordas[i] > bundle2Bordas[i]:
				return True
			if bundle1Bordas[i] < bundle2Bordas[i]:
				default = False
		return default


	@staticmethod
	def randomOrdinal(items):
		return Pref(ordinal = list(np.random.permutation(items)))

	@staticmethod
	def randomCardinal(marketValues, maxNoiseSize):
		"""
		marketValues: a dictionary that maps each item to its "market value".

		maxNoiseSize: a number that represents the maximum difference between the market value and the agent's value.

		The agent's cardinal values for each item will be selected by adding a random noise in [-maxNoiseSize,maxNoiseSize] to the market value of the item.
		"""
		cardinal = {}
		for item in marketValues.items():
			agentValue = item[1] + np.random.uniform(-maxNoiseSize, maxNoiseSize)
			cardinal[item[0]] = agentValue
		return Pref(cardinal=cardinal)

	@staticmethod
	def randomCardinalGaussian(marketValues, stddev):
		"""
		marketValues: a dictionary that maps each item to its "market value".

		stddev: standard deviation of the distribution.

		The agent's cardinal values for each item will be selected by adding a random noise distributed like Normal(0,stddev) to the market value of the item.
		"""
		cardinal = {}
		for item in marketValues.items():
			agentValue = np.random.normal(item[1], stddev)
			cardinal[item[0]] = agentValue
		return Pref(cardinal=cardinal)


if __name__ == "__main__":
	import doctest
	print(doctest.testmod())

	print ("random ",Pref.randomOrdinal([1,2,3,4,5]))
	np.random.seed()
	print ("random ",Pref.randomCardinal({1:6, 2:2, 3:5}, 0.5))
	np.random.seed(1)
	print ("random gaussian ",Pref.randomCardinalGaussian({1:600, 2:400, 3:500}, 200))
