import pandas as pd
import numpy as np
import copy

class Setup:
    '''
        this is only valid for 2012 and after, when AFL expanded to the current 18 teams.
        
        file should be a json file that matches the time frame
        date_range should be a list of 4 digit integer years [2012, 2013, etc.]
        The list of teams is loaded in the function.  It is a constant from 2012 on.

        this setup function will convert the json file into a dataframe.

        '''
    team_list = ['Adelaide', 'Brisbane', 'Carlton', 'Collingwood', 'Essendon', 'Fremantle', 'Geelong', 'Gold Coast',
             'GWS', 'Hawthorn', 'Melbourne', 'North Melbourne', 'Port Adelaide', 'Richmond',
             'St. Kilda', 'Sydney', 'West Coast', 'Western Bulldogs']
    
    def __init__(self, file, date_range, teams = team_list):
        
        self.file = file
        self.date_range = date_range
        self.teams = teams
    
    def setup(self):
        
        new_season_team_PI = []
        for y, year in zip(self.date_range, range(len(self.date_range))):
            new_team_round_PI = []
            for t, team in zip(self.teams, range(len(self.teams))):
                new_round_PI = []

                for rnd in range(len(self.file[team][year])):

                    new_rtc_df = pd.DataFrame.from_dict(self.file[team][year][rnd])

                    new_round_PI.append(new_rtc_df)
                new_team_round_PI.append(new_round_PI)
            new_season_team_PI.append(new_team_round_PI)

        self.master_seasonPI_df = pd.DataFrame()


        for s in range(len(self.date_range)):
            for t in range(len(self.teams)):
                self.master_seasonPI_df = self.master_seasonPI_df.append(new_season_team_PI[s][t])


        self.master_seasonPI_df.reset_index(inplace = True)
        self.master_seasonPI_df.rename(columns={'index': 'Round'}, inplace = True)
        self.master_seasonPI_df['Round'] = self.master_seasonPI_df['Round'].str.replace('R','round')
        self.master_seasonPI_df.fillna(value = 0, inplace = True)

        self.with_ruck = self.master_seasonPI_df[self.master_seasonPI_df['R-HO'] != 0]

        self.with_ruck[['D-HO', 'F-HO', 'M-HO', 'R-HO']]

        self.with_ruck = self.with_ruck[self.with_ruck.loc[:] !=0].dropna(thresh = 4)

        self.no_ruck = self.master_seasonPI_df[self.master_seasonPI_df['R-HO'] == 0]

        self.no_ruck[['D-HO', 'F-HO', 'M-HO', 'R-HO']]

        self.no_ruck = self.no_ruck[self.no_ruck.loc[:] !=0].dropna(thresh = 4)

        self.baseline_with_ruck = self.with_ruck[['Season', 'D-HO', 'F-HO', 'M-HO', 'R-HO']].groupby('Season').mean()
        self.baseline_without_ruck = self.no_ruck[['Season', 'D-HO', 'F-HO', 'M-HO', 'R-HO']].groupby('Season').mean()

        self.test_df = copy.deepcopy(self.master_seasonPI_df)

        self.new_ruck_PI = pd.DataFrame(columns = ['R-HO', 'F-HO', 'D-HO', 'R-Age', 'R-Height', 'R-Weight'])

        # This gets me the indices where there are no ruck stats
        self.select_indices = list(np.where(self.test_df["R-HO"] == 0)[0])

        for index in self.select_indices:
            self.yiq = self.test_df.iloc[index]['Season']

            if self.test_df.iloc[index][3:-3].sum() != 0:

                if self.test_df.iloc[index]['D-HO'] > 0 and self.test_df.iloc[index]['F-HO'] > 0:

                    if self.test_df.iloc[index]['D-HO'] > self.baseline_with_ruck.loc[self.yiq]['D-HO'] and self.test_df.iloc[index]['F-HO'] > self.baseline_with_ruck.loc[self.yiq]['F-HO']:

                        self.new_rho = (self.test_df.iloc[index]['D-HO'] - self.baseline_with_ruck.loc[self.yiq]['D-HO']) + (self.test_df.iloc[index]['F-HO'] - self.baseline_with_ruck.loc[self.yiq]['F-HO'])
                        self.new_fho = self.baseline_with_ruck.loc[self.yiq]['F-HO']
                        self.new_dho = self.baseline_with_ruck.loc[self.yiq]['D-HO']
                        self.new_rage = (self.test_df.iloc[index]['D-Age'] + self.test_df.iloc[index]['F-Age']) / 2
                        self.new_rh = (self.test_df.iloc[index]['D-Height'] + self.test_df.iloc[index]['F-Height']) / 2
                        self.new_rw = (self.test_df.iloc[index]['D-Weight'] + self.test_df.iloc[index]['F-Weight']) / 2

                    else:

                        self.new_rho = 2.0
                        self.new_fho = self.test_df.iloc[index]['F-HO'] - 1.0
                        self. new_dho = self.test_df.iloc[index]['D-HO'] - 1.0
                        self.new_rage = (self.test_df.iloc[index]['D-Age'] + self.test_df.iloc[index]['F-Age']) / 2
                        self.new_rh = (self.test_df.iloc[index]['D-Height'] + self.test_df.iloc[index]['F-Height']) / 2
                        self.new_rw = (self.test_df.iloc[index]['D-Weight'] + self.test_df.iloc[index]['F-Weight']) / 2

                elif self.test_df.iloc[index]['D-HO'] > 0:

                    if self.test_df.iloc[index]['D-HO'] > self.baseline_with_ruck.loc[self.yiq]['D-HO']:

                        self.new_rho = (self.test_df.iloc[index]['D-HO'] - self.baseline_with_ruck.loc[self.yiq]['D-HO'])
                        self.new_fho = self.test_df.iloc[index]['F-HO']
                        self.new_dho = self.baseline_with_ruck.loc[self.yiq]['D-HO']
                        self.new_rage = self.test_df.iloc[index]['D-Age']
                        self.new_rh = self.test_df.iloc[index]['D-Height']
                        self.new_rw = self.test_df.iloc[index]['D-Weight']

                    else:

                        self.new_rho = 1.0
                        self.new_fho = self.test_df.iloc[index]['F-HO']
                        self.new_dho = self.test_df.iloc[index]['D-HO'] - 1.0
                        self.new_rage = self.test_df.iloc[index]['D-Age']
                        self.new_rh = self.test_df.iloc[index]['D-Height']
                        self.new_rw = self.test_df.iloc[index]['D-Weight']

                elif self.test_df.iloc[index]['F-HO'] > 0:

                    if self.test_df.iloc[index]['F-HO'] > self.baseline_with_ruck.loc[self.yiq]['F-HO']:

                        self.new_rho = (self.test_df.iloc[index]['F-HO'] - self.baseline_with_ruck.loc[self.yiq]['F-HO'])
                        self.new_fho = self.baseline_with_ruck.loc[self.yiq]['F-HO']
                        self.new_dho = self.test_df.iloc[index]['D-HO']
                        self.new_rage = self.test_df.iloc[index]['F-Age']
                        self.new_rh = self.test_df.iloc[index]['F-Height']
                        self.new_rw = self.test_df.iloc[index]['F-Weight']

                    else:

                        self.new_rho = 1.0
                        self.new_fho = self.test_df.iloc[index]['F-HO'] - 1.0
                        self.new_dho = self.test_df.iloc[index]['D-HO']
                        self.new_rage = self.test_df.iloc[index]['F-Age']
                        self.new_rh = self.test_df.iloc[index]['F-Height']
                        self.new_rw = self.test_df.iloc[index]['F-Weight']

                self.new_list = [self.new_rho, self.new_fho, self.new_dho, self.new_rage, self.new_rh, self.new_rw]

                self.new_ruck_PI.loc[index] = self.new_list
            else:
                pass

        self.nri = self.new_ruck_PI.index.tolist()
        self.nrc = self.new_ruck_PI.columns

        for i in self.nri:
            for c in self.nrc:

                self.master_seasonPI_df.loc[i, c] = self.new_ruck_PI.loc[i, c]


        self.index_names2 = self.master_seasonPI_df.loc[(self.master_seasonPI_df['Round'].isin(['round19', 'round20', 'round21', 'round22', 'round23'])) & (self.master_seasonPI_df['Season'] == '2020')].index
        self.master_seasonPI_df = self.master_seasonPI_df.drop(self.index_names2)
        self.master_seasonPI_df.replace({'Greater Western Sydney': 'GWS'}, inplace = True)
        self.master_seasonPI_df.replace({'round1': 'round01', 'round2': 'round02', 'round3': 'round03', 
                                         'round4': 'round04', 'round5': 'round05', 'round6': 'round06', 
                                         'round7': 'round07', 'round8': 'round08','round9': 'round09'}, inplace = True)
        self.master_seasonPI_df['Season'] = pd.to_numeric(self.master_seasonPI_df['Season'])

        return self.master_seasonPI_df

