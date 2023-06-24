from openai import Embedding, Completion
from openai.embeddings_utils import distances_from_embeddings
import pickle
from pathlib import Path


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
