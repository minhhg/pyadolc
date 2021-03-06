#!/usr/bin/env python

"""
This file fixes a shortcoming of the hov_reverse as implemented in ADOL-C.
ADOLC only supports to prodived adjoint directions U in (Q x M).
To "lift" tapes we need the means to provide also the higher order coefficients,
i.e. we want to pass
U in ( Q x M x D ) 
"""

import numpy
import adolc

def hovt_reverse(tape_tag,D,U):
	"""
	This is a workaround for hov_reverse that allows
	U as Q x M x D matrix
	"""
	Q,M,D = numpy.shape(U)
	V = numpy.zeros((Q*D,M))
	for q in range(Q):
		for d in range(D):
			V[q*D+d,:] = U[q,:,d]
	(Z,z) = adolc.hov_reverse(tape_tag,D,V)

	N = numpy.shape(Z)[1]

	def delta(d):
		if d == 0:
			return
		else:
			return d

	W = numpy.zeros((Q,N,D+1))
	for q in range(Q):
		for d in range(D):
			W[q,:,d:] += Z[q*D+d,:, :delta(-d)]

	return (W,z)


def ffcn(x):
	return numpy.array([x[0]*x[1]*x[2],x[0]*x[1]])

if __name__ == "__main__":
	N = 3
	ax = numpy.array([adouble(0) for i in range(N)])
	trace_on(1)
	for n in range(N):
		ax[n].is_independent(n+1)
	ay = ffcn(ax)
	depends_on(ay[0])
	depends_on(ay[1])
	trace_off()

	# hos_forward
	x = numpy.array([3,5,7.])
	D = 2
	keep = D+1
	V = numpy.zeros((N,D))
	V[0,0] = 1
	adolc.hos_forward(1,D,x,V,keep)

	# hovt_reverse
	Q = 2
	M = 2
	U = numpy.zeros((Q,M,D))
	U[0,0,0] = 1
	U[0,0,1] = 2
	U[1,1,0] = 3
	U[1,1,1] = 4
	#print 'U=',U
	Z = hovt_reverse(1,D,U)[0]

	# first adoint direction
	# xbar
	assert Z[0,0,0] == 35
	assert Z[0,0,1] == 70
	# ybar
	assert Z[0,1,0] == 21
	assert Z[0,1,1] == 49
	# zbar
	assert Z[0,2,0] == 15
	assert Z[0,2,1] == 35

	# second adoint direction
	# xbar
	assert Z[1,0,0] == 15
	assert Z[1,0,1] == 20
	# ybar
	assert Z[1,1,0] == 9
	assert Z[1,1,1] == 15
	# zbar
	assert Z[1,2,0] == 0
	assert Z[1,2,1] == 0


	# combine the above results
	Q = 1
	M = 2
	U = numpy.zeros((Q,M,D))
	U[0,0,0] = 1
	U[0,0,1] = 2
	U[0,1,0] = 3
	U[0,1,1] = 4
	#print 'U=',U
	Z2 = hovt_reverse(1,D,U)[0]

	# xbar
	assert Z2[0,0,0] == Z[0,0,0] + Z[1,0,0]
	assert Z2[0,0,1] == Z[0,0,1] + Z[1,0,1]
	# ybar
	assert Z2[0,1,0] == Z[0,1,0] + Z[1,1,0]
	assert Z2[0,1,1] == Z[0,1,1] + Z[1,1,1]
	# zbar
	assert Z2[0,2,0] == Z[0,2,0] + Z[1,2,0]
	assert Z2[0,2,1] == Z[0,2,1] + Z[1,2,1]


	

