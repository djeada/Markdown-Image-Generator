import pandas as pd

from src.image_generation.draw_strategy import DrawTable


def test_text_to_dataframe():
    # Create a DrawTable instance
    dt = DrawTable("black")

    # Text input for the function
    input_text = "| column1 | column2 |\n| ------- | ------- |\n|  value1  |  value2  |"

    # Expected output as a DataFrame
    expected_output = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]}, index=[1])

    # Call the function and get its output
    result = dt.text_to_dataframe(input_text)

    # Check if the function output is same as the expected output
    assert result.to_dict() == expected_output.to_dict()
