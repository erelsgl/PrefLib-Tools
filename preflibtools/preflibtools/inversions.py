#!python3
"""
Functions related to inversions of elements in arrays.

Author:  Erel Segal-Halevi (collected from various sources)
Date:    2017-02
"""

import functools

@functools.lru_cache(maxsize=None)
def numNPermutationsWithAtMostKInversions(N: int, K: int) -> int:
	"""
	Return the number of n-element permutations with at most k inverted pairs.
	"""
	return sum([numNPermutationsWithKInversions(N,i) for i in range(K+1)])

@functools.lru_cache(maxsize=None)
def numNPermutationsWithKInversions(N: int, K: int) -> int:
	"""
	Return the Mahonian number T(N,K) --- the number of n-element permutations with exactly k inverted pairs.

	Based on an explanation by Vineel Kumar Reddy Kovvuri, http://stackoverflow.com/a/25747326/827927

	>>> numNPermutationsWithKInversions(4,0)
	1
	>>> numNPermutationsWithKInversions(4,1)
	3
	>>> numNPermutationsWithKInversions(4,2)
	5
	>>> numNPermutationsWithKInversions(4,3)
	6
	>>> numNPermutationsWithKInversions(4,4)
	5
	>>> numNPermutationsWithKInversions(4,5)
	3
	>>> numNPermutationsWithKInversions(4,6)
	1
	>>> numNPermutationsWithKInversions(4,7)
	0
	"""
	if K==0: return 1
	if N==0: return 0

	#I(n, k) = sum of I(n-1, k-i) such that i < n && k-i >= 0
	val = 0
	for j in range(min(N,K+1)):
	    val += numNPermutationsWithKInversions(N-1, K-j);
	return val;


def inversionDistance(A: list, B: list) -> int:
	"""
	INPUT: two lists, A and B. Must have the same size and the same set of elements.

	OUTPUT: The number of adjacent-inversions required to change A to B.


	>>> inversionDistance([1,2,3],[1,2,3])
	0
	>>> inversionDistance([1,2,3],[1,3,2])
	1
	>>> inversionDistance([1,2,3],[2,3,1])
	2
	>>> inversionDistance([1,2,3],[3,2,1])
	3
	>>> inversionDistance([1,3,2],[3,1,2])
	1
	>>> inversionDistance([1,3,2],[1,2,3])
	1
	>>> inversionDistance([1,3,2],[3,2,1])
	2
	>>> inversionDistance([1,3,2],[2,3,1])
	3
	>>> inversionDistance([3,2,1],[3,2,1])
	0
	>>> inversionDistance([3,2,1],[2,3,1])
	1
	>>> inversionDistance([3,2,1],[3,1,2])
	1
	>>> inversionDistance([3,2,1],[2,1,3])
	2
	>>> inversionDistance([3,2,1],[1,2,3])
	3
	>>> inversionDistance([1,4,2,3],[1,2,4,3])
	1
	>>> inversionDistance([1,4,2,3],[3,2,4,1])
	6
	"""
	inverseA = {A[i]: i for i in range(len(A))}
	renamedB = [inverseA[b] for b in B]
	return sortCount(renamedB)[1]


def sortCount(A: list) -> (list,int):
	"""
	Author: Shawn Ohare, http://www.shawnohare.com/2013/08/counting-inversions-in-python.html

	Sort the array A and calculate the number of inversions in it.

	>>> sortCount([1,2,3])[1]
	0
	>>> sortCount([1,3,2])[1]
	1
	>>> sortCount([2,1,3])[1]
	1
	>>> sortCount([2,3,1])[1]
	2
	>>> sortCount([3,1,2])[1]
	2
	>>> sortCount([3,2,1])[1]
	3
	"""
	l = len(A)
	if l > 1:
		n = l//2
		C = A[:n]
		D = A[n:]
		C, c = sortCount(A[:n])
		D, d = sortCount(A[n:])
		B, b = mergeCount(C,D)
		return B, b+c+d
	else:
		return A, 0


def mergeCount(A: list, B: list) -> (list,int):
	""" Subroutine of sortCount """
	count = 0
	M = []
	while A and B:
		if A[0] <= B[0]:
			M.append(A.pop(0))
		else:
			count += len(A)
			M.append(B.pop(0))
	M  += A + B
	return M, count


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print("Doctest OK!\n")

	print(numNPermutationsWithKInversions(200,200))
	# print(inversionDistance([2,5,6,7,8],[8,7,4,5,2])) # exception - not the same elements
