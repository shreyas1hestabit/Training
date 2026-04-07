def reciprocal_rank_fusion(dense_results, bm25_results, k=60): #we have used 60 and not any other because 60 acts as a goldilock no which is neither too small (which leads to large diff in rank1 and rank2 scores) and nor too large (by using which the diff between two scores is almost negligible)
    scores={} #scores final unified result for every chunk.
    #processing faiss results
    for rank, (idx, _) in enumerate(dense_results): #enumerate gives us the rank 0,1,2...
        scores[idx]=scores.get(idx,0)+1/(k+rank+1) #idx -> chunk's id number
        #scores.get(idx,0) -> if the chunk is already seen it adds new score to the old one.
    for rank,(idx,_) in enumerate(bm25_results):
        scores[idx] = scores.get(idx,0)+1/(k+rank+1)
    return sorted(scores.keys(),key=lambda x: scores[x], reverse=True) #sorts all the ids based on their newly calculated total scores (highest to lowest)