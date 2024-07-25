# Developer: Kevin Mercy
# Package: s3_process
# Test: s3process.results

# Description: Test suite for s3process.results

#_____________________________________________________________________________________


from s3process.results import get, process_results, process_hours
import pandas as pd

# Test if content does not contain several rows
# should be at least 2 lines
# Test Fixture: Kevin's Test
# Return: should not process DF
def test_if_empty():
    testing = "Kevin's Test"
    df_test = process_results(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test if header if wrong size -> should be 3
# TODO Change Test to what header actually is
# Fixture: Kevin's Test \n Kevin's test.
# Return: should not process DF
def test_if_formatted_correct():
    testing = "Kevin's Test \n Kevin's test."
    df_test = process_results(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test if data is different format -- Data isn't string format
# Fixture: ["Kevin's Test"]
# Return: should not process DF
def test_if_correct_datatype():
    testing = ["Kevin's Test"]
    df_test = process_results(testing)
    if isinstance(df_test, pd.DataFrame):
        print(df_test)
        assert False
    else:
        print("No df processed")
        assert True

# Test Correct results.csv -- This should process DF, this is the real datastream
# Fixture: https://photometricsai.s3.us-west-2.amazonaws.com/results.csv
# Return: DF
def test_correct_df():
    url = "https://photometricsai.s3.us-west-2.amazonaws.com/results.csv"
    out = get(url)
    if out != False:
        df = process_results(out)
        if isinstance(df, pd.DataFrame):
            print(df)
            assert True
        else:
            print("No df processed")
            assert False
    else:
        print("Error in retrieval:", url)
        assert False

# Test Time CSV Processing -- This should process DF, this is the real datastream
# Fixture: https://photometricsai.s3.us-west-2.amazonaws.com/evari_data_1223_output.csv
# Return: DF
def test_correct_light_hours():
    url = "https://photometricsai.s3.us-west-2.amazonaws.com/evari_data_1223_output.csv"
    out = get(url)
    if out != False:
        df = process_hours(out)
        print(df)
        assert True