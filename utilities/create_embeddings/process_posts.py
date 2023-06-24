import pandas as pd
from pathlib import Path
import json


def remove_newlines(text):
    text = text.replace("\n", " ")
    text = text.replace("\\n", " ")
    text = text.replace("  ", " ")
    text = text.replace("  ", " ")
    return text


# This is the blogthedata directory if you cloned the repo
BASE_DIR = Path(__file__).resolve().parent.parent

# Create a list to store the posts
posts = []

# Get all the JSON files in the exported_posts directory
posts_path = BASE_DIR / "utilities/create_embeddings/exported_posts"
filepaths = [
    path
    for path in posts_path.iterdir()
    if path.is_file() and path.name.endswith(".json")
]

# Loop through the list of file paths and read the JSON data
for filepath in filepaths:
    with filepath.open("r") as f:
        data = json.load(f)

        # Append the post fields to the list of posts
        posts.append(
            {
                "title": data["title"],
                "category": data["category"],
                "date_posted": data["date_posted"],
                "author": data["author"],
                "content": data["content"],
            }
        )

# Create a dataframe from the list of posts
df = pd.DataFrame(posts)

"""
Set the content column to be the raw text with the newlines removed.
We add the title to the content for additional context.
"""
df["content"] = df.apply(
    lambda row: f"{row.title}. {remove_newlines(row.content)}", axis=1
)

# Save the dataframe to a JSON file in the processed directory
json_path = BASE_DIR / "utilities/create_embeddings/processed/processed_posts.json"
df.to_json(json_path, orient="records")

# Print the first few rows of the dataframe
print(df.head())
