# EasyGCPz


**EasyGCPz** takes a significant load off of python users of GCP by automating query generation, executing queries, and returning query results in a number of optional accessible data structures. It enables users of any skill level to unlock their querying potential by offering multiple degrees of flexibility, while also being robust against a wide number of common querying and usage problems.

## In this README

- [Features](#features)
- [Initial setup](#initial-setup)
- [Usage](#usage)
- [FAQ](#faq)
- [Contributing](#contributing)


## Features

EasyGCPz comes with several features that streamline GCP usage in python.
1. Easy GCP querying.
    Simply write a query and return its results without any need to understand GCP configurations or data structures, EasyGCP handles all of that for you! Anyone can now approach GCP databases with any level of python experience.

2. The ability to flexibly generate dynamic queries on the fly.
    No need to longer make several copies of the same query and then carefully run and organize them yourself. EasyGCPz conforms to your query and allows you to dynamically specify all the permutations of that query to run! Key abilities include run permutations of several dynamic variables, make copies of a query by iterating the dynamic components by user-defined lists, and built in syntax to help easy generate queries using the SQL between command.

3. Manipulating output data into a workable format is a thing of the past; with 17 choices of outgoing data structures let EasyGCPz do the heavy lifting. 
    With the ability to have queried data delivered to you in any combination of pandas, numpy, standard python, or google bigquery data structures, the ability to have a familiar data structure is on hand with a single command.

4. Fixed type formatting does away with whatever complications the database formatting throws at you.
    Sometimes when we query a database we want the formatted object types that are already there (like _datetime_, _Decimal_, or _char_ objects for example). Other times all we want is the data as we see it without any of the special formatting. By setting one simple variable you can ensure that the outputs of a query only come back as letters _(strings)_ and numbers _(floats)_.

5. Easily auditable querying is now local, with automatic logging working in the background.
    For your own sake, or for the sake of your collaborators, it is essential to know what exact actions are taken at what exact times when it comes to database management and auditable exercises. With a _hands-off_ approach to logging, this system works in the background of a local session and instantly records the metadata of all actions that EasyGCPz undertakes.

6. Saving data has never been easier.
    Iterating over multiple queries, saving the outputs, and remembering which files belong to which queries can be a lot to take care of. Luckily EsayGCPz handles all of this for you in the supported two ways that it can save your results for you. The first way saves data to separate files and takes care of all the indexing, the second way writes all of the data over multiple queries into the same file so that the outputs from multiple queries can be saved together. In both cases the executed queries are automatically saved with the outputs, in separate files, so that you can always keep track of which data belongs to which queries. 

7. Changing connection information during the same session.
    When working on large scale operations there is often the need to switch the connection information on the fly, but this can be a huge hassle to write code that does this at the appropriate points. EasyGCPz can flexibly handle new connection information when entering a new query, making it easy to switch connections at any time or explicitly linking specific queries to specific connections at runtime. 


## Initial setup

1. Download via pip.

    ```
    python -m pip install easygcpz
    ```

2. Import the package into your module.

    ```
    from easygcpz import easygcpz
    ```

3. Run your first query:

    ```
    # establish connection information
    json_path = "~/path/to/gcp_file.json"
    project_name = "MyFirstProject"

    # example query
    example_query = \
    """
    SELECT * FROM MyCoolTable
    """

    # create your first instance with your connection information
    new_instance = easygcpz(json_path, project_name)

    # execute a query and receive its outputs 
    query_output = new_instance.query(example_query)

    ```


## Usage
 
### Creating an instance

When creating an instance there are two required inputs and one optional one. Elaborating on the example query above

```
new_instance = easygcpz(connection_json=json_path, connection_project=project_name, Verbose=True)
```
- The `connection_json` argument contains the path to the [.json file that GCP provides you.](https://stackoverflow.com/questions/46287267/how-can-i-get-the-file-service-account-json-for-google-translate-api). 
- The `connection_json` argument contains the [project name associated with the account](https://stackoverflow.com/questions/24682180/how-to-get-project-id-in-google-cloud-storage)
- The `Verbose` argument prints out the log to the console in real time, as it is being written, when set to True. Setting this to False make it run 'silently', but the log is still available upon request. 

### Running queries. 

Running a query is as easy as calling the **.query()** method, the overall structure to run **query** is as follows: 

```
results = new_instance.query(
              queries='Select * from MyCoolTable'
              return_format='dict',
              return_ascii=False,
              file_separate='',
              file_same='',
              connection_json=None,
              connection_project=None,
              **kwargs)
```

### Query arguments description

- The `queries` argument takes in a single query as a string or a list of query strings.

- The `return_format` argument specifies the data structure that the query data should be returned in. The options for this are as follows: 
    - *array*: columns are concatenated into a numpy array
    - *dataframe*: columns are concatenated into a pandas DataFrame
    - *dict*: columns held as lists in a dictionary
    - *dict_series*: columns held as pandas Series in a dictionary 
    - *dict_array*: columns held as numpy arrays in a dictionary
    - *list*: columns held as zipped list of lists
    - *list_tuple*: columns held as zipped tuple of lists 
    - *list_array*: columns held as zipped list of numpy arrays
    - *list_series*: columns held as zipped list of pandas series
    - *none*: nothing is returned after run, this is useful for queries that do not return anything as well as when the returned data is only to be saved
    - *no_processing*: the google bigquery object is returned as it is, results are not processed at all
    - *structured_array*: columns are concatenated into a numpy structured array

- The `return_ascii` argument specifies if queried outputs should only be returned as letters _(strings)_ and numbers _(floats)_. Setting this to True forces all the query outputs to be string or float type, while setting this to False allows the original data format of each column to be returned as it is.

- Specifying the `file_separate` argument means that each query that is in the current .query() method call gets saved to a new file. This argument counts the number of queries and appends the respective index of each query to its filename. Therefore if gave this argument an example filename `~/example/file.csv` and it executed two queries, the resulting filenames will be `~/example/file_1.csv` and `~/example/file_2.csv`. The queries that were used for these outputs are also saved in separate files. 

- Specifying the `file_same` argument means that each query that is in the current .query() method call gets saved into the same file. Therefore if this argument has an example filename `~/example/file.csv` and it executed two queries, the results of both queries are appended directly into the `~/example/file.csv` file. The queries that were used for these outputs are also appended into the same query log file. Note: this argument assumes that all queries saved into the same file have the same column names; therefore every query executed after the first query is saved without the column name headers since it's assumed that the first entered column names will match all of the appended columns thereafter.

- To change the connection information at any time, or to explicitly enforce connection information to a specific query, the `connection_json` the `connection_project` arguments can be specified along with any query. These two arguments can be specified one at a time or together when invoked through the .query() method call. 

- The general keyword argument `**kwargs` allows for the dynamic generation of new queries with various iterables as demonstrated in following subsections. Any keyword arguments placed at the end of the query call are assumed to be substring matches in the query string or list of query strings provided in the `queries` argument. 

### Generating & executing automatically iterated queries

There are three primary ways that EasyGCPz supports the automatic generation of queries. To demonstrate how each of them works we will start with an example query, show how to call the function, and then show the resulting queries. The general format is that the name of the argument that you specify should be the matching element to replace in a query as demonstrated here: 

*my_query* = 'Select * from **ReplaceMeHere**'
*replacement_list* = ['table_1', 'table_2', ..., 'table_n']
results = new_instance.query(queries=*my_query*, **ReplaceMeHere**=*replacement_list*)

In this way EasyGCPz adapts to your conventions and does not force you to adapt to any format. The follow example subsections will be demonstrated with the EasyGCPz instance we made above in the examples above.

```
new_instance = easygcpz(connection_json=json_path, connection_project=project_name, Verbose=True)
```

#### Iterating query based on one iterable

Lets say you have an example query in python and you want to run it on multiple tables

```
example_query = 'SELECT * FROM my_example_table_list'
```

In this case you can specify the iterable my_example_table_list as a list of table names here: 

```
table_list = ['MyCoolTable', 'MyKindaCoolTable', 'MyReallyCoolTable', 'MySuperCoolTable']
```

Now all we have to do is feed both of these into the query call. To let EasyGCPz know that on what substring you would like your iterables to be placed into, you can specify that substring into the query call itself. 

```
query_output = new_instance.query(queries=example_query, my_example_table_list=table_list)
```

This EasyGCPz call will find the my_example_table_list substring in the example_query string, and make 4 copies of it and replace that substring with the list it was provided with in each copy. The 4 corresponding queries that were executed in the following order are: 

1. `'SELECT * FROM MyCoolTable'`
2. `'SELECT * FROM MyKindaCoolTable'`
3. `'SELECT * FROM MyReallyCoolTable'`
4. `'SELECT * FROM MySuperCoolTable'`

#### Iterating query based on nested iterables

Sometimes we need to have every permutation of a query executed where there multiple parts. EasyGCPz takes care of this in a similar way as it did in the single iterable example above.
Lets say that we need to select two different columns (Score & Time), but we need both columns in both float and integer types. We can specify EasyGCPz to take care of this with a nested list of lists

```
example_query = 'SELECT *, CAST (nested_iterable_example AS nested_iterable_example)'
```

To iterate through all permutations we can specify a nested list of lists

```
nested_list = [['Score', 'Time'], ['float', 'int']]
```

By calling this in the .query() method call:
```
query_output = new_instance.query(queries=example_query, nested_iterable_example=nested_list)
```

EasyGCPz is effectively executing the following four queries: 

1. `'SELECT *, CAST(Score AS float)'`
2. `'SELECT *, CAST(Score AS int)'`
3. `'SELECT *, CAST(Time AS float)'`
4. `'SELECT *, CAST(Time AS int)'`

#### Iterating query between multiple inputs
EasyGCPz only retains one reserved keyword argument for the query call, and that is the **iterate_between** keyword. When this keyword shows up in the .query() method call it looks for **'iterate_between'** in the query for a particular type of replacement. Lets say that we need to iterate a query between 4 different weeks, week 1 of 2020, to week 4 of 2020. The iterate_between keyword can take care of this intrinsically. 

```
example_query = 'SELECT * FROM MyCoolTable WHERE Time BETWEEN iterate_between and iterate_between'
```

To generate the ranges between all four weeks we specify the five dates that mark the stand and end of all of the weeks

```
date_list = ['2020-01-01', '2020-01-08', '2020-01-15', '2020-01-22', '2020-01-29']
```

By calling this in the .query() method call:
```
query_output = new_instance.query(queries=example_query, iterate_between=date_list)
```

*iterate_between* places its substring matches in the order that they appear in the query. If there are multiple things that need to be iterated between the *iterate_between* supports any number of nested lists (list of any number of lists) to work through all iterations as demonstrated in the subsection below.

EasyGCPz is effectively executing the following four queries: 

1. `'SELECT * FROM MyCoolTable WHERE Time BETWEEN 2020-01-01 and 2020-01-08'`
2. `'SELECT * FROM MyCoolTable WHERE Time BETWEEN 2020-01-08 and 2020-01-15'`
3. `'SELECT * FROM MyCoolTable WHERE Time BETWEEN 2020-01-15 and 2020-01-22'`
4. `'SELECT * FROM MyCoolTable WHERE Time BETWEEN 2020-01-22 and 2020-01-29'`

#### Mixing and matching multiple iterable queries of arbitrary complexity
Any number of queries can support any number of arbitrary iterations with EasyGCPz. In this example we will show how 8 queries can be dynamically generated from two input queries and multiple iterables. To keep this example understandable we will step away from standard SQL queries to show how these multiple string are generated, but these results equally extend to SQL queries. 

Here are two example query-like strings

```
query_list = [
'QUERY 1 TEXT: nested_iter | nested_iter | iter_1 | iter_2 | iterate_between | iterate_between | iterate_between | iterate_between' ,
'QUERY 2 TEXT: iterate_between | iter_1 | nested_iter | iterate_between | iter_2 | nested_iter | iterate_between | iterate_between ]
```

Here are the four iterables that we need to specify for the substring matches


```
nested_iterable_ex = [[1 , 2], [3, 4]]
iterable_1_ex = ['a', 'b', 'c', 'd']
iterable_2_ex = ['A', 'B', 'C', 'D']
iterate_between_ex = [['i', 'ii', 'iii', 'iv', 'v'], ['I', 'II', 'III', 'IV', 'V']]
```

By calling this in the .query() method call:

```
query_output = new_instance.query(queries=query_list,
	iter_1=iterable_1_ex,  
	iterate_between=iterate_between_ex, 
	nested_iter=nested_iterable_ex, 
	iter_2=iterable_2_ex)
```

We are dynamically generating and executing the following 8 queries! 
1. `'QUERY 1 TEXT: 1 | 3 | a | A | i | ii' | I | II' `
2. `'QUERY 1 TEXT: 1 | 4 | b | B | ii | iii' | II | III' `
3. `'QUERY 1 TEXT: 2 | 3 | c | C | iii | iv' | III | IV' `
4. `'QUERY 1 TEXT: 2 | 4 | d | D | iv | v' | IV | V' `
5. `'QUERY 2 TEXT: i | a | 1 | ii | A | 3 | I | II' `
6. `'QUERY 2 TEXT: ii | b | 1 | iii | B | 4 | II | III' `
7. `'QUERY 2 TEXT: iii | c | 2 | iv | C | 3 | III | IV' `
8. `'QUERY 2 TEXT: iv | d | 2 | v | D | 4 | IV | V' `

The `queries` argument can support any number of queries to be ran. If there is a substring replacement keyword that is specified then EasyGCPz will attempt to perform these replacements in all of the queries provided in that list. If there are no substring replacement keywords specified then the provided query list is executed in the respective order.  

### Checking iterated queries before running
The **iterated_query** method is what performs the iteration of a query when executing an iterated query, this method is also available directly to you to see exactly the iterated queries that EasyGCPz is generating. This is great for confirmation before executing, or if you just want to use this functionality to generate new queries to share. Note: the **iterated_query** method only takes in one query at a time. Using our existing EasyGCPz instance, *new_instance*, from the examples above lets look at how this works:

```
# making our query
example_query = 'Iterated query test: nested_iter | nested_iter | iter_1 | iter_2 | iterate_between | iterate_between | iterate_between | iterate_between' 

# specifying all of the iterables
nested_iterable_ex = [[1 , 2], [3, 4]]
iterable_1_ex = ['a', 'b', 'c', 'd']
iterable_2_ex = ['A', 'B', 'C', 'D']
iterate_between_ex = [['i', 'ii', 'iii', 'iv', 'v'], ['I', 'II', 'III', 'IV', 'V']] 

# lets see the queries that would be generated from this, without executing them
query_strings = new_instance.iterated_query(
	example_query,
	iter_1=iterable_1_ex,  
	iterate_between=iterate_between_ex, 
	nested_iter=nested_iterable_ex, 
	iter_2=iterable_2_ex)

print(query_strings)
>>> ['Iterated query test: 1 | 3 | a | A | i | ii' | I | II',
     'Iterated query test: 1 | 4 | b | B | ii | iii' | II | III',
     'Iterated query test: 2 | 3 | c | C | iii | iv' | III | IV',
     'Iterated query test: 2 | 4 | d | D | iv | v' | IV | V']

```

### Directly downloading large amounts of queried data

With strict requirements around the GCP console, query size, local memory limitations, or other bandwidth issues it might be necessary to parse out a large amount of downloaded query data into multiple queries. Let's demonstrate how EasyGCPz handles this and then break down all of the arguments present. Using our existing EasyGCPz instance, *new_instance*, from the examples above lets look at how this works:

```
example_query = 'SELECT * FROM MyCoolTable WHERE Time BETWEEN iterate_between and iterate_between'

months_list = ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04', '2020-01-05', '2020-01-06', '2020-01-07', '2020-01-08', '2020-01-09', '2020-01-10', '2020-01-11', '2020-01-12', '2021-01-01']

results_file_path = '~/path/to/results_file.csv'

query_output = new_instance.query(
	               queries=example_query, 
	               return_format='none',
                   file_same=results_file_path,
              	   iterate_between=months_list)
```

This example query call generates one query for every month of data using all of the dates in the *iterate_between* keyword. It downloads each month's data one at a time and appends it into the file in the *file_same* argument. By setting the *return_format* argument to 'none' the downloaded data is not returned to the python environment, thus reducing the memory foot print of the program after each month of data is saved. To verify this we can examine the resulting *query_output* variable: 

```
print(query_output)
>>> [None, None, None, None, None, None, None, None, None, None, None, None]
```

### Getting the runtime log

If you would like a copy of the runtime log there are two available options. The first way to access the log is to get a local copy of it in python, the second way to to have EasyGCPz save it directly to a file for you. Using our existing EasyGCPz instance, *new_instance*, from the examples above here is how to do both:

```
# how to get a local copy of it in python
my_query_log = new_instance.log()

# how to save it directly to a file
log_file_path = '~/path/to/query_log_file.csv'
new_instance.save_log(log_file_path)
```


## FAQ

### What can I use EasyGCPZ for? 

Anything and everything that utilizes a GCP database, for any type of utility and application!

### What license is EasyGCPz released under? 

EasyGCPz is release under a MIT License and is completely open source.

### Any plans for future updates? 

Current planned updates include features for:
- Uploading .csv files straight to a database table
- Expanded ability to handle more types of dynamic query iterations
- Further options for output data structures
- Multithreaded queries to be ran simultaneously
- Support for concurrent i/o processes

## Contributing

If you find a bug, [please feel free to report it!](https://github.com/mw-os/EasyGCPz/issues/new?assignees=&labels=bug).
If you have additional ideas that you would like to see in EasyGCPz, [please request them!](https://github.com/mw-os/EasyGCPz/issues/new?assignees=&labels=enhancement).

eof
