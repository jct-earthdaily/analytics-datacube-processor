"""Input schema class"""
from typing import List

from pydantic import BaseModel


class Parameters(BaseModel):
    """
    Parameters class

    Attributes:
        polygon (str): A string representing the polygon for spatial filtering.
        startDate (str): A string representing the start date for temporal filtering.
        endDate (str): A string representing the end date for temporal filtering.
    """
    polygon: str
    startDate: str
    endDate: str


class InputModel(BaseModel):
    """
    Input model class

    Attributes:
        parameters (Parameters): An instance of the Parameters class containing task parameters.
        indicators (List[str]): A list of strings representing indicators for data analysis.
    """
    parameters: Parameters
    indicators: List[str]
