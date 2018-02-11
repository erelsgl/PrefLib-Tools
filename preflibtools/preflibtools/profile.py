#!python3
'''
File:   profile.py
Author: Nicholas Mattei (nsmattei@gmail.com)
Date:   June 8, 2016

About
--------------------

This is the base classes for profiles and rank orders.  At the moment
we have just two classes (WeightedPrefOrder and Profile) where each element
of a profile is indexable.  While this creates a larger instance, it does
allow for more flexiable control.


* Copyright (c) 2016, Nicholas Mattei and NICTA and Data61 and CSIRO
* All rights reserved.
*
* Developed by: Nicholas Mattei
*               NICTA/Data61/CSIRO
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
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
* OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
* HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
* LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
* OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
* OF SUCH DAMAGE.

'''

class WeightedPreferenceOrder:
  '''
  Weighted Pref Order object which holds a weight, a mapping from
  ranks to elements, and possibly a utility.

  Data
  -----------
  ranks: dict
    A mapping of rank (integer) --> list of object id's.

  utilities: dict
    A mapping of rank (integer) --> utility (real).

  weight: real
    A real valued weight for this preference order.
  -----------

  >>> WeightedPreferenceOrder()  # empty instance
  Weight: 0.0
  Order: 
  Utilities: 

  >>> WeightedPreferenceOrder(ranks={1: [1], 2: [3], 3: [2]})  # simple instance
  Weight: 0.0
  Order: 1,3,2
  Utilities: 

  >>> WeightedPreferenceOrder(ranks={1: [1,4], 2: [3], 3: [2]})  # ties instance
  Weight: 0.0
  Order: {1,4},3,2
  Utilities: 
  
  >>> p = WeightedPreferenceOrder(ranks={1: [1,4], 2: [3], 3: [2]}, weight=12.0, utilities={1: 12, 2: 15.0, 3: 2})   # All features
  >>> p
  Weight: 12.0
  Order: {1,4},3,2
  Utilities: 12,15.0,2
  >>> p.get_order_list()
  [[1, 4], 3, 2]
  >>> p.get_order_tuple()
  ([1, 4], 3, 2)
  >>> p.get_order_string()
  '{1,4},3,2'
  >>> p.num_of_alternatives()
  4
  '''

  def __init__(self, ranks={}, utilities={}, weight=0.0):
    self.ranks = ranks
    self.utilities = utilities
    self.weight = weight
    
  def alternatives(self) -> list:
    return sum(self.ranks.values(),[])   # http://stackoverflow.com/a/952946/827927
    
  def num_of_alternatives(self):
    return len(self.alternatives())
               
    return len(sum(self.ranks.values(),[]))

  def get_order_list(self):
    return [v[0] if len(v)==1 else v     for k,v in sorted(self.ranks.items())]

  def get_order_tuple(self):
    return tuple(self.get_order_list())

  def get_order_string(self):
    o = ""
    for k,v in sorted(self.ranks.items()):
      if len(v) == 1:
        o += str(v[0]) + ","
      else:
        o += "{" + ",".join([str(x) for x in v]) + "}" + ","
    o = o[:-1]
    return o

  def get_utilities_string(self):
    o = ",".join([str(self.utilities[x]) for x in sorted(self.utilities.keys())])
    return o

  def __repr__(self):
    # Return in PrefLib format.
    return "Weight: " + str(self.weight) + "\nOrder: " + self.get_order_string() + "\nUtilities: " + self.get_utilities_string()


class WeightedOrderProfile:
  '''
  Basic Profile object that uses a weighted pref order as its internal
  representation.

  Data
  -----------
  objects: dict
    A mapping of object index (int) --> name.  Hence the keys are
    a list of all the ojects which one can have preference over.

  preferences: WeightedPrefOrder:
    A dict from ID --> weighted pref order object representing the preference
    of an agent.

  Notes
  -----------
  A possible future TODO is to collapse similar preferences, though
  this can be achieved by using a weighted profile implemented
  by whatever reader/writer we end up with.

  >>> WeightedOrderProfile()
  -------------------------------------------------------------------------------
      ID    |           Objects            
  -------------------------------------------------------------------------------
  -------------------------------------------------------------------------------
      ID    | Weight  |            Order             |           Utility            
  -------------------------------------------------------------------------------
  <BLANKLINE>


  >>> pref1 = WeightedPreferenceOrder(ranks={1: [1], 2: [2], 3: [3]}, weight=12, utilities={1: 10, 2: 9, 3: 8})
  >>> pref2 = WeightedPreferenceOrder(ranks={1: [2], 2: [1], 3: [3]}, weight=15, utilities={1: 5, 2: 6, 3: 4})
  >>> profile = WeightedOrderProfile(objects={1: "Candidate 1", 2: "Candidate 2"}, preferences={1: pref1, 2: pref2})
  >>> profile.get_map_from_order_to_weight()
  {(2, 1, 3): 15, (1, 2, 3): 12}
  >>> profile.num_of_alternatives()
  3
  >>> profile
  -------------------------------------------------------------------------------
      ID    |           Objects            
  -------------------------------------------------------------------------------
      1     |         Candidate 1          
      2     |         Candidate 2          
  -------------------------------------------------------------------------------
      ID    | Weight  |            Order             |           Utility            
  -------------------------------------------------------------------------------
      1     |   12    |            1,2,3             |            10,9,8            
      2     |   15    |            2,1,3             |            5,6,4             
  <BLANKLINE>
  '''
  def __init__(self, objects={}, preferences={}):
    self.objects = objects
    self.preferences = preferences
    
  def num_of_alternatives(self):
    for pref in self.preferences.values():
      return pref.num_of_alternatives()
    
  def get_map_from_order_to_weight(self) -> dict:
    """
    Returns a dict that maps each possible ranking (a tuple) to its weight (number of agents with that ranking).
    """
    return {v.get_order_tuple(): v.weight    for k,v in self.preferences.items()}

  def __repr__(self):
    # Object Headder
    o = "{:-^79}".format("") + "\n"
    o += "{:^10}".format("ID") + "|" + "{:^30}".format('Objects') + "\n"
    o += "{:-^79}".format("") + "\n"
    for k,v in sorted(self.objects.items()):
      o +="{:^10}".format(str(k)) + "|" + "{:^30}".format(str(v)) + "\n"
    o += "{:-^79}".format("")

    # Preferences
    o += "\n" + "{:^10}".format("ID") + "|" + "{:^9}".format("Weight") + "|" + "{:^30}".format('Order') + "|" + "{:^30}".format('Utility') + "\n"
    o += "{:-^79}".format("") + "\n"
    for k,v in sorted(self.preferences.items()):
      o += "{:^10}".format(str(k)) + "|" + "{:^9}".format(str(v.weight)) + "|" + "{:^30}".format(v.get_order_string()) + "|" + "{:^30}".format(v.get_utilities_string()) + "\n"
    return o

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  print("Doctest OK!\n")
  
