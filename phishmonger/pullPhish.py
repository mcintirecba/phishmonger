#########################
# POSSIBLE IMPROVEMENTS #
#########################

# 1) skip a pull with 0 new sites (although making a folder is okay)
# 2) looping error should send an email and/or reset (note: disk space issue)

import bz2
import sys
import os
import json
from datetime import datetime
from subprocess import call, TimeoutExpired
import time
import requests
import shutil

##################################
# API KEY AND PATH CONFIGURATION #
##################################

# Set PhishTank API key and adjust folder paths as desired:

ptAPIkey = ''

indexPath = 'output/index/' # make sure this folder includes two subfolders: oldPulls and uniquePulls
pullPath = 'output/storage/'
archivePath = 'output/archives/'

########################
# FUNCTION DEFINITIONS #
########################

def countIndicies (path = indexPath):

	directory = path + "oldPulls/"
	numFiles = len([item for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item))])

	return(numFiles)

def findNewPulls (updateIndex = False, path = indexPath, useUniqueIndicies = False, doPull = False):

	numFiles = countIndicies()

	# subtract one from oldPulls if index was updated for a new pull (i.e., so new pull is not counted as "existing")
	if (updateIndex):
		numFiles = numFiles - 1

	print("Existing Index Count:", numFiles, "\n")

	# only fetch the new IDs that aren't already in the db
	'''
	j1 = loadOldPhish(filename = '1.json.bz2')
	j2 = loadOldPhish(filename = '2.json.bz2')

	l1 = []
	l2 = []

	for i, entry in enumerate(j1):
		l1.append(entry['phish_id'])
	for i, entry in enumerate(j2):
		l2.append(entry['phish_id'])

	newIDs = list(set(l2) - set(l1))

	print( "New ID count:", len(newIDs) )

	#print(newIDs[0])
	'''

	j1 = []
	j2 = []

	l1 = []
	l2 = []

	directory = path + "oldPulls/"

	# check for existing unique indicies
	try:
		with open(uniqueIndexPath + 'unique-pulls.json') as json_file:
			l1 = json.load(json_file)
	except:
		print("Note: No unique index file found...")
		useUniqueIndicies = False

	if useUniqueIndicies:
		uniqueIndexPath = path + "uniquePulls/"

		if not os.path.exists(uniqueIndexPath):
			os.makedirs(uniqueIndexPath)

		print("Loading unique indicies...\n")

		with open(uniqueIndexPath + 'unique-pulls.json') as json_file:
			l1 = json.load(json_file)

		print("Loading latest index:", len(os.listdir(directory)))
		j2 = loadOldPhish(filename = str(len(os.listdir(directory))) + '.json.bz2')

		for j, entry in enumerate(j2):
			l2.append(entry['phish_id'])

		if updateIndex == False:
			print("\nNote: Index was not updated. Including latest index in existing set...")
			l1 = list(set(l1 + l2))

	else:

		for i, item in enumerate(os.listdir(directory)):

			if i + 1 == len(os.listdir(directory)):
				print("\nLoading latest index:", i + 1)
				j2 = loadOldPhish(filename = str(i + 1) + '.json.bz2')

				for j, entry in enumerate(j2):
					l2.append(entry['phish_id'])

				# if the index is not updated, these are actually old pulls and should also be in l1
				if updateIndex == False:
					print("\nNote: Index was not updated. Including latest index in existing set...")
					for j, entry in enumerate(j2):
						l1.append(entry['phish_id'])


			else:
				print("Loading older index:", i + 1)
				temp = loadOldPhish(filename = str(i + 1) + '.json.bz2')

				for j, entry in enumerate(temp):
					l1.append(entry['phish_id'])

	print("\nLength of latest index:", len(l2))
	print("Length of older indices:", len(l1))
	print("Unique length of older indices:", len(set(l1)), "\n")

	newIDs = list(set(l2) - set(l1))
	print( "New ID count:", len(newIDs) )

	newUniqueIndicies = list(set(l1)) + newIDs
	oldUniqueIndicies = list(set(l1))

	# save the new unique indices with the old set (but only if we do pull)
	uniquePullsPath = path + "uniquePulls/"
	if doPull:
		writeIndicies = newUniqueIndicies
		print("New unique indicies count:", len(newUniqueIndicies), "\n")
	else:
		writeIndicies = oldUniqueIndicies
		print("Existing unique indicies count (note: no pull conducted):", len(oldUniqueIndicies), "\n")

	with open(uniquePullsPath + 'unique-pulls.json', 'w') as outfile:
		json.dump(writeIndicies, outfile)

	# save a backup in case of an error
	with open(uniquePullsPath + 'unique-pulls-bak.json', 'w') as outfile:
		json.dump(oldUniqueIndicies, outfile)

	return(newIDs)



def pullLivePhish (path = indexPath):

	url = 'http://data.phishtank.com/data/' + ptAPIkey + '/'
	filename = 'online-valid.json.bz2'

	head, tail = os.path.split(filename)

	r = requests.get(url + filename, stream=True)

	if r.status_code == 509:
		print("Hit 509 rate limit. Stopping execution...\n")
		print(r.headers)

		sys.exit(0)

	elif r.status_code == 200:
		with open(path + tail, 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)

		directory = path + "oldPulls/"

		if not os.path.exists(directory):
			os.makedirs(directory)

		numFiles = len([item for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item))]) + 1

		# save backup for reference
		shutil.copy2(path + tail, path + "oldPulls/" + str(numFiles) + ".json.bz2")
		return(path + "oldPulls/" + str(numFiles) + ".json.bz2")
	else:
		print("Unexpected error...\n")
		print(r.headers)

