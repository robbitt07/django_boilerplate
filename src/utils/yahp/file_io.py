from django.core.files import File
from django.db.models import FileField

import io
import numpy as np
import pandas as pd


class FileException(Exception):
    pass


def read_csv_file(file_bytes, nrows=None, chunksize=None):
    """
    Helper function to read in CSV Files
    """
    try:
        # Get columns - pandas does not allow access to columns for chunked dataframe, so read the top row
        temp_df = pd.read_csv(
            file_bytes,
            on_bad_lines="skip",
            index_col=False,
            dtype=str,
            nrows=1,
        )
        columns = temp_df.columns

        # Check if the file is tab separated
        if len(columns) == 1 and (columns or [""])[0].count("\t") > 1:
            file_bytes.seek(0, 0)
            df = pd.read_csv(
                file_bytes,
                on_bad_lines="skip",
                index_col=False,
                dtype=str,
                nrows=nrows,
                chunksize=chunksize,
                sep="\t"
            )
        else:
            file_bytes.seek(0, 0)
            df = pd.read_csv(
                file_bytes,
                on_bad_lines="skip",
                index_col=False,
                dtype=str,
                nrows=nrows,
                chunksize=chunksize,
            )

    except UnicodeDecodeError:
        # Repeat logic with latin1 encoding
        try:
            # Update the read position of the file bytes back to start
            file_bytes.seek(0, 0)
            temp_df = pd.read_csv(
                file_bytes,
                encoding="latin1",
                on_bad_lines="skip",
                index_col=False,
                dtype=str,
                nrows=1,
            )
            columns = temp_df.columns
            # Check if the file is tab separated
            if len(temp_df.columns) == 1 and (temp_df.columns or [""])[0].count("\t") > 1:
                file_bytes.seek(0, 0)
                df = pd.read_csv(
                    file_bytes,
                    encoding="latin1",
                    on_bad_lines="skip",
                    index_col=False,
                    dtype=str,
                    nrows=nrows,
                    chunksize=chunksize,
                    sep="\t"
                )
            else:
                file_bytes.seek(0, 0)
                df = pd.read_csv(
                    file_bytes,
                    encoding="latin1",
                    on_bad_lines="skip",
                    index_col=False,
                    dtype=str,
                    nrows=nrows,
                    chunksize=chunksize,
                )
        except Exception as e:
            raise FileException(e)
    except Exception as e:
        raise FileException(e)
    return df


def read_excel_file(file_bytes, nrows=None, *args, **kwargs):
    try:
        return pd.read_excel(
            file_bytes,
            index_col=False,
            dtype=str,
            nrows=nrows
        )
    except Exception as e:
        try:
            file_bytes.seek(0, 0)
            return read_csv_file(
                file_bytes=file_bytes, 
                nrows=nrows, 
            )
        except:
            raise FileException(e)


def read_json_file(file_bytes, nrows=None, chunksize=None, *args, **kwargs):
    try:
        return pd.read_json(
            file_bytes,
            index_col=False,
            dtype=str,
            nrows=nrows,
            chunksize=chunksize
        )
    except UnicodeDecodeError:
        try:
            # Update the read position of the file bytes back to start
            file_bytes.seek(0, 0)
            return pd.read_json(
                file_bytes,
                index_col=False,
                dtype=str,
                encoding="latin1",
                nrows=nrows,
                chunksize=chunksize
            )
        except Exception as e:
            raise FileException(e)
    except Exception as e:
        raise FileException(e)


def read_file_to_df(file_field: FileField, nrows=None, chunksize=None):
    """
    Read File into Pandas DataFrame, accepts in a File Field
    """
    if file_field is None:
        raise ValueError("file_field can not be null")

    # File Bytes into Memory to avoid opening file connection multiple times
    file_field.seek(0,0)
    file_bytes = io.BytesIO(file_field.read())

    # Looks for file extension (TODO: Add Compression Option)
    extension = file_field.name.split(".")[-1].lower()
    if extension == "csv":
        return read_csv_file(file_bytes=file_bytes, nrows=nrows, chunksize=chunksize)
    elif extension in ("xls", "xlsx"):
        df = read_excel_file(file_bytes=file_bytes, nrows=nrows)
        # Chunk dataframe post load
        if chunksize:
            return (chunk for _, chunk in df.groupby(np.arange(len(df))//chunksize))
        return df
    elif extension == "json":
        return read_json_file(file_bytes=file_bytes, nrows=nrows, chunksize=chunksize)
    else:
        raise NotImplementedError(f"File type `{extension}` not supported")


def write_file_from_df(df: pd.DataFrame, file_name: str, compress=False) -> File:
    """
    Write Pandas DataFrame to a Django FileField

    Params
    ---------
        df pd.DataFrame
            DataFrame duhh
        file_name str
            String name of file name to write, include extension
        compress bool
            Default set to false, NOT IMPLEMENTED
    Returns
    ---------
        file django.core.files.File
            Django File object that can be saved to a Django FileField
    """
    extension = file_name.split(".")[-1].lower()
    if extension == "csv":
        return File(io.BytesIO(df.to_csv(index=False).encode("utf-8")), name=file_name)
    
    elif extension in ("xls", "xlsx"):
        # Special Writing of Excel File
        file_bytes = io.BytesIO()
        writer = pd.ExcelWriter(file_bytes, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Sheet1")
        writer.save()
        return File(file_bytes, name=file_name)
    
    elif extension == "json":
        return File(io.BytesIO(df.to_json(index=False, orient="records").encode("utf-8")), name=file_name)
    else:
        raise NotImplementedError(f"File type `{extension}` not supported")