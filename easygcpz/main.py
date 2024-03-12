"""
EasyGCPz takes a significant load off of python users of GCP by
automating query generation, executing queries, and returning
query results in a number of optional accessible data structures.
EasyGCPz enables users of any skill level to unlock their querying
potential by offering multiple degrees of flexibility, while also
being robust against a wide number of common querying and usage
problems.
"""

# standard
import csv
import datetime
import itertools
import os
import pathlib
import sys
import warnings

# third party
from google.cloud import bigquery

# try importing numpy and pandas since they are not explicitly required
# optional third party packages

try:
    import numpy as np
except ModuleNotFoundError:
    pass

try:
    import pandas as pd
except ModuleNotFoundError:
    pass


# -------- EasyGCPz class package --------
class EasyGCPz:
    """Package class that contains all of EasyGCPZ uses and features.

    --------------
    Public methods
    --------------

    query(queries,
          return_format='dict',
          return_ascii=False,
          file_separate='',
          file_same='',
          connection_json=None,
          connection_project=None,
          **kwargs)

    -> Executes a query, optionally iterating queries,
       optionally saving results.

    iterated_query(query_in,
                   **kwargs)

    -> Returns a list of iterated query strings, without executing them.

    save_log(path_out)

    -> Saves the current runtime log to file path provided in path_out.

    -----------------
    Public attributes
    -----------------
    log

    -> Returns the current runtime log.

    connection

    -> Returns GCP connection object:
       google.cloud.bigquery.client.Client.

    """

    __slots__ = ("_connection",
                 "connection_info",
                 "_log",
                 "verbose",
                 "_kwargs",)

    def __init__(self,
                 connection_json=None,
                 connection_project=None,
                 verbose=True,
                 **kwargs):
        """Init method establishes first connection.

        :param connection_json: Required incoming file path string of
            the json file that is connected to a GCP account.
        :param connection_project: Required incoming project string
            that contains the name of the project that the GCP account
            connects to.
        :param verbose: Optional bool input. Setting this to True
            prints out the execution log as it is being written,
            showing what actions are being taken in what order and
            at what time. Setting to False makes a silent runtime.
        """

        # handoff
        self._kwargs = kwargs
        self.verbose = verbose
        # initialize connection and log attributes
        self._log = []
        self.connection_info = []
        self.connection = [connection_json, connection_project]

    def __call__(self, *args, **kwargs):
        """Calling instance directly invokes query method."""

        return self.query(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        """Calling instance via entering invokes self for use."""

        return self

    def __exit__(self, ex, e, tb):
        """Exiting a call is designed to close connection upon exit."""

        del self.connection


# -------- connection methods --------

    @property
    def connection(self):
        """Quick method to return the instance's current connection object.

        :returns: Bigquery connection object.
        """

        self.log = f'GETTING CONNECTION FOR: {self.connection_info}'
        return self._connection

    @connection.setter
    def connection(self, connection_info):
        """Sets the connection object that the instance uses. Connection
            can be changed at any time using this method or providing these
            variables to the query method.

        :param connection_info: a list of two elements respectively:
            - connection_json: Incoming file path string of the json
                file that is connected to a GCP account.
            - connection_project: Incoming project string that contains
                the name of the project that the GCP account connects to.
        """

        try:
            connection_json, connection_project = connection_info
            # set the connection
            if connection_json is None or connection_project is None:
                warnings.warn(
                    f"\n - No connection information set",
                    UserWarning,
                    stacklevel=2)
            else:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = connection_json
                self._connection = bigquery.Client(project=connection_project)

        except Exception as e:
            raise EasyGCPzException(
                f'EasyGCPz cannot find or assign inputs '
                f'correctly. In the class creation the '
                f'json credential file path and the '
                f'project name must be supplied in the '
                f'first and second arguments respectively, '
                f'or to the connection_json and '
                f'connection_project keyword arguments '
                f'respectively. When updating the connection '
                f'information when the class is already '
                f'initiated the json credential file path '
                f'and the project name must be supplied in '
                f'the connection_info input (first argument) '
                f'as a list of the connection_json '
                f'connection_project strings respectively.'
                f'If these are supplied correctly, then '
                f'the connection cannot be made \n '
                f'Error information: \n{e}')

        # establish current connection data and log it
        finally:
            self.connection_info = connection_info
            self.log = (f'ATTEMPT CONNECTION SETTING: '
                        f'{connection_json} + '
                        f'{connection_project}')

    @connection.deleter
    def connection(self):
        """Manual override to close/reset the current connection."""

        self.log = f'EXITING CONNECTION MANUALLY: {self.connection_info}'
        self._connection.close()
        self._connection = [None, None]
        self.connection_info = None
        print(self.log)

    # -------- core query processing methods --------

    def query(self,
              queries,
              return_format='dict',
              return_ascii=False,
              file_separate='',
              file_same='',
              connection_json=None,
              connection_project=None,
              **kwargs):
        """Core querying method, organizes internal parameters and calls
            to run a query and process and or return its results.

        :param queries: A string or a list/tuple of strings that contain
            the query/queries that will be modified (if kwargs are present)
            and executed.
        :param return_format: Optional string input that established the
            desired data structure/format of data from the query results.
        :param return_ascii: Optional bool input that enforces query
            results to only be returned as strings and floats.
        :param file_separate: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Setting a filepath in this input
            (and not file_same) makes it so data is written into a
            new file every time a query is executed. Results are written
            into a new file whose file names are indexed with respect
            to the order in which they were executed in.
        :param file_same: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Setting a filepath in this
            input (and not file_separate) makes it so data is appended
            into this same file every time a query is executed. Results
            are appended directly into this file.
        :param connection_json: Optional json input that can be used to
            update the GCP connection information instance that has
            already been initiated. Handed off directly to the
            connection setting method.
        :param connection_project: Optional project input that can be
            used to update the GCP connection information instance that
            has already been initiated. Handed off directly to the
            connection setting method.
        :param kwargs: Optional argument(s) that contain all the keyword
            matches in the provided query/queries for dynamic replacement.
        :returns: The results of the executed query in the desired
            format, specified in the return_format input.
            If multiple queries are executed the results are returned
            in a list (respective of the order that they were executed)
            in the desired format, specified in the return_format input.
        """

        # update the connection information if values are present
        if connection_json is not None or connection_project is not None:
            self.connection_info[0] = self.connection_info[0] if \
                connection_json is None else connection_json
            self.connection_info[1] = self.connection_info[1] if \
                connection_project is None else connection_project
            # update the connection with new connection info
            self.connection = self.connection_info

        # validate all the inputs are as expected
        self._query_inputs_validate(queries=queries,
                                    return_ascii=return_ascii,
                                    return_format=return_format,
                                    file_same=file_same,
                                    file_separate=file_separate,
                                    kwargs=kwargs)

        # if kwargs is not empty then develop multiple queries
        if kwargs != {}:
            # generate the iterated queries for a single incoming query
            if isinstance(queries, (str, int, float, complex)):
                queries = self.iterated_query(queries, **kwargs)
            # generate the iterated queries for a multiple incoming queries
            elif isinstance(queries, (list, tuple)):
                queries = \
                    list(itertools.chain.from_iterable(
                        self.iterated_query(i, **kwargs) for i in queries))
            # raise exception if the type is not accepted
            else:
                raise EasyGCPzException(
                    f'A query must be either a str list, a str tuple '
                    f'or plain str. The provided query input is of '
                    f'{type(queries)} type for the following input: '
                    f'\n {type(queries)}')

        # wrap single query as a list
        if isinstance(queries, str):
            queries = [queries]

        # initiate the outgoing file paths for separate files
        if file_separate != '':
            # generate filenames of all the outgoing files
            # splits path and inserts a number at the end
            file_separate = [f'{os.path.splitext(file_separate)[0]}_'
                             f'{str(i).zfill(len(str(len(queries))))}'
                             f'{os.path.splitext(file_separate)[1]}'
                             for i in range(len(queries))]
        else:
            file_separate = [''] * len(queries)

        # execute all queries and process outputs
        data_out = tuple(
            self._query_exec(
                query_in=i,
                return_ascii=return_ascii,
                return_format=return_format,
                file_same=file_same,
                file_separate=j)
            for i, j in zip(queries, file_separate))

        # if only a single query came in then return its single output,
        # else return multiple inputs as a tuple
        if len(data_out) == 1:
            return data_out[0]
        else:
            return data_out

    def _query_exec(self,
                    query_in,
                    return_format='dict',
                    return_ascii=False,
                    file_separate='',
                    file_same=''):
        """Internal method to execute a query, passing results and post-
        processing info to the internal _query_out_processor method.

        :param query_in: A string that contains the query to be executed.
        :param return_format: Optional string input that established the
            desired data structure/format of data from the query results.
        :param return_ascii: Optional bool input that enforces query
            results to only be returned as strings and floats.
        :param file_separate: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            desired to be saved to a file. Results are written directly
            into this new file; existing file contents overwritten.
        :param file_same: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Results are appended directly into this
            file.
        :returns: The results of the executed query in the desired
            format, specified in the return_format input.
        """

        # try running query
        try:
            self.log = f'QUERY STARTING: {query_in}'
            res_obj = self._connection.query(query_in).result()
        except Exception as e:
            raise EasyGCPzQueryError(
                f'EasyGCPz has encountered the following error from GCP: '
                f'\n--> {e} \n-\n'
                f'While attempting to execute the following query:'
                f'\n-\n{query_in} \n-')

        # return bigquery object itself, no processing/formatting of results
        if return_format == 'no_processing':
            self.log = 'QUERY COMPLETED'
            return res_obj

        # get the returned column data values and column names
        values = zip(*list(map(lambda x: x.values(), res_obj)))
        names = (i.name for i in res_obj.schema)
        self.log = 'QUERY COMPLETED'

        # process the outputs into user requested formats and/or
        # write data to files. inputs constructed in return call
        # for clarity and efficiency
        return self._query_out_processor(
            query_in=query_in,
            results={i: j for i, j in zip(names, values)},
            return_ascii=return_ascii,
            return_format=return_format,
            file_same=(pathlib.Path(file_same).as_posix()
                       if file_same else ''),
            file_separate=(pathlib.Path(file_separate).as_posix()
                           if file_separate else ''))

    def _query_out_processor(self,
                             query_in,
                             results,
                             return_format='dict',
                             return_ascii=False,
                             file_separate='',
                             file_same=''):

        """Process queried data into expected formats and/or files.

        :param query_in: A string that contains the query to be executed.
        :param results: A dict of the executed query's results, keys are
            names of columns and values are column data.
        :param return_format: Optional string input that established the
            desired data structure/format of data from the query results.
        :param return_ascii: Optional bool input that enforces query
            results to only be returned as strings and floats.
        :param file_separate: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            desired to be saved to a file. Results are written directly
            into this new file; existing file contents overwritten.
        :param file_same: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Results are appended directly into this
            file.
        :returns: The results of the executed query in the desired
            format, specified in the return_format input.
        """

        # see if the values should be returned as ascii
        if return_ascii:
            self.log = 'ENFORCING ASCII (string and float types only)'
            results = self._force_uft8(results)

        # ---- save data into the same file if it is specified ----
        if file_same != '':
            self.log = f'APPENDING OUTPUT TO: {file_same}'
            # if the file does not exist then write it with column headers,
            # else it exists and write without headers
            if os.path.isfile(file_same):
                with open(file_same, 'a+t', newline='') as f:
                    # convert from column centric data to row centric
                    csv.writer(f).writerows(
                        list(map(list, zip(*list(results.values())))))
            else:
                # add headers back and transpose to for file column format
                with open(file_same, 'a+t', newline='') as f:
                    # add header and convert from column centric data
                    # to row centric
                    csv.writer(f).writerows(
                        [list(results.keys())] +
                        list(map(list, zip(*list(results.values())))))

            # save the query too
            file_same_query = f'{os.path.splitext(file_same)[0]}_QUERY_.txt'
            self.log = f'APPENDING RESPECTIVE QUERY TO: {file_same_query}'
            with open(file_same_query, 'a+t') as f:
                f.write(f'{os.getlogin()} has executed the following '
                        f'EasyGCPz query at {self._get_ts()}: \n \n'
                        f'{query_in} \n \n')

        # ---- save data into new file if it is specified ----
        if file_separate != '':
            self.log = f'WRITING OUTPUT TO: {file_separate}'
            with open(file_separate, 'w+', newline='') as f:
                # add header and convert from column centric data to
                # row centric
                csv.writer(f).writerows(
                    [list(results.keys())] +
                    list(map(list, zip(*list(results.values())))))

            # save the query too
            file_separate_query = \
                f'{os.path.splitext(file_separate)[0]}_QUERY_.txt'
            self.log = f'WRITING RESPECTIVE QUERY TO: {file_separate_query}'
            with open(file_separate_query, 'w+') as f:
                f.write(f'{os.getlogin()} has executed the following '
                        f'EasyGCPz query at {self._get_ts()}: \n \n'
                        f'{query_in} \n \n')

        # ---- return the data in the desired format ----

        # -- pythonic --

        if return_format == 'dict':
            return results

        elif return_format == 'list':
            return [i[0] for i in results.values()]

        elif return_format == 'list_tuple':
            return [i[0] for i in results.items()]

        elif return_format == 'none':
            self.log = "NO VALUES RETURNED: return_format == 'none'"
            return None

        # -- numpy --

        elif return_format == 'array':
            return np.squeeze(np.array(list(results.values()), dtype=object))

        elif return_format == 'dict_array':
            return {i: np.squeeze(np.array(results[i]))
                    for i in results.keys()}

        elif return_format == 'list_array':
            return [np.squeeze(np.array(i))
                    for i in results.values()]

        elif return_format == 'structured_array':
            # initialize structured array with generic object type
            # since queries could return any number of types if
            # return_ascii is False
            _res_len = len(list(results.values())[0])
            _res_keys = list(results.keys())
            obj_out = np.zeros(
                _res_len,
                dtype={'names': _res_keys,
                       'formats': [object] * len(_res_keys)})
            for i in results:
                obj_out[i] = results[i]
            return obj_out

        # -- pandas --

        elif return_format == 'dataframe':
            return pd.DataFrame(results)

        elif return_format == 'dict_series':
            return {i[0]: pd.Series(i[1]).rename(i[0])
                    for i in results.items()}

        elif return_format == 'list_series':
            return [pd.Series(i[1]).rename(i[0])
                    for i in results.items()]

        else:
            warnings.warn(
                f"The return_format: {return_format} provided does not "
                f"match any of available options for type of data "
                f"structures to return. Returning a dict of lists "
                f"(return_format == 'dict')",
                UserWarning,
                stacklevel=2)
            return results

    # -------- class support methods --------

    @staticmethod
    def _query_inputs_validate(queries,
                               return_ascii,
                               return_format,
                               file_same,
                               file_separate,
                               kwargs):
        """Validate incoming user provided arguements and notify user
            of issues. Provides strong-like type checking and verification
            that specific arguements are expected by the program

        :param queries: A string or a list/tuple of strings that contain
            the query/queries that will be modified (if kwargs are present)
            and executed.
        :param return_format: Optional string input that established the
            desired data structure/format of data from the query results.
        :param return_ascii: Optional bool input that enforces query
            results to only be returned as strings and floats.
        :param file_separate: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Setting a filepath in this input
            (and not file_same) makes it so data is written into a
            new file every time a query is executed. Results are written
            into a new file whose file names are indexed with respect
            to the order in which they were executed in.
        :param file_same: Optional string input to a filepath (which
            does not have to exist yet) if the data of the query result is
            to be saved to a file. Setting a filepath in this
            input (and not file_separate) makes it so data is appended
            into this same file every time a query is executed. Results
            are appended directly into this file.
        :param kwargs: Optional argument(s) that contain all the keyword
            matches in the provided query/queries for dynamic replacement.
        """

        # init a list of input issues
        issue_list = []

        # validate queries
        if isinstance(queries, (str, int, float, complex)):
            pass
        elif isinstance(queries, (list, tuple)):
            if not (all(isinstance(i, (str, int, float, complex))
                        for i in queries)):
                issue_list += [f'All queries must be of str, int, or float '
                               f'type, but the following types were received:'
                               f' {", ".join(type(i) for i in queries)}']
            else:
                pass
        else:
            issue_list += [f'All queries must be of str, int, float, list, '
                           f'or tuple type, but the following type was '
                           f'received: {type(queries)}']

        # validate return_ascii value
        if not isinstance(return_ascii, bool):
            issue_list += [f'return_ascii value must be either True or '
                           f'False (bool type), but received value is of '
                           f'{type(return_ascii)} type']

        # validate return_format value
        data_structures_out = ('dict', 'none', 'dict_series', 'dict_array',
                               'dataframe', 'array', 'structured_array',
                               'no_processing', 'list', 'list_tuple',
                               'list_array', 'list_series')
        if return_format not in data_structures_out:
            issue_list += [f'return_format value is set to {return_format}, '
                           f'but this option is not supported. Please '
                           f'choose from one of the following options: '
                           f'{", ".join(data_structures_out)}']

        # validate file_same value
        if not isinstance(file_same, (str, pathlib.PurePath)):
            issue_list += [f'file_same value must be of type str or '
                           f'pathlib.PurePath, but the received type is '
                           f'{type(file_same)}']

        # validate file_separate value
        if not isinstance(file_separate, (str, pathlib.PurePath)):
            issue_list += [f'file_separate value must be of type str or '
                           f'pathlib.PurePath, but the received type is '
                           f'{type(file_separate)}']

        # validate kwargs types
        for i in kwargs.keys():
            if not isinstance(i, (str, int, float, complex)):
                issue_list += [f'provided keyword argument names must '
                               f'be of string type, but {i} was found '
                               f'to be of {type(i)} type.']
        for i in kwargs.values():
            for j in i:
                if not isinstance(j, (str, int, float, complex)):
                    issue_list += [f'provided keyword argument values must '
                                   f'be of string type, but {j} was found '
                                   f'to be of {type(j)} type.']

        # raise formatted exception if any issues exist
        if len(issue_list) > 0:
            # formulate all issues in easy to read format and raise
            issue_str = ' \n'.join(f'{i[0]+1}. \n- {i[1]}'
                                   for i in enumerate(issue_list))
            raise EasyGCPzException(
                f'Issues encountered in the inputs: \n{issue_str}')

    @staticmethod
    def iterated_query(query_in,  **kwargs):
        """Generate multiple queries using kwargs as iterables.

        :param query_in: Incoming string to be referenced from.
        :param kwargs: Keys represent substring matches found within
            query_in and values are lists of values to replace into the
            substring matches.
        :returns: A list of queries, each with the appropriate
            iterables placed into the substring matches of kwargs keys.
        """

        # initialize dict to house the unpacked iterables
        iterable_dict = {}

        # generate between-like iterables if iterate_between in kwargs
        if 'iterate_between' in kwargs.keys():
            # create temporary variable to pop into, unpack as needed
            _ib = kwargs.pop('iterate_between')
            if all(isinstance(i, (list, tuple)) for i in _ib):
                tmp_list = \
                    [list(map(list, zip(i[:-1], i[1:])))
                     for i in _ib]
                iterable_dict['iterate_between'] = \
                    [list(itertools.chain.from_iterable(i))
                     for i in list(zip(*tmp_list))]
            else:
                iterable_dict['iterate_between'] = \
                    list(map(list, zip(_ib[:-1], _ib[1:])))

        for i in kwargs.keys():
            # check if the inputs themselves are to be iterated
            if bool(set(map(type, kwargs[i])).intersection({list, tuple})):
                iterable_dict[i] = list(itertools.product(*kwargs[i]))
            # if not then append them directly in
            else:
                iterable_dict[i] = [[str(j)] for j in kwargs[i]]

        # create the queries list with the iterable inputs
        all_queries = []

        # count the number of iterables from the first kwarg and make that
        # number of queries that gets generated
        for i in range(len(list(iterable_dict.values())[0])):
            # get required iterables
            tmp_q_replace = list(itertools.chain.from_iterable(
                [list(itertools.product([j], iterable_dict[j][i]))
                 for j in iterable_dict.keys()]))
            tmp_q = ''.join(query_in)
            for j in tmp_q_replace:
                if str(j[0]) in tmp_q:
                    tmp_q = tmp_q.replace(str(j[0]), str(j[1]), 1)
                else:
                    raise EasyGCPzException(
                        f'The value to be replaced cannot be found in '
                        f'the current query:\n    Query = " {tmp_q} \n", '
                        f'Value = " {j[0]} " ')
            all_queries.append(tmp_q)

        return all_queries

    # -------- logging methods --------

    @property
    def log(self):
        """Quick way to return the instance's execution log directly."""

        return self._log

    @log.setter
    def log(self, str_in):
        """Append message into execution log and print if verbose is True.

        :param str_in: Incoming string to be appended into log.
        """

        str_in = (f'{self._get_ts()}: {os.getlogin()}: '
                  f'EasyGCPz log entry: {str_in}')
        self._log.append(str_in)

        if self.verbose:
            print(str_in)

    def save_log(self, path_out):
        """Quick method to write log to specified file.

        :param path_out: Write log file to path_out file.
        """

        if not isinstance(path_out, (str, pathlib.PurePath)):
            warnings.warn(
                f"\n - save_log method requires the path_out "
                f"argument to be of string or pathlib type, "
                f"but it is of {type(path_out)} type for the "
                f"provided argument: {path_out}.\n"
                f"Please input valid path and try again \n"
                f" -- LOG NOT SAVED --",
                UserWarning,
                stacklevel=2)
        else:
            try:
                self.log = f'SAVING CURRENT LOG TO: {path_out}'
                with open(path_out, 'w+', newline='') as f:
                    f.write('\n'.join(i for i in tmp.log))
            except Exception as e:
                warnings.warn(
                    f"The following error was encountered when "
                    f"trying to save the current log to the provided "
                    f"file : \n"
                    f"{e}"
                    f" -- LOG NOT SAVED --",
                    UserWarning,
                    stacklevel=2)

    # -------- class utility methods --------

    @staticmethod
    def _get_ts():
        """Get formatted timestamp string of current local time."""

        return str(datetime.datetime.now().strftime("%D-%H:%M:%S"))

    def _force_uft8(self, dict_in: dict):
        """Force values to be returned as str or float types.

        :param dict_in: Dict of values to update.
        :returns: A corresponding dict of strings and floats.
        """

        return {i: self._try_str_float(dict_in[i]) for i in dict_in.keys()}

    @staticmethod
    def _try_str_float(obj_in):
        """Take in a list-like object, return elements as str or float type.

        :param obj_in: Incoming list-like object to be referenced from.
        :returns: A corresponding list of either strings or floats.
        """
        try:
            return [float(i) for i in obj_in]
        except ValueError:
            return [str(i) for i in obj_in]

    def csv_reader(self, path_in: str) -> dict:
        """Read in csv to dict, assumes column headers as keys.

        :param path_in: File path of .csv file to be read in.
        :returns: A corresponding dict
        """

        # read in data
        with open(path_in, newline='') as reader_obj:
            reader_list = list(map(list, csv.reader(reader_obj)))

        # return headers as keys and all else as columns
        headers_list = reader_list.pop(0)
        return {k: self._try_str_float(v) for k, v in
                zip(headers_list, map(list, zip(*reader_list)))}


class EasyGCPzException(Exception):
    """Base exception class for package."""
    def __init__(self, *args):
        # Call the base class constructor with the parameters it needs
        super().__init__(*args)
        self._args = args


class EasyGCPzQueryError(EasyGCPzException):
    """Exception class for failed querying calls"""
    pass


if __name__ == '__main__':

    print(f'Running EasyGCPz directly from file: '
          f'{pathlib.Path(__file__).as_posix()}')

    # for command line usage
    with EasyGCPz(sys.argv[0], sys.argv[1], verbose=True) as tmp:
        if len(sys.argv) <= 7:
            tmp.query(queries=sys.argv[2],
                      return_format=sys.argv[3] if
                      len(sys.argv) >= 4 else 'dict',
                      return_ascii=bool(sys.argv[4]) if
                      len(sys.argv) >= 5 else True,
                      file_separate=sys.argv[5] if
                      len(sys.argv) >= 6 else '',
                      file_same=sys.argv[6] if
                      len(sys.argv) >= 7 else '')
        else:
            # build incoming kwargs dict from every other element
            # get list of kwargs
            kwargs_l = sys.argv[7:]
            # build out kwargs keys and values lists
            kwargs_k = [i[1] for i in enumerate(kwargs_l) if i[0] % 2 == 0]
            kwargs_v = [i[1] for i in enumerate(kwargs_l) if i[0] % 2 == 1]
            # reconstruct a kwargs dict
            dict_ = {kwargs_k[i]: kwargs_v[i] for i in range(len(kwargs_k))}
            # run query
            tmp.query(queries=sys.argv[2],
                      return_format=sys.argv[3],
                      return_ascii=bool(sys.argv[4]),
                      file_separate=sys.argv[5],
                      file_same=sys.argv[6],
                      **dict_)

# eof
