import sys
from HT4032L import HTDriver, LA
from util import outhex

la = LA(driver=HTDriver())
la.open()

print "Reset..."
la.Reset()

la.SetThresholdA(1.7)
la.SetThresholdB(1.7)

la.config.SampleRate = 0x1C
la.config.EnableTrigger1 = 1
la.config.EnableTrigger2 = 0
la.config.Trigger1.EdgeSignal = 0 # A0
la.config.Trigger1.EdgeType = 0 # posedge

print "Start..."
la.Start()

print "Poll..."
prev_status = -1
poll_cnt = 0
while la.status[2]!=2:
	la.Poll()
	poll_cnt += 1
	if prev_status!=la.status[2]:
		print "\n", la.status[2]
		prev_status = la.status[2]
	sys.stdout.write("\r%08X" % (la.status[1]))

print "\nTriggered at", poll_cnt
print "Getting data..."
data = la.GetData()
print hex(len(data))

la.close()
