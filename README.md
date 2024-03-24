# PhonePe Pulse Data Exploration Project with Streamlit, SQL, and Pandas
This project provides a user-friendly, interactive dashboard for exploring PhonePe Pulse data using Python libraries: Streamlit, SQLite, and Pandas.

**View App:** https://phonepe-pulse-guvi.streamlit.app/ 

**Demo:** https://www.linkedin.com/posts/aishwarya-velmurugan_hi-everyone-im-excited-to-share-my-latest-activity-7177355823961051136-r7Uz?utm_source=share&utm_medium=member_desktop

**Data:** https://github.com/PhonePe/pulse.git

**Reference:** https://www.phonepe.com/pulse/explore/transaction/2023/4/   
<br>

# PhonePe-Pulse
PhonePe Pulse is a data product offered by PhonePe, a leading digital payments platform in India. It provides insights and trends based on anonymized and aggregated transaction data collected through the PhonePe app.   


This data has been structured to provide details of the following three sections with data cuts on Transactions, Users, and Insurance of PhonePe Pulse - Explore tab.

**Aggregated** - Aggregated values of various payment categories as shown under the Categories section


**Map** - Total values at the State and District levels.


**Top** - Totals of top States / Districts /Pin Codes


All the data provided in these folders is in JSON format.
<br>

# Workflow
## Step 1: Prerequisites
Install and Import the following libraries
- Python 3.x (https://www.python.org/downloads/)
- Streamlit (pip install streamlit)
- Streamlit option menu (pip install streamlit-option-menu)
- sqlite3 (pip install db-sqlite3)
- Pandas (pip install pandas)
- json (pip install jsons)   
<br>

## Step 2: Clone this repository
Clone the pulse data repository using VS-Code:
- Open a new VS-Code window.
- Open the terminal and enter
```python
git clone https://github.com/PhonePe/pulse.git
```
<br>  

## Step 3: Data transformation
The pulse data is broken down state-wise, year-wise, and quarter-wise in a JSON file. The data is transformed into column-wise records of the data frame using the PANDAS library.
```python
# Aggregated-Transaction
path = "pulse/data/aggregated/transaction/country/india/state/"
Agg_state_list = os.listdir(path)
clm={'State':[], 'Year':[],'Quater':[],'Transaction_type':[], 'Transaction_count':[], 'Transaction_amount':[]}

for i in Agg_state_list:
    p_i = path + i + "/"
    Agg_yr_list = os.listdir(p_i)
    for j in Agg_yr_list:
        p_j = p_i + j + "/"
        Agg_Q_list = os.listdir(p_j)
        for k in Agg_Q_list:
            p_k = p_j + k
            Data = open(p_k,'r')
            D = json.load(Data)
            for z in D['data']['transactionData']:
                Name = z['name']
                count = z['paymentInstruments'][0]['count']
                amount = z['paymentInstruments'][0]['amount']
                clm['Transaction_type'].append(Name)
                clm['Transaction_count'].append(count)
                clm['Transaction_amount'].append(amount)
                clm['State'].append(i)
                clm['Year'].append(j)
                clm['Quater'].append(int(k.strip('.json')))
#Succesfully created a dataframe
Agg_Trans = pd.DataFrame(clm)
```
The generated data is stored as .csv in the file location.
```python
Agg_Trans.to_csv("Agg_Trans.csv", encoding='utf-8', index=False)
```
Similarly, Aggregated-Users, Map-transaction, Map-users, top-transaction, and top-users were generated and stored as a .csv file.
 <br>

## Step 4: EDA-Exploratory Data Analysis
The data is explored and visualized for any null values in the data frame. 
```python
Agg_Trans.isnull().sum()
```
 <br>  

## Step 5: SQL Database
To ensure independent operation on a cloud platform, the application stores generated data at End-of-Day (EOD) within a lightweight, file-based SQLite3 database. This approach eliminates the need for developers to rely on local host SQL credentials and simplifies deployment.
```python
# Connect to SQL DB
connection = sqlite3.connect("PhonePe_pulse.db")
cur = connection.cursor()
# Load Data
df_Agg_Trans = pd.read_csv("Data/Agg_Trans.csv")
# Inserting each DF to SQL server:
df_Agg_Trans.to_sql('Agg_Trans', connection, if_exists='replace')
```
 <br>  

## Step 6: Streamlit Dashboard
- The dashboard provides various interactive filters and charts to explore PhonePe Pulse data.
- Specific functionalities will depend on the data structure and your desired insights. However, common features might include:
    - **Date range selection:** Allow users to filter data by specific date ranges.
    - **Category selection:** Enable filtering based on categories within the data (e.g., location, demographics).
    - **Interactive charts:** Generate charts like bar graphs, line plots, or geographical visualizations to highlight trends and patterns.
<br>

## Step 7: Deploy Application
- From your workspace at share.streamlit.io, click "New app" from the upper-right corner of your workspace.
- Create requirements.txt file containing the libraries with the version in the file folder.
```python
!pip install pipreqs
```
Type pipreqs in the terminal to create the requirements.txt
- In the deploy an app screen, paste the "**GitHub link**".