def decompressLivePhish (path = indexPath, filename = 'online-valid.json.bz2'):

	f = path + filename

	input = bz2.BZ2File(f, 'rb').read()

	head, tail = os.path.split(f)
	newfilename = ".".join( tail.split(".")[0:2] )
	#print(newfilename)

	open(path + newfilename, 'wb').write(input) # write a uncompressed file

def loadLivePhish (path = indexPath, file = 'online-valid.json'):

	with open(path + file) as json_file:
		json_data = json.load(json_file)

	#print(json_data)
	print("Using",len(json_data),"live sites from latest pull to collect new sites...")

	return(json_data)

def loadOldPhish (path = indexPath + "oldPulls/", filename = '1.json.bz2'):

	f = path + filename

	input = bz2.BZ2File(f, 'rb').read()

	json_data = json.loads(input.decode('UTF-8'))

	#print(json_data)
	print("Fetched a total of",len(json_data),"live sites...")

	return(json_data)

def pullFullWebsite (outpath = 'output/test', url = 'http://www.phishtank.com/', thorough=False, silent=False, entry=''):

	# note for silent, fullpath is expected

	if not os.path.exists(outpath):
		os.makedirs(outpath)

	extraOptions = []
	if thorough:
		extraOptions.append('-H')
	if silent:
		#extraOptions.append('-a'+ os.getcwd() + '/' + outpath + '/log.txt')
		extraOptions.append('-a' + outpath + '/log.txt')

	try:
		call(['wget', '--mirror', '--page-requisites', '--adjust-extension', '--backup-converted', '-e robots=off', '--convert-links', '--level=1', '--tries=3', '--timeout=60', '--quota=10m', '-P' + outpath, url] + extraOptions, timeout = 60*60) # fail after 60 minutes

		open(outpath + "/" + "index.txt", 'w').write(url)

		if entry != '':
			f = open(outpath + "/" + "index.json", 'w')
			json.dump(entry, f)
			f.close()

	except TimeoutExpired:
		print("Operation timed out. Deleting folder and skipping...")
		shutil.rmtree(outpath)



def pullPhish (updateIndex = False, doPull = False, useUniqueIndicies = False, doCompress = False, pullPath = '/media/ubuntu/storage/', archivePath = '/media/ubuntu/archives/'):

	if updateIndex == True:
		backupPath = pullLivePhish()
		print("Pulling latest index (", str(countIndicies()), ")...\n", sep="")
		decompressLivePhish()

	# build new pull list
	newIDs = findNewPulls(updateIndex = updateIndex, useUniqueIndicies = useUniqueIndicies, doPull = doPull)

	# conduct actual pull
	countPulls = 0

	if doPull is False and updateIndex is True:
		print("Removing latest index since no pull was conducted...\n")
		os.remove(backupPath)

	if doPull is True:

		json_data = loadLivePhish()

		# check starting path and create if needed
		theBasePath = pullPath + 'output_' + str(countIndicies()) + '/'

		if not os.path.exists(theBasePath):
			os.makedirs(theBasePath)

		# handle resume
		for i, entry in enumerate(json_data):

			thePath = theBasePath + entry["target"] + '/' + entry["phish_id"] # note this path includes which index it belongs to

			pullSite = False
			entryIsNew = False

			# only do entries not already fetched
			if entry["phish_id"] in newIDs:
				entryIsNew = True
			else:
				entryIsNew = False

			#entryIsNew = False

			if entryIsNew:

				# avoid undoable pulls
				if os.path.isdir(thePath) and os.listdir(thePath):
					#print("Exists...")
					pass
				elif os.path.isdir(thePath) and not os.listdir(thePath):
					print("Need to fetch (folder exists but empty)..." + entry["phish_id"])
					pullSite = True
				elif not os.path.isdir(thePath):
					print("Need to fetch (folder does not exist)..." + entry["phish_id"])
					pullSite = True

				if pullSite:
					countPulls += 1
				#pullSite = False

				if pullSite:
					print("Now fetching: ", entry["phish_id"], " (", i+1, " of ", len(json_data), ")", " - ", time.strftime("%a %b %d %I:%M:%S %p"), sep='') #entry["url"]
					#print(entry["url"])
					pullFullWebsite(thorough=True, silent=True, outpath=thePath, url = entry["url"], entry = entry)

		print("Total pulls:", countPulls, "\n")

		if doCompress:
			whichOutputFolder = 'output_' + str(countIndicies()) + '/'
			archiveFile = 'output_' + str(countIndicies()) + '.tar.gz'

			call(['tar', '-zcf', archivePath + archiveFile, whichOutputFolder], cwd = pullPath)

#############
# MAIN CALL #
#############

def doTwistedPull ():

	startTime = datetime.now().replace(microsecond=0)

	print("Operation started at:", time.strftime("%a %b %d %I:%M:%S %p"), "\n")
	pullPhish(updateIndex = True, doPull = True, useUniqueIndicies = True, doCompress = True, pullPath = pullPath, archivePath = archivePath)

	print("Operation completed at:", time.strftime("%a %b %d %I:%M:%S %p"), "\n", "Duration:", datetime.now().replace(microsecond=0) - startTime, "\n\nPausing for timeout...\n\n---\n")

# doTwistedPull()

########
# MISC #
########

# this can rebuild the index if needed (potentially very time consuming)
# pullPhish(updateIndex = False, doPull = False, useUniqueIndicies = False, doCompress = False, pullPath = pullPath, archivePath = archivePath)
