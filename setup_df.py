import pandas as pd
import numpy as np
import copy

class Setup:
    '''
        this is only valid for 2012 and after, when AFL expanded to the current 18 teams.
        
        file should be a json file
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