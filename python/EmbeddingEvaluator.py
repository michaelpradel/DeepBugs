'''
Created on Jul 4, 2017

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
import numpy as np

sampling_rate_for_PCA = 0.01

if __name__ == '__main__':
    # arguments: <name to vector file>
    name_to_vector_file = join(getcwd(), sys.argv[1])
    with open(name_to_vector_file) as f:
        name_to_vector = json.load(f)
    
    names = []
    vectors = []
    for name, vector in name_to_vector.items():
        names.append(name)
        vectors.append(vector)
    
    # perform q few similarity queries
    queries = [ "ID:i", "ID:name", "ID:jQuery", "ID:counter", "ID:element", "LIT:true", "ID:msg", "ID:length"] # for AST-based
    kd_tree = KDTree(np.array(vectors))
    for query in queries:
        if query in name_to_vector:
            print(query + " has similar names:")
            query_vector = name_to_vector[query]
            _, neighbor_idxs = kd_tree.query(query_vector, k=6)
            closest_names = []
            for idx in neighbor_idxs:
                close_name = names[idx]
                if close_name != query:
                    print("  " + close_name)
    
    # show PCA
    pca_vectors = []
    pca_labels = []
    for idx, name in enumerate(names):
        if random.random() < sampling_rate_for_PCA:
            pca_labels.append(name)
            pca_vectors.append(vectors[idx])
    
    ipca = IncrementalPCA(n_components=2)
    reduced_vectors = ipca.fit_transform(pca_vectors)

    fig, ax = pyplot.subplots()
    x = reduced_vectors[:, 0]
    y = reduced_vectors[:, 1]
    ax.scatter(x, y)
    for idx, label in enumerate(pca_labels):
        escaped_label = re.escape(label)
        ax.annotate(escaped_label, (x[idx], y[idx]))
        
    pyplot.show()
    
    
