#!python3
"""
Experiments related to finding level-1-consensus in a preference profile.

Author:  Erel Segal-Halevi
Date:    2017-02
"""

import pprint, glob, time, datetime, sys
sys.path.append("../../preflibtools")

from preflibtools import consensus, io, generate_profiles, domain_restriction
from collections import Counter
import pandas
from pandas import DataFrame
from pandas.tools import plotting
import matplotlib.pyplot as plt
from datetime import datetime

class ConsensusCounter(object):
	def __init__(self, verbose=False):
		self.total = Counter()
		self.consensusExists = Counter()
		self.weakConsensusExists = Counter()
		self.singlePeaked = Counter()
		self.verbose = verbose
		
	def count(self, profile, numalternatives):
		self.total[numalternatives] += 1

		before = time.process_time()
		consensusPref = consensus.getLevel1Consensus(profile)
		if (self.verbose): print("consensus pref: ",consensusPref)
		self.consensusExists[numalternatives] += (consensusPref is not None)
		if (self.verbose): print("time: ",time.process_time()-before)

		before = time.process_time()
		consensusPref = consensus.getLevel1Consensus(profile, flexible=True)
		if (self.verbose): print("flexible consensus pref: ",consensusPref)
		self.weakConsensusExists[numalternatives] += (consensusPref is not None)
		if (self.verbose): print("time: ",time.process_time()-before)
		
		socialAxis = domain_restriction.is_single_peaked_orders(map(list,profile.keys()))
		self.singlePeaked[numalternatives] += (len(socialAxis)>0)
		
	def getTotal(self): return sum(self.total.values())
	def getConsensusExists(self): return sum(self.consensusExists.values())
	def getWeakConsensusExists(self): return sum(self.weakConsensusExists.values())
	def getSinglePeaked(self): return sum(self.singlePeaked.values())

	def show(self):
		print ()
		print ("Total: ", sum(self.total.values()), self.total)
		print ("Consensus: ", sum(self.consensusExists.values()), self.consensusExists)
		print ("WeakConsensus: ", sum(self.weakConsensusExists.values()), self.weakConsensusExists)
		print ("SinglePeaked: ", sum(self.singlePeaked.values()), self.weakConsensusExists)
		

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
			counter.count(profile, numalternatives)
	counter.show()

def SinglePeakedExperiment(iterations:int, numvotes:int, numalternativess:list):
	print("\nImpartial-Culture Single-Peaked, "+str(numvotes)+" votes")
	counter = ConsensusCounter(verbose=False)
	for numalternatives in numalternativess:
		for i in range(iterations):
			profile = generate_profiles.gen_icsp(numvotes, range(numalternatives))
			print (".",end='',flush=True)
			counter.count(profile, numalternatives)
	counter.show()

def MallowsExperiment(iterations:int, numvotess:int, phis:float, numalternativess:list, filename:str):
	results =  DataFrame(columns=('iterations', 'numvotes', 'phi', 'numalternatives', 'Level-1 Consensus', 'Flexible Consensus', 'Single-peaked'))
	
	for numalternatives in numalternativess:
		alternatives = range(numalternatives)
		for numvotes in numvotess:
			for phi in phis:
				print("\nMallows with phi="+str(phi)+", numvotes="+str(numvotes)+", numalternative="+str(numalternatives)+", filename="+filename)
				counter = ConsensusCounter(verbose=False)
				for i in range(iterations):
					profile = generate_profiles.gen_mallows_voteset(numvotes, alternatives, [1], [phi], [alternatives])
					print (".",end='',flush=True)
					# print(numalternatives, profile)
					counter.count(profile, numalternatives)
				counter.show()
				results.loc[len(results)] = [iterations, numvotes, phi, numalternatives, counter.getConsensusExists(), counter.getWeakConsensusExists(), counter.getSinglePeaked()]
				results.to_csv("results/"+filename+".csv")

