from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=500,
    chunk_overlap=40,
    length_function=len,
    is_separator_regex=False,
)

def RCTsplitter(text_str: str):
    text_list = text_splitter.split_text(text_str)
    return text_list