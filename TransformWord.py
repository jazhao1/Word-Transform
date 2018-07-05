import editdistance
from functools import total_ordering
from queue import *
import pickle

@total_ordering
class Node(object):
	def __init__(self, word):
		self.word = word
		self.connections = {}
		self.distance = Node.distance
		self.prev = None


	def length(self):
		return len(self.word)

	def add_connection(self, word, connection_type):
		self.connections[word.word] = [connection_type, word]


	def get_connection_type(self, word):
		return self.connections[word][0]

	def get_connected_node(self, word):
		return self.connections[word][1]


	def reset_distance(self):
		self.distance = float("inf")
		self.prev = None


	def __eq__(self, other):
		if other == None:
			return False
		return self.distance == other.distance

	def __ne__(self, other):
		return self.distance != other.distance

	def __lt__(self, other):
		return self.distance < other.distance

	def __repr__(self):
		return self.word

	def __str__(self):
		return self.word
		
def to_node(word_lst):
	rv = {}
	for word in word_lst:
		rv[word.upper()] = Node(word.upper())
	return rv


def is_acronym(word1, word2):
	return sorted(word1) == sorted(word2)


def build_network(words):
	all_words_map = to_node(words)                #{word:node}
	all_nodes = list(all_words_map.values())      #[node]

	while len(all_nodes) != 0:
		curr_node =	all_nodes.pop()
		for other_node in all_nodes:
			if editdistance.eval(curr_node.word, other_node.word) == 1 :
				if curr_node.length() > other_node.length():
					curr_node.add_connection(other_node, "delete")
					other_node.add_connection(curr_node, "add")

				elif curr_node.length() < other_node.length():
					curr_node.add_connection(other_node, "add")
					other_node.add_connection(curr_node, "delete")
				else:
					curr_node.add_connection(other_node, "swap")
					other_node.add_connection(curr_node, "swap")

			elif is_acronym(curr_node.word, other_node.word):
				curr_node.add_connection(other_node, "acronym")	
				other_node.add_connection(curr_node, "acronym")	
	return all_words_map

def transform(costs, start, end, network):

	start = start.upper()
	end = end.upper()

	if  start not in network or end not in network:
		return -1

	edge_weights = {"add" : costs[0],
					"delete" : costs[1],
					"swap" : costs[2],
					"acronym" : costs[3]}

	for node in network.values():
		node.reset_distance()

	start_node = network[start]
	start_node.distance = 0

	pq = PriorityQueue() 
	for node in network.values():
		pq.put(node)

	while not pq.empty():
		curr_node = pq.get()
		curr_node_dist = curr_node.distance #dist(u)
		for adj_word in curr_node.connections:
			adj_node = curr_node.get_connected_node(adj_word)
			adj_node_dist = adj_node.distance #dis(v)

			edge_weight = edge_weights[curr_node.get_connection_type(adj_word)]

			if adj_node_dist > curr_node_dist + edge_weight:
				adj_node.distance = curr_node_dist + edge_weight
				adj_node.prev = curr_node

		if curr_node.word == network[end].word:
			break

	end_node = network[end]

	if end_node.prev == None:
		return -1

	word_lst = []
	curr_node = end_node 

	while (curr_node.word != start):
		word_lst = [curr_node.word] + word_lst

		curr_node = curr_node.prev

		if len(word_lst) > 15:
			break
	rv = [start] + word_lst
	return len(rv), rv


enlgish_words = open("wordList.txt", 'r')
enlgish_words_list = [line[:-1] for line in enlgish_words.readlines()]

network = build_network(enlgish_words_list)

print(transform((1,3,1,5), "health", "hents", network))

print(transform((1,9,1,3), "team", "mate", network))
print(transform((7,1,5,2), "ophthalmology", "glasses", network))