def probabilityOfCondorcetWinner(numvoters:int) -> float:
	"""
	From "The expected probability of Condorcet's paradox", by William V. Gehrlein.
	Economics Letters, Vol. 7, No. 1. (1981), pp. 33-37, doi:10.1016/0165-1765(81)90107-5
	"""
	n = numvoters
	return (15*(n+3)*(n+3))/(16*(n+2)*(n+4))


def plot_prob_vs_phi(results: DataFrame, ax, numvotes:int, numalternatives:int, legend:bool):
	#ax.set_title("probability vs. phi, "+str(numvotes)+' voters, '+str(numalternatives)+' alternatives',fontsize= 10, weight='bold')
	ax.set_title(str(numvotes)+' voters, '+str(numalternatives)+' alternatives',fontsize= 15, weight='bold')
	results1 = results.query("numvotes=="+str(numvotes)+" and numalternatives=="+str(numalternatives))

	results1.plot(x='phi', y='Flexible Consensus %', ax=ax, legend=legend, style=['go-'])
	results1.plot(x='phi', y='Single-peaked %', ax=ax, legend=legend, style=['b--'])
	results1.plot(x='phi', y='Level-1 Consensus %', ax=ax, legend=legend, style=['r^-'])
	ax.set_xlabel('phi', fontsize=15)
	ax.set_ylabel('% exists', fontsize=15)


def plots(results: DataFrame):
	results['Level-1 Consensus %'] = results.apply ( \
		lambda row: 100*row['Level-1 Consensus']/row['iterations'], \
		axis=1)
	results['Flexible Consensus %'] = results.apply ( \
		lambda row: 100*row['Flexible Consensus']/row['iterations'], \
		axis=1)
	results['Single-peaked %'] = results.apply ( \
		lambda row: 100*row['Single-peaked']/row['iterations'], \
		axis=1)

	plt.subplots(2, 3, sharex=True)

	plot_prob_vs_phi(results, plt.subplot(2, 3, 1), numvotes=100, numalternatives=3, legend=False)
	plot_prob_vs_phi(results, plt.subplot(2, 3, 4), numvotes=1000, numalternatives=3, legend=False)
	plot_prob_vs_phi(results, plt.subplot(2, 3, 2), numvotes=100, numalternatives=4, legend=False)
	plot_prob_vs_phi(results, plt.subplot(2, 3, 5), numvotes=1000, numalternatives=4, legend=False)
	plot_prob_vs_phi(results, plt.subplot(2, 3, 3), numvotes=100, numalternatives=5, legend=False)
	plot_prob_vs_phi(results, plt.subplot(2, 3, 6), numvotes=1000, numalternatives=5, legend=True)
	plt.legend(loc=0,prop={'size':15})
	
	for i in range(1,7):
		plt.subplot(2, 3, i).tick_params(axis='both', which='major', labelsize=15)
	for i in [1,2,3]:
		plt.subplot(2, 3, i).get_xaxis().set_visible(False)
	for i in [2,3,5,6]:
		plt.subplot(2, 3, i).get_yaxis().set_visible(False)

	#ax = plt.subplot(1, 2, 2, sharey=ax)

	plt.show()


#################  MAIN  ###################

createResults = True
if createResults:
	#preflibDataExperiment()
	iterations = 1000
	#ImpartialCultureExperiment(iterations, numvotes, numreplace=0, numalternativess=[3,4])
	#SinglePeakedExperiment(iterations, numvotes, numalternativess=[3,4])
	filename = "mallows_"+str(datetime.now()); 	  MallowsExperiment(iterations, numvotess=[100,200,300,400,500,600,700,800,900,1000], phis=[0,.05,.1,.15,.2,.25,.3,.4,.5,.6,.7,.8,.9,1.0], numalternativess=[3,4,5], filename=filename)
else:   # Use existing results:
	filename = "mallows_1000iters"
	
results = pandas.read_csv("results/"+filename+".csv")
impartial3 = results[results["phi"]==1][results["numalternatives"]==3]
impartial3.to_csv("results/mallows_1000iters_impartial3.csv")
plots(results)
