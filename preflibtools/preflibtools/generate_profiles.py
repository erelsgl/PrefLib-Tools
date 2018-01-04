#!python3
'''
  File:   generate_profiles.py
  Author:  Nicholas Mattei (nicholas.mattei@nicta.com.au)
  Date:  Sept 11, 2013
      November 6th, 2013

  * Copyright (c) 2014, Nicholas Mattei and NICTA
  * All rights reserved.
  *
  * Developed by: Nicholas Mattei
  *               NICTA
  *               http://www.nickmattei.net
  *               http://www.preflib.org
  *
  * Redistribution and use in source and binary forms, with or without
  * modification, are permitted provided that the following conditions are met:
  *     * Redistributions of source code must retain the above copyright
  *       notice, this list of conditions and the following disclaimer.
  *     * Redistributions in binary form must reproduce the above copyright
  *       notice, this list of conditions and the following disclaimer in the
  *       documentation and/or other materials provided with the distribution.
  *     * Neither the name of NICTA nor the
  *       names of its contributors may be used to endorse or promote products
  *       derived from this software without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY NICTA ''AS IS'' AND ANY
  * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL NICTA BE LIABLE FOR ANY
  * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
  * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


About
--------------------
  This file generates voting profiles according to a given distribution.
  
  Available distributions are:
  
  * Impartial Culture --- gen_impartial_culture_strict, gen_urn
  * Impartial Anonymous Culture --- gen_impartial_aynonmous_culture_strict, gen_urn
  * Urn Culture with Replacement --- gen_urn_culture_strict, gen_urn_strict, gen_urn
  * Single-Peaked Impartial Culture --- gen_single_peaked_impartial_culture_strict, gen_icsp
  * Mallows       --- gen_mallows
  * Mallows mix   --- gen_mallows_mix
  
  

'''
import random
import itertools
import math
import copy
import argparse
import sys
import numpy as np

from preflibtools import io

# Refactored Generator Functions.



# Generator Functions

# Generate a generically labeled candidate map from
# a number of alternatives.
def gen_cand_map(nalts):
  """
  INPUT: nalts: int, number of alternatives (candidates).
  
  OUTPUT: dict, maps candidate id to candidate name.
  
  >>> gen_cand_map(3)
  {1: 'Candidate 1', 2: 'Candidate 2', 3: 'Candidate 3'}
  """
  candmap = {}
  for i in range(1, nalts+1):
    candmap[i] = "Candidate " + str(i)
  return candmap

# Generate an Impartial Culture profile
# that adheres to the format above given a candidate map.
def gen_impartial_culture_strict(numvotes, candmap):
  """
  INPUT: 
  * numvotes - int,   total number of voters.
  * candmap  - dict,  maps candidate code to candidate name (actually, only the list of candidate codes is used)
  
  OUTPUT:
  * rmaps - list, contains len(votemap) maps, each map represents a ranking (maps a candidate-id to the candidate-rank).
  * rmapscounts - list, contains len(votemap) ints, each int represents the number of voters that support the corresponding ranking. 
  
  >>> (rmaps,rmapscounts) = gen_impartial_culture_strict(100, {1:"Alice",2:"Bob",3:"Carl"})
  >>> len(rmaps)    # should be 3! - number of possible rankings.
  6
  >>> len(rmapscounts)
  6
  """
  voteset = gen_urn(numvotes, numreplace=0, alternatives=candmap.keys())
  return voteset_to_rankmap(voteset)

# Generate an Impartial Anonymous Culture profile
# that adheres to the format above.
def gen_impartial_aynonmous_culture_strict(numvotes, candmap):
  voteset = gen_urn(numvotes, numreplace=1, alternatives=candmap.keys())
  return voteset_to_rankmap(voteset)

# Generate an Urn Culture with Replacement = replace profile
# that adheres to the format above.
def gen_urn_culture_strict(numvotes, numreplace, candmap):
  voteset = gen_urn(numvotes, numreplace, candmap.keys())
  return voteset_to_rankmap(voteset)

# Generate an SinglePeakedImpartialCulture vote set.
def gen_single_peaked_impartial_culture_strict(numvotes, candmap):
  voteset = gen_icsp(numvotes, list(candmap.keys()))
  return voteset_to_rankmap(voteset)

# Generate strict Urn
# Identical to gen_urn_culture_strict
def gen_urn_strict(numvotes, numreplace, candmap):
  voteset = gen_urn(numvotes, numreplace, candmap.keys())
  return voteset_to_rankmap(voteset)


