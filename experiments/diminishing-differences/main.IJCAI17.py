#!python3

"""
Simulations of item assignment.

Author: Erel Segai-Halevi
Date:   2017-02
"""

import numpy as np
import pandas
from pandas import DataFrame
from pandas.tools import plotting
import matplotlib.pyplot as plt
from datetime import datetime

from Pref import Pref
from itemAssignment import *
from partitions import equalPartitions
import operator
from timeit import default_timer as timer
import sys

np.random.seed(1)

def checkProportional(prefProfile):
	"""
	OUTPUT (bool,bool):  whether an NDDPR allocation exists for the given profile,
	and if it exists, whether it is cardinally fair.
	"""
	sumNecExists = sumNDDExists = sumNDDExistsFair = sumPDDExists = sumPDDExistsFair = sumPosExists  = sumPosExistsFair = 0
	for allocation in equalPartitions(prefProfile.agents, prefProfile.items):
		isNecProp  = isNecessarilyProportional(prefProfile, allocation)
		isCardProp = isCardinallyProportional(prefProfile, allocation)
		isNDDProp  = isNDDProportional(prefProfile, allocation)
		isPDDProp  = isPDDProportional(prefProfile, allocation)
		isPosProp  = isPossiblyProportional(prefProfile, allocation)

		# Sanity checks:
		if isNecProp: assert isNDDProp
		if isNDDProp: assert isPDDProp
		if isPDDProp: assert isPosProp
		if isNecProp: assert isCardProp
		#if isCardProp: assert isPosProp

		# Sums:
		sumNecExists += isNecProp
		sumNDDExists += isNDDProp
		sumNDDExistsFair += (isNDDProp and isCardProp)
		sumPDDExists += isPDDProp
		sumPDDExistsFair += (isPDDProp and isCardProp)
		sumPosExists += isPosProp
		sumPosExistsFair += (isPosProp and isCardProp)

		if isNecProp: break

	allocation = findABCCBAAllocation(prefProfile)
	sumABCCBANecProp  = isNecessarilyProportional(prefProfile, allocation)
	sumABCCBACardProp = isCardinallyProportional(prefProfile, allocation)
	sumABCCBANDDProp  = isNDDProportional(prefProfile, allocation)
	sumABCCBAPDDProp  = isPDDProportional(prefProfile, allocation)
	sumABCCBAPosProp  = isPossiblyProportional(prefProfile, allocation)

	return (sumNecExists>0, \
			sumNDDExists>0, \
			# sumNDDExistsFair/sumNDDExists if sumNDDExists>0 else 0, \
			sumABCCBACardProp if sumNDDExists>0 else 0, \
			sumPDDExists>0, \
			# sumPDDExistsFair/sumPDDExists if sumPDDExists>0 else 0, \
			sumABCCBACardProp if sumPDDExists>0 else 0, \
			sumPosExists>0, \
			#sumPosExistsFair/sumPosExists if sumPosExists>0 else 0, \
			sumABCCBACardProp if sumPosExists>0 else 0, \
			sumABCCBACardProp, \
			prefProfile.countDiminishingDifferences()/prefProfile.agentCount
			)

def calcFractions(agents, items, lowMarketValue, highMarketValue, maxNoiseSize, iterations):
	"""
	Run "iterations" random experiments.
	OUTPUT (float,float): the fraction of times an NDDPR allocation exists,
	and from this, the fraction of times the NDDPR allocation is fair.
	"""
	sums = [0,]*9
	for i in range(iterations):
		prefProfile = PrefProfile.randomCardinal(agents, items, lowMarketValue, highMarketValue, maxNoiseSize)
		sums = map(operator.add, sums, checkProportional(prefProfile))
	return map(lambda x: x/iterations, sums)

def cardinalSimulation(agents, itemCounts, lowMarketValue, highMarketValue, maxNoiseSizeList, iterations, filename):
	results =  DataFrame(columns=('Agents', 'Iterations', 'Noise size', 'Items per agent', 'NecPR exists', 'NDDPR exists', 'NDDPR fair', 'PDDPR exists', 'PDDPR fair', 'PosPR exists', 'PosPR fair', 'ABCCBA fair', 'DD'))
	agentCount = len(agents)
	for maxNoiseSize in maxNoiseSizeList:
		for itemCount in itemCounts:
			if agentCount==3 and itemCount==6: iterations = 50
			start = timer()
			print("noise="+str(maxNoiseSize)+" items="+str(itemCount)+" file="+filename)
			sums = calcFractions(agents, range(itemCount*len(agents)), lowMarketValue, highMarketValue, maxNoiseSize, iterations)
			results.loc[len(results)] = [agentCount, iterations, maxNoiseSize, itemCount] + list(sums)
			results.to_csv("results/"+filename+".csv")
			print(timer() - start)
	return results

