#!python3
'''
  File:   profile_tests.py
  Author: Nicholas Mattei (nsmattei@gmail.com)
  Date:   June 8, 2016

  About
  --------------------
    Tests to work out the profile class and the IO.

    For PyTest we need....

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

from preflibtools import profile
from preflibtools import io

def test_weighted_order():
  '''
    Test the code for the weighted pref order class.
  '''
  print("** test: Generating an empty instance")
  order = profile.WeightedPreferenceOrder()
  print(order)

  print("** test: Simple instance")
  order = profile.WeightedPreferenceOrder(ranks={1: [1], 2: [3], 3: [2]})
  print(order)

  print("** test: Ties instance")
  order = profile.WeightedPreferenceOrder(ranks={1: [1,4], 2: [3], 3: [2]})
  print(order)

  print("** test: All")
  order = profile.WeightedPreferenceOrder(ranks={1: [1,4], 2: [3], 3: [2]}, weight=12.0, utilities={1: 12, 2: 15.0, 3: 2})
  print(order)

  print("** Creating some profiles")
  p = profile.WeightedOrderProfile()
  print(p)

  print("** Creating some profiles")
  p = profile.WeightedOrderProfile(objects={1: "Candidate 1", 2: "Candidate 2"}, preferences={1: order, 2: order})
  print(p)

def test_file_read():
  p = io.read_weighted_preflib_file("/Users/Nick/repo/www-preflib.github/www/data/election/agh/ED-00009-00000001.soc")

  print(p)

  p = io.read_weighted_preflib_file("/Users/Nick/repo/www-preflib.github/www/data/election/glasgow/ED-00008-00000001.toc")

  print(p)
