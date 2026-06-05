def run_pipeline(X_train, y_train, X_test, odds):

    # models
    xgb = train_xgb(X_train, y_train)
    lgb = train_lgb(X_train, y_train)
    cat = train_cat(X_train, y_train)

    ensemble = EnsembleModel(xgb, lgb, cat)

    probs = ensemble.predict_proba(X_test)

    market_prob = 1 / odds

    edges = probs - market_prob

    evs = (probs * odds) - 1

    return probs, edges, evs
