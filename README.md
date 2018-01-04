# PrefLib-Tools

# About
**PrefLib Tools** - Python 3 tools for working with preference-relations. 

It is especially tailored for working with 
data from the PrefLib repository. see www.PrefLib.org for more information about the project and a large library of real-world preference data.

It also conatains functions for generating synthetic data for use in voting and preference experiments.  

The original code is by Nicholas Mattei and Data61/NICTA (c). For questions or comments please contact nsmattei@gmail.com or Nicholas.Mattei@nicta.com.au.

Some additions were made by Erel Segal-Halevi (erelsgl@gmail.com):

* Adding documentation to existing code.
* Adding code to check whether a preference-profile satisfies the Level-1 Consensus and Flexible Consensus domain restriction (see preflibtools/consensus.py).
* Adding code for simulation experiments related to domain-restrictions (see the experiments/ folder).

The code comes without warranty. Please use or distribute for research and academic uses only. 
Please use according to the citation and fair use requests on found at www.preflib.org.

# Installation
    git clone https://github.com/erelsgl/PrefLib-Tools

    cd PrefLib-Tools/preflibtools

    sudo pip3 install -e .

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