# Generate Mallows with a particular number of reference rankings and phi's drawn iid.
def gen_mallows_mix(numvotes, candmap, nref):
  """
  INPUT:
  numvotes - int, number of votes to generate.
  candmap - dict, maps candidate id to candidate name.
  nref    - int number of reference-rankings.
  
  >>> (rmap,rmapcount) = gen_mallows_mix(100, {1:"Alice",2:"Bob",3:"Carl"}, 1)
  >>> len(rmap)    # should be 3! - number of possible rankings.
  6
  >>> len(rmapcount)
  6
  """
  #Generate the requisite number of reference rankings and phis
  #Mix should be a random number over each...
  mix = []
  phis = []
  refs = []
  for i in range(nref):
    refm, refc = gen_impartial_culture_strict(1, candmap);
    refs.append(io.rankmap_to_order(refm[0]))
    phis.append(round(random.random(), 5))
    mix.append(random.randint(1,100))
  # Normalize mix to 1:
  smix = sum(mix)
  mix = [float(i) / float(smix) for i in mix]  
  return gen_mallows(numvotes, candmap, mix, phis, refs)

  
def gen_mallows(numvotes, candmap, mix, phis, refs):
  """
  INPUT:
  numvotes - int, number of votes to generate.
  candmap - dict, maps candidate id to candidate name.
  mix     - list of float, summing to 1. Probability distribution over Mallows models with different references.
  phis    - list of float, parameter of Mallows function for each reference.
  refs    - list of lists, the reference ("correct") rankings.
  
  OUTPUT:
  rmap, rmapcount - represent a preference profile.
 
  >>> rmap,rmapcount = gen_mallows(1000, {1:"Alice",2:"Bob",3:"Carl"}, [1.0], [0.5], [[1,2,3]])
  >>> len(rmap)    # should be 3! - number of possible rankings.
  6
  >>> len(rmapcount)
  6
  """
  voteset = gen_mallows_voteset(numvotes, list(candmap.keys()), mix, phis, refs)
  return voteset_to_rankmap(voteset, candmap)


def gen_mallows_voteset(numvotes, alternatives, mix, phis, refs):
  """
  INPUT:
  numvotes - int, number of votes to generate.
  alternatives - list of alternatives.
  mix     - list of float, summing to 1. Probability distribution over Mallows models with different references.
  phis    - list of float, parameter of Mallows function for each reference.
  refs    - list of lists, the reference ("correct") rankings.
  
  OUTPUT:  dict, represents a profile, maps preferences (tuples) to their frequency in the profile.
  
  >>> voteset = gen_mallows_voteset(100, {1:"Alice",2:"Bob",3:"Carl"}, [1.0], [0.5], [[1,2,3]])
  >>> len(voteset)    # should be 3! - number of possible rankings.
  6
  """
  numrefs = len(refs)
  if len(mix) != numrefs or len(phis) != numrefs:
    raise ValueError("mix, phis and refs must be lists of the same length")

  #Precompute the distros for each Phi and Ref.
  #Turn each ref into an order for ease of use...
  m_insert_dists = []
  for i in range(numrefs):
    m_insert_dists.append(compute_mallows_insertvec_dist(len(alternatives), phis[i]))
    
  #print("m_insert_dists",m_insert_dists)

  #Now, generate votes...
  votemap = {}
  for cvoter in range(numvotes):
    #print("drawing")
    cmodel = draw(range(numrefs), mix)
    #print("cmodel", cmodel)
    ref = refs[cmodel]
    #print("ref", ref)
    insertvec_dist = m_insert_dists[cmodel]   # the probabilities of Mallows model. A dict from int to discrete probability distribution.
    
    #Generate a vote for the selected model
    insvec = [0] * len(alternatives)
    for i in range(1, len(insvec)+1):
      options = list(range(1, i+1))
      #options are 1...max
      #print("Options: " + str(options))
      #print("Dist: " + str(insertvec_dist[i]))
      #print("Drawing on model " + str(cmodel))
      insvec[i-1] = draw(options, insertvec_dist[i])
    #print("insvec",insvec)
    vote = []
    for i in range(len(ref)):
      vote.insert(insvec[i]-1, ref[i])
    #print("mallows vote: " + str(vote))
    tvote = tuple(vote)
    votemap[tvote] = votemap.get(tvote, 0) + 1
  return votemap


#  Helper Functions -- Actual Generators -- Don't call these directly.

# Return a value drawn from a particular distribution.
def draw(values, distro):
  #Return a value randomly from a given discrete distribution.
  #This is a bit hacked together -- only need that the distribution
  #sums to 1.0 within 5 digits of rounding.
  if round(sum(distro),5) != 1.0:
    raise ValueError("Input Distro is not a Distro...\n"+str(distro) + "  Sum: " + str(sum(distro)))
  if len(distro) != len(values):
    raise ValueError("Values and Distro have different length")

  cv = 0
  draw = random.random() - distro[cv]
  while draw > 0.0:
    cv+= 1
    draw -= distro[cv]
  return values[cv]
  
  
# For Phi and a given number of candidates, compute the
# insertion probability vectors.
def compute_mallows_insertvec_dist(ncand:int, phi:float) -> dict:
  """
  INPUT:
  ncand - int, number of candidates (alternativcs).
  phi   - float, parameter of the Mallows distribution.
  
  OUTPUT: dict, maps int to discrete probability distribution (a list of floats whose sum is 1)
  
  >>> compute_mallows_insertvec_dist(3, 1)
  {1: [1.0], 2: [0.5, 0.5], 3: [0.3333333333333333, 0.3333333333333333, 0.3333333333333333]}
  >>> compute_mallows_insertvec_dist(3, 0.5)
  {1: [1.0], 2: [0.3333333333333333, 0.6666666666666666], 3: [0.14285714285714285, 0.2857142857142857, 0.5714285714285714]}
  >>> compute_mallows_insertvec_dist(3, 1/3)
  {1: [1.0], 2: [0.25, 0.75], 3: [0.07692307692307691, 0.23076923076923075, 0.6923076923076923]}
  >>> compute_mallows_insertvec_dist(3, 0)
  {1: [1.0], 2: [0.0, 1.0], 3: [0.0, 0.0, 1.0]}
  >>> compute_mallows_insertvec_dist(4, 0.5)
  {1: [1.0], 2: [0.3333333333333333, 0.6666666666666666], 3: [0.14285714285714285, 0.2857142857142857, 0.5714285714285714], 4: [0.06666666666666667, 0.13333333333333333, 0.26666666666666666, 0.5333333333333333]}
  >>> compute_mallows_insertvec_dist(4, 1/3)
  {1: [1.0], 2: [0.25, 0.75], 3: [0.07692307692307691, 0.23076923076923075, 0.6923076923076923], 4: [0.024999999999999994, 0.075, 0.225, 0.675]}
  """
  #Compute the Various Mallows Probability Distros
  vec_dist = {}
  for i in range(1, ncand+1):
    #Start with an empty distro of length i
    dist = [0] * i
    #compute the denom = phi^0 + phi^1 + ... phi^(i-1)
    denom = sum([pow(phi,k) for k in range(i)])
    #Fill each element of the distro with phi^i-j / denom
    for j in range(1, i+1):
      dist[j-1] = pow(phi, i - j) / denom
    #print(str(dist) + "total: " + str(sum(dist)))
    vec_dist[i] = dist
  return vec_dist
  

# Convert a votemap to a rankmap and rankmapcounts....
def voteset_to_rankmap(votemap, candmap=None):
  """
  INPUT:
  * votemap - dict, maps tuples (representing strict rankings) to ints (representing num-of-occurences).
  * candmap - dict, maps candidate ids to candidate names. This parameter is currently not used.
  
  OUTPUT:
  * rmap - list, contains len(votemap) maps, each map represents a ranking (maps a rank to the candidate at that rank).
  * rmapcount - list, contains len(votemap) ints, each int represents the number of voters that support the corresponding rank. 
  
  >>> voteset_to_rankmap(votemap={(1,2,3):100, (2,1,3):150, (3,1,2):200})
  ([{1: 2, 2: 1, 3: 3}, {1: 2, 2: 3, 3: 1}, {1: 1, 2: 2, 3: 3}], [150, 200, 100])
  """
  rmapcount =[]
  rmap = []
  #Votemaps are tuple --> count, so it's strict and easy...
  for order in votemap.keys():
    rmapcount.append(votemap[order])
    cmap = {}
    for crank in range(1, len(order)+1):
      cmap[order[crank-1]] = crank
    rmap.append(cmap)
  return rmap, rmapcount
  
