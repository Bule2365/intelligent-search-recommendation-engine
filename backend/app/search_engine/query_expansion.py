SYNONYM_DICT = {
    "hp": ["smartphone", "handphone", "ponsel"],
    "murah": ["budget", "hemat", "terjangkau"],
    "laptop": ["notebook"],
    "sepatu": ["footwear"],
    "baju": ["pakaian", "kemeja", "kaos"],
    "celana": ["bawahan"],
    "tas": ["bag"],
}


def expand_query(query: str) -> str:
    """Mengembalikan query asli + kata-kata sinonim yang relevan,
    digabung jadi satu string untuk diberikan ke BM25Search.search()
    atau SemanticSearch.search()."""
    tokens = query.lower().split()
    expanded_terms = list(tokens)
    for token in tokens:
        if token in SYNONYM_DICT:
            expanded_terms.extend(SYNONYM_DICT[token])
    return " ".join(expanded_terms)
