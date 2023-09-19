TA
- functions required
	- prepare alternatives
		- input alternatives as raw data
		- make alternatives
			init db file 
			pick a function 
			- if table has relations - set related entities as possible args
			allow user to add/delete args
			- if table has relations - compose alts based on the keys
			- if table does not have relations join func and args as is
	- sort alternatives
		pick methods and/or, if necessary, specifics
		sort out non-pareto-optimal
		rank remaining alts 
		show list of methods used and their preferred alts
- interface specifics
	- local, but must use UI states to ensure data persistency
	- db is on SQLite, but must allow manual inputs or imports from csv/xlsx
	- must allow export of alternatives' rankings to csv/xlsx
- app modules
	- main window (input data - manually/auto; continue work with prev imported db)
	- raw data window (if imported, to clean / reselect)
	- alternatives window (to select assessment method and it's characteristics)
	- assessment results window (pareto-optimised; method 1..n results and generalised rule)
