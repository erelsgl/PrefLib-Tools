# PrefLib-Tools
README.md for PrefLib Tools (c) Nicholas Mattei and Data61/NICTA.

A a small of lightweight tools in Python3 for working with data from www.PrefLib.org and generating synthetic data for use in voting and preference experiments.

Please see www.PrefLib.org for more information about our project and a large library of real-world preference data For questions or comments please contact nsmattei@gmail.com or Nicholas.Mattei@nicta.com.au.

This code comes without warranty. Please use or distribute for research and academic uses only. Please use according to the citation and fair use requests on found at www.preflib.org.

#Dev Notes
- This is being updated piecemeal in order to make it a more coherent Python package and make the interface more reasonable.  The master branch will always contain a working version of the code while the dev branch may be a bit spotty.
- I am currently working on adding some tests and adding notebooks which serve as documentation to the interface.
- We are mid-refactor so the tools may be broken until the next major release number (v2.0).  Please checkout from tagged version 1.5 if you need working tools.
- The notebooks and most of the library is build around a full SciPy stack (IPython, MatPlotLib, Numpy, Pandas, etc.).  For more on scientific computing in Python please see the great resource at http://bender.astro.sunysb.edu/classes/python-science/ 

## Dev Version > 1.5
This release includes a new directory structure and information to use PrefLib Tools as a package.

-To install use pip3 install -e . as we are still devloping the library and you likely don't want to install it every time.  It may be best to do this in a virturalenv for any projects you are working on.

## Release Version 1.5

This release includes the following 3 files:

1. generate_profiles.py
2. io.py
3. domain_restriction.py

# OVERVIEW

The code in this release consists of the working versions of code that has
been used in my research for a couple of years.

Currently the code-base has the ability to:

- Read and write all the PrefLib file formats.

- Generate profiles according to various distributions including
	Impartial Culture (IC), Impartial Anonymous Culture (IAC), 
	Urn Cultures (UC), Single Peaked Impartial Culture (SPIC),
	and Mallows Mixture Models (MMM).  Please refer to
	GenerateProfiles.py for examples and an easy to use command line interface

- Test for domain restrictions like SinglePeakedness.

## DETAILS

The code is built around the following basic data objects.  These are all 
just basic Python data structures (lists and dictionaries).  The plan is to port this whole structure into a more OO friendly structure in the future when we finish the Matching toolkits.

Generally speaking a Profile (set of votes) is represented by one or more of the following elements.  votemap and rankmaps are two different ways to view the same profile and this should likely all be formalized under a "Profile" object in a future release.

- candmap
	-- A candmap is a dictionary that maps a candidate number onto a
	candidate name.

- votemap
	-- A votemap is a dictionary that maps a string representing
	a vote in PrefLib format onto the count of that vote in the 
	profile represented by the votemap.

- rankmap
	-- A rankmap is a dictionary that maps the candidate numbers
	to a rank (1 up to the number of candidates).  This 
	allows us to represent partial and strict orders in 
	the same way.

- rankmapcounts
	-- A rankmapcouns array is a parallel array to an array of rankmaps
	which keeps a count of the number of times that rankmap exists
	in a profile.




