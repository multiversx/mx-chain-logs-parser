# mx-chain-logs-parser
Logs parsing utilities and applications

## LOGS PARSER TOOLS:
The tool provides general abstract classes that can be useful for parsing logs.
In order to create an application that uses off-line parsing of logs files, these classes must be inherited and methods should be implemented for that particular case.

### ARCHIVE HANDLER
- General application processing class, that loops through the nodes in the downloaded logs archive and calls its NodeLogsChecker instance for each one of them
- run level methods should be implemented in inheriting classes

### NODE LOGS CHECKER
- Node level processing, that loops through individual log files for a node and calls its instance of the AhoCorasickParser to search for entries with pre-defined key phrases
- node level methods should be implemented in inheriting classes

### AHO-CORASICK PARSER
- Log level processing implementing the Aho-Corasick algorithm that searches for a list of given keywords simultaneously. It uses an *EntryParser* to extract information from the entries of interest

### ENTRY PARSER
- Entry level processing, divides the log entry into its basic components: log level, context, message, parameters
- can be extended with re recognition to handle specific cases


## CROSS SHARD ANALYSIS TOOL
This tool validates that cross shard mini-blocks are executed (and proposed) in strict order, without gaps or duplications.
It uses color coded data to illustrate each state in the processing. A configuration file (issues.py) is provided to signal certain issues with the miniblock production.

The tool creates a run specific folder under Reports that includes parsed headers in the *Shards* subfolder, mini-blocks in the *Miniblocks* folder.  
The generated reports will also be included in this folder, in individual sub-folders named after the respective report: 
- **MiniblocksShardTimeline** contains a report that goes through rounds and displays what mini-blocks where proposed, executed or notarized for each shard; individual pdf files are generated for each epoch; 
- **MiniblocksTimelineDetails** will produce a timeline of mini-blocks for each shard, type of miniblock and other information is included for each one of them; 
- **NonceTimeline** ; will produce a timeline of headers processed, originating from each shard. Alarms, like round gaps, missing  are representedd by colored borders;
- **NonceAlarms** this report is similar to the NonceTimeline report, but only includes headers that have issues. The report is divided into chapters for each type of alarm. A header may be included in more than one such category, depending on its characteristics. 

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
python -m multiversx_cross_shard_analysis.gather_data --path ~/Downloads/cross-shard-execution-anal-9afe696daf.zip
```
where the argument --path is mandatory, describing the path to the zip file containing the logs.
The command will also generate all reports available, saving them inside a subfolder of Reports with the same name as the zip file provided.

In order to run a specific report from the report folder:
```
python -m multiversx_cross_shard_analysis.headers_timeline_report --run-name cross-shard-execution-anal-6cc663f7af
``` 
where --run-name is the name of the subfolder where the run's files reside.