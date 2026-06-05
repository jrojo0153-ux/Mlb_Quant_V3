def compute_edge(model_prob, market_prob):

    return model_prob - market_prob


def is_value_bet(edge, threshold=0.04):

    return edge > threshold