def experiments(agents, iterations, filename):
	agentCount = len(agents)

	itemCounts1 = 5 if agentCount==2 else 4
	results1 = cardinalSimulation(
		agents,
		itemCounts = [itemCounts1],
		lowMarketValue=1,
		highMarketValue=2,
		maxNoiseSizeList=[.1,.2,.3,.4,.5,.6,.7,.8,.9,1],
		iterations = iterations,
		filename = filename+"-noise"
		)
	print(results1)

	itemCounts = [2,3,4,5,6,7,8]  if agentCount==2 else [2,3,4,5,6]
	results2 = cardinalSimulation(
		agents,
		itemCounts = itemCounts,
		lowMarketValue=1,
		highMarketValue=2,
		maxNoiseSizeList=[.5],
		iterations = iterations,
		filename = filename+"-items"
		)
	print(results2)

	return (results1, results2)


titleFontSize = 14
legendFontSize = 16
axesFontSize = 16

def plots(results1, results2):
	
	ax = plt.subplot(1, 2, 1)
	agentCount = int(results1['Agents'][0])
	iterations  = int(results1['Iterations'][0])
	itemCounts1  = int(results1['Items per agent'][0])

	results1['NDDPR fair 2'] = results1.apply ( \
		lambda row: row['NDDPR fair']/row['NDDPR exists'], \
		axis=1)

	ax.set_title("probability vs. noise, "+str(agentCount)+' agents, '+str(itemCounts1)+' items per agent',fontsize= titleFontSize, weight='bold')
	ax.set_xlabel('Noise size', fontsize=axesFontSize)

	results1.plot(x='Noise size',y='NDDPR exists', ax=ax, legend=True, style=['go-'], fontsize=axesFontSize)

	results1.plot(x='Noise size',y='NDDPR fair', ax=ax, legend=True, style=['g--'], fontsize=axesFontSize)

	results1.plot(x='Noise size',y='NecPR exists', ax=ax, legend=True, style=['r^-'], fontsize=axesFontSize)

	plt.legend(loc=0,prop={'size':legendFontSize})


	ax = plt.subplot(1, 2, 2, sharey=ax)
	agentCount = int(results2['Agents'][0])
	iterations  = int(results2['Iterations'][0])
	maxNoise  = results2['Noise size'][0]

	results2['NDDPR fair 2'] = results2.apply ( \
		lambda row: row['NDDPR fair']/row['NDDPR exists'], \
		axis=1)

	ax.set_title("probability vs. items, "+str(agentCount)+' agents, |noise|<='+str(maxNoise),fontsize= titleFontSize, weight='bold')
	ax.set_xlabel('Items per agent', fontsize=axesFontSize)

	results2.plot(x='Items per agent',y='NDDPR exists', ax=ax,  legend=True, style=['go-'], fontsize=axesFontSize)

	results2.plot(x='Items per agent',y='NDDPR fair', ax=ax, legend=True, style=['g--'], fontsize=axesFontSize)

	results2.plot(x='Items per agent',y='NecPR exists', ax=ax, legend=True, style=['r^-'], fontsize=axesFontSize)

	itemCounts = results2['Items per agent'].tolist()

	plt.legend(loc=0,prop={'size':legendFontSize})
	plt.xticks(itemCounts)

	plt.show()


if __name__ == "__main__":
	agents = [1,2]
	iterations = 1000
	createResults = False
	if createResults:
		filename = str(datetime.now())
		(results1, results2) = experiments(agents, iterations, filename)
	else:   # Use existing results:
		# filename = "3agents-200iters"
		# filename = "2agents-1000iters"
		filename = "2agents-1000iters-scale"
		results1 = pandas.read_csv("results/"+filename+"-noise.csv")
		results2 = pandas.read_csv("results/"+filename+"-items.csv")
	plots(results1, results2)
