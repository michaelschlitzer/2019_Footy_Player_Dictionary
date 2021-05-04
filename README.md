# 2019_Footy_Player_Dictionary

Prepatory Work File

I have included the Prepatory work file, for you to examine, but I would not recommend that you run it because it takes a long time to run.

Its primary purpose is to read from the CSV files in this repository and then, critically, scrape the information from AFLtables.com to gather the basic information for the analysis.  Seasons 2012-2019 all had the same number of rounds.  Season 2020 was cut short due to COVID, so I ran that separately and padded the data with NaNs to maintain a consistent shape across all seasons.

The most critical part of this Prepatory work file is to reorganize the data from the website.  AFLtables.com has the data organized by Performance Indicator (PI) for all games, but I need the data to be organized by game with all of the PI for that game visible, so it took a good bit of reorganization.  All of this information is per player.

Once I have the information for each team and player for every game for every season, I merge the data with player position data and then group by Position Group (POS).  I split the data, executing a SUM for each round on the PI, and a MEAN on the biometric data to get the average height, weight, and age for each POS group.

I take this information and save it as a JSON file, which you can pick up just by running the Capstone file.

Capstone File

This is the main file that you should run.  It pulls from all of the other files here, formats the dataframe and runs all of the different machine learning classifiers that are at the heart of the project.
