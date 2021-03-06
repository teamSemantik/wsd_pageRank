#!/usr/bin/python
# Python 2.7

import time
import Onti
from Word import Word
from Node import Node
from Graph import Graph
from Tree import Tree
import Evaluator
from Data import Data
from collections import deque
import sys
import re
import os
import OntoNodesSentenceExtractor

class WordNetSearcher(object):
    indexFiles = ["data/index.noun", "data/index.verb", "data/index.adv", "data/index.adj"]
    dataFiles = ["data/data.noun", "data/data.verb", "data/data.adv", "data/data.adj"]
    #input: list of word objects
    def __init__(self, inputWords):
        self.inputWords = [] #words of one input sentence
        for word in inputWords:
            self.inputWords.append(Word(word))
        self.raw_trees = [] #contains all subtrees
        self.deadSentence = False
        self.nodes = set() #this contains all nodes that are in all subtrees
        self.graph_nodes = set() #here the final graph is created
        self.root_nodes = set() #this is the set of all root nodes
        self.combinations = []

    @staticmethod
    def readIndexFiles():
        for indexFile in WordNetSearcher.indexFiles:
            file = open(indexFile, 'r')
            lines = file.readlines()
            for line in lines:
                if not line.startswith("  "):
                    elements = line.strip(" \t\n\r").split(" ")
                    WordNetSearcher.findAllSynsetsForIndexLine(elements)

    @staticmethod
    def findAllSynsetsForIndexLine(lineAsList):
        lemma = lineAsList[0]
        pnt_count = lineAsList[3]
        dict = Onti.indexDictionary
        indexOfFirstSynset = 3 + int(pnt_count) + 3 # pnt_count is at index 3 + relations + 2 for synset count and target_synset count + 1 -> first index of synset
        synsets = set(lineAsList[indexOfFirstSynset:len(lineAsList)])
        if lemma in dict:
            dict[lemma].update(synsets)
        else:
            dict.setdefault(lemma, synsets)
    
    @staticmethod
    def readDataFiles():
        for dataFile in WordNetSearcher.dataFiles:
            file = open(dataFile, 'r')
            lines = file.readlines()
            for line in lines:
                if not line.startswith("  "):
                    line = line.strip(" \t\n\r")
                    WordNetSearcher.findAllSemanticRelationsForSynset(line)
    
    @staticmethod
    def findAllSemanticRelationsForSynset(lineAsString):
        synset = lineAsString[0:8]
        #find all 8 digit numbers in the line that are not the synset itself
        semRelations = set([m.strip() for m in re.findall(" [0-9]{8} ", lineAsString) if m != synset])
        dummy = []
        for semRelation in semRelations:
            semRelation = semRelation.strip()
            dummy.append(semRelation)
        dict = Onti.dataDictionary
        dict.setdefault(synset, set(dummy))

    def getMeaningsForWord(self, word):
        lemma = word.name
        dict = Onti.indexDictionary
        if lemma in dict:
            for synsetString in dict[lemma]:
                newNode = Node.createNode(synsetString)
                word.synsets.add(newNode)
                self.root_nodes.add(newNode)
                self.nodes.add(newNode)
                
        else:
            word.DeadWord = True
            #sys.stderr.write("This word is empty or was not found in WordNet 2.1")
            #print
    
    def createTree(self, wurzel):
        queue = [wurzel]
        this_iteration = []
        results = [wurzel]
        iterator = 0
        while iterator < 3:
            iterator += 1
            for node in queue:
                neighbouries = set()
                for neighbour in Onti.dataDictionary[node.name]:
                    neighbour_node = Node.createNode(neighbour)
                    self.nodes.add(neighbour_node)
                    neighbour_node.neighbours.add(node)
                    neighbouries.add(neighbour_node)
                    if not neighbour_node in results:
                        results.append(neighbour_node)
                        this_iteration.append(neighbour_node)
                        neighbour_node.tree_dictionary[wurzel] = [[node], iterator]
                    else:
                        if not wurzel.name == neighbour_node.name:
                            if neighbour_node.tree_dictionary[wurzel][1] == iterator: #diese vier zeilen braucht man um ggf das tree_dictionary um node zu erweitern
                                neighbour_node.tree_dictionary[wurzel][0].append(node)
                node.neighbours = neighbouries
            queue = this_iteration
            this_iteration = []
        subtree = Tree(results)
        self.raw_trees.append(subtree)
        
        
                
    def createTrees(self):
        # should create a tree for each synset
        #nodes = []
        for word in self.inputWords:
            self.getMeaningsForWord(word)
            synsetsForWord = word.synsets
            # for sense in word.synsets:
                # word_bag.append(sense)
            # for node in self.root_nodes:
                # for other_node in node.tree_dictionary.keys():
                    # if not other_node in word_bag:
                        # print "yummi"
            for root in synsetsForWord:
                self.root_nodes.add(root)
                root.neighbours = set(Onti.dataDictionary[root.name])
                for neighbour in root.neighbours:
                    neighbour = Node.createNode(neighbour)
                    neighbour.neighbours.add(root)
                self.createTree(root)
    
    
    def constructGraph(self, d):
        for node in self.nodes:
            for other_node in node.tree_dictionary.keys():
                if other_node not in self.root_nodes:
                    node.tree_dictionary.pop(other_node)
        count = 0
        for node in self.nodes: #search for all nodes that will belong to the graph
            if len(node.tree_dictionary.keys())>1: #this node only creates a new path if it is close enough to at least two root_nodes
                dicti = list(node.tree_dictionary.keys())
                # dicti.remove(node)
                for key_iter1 in range(len(dicti)-1):
                    for key_iter2 in range(key_iter1+1, len(dicti)):
                        key1 = dicti[key_iter1]
                        key2 = dicti[key_iter2]
                        first_word = None
                        different_words = False
                        for word in self.inputWords: #all that is coming in the next 15 lines is to check if two synsets belong to the same word. if that is the case, their path is not added to the graph
                            for synset in word.synsets:
                                if synset == key1:
                                    if first_word == None:
                                        first_word = word
                                        break
                                    else:
                                        different_words = True
                        if different_words == False:
                            if not key2 in first_word.synsets:
                                for word in self.inputWords:
                                    if word != first_word:
                                        for synset in word.synsets:
                                            if synset == key2:
                                                different_words = True
                            else:
                                different_words = True
                        
                        if different_words == True:
                            if not [key1, key2] in self.combinations:
                                self.graph_nodes.add(node)
                                self.combinations.append([key1, key2])
                                #print key1, key2
                                present_node = node
                                while not present_node == key1: #walk to first root, collect the nodes
                                    
                                    present_node = present_node.tree_dictionary[key1][0][0]
                                    self.graph_nodes.add(present_node)
                                present_node = node
                                while not present_node == key2: #walk to second node
                                    present_node = present_node.tree_dictionary[key2][0][0]
                                    self.graph_nodes.add(present_node)
        for node in self.graph_nodes: #delete all nodes and connections that don't belong to the graph
            neighbours_nodes = list(node.neighbours)
            for sub_node in node.neighbours:
                if sub_node not in self.graph_nodes:
                    neighbours_nodes.remove(sub_node)
            node.neighbours = set(neighbours_nodes)
        graph = Graph(self.inputWords, self.root_nodes, self.graph_nodes, d)
        # for node in graph.node: #delete all neighbours in tree_dicionary that are not in the graph
            # for neighbour in node.tree_dictionary.keys():
                # if neighbour not in self.tree_nodes:
                    # tree_dictionary.pop(neighbour)
        return graph
                                

