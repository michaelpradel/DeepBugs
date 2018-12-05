'''
Created on Mar 20, 2018

@author: Michael Pradel
'''

import sys
from gensim.models import Word2Vec
from sklearn.decomposition.incremental_pca import IncrementalPCA
from matplotlib import pyplot
import re

if __name__ == '__main__':
    # arguments: embedding_model_file
    model = Word2Vec.load(sys.argv[1])
    
    queries = [ "ID:i", "ID:name", "ID:jQuery", "ID:counter", "ID:element", "LIT:true", "ID:msg", "ID:length", "ID:nextSibling", "ID:toLowerCase", "ID:wrapper", "ID:width", "ID:getWidth"]
    
    for query in queries:
        results = model.wv.most_similar(positive=[query])
        print("\\begin{tabular}{rl}")
        print("  \\toprule")
        print("  \\multicolumn{2}{c}{\\emph{\\textbf{"+query+"}}} \\\\")
        print("  \\midrule")
        print("  Simil. & Identifier \\\\")
        print("  \\midrule")
        for (other_id, simil) in results:
            escaped = other_id.replace("_", "\\_")
            print("  "+str(round(simil, 2))+" & "+escaped+" \\\\")
        print("  \\bottomrule")
        print("\end{tabular}")
        print()
    
    
    # show PCA
    pca_queries = [ "ID:wrapper", "ID:container", "ID:msg", "ID:alert", "ID:list", "ID:seq", "ID:lst", "ID:list", "LIT:error" ]
    pca_vectors = []
    pca_labels = []
    for _, name in enumerate(pca_queries):
        if name.startswith("LIT:"):
            print_name = "\"" + name.replace("LIT:", "") + "\""  # assumes string literals only
        else:
            print_name = name.replace("ID:", "")
        pca_labels.append(print_name)
        pca_vectors.append(model.wv[name])
    
    ipca = IncrementalPCA(n_components=2)
    reduced_vectors = ipca.fit_transform(pca_vectors)

    fig, ax = pyplot.subplots()
    x = reduced_vectors[:, 0]
    y = reduced_vectors[:, 1]
    ax.scatter(x, y)
    for idx, label in enumerate(pca_labels):
        #escaped_label = re.escape(label)
        ax.annotate(label, (x[idx], y[idx]))

    pyplot.show()
    