# New Class to set up Home-Away for all PI

class Home_Away:

	def __init__(self, home_fixture, away_fixture, master_df):
        
        self.home_fixture = home_fixture
        self.away_fixture = away_fixture
        self.master_df = master_df

	def home_away_setup(self):
	    '''
	    This takes a df of the fixtures, broken out by home and away and then combines them, using
	    the data from the master_df that was created with all of the PI for each season
	    
	    '''
	    # import pandas as pd

	    self.home_fixture.replace({'Greater Western Sydney': 'GWS'}, inplace = True)
	    self.away_fixture.replace({'Greater Western Sydney': 'GWS'}, inplace = True)

	    self.home_fixture['Game'] = self.home_fixture['Game'].str.lstrip(string.digits)
	    self.away_fixture['Game'] = self.away_fixture['Game'].str.lstrip(string.digits)

	    self.home_fixture.sort_values(by = ['Year', 'Round', 'Game'], axis = 0, ignore_index = True, inplace = True)
	    self.away_fixture.sort_values(by = ['Year', 'Round', 'Game'], axis = 0, ignore_index = True, inplace = True)

	    self.home_list = pd.merge(self.home_fixture, self.master_df, how = 'left', left_on = ['Year', 'Home', 'Round'],
	    	right_on = ['Season', 'Team', 'Round'])
	    self.away_list = pd.merge(self.away_fixture, self.master_df, how = 'left', left_on = ['Year', 'Away', 'Round'],
	    	right_on = ['Season', 'Team', 'Round'])

	    self.away_list.drop(['Team', 'Season'], axis = 1, inplace = True)
	    self.home_list.drop(['Team', 'Season'], axis = 1, inplace = True)
	    
	    home_list_stats = self.home_list.iloc[:,9:]
	    away_list_stats = self.away_list.iloc[:,8:]

	    home_list_info = self.home_list.iloc[:,:9]
	    away_list_info = self.away_list.iloc[:,:8]


	    # This is the key of the analysis, I subtract the away PI from the home PI
	    home_away_net = home_list_stats.subtract(away_list_stats, fill_value = None)


	    # Here I merge the info for each match together and create the Relative Ladder Position (RLP) column
	    # and manually set up categorical variables, rather than using one hot encoding
	    info = home_list_info.merge(away_list_info, how = 'left', left_index = True, right_index = True)

	    info['RLP'] = info['LP-H'] - info['LP-A']

	    condition1 = info['Venue'] == info['Home Field-H'] 
	    condition2 = info['Home Field-H'] == info['Home Field-A']

	    condition3 = info['Venue'] != info['Home Field-H'] 
	    condition4 = info['Home Field-H'] != info['Home Field-A']


	    (info['Net Score'], info['Intrastate'], info['Same / Neutral Venue']) = \
	    ((info['Home Score'] - info['Away Score']), np.where(info['Home State'] == info['Away State'], 0, 1), 
	     np.where((condition1 & condition2) | (condition3 & condition4), 1, 0))

	    info['Clash'] = np.where((info['Intrastate'] == 0) & (info['Same / Neutral Venue'] == 1), 1, 0)
	    # info['Winner'] = np.where(info['Net Score'] >0, 'Home', 'Away')

	    ###

	    conditions = [info['Net Score'] > 0, info['Net Score'] < 0, info['Net Score'] == 0]
	    choices = ['Home', 'Away', 'Draw']

	    info['Winner'] = np.select(conditions, choices, default = np.nan)

	    ###

	    # Here I reconstruct and finalize the information portion of the dataframe, merge it with the PI, and then reorder it.

	    info = info[['Year_x','Home', 'Away', 'Intrastate', 'Same / Neutral Venue', 'Clash', 'RLP','Net Score', 'Winner']]
	    info = info.rename(columns = {'Year_x': 'Season'})

	    home_away_net_complete = home_away_net.join(info)

	    home_away_net_complete['Round'] = home_list_info['Round']
	    home_away_net_complete['Game'] = home_list_info['Game']

	    col = home_away_net_complete.pop('Round')
	    home_away_net_complete.insert(0, col.name, col)
	    col = home_away_net_complete.pop('Game')
	    home_away_net_complete.insert(0, col.name, col)
	    col = home_away_net_complete.pop('Season')
	    home_away_net_complete.insert(0, col.name, col)
	    col = home_away_net_complete.pop('Away')
	    home_away_net_complete.insert(0, col.name, col)
	    col = home_away_net_complete.pop('Home')
	    home_away_net_complete.insert(0, col.name, col)
	    
	    d_cols = [col for col in master_df.columns if col.startswith('D-')]
	    f_cols = [col for col in master_df.columns if col.startswith('F-')]
	    m_cols = [col for col in master_df.columns if col.startswith('M-')]
	    r_cols = [col for col in master_df.columns if col.startswith('R-')]

	    hd = home_list_stats[d_cols]
	    af = away_list_stats[f_cols]
	    hf = home_list_stats[f_cols]
	    ad = away_list_stats[d_cols]
	    new_computed_column_basis = ['DI', 'KI', 'MK', 'HB', 'GL', 'BH', 'HO', 'TK', 'RB', 'IF', 'CL', 'CG', 'FF', 'FA', 'CP',
	                                 'UP', 'CM', 'MI', '1%', 'BO', 'AMG', 'GA', 'Height', 'Weight', 'Age']

	    new_posgru = [hd, af, hf, ad]

	    for npg in new_posgru:
	        npg.columns = new_computed_column_basis

	    hdaf = hd - af
	    hfad = hf - ad
	    ####
	    pos_prefixes = ['HDAF', 'HFAD']

	    new_delta_headers = []
	    for pos in pos_prefixes:
	        for stat in new_computed_column_basis:
	            new_col_head = pos+'-'+stat
	            new_delta_headers.append(new_col_head)
	    hdaf_headers = new_delta_headers[:25]
	    hfad_headers = new_delta_headers[25:]

	    hdaf.columns = hdaf_headers
	    hfad.columns = hfad_headers

	    hdaf_avmg = home_list_stats['D-AMG'] - away_list_stats['F-AMG']
	    hfad_avmg = home_list_stats['F-AMG'] - away_list_stats['D-AMG']
	    ####

	    pos_dfs = [hdaf, hfad]

	    for pp, pd in zip(pos_prefixes, pos_dfs):
	        pd[pp+'-TM'] = pd[pp+'-MK'] + pd[pp+'-CM'] + pd[pp+'-MI']
	        pd[pp+'-TP'] = pd[pp+'-CP'] + pd[pp+'-UP']
	        pd[pp+'-TT'] = pd[pp+'-FA'] + pd[pp+'-CG']

	    hdaf_short = hdaf[['HDAF-TM', 'HDAF-TP', 'HDAF-FF', 'HDAF-TT', 'HDAF-Height', 'HDAF-Weight', 'HDAF-Age']]
	    hfad_short = hfad[['HFAD-TM', 'HFAD-TP', 'HFAD-FF', 'HFAD-TT', 'HFAD-Height', 'HFAD-Weight', 'HFAD-Age']]

	    short_stack = hfad_short.join(hdaf_short)

	    # I need to move these special columns to the end.
	    home_away_net_complete = home_away_net_complete.join(short_stack)

	    # Here I'm just re-ordering my columns to make it easier to normalize later.

	    home_away_net_complete = home_away_net_complete[['Home', 'Away', 'Season', 'Game', 'Round', 'D-DI', 'D-KI', 'D-MK', 'D-HB', 
	                                                     'D-GL', 'D-BH', 'D-HO', 'D-TK', 'D-RB', 'D-IF', 'D-CL', 'D-CG', 'D-FF', 
	                                                     'D-FA', 'D-CP', 'D-UP', 'D-CM', 'D-MI', 'D-1%', 'D-BO', 'D-AMG','D-GA', 'D-Height', 
	                                                     'D-Weight', 'D-Age', 'F-DI', 'F-KI', 'F-MK', 'F-HB', 'F-GL', 'F-BH', 'F-HO', 
	                                                     'F-TK', 'F-RB', 'F-IF', 'F-CL', 'F-CG', 'F-FF', 'F-FA', 'F-CP', 'F-UP', 
	                                                     'F-CM', 'F-MI', 'F-1%', 'F-BO', 'F-AMG','F-GA', 'F-Height', 'F-Weight', 'F-Age', 
	                                                     'M-DI', 'M-KI', 'M-MK', 'M-HB', 'M-GL', 'M-BH', 'M-HO', 'M-TK', 'M-RB', 
	                                                     'M-IF', 'M-CL', 'M-CG', 'M-FF', 'M-FA', 'M-CP', 'M-UP', 'M-CM', 'M-MI', 
	                                                     'M-1%', 'M-BO', 'M-AMG','M-GA', 'M-Height', 'M-Weight', 'M-Age', 'R-DI', 'R-KI', 
	                                                     'R-MK', 'R-HB', 'R-GL', 'R-BH', 'R-HO', 'R-TK', 'R-RB', 'R-IF', 'R-CL', 
	                                                     'R-CG', 'R-FF', 'R-FA', 'R-CP', 'R-UP', 'R-CM', 'R-MI', 'R-1%', 'R-BO', 'R-AMG',
	                                                     'R-GA', 'R-Height', 'R-Weight', 'R-Age', 'HFAD-TM', 'HFAD-TP', 'HFAD-FF', 
	                                                     'HFAD-TT', 'HFAD-Height', 'HFAD-Weight', 'HFAD-Age', 'HDAF-TM', 'HDAF-TP',
	                                                     'HDAF-FF', 'HDAF-TT', 'HDAF-Height', 'HDAF-Weight', 'HDAF-Age', 'Intrastate',
	                                                     'Same / Neutral Venue', 'Clash', 'RLP', 'Net Score', 'Winner']]
	    
	    home_away_net_complete.drop(home_away_net_complete[home_away_net_complete['Winner'] == 'Draw'].index, inplace = True)

	    # Here I eliminate all goal-scoring features (Goals, Behinds, and Goal Assists)

	    han_cols = home_away_net_complete.columns
	    no_goals = [g for g in han_cols if g.endswith(('GL', 'BH', 'GA'))]

	    home_away_net_complete_AMG_ng = home_away_net_complete.drop(no_goals, axis = 1)

	    
	    return home_away_net_complete_AMG_ng