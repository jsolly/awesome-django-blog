import pandas as pd
import numpy as np
import json
import os
import pickle

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
embeddings_path = os.path.join(
    BASE_DIR, "utilities/create_embeddings/processed/embeddings.json"
)
df_pickle_path = os.path.join(BASE_DIR, "utilities/create_embeddings/processed/df.pkl")

# Load the JSON file as a list of dictionaries
with open(embeddings_path, "r") as f:
    data = json.load(f)

# Create a dataframe from the list of dictionaries
df = pd.DataFrame(data)

# Convert the embeddings column from string to numpy array
df["embeddings"] = df["embeddings"].apply(np.array)

# Pickle the dataframe for future use
with open(df_pickle_path, "wb") as f:
    pickle.dump(df, f)

# Verify that the pickle file was created successfully by loading it and printing the head of the dataframe
with open(df_pickle_path, "rb") as f:
    df_pickle = pickle.load(f)

print(df_pickle.head())
