# Map the age demo data to the Prem et al age bins.
# Generates a probability distribution over age bins for each acip group, i.e. P(age_bin | group)

import numpy as np
import pandas as pd

age_bins = np.array(
            [[0, 4], 
            [5, 9],
            [10, 14], 
            [15, 19], 
            [20, 24], 
            [25, 29],
            [30, 34], 
            [35, 39], 
            [40, 44],
            [45, 49], 
            [50, 54], 
            [55, 59], 
            [60, 64], 
            [65, 69],
            [70, 74], 
            [74, 120]])

def age_interp(x_bins_new, x_bins, y):
        """Interpolate parameters define in age groups to a new set of age groups"""
        x_mean_new = np.mean(np.array(x_bins_new), axis=1)
        x_mean = np.mean(np.array(x_bins), axis=1)
        return np.interp(x_mean_new, x_mean, y)


def read_national_health_survey_file(filename):

    survey_df = pd.read_csv(filename, skiprows=1, skipfooter=8, engine='python')
    survey_df = survey_df.loc[survey_df['Year'] == 2018]

    # Columns are 18-44, 45-64, 65-74, 75+
    survey_df = survey_df[['18-44 years', '45-64 years', '65-74 years', '75 and over']]
    survey_age_bins = np.array([[18, 44], [45, 64], [65, 74], [75, 120]])

    interp_res = age_interp(age_bins, survey_age_bins, survey_df.values[0])

    # Drop 65+ to avoid double counting
    interp_res[-3:] = 0.

    # Make 0 for < 15
    interp_res[0:3] = 0.

    return interp_res

def process_labor_bins(row, bins):

    values = row.values[1:].astype(float)

    # Interpolate
    interp_res = age_interp(age_bins, bins, values)

    # Make 0 for < 15
    interp_res[0:3] = 0.

    return interp_res

'''
ACIP Groups:
1a. Healthcare personnel + long-term care residents
1b. Frontline essential workers + persons aged 75+
1c. Persons aged 65-74, persons 18-64 with chronic conditions, 
   persons under 65 with cancer, persons 15-49 who are pregnant,
   smokers aged 16+, all other essential workers 

References:
https://www.cdc.gov/vaccines/acip/meetings/downloads/slides-2020-12/slides-12-20/02-COVID-Dooling.pdf
https://covid19vaccineallocation.org/
'''

# Employment data from US Bureau of Labor Statistics
# https://www.bls.gov/cps/cpsaat18b.htm
labor_data = pd.read_excel('group_age_data/cpsaat18b.xlsx', header=4)
labor_data = labor_data.rename(columns={'Unnamed: 0' : 'Industry'})
labor_data.columns = labor_data.columns.str.replace('\n', '')

# Drop columns we don't need
labor_data = labor_data.drop(columns=['Total, 16years and over', 'Median age'])
labor_age_bins = [[16, 19], [20, 24], [25, 34], [35, 44], [45, 54], [55, 64], [65, 120]]

# 1a. 
# Healthcare personnel: 
# Categories: Hospitals + Health services, except hospitals
healthcare_industries = ['Hospitals', 'Health services, except hospitals']
healthcare_workers = labor_data.loc[labor_data['Industry'].isin(healthcare_industries)].sum()
healthcare_arr = process_labor_bins(healthcare_workers,labor_age_bins)

# Long-term care: Assume all in the 65+ bins
longterm_care = np.array([0 if i < 13 else 1 for i in range(16)])

# 1b. 
# Frontline workers
frontline_1b = ['Educational services',
                'Manufacturing',
                'Child day care services',
                'Agriculture, forestry, fishing, and hunting',
                'Postal Service',
                'Bus service and urban transit',
                'Supermarkets and other grocery (except convenience) stores',
                'Convenience stores',
                'Pharmacies and drug stores',
                'Justice, public order, and safety activities',
                'General merchandise stores, including warehouse clubs and supercenters']

frontline_workers = labor_data.loc[labor_data['Industry'].isin(frontline_1b)].sum()
frontline_arr = process_labor_bins(frontline_workers, labor_age_bins)

# Remove 65+ to avoid double counting
frontline_arr[-3:] = 0.

# Persons aged 75+
aged_75 = np.array([0 if i < 15 else 1 for i in range(16)])

