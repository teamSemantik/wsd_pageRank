# import

class Lemma(object):
	
	def __init__(self, sentence, word_in_sentence, word, wordtype, word_override, sense):

	# Number of the sentence the word is in -> INT
		self.sentence = int(sentence)
	# Number of the word of the sentence the word is in -> INT
		self.word_in_sentence = int(word_in_sentence)
	# Word itself, if no override is given -> STR
		if word_override == "-":
			self.word = str(word)
		else:
			self.word = str(word_override)
	# Type of Word, if NN , ADJ or V - otherwise <other> to differentiate -> STR
		if wordtype in "NN_NNP_NNS":
			self.wordtype = "n"
		if wordtype in "VBG_VBN_VBP_VBZ":
			self.wordtype = "v"
		if wordtype in "JJ":
			self.wordtype = "a"
		if wordtype in "RB":
			self.wordtype = "r"
		if wordtype not in 'NN_NNP_NNS_JJ_VBG_VBN_VBP_VBZ_RB':
			self.wordtype = "other"
		
	# Annotated Sense of the word, if existent - otherwise <0> to differentiate -> INT
		if sense != "-" and "." not in sense:
			self.sense = int(sense)
		elif "." in sense:
			dummy_split = sense.split(".")
			self.sense = int(dummy_split[0])
		else:
			self.sense = 0
	
	# return value stuff
	def returnSentenceNR(self):
		# INT
		return self.sentence
	def returnWordNR(self):
		# INT
		return self.word_in_sentence
	def returnWord(self):
		# STR
		return self.word
	def returnWordtype(self):
		# STR
		return self.wordtype
	def returnSense(self):
		# INT
		return self.sense
	
	# return all data at once in a list
	def returnLemma(self):
		return [self.sentence, self.word_in_sentence, self.word, self.wordtype, self.sense]