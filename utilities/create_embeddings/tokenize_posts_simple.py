import tiktoken
import pandas as pd
from pathlib import Path
import json
import matplotlib.pyplot as plt

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Three levels up

# Load the JSON file as a list of dictionaries
with open(
    BASE_DIR / "utilities/create_embeddings/processed/processed_posts.json",
    "r",
) as f:
    data = json.load(f)

# Create a dataframe from the list of dictionaries
df = pd.DataFrame(
    data, columns=["title", "category", "date_posted", "author", "content"]
)

# Tokenize the text and save the number of tokens to a new column
df["n_tokens"] = df.content.apply(lambda x: len(tokenizer.encode(x)))

# Visualize the distribution of the number of tokens per row using a histogram
df.n_tokens.hist()
# print the length of the longest line
plt.show()
