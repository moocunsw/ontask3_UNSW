from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from xlrd import open_workbook
import csv
import boto3
import io
import random
import os
from collections import defaultdict
from dateutil import parser
import pandas as pd
import re

from ontask.settings import SECRET_KEY, DB_DRIVER_MAPPING, AWS_PROFILE


def process_data(data):
    df = pd.DataFrame(data)

    # Replace illegal characters in column headers
    df.columns = df.columns.str.replace("[", "(")
    df.columns = df.columns.str.replace("]", ")")

    # Remove percentage signs from each cell
    df = df.applymap(
        lambda x: x.rstrip("%") if isinstance(x, str) and x.endswith("%") else x
    )

    # Trim whitespaces from each cell
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    df.replace({pd.np.nan: None}, inplace=True)
    return df.to_dict("records")


def retrieve_sql_data(connection):
    """Generic service to retrieve data from an SQL server with a provided query"""

    # Decrypt the password provided by the user to connect to the remote database
    cipher = Fernet(SECRET_KEY)
    try:
        decrypted_password = cipher.decrypt(
            bytes(connection["password"], encoding="UTF-8")
        )
    except:
        decrypted_password = cipher.decrypt(connection["password"])

    # Initialize the DB connection parameters
    connection_parameters = {
        "drivername": DB_DRIVER_MAPPING[connection["dbType"]],
        "username": connection["user"],
        "password": decrypted_password,
        "host": connection["host"],
        "port": connection["port"] if "port" in connection else None,
        "database": connection["database"],
    }

    # SQL alchemy code to add connect to the external DB generically to access the query data
    engine = create_engine(URL(**connection_parameters))
    db_connection = engine.connect()

    # Stream the results from the user query
    # The stream_results=True argument here will eliminate the buffering of the query results
    # The result rows are not buffered, but fetched as they're needed.
    # Ref - http://dev.mobify.com/blog/sqlalchemy-memory-magic/
    try:
        results = db_connection.execution_options(stream_results=True).execute(
            connection["query"]
        )
    except:
        raise Exception("Query returned an error")

    # Convert the buffered results into a list of dicts
    data = [dict(zip(row.keys(), row)) for row in results]

    db_connection.close()

    return data


def retrieve_csv_data(file, delimiter):
    """ Generic service to retrieve data from a csv file with a given 
        delimiter (comma by default) """

    delimiter = "," if delimiter is None else delimiter

    file = file.read().decode("utf-8").splitlines()
    for char in [".", "$"]:
        file[0] = file[0].replace(char, "")

    reader = csv.DictReader(file, delimiter=delimiter)
    data = list(reader)

    return data


def retrieve_excel_data(file, sheetname):
    """ Generic service to retrieve data from the given sheetname of an 
        excel file (supports both .xls and .xlsx) """

    book = open_workbook(file_contents=file.read())
    sheet = book.sheet_by_name(sheetname)

    number_of_columns = sheet.ncols
    number_of_rows = sheet.nrows

    # Identify the header of each column
    fields = [sheet.cell(0, y).value for y in range(number_of_columns)]

    # Remove illegal characters from column headers
    for index, field in enumerate(fields):
        for char in [".", "$", '"', "'"]:
            if char in field:
                fields[index] = fields[index].replace(char, "")

    # Initialize the list that will store the dicts which represent each row
    data = []

    # Iterate over the rows, skipping the first (i.e. the headers)
    for x in range(1, number_of_rows):
        data.append(
            {fields[y]: sheet.cell(x, y).value for y in range(number_of_columns)}
        )

    return data


def retrieve_file_from_s3(connection):
    """ Generic service to retrieve the data from a file in an s3 bucket, 
        depending on the type of the file """

    try:
        bucket = connection["bucket"]
        files = connection["files"]
    except:
        raise Exception("Invalid connection settings")

    data_files = []
    try:
        s3 = None
        if AWS_PROFILE:
            session = boto3.Session(profile_name=AWS_PROFILE)
            s3 = session.resource("s3")
        else:
            s3 = boto3.resource("s3")

        for file in files:
            file_name = file["name"]

            obj = s3.Object(bucket, file_name)
            data = obj.get()["Body"]

            # Parse the data based on the file type
            if file_name.lower().endswith((".csv", ".txt")):
                data = retrieve_csv_data(data, file["delimiter"])
            elif file_name.lower().endswith((".xls", ".xlsx")):
                data = retrieve_excel_data(data, file["sheetname"])
            else:
                raise Exception("File type is not supported")
            data_files.append(data)
    except:
        raise Exception("Error reading file from s3 bucket")

    # TODO: Ensure that columns in each data file are identical

    # Append the data
    data = [record for file in data_files for record in file]

    return data


def guess_column_types(data):
    # Take 25 random records from the dataset, or the entire dataset if
    # there are less than 25 records
    data_range = range(len(data))
    chosen_indexes = random.sample(data_range, 25) if len(data) > 25 else data_range

    # Create a set of values for each field across the chosen indexes
    records = defaultdict(set)
    for i in chosen_indexes:
        for field, value in data[i].items():
            records[field].add(value)

    types = {}
    for field, values in records.items():
        for value in values:
            # If one of the records has been determined to be text, then
            # skip further type checking. Following this approach, a column
            # will only be given a type of 'number' or 'date' if *all* records
            # conform to that type.
            if field in types and types[field] == "text":
                break

            try:
                float(value)
                types[field] = "number"
                continue
            except:
                pass

            try:
                test = parser.parse(value)
                types[field] = "date"
                continue
            except:
                pass

            types[field] = "text"

    return types
