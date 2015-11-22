#! /opt/python/2.7.5/bin/python

import argparse
import io
import math
import re

"""NOTE ON SETTINGS: 
Best Hypothesis Text on the Training file 
n-gram order: 2
smoothing/backoff: used backoff
weight to the channel model: .8
"""

def parseArpaFile(arpafile,n): #parses arpafile (with n-grams up to 2) and returns loaded dictionaries

	sourceModel = open(arpafile, 'r')
	bigramDic = {'<s>': {}}
	unigramDic = {}
	sourceModel.next() #skips first two lines
	sourceModel.next()
	unigramNumber = sourceModel.next().split('=') #gets how many unigrams are in arpa file.
	unigramNumber = int(unigramNumber[1].strip('\n'))
	bigramNumber = sourceModel.next().split('=')
	bigramNumber = int(bigramNumber[1].strip('\n'))
	sourceModel.next()
	sourceModel.next()

	for x in range(0, unigramNumber):
		line = sourceModel.next().split('\t')
		unigramDic[line[1].strip()] = (float(line[0]), float(line[2].strip())) #tuple with unigramProb, and unigramBackOffProb
	
	sourceModel.next() #skips two lines separating 1-grams and 2-grams.
	sourceModel.next()

	if n == 2:
		for x in range(0, bigramNumber):
			line = sourceModel.next()
			line = line.split()
			word = line[1].strip()
			nextWord = line[2].strip()
			prob = float(line[0])
			if (word not in bigramDic): 
				bigramDic[word] = {}
			bigramDic[word][nextWord] = prob

		#check if it reiterates
	sourceModel.close()
	if n == 2:
		return bigramDic, unigramDic
	else:
		return {}, unigramDic #empty dictionary

def parseChannelModel(txtfile):

	model = {}
	channelModel = open(txtfile, 'r')

	letters = channelModel.next().strip('\n').split() #the first line - letters

	for line in channelModel:
		line = line.split()
		model[line[0]] = {}
		for i in range(1,len(line)):
			model[line[0]][letters[i-1]] = float(line[i])

	return model


def guessCorrectWord(word, prevWord, nextWord, weight):
	maxscore = ('none', float("-inf")) #initializes the max score - to be overwritten
	guessWord = ""
	for x in unigramDic:
		if re.match('.*[^a-zA-Z]+', x):
			continue #skip over any word in the dictionary with non-alphabetic characters
		
		#editDistance = calculateEditDistance(word, x)
		editDistance = shorterEditDistance(word, x)
		probC = editDistance * -1 * weight #multiply by weight

		if args.n == 1:
			probC += unigramDic[x][0]
			
		if args.n == 2:
			if prevWord in bigramDic and x in bigramDic[prevWord]:
				probC += bigramDic[prevWord][x]
			else:
				if prevWord not in unigramDic: #must put in <unk> probability
					prevWord = '<unk>'
				probC += unigramDic[prevWord][1] + unigramDic[x][0] #backoff(c-1) and P(c)

			if x in bigramDic and nextWord in bigramDic[x]:
				probC += bigramDic[x][nextWord]
			else:
				if nextWord not in unigramDic: #must put in <unk> probability
					nextWord = '<unk>'
				probC += unigramDic[x][1] + unigramDic[nextWord][0] #backoff(c-1) and P(c)

		if probC > maxscore[1]:
			maxscore = (x, probC) #replaces maxscore if new Probability is higher

	guessWord = maxscore[0]

	return guessWord

def calculateEditDistance(word, dicWord): 
	wordChars = list(word)
	dicWordChars = list(dicWord)
	matrix = [[0 for x in xrange(len(dicWordChars)+1)] for x in xrange(len(wordChars)+1)]
	matrix[0][0] = 0 #start
	for y in range(1, len(matrix[0])): #fill in deletion costs (1st row)
		matrix[0][y] = matrix[0][y-1] + -math.log(costsMatrix[dicWordChars[y-1]]['eps'],10)
		
	for x in range(1, len(matrix)): #fill in insertion costs (1st col)
		matrix[x][0] = matrix[x-1][0] + -math.log(costsMatrix['eps'][wordChars[x-1]],10)

	for x in range(1, len(matrix)):
		for y in range(1, len(matrix[0])):
			delCost = matrix[x][y-1] + -math.log(costsMatrix[dicWordChars[y-1]]['eps'],10) #left row

			insCost = matrix[x-1][y] + -math.log(costsMatrix['eps'][wordChars[x-1]],10) #up a row

			subCost = matrix[x-1][y-1] + -math.log(costsMatrix[wordChars[x-1]][dicWordChars[y-1]],10) #corner

			matrix[x][y] = min(delCost, insCost, subCost)

	editDistance = matrix[len(wordChars)][len(dicWordChars)]
	return editDistance

def shorterEditDistance(word, dicWord): 
	"""I implememented the Levenshtein_distance algorithm here, calculating edit distance faster than method above."""
	wordChars = list(word)
	dicWordChars = list(dicWord)
	row1 = [0 for x in xrange(len(dicWord) + 1)]
	row2 = [0 for x in xrange(len(dicWord) + 1)]
 
	row1[0] = 0

	for y in range(1,len(row1)): #initializes first row
		row1[y] = row1[y-1] - math.log(costsMatrix[dicWordChars[y-1]]['eps'],10) #deletes
 
	for x in range(0, len(wordChars)):

		row2[0] = row1[0]-math.log(costsMatrix['eps'][wordChars[x]],10) #insert 1 char
 
		for y in range(0,len(dicWordChars)): 
			subCost = row1[y] + -math.log(costsMatrix[wordChars[x]][dicWordChars[y]],10)
 			delCost = row2[y] + -math.log(costsMatrix[dicWordChars[y]]['eps'],10) #left row
			insCost = row1[y+1] + -math.log(costsMatrix['eps'][wordChars[x]],10) #up a row
			row2[y+1] = min(delCost, insCost, subCost)
 
		#copy row2 (current row) to row1 (previous row) for next iteration
		row1 = row2 * 1

	return row2[len(dicWord)]

if __name__=='__main__': 
	parser = argparse.ArgumentParser(description='test')
	parser.add_argument('-lmfile', help='arpa file', required=True)
	parser.add_argument('-n', type=int, help='number for n-gram (2, bi-gram is recommended)', required=True)
	parser.add_argument('-infile', help='file with spelling errors', required=True)
	parser.add_argument('-channel', help='file with edit distance probabilities', required=True)
	parser.add_argument('-o', help='specify an output file hypothesized correct spellings', required=True)
	parser.add_argument('-w', type=float, default=1.0, dest='weight', help='optional weight for channelModel:sourceModel ratio') 
	args = parser.parse_args()

	bigramDic, unigramDic = parseArpaFile(args.lmfile, args.n)
	costsMatrix = parseChannelModel(args.channel)
	words = []
	errorFile = open(args.infile, 'r')
	outfile = open(args.o, 'w')
	

	n = 100 #reading in first 100 lines of the training
	for x in range(0,n):
		line = errorFile.next()
		line = line.rstrip('\n').split()
		for y in line:
			words.append(y)

	for i, s in enumerate(words):
		if '<ERROR>' in s:
			index = i
			word = s[len('<ERROR>'):-len('</ERROR>')].strip() #strips of the Errors on each side
			prevWord = words[i-1].strip()
			nextWord = words[i+1].strip()
			outfile.write(guessCorrectWord(word,prevWord,nextWord,args.weight) + '\n')

	errorFile.close()
	outfile.close()
