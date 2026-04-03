class ContextBuilder:

    def build(self, docs):

        blocks = []
        sources = []
        #defining headers for AI
        for i, doc in enumerate(docs, start=1):
            block = (
                f"[Source {i} | Chunk ID: {doc['chunk_id']} | "
                f"Year: {doc['year']} | Type: {doc['type']}]\n"
                f"{doc['text']}\n"
            )
            blocks.append(block)
            #tracking the sources for the UI
            sources.append({
                "source_number": i,
                "chunk_id": doc["chunk_id"],
                "original_source": doc["source"]
            })

        return {
            "context": "\n\n".join(blocks),
            "sources": sources
        }