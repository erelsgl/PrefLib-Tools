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
  It requires io to work properly.

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
  voteset = gen_urn(numvotes, numreplace=0, alternatives=candmap.keys())   # a map from ranking-tuples to num-of-occurences in the profile.
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
  voteset = {}
  for i in range(numvotes):
    tvote = gen_icsp_single_vote(list(candmap.keys()))  # returns a tuple representing a rank
    voteset[tvote] = voteset.get(tvote, 0) + 1
  return voteset_to_rankmap(voteset)

# Generate strict Urn
# Identical to gen_urn_culture_strict
def gen_urn_strict(numvotes, numreplace, candmap):
  voteset = gen_urn(numvotes, numreplace, candmap.keys())
  return voteset_to_rankmap(voteset)

# Generate a Mallows model with the various mixing parameters passed in
# nvoters is the number of votes we need.
# candmap is a dictionary that maps candidate id to candidate name.
# mix is an array such that sum(mix) == 1 and describes the distro over the models
# phis is an array len(phis) = len(mix) = len(refs) that is the phi for the particular model
# refs is an array of dicts that describe the reference ranking for the set.
def gen_mallows(nvoters, candmap, mix, phis, refs):
  if len(mix) != len(phis) or len(phis) != len(refs):
    print("Mix != Phis != Refs")
    exit()

  #Precompute the distros for each Phi and Ref.
  #Turn each ref into an order for ease of use...
  m_insert_dists = []
  for i in range(len(mix)):
    m_insert_dists.append(compute_mallows_insertvec_dist(len(candmap), phis[i]))

  #Now, generate votes...
  votemap = {}
  for cvoter in range(nvoters):
    #print("drawing")
    cmodel = draw(list(range(len(mix))), mix)
    #print(cmodel)
    #print(refs[cmodel])
    #Generate a vote for the selected model
    insvec = [0] * len(candmap)
    for i in range(1, len(insvec)+1):
      #options are 1...max
      #print("Options: " + str(list(range(1, i+1))))
      #print("Dist: " + str(insertvec_dist[i]))
      #print("Drawing on model " + str(cmodel))
      insvec[i-1] = draw(list(range(1, i+1)), m_insert_dists[cmodel][i])
    vote = []
    for i in range(len(refs[cmodel])):
      vote.insert(insvec[i]-1, refs[cmodel][i])
    #print("mallows vote: " + str(vote))
    tvote = tuple(vote)
    votemap[tuple(vote)] = votemap.get(tuple(vote), 0) + 1

  return voteset_to_rankmap(votemap, candmap)

# Generate Mallows with a particular number of reference rankings and phi's drawn iid.
def gen_mallows_mix(nvoters, candmap, nref):
  """
  INPUT:
  nvoters - int, number of votes to generate.
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
  return gen_mallows(nvoters, candmap, mix, phis, refs)


#  Helper Functions -- Actual Generators -- Don't call these directly.

# Return a value drawn from a particular distribution.
def draw(values, distro):
  #Return a value randomly from a given discrete distribution.
  #This is a bit hacked together -- only need that the distribution
  #sums to 1.0 within 5 digits of rounding.
  if round(sum(distro),5) != 1.0:
    print("Input Distro is not a Distro...")
    print(str(distro) + "  Sum: " + str(sum(distro)))
    exit()
  if len(distro) != len(values):
    print("Values and Distro have different length")

  cv = 0
  draw = random.random() - distro[cv]
  while draw > 0.0:
    cv+= 1
    draw -= distro[cv]
  return values[cv]
# For Phi and a given number of candidates, compute the
# insertion probability vectors.
def compute_mallows_insertvec_dist(ncand, phi):
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

# Return a Tuple for a IC-Single Peaked... with alternatives in range 1....range.
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
