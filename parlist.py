#!/usr/bin/env python
import time
from mpi4py import MPI
comm=MPI.COMM_WORLD

class parList(list):
  #proxy is not currently used
  def __init__(self):
    self.proxy=list()
    return super(parList,self).__init__(self)

  def append(self,item):
    self.proxy.append(item.temperature)
    if(comm.rank==len(self)):
      return super(parList,self).append(item)
    else:
      return super(parList,self).append(None)

  def __getitem__(self,key):

    #just broadcast the item to all other processes
    if(comm.rank==key):
      myItem = list.__getitem__(self,key)
    else:
      myItem = None
    myItem = comm.bcast(myItem,root=key)
    return myItem

    #this is the original version
    #return list.__getitem__(self,key)

class simulation(object):
  def __init__(self,temperature):
    self.temperature=temperature

  def __str__(self):
    return str(self.temperature)
  def __repr__(self):
    return str(self.temperature)

  #may need to be very creative
  def setTemperature(self,temperature):
    self.temperature=temperature


if __name__ == "__main__":
  l = parList()
  l.append(simulation(10))
  l.append(simulation(20))
  l.append(simulation(30))
  l.append(simulation(40))

  print comm.rank,l
  comm.Barrier()
  print l[1]
  comm.Barrier()
  print comm.rank,l


  #does not work yet
  #if(comm.rank==0):
    #print
    #print "making exchanges"

  #tmp=l[0].temperature
  #l[0].setTemperature(l[1].temperature)
  #l[1].setTemperature(tmp)

  #tmp=l[2].temperature
  #l[2].setTemperature(l[3].temperature)
  #l[3].setTemperature(tmp)
  #print comm.rank,l
