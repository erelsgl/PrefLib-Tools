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

class WeightedPrefOrder:
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

  Notes
  -----------
  '''

  def __init__(self, ranks={}, utilities={}, weight=0.0):
    self.ranks = ranks
    self.utilities = utilities
    self.weight = weight

  def get_order_string(self):
    o = ""
    for k in sorted(self.ranks.keys()):
      if len(self.ranks[k]) == 1:
        o += str(self.ranks[k][0]) + ","
      else:
        o += "{" + ",".join([str(x) for x in self.ranks[k]]) + "}" + ","
    o = o[:-1]
    return o

  def get_utilities_string(self):
    o = ",".join([str(self.utilities[x]) for x in sorted(self.utilities.keys())])
    return o

  def __repr__(self):
    # Return in PrefLib format.
    return "Weight: " + str(self.weight) + "\nOrder: " + self.get_order_string() + "\nUtilities: " + self.get_utilities_string()




class Profile:
  """
  Profile object for PrefLib Tools.  This holds all
  the information for an anonymous prefernce profile.

  Data
  -----------
  objects: dict
    A mapping of object index --> name.  Hence the keys are
    a list of all the ojects which one can have preference over.

  prefs: array like
    An array

'''

