def create_target(df):

    df["target"] = (df["home_score"] > df["away_score"]).astype(int)

    return df
