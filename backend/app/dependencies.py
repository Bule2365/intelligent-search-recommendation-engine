from fastapi import Request


def get_keyword_search(request: Request):
    return request.app.state.keyword_search


def get_bm25_search(request: Request):
    return request.app.state.bm25_search


def get_semantic_search(request: Request):
    return request.app.state.semantic_search  # None jika ENABLE_SEMANTIC_SEARCH=false


def get_hybrid_search(request: Request):
    return request.app.state.hybrid_search


def get_content_recommender(request: Request):
    return request.app.state.content_recommender


def get_collaborative_recommender(request: Request):
    return request.app.state.collaborative_recommender


def get_hybrid_recommender(request: Request):
    return request.app.state.hybrid_recommender


def get_user_interactions(request: Request):
    return request.app.state.user_interactions


def get_products_cache(request: Request) -> list[dict]:
    return request.app.state.products_cache


def get_products_by_id_cache(request: Request) -> dict[str, dict]:
    return request.app.state.products_by_id_cache
