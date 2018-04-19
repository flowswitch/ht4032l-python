"""Acquisition example"""
import sys
from HT4032L import LA

la = LA()
print "Using", la.driver.name

la.open()

print "Reset..."
la.Reset()

la.SetThresholdA(3.3/2)
la.SetThresholdB(3.3/2)

la.config.SampleRate = 0x1B # 2KS/s
la.config.SampleDepth = 2048
la.config.EnableTrigger1 = 0
la.config.EnableTrigger2 = 0
la.config.Trigger1.EdgeSignal = 0 # A0
la.config.Trigger1.EdgeType = 0 # posedge

print "Start..."
la.Start()

print "Poll..."
prev_status = -1
while la.status[2]!=2: # not DONE
	la.Poll()
	if prev_status!=la.status[2]:
		print "\n", la.status[2]
		prev_status = la.status[2]
	sys.stdout.write("\r%08X" % (la.status[1]))

print "\nGetting data..."
data = la.GetData()
la.close()
print "Got %d samples" % (len(data))
