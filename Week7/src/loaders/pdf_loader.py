from pypdf import PdfReader # library to open and read pdf files 
# pdfreader class reads binary files.
def load_pdf(file_path):
    reader=PdfReader(file_path)  # creates an object which tells the library to go to the file path and prepare pdf reading
    pages=[] #initializes an empty list which will be our bucket where we store the text from every page and this list is stored in the name pages.
    for i,page in enumerate(reader.pages): #render.pages is the list of all the pages inside the pdf
        # instead of just giving the page enumrate gives us a counter i starting at 0 and the actual page data. page is the actual data for that specific page (i).
        text=page.extract_text() #pulls raw text in the format text and page no. basically looks at the current page and tries to convert the visual characters into Python string(text).
        # this generates a string of all the words found on that specific page.
        if text: #this checks if the variable is truthy i.e. if a page is blank or contains only image then extract_text might return an empty string. this line ensures that we dont save empty data.
            pages.append((text,i+1)) #adds an item at the end of the pages list. stored in tuple format
            # text -> words from the page
            # i+1 -> page no and since computer start counting from 0 we add 1 so that the first page is labeled 1 instead of 0.
    return pages #sends the final result back to whoever called the function. output would be a list of tuples.