class WeatherFeatures:

    @staticmethod
    def weather_score(temp, wind):

        score = 0

        if temp > 28:
            score += 0.10

        if wind > 15:
            score += 0.05

        return score
