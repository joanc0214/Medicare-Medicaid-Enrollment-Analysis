# Import libraries
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
file_path = 'MMLEADS_PUF_V2.0_2006-2012_02.2019.xlsx'
sheet_name = 'PUF_2006'  # Replace with the appropriate sheet name
data = pd.read_excel(file_path, sheet_name=sheet_name, header=1)

# Filter relevant columns
data.columns = data.columns.str.strip()
columns_of_interest = ['State', 'Number of People', 'Number of People with FFS', 
                       'Percent under 40 Years', 'Percent between 40-64 Years', 
                       'Percent between 65-84 Years', 'Percent 85+ Years', 
                       'Percent Female', 'Percent Male', 'Percent Non-Hispanic White', 
                       'Percent African American', 'Percent Hispanic', 
                       'Percent Asian or Pacific Islander', 'Percent American Indian or Alaska Native', 
                       'Percent Other or Unknown Race', 'Percent of Medicaid enrollees with MAS - Receiving Cash or Section 1931', 
                       'Percent of Medicaid enrollees with MAS - Medically Needy', 
                       'Percent of Medicaid enrollees with MAS - Poverty Related', 
                       'Percent of Medicaid enrollees with MAS - 1115 Demonstration Expansion', 
                       'Percent of Medicaid enrollees with MAS - unclassified or unknown']


# Replace '*' and '.' with NaN for proper numeric conversion BEFORE fillna
data_filtered = data[columns_of_interest].replace({'*': pd.NA, '.': pd.NA})

# Ensure 'State' remains as string
data_filtered['State'] = data_filtered['State'].astype(str).str.strip()

# Convert only numeric columns
numeric_cols = data_filtered.columns.drop('State')
data_filtered[numeric_cols] = data_filtered[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Handle missing values (if any) AFTER proper replacement
data_filtered = data_filtered.fillna(0)  # Replace missing values with 0 or another appropriate strategy

# Group by state and calculate summary statistics
state_summary = data_filtered.groupby('State').agg({
    'Number of People': 'sum',
    'Percent under 40 Years': 'mean',
    'Percent between 40-64 Years': 'mean',
    'Percent between 65-84 Years': 'mean',
    'Percent 85+ Years': 'mean',
    'Percent Female': 'mean',
    'Percent Male': 'mean',
    'Percent Non-Hispanic White': 'mean',
    'Percent African American': 'mean',
    'Percent Hispanic': 'mean',
    'Percent Asian or Pacific Islander': 'mean',
    'Percent American Indian or Alaska Native': 'mean',
    'Percent Other or Unknown Race': 'mean'
}).reset_index()

# Filter out 'National' row
data_filtered = data_filtered[data_filtered['State'] != 'National']

# Calculate enrollment percentages by state
enrollment_by_state = data_filtered.groupby('State')['Number of People'].sum().reset_index()
enrollment_by_state['Enrollment Percentage'] = (enrollment_by_state['Number of People'] / enrollment_by_state['Number of People'].sum()) * 100

# Sort by enrollment percentage
enrollment_by_state = enrollment_by_state.sort_values(by='Enrollment Percentage', ascending=False)
print(enrollment_by_state)

# Create a choropleth map of enrollment percentages by state
fig = px.choropleth(
    enrollment_by_state,
    locations='State',
    locationmode='USA-states',
    color='Enrollment Percentage',
    scope='usa',
    title='Medicare-Medicaid Enrollment Percentage by State',
    color_continuous_scale='Blues'
)

# Save the map as an HTML file
fig.write_html('enrollment_by_state_map.html')


## Race Demographics

# Load all sheets except the first one
df_excel = pd.read_excel(file_path, sheet_name=None, header=1)
df_excel.pop(list(df_excel.keys())[0])  # Remove first sheet

columns_of_interest = [
    "Percent Non-Hispanic White",
    "Percent African American",
    "Percent Hispanic",
    "Percent Asian or Pacific Islander",
    "Percent American Indian or Alaska Native",
    "Percent Other or Unknown Race"
]

df_filtered_all_sheets = {}

for sheet_name, df in df_excel.items():
    try:
        filtered_df = df[[col for col in columns_of_interest if col in df.columns]]
        row = filtered_df.iloc[2]  # Select the third row (index 2)
        df_filtered_all_sheets[sheet_name.split('_')[1]] = row  # Use year as key
    except KeyError as e:
        print(f"Warning: Column(s) not found in sheet '{sheet_name}': {e}")

# Convert to DataFrame and clean up
df_combined = pd.DataFrame(df_filtered_all_sheets).transpose().reset_index().rename(columns={'index': 'Year'})

# Generates line plot
plt.figure(figsize=(10, 6))
sns.lineplot(x='Year', y='Percent Non-Hispanic White', data=df_combined, label='Non-Hispanic White', marker='o')
sns.lineplot(x='Year', y='Percent African American', data=df_combined, label='African American', marker='o')
sns.lineplot(x='Year', y='Percent Hispanic', data=df_combined, label='Hispanic', marker='o')
sns.lineplot(x='Year', y='Percent Asian or Pacific Islander', data=df_combined, label='Asian or Pacific Islander', marker='o')
sns.lineplot(x='Year', y='Percent American Indian or Alaska Native', data=df_combined, label='American Indian or Alaska Native', marker='o')
sns.lineplot(x='Year', y='Percent Other or Unknown Race', data=df_combined, label='Other or Unknown Race', marker='o')

plt.title('Percent Distribution of Different Racial Groups (2006-2012)')
plt.xlabel('Year')
plt.ylabel('Percent')
plt.legend(title='Racial Groups')
plt.grid(True)
plt.tight_layout()

# Save the line plot as an image
plt.savefig('line_plot.png')

# Create an HTML file to display both plots 
html_content = f"""
<html>
<head>
    <title>Combined Data Visualization</title>
</head>
<body>
    <h1>Medicare-Medicaid Enrollment and Racial Distribution</h1>
    <h2>Enrollment by State</h2>
    <iframe src="enrollment_by_state_map.html" width="1000" height="600"></iframe>
    <h2>Percent Distribution of Different Racial Groups (2006-2012)</h2>
    <img src="line_plot.png" width="800">
</body>
</html>
"""

# Save the HTML file
with open('combined_visualization.html', 'w') as f:
    f.write(html_content)