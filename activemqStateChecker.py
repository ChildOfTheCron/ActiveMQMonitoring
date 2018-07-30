#!/usr/bin/python3.5
 
import requests
import json
import time
import argparse
import io
import sys

class QueueDataStorage(object):
	def __init__(self, queueData, consumerData):
		self.queueData = queueData
		self.consumerData = consumerData

class QueueParser(object):
	def __init__(self, queueURL, user, passwd):
		self.queueURL = queueURL
		self.user = user
		self.passwd = passwd

	def getData(self): 

		rawJsonData = requests.get(self.queueURL, auth=(self.user, self.passwd))
	
		firstVal = rawJsonData.json()
		subDict = firstVal['value']

		newJson = json.dumps(subDict, sort_keys=True, indent=4, separators=(',', ': ')) 
		queueJson = json.loads(newJson)
		queueData = QueueDataStorage(queueJson["QueueSize"], queueJson["ConsumerCount"])	
		
		return queueData

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("url", help="URL of GET request", type=str)

	args = parser.parse_args()

	oldObjectPool = {}
	newObjectPool = {}	

	queueUser = 'user'
	queuePass = 'user'
	flagConsumerDown = False
	flagSizeIssue = False

	tmpParser = QueueParser(args.url, queueUser, queuePass)
	tmpParserData = tmpParser.getData()
	tmpID = args.url
	oldObjectPool[tmpID] = tmpParserData

        if (oldObjectPool[key].consumerData == 0):
            print("WARNING: No consumers found for queue.")
            sys.exit(1)

	time.sleep(1800)
	
	tmpParser = QueueParser(args.url, queueUser, queuePass)
	tmpParserData = tmpParser.getData()
	tmpID = args.url
	newObjectPool[tmpID] = tmpParserData
	
	for key in oldObjectPool:
		if (key in newObjectPool):
			if (oldObjectPool[key].consumerData == 0 or newObjectPool[key].consumerData == 0):
				#print("WARNING: No consumers found for one or more ingest queues.")
 				#sys.exit(1)
				flagConsumerDown = True
			if (oldObjectPool[key].queueData < newObjectPool[key].queueData):
				#print("WARNING: Ingest queue size larger than set threshold for one or more queues.")
				#sys.exit(1)
				flagSizeIssue = True

	if (flagConsumerDown and flagSizeIssue):
		print("WARNING: No consumers found for queue, ingest queue size larger than before.")
		sys.exit(1)
	elif flagSizeIssue:
		print("WARNING: Queue size larger than previous size.")
		sys.exit(1)
	elif flagConsumerDown:
		print("WARNING: No consumers found for queue.")
		sys.exit(1)
	else:
		print("Check OK")
		sys.exit(0)
		


