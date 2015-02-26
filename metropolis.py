#!/usr/bin/env python
import math
import time
import random
from tail import tail_call_optimized
from mpi4py import MPI
comm=MPI.COMM_WORLD
currentRank=0
# Gas constant  kcal/mol/degree
R=1.9872156e-3


#particle in a classical 1D double-well potential
class particle(object):
  def __init__(self,position):
    self.position=position

  def energy(self):
    return self.trial(0.0)

  def move(self,displace):
    self.position=self.position+displace

  def trial(self,displace):
    x=self.position+displace
    return x**4-5.*x**2+5.*x


# metropolis monte carlo algorithm
class metropolis(object):
  def __init__(self,temperature,steps,stepSize,exchange):
    self.steps=steps
    self.exchange=exchange
    self.temperature=temperature
    self.beta=1.0/R/temperature
    self.stepSize=stepSize
    self.particles=list()
    self.out=open('rank'+str(comm.rank),'w')

  def setTemperature(self,temperature):
    self.temperature=temperature
    self.beta=1.0/R/temperature

  def addParticle(self,particle):
    self.particles.append(particle)

  def exTrial(self,newTemp,newE):
    #Metropolis-Hastings criterion
    print comm.rank,' checking ',self.temperature,newTemp
    myE = self.particles[0].energy()
    return math.exp( (myE - newE) * (1.0/R/self.temperature - 1.0/R/newTemp) )

  @tail_call_optimized
  def step(self,step=0):
    step=step+1
    if(step == self.steps):
      return

    eOld = self.particles[0].energy()

    #this is the parallel tempering monte carlo method
    #very clunky communication, but works
    if(step%self.exchange==0):
      comm.Barrier()
      print comm.rank,self.temperature,' ready'
      newTemp=None
      if(comm.rank==1):
        comm.send(self.temperature,dest=0,tag=11)
        comm.send(eOld,dest=0,tag=21)
        print comm.rank,' send t and e'
        newTemp = comm.recv(source=0,tag=10)
      elif(comm.rank==0):
        newTemp = comm.recv(source=1,tag=11)
        newE = comm.recv(source=1,tag=21)
        print comm.rank,' received ',newTemp,newE
        if(self.exTrial(newTemp,newE)<1.0):
          print comm.rank,' sent accepted temp'
          comm.send(self.temperature,dest=1,tag=10)
        else:
          #I am actually sending the original temperature back
          print comm.rank, 'send back ',newTemp
          comm.send(newTemp,dest=1,tag=10)
          newTemp=self.temperature

      self.setTemperature(newTemp)
      print comm.rank,self.temperature,' who am i?'
      comm.Barrier()
      print

    trialMove = self.stepSize*(random.randint(-10,11)/10.)*2.0
    eTrial = self.particles[0].trial(trialMove)

    deltaE = eTrial - eOld

    if(deltaE < 0.0):
      self.particles[0].move(trialMove)
      if(step>0.7*self.steps):
        p="%d %f %f %d\n" % (step,self.particles[0].position,self.particles[0].energy(),self.temperature)
        self.out.write(p)
    else:
      w = math.exp(-self.beta*abs(deltaE))
      rand = random.random()
      if (rand <= w):
        self.particles[0].move(trialMove)
        if(step>0.7*self.steps):
          p="%d %f %f %d\n" % (step,self.particles[0].position,self.particles[0].energy(),self.temperature)
          self.out.write(p)

    self.step(step)





# outline for parallelTempering container
class parallelTempering(object):
  def __init__(self,steps,exchange):
    self.steps=steps
    self.exchange=exchange
    self.simulations=list()
    self.placement={}

  #every item gets added on a differet mpi rank
  #every rank have identical placement dictionaries
  def addSimulation(self,simulation):
    global currentRank
    if(comm.rank==0):
      print "Adding " + str(simulation.temperature) + " : Rank " + str(currentRank)

    if(comm.rank==currentRank):
      self.simulations.append(simulation)
    self.placement[simulation.temperature]=currentRank

    currentRank = currentRank+1
    if(currentRank == comm.size):
      currentRank=0


if __name__ == "__main__":
  random.seed(104424)

  if(comm.rank==0):
    sim=metropolis(75,1000000,0.1,250)
    sim.addParticle(particle(-1.0))
  elif(comm.rank==1):
    sim=metropolis(100,1000000,0.1,250)
    sim.addParticle(particle(1.5))

  sim.step()


