from pydantic import BaseModel, Field
from datetime import date

class TimePoint(BaseModel):
    date: date
    value: int

class TimeSeriesData(BaseModel):
    series_name: str
    data_points: list[TimePoint]

# Example usage:
if __name__ == "__main__":
    time_series = TimeSeriesData(
        series_name="Daily Active Users",
        data_points=[
            TimePoint(date=date(2024, 1, 1), value=1500),
            TimePoint(date=date(2024, 1, 2), value=1600),
            TimePoint(date=date(2024, 1, 3), value=1700),
        ]
    )

    print(time_series.json(indent=4))

