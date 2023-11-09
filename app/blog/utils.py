from openai import Embedding, Completion
from openai.embeddings_utils import distances_from_embeddings
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Post, Similarity
from django.db import models


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
    model="text-davinci-003",
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


def cleanup_similarities(post: Post) -> None:
    # Get all Similarity instances related to the post and order by score descending
    all_similarities = Similarity.objects.filter(
        models.Q(post1=post) | models.Q(post2=post)
    ).order_by("-score")

    # Keep the top 3 similarities
    top_similarities = all_similarities[:3]

    # Exclude the top similarities and delete the rest
    all_similarities.exclude(
        id__in=top_similarities.values_list("id", flat=True)
    ).delete()


def compute_similarity(post_id: int) -> None:
    post = Post.objects.get(id=post_id)
    other_posts = Post.objects.exclude(id=post_id)
    vectorizer = TfidfVectorizer()
    text_data = [f"{post.content} {post.title}"] + [
        f"{other_post.content} {other_post.title}" for other_post in other_posts
    ]
    tfidf_matrix = vectorizer.fit_transform(text_data)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    # Get primary keys of all other posts
    other_posts_pks = list(other_posts.values_list("pk", flat=True))

    # Get as many indices as there are other posts, up to 3
    num_similar_posts = min(len(other_posts_pks), 3)
    top_indices = np.argsort(-cosine_sim[0])[:num_similar_posts]

    # Update or create Similarity instances for the top similar posts
    for idx in top_indices:
        similar_post_pk = other_posts_pks[int(idx)]
        similar_post = Post.objects.get(pk=similar_post_pk)
        Similarity.objects.update_or_create(
            post1=post, post2=similar_post, defaults={"score": cosine_sim[0][idx]}
        )

    cleanup_similarities(post)
