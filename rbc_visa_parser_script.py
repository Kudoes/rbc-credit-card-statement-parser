import tabula
import pandas as pd
import numpy as np
import os
import json
import sys
from pathlib import Path

# Define a function to clean up the format of the price entries
def parse_price(price):
    # Define a factor variable to multiply the price with (for debit/credit)
    factor = 1
    
    # Remove all commas in the price string
    price = price.replace(",", "")
    
    # If the price has a negative sign, it is a payment
    if price[0] == '-':
        factor = -1
        price = price[1:]
        
    # Convert the string to a float and multiply by appropriate factor
    return float(price[1:]) * factor

# Validate that the user-defined directory inputs from CMD are valid
def validate_inputs():
    
    SOURCE_DIR = ""
    RESULTS_DIR = ""
    CATEGORY_FILE = ""

    # Validate source and dest directories exist
    try:
        SOURCE_DIR = sys.argv[1] # statements location
        RESULTS_DIR = sys.argv[2] # output file location

        # Validate source directory exists
        if Path(SOURCE_DIR).is_dir():
            pass
        else:
            print("SOURCE_DIR is invalid. Please provide a valid SOURCE directory.\nExecution Stopped")
            sys.exit()

        # Validate results directory exists
        if Path(RESULTS_DIR).is_dir():
            pass
        else:
            print("RESULTS_DIR is invalid. Please provide a valid RESULTS directory.\nExecution Stopped")
            sys.exit()

    except IndexError as e:
        print("You must specify an input and output directory!\nExecution Stopped")
        sys.exit()

    # validate either JSON file is not provided, or if provided, is valid file
    try:
        CATEGORY_FILE = sys.argv[3] # category JSON file
        
        # Validate source directory exists
        if Path(CATEGORY_FILE).is_file():
            pass
        else:
            print("CATEGORY_FILE is invalid. Please provide a valid CATEGORY_FILE JSON file.\nExecution Stopped")
            sys.exit()
    except IndexError as e:
        pass
    
    return SOURCE_DIR, RESULTS_DIR, CATEGORY_FILE

# This is the main function
def main():
    
    # Specify the directory with all VISA transactions
    SOURCE_DIR, RESULTS_DIR, CATEGORY_FILE = validate_inputs()

    print("\nBeginning PDF Extraction....")
    print("Source Directory: {}".format(SOURCE_DIR))
    print("Result Output Directory: {}".format(RESULTS_DIR))
    print("JSON Category File: {}\n=================================".format(CATEGORY_FILE))
    
    # Extract transactions from statements located in SOURCE_DIR
    master_df = extract_transactions(SOURCE_DIR)
    
    # Assign categories to the transactions
    if CATEGORY_FILE != "":
        master_df = assign_categories(master_df, CATEGORY_FILE)
        
    # Save results to CSV file
    min_txn_date = master_df['Transaction Date'].min().strftime('%Y%m%d')
    max_txn_date = master_df['Transaction Date'].max().strftime('%Y%m%d')

    # Write to CSV
    master_df.to_csv('{}/statements_parsed_{}_{}.csv'.format(RESULTS_DIR, min_txn_date, max_txn_date), index=False)
    
    print("Execution successfully completed.\nFile has been saved to: {}".format('{}/statements_parsed_{}_{}.csv'.format(RESULTS_DIR, min_txn_date, max_txn_date)))

