#!/usr/bin/env python2

# Claatu::annotate_subtree -Subtree annotation
#Copyright (C) 2015  Christopher A. Gaulke
#author contact: gaulkec@science.oregonstate.edu
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program (see LICENSE.txt).  If not, see
#<http://www.gnu.org/licenses/>

####################
#   ___________    #
#  |           |   #
#  | |==(*)==| |   #
#   |         |    #
#    |_______|     #
#                  #
####################

#########################
#                       #
#  annotate_subtree.py  #
#                       #
#########################



import dendropy
import argparse
import random
import re

parser = argparse.ArgumentParser()
parser.add_argument("biom_fp", help="file path to the biom table to be used.")
parser.add_argument("tree_fp", help="file path to the tree to be used.")
parser.add_argument("out_fp", help="file path and suffix for out files. No extension needed.")
#parser.add_argument("node_list_fp", help="file path to the node list for the nodes that make subtrees to be annotated.")
parser.add_argument("-s", default = None, help="A list of species (one per line) used to restrict analyses.")
args = parser.parse_args()

biom_fp = args.biom_fp
tree_fp = args.tree_fp # should be prepped tree from prep tree
out_fp = args.out_fp
#node_list_fp = args.node_list_fp
species_fp = args.s

tree1 = dendropy.Tree.get(path = "{0}".format(tree_fp), schema = "newick")

#this needs work could require a specific mapping file of colors to samples but would rather not

my_colors =["#283435",
"#75E43A",
"#D54BD8",
"#E74618",
"#74E6D6",
"#D3AAD3",
"#E4C338",
"#8B3047",
"#896124",
"#534C96",
"#5C9B67",
"#DC3F93",
"#688694",
"#D88E8A",
"#DAD683",
"#9B3621",
"#55942C",
"#8965D8",
"#D8395C",
"#592A58",
"#62DE9A",
"#D281D4",
"#6FC5DF",
"#C4E0B6",
"#29401B",
"#82635D",
"#718ADE",
"#953688",
"#D87228",
"#BFB0A3",
"#C6DC40",
"#9D9B3C",
"#CA688C",
"#394365",
"#578FC0",
"#436C5F",
"#8F7099",
"#C1A575",
"#64261B",
"#CA8054",
"#61D45E",
"#D89C39",
"#ABDC7B",
"#E2695F",
"#5EADA3",
"#596A2D",
"#DB3E33"]

def BiomTabParser(biom):
	"This function parses a biom file (closed ref OTUS) in tab delim format and creates a dictionary of samples by OTU by count"
	"""Columns of the table should be samples and rows should be OTUs
	should ignore lines until matching a line #OTU"""
	#set pattern
	my_pattern = re.compile('\#OTU')
	#read in biom table line by line
	biom_dict = {}
	my_header = ""
	with open(biom) as f:
		for line in f:
			if re.match('#', line):
				if re.match(my_pattern, line):
					my_header = line
					my_header = my_header.strip('#')
					my_header = my_header.rstrip()
					my_header = my_header.split('\t')
					for i in range(1,len(my_header)):
						biom_dict[my_header[i]] = {}
			else:
				line = line.rstrip()
				temp = line.split("\t")
				for i in range(1,len(temp)):
					biom_dict[my_header[i]][temp[0]] = temp[i]
	return biom_dict

def MakeColorDict(biom_dict, species_fp):
	"make a lookup dict for colors that will be used to color tips"
	species_cols = []
	col_dict = {}
	if species_fp == None:
		my_len = len(biom_dict)
		species_cols = random.sample(my_colors,my_len)
		for key in biom_dict.keys():
			col_dict[key] = species_cols.pop()
	else:
		species = []
		with open(species_fp) as f3:
			for line in f3:
				line = line.strip()
				species.append(line)
		my_len = len(species)
		species_cols = random.sample(my_colors,my_len)
		for sp in species:
			col_dict[sp] = species_cols.pop()
	return col_dict

def MakeDescendantDict(tree, species_fp, biom_dict):
	"Makes a dictionary of all tips that descend from the root of the subtree. Dictionary is tip by species"
	species = []
	des_dict = {}
	tips = tree.leaf_nodes()

	if species_fp == None:
		for key in biom_dict:
			species.append(key)
	else:
		with open(species_fp) as f2:
			for line in f2:
				line = line.strip()
				species.append(line)
	for tip in tips:
		tip = str(tip.taxon)
		tip = tip.strip('\'')
		if tip in biom_dict[biom_dict.keys()[0]].keys():
			des_dict[tip] = {}
			for s in species:
				if float(biom_dict[s][tip]) > 0:
					des_dict[tip][s] = 1
				else:
					des_dict[tip][s] = 0
		else:
			continue
	return des_dict

def MakeTipMetaData(des_dict, col_dict):
	"Assigns metadata based on the presence of only one species at a give tip"
	ann_dict = {}
	for tip in des_dict:
		color = ""
		set = ""
		count = 0
		for sp in des_dict[tip]:
			if des_dict[tip][sp] == 1:
				count += 1
				set = sp
			else:
				continue
		#print "%s\t%s" %(tip, count)
		if count > 1: #look in here for bug
			color = "black"
		elif count == 1:
			color = col_dict[set]
		else:
			color = "black"
		ann_dict[tip] = color
	return ann_dict

def MakeTipHostTaxDict(des_dict):
	"makes a list of host taxon present at each tip. These data can be used to make annotation files"
	host_dict = {}
	for tip in des_dict:
		sp_list = []
		for sp in des_dict[tip]:
			if des_dict[tip][sp] == 1:
				sp_list.append(sp)
			else:
				continue
		host_dict[tip] = sp_list
	return host_dict

def MakeCodeFile(ann_dict, out_fp):
	"Makes code files for input into scripttree"
	code_file = "%s.%s" %(out_fp, "code")
	with open(code_file, 'w+') as o1:
		print >> o1, "tree -height 1500 -width 800 -columns 2 -conformation 1 -font {Times 6 italic}"
		for tip in ann_dict:
			print >> o1, "query_newick -ql {%s} -hi {-o {lfg sfg} -c %s}" %(tip, ann_dict[tip])
	return None

def MakeAnnotationFile(host_dict, out_fp):
	"Makes an annotation file for tree"
	ann_file = "%s.%s" %(out_fp, "annotations")
	with open(ann_file, 'w+') as o2:
		for tip in host_dict:
			if len(host_dict[tip]) == 0:
				print >> o2, "%s accession {%s} hosts {%s}" %(tip,tip,'None')
			else:
				print >> o2, "%s accession {%s} hosts {%s}" %(tip,tip,','.join(host_dict[tip]))

	return None

biom_dict= BiomTabParser(biom_fp)

#col_dict = MakeColorDict(biom_dict, species_fp)
#00FF00 is lime green
col_dict = {
	'Chimp1'     : 'red',
	'Chimp2'     : 'red',
	'Saki'       : 'yellow',
	'BaboonW'    : '#00FF00',
	'BaboonSTL'  : '#00FF00',
	'RTLemur'    : 'purple',
	'GorillaSTL' : 'blue',
	'Orang1'     : 'green',
	'Colobus'    : 'pink',
	'BlackLemur' : 'aqua',
	'Callimicos' : 'orange',
}
#print col_dict
des_dict = MakeDescendantDict(tree1, species_fp, biom_dict)

ann_dict = MakeTipMetaData(des_dict, col_dict)
MakeCodeFile(ann_dict, out_fp)
host_dict = MakeTipHostTaxDict(des_dict)
MakeAnnotationFile(host_dict, out_fp)