# Given a rankmap and counts, return a voteset for writing.
def rankmap_to_voteset(rankmaps, rankmapcounts):
  #convert these
  votemap = {}
  for n in range(len(rankmaps)):
    cmap = rankmaps[n]
    #Decompose the rankmap into a string.
    #Get number of elements
    lenrank = max(cmap.values())
    strlist = ['']*lenrank
    #place the candidates in their buckets
    for i in sorted(cmap.keys()):
      strlist[cmap[i]-1] += str(i) + ","
    #Strip off unecessary commas.
    strlist = [i[:len(i)-1] for i in strlist]
    #Make the correct string.
    votestr = ""
    for i in strlist:
      if i.find(",") == -1:
        votestr += i + ","
      else:
        votestr += "{" + i + "},"
    #Trim
    votestr = votestr[:len(votestr)-1].strip()
    #insert into the map.
    votemap[votestr] = votemap.get(votestr, 0) + rankmapcounts[n]
  return votemap

# Return a Tuple for an Impartial-Culture-Single-Peaked... with alternatives in range 1....range.
def gen_icsp_single_vote(alternatives):
  a = 0
  b = len(alternatives)-1
  temp = []
  while a != b:
    if random.randint(0,1) == 1:
      temp.append(alternatives[a])
      a += 1
    else:
      temp.append(alternatives[b])
      b -= 1
  temp.append(alternatives[a])
  return tuple(temp[::-1]) # reverse


def gen_icsp(numvotes, alternatives):
  """
  Generate single-peaked votes based on Impartial-Culture assumption.

  INPUT:
  * numvotes -         int, total number of voters.
  * alternatives  -    list, codes of alternatives (aka candidates)
  
  OUTPUT:
  * voteMap - dict from tuples to ints: maps tuples that represent rankings, to the number of times it appears in the profile.
  
  >>> voteMap = gen_urn(200, 0, [10,20,30])
  >>> len(voteMap)   # should be 3! = num of different strict rankings.
  6
  >>> type(voteMap)
  <class 'dict'>
  >>> voteMap[(10,20,30)] > 0
  True
  >>> voteMap[(30,20,10)] > 0
  True
  """
  voteset = {}
  for i in range(numvotes):
    tvote = gen_icsp_single_vote(alternatives)  # returns a tuple representing a rank
    voteset[tvote] = voteset.get(tvote, 0) + 1
  return voteset

# Generate votes based on the URN Model.
# we need numvotes votes with numreplace replacements.
def gen_urn(numvotes, numreplace, alternatives):
  """
  Generate votes based on the URN Model.

  INPUT:
  * numvotes -         int, total number of voters.
  * numreplace -       int, number of replacements (???)
  * alternatives  -    list, codes of alternatives (aka candidates)
  
  OUTPUT:
  * voteMap - dict from tuples to ints: maps tuples that represent rankings, to the number of times it appears in the profile.
  
  >>> voteMap = gen_urn(200, 0, [10,20,30])
  >>> len(voteMap)   # should be 3! = num of different strict rankings.
  6
  >>> type(voteMap)
  <class 'dict'>
  >>> voteMap[(10,20,30)] > 0
  True
  >>> voteMap[(30,20,10)] > 0
  True
  """
  voteMap = {}
  ReplaceVotes = {}

  numranks = math.factorial(len(alternatives))
  alternatives = list(alternatives)
  ReplaceSize = 0

  for x in range(numvotes):
    flip = random.randint(1, numranks+ReplaceSize)
    if flip <= numranks:
      #generate an impartial-culture vote and make a suitable number of replacements...
      tvote = tuple(np.random.permutation(alternatives))
      voteMap[tvote] = (voteMap.get(tvote, 0) + 1)
      ReplaceVotes[tvote] = (ReplaceVotes.get(tvote, 0) + numreplace)
      ReplaceSize += numreplace

    else:
      #iterate over replacement hash and select proper vote.
      flip = flip - numranks
      for vote in ReplaceVotes.keys():
        flip = flip - ReplaceVotes[vote]
        if flip <= 0:
          voteMap[vote] = (voteMap.get(vote, 0) + 1)
          ReplaceVotes[vote] = (ReplaceVotes.get(vote, 0) + numreplace)
          ReplaceSize += numreplace
          break
      else:
        raise RuntimeError("We Have a problem... replace fell through....")

  return voteMap

# Return an impartial-culture vote as a tuple which represents a strict ranking.
def gen_ic_vote(alternatives):
  return tuple(np.random.permutation(list(alternatives)))
#  options = list(alternatives)
#  vote = []
#  while(len(options) > 0):
#    #randomly select an option
#    vote.append(options.pop(random.randint(0,len(options)-1)))  # random.randint(a,b) Return a random integer N such that a <= N <= b
#  return tuple(vote)


