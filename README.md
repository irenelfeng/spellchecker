README for spellchecker
Author: Irene Feng. 10/20/2014

Description: using edit distance algorithm, guesses correct words spelled for incorrect words. 

Input: -lmfile ARPA wordbank file with probabilities 
		-n Number of n-grams to calculate probabilities for words before and after (recommended: 2)
		-infile file with errors marked as "<ERROR>mispelled_word_here</ERROR>" (program reads first 100 lines)
        [-channel CHANNEL] tab or space-separated file of conversion matrix for each letter.
        [-w WEIGHT] optional channelModel:sourceModel ratio. If want more weight on the channel, >1, if more weight on sourceModel, <1.
        [-o O]

Sample Usage: python spellcheck.py -lmfile guten_brown_reuters_state.arpa -infile penntreebank.test -n 2 -channel feng-confusion.txt -o checked_out.txt -w .8
	- please allow 30+ minutes for program to run. 

Special Considerations: 
If using penntreebank.test as infile, you may compare the output file with penntreebank.test.gold for results. To test results, change weight ratios, n-grams, or channel file. 
The channel file should be a 28*28 matrix in which 27 letters are specified (including eps, a "deletion" character); First row and column specify letters for readability. 
	- each row should add up to probability 1. Each cell corresponds to the probability letter @ is actually meant to be letter &. 