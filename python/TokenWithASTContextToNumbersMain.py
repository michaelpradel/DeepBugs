from multiprocessing import Pool
from itertools import product
from TokenWithASTContextToNumbers import *

kept_main_tokens = 10000
kept_context_tokens = 1000


nb_processes = 30

if __name__ == '__main__':
    # arguments: <list of .json files with tokens and contexts> 
    if len(sys.argv) > 1:
        filepaths = sys.argv[1:]
    else:
        filepaths = ['idsLitsWithASTFamily_1518650188081.json', 'idsLitsWithASTFamily_1518650188168.json']
    
    all_raw_data_paths = list(map(lambda f: join(getcwd(), f), filepaths))
    total_files = len(all_raw_data_paths)
    print("Total files: "+str(total_files))

    if total_files < nb_processes:
        nb_processes = total_files 

    pool = Pool(processes=nb_processes)
    chunksize = round(len(all_raw_data_paths) / nb_processes)
    counters = pool.map(count_tokens, chunks(all_raw_data_paths, chunksize))
    # counters = list(sum(counters, ()))


    # merge counters that were gathered in parallel
    print("Merging counters...")
    all_main_tokens = Counter()
    all_context_tokens = Counter()
    for main_tokens, context_tokens in counters:
        all_main_tokens.update(main_tokens)
        all_context_tokens.update(context_tokens)
    print("Done with merging counters")
    
    # analyze histograms
    print("Unique main tokens: " + str(len(all_main_tokens)))
    print("  " + "\n  ".join(str(x) for x in all_main_tokens.most_common(20)))
    analyze_histograms(all_main_tokens)
    print()
    print("Unique context tokens: " + str(len(all_context_tokens)))
    print("  " + "\n  ".join(str(x) for x in all_context_tokens.most_common(20)))
    analyze_histograms(all_context_tokens)
    
    # replace infrequent tokens w/ placeholder and write number-encoded tokens + contexts to files
    frequent_main_tokens = frequent_tokens(all_main_tokens, kept_main_tokens)
    frequent_context_tokens = frequent_tokens(all_context_tokens, kept_context_tokens)
    
    save_token_numbers(frequent_main_tokens, "main")
    save_token_numbers(frequent_context_tokens, "context")
    
    print("Encoding data and written it to files...")
    pool = Pool(processes=nb_processes)
    pool.starmap(encode_tokens_with_context, product(chunks(all_raw_data_paths, chunksize), [(frequent_main_tokens, frequent_context_tokens) for i in range(chunksize)]))
    
    print("Done")
        
        