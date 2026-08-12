from datetime import datetime
from itertools import combinations
import numpy as np
import pandas as pd
import helper

from openai import OpenAI

client = OpenAI(
    base_url="...", #embedder API endpoint compatible wiht openAI needs to be set here
    api_key="required-but-not-used",
)


def get_coalition_for_date(date_str, entries, key):
    query_date = datetime.strptime(date_str, "%d.%m.%Y")

    for i, (date, value) in enumerate(entries):
        # If this is the last entry or the query date is before the next date
        if i == len(entries) - 1 or query_date < entries[i + 1][0]:
            if query_date >= date:
                if (key == "ALL"):
                    return value["government"] + value["opposition"]
                return value[key]

    return None  # if query_date is before the first known date



# -> Average pairwise agreement
# 1 means same positions, -1 opposite positions, 0 means mixed positions
def group_agreement_similarity(values):
    if len(values) < 2:
        return 1.0
    pairwise_products = [a*b for a,b in combinations(values, 2)]
    return np.mean(pairwise_products)


# 0: perfect alignment, 1: maximal dispersion
def group_distance_dispersion(values):
    l = len(values)
    if l < 2:
        return 0.0
    
    total = 0
    for i in range(l):
        for j in range(i + 1, l):
            total += abs(values[i] - values[j])

    return total / (l * (l - 1))


position_values = {
    "stimme zu": 1,
    "neutral": 0,
    "stimme nicht zu": -1
}


def calc_similarity_score(positions, position_values=position_values):
    numeric_values = [position_values[val] for val in positions]
    dispersion = group_distance_dispersion(numeric_values)
    return 1 - dispersion

def get_similarity_score(date_str, parliament_coalitions, statements, coalition_type):
    parties = get_coalition_for_date(date_str, parliament_coalitions, coalition_type)
    parties_positions = statements[statements["Partei: Kurzbezeichnung"].isin(parties)]["Position: Position"]
    return calc_similarity_score(parties_positions.to_list())



def calculate_agreement_scores(
    file_path: str,
    sheet_name: str,
    reference_date: str,
    coalitions,
):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    rows = []

    for number, group in df.groupby('These: Nr.'):
        rows.append({
            "statement_number": number,
            "title": group["These: Titel"].iloc[0],
            "these": group["These: These"].iloc[0],
            "government": helper.get_similarity_score(
                reference_date, coalitions, group, "government"
            ),
            "opposition": helper.get_similarity_score(
                reference_date, coalitions, group, "opposition"
            ),
            "all": helper.get_similarity_score(
                reference_date, coalitions, group, "ALL"
            ),
        })

    return pd.DataFrame(rows)


def get_topic_embeddings(file_path: str, sheet_name: str):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    wahlOMatTopics = df[['These: Nr.', 'These: Titel', 'These: These']].drop_duplicates()

    # Create embedding input text
    wahlOMatTopicsStrings = (
        "Titel: " + wahlOMatTopics['These: Titel'].astype(str) +
        " - These: " + wahlOMatTopics['These: These'].astype(str)
    ).tolist()

    # Get embeddings
    wahlOMatTopics_embeddings = helper.get_embeddings(wahlOMatTopicsStrings)

    # Add embeddings as a new column
    wahlOMatTopics = wahlOMatTopics.copy()
    wahlOMatTopics["embedding"] = wahlOMatTopics_embeddings

    return wahlOMatTopics



def get_embedding(text, model="llm5"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def get_embeddings(texts, model="llm5"):
    # texts: list[str]
    texts = [t.replace("\n", " ") for t in texts]
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    return [d.embedding for d in response.data]




def get_top_k_for_event(event_emb, topic_norm, topic_df, top_k=3):
    """
    Compute top-k most similar topics for a single event.
    
    Args:
        event_emb (array-like): shape (dim,)
        topic_norm (np.array): normalized topic embeddings, shape (num_topics, dim)
        topic_df (pd.DataFrame): dataframe with topic info (column 'These: Nr.')
        top_k (int): number of top topics to return
    
    Returns:
        list of tuples: [(These: Nr., score), ...] sorted descending
    """
    # Normalize the event embedding
    e_norm = event_emb / np.clip(np.linalg.norm(event_emb), 1e-10, None)
    
    # Cosine similarity
    sims = e_norm @ topic_norm.T
    
    # Top-K indices
    top_k_idx = np.argsort(sims)[-top_k:][::-1]
    
    # Prepare results
    top_k_list = [(topic_df.iloc[idx]["These: Nr."], sims[idx]) for idx in top_k_idx]
    
    return top_k_list

