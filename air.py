import streamlit as st
import altair as alt
import pandas as pd

def load_data():
    df = pd.read_csv("Air Crash Full Data Updated_2024.csv")

    # clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_") \
        .str.replace("(", "", regex=False).str.replace(")", "", regex=False) \
        .str.replace("/", "_")
    print(" columns ;",df.columns)
    
    # replace blank strings with NaN for object columns
    #df[df.select_dtypes(include='object').columns] = df.select_dtypes(include='object').replace
    
    
    print(df.head())
    # now fill essential missing values
    df['country_region'] = df['country_region'].fillna("Unknown")#df.get('country_region', pd.Series()).fillna("Unknown")
    df['operator'] = df['operator'].fillna('Unknown')
    df['aircraft_manufacturer'] = df['aircraft_manufacturer'].fillna('Unknown')#df.get('aircraft_manufacturer', pd.Series()).fillna('Unknown')

    # convert numeric columns
    df['year'] = pd.to_numeric(df.get('year', pd.Series()), errors='coerce')
    df['day'] = pd.to_numeric(df.get('day', pd.Series()), errors='coerce')
    df['abroad'] = pd.to_numeric(df.get('abroad', pd.Series()), errors='coerce')
    df['fatalities_air'] = pd.to_numeric(df.get('fatalities_air', pd.Series()), errors='coerce')
    df['ground'] = pd.to_numeric(df.get('ground', pd.Series()), errors='coerce') 
                                                           

    # map month names to numbers
    month_map = {
    'January': 1, 'Feburary': 2, 'March': 3, 'April': 4, 
    'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12
}
    df["month_num"] = df['month'].map(month_map)

# create a datetime column from year and month_num
    df['month_date'] = pd.to_datetime(
        dict(year=df['year'], month=df['month_num'], day=1),
        errors="coerce"
    )

# add month name for charts
    df['month_name'] = df['month_date'].dt.month_name()

# add decade/period bins
    bins = [1908, 1920, 1932, 1944, 1956, 1968, 1980, 1992, 2004, 2016, 2020, 2024]
    labels = [
        "Early 1910s", "Mid 1920s", "Late 1930s", "Early 1940s",
        "Mid 1950s", "Late 1960s", "Early 1970s", "Late 1980s",
        "Early 2000s", "Mid 2010s", "Early 2020s"
    ]
    df['year_bin'] = pd.cut(df['year'], bins=bins, labels=labels, include_lowest=True)

    # drop exact duplicates
    df.drop_duplicates(inplace=True)
    return df

# Load data
df = load_data()

# Streamlit app layout
st.title('Air Crash Full Data Updated_2024.csv')
st.sidebar.header('Filters')

# Sidebar filters
#filters = {
#    "year": df["year"].dropna().unique(),
#    "quarter": df["quarter"].dropna().unique(),
#    "month": df["month"].dropna().unique(),
#}
filters = {
    "year": df["year"].dropna().unique().tolist(),
    "quarter": df["quarter"].dropna().unique().tolist(),
    "month": df["month"].dropna().unique().tolist(),
}

# Store user selections
selected_filters = {}
for key, options in filters.items():
    selected_filters[key] = st.sidebar.multiselect(key.capitalize(), sorted(options))

# Apply filters
filtered_df = df.copy()
for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_df = filtered_df[filtered_df[key].isin(selected_values)]

# Display data
st.dataframe(filtered_df.head())
print (filtered_df.columns)
# Calculations
no_of_fatalities = len(filtered_df)
total_year = filtered_df["year"].sum()
sum_of_fatalities = filtered_df["fatalities_air"].sum()
no_of_aircrafts = filtered_df["aircraft"].nunique()

# Metric display
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Fatality Records", no_of_fatalities)

with col2:
    st.metric("Sum of Years", int(total_year))

with col3:
    st.metric("Total Fatalities (Air)", int(sum_of_fatalities))

with col4:
    st.metric("Unique Aircraft", int(no_of_aircrafts))

# Top 5 years with highest fatalities
st.subheader("Top 5 Years With Highest Fatalities")
crashes_per_year = (
    filtered_df.groupby("year")["fatalities_air"]
    .sum()
    .nlargest(5)
    .reset_index()
)

st.write(crashes_per_year)

# Bar chart
if not crashes_per_year.empty:
    st.subheader("Top 5 Yearly Fatalities (Bar Chart)")
    chart = alt.Chart(crashes_per_year).mark_bar().encode(
        x=alt.X('fatalities_air:Q', title="Total Fatalities"),
        y=alt.Y("year:N", sort='-x', title="Year"),
        color=alt.Color("year:N", scale=alt.Scale(scheme='category20'), legend=None)
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data to display for the selected filters.")

top_countries = (
    filtered_df.groupby("country_region")["fatalities_air"]
    .sum().nlargest(5).reset_index()
)

st.subheader("Top 5 Countries by Fatalities")
pie_chart = alt.Chart(top_countries).mark_arc().encode(
    theta=alt.Theta(field="fatalities_air", type="quantitative"),
    color=alt.Color("country_region:N", scale=alt.Scale(scheme='dark2')),
    tooltip=["country_region:N", "fatalities_air:Q"]
).properties(height=300)

st.altair_chart(pie_chart, use_container_width=True)

print(crashes_per_year)
