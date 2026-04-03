#we are using sliding window chunking. it breaks a long string of text into smaller, manageable pieces (chunks) while ensuring that the end of one chunk repeats at the start of the next.
def create_chunks(text,chunk_size=500,overlap=100): #it prepares the logic for the window to slide accross the text
    #text is the long string of data we want to break
    #chunk size is the max length of each piece
    #overlap defines how many same characters will be there in two chunks.
    chunks=[] # empty list to store our final pieces of text.
    start=0 #a marker telling the the code where to begin cutting the current chunk
    text_length=len(text) #pre calculates the total no of char so the code knows when to stop
    #pre calculation helps because it prevents computer from re-counting the characters everytime the while loop runs.
    while start < text_length: #loop till the start marker hasn't reached the very end of the doc.
        end= start+chunk_size # tells where the chunk should stop. it outputs the no representing the index of the last char in the current chunk
        chunk=text[start:end] #this is the main slicing text which grabs everything from the start to the end and return it in the string format
        chunks.append(chunk) #adds the newly cut chunk to the chunks list.
        start=end-overlap #for the new chunk instead of moving at the next index it moves back by the overlap amount and updates the start index.
    return chunks #returns the list of overlapping text blocks called chunks.