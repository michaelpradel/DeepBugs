'''
Created on Oct 24, 2017

@author: Michael Pradel
'''

import sys
import json
from os.path import join
from os import getcwd
from sklearn.decomposition.incremental_pca import IncrementalPCA
from matplotlib import pyplot
import re
import random
from scipy.spatial.kdtree import KDTree
from scipy.spatial.distance import cosine 
import numpy as np
import resource  # @UnresolvedImport
from dca.Util import Util

sampling_rate_for_PCA = 0.01

util = Util()

class RawDataReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths
         
    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                items = json.load(file)
                for item in items:
                    yield item

if __name__ == '__main__':
    # arguments: <location to vector file> <idsListWithContext.json files>
    
    giga_byte = 1024 * 1024 * 1024
    max_bytes = 8 * giga_byte   
    resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
    
    location_to_vector_file = join(getcwd(), sys.argv[1])
    with open(location_to_vector_file) as f:
        location_to_vector = json.load(f)
        
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[2:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)
    
    location_to_name = dict()
    name_to_locations = dict()
    reader = RawDataReader(data_paths)
    for token_with_context in reader:
        name = token_with_context["token"]
        location = token_with_context["location"]
        location_to_name[location] = name
        if name in name_to_locations:
            locations = name_to_locations[name]
        else:
            locations = []
            name_to_locations[name] = locations
        locations.append(location)
    
    # prepare data structures for efficient similarity queries
    names = []
    vectors = []
    for location, vector in location_to_vector.items():
        if location in location_to_name: # some locations have no vectors because their names are infrequent
            name = location_to_name[location]
            names.append(name)
            vectors.append(vector)
    print("Name-vector pairs: " + str(len(names)))

    # inspect similarities of locations with same name
    remaining_samples = 20 
    print("\n")
    print("In-group simil, Out-group simil, Factor, #Vectors, Token")
    for name, locations in name_to_locations.items():
        if len(locations) > 5:
            vector_group = list(map(lambda location: location_to_vector[location], locations))
            # compute avg. pairwise similarity in group with same name
            in_group_simil = util.in_group_similarity(vector_group)
            
            # compute avg. similarity to some other vectors
            out_group_simil = util.out_group_similarity(vector_group, vectors)
            
            factor = in_group_simil / out_group_simil
            print(str(round(in_group_simil, 4))+", "+str(round(out_group_simil, 4))+", "+str(round(factor, 2))+", "+str(len(vector_group))+", "+name)
            remaining_samples -= 1
            if remaining_samples is 0:
                break
            
            
#                 
# 
#     names = []
#     vectors = []
#     for name, vector in name_to_vector.items():
#         names.append(name)
#         vectors.append(vector)
#     
#     # perform q few similarity queries
#     queries = [ "i", "name", "jQuery", "counter", "element", "true", "msg", "length"] # for token-based
#     queries = [ "ID:i", "ID:name", "ID:jQuery", "ID:counter", "ID:element", "LIT:true", "ID:msg", "ID:length"] # for AST-based
#     kd_tree = KDTree(np.array(vectors))
#     for query in queries:
#         if query in name_to_vector:
#             print(query + " has similar names:")
#             query_vector = name_to_vector[query]
#             _, neighbor_idxs = kd_tree.query(query_vector, k=6)
#             closest_names = []
#             for idx in neighbor_idxs:
#                 close_name = names[idx]
#                 if close_name != query:
#                     print("  " + close_name)
#     
#     # show PCA
#     pca_vectors = []
#     pca_labels = []
#     for idx, name in enumerate(names):
#         if random.random() < sampling_rate_for_PCA:
#             pca_labels.append(name)
#             pca_vectors.append(vectors[idx])
#     
#     ipca = IncrementalPCA(n_components=2)
#     reduced_vectors = ipca.fit_transform(pca_vectors)
# 
#     fig, ax = pyplot.subplots()
#     x = reduced_vectors[:, 0]
#     y = reduced_vectors[:, 1]
#     ax.scatter(x, y)
#     for idx, label in enumerate(pca_labels):
#         escaped_label = re.escape(label)
#         ax.annotate(escaped_label, (x[idx], y[idx]))
#         
#     pyplot.show()
    
    
