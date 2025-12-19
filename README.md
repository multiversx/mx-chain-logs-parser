# mx-chain-logs-parser
Logs parsing utilities and applications

## LOGS PARSER TOOLS:
The tool provides general abstract classes that can be useful for parsing logs.
In order to create an application that uses off-line parsing of logs files, these classes must be inherited and methods should be implemented for that particular case.

### ARCHIVE HANDLER
- General application processing class, that loops through the nodes in the downloaded logs archive and calls its NodeLogsChecker instance for each one of them
- run level methods should be implemented in inheriting classes

### NODE LOGS CHECKER
- Node level processing, that loops through individual log files for a node and calls its instance of the AhoCorasikParser to search for entries with pre-defined key phrases
- node level methods should be implemented in inheriting classes

### AHO-CORASIK PARSER
- Log level processing implementing the aho-corasik algorithm that searches for a list of given keywords simultaneously. It uses an EntryParser to extract information from the entries of interest

### ENTRY PARSER
- Entry level processing, divides the log entry into its basic components: log level, context, message, parameters
- can be extended with re recognition to handle specific cases


## CROSS SHARD ANALYSIS TOOL
Tool that validates that cross shard miniblocks are executed (and proposed) in strict order, without gaps or duplications.


INSTALL
Create a virtual environment and install the dependencies:

```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt --upgrade
export PYTHONPATH=.
```

INSTALL DEVELOPMENT DEPENDENCIES
```
pip install -r ./requirements-dev.txt --upgrade
```

EXAMPLE USAGE
```
python -m multiversx_cross_shard_analysis.gather_data --path /home/mihaela/Downloads/cross-shard-execution-anal-9afe696daf.zip
python -m multiversx_cross_shard_analysis.headers_timeline_report --run-name cross-shard-execution-anal-6cc663f7af
```
