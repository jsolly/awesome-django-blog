import pandas as pd
import os
import json


def remove_newlines(series):
    series = series.str.replace("\n", " ")
    series = series.str.replace("\\n", " ")
    series = series.str.replace("  ", " ")
    series = series.str.replace("  ", " ")
    return series


# This is the blogthedata directory if you cloned the repo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Create a list to store the posts
posts = []

# Get all the JSON files in the exported_posts directory
posts_path = os.path.join(BASE_DIR, "utilities/create_embeddings/exported_posts")
filepaths = [
    os.path.join(posts_path, filename)
    for filename in os.listdir(posts_path)
    if filename.endswith(".json")
]

# Loop through the list of file paths and read the JSON data
for filepath in filepaths:
    with open(filepath, "r") as f:
        data = json.load(f)

        # Append the post fields to the list of posts
        posts.append(
            (
                data["title"],
                data["category"],
                data["date_posted"],
                data["author"],
                data["content"],
            )
        )

# Create a dataframe from the list of posts
df = pd.DataFrame(
    posts, columns=["title", "category", "date_posted", "author", "content"]
)

"""
Set the content column to be the raw text with the newlines removed.
We add the title to the content for additional context.
"""
df["content"] = f"{df.title}. {remove_newlines(df.content)}"

# Save the dataframe to a CSV file in the processed_posts directory
csv_path = os.path.join(
    BASE_DIR, "utilities/create_embeddings/processed_posts", "processed_posts.csv"
)
df.to_csv(csv_path, index=False)

# Print the first few rows of the dataframe
print(df.head())
