def reciprocal_rank_fusion(dense_results, bm25_results, k=60):
    scores={}

    for rank, (idx, _) in enumerate(dense_results):
        scores[idx]=scores.get(idx,0)+1/(k+rank+1)
    for rank,(idx,_) in enumerate(bm25_results):
        scores[idx] = scores.get(idx,0)+1/(k+rank+1)
    return sorted(scores.keys(),key=lambda x: scores[x], reverse=True)