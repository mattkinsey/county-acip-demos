# county-acip-demos

County level populations for each priority group in the ACIP recommendations. 

Scraped from https://covid19vaccineallocation.org/ (on 2021-01-07), they detail the methods used to estimate these populations [here](https://covid19vaccineallocation.org/assets/Vaccine_Allocation_Planner_for_COVID19_Methods.pdf).

This data is provided as-is, if you'd like the see the scripts used to scrap it please email matt@mkinsey.com

## Data Description
### county_acip_demos.csv
The file county_acip_demos.csv contains the following columns:
- 'adm2' -- The county FIPS code as an int (i.e. without leading 0s)
- 'group' -- An int identifying which of the priority groups the row is specifying
- 'phase' -- the overall ACIP phase that the group belongs to
- 'group_name' -- a plain string description of the group (as named on https://covid19vaccineallocation.org/)
- 'total_eligible' -- the int number of people in that county that are members of that group

### acip_conditional_probs.csv
Also included are the conditional probabilities of group membership.

This file is based off the conditional probabilities found in Appendix A of the [methods document](https://covid19vaccineallocation.org/assets/Vaccine_Allocation_Planner_for_COVID19_Methods.pdf) and was pulled from the google sheet available [here](https://docs.google.com/spreadsheets/d/1a-HffiAJUXQH2wb2inCtE6HHYEBYzDmWSlyGQFV-mhA/edit#gid=0) (the 'Matrix' sheet).

Each cell in this matrix represents the probability P(row|column), i.e. the probability of being in the row group if you are a member of the column group. NB: this is the transpose of the matrix in the google sheet.

Each row and column are labeled with the 'group' int corresponding to the 'group' column in county_acip_demos.csv.
