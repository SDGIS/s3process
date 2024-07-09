from s3process.results import get, process
import pandas as pd

# Test Error's #1 -- Test Content Length, at least 2
def test_if_empty():
    testing = "Kevin's Test"
    df_test = process(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test Error's #2 -- Test Content Header Size, should be 3
def test_if_formatted_correct():
    testing = "Kevin's Test \n Kevin's test."
    df_test = process(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test Error's #3 -- Data isn't string format
def test_if_correct_datatype():
    testing = ["Kevin's Test"]
    df_test = process(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test Correct Table #4 -- Data is correct format
def test_correct_df():
    url = "https://photometricsai.s3.us-west-2.amazonaws.com/results.csv"
    out = get(url)
    if out != False:
        df = process(out)
        if isinstance(df, pd.DataFrame):
            print(df)
            assert True
        else:
            print("No df processed")
            assert False
    else:
        print("Error in retrieval:", url)
        assert False