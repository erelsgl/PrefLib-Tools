#!python3
"""
Experiments related to finding level-1-consensus in a preference profile.

Author:  Erel Segal-Halevi
Date:    2017-02
"""

import pprint
from preflibtools import consensus, io, generate_profiles
from collections import Counter
import glob
import time

class ConsensusCounter(object):
	def __init__(self, verbose=False):
		self.total = Counter()
		self.consensusExists = Counter()
		self.weakConsensusExists = Counter()
		self.verbose = verbose
		
	def count(self, profile, numalternatives):
		self.total[numalternatives] += 1

		before = time.process_time()
		consensusPref = consensus.getLevel1Consensus(profile)
		if (self.verbose): print("consensus pref: ",consensusPref)
		self.consensusExists[numalternatives] += (consensusPref is not None)
		if (self.verbose): print("time: ",time.process_time()-before)

		before = time.process_time()
		consensusPref = consensus.getLevel1Consensus(profile, weak=True)
		if (self.verbose): print("weak consensus pref: ",consensusPref)
		self.weakConsensusExists[numalternatives] += (consensusPref is not None)
		if (self.verbose): print("time: ",time.process_time()-before)
		
	def show(self, iterations=0):
		print ()
		print ("Total: ", sum(self.total.values()), self.total)
		print ("Consensus: ", sum(self.consensusExists.values()), self.consensusExists)
		print ("WeakConsensus: ", sum(self.weakConsensusExists.values()), self.weakConsensusExists)
		

def preflibDataExperiment():
	print("\nPreflib Data")
	counter = ConsensusCounter(verbose=True)
	for filename in sorted(glob.iglob('../preflibdata/*.soc')):
		profileObject = io.read_weighted_preflib_file(filename)
		profile = profileObject.get_map_from_order_to_weight()
		numalternatives = profileObject.num_of_alternatives()
		print(filename, numalternatives, profile)
		counter.count(profile, numalternatives)
	counter.show(iterations)

def ImpartialCultureExperiment(iterations:int, numvotes:int, numreplace:int, numalternativess:list):
	print("\nImpartial Culture with "+str(numreplace)+" replacements, "+str(numvotes)+" votes")
	counter = ConsensusCounter(verbose=False)
	for numalternatives in numalternativess:
		for i in range(iterations):
			profile = generate_profiles.gen_urn(numvotes, numreplace, range(numalternatives))
			print (".",end='',flush=True)
			#print(numalternatives, profile)
			counter.count(profile, numalternatives)
	counter.show(iterations)

def SinglePeakedExperiment(iterations:int, numvotes:int, numalternativess:list):
	print("\nImpartial-Culture Single-Peaked, "+str(numvotes)+" votes")
	counter = ConsensusCounter(verbose=False)
	for numalternatives in numalternativess:
		for i in range(iterations):
			profile = generate_profiles.gen_icsp(numvotes, range(numalternatives))
			print (".",end='',flush=True)
			# print(numalternatives, profile)
			counter.count(profile, numalternatives)
	counter.show(iterations)

def MallowsExperiment(iterations:int, numvotes:int, phi:float, numalternativess:list):
	print("\nMallows with phi="+str(phi)+", "+str(numvotes)+" votes")
	counter = ConsensusCounter(verbose=False)
	for numalternatives in numalternativess:
		for i in range(iterations):
			alternatives = range(numalternatives)
			profile = generate_profiles.gen_mallows_voteset(numvotes, alternatives, [1], [phi], [alternatives])
			print (".",end='',flush=True)
			# print(numalternatives, profile)
			counter.count(profile, numalternatives)
	counter.show(iterations)

def probabilityOfCondorcetWinner(numvoters):
	"""
	From "The expected probability of Condorcet's paradox", by William V. Gehrlein.
	Economics Letters, Vol. 7, No. 1. (1981), pp. 33-37, doi:10.1016/0165-1765(81)90107-5
	"""
	n = numvoters
	return (15*(n+3)*(n+3))/(16*(n+2)*(n+4))
	
#preflibDataExperiment()
iterations = 1000
for numvotes in [100]:
	ImpartialCultureExperiment(iterations, numvotes, numreplace=0, numalternativess=[3,4])
	SinglePeakedExperiment(iterations, numvotes, numalternativess=[3,4])
	MallowsExperiment(iterations, numvotes, phi=0.5, numalternativess=[3,4])
