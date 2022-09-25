# RBC Credit Card Statement Parser
This project contains Python scripts to parse RBC Visa statements downloaded from the online banking application into a CSV file for reporting/analysis purposes.

**Main Functions:**
1. Output all transactions parsed from a directory containing (multiple) RBC Visa statements into a CSV file
2. Classify each transaction into a category based on a user-defined JSON classification file

## Table of Contents

1. [ Usage ](#Usage)
2. [ Execution ](#execution)
3. [ Input Data Requirements ](#datarequirements)
4. [ Important Considerations ](#notes) 

# Repository Contents
1. `README.MD`
2. `rbc_visa_parser_notebook.ipynb`: A Jupyter Notebook implementation of this code
3. `rbc_visa_parser_script.py`: Python script version of this code
4. `transaction_classification.json`: Sample transaction classification JSON file

# Usage
Users can either use the Jupyter Notebook implementation of this code, or the Python script version.

## Requirements
The code has two main requirements:
1. Java
2. External Python packages

### Java
You need to ensure that Java is installed in your machine/environment. You can download Java from [their official website](https://www.java.com/en/download/).

### Python Packages
1. tabula-py
2. pandas
3. numpy

You can download the above packages using either pip or conda:

**Pip**
```
pip install tabula-py
pip install pandas
pip install numpy
```
**Conda**
```
conda install tabula-py
conda install pandas
conda install numpy
```

## Execution

This repo contains two options for execution:
1. Jupyter Notebook
2. Python Script

For both implementations, the user needs to specify the SOURCE_DIR, RESULTS_DIR and (optionally) CATEGORY_FILE.

1. `SOURCE_DIR`: The directory containing all the RBC statements
2. `RESULTS_DIR`: The results directory where they want to output the CSV file
3. `CATEGORY_FILE`: The categorization file for each transaction. This file is **optional**.

### Jupyter Notebook
The user needs to update only **cell 4** with the SOURCE_DIR, RESULTS_DIR and CATEGORY_FILE.

### Python Script
The user can run the following command with the specified arguments
```
python rbc_visa_parser_script.py <SOURCE_DIR> <RESULTS_DIR> <CATEGORY_FILE>
```

<a name="datarequirements"></a>
## Input Data Requirements

### Statement Format

The statements that are to be parsed need to have filenames following a specific format.

The ending of the filenames **must** contain the date in the format: `YYYY-MM-DD`

**Example Filenames:**
1. Visa Statement-XXXX 2022-09-06
2. Visa Statement-XXXX 2021-12-01

The **day** is not particularly important, but the **year** and the **month** are crucial to the functioning of this code.

### Category Classification

Users can optionally also utilize a JSON file to classify transactions into various categories.

To use this file, users simply need to add a `Category` key, and an array of keywords assigned to that category. The keywords are patterns that the script 
checks for in the 'Activity Description' section of the transactions, and any Regex match is assigned to this category.

```json
{
    "Category1": [
        "Activity Description Match 1",
        "Activity Description Match 2",
        "..."
    ]
}
```
For example, if a user wants to assign any transactions where the activity description contains the substrings "EXPEDIA", "HOLIDAY INN" or "QUALITY INN" to the 
"Travel/Accomodation" category, we can define it in the JSON as follows:
```json
{
    "Travel/Accomodation": [
        "EXPEDIA",
        "HOLIDAY INN",
        "QUALITY INN"
    ]
}
```

The included `transaction_classification.json` file contains some pre-populated categories that users can use as a starting point.

<a name="notes"></a>
## Important Considerations
As this code utilizes Tabula and PDF layout-based parsing, any time the underlying PDF statements file undergoes format/layout changes, 
this code will need to be updated.

If any other errors or bugs are noticed, please feel free to leave a comment.
