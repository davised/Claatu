#!/usr/bin/env python2

# Claatu::prep_tree -Prepares tree for use in Claatu 
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

##################
#                #
#  prep_tree.py  #
#                #
##################


import dendropy
import re
import os
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("tree_fp", help="file path to the tree that is to be modified")
parser.add_argument("-nbs", help="Pass to indicate that the tree doesn't contain bootstraps", action="store_true")
parser.add_argument("-up_bi", help="Pass to indicate you wish to update bipartitions", action="store_true")
parser.add_argument("-mid", help="Pass to indicate you wish to midpoint root. Warning using this option will consume large amounts of RAM and time! For 60,000 tips it can cosume > 250 Gb of ram and run for days.", action="store_true")
args = parser.parse_args()
parser.set_defaults(nbs=False)
parser.set_defaults(up_bi=False)
parser.set_defaults(mid=False)
wd = os.getcwd()
up_bi = args.up_bi
nbs = args.nbs
mid = args.mid

####
#Prep Tree
####

tree_fp = args.tree_fp
tree_type = "newick"

#might want to save bootstraps for latter
#this labels tips as tip taxon (i.e., OTU or species name)

def PrepTree(tree_fp, tree_type, bs=nbs):
	#tree_fp: file path to tree
	#tree_type: type of tree to be processed (only newick type is currently supported)
	#bs: Boolean, does the tree contain bootstrap values
	
	#import tree object
	tree1 = dendropy.Tree.get_from_path("{0}".format(tree_fp), schema="{0}".format(tree_type))
	
	#make node bootstrap dictionary 
	bootstraps = {}
	bootstraps['root'] = 0.0
	if mid==True:
		if up_bi==True:
			#print("up_bi=T")
			tree1.reroot_at_midpoint(update_bipartitions=True)
		else:
			#print("up_bi=F")
			tree1.reroot_at_midpoint(update_bipartitions=False)
	
	k = 1
	if bs==True:	
		#name nodes
		node_it = tree1.preorder_node_iter()
		for i in node_it:
			if i.label == None:
				if hasattr(i, 'taxon') and i.taxon != None: # (i.e., a tip)
					i.label = i.taxon.label
				else:
					if hasattr(i, '_parent_node') and i._parent_node != None: #new
						j = str(k)
						mlabel = "{0}{1}".format("node", j)
						#print(mlabel)
						bootstraps[mlabel] = i.label
						i.label = mlabel
						#i.label = "{0}{1}".format("node", j) 
						k = k + 1
					else:
						i.label = "root"
	else:
		#name nodes
		node_it = tree1.preorder_node_iter()
		for i in node_it:
			if i.label != None:
				if hasattr(i, 'taxon') and i.taxon != None: # (i.e., a tip)
					i.label = i.taxon.label
				else:
					if hasattr(i, '_parent_node') and i._parent_node != None: #new
						j = str(k)
						mlabel = "{0}{1}".format("node", j)
						bootstraps[mlabel] = i.label
						i.label = mlabel
						#i.label = "{0}{1}".format("node", j) 
						k = k + 1
					else:
						i.label = "root"
			else:
				if hasattr(i, 'taxon') and i.taxon != None: # (i.e., a tip)
					i.label = i.taxon.label
				else:
					if hasattr(i, '_parent_node') and i._parent_node != None: #new
						j = str(k)
						mlabel = "{0}{1}".format("node", j)
						bootstraps[mlabel] = i.label
						i.label = mlabel
						#i.label = "{0}{1}".format("node", j) 
						k = k + 1
					else:
						i.label = "root"
	#print(bootstraps)
	f = open("bootstraps_prep_tree.txt", 'w')
	for key, value in bootstraps.iteritems():
		f.write('%s\t%s\n' % (key, value))
	f.close()
	return tree1

#def PrepTree(tree_fp, tree_type):
#	#import tree object
#	tree1 = dendropy.Tree.get_from_path("{0}".format(tree_fp), schema="{0}".format(tree_type))
#	
#	#name nodes
#	node_it = tree1.preorder_node_iter()
#	k = 1
#	for i in node_it:
#		if i.label == None:
#			if hasattr(i, 'taxon') and i.taxon != None: # (i.e., a tip)
#				i.label = i.taxon.label
#			else:
#				if hasattr(i, '_parent_node') and i._parent_node != None: #new
#					j = str(k)
#					i.label = "{0}{1}".format("node", j) 
#					k = k + 1
#				else:
#					i.label = "root"
#	return tree1



####
#Make node ancestor lookup table
####

def AncestorLookup(tree):
	"This function makes a dictionary of the ancestors of each node"
	node_it = tree.preorder_node_iter()	
	tip_ancestors = {}
	#make an iterator for each node and append each ancestor to a list(vals)
	for node in node_it:
		ancest_it = node.ancestor_iter(inclusive=False) #get iter for all ancestors	
		vals = []
		for ancestor in ancest_it: 		 
			vals.append(str(ancestor.label))
		tip_ancestors[str(node.label)] = vals
	return tip_ancestors



tree1 = PrepTree(tree_fp, tree_type)  	

ancestor_lookup_dict = AncestorLookup(tree1)

tree1.write_to_path(
        'new_prepped_tree.tre',
        'newick')


