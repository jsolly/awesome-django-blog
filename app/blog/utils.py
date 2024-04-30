from openai import Embedding, Completion
from openai.embeddings_utils import distances_from_embeddings
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Post, Similarity
import string
import re
import nltk
from nltk.corpus import stopwords


def load_pickle_file():
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "blog" / "df.pkl"

    with file_path.open("rb") as f:
        df = pickle.load(f)

    return df


global_df = load_pickle_file()


def create_context(question, df, max_len=1800, size="ada"):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = Embedding.create(input=question, engine="text-embedding-ada-002")[
        "data"
    ][0]["embedding"]

    # Get the distances from the embeddings
    df["distances"] = distances_from_embeddings(
        q_embeddings, df["embeddings"].values, distance_metric="cosine"
    )

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values("distances", ascending=True).iterrows():
        # Add the length of the text to the current length
        cur_len += row["n_tokens"] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["content"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    model="gpt-3.5-turbo-instruct",
    question=None,
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=150,
    stop_sequence=None,
    df=global_df,
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    # if debug:
    #     print("Context:\n" + context)
    #     print("\n\n")

    # Create a completions using the question and context
    response = Completion.create(
        prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop_sequence,
        model=model,
    )
    return response["choices"][0]["text"].strip()


def preprocess_text(text: str) -> str:
    """
    Preprocess the input text by applying text preprocessing steps
    """
    # Convert the text to lowercase
    text = text.lower()
    # Remove any leading or trailing whitespace
    text = text.strip()
    # Remove punctuation marks
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove stopwords
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text


def getPostChunks(post: Post, chunk_size: int = 1800) -> list:
    """
    Split the post content into chunks of specified size
    """
    content = preprocess_text(post.content)
    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
    return chunks

def compute_similarity(post_id: int) -> None:
    post = Post.objects.get(id=post_id)
    other_posts = Post.objects.exclude(id=post_id).exclude(content="")

    if not other_posts.exists():
        return

    # Create a list of (chunk, post_pk) tuples for all other posts
    combined_texts_and_pks = [
        (chunk, other_post.pk) for other_post in other_posts
        for chunk in getPostChunks(other_post)
    ]

    # Prepend the target post's content as the first element, associating it with its own PK
    combined_texts_and_pks.insert(0, (f"{post.content} {post.title}", post.pk))

    # Separate the combined texts and their corresponding post PKs
    combined_texts, post_pks = zip(*combined_texts_and_pks)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    if tfidf_matrix.shape[0] < 2:
        return

    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    
    # Calculate the number of similar posts to consider
    num_similar_posts = min(len(set(post_pks)) - 1, 3)  # Exclude the target post itself

    # Get the top indices, but make sure to map them back to unique post PKs
    top_indices = np.argsort(-cosine_sim[0])[:num_similar_posts]
    unique_top_pks = {post_pks[i + 1] for i in top_indices}  # +1 to skip the first post itself

    for pk in unique_top_pks:
        idx = combined_texts_and_pks.index(next(filter(lambda x: x[1] == pk, combined_texts_and_pks)))
        Similarity.objects.update_or_create(
            post1=post,
            post2=Post.objects.get(pk=pk),
            defaults={"score": cosine_sim[0][idx - 1]},  # Adjust index for cosine_sim offset
        )