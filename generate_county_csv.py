import glob
import us
import pandas as pd
from functools import partial
import addfips
af = addfips.AddFIPS()
county_name_fixes = {'Louisiana':{'LaSalle': 'La Salle'}, "New Mexico":{'DoÃƒÂ±a Ana':'Dona Ana'}}

all_files = glob.glob('raw_scrapped_data/*.csv')
state_fips_map = us.states.mapping('name', 'fips')

phase_map = {
        '0': '1a',
        '1': '1a',
        '2': '1b',
        '3': '1b',
        '4': '1c',
        '5': '1c',
        '6': '1c',
        '7': '1c',
        '8': '1c',
        '9': '1c',
    }

states = set()
groups = set()
for f in all_files:
    f = f.split('/')[-1]
    state, num = f[:-4].split('_')
    states.add(state)
    groups.add(num)

dfs = []
group_map = {}
state_fips_map = us.states.mapping('name', 'fips')
for state in states:
    state_fips=state_fips_map[state]
    for num in groups:
        fname = state+'_'+num+'.csv'
        data = pd.read_csv('raw_scrapped_data/'+state+'_'+num+'.csv', skiprows=1)
        group_name = data['County'].iloc[-1]
        if num in group_map.keys():
            if group_map[num] != group_name:
                print('something is wrong with ' + fname)

        else:
            group_map[num] = group_name
        #from IPython import embed
        #embed()
        cities = data.County.str.contains(' City')
        if cities.any() and state != 'Alaska':
            data['County'][~cities] = data.County.loc[~cities] + ' County'
        data = data.iloc[:-3].set_index('County').astype(float).reset_index()
        county_mapper = partial(af.get_county_fips, state=state)
        #print(data)
        if state in county_name_fixes.keys():
            fix_mask = data.County.isin(county_name_fixes[state].keys())
            data.County.loc[fix_mask] = data['County'].loc[fix_mask].map(county_name_fixes[state])
        data['adm2'] = data['County'].apply(county_mapper)
        data['group'] = num
        data['group_name'] = group_name
        data['phase'] = data.group.map(phase_map)
        
        unmapped = data.loc[data.adm2.isna()]
        if len(unmapped):
            #from IPython import embed
            #embed()
            print(state, unmapped.County)
        dfs.append(data)

df = pd.concat(dfs)

df.drop(columns=['Courses Allocated', 'Vaccine Allocation%'], inplace=True)
df['adm2'] = df['adm2'].astype(int)
df['group'] = df['group'].astype(int)
df = df.set_index(['adm2', 'group']).sort_index()
df.drop(columns=['County'], inplace=True)
df.rename(columns={'Total Eligible People': 'total_eligible'}, inplace=True)
df = df[['phase','group_name','total_eligible']]
df['total_eligible'] = df['total_eligible'].astype(int)

#insert zeros for any missing rows
# there's probably a better way to do this...
new_index = pd.MultiIndex.from_product(df.index.levels)
final_df = df.reindex(new_index)
nan_rows = final_df.loc[final_df.isna().any(1)]
nan_rows['total_eligible'] = 0
for group in nan_rows.reset_index().group.unique():
    tmp = df.reset_index().set_index('group').loc[group].head(1)
    nan_rows.loc[nan_rows.index.get_level_values('group')== group,'phase'] = tmp.phase.item()
    nan_rows.loc[nan_rows.index.get_level_values('group')== group,'group_name'] = tmp.group_name.item()

df = df.reset_index().merge(nan_rows.reset_index(), how='outer')
df = df.set_index(['adm2', 'group']).sort_index()

df.to_csv('county_acip_demos.csv', index=True)