# Below is a template Main which shows off some of the
# features of this library.
if __name__ == '__main__':
  import doctest
  doctest.testmod()
  print("Doctest OK!\n")
  
  if len(sys.argv) < 2:
    print("Run " + sys.argv[0] + " -h for help.")

  parser = argparse.ArgumentParser(description='Prefence Profile Generator for PrefLib Tools.\n\n Can be run in interactive mode or from the command line to generate preferenes from a fixed set of statistical cultures.')
  parser.add_argument('-i', '--interactive', dest='interactive', action='store_true', help='Run in Interactive Mode.')
  parser.add_argument('-n', '--voters', type=int, dest='nvoter', metavar='nvoter', help='Number of voters in profiles.')
  parser.add_argument('-m', '--candidates', type=int, dest='ncand', metavar='ncand', help='Number of candidates in profiles.')
  parser.add_argument('-t', '--modeltype', type=int, dest='model', metavar='model', default="1", help='Model to generate the profile:  (1) Impartial Culture (2) Single Peaked Impartial Culture (3) Impartial Anonymous Culture (4) Mallows with 5 Reference Orders  (5) Mallows with 1 Reference Order  (6) Urn with 50%% Replacement.')
  parser.add_argument('-c', '--numinstances', type=int, dest='ninst', metavar='ninst', help='Number of instanes to generate.')
  parser.add_argument('-o', '--outpath', dest='outpath', metavar='path', help='Path to save output.')

  results = parser.parse_args()


  if results.interactive:
    # Generate a file in Preflib format with a specified number
    # of candidates and options
    print("Preference Profile Generator for PrefLib Tools. \nCan be run in interactive mode or from the command line to generate preferenes from a fixed set of statistical cultures.  \n\nRun with -h to see help and command line options. \n\n")
    ncand = int(input("Enter a number of candidates: "))
    nvoter = int(input("Enter a number of voters: "))

    print('''Please select from the following: \n 1) Impartial Culture \n 2) Single Peaked Impartial Culture \n 3) Impartial Anonymous Culture \n 4) Mallows with 5 Reference Orders \n 5) Mallows with 1 Reference Order \n 6) Urn with 50% Replacement \n''')
    model = int(input("Selection >> "))
    ninst = 1
  else:
    ncand = results.ncand if results.ncand != None else 1
    nvoter = results.nvoter if results.nvoter != None else 1
    model = results.model if results.model != None else 1
    ninst = results.ninst if results.ninst != None else 1
    base_file_name = "GenModel_"
    base_path = results.outpath if results.outpath != None else "./"

  candidateMap = gen_cand_map(ncand)
  for i in range(ninst):
    if model == 1:
      # Generate an instance of Impartial Culture
      rmaps, rmapscounts = gen_impartial_culture_strict(nvoter, candidateMap)
    elif model == 2:
      # Generate an instance of Single Peaked Impartial Culture
      rmaps, rmapscounts = gen_single_peaked_impartial_culture_strict(nvoter, candidateMap)
    elif model == 3:
      # Generate an instance of Impartial Aynonmous Culture
      rmaps, rmapscounts = gen_impartial_aynonmous_culture_strict(nvoter, candidateMap)
    elif model == 4:
      # Generate a Mallows Mixture with 5 random reference orders.
      rmaps, rmapscounts = gen_mallows_mix(nvoter, candidateMap, 5)
    elif model == 5:
      # Generate a Mallows Mixture with 1 reference.
      rmaps, rmapscounts = gen_mallows_mix(nvoter, candidateMap, 1)
    elif model == 6:
      #We can also do replacement rates, recall that there are items! orders, so
      #if we want a 50% chance the second preference is like the first, then
      #we set replacement to items!
      rmaps, rmapscounts = gen_urn_strict(nvoter, math.factorial(ncand), candidateMap)
    else:
      print("Not a valid model")
      exit()

    if results.interactive:
      #Print the result to the screen
      io.pp_profile_toscreen(candidateMap, rmaps, rmapscounts)

      #Write it out.
      fname = str(input("\nWhere should I save the file:  "))
      outf = open(fname, 'w')
      io.write_map(candidateMap, nvoter, rankmap_to_voteset(rmaps, rmapscounts),outf)
      outf.close()
    else:
      outf = open(base_path + base_file_name + str(i) + ".soc", 'w')
      io.write_map(candidateMap, nvoter, rankmap_to_voteset(rmaps, rmapscounts),outf)
      outf.close()