# 1c. 
# Persons aged 65-74 TODO
aged_65_74 = np.array([0 for i in range(16)])
aged_65_74[-3:-1] = 1.

# Persons under 65 with cancer
# National Health Interview Survey
# https://www.cdc.gov/nchs/nhis/ADULTS/www/index.htm
# Crude percentages of any cancer for adults aged 18 and over, United States, 2015-2018
percent_cancer = read_national_health_survey_file('group_age_data/any_cancer_by_age.csv')

# Persons with chronic conditions:
# National Health Interview Survey
# https://www.cdc.gov/nchs/nhis/ADULTS/www/index.htm
# Crude percentages of obesity for adults aged 18 and over, United States, 2015-2018 
percent_obesity = read_national_health_survey_file('group_age_data/obesity_percent_adults.csv')

# Crude percentages of all types of heart disease for adults aged 18 and over, United States, 2015-2018
percent_heart_disease = read_national_health_survey_file('group_age_data/heart_disease_percent_adults.csv')

# Crude percentages of emphysema for adults aged 18 and over, United States, 2015-2018
percent_emphysema = read_national_health_survey_file('group_age_data/emphysema_percent_adults.csv')

# Crude percentages of diabetes for adults aged 18 and over, United States, 2015-2018
percent_diabetes = read_national_health_survey_file('group_age_data/diabetes_percent_adults.csv')

# Crude percentages of kidney disease for adults aged 18 and over, United States, 2015-2018
percent_ckd = read_national_health_survey_file('group_age_data/kidney_disease_adults.csv')

# Take max of each
chronic_conditions = np.max(np.vstack((percent_obesity, 
                                percent_heart_disease, 
                                percent_emphysema, 
                                percent_ckd,
                                percent_diabetes)), axis=0)

# Persons 15-49 who are pregnant
# https://www.cdc.gov/nchs/data/nvsr/nvsr68/nvsr68_13-508.pdf
# Table 18. Births, by method of delivery and by age and race and Hispanic origin of mother: United States, 2018
birth_data = {
    'Under 20' : 181607, 
    '20-24' : 726175,
    '25-29' : 1099491,
    '30-34' : 1090697,
    '35-39' : 566786,
    '40-54' : 126956
}

birth_age_bins = [[15, 19], [20, 24], [25, 29], [30, 34], [35, 39], [40, 54]]
pregnant_data = age_interp(age_bins, birth_age_bins, list(birth_data.values()))

# Remove people < 15 and over 49
pregnant_data[0:3] = 0.
pregnant_data[10:] = 0.

# Smokers aged 16+
percent_smoker = read_national_health_survey_file('group_age_data/cigarette_smoking_percent_adults.csv')

# All other essential workers
essential_1c = ['Transportation and utilities',
                'Construction',
                'Food services and drinking places',
                'Financial activities',
                'Information',
                'Utilities',
                'Legal services']

essential_workers = labor_data.loc[labor_data['Industry'].isin(essential_1c)]

# Remove postal service and postal services as they were already counted
essential_workers = essential_workers.loc[~essential_workers['Industry'].isin(['Postal Service', 'Bus service and urban transit'])]
essential_workers = essential_workers.sum()
essential_arr = process_labor_bins(essential_workers, labor_age_bins)

# Remove 65+ to avoid double counting
essential_arr[-3:] = 0.

# Place in order
# 0. Healthcare personnel
# 1. Long term facility care residents
# 2. Frontline essential workers
# 3. Persons aged 75+
# 4. Persons aged 65-74
# 5. Persons aged 18-64 with obesity, diabetes, COPD (emphysema), heart disease, CKD
# 6. Persons under 65 with cancer
# 7. Pregnant people 15-49
# 8. Smokers aged 16+
# 9. Other essential workers

full_data = np.vstack((
            healthcare_arr,
            longterm_care,
            frontline_arr,
            aged_75,
            aged_65_74,
            chronic_conditions,
            percent_cancer,
            pregnant_data,
            percent_smoker,
            essential_arr))

full_data = full_data/full_data.sum(axis=1)[:, None] # normalize so each group is the PDF over the age groups

np.savetxt('acip_age_demos.csv', full_data, delimiter=',')
