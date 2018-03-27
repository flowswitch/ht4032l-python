"""Acquisition example"""
import sys
from HT4032L import HTDriver, LA

la = LA(driver=HTDriver()) # use Hantek native driver
la.open()

print "Reset..."
la.Reset()

la.SetThresholdA(3.3/2)
la.SetThresholdB(3.3/2)

la.config.SampleRate = 0x1C # 1KS/s
la.config.EnableTrigger1 = 1
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

print "Getting data..."
data = la.GetData()
la.close()
print "Got %d samples" % (len(data))
