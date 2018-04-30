'''
Created on Mar 20, 2018

@author: Michael Pradel
'''

import sys
from gensim.models import Word2Vec

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
    