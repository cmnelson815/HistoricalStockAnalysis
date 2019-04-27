class Trend:

    def __init__(self):
        self.start_date = '1970-01-01'
        self.end_date = '1970-01-01'
        self.percentage = 0.0
        self.start_value = 0.0
        self.end_value = 0.0
        self.min_value = 0.0

    def get_trend_length_in_days(self):
        return (self.end_date - self.start_date).days
