# 2019_Footy_Player_Dictionary

Prepatory Work File

I have included the Prepatory work file, for you to examine, but I would not recommend that you run it because it takes a long time to run.

Its primary purpose is to read from the CSV files in this repository and then, critically, scrape the information from AFLtables.com to gather the basic information for the analysis.  Seasons 2012-2019 all had the same number of rounds.  Season 2020 was cut short due to COVID, so I ran that separately and padded the data with NaNs to maintain a consistent shape across all seasons.

The most critical part of this Prepatory work file is to reorganize the data from the website.  AFLtables.com has the data organized by Performance Indicator (PI) for all games, but I need the data to be organized by game with all of the PI for that game visible, so it took a good bit of reorganization.  All of this information is per player.

Once I have the information for each team and player for every game for every season, I merge the data with player position data and then group by Position Group (POS).  I split the data, executing a SUM for each round on the PI, and a MEAN on the biometric data to get the average height, weight, and age for each POS group.

I take this information and save it as a JSON file, which you can pick up just by running the Capstone file.

Capstone File

Here, I begin by reading the JSON file that I created in the Prepatory Work file and convert that nested dictionary into a flat data frame with every game in every season stacked on top of the other.

Here, I have to do some cleanup for one POS, the Ruck.  Most teams only carry one Ruck and so, if the Ruck sustains an injury, they have to press another position player into that role.  There are enough games throughout the sample where there are no Ruck stats.  It is clear that the Ruck role must be filled, and the primary, unique PI for a Ruck is the Hit Out (HO).  So, I computed the average number of HO for all other position groups when there was a ruck in the game and, moved the difference between the Forward or Defender HO and that average number over to the Ruck slot for HO.  If the number was extremely low (this only happened in two cases), I only subtracted 1 HO from the other POS and moved it to the Ruck column.  Then, for biometric data I took the average (if the HO were shared between POS) or the same number (if only one POS filled the Ruck role).

So, at this point, I have a dataframe with 3,472 rows (representing individual games) and  99 features with three features being identifiers (Season, Team, Round).