def extract_transactions(SOURCE_DIR):

    # Define the valid months as they appear in the transactions
    valid_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL',
                'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    # Create a master dataframe to store all extracted transactions from all statements
    master_df = pd.DataFrame(columns = ['Transaction Date', 'Posting Date', 'Activity', 'Amount (CAD)'])
    
    # Iterate over each statement PDF
    res = pd.DataFrame()
    for entry in os.scandir(SOURCE_DIR):

        # Ensure that the file is a PDF
        if entry.name[-4:] == '.pdf':

            # Parse statement based on identified area markers
            # If the statement layout changes, this will likely break and need to be updated
            pdf_path = entry
            dfs = tabula.read_pdf(pdf_path, 
                                  stream=True,
                                  pages='all', 
                                  pandas_options={'header': None}, 
                                  area=(195, 57, 800, 353),
                                  columns = [58, 95.8, 128, 301]) # Columns is very important!

            # Create a dataframe to store all transactions from all pages for this PDF

            # Combine transactions from all pages (if > 1 page) and clean column names
            df_transactions = pd.concat(dfs)
            df_transactions = df_transactions.drop(df_transactions.columns[0], axis='columns').dropna()
            df_transactions.index = np.arange(0, len(df_transactions))
            df_transactions.columns = ['Transaction Date', 'Posting Date', 'Activity', 'Amount (CAD)']

            # Drop all rows that don't include transactions
            df_transactions = df_transactions.loc[df_transactions['Transaction Date'].str.startswith(tuple(valid_months))]

            # Clean up the transaction amount column values
            df_transactions['Amount (CAD)'] = df_transactions['Amount (CAD)'].apply(lambda x: parse_price(x))

            # Assign the year to the date
            # This involves custom logic for Dec/Jan statements with transactions that span multiple years
            statement_year_month = entry.name[-14:-7]
            statement_year = statement_year_month.split('-')[0]
            statement_month = statement_year_month.split('-')[1]

            # If the month is not Dec/Jan, assign simple year to transaction
            if statement_month not in ['01', '12']:
                df_transactions['Transaction Date'] = df_transactions['Transaction Date'] + " " + statement_year
                df_transactions['Posting Date'] = df_transactions['Posting Date'] + " " + statement_year

            # If the statement is for January and contains (STATEMENT_YEAR - 1) transactions for December, we need to specify those
            elif statement_month in ['01']:
                df_transactions['Transaction Date'] = df_transactions.apply(lambda x: x['Transaction Date'] + " {}".format(int(statement_year)-1) \
                                                                            if x['Transaction Date'][:3] == "DEC" \
                                                                            else x['Transaction Date'] + " {}".format(int(statement_year)), axis='columns')

                df_transactions['Posting Date'] = df_transactions.apply(lambda x: x['Posting Date'] + " {}".format(int(statement_year)-1) \
                                                                            if x['Posting Date'][:3] == "DEC" \
                                                                            else x['Posting Date'] + " {}".format(int(statement_year)), axis='columns')

            # If the statement is for December and contains (STATEMENT_YEAR + 1) transactions for January, we need to specify those
            # This should not be the case with the current statement format from RBC, but just to catch edge cases we include this here
            elif statement_month in ['12']:
                df_transactions['Transaction Date'] = df_transactions.apply(lambda x: x['Transaction Date'] + " {}".format(int(statement_year)+1) \
                                                                            if x['Transaction Date'][:3] == "JAN" \
                                                                            else x['Transaction Date'] + " {}".format(int(statement_year)), axis='columns')

                df_transactions['Posting Date'] = df_transactions.apply(lambda x: x['Posting Date'] + " {}".format(int(statement_year)+1) \
                                                                        if x['Posting Date'][:3] == "JAN" \
                                                                        else x['Posting Date'] + " {}".format(int(statement_year)), axis='columns')

            # Convert all time columns to DATETIME format
            df_transactions['Transaction Date'] = pd.to_datetime(df_transactions['Transaction Date'],format='%b %d %Y').dt.date
            df_transactions['Posting Date'] = pd.to_datetime(df_transactions['Posting Date'],format='%b %d %Y').dt.date

            # Append the transactions to the master dataframe
            master_df = master_df.append(df_transactions)

    # Sort the final dataframe by transaction dates
    master_df = master_df.sort_values('Transaction Date')

    # Re-index the rows
    master_df.index = np.arange(0, len(master_df))
    
    return master_df
    
    

def assign_categories(master_df, CATEGORY_FILE):
    # Read in JSON file
    with open(CATEGORY_FILE) as json_file: 
        categories = json.load(json_file)

    # Create new column for category
    master_df['Category'] = None

    # Iterate through categories and assign the transaction the category based on regex matching
    for category in categories:
        for value in categories[category]:
            master_df.loc[master_df['Activity'].str.contains(value, regex=False), 'Category'] = category
    
    return master_df
   
# Execute Code
if __name__ == "__main__":
    main()