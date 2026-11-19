import numpy as np
from itertools import product
rng=np.random.default_rng(4)
n=2; I=np.eye(n); J=np.block([[np.zeros((n,n)),I],[-I,np.zeros((n,n))]])
T=np.block([[-I,I],[np.zeros((n,n)),I]])
Rs=[np.vstack((np.diag(d),np.diag((1+np.array(d))/2))) for d in product([-1,1],repeat=n)]
def cop2(Q): return min(Q[0,0],Q[1,1],Q[0,1]+np.sqrt(max(0,Q[0,0]*Q[1,1])))>=-1e-9
def valid(M): return all(cop2(R.T@M@R) for R in Rs)
pool=[]
for k in range(20000):
 N=rng.integers(0,5,(4,4)); N=(N+N.T)/2
 M=T.T@N@T
 M[:n,:n]+=np.ceil(max(0,1-np.linalg.eigvalsh(M[:n,:n])[0]))*I
 t=np.ceil(max(1,(np.linalg.eigvalsh(M[n:,n:])[-1]+1)/2))
 M+=np.block([[np.zeros((n,n)),t*I],[t*I,-2*t*I]])
 H=-J.T@np.linalg.inv(M)@J
 assert valid(M)
 if pool:
  M0,H0=pool[rng.integers(len(pool))]
  Ha=(H+H0)/2; Ma=-J@np.linalg.inv(Ha)@J.T
  if not valid(Ma):
   print('FOUND',k); print('M1',M0);print('M2',M);print('Havg',Ha);print('Mavg_recovered',Ma);print('qcs',[R.T@Ma@R for R in Rs]); break
 pool.append((M,H))
else: print('none')
H=np.array([[1.125,-1,2,0],[-1,1.125,0,2],[2,0,-4,2],[0,2,2,-4]])
print('incremental example eigenvalues',np.linalg.eigvalsh(H))
for d in product([0,1],repeat=2):
 E=np.vstack((I,np.diag(d))); print(d,np.linalg.eigvalsh(E.T@H@E))
V=np.array([[np.sqrt(3),1],[np.sqrt(3),-1],[np.sqrt(3)/2,1.5],[np.sqrt(3)/2,-1.5]])
print('sector separation trace',np.trace(V.T@H@V))
