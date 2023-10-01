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
	- adjust assessment results
		- analyse entered data to detect cyclic tendencies 
		- if calculated/inserted alternatives contain are related to data with such tendencied, on assessment criteria's weigths must be adjusted depending on the positions of data point withing the detected season
	- sort alternatives
		pick methods and/or, if necessary, specifics
		sort out non-pareto-optimal
		rank remaining alts 
		show list of methods used and their preferred alts
- interface specifics
	- local, but must utilise UI states to ensure data persistency
	- db is on SQLite, but must allow manual inputs or imports from csv/xlsx
	- must allow export of alternatives' rankings to csv/xlsx
- app modules
	- alternatives calculation window (data is imported from a db file, user can select tables/corteges to work with and clean data, if needed)
	- alternatives input window (no calculation or automation through db relations here, but user can use import mode from csv/xlsx or input data manually)
	- assessment settings window (user can set sorting out pareto-non-oprimals on or off, select MCDM methods and input related additional inputs such as criteria weigths, thresholds or concordance)
	- assessment results window (if app was set to sort out, user is shown what slternatives methods were applied to; listed preferred alternatives as per selected methods)