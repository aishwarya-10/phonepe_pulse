import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import json
import sqlite3


# Streamlit Page Configuration
st.set_page_config(
    page_title = "PhonePe Pulse Data",
    layout = "wide",
    initial_sidebar_state= "expanded"
    )

container = st.container()
with container:
    col1, col2 = st.columns(2)
    # Column 1: Title
    with col1:
        col1.markdown("# :gray[PhonePe Pulse] :violet[| THE BEAT OF PROGRESS]", unsafe_allow_html=True)

    # Column 2: Navigation Menu
    with col2:
        selected = option_menu(
            menu_title = None,
            options=["Explore Data", "Insights", "Data APIs"],
            default_index= 0,
            icons = ["map", "bar-chart", "card-heading"],
            orientation = "horizontal",
            styles={
            "container": {"padding": "10px", "background-color": "#f0f0f0"},
            "nav-link": { "--hover-color": "#834da0","color": "black","width":"140px",
                            "text-align":"center","padding":"5px 0",
                            "border-bottom":"4px solid transparent","transition":"border-bottom 0.5 ease","font-size":"14px", "font-weight": "bold"},
            "nav-link:hover": {"color":"black"},
            "nav-link-selected": {"background-color": "#391c59", "width":"140px","border-bottom":"4px solid #834da0","color":"white"}
            }           
        )


def format_num(number):
    """Formats a number to indian number format with commas and decimal places.

    Args:
        number: the number to be fomrated.
    
    Returns:
        A string representing the formatted number.
    """
    number_str = str(number)
    sep = ","
    reversed_num = number_str[::-1]
    thousand = reversed_num[:3]
    bal = reversed_num[3:]
    if len(bal) == 0:
        formatted_num = f"{thousand}"[::-1]
    elif len(bal) < 3:
        formatted_num = f"{thousand},{bal}"[::-1]
    else:
        formatted_int = sep.join(bal[i:i+2] for i in range(0, len(bal), 2))
        formatted_num = f"{thousand},{formatted_int}"[::-1]
    return formatted_num


def format_currency(number):
    """Formats a number in Indian currency format with commas and two decimal places.

    Args:
        number: The number to be formatted.

    Returns:
        A string representing the formatted number in Indian currency format.
    """
    number_str = str(number)
    sep = ","
    
    # Check for presence of decimel places
    has_decimal = "." in number_str

    # Integer and decimel parts separation
    if has_decimal:
        integer, decimal = number_str.split(".")
        reversed_num = integer[::-1]
        thousand = reversed_num[:3]
        bal = reversed_num[3:]
        if len(bal) == 0:
            formatted_num = f"₹{thousand[::-1]}.{decimal[:2]} Cr"
        elif len(bal) < 3:
            formatted_int = thousand + "," + bal
            formatted_num = f"₹{formatted_int[::-1]}.{decimal[:2]} Cr"
        else:
            hundreds = sep.join(bal[i:i+2] for i in range(0, len(bal), 2))
            formatted_int = thousand + "," + hundreds
            formatted_num = f"₹{formatted_int[::-1]}.{decimal[:2]} Cr"
    else:
        integer = number_str
        reversed_num = integer[::-1]
        thousand = reversed_num[:3]
        bal = reversed_num[3:]
        if len(bal) == 0:
            formatted_num = f"₹{thousand[::-1]} Cr"
        elif len(bal) < 3:
            formatted_int = thousand + "," + bal
            formatted_num = f"₹{formatted_int[::-1]} Cr"
        else:
            hundreds = sep.join(bal[i:i+2] for i in range(0, len(bal), 2))
            formatted_int = thousand + "," + hundreds
            formatted_num = f"₹{formatted_int[::-1]} Cr"
    return formatted_num


def lineChart(df, x, y):
    """Plotly line chart

    Args: 
        df: A pandas DataFrame.
        x: x-axis column name.
        y: y-axis column name.
    Returns:
        Plotly chart.
    """

    figch = px.line(df, x= x, y=y, width=850, height=525, title=f"{map_sn}: {att} Analysis (Q{qua} {year})")
    figch.update_layout(title={'font': {'size': 24}},
                        hoverlabel_font={'size': 18})
    return st.plotly_chart(figch, use_container_width=True, layout=dict({'width': '100%'}, **{'height': '100%'}))


def barChart(df, x, y):
    """Plotly bar chart
    
    Args: 
        df: A pandas DataFrame.
        x: x-axis column name.
        y: y-axis column name.
    Returns:
        Plotly chart.
    """
    figch = px.bar(df, x= x, y=y, width=850, height=525, title=f"{map_sn}: {att} Analysis (Q{qua} {year})")
    figch.update_layout(title={'font': {'size': 24}},
                        hoverlabel_font={'size': 18})
    return st.plotly_chart(figch, use_container_width=True, layout=dict({'width': '100%'}, **{'height': '100%'}))
   

def replace_state_names(df: pd.DataFrame, new_state_names: dict):
    """Replaceing the dataframe column with new state name series."""
    def replace_state(state):
        return new_state_names.get(state, state)  # Return original state if not found

    df['State'] = [replace_state(state) for state in df['State']]
    return df 


def replace_name(current_name, names):
    """Replaceing the state name with a new state name from a dict."""
    for old_name, new_name in names.items():
        current_name = current_name.replace(new_name, old_name)
    return current_name

# list of state names used in sql table
state_names = ['andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar', 'chandigarh', 'chhattisgarh', 
                'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 'jammu-&-kashmir', 
                'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 
                'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 'tripura', 
                'uttar-pradesh', 'uttarakhand', 'west-bengal']
# Dict of states names
map_state_names = {'andaman-&-nicobar-islands':'Andaman & Nicobar Island', 'andhra-pradesh':'Andhra Pradesh', 'arunachal-pradesh':'Arunanchal Pradesh', 'assam':'Assam', 'bihar':'Bihar', 'chandigarh':'Chandigarh', 'chhattisgarh':'Chhattisgarh',
            'dadra-&-nagar-haveli-&-daman-&-diu':'Dadara & Nagar Havelli', 'ladakh':'Daman & Diu', 'goa':'Goa', 'gujarat':'Gujarat', 'haryana':'Haryana', 'himachal-pradesh':'Himachal Pradesh', 'jammu-&-kashmir':'Jammu & Kashmir', 
            'jharkhand':'Jharkhand', 'karnataka':'Karnataka', 'kerala':'Kerala', 'lakshadweep':'Lakshadweep', 'madhya-pradesh':'Madhya Pradesh', 'maharashtra':'Maharashtra', 'manipur':'Manipur', 'meghalaya':'Meghalaya', 
            'mizoram':'Mizoram', 'delhi':'NCT of Delhi', 'nagaland':'Nagaland', 'odisha':'Odisha', 'puducherry':'Puducherry', 'punjab':'Punjab', 'rajasthan':'Rajasthan', 'sikkim':'Sikkim', 'tamil-nadu':'Tamil Nadu', 
            'telangana':'Telangana', 'tripura':'Tripura', 'uttar-pradesh':'Uttar Pradesh', 'uttarakhand':'Uttarakhand', 'west-bengal':'West Bengal'}

# Connect to SQL DB
connection = sqlite3.connect("PhonePe_pulse.db")
cur = connection.cursor()

# Load Data
df_Agg_Trans = pd.read_csv("Data/Agg_Trans.csv")
df_Agg_Users = pd.read_csv("Data/Agg_Users.csv")
df_Agg_Ins = pd.read_csv("Data/Agg_Ins.csv")
df_Map_Trans = pd.read_csv("Data/Map_Trans.csv")
df_Map_Users = pd.read_csv("Data/Map_Users.csv")
df_Map_Ins = pd.read_csv("Data/Map_Ins.csv")
df_Top_Trans = pd.read_csv("Data/Top_Trans.csv")
df_Top_Users = pd.read_csv("Data/Top_Users.csv")
df_Top_Ins = pd.read_csv("Data/Top_Ins.csv")

# Inserting each DF to SQL server:
df_Agg_Trans.to_sql('Agg_Trans', connection, if_exists='replace')
df_Agg_Users.to_sql('Agg_Users', connection, if_exists='replace')
df_Map_Trans.to_sql('Map_Trans', connection, if_exists='replace')
df_Map_Users.to_sql('Map_Users', connection, if_exists='replace')
df_Top_Trans.to_sql('Top_Trans', connection, if_exists='replace')
df_Top_Users.to_sql('Top_Users', connection, if_exists='replace')

if selected == "Explore Data":
    st.write("") # empty space
    st.header("Explore Data")
    # A short story on the section
    st.write("""Tapping fingers impatiently as the massive PhonePe Pulse dataset finished downloading.
                **PhonePe Pulse**, a teasure trove of anonymized user transaction, insurance data has promised 
                valuable insights into India's booming digital payments landscape. The first hurdle of 
                data cleaning of endless spreadsheet led to a visualization in a **kaleidoscope of colors**.
                """)
    col1, col2 = st.columns((6,4))

    with col1:
        # Column 1: Title
        st.header("All India")

    with col2:
        # Column 2: Data Exploration
        sub1, sub2, sub3 = st.columns(3)

        with sub1:
            sections = ["Transactions", "Users"]
            default_sec = sections.index("Transactions")
            section = st.selectbox(
                "Select a payment section...",
                options = sections,
                index = default_sec,
                label_visibility = "collapsed"
            )

        with sub2:
            years = ["2018", "2019", "2020", "2021", "2022", "2023"]
            default_y = years.index("2023")
            year = st.selectbox(
                "Select an year...",
                options = years,
                index = default_y,
                label_visibility = "collapsed"
            )

        with sub3:
            quaters = ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"]
            default_q = quaters.index("Q1 (Jan-Mar)")
            quater = st.selectbox(
                "Select a quater...",
                options = quaters,
                index = default_q,
                label_visibility = "collapsed"
            )

            if quater == "Q1 (Jan-Mar)":
                qua = "1"
            elif quater == "Q2 (Apr-Jun)":
                qua = "2"
            elif quater == "Q3 (Jul-Sep)":
                qua = "3"
            elif quater == "Q4 (Oct-Dec)":
                qua = "4"


    if section == "Transactions":
        # Transactions
        cur.execute(f"""SELECT SUM(Transaction_count), SUM(Transaction_amount) FROM Agg_Trans 
                    WHERE Year = {year} AND Quater = {qua}
                    """)
        result1 = cur.fetchall()
        columns = ["All PhonePe transactions", "Total payment value"]
        df1 = pd.DataFrame(result1, columns = columns).reset_index(drop=True)
        df1["Avg. payment value"] = format_currency((df1.loc[0,"Total payment value"])/(df1.loc[0,"All PhonePe transactions"]))
        df1["All PhonePe transactions"] = df1["All PhonePe transactions"].apply(lambda x: format_num(x))
        df1["Total payment value"] = df1["Total payment value"].apply(lambda x: format_currency(x/10000000))

        total_trans = str(df1.loc[0,"All PhonePe transactions"])
        total_val =  str(df1.loc[0,"Total payment value"])
        avg_trans = str(df1.loc[0,"Avg. payment value"])

        # Categories
        cur.execute(f"""SELECT Transaction_type, SUM(Transaction_count) FROM Agg_Trans
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY Transaction_type
                    """)
        result2 = cur.fetchall()
        columns = ["Transaction_type", "Transaction_count"]
        df2 = pd.DataFrame(result2, columns = columns).reset_index(drop=True)
        df2["Transaction_count"] = df2["Transaction_count"].apply(lambda x: format_num(x))

        # Top 10
        cur.execute(f"""SELECT State, SUM(Trans_dist_amount) AS Total_trans FROM Top_Trans
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY State, Year, Quater
                    ORDER BY Total_trans DESC LIMIT 10
                    """)
        result3 = cur.fetchall()
        df3 = pd.DataFrame(result3, columns=["State", "Transactions"]).reset_index(drop=True)
        df3.index += 1
        df3 = replace_state_names(df3, map_state_names)
        df3["Transactions"] = df3["Transactions"].apply(lambda x: format_currency(x/10000000))

        cur.execute(f"""SELECT District, Trans_dist_amount AS Total_trans FROM Top_Trans
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY District, Year, Quater
                    ORDER BY Total_trans DESC LIMIT 10
                    """)
        result4 = cur.fetchall()
        df4 = pd.DataFrame(result4, columns=["District", "Transactions"]).reset_index(drop=True)
        df4.index += 1
        df4["District"] = df4["District"].apply(lambda x: str(x)).apply(lambda x: x.replace("district", "")).apply(lambda x: x.capitalize())
        df4["Transactions"] = df4["Transactions"].apply(lambda x: format_currency(x/10000000))

        cur.execute(f"""SELECT Pincode, SUM(Trans_pincode_amount) AS Total_trans FROM Top_Trans
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY Pincode, Year, Quater
                    ORDER BY Total_trans DESC LIMIT 10
                    """)
        result5 = cur.fetchall()
        df5 = pd.DataFrame(result5, columns=["Postal Code", "Transactions"]).reset_index(drop=True)
        df5.index += 1
        df5["Postal Code"] = df5["Postal Code"].apply(lambda x: str(x)).apply(lambda x: x.replace(",", " "))
        df5["Transactions"] = df5["Transactions"].apply(lambda x: format_currency(x/10000000))

        col1, col2 = st.columns((6,4))
        with col1:
            # Column 1: Transaction Map
            cur.execute(f"""SELECT State, Year, Quater, Transaction_count, Transaction_amount FROM Map_Trans 
                        WHERE Year = {year} AND Quater = {qua}
                        GROUP BY State
                        ORDER BY State
                        """)
            result10 = cur.fetchall()
            columns = ["State", "Year", "Quater", "All PhonePe transactions", "Total payment value"]
            df10 = pd.DataFrame(result10, columns = columns).reset_index(drop=True)
            df10.index += 1
            df10 = replace_state_names(df10, map_state_names)
            df10["Avg. payment value"] = (df10["Total payment value"]/df10["All PhonePe transactions"]).apply(lambda x: format_currency(x))
            df10["Avg. payment value"] = df10["Avg. payment value"].apply(lambda x: x.replace("Cr", ""))
            df10["All PhonePe transactions"] = df10["All PhonePe transactions"].apply(lambda x: format_num(x))
            df10["mapTransactions"] = df10["Total payment value"]
            df10["Total payment value"] = df10["Total payment value"].apply(lambda x: format_currency(x/10000000))
     
            india_states = json.load(open("Data/states_india.geojson", "r"))
            # map geojson and dataframe using an id
            state_id_map = {}
            for feature in india_states["features"]:
                feature["id"] = feature["properties"]["state_code"]
                state_id_map[feature["properties"]["st_nm"]] = feature["id"]

            df10["id"] = df10["State"].apply(lambda x: state_id_map[x])
            fig = px.choropleth_mapbox(
                df10,
                locations = 'id',
                geojson = india_states,
                hover_name = "State",
                hover_data = {'All PhonePe transactions':True, 'Total payment value':True, 'id':False, 'Avg. payment value':True, "mapTransactions":False},
                title = f"PhonePe Amount Transactions in Q{qua}-{year}",
                mapbox_style = "carto-positron",
                center = {"lat":24, "lon":78},
                color = "mapTransactions",
                color_continuous_scale = 'Viridis',
                zoom = 3.6,
                width = 800, 
                height = 800
            )
            fig.update_layout(coloraxis_colorbar=dict(title='Transaction Amount', showticklabels=True),
                            title={'font': {'size': 24}},
                            hoverlabel_font={'size': 18})
            fig.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Fun Facts"):
                Ecol1, Ecol2 = st.columns(2)
                with Ecol1:
                    container1 = st.container(border=True)
                    container1.write("""Maharashtra's PhonePe users with Xiaomi phones could create a human chain stretching 
                                     for over 1,134 kilometers – that's almost the distance from Mumbai to Delhi!""")
                    
                with Ecol2:
                    container2 = st.container(border=True)
                    container2.write("""PhonePe transactions in Maharashtra during Q4 2023 (₹70,786.27 billion) helped save millions of trees!
                                      Since most transactions are digital, there's less need for paper receipts
                                     """)
        with col2:
            # Column 2: Insights of Transaction
            st.header("Transactions")
            st.write("All PhonePe transactions (UPI+Cards+Wallets)")
            st.write(total_trans)
            Tcol1, Tcol2 = st.columns(2)
            with Tcol1:
                st.write("Total payment value")
                st.write(total_val)
            with Tcol2:
                st.write("Avg. transaction value")
                st.write(avg_trans.replace("Cr", ""))
            st.markdown("""
                        <hr style="border: 1px solid #673ab7; margin-top: 10px; margin-bottom: 20px;">
                        """, unsafe_allow_html=True
                        )

            st.header("Categories")
            for i in range(len(df2["Transaction_count"])):
                name, value = list(df2.iloc[i,0:2])
                col1, col2 = st.columns(2)
                with col1:
                    st.write(name)
                with col2:
                    st.write(value)
            st.markdown("""
                        <hr style="border: 1px solid #673ab7; margin-top: 10px; margin-bottom: 20px;">
                        """, unsafe_allow_html=True
                        )

            tab1, tab2, tab3 = st.tabs(["States", "Districts", "Postal Codes"])
            with tab1:
                st.header("Top 10 States")
                st.dataframe(df3, width= 500)
            with tab2:
                st.header("Top 10 Districts")
                st.dataframe(df4, width= 500)
            with tab3:
                st.header("Top 10 Postal Codes")
                st.dataframe(df5, width= 500)


    elif section == "Users":
        # Users
        cur.execute(f"""SELECT SUM(Registered_users), SUM(App_opens) FROM Agg_Users
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY Year, Quater
                    ORDER BY Year, Quater
                    """)
        result6 = cur.fetchall()
        columns = ["Registered_users", "App_opens"]
        df6 = pd.DataFrame(result6, columns= columns).reset_index(drop=True)
        if df6.size != 0:
            Registered_users = format_num(df6.iloc[0,0])
            App_opens = format_num(df6.iloc[0,1])
        else: 
            Registered_users = 0
            App_opens = 0

        # Top 10
        cur.execute(f"""SELECT State, SUM(User_dist_count) AS Total_users FROM Top_Users
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY State, Year, Quater
                    ORDER BY Total_users DESC LIMIT 10
                    """)
        result7 = cur.fetchall()
        df7 = pd.DataFrame(result7, columns=["State", "Users"]).reset_index(drop=True)
        df7.index += 1
        df7 = replace_state_names(df7, map_state_names)
        df7["Users"] = df7["Users"].apply(lambda x: format_num(x))

        cur.execute(f"""SELECT District, User_dist_count AS Total_users FROM Top_Users
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY District, Year, Quater
                    ORDER BY Total_users DESC LIMIT 10
                    """)
        result8 = cur.fetchall()
        df8 = pd.DataFrame(result8, columns=["District", "Users"]).reset_index(drop=True)
        df8.index += 1
        df8["District"] = df8["District"].apply(lambda x: str(x)).apply(lambda x: x.replace("district", "")).apply(lambda x: x.capitalize())
        df8["Users"] = df8["Users"].apply(lambda x: format_num(x))

        cur.execute(f"""SELECT Pincode, SUM(User_pincode_count) AS Total_users FROM Top_Users
                    WHERE Year = {year} AND Quater = {qua}
                    GROUP BY Pincode, Year, Quater
                    ORDER BY Total_users DESC LIMIT 10
                    """)
        result9 = cur.fetchall()
        df9 = pd.DataFrame(result9, columns=["Postal Code", "Users"]).reset_index(drop=True)
        df9.index += 1
        df9["Postal Code"] = df9["Postal Code"].apply(lambda x: str(x)).apply(lambda x: x.replace(",", " "))
        df9["Users"] = df9["Users"].apply(lambda x: format_num(x))

        col1, col2 = st.columns((6,4))
        with col1:
            # Column 1: Map
            cur.execute(f"""SELECT State, Registered_users, App_opens FROM Map_Users 
                        WHERE Year = {year} AND Quater = {qua}
                        GROUP BY State
                        ORDER BY State
                        """)
            result11 = cur.fetchall()
            columns = ["State", "Registered Users", "App Opens"]
            df11 = pd.DataFrame(result11, columns = columns).reset_index(drop=True)
            df11.index += 1
            df11 = replace_state_names(df11, map_state_names)
            
            if df11.size != 0:
                Registered_users = format_num(df11.iloc[0,1])
                App_opens = format_num(df11.iloc[0,2])
            else: 
                Registered_users = 0
                App_opens = 0

            india_states = json.load(open("Data/states_india.geojson", "r"))
            # map geojson and dataframe using an id
            state_id_map = {}
            for feature in india_states["features"]:
                feature["id"] = feature["properties"]["state_code"]
                state_id_map[feature["properties"]["st_nm"]] = feature["id"]

            df11["id"] = df11["State"].apply(lambda x: state_id_map[x])

            fig = px.choropleth_mapbox(
                df11,
                locations = 'id',
                geojson = india_states,
                hover_name = "State",
                hover_data = {'Registered Users':True, 'App Opens':True, 'id':False},
                title = f"PhonePe Users in Q{qua}-{year}",
                mapbox_style = "carto-positron",
                center = {"lat":24, "lon":78},
                color = "App Opens",
                color_continuous_scale = px.colors.diverging.PuOr,
                zoom = 3.6,
                width = 800, 
                height = 800
            )
            fig.update_layout(coloraxis_colorbar=dict(title='App Opens', showticklabels=True),
                            title={'font': {'size': 24}},
                            hoverlabel_font={'size': 18})
            fig.update_geos(fitbounds = "locations", visible = False,)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Insights of User
            st.header("Users")
            st.write(f"Registered PhonePe users till Q{qua} {year}")
            st.write(Registered_users)
            st.write(f"PhonePe app opens in Q{qua} {year}")
            st.write(App_opens)
            st.markdown("""
                        <hr style="border: 1px solid #673ab7; margin-top: 10px; margin-bottom: 20px;">
                        """, unsafe_allow_html=True
                        )

            tab1, tab2, tab3 = st.tabs(["States", "Districts", "Postal Codes"])
            with tab1:
                st.header("Top 10 States")
                st.dataframe(df7, width= 500)
            with tab2:
                st.header("Top 10 Districts")
                st.dataframe(df8, width= 500)
            with tab3:
                st.header("Top 10 Postal Codes")
                st.dataframe(df9, width= 500)


    # Districts
    st.write("")
    st.write("")
    st.write("")
    st.header("Districts")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        # Column 1: Select State
        States = list(map_state_names.values())
        default_sec = States.index("Tamil Nadu")
        State = st.selectbox(
            "Select a State...",
            options = States,
            index = default_sec,
            label_visibility = "collapsed",
            key = "state-dist"
        )
        map_sn = State
        State = replace_name(State, map_state_names)

    with col2:
        # Column 2: Select Section
        sections = ["Transactions", "Users"]
        default_sec = sections.index("Transactions")
        section = st.selectbox(
            "Select a payment section...",
            options = sections,
            index = default_sec,
            label_visibility = "collapsed",
            key = "sec-dist"
        )

    with col3:
        # Column 3: Select Section-info
        if section == "Transactions":
            attrs = ["Transaction Count", "Transaction Amount"]
            default_TA = attrs.index("Transaction Count")
            att = st.selectbox(
                "Select an attribute...",
                options = attrs,
                index = default_TA,
                label_visibility = "collapsed",
                key = "T_att-dist"
            )
        elif section == "Users":
            attrs = ["Registered Users", "App Opens"]
            default_UA = attrs.index("Registered Users")
            att = st.selectbox(
                "Select an attribute...",
                options = attrs,
                index = default_UA,
                label_visibility = "collapsed",
                key = "U_att-dist"
            )

    with col4:
        # Column 4: Select Year
        years = ["2018", "2019", "2020", "2021", "2022", "2023"]
        default_y = years.index("2023")
        year = st.selectbox(
            "Select an year...",
            options = years,
            index = default_y,
            label_visibility = "collapsed",
            key = "year-dist"
        )

    with col5:
        # Column 5: Select Quater
        quater = ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"]
        default_q = quaters.index("Q1 (Jan-Mar)")
        quater = st.selectbox(
            "Select a quater...",
            options = quaters,
            index = default_q,
            label_visibility = "collapsed",
            key = "qua-dist"
        )

        if quater == "Q1 (Jan-Mar)":
            qua = "1"
        elif quater == "Q2 (Apr-Jun)":
            qua = "2"
        elif quater == "Q3 (Jul-Sep)":
            qua = "3"
        elif quater == "Q4 (Oct-Dec)":
            qua = "4"

    with col6:
        # Column 6: Select Chart
        charts = ["line", "bar"]
        default_c = charts.index("bar")
        chart = st.selectbox(
            "Select an chart...",
            options = charts,
            index = default_c,
            label_visibility = "collapsed",
            key = "chart-dist"
        )


    if section == "Transactions":
        cur.execute(f"""SELECT District, Transaction_count, Transaction_amount FROM Map_Trans 
                    WHERE State = "{State}" AND Year = {year} AND Quater = {qua}
                    ORDER BY District
                    """)
        result12 = cur.fetchall()
        columns = ["District", "Transaction_count", "Transaction_amount"]
        df12 = pd.DataFrame(result12, columns = columns).reset_index(drop=True)
        df12.index += 1
        df12["District"] = df12["District"].apply(lambda x: str(x)).apply(lambda x: x.replace("district", "")).apply(lambda x: x.capitalize())
        df12["Transaction Count"] = df12["Transaction_count"].apply(lambda x: format_num(x))
        df12["mapTransactions"] = df12["Transaction_amount"]
        df12["Transaction Amount"] = df12["Transaction_amount"].apply(lambda x: format_currency(x/10000000))
    
        if att == "Transaction Count":
            if chart == "line":
                lineChart(df12, 'District', att)
            else:
                barChart(df12, 'District', att)

        elif att == "Transaction Amount":
            if chart == "line":
                lineChart(df12, 'District', att)
            else:
                barChart(df12, 'District', att)

    elif section == "Users":
        cur.execute(f"""SELECT District, Registered_users, App_opens FROM Map_Users 
                    WHERE State = "{State}" AND Year = {year} AND Quater = {qua}
                    ORDER BY District
                    """)
        result12 = cur.fetchall()
        columns = ["District", "Registered_users", "App_opens"]
        df12 = pd.DataFrame(result12, columns = columns).reset_index(drop=True)
        df12.index += 1
        df12["District"] = df12["District"].apply(lambda x: str(x)).apply(lambda x: x.replace("district", "")).apply(lambda x: x.capitalize())
        df12["Registered Users"] = df12["Registered_users"].apply(lambda x: format_num(x))
        df12["App Opens"] = df12["App_opens"].apply(lambda x: format_num(x))

        if att == "Registered Users":
            if chart == "line":
                lineChart(df12, 'District', att)
            else:
                barChart(df12, 'District', att)

        elif att == "App Opens":
            if chart == "line":
                lineChart(df12, 'District', att)
            else:
                barChart(df12, 'District', att)
    connection.close()


elif selected == "Insights":
    st.header("Insights")
    st.write("""Our next mission is to unearth **hidden trends** and patterns that could revolutionize PhonePe mobile wallet strategy.""")

    connection = sqlite3.connect("PhonePe_pulse.db")
    cur = connection.cursor()

    # Initial value for session state
    if "selectbox_enabled" not in st.session_state:
        st.session_state["selectbox_enabled"] = False

    # Function to execute the chosen query
    def execute_query(selected_option: str):
        """
        Extracts data from SQL table.

        Args:
            selected_option (str): A question selected to query SQL table.

        Returns:
            DataFrame: The extracted info is displayed in table.
        """
        if selected_option == "1. Top 10 spending categories by total transaction amount?":
            col1, col2 = st.columns(2)
            # Table
            with col1:
                cur.execute("""SELECT Transaction_type, AVG(Transaction_amount/Transaction_count) AS Average FROM Agg_Trans
                            GROUP BY Transaction_type
                            ORDER BY Transaction_type
                            """)
                result1 = cur.fetchall()
                df1 = pd.DataFrame(result1, columns=["Category", "Avg. Transaction Payment"]).reset_index(drop=True)
                df1.index += 1
                df1["Avg. Payment"] = df1["Avg. Transaction Payment"]
                df1["Avg. Transaction Payment"] = df1["Avg. Transaction Payment"].apply(lambda x: format_currency(x)).apply(lambda x: x.replace("Cr", ""))
                st.dataframe(df1[["Category", "Avg. Transaction Payment"]])
            # Chart
            with col2:
                fig = px.bar(df1, x= "Category", y= "Avg. Payment", orientation= 'v', color= "Avg. Payment", text_auto='.2s', title="Top 10 spending categories by total transaction amount")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "2. How many PhonePe users were registered in a quater year?":
            col1, col2 = st.columns(2)
            with col1:
                cur.execute("""SELECT Year, Quater, Registered_users FROM Agg_Users
                            GROUP BY Year, Quater
                            ORDER BY Year, Quater
                            """)
                result2 = cur.fetchall()
                df2 = pd.DataFrame(result2, columns=["Year", "Quater", "Registered Users"]).reset_index(drop=True)
                df2.index += 1
                df2["Users"] = df2["Registered Users"]
                df2["Registered Users"] = df2["Registered Users"].apply(lambda x: format_num(x))
                df2["Year"] = df2["Year"].apply(lambda x: str(x).replace(",", ""))
                st.dataframe(df2[["Year", "Quater", "Registered Users"]])

            with col2:
                fig = px.bar(df2, x= "Year", y= "Users", orientation= 'v', color= "Quater", text_auto='.2s', title="PhonePe Users")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "3. Top 10 mobile brands based on PhonePe registrations?":
            col1, col2 = st.columns(2)
            with col1:
                cur.execute("""SELECT State, Device_Brand, Registered_users FROM Agg_Users
                                GROUP BY Device_Brand
                                ORDER BY Brand_users DESC
                            """)
                result3 = cur.fetchall()
                df3 = pd.DataFrame(result3, columns=["State", "Device Brand", "Registered Users"]).reset_index(drop=True)
                df3.index += 1
                df3 = replace_state_names(df3, map_state_names)
                df3["Users"] = df3["Registered Users"]
                df3["Registered Users"] = df3["Registered Users"].apply(lambda x: format_num(x))
                st.dataframe(df3[["State", "Device Brand", "Registered Users"]])

            with col2:
                fig = px.bar(df3, x= "Device Brand", y= "Users", orientation= 'v', color= "State", text_auto='.2s', title="Top 10 Most Mobile Brands")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "4. Top 10 registered users with respect to District?":
            cur.execute("""SELECT State, District, User_dist_count FROM Top_Users 
                        GROUP BY District 
                        ORDER BY User_dist_count DESC LIMIT 10
                        """)
            result4 = cur.fetchall()
            df4 = pd.DataFrame(result4, columns=['State', 'District', 'Users']).reset_index(drop=True)
            df4.index += 1
            df4  = replace_state_names(df4, map_state_names)
            df4["map_Users"] = df4["Users"]
            df4["District"] = df4["District"].apply(lambda x: x.capitalize())
            df4["Users"] = df4["Users"].apply(lambda x: format_num(x))
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df4[['State', 'District', 'Users']])

            with col2:
                fig = px.bar(df4, x="District", y="map_Users", orientation= 'v', color= "State", text_auto='.2s', title="Top 10 Registered-users based on District")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "5. Least registered registered users with respect to District?":
            col1, col2 = st.columns(2)
            with col1:
                cur.execute("""SELECT State, District, User_dist_count FROM Top_Users 
                            GROUP BY District 
                            ORDER BY User_dist_count ASC LIMIT 10
                            """)
                result5 = cur.fetchall()
                df5 = pd.DataFrame(result5, columns=['State', 'District', 'Users']).reset_index(drop=True)
                df5.index += 1
                df5 = replace_state_names(df5, map_state_names)
                df5["map_Users"] = df5["Users"]
                df5["District"] = df5["District"].apply(lambda x: x.capitalize())
                df5["Users"] = df5["Users"].apply(lambda x: format_num(x))
                st.dataframe(df5[['State', 'District', 'Users']])

            with col2:
                fig = px.bar(df5, x="District", y="map_Users", orientation= 'v', color= "State", text_auto='.2s', title="Least Registered-users based on District")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "6. Leading states in merchant trasnacations of year 2023?":
            cur.execute("""SELECT State, Transaction_amount FROM Agg_Trans 
                        WHERE Transaction_type = "Merchant payments" AND Year = "2023"
                        ORDER BY Transaction_amount DESC
                        """)
            result6 = cur.fetchall()
            df6 = pd.DataFrame(result6, columns=["State", "Transaction Amount"]).reset_index(drop=True)
            df6.index += 1
            df6 = replace_state_names(df6, map_state_names)
            df6["Transaction Value"] = df6["Transaction Amount"]
            df6["Transaction Amount"] = df6["Transaction Amount"].apply(lambda x: format_currency(x/10000000))
            st.dataframe(df6[["State", "Transaction Amount"]])

        elif selected_option == "7. Reveal spending pattern across Tamil Nadu?":
            col1, col2 = st.columns(2)
            with col1:
                cur.execute("""SELECT District, Trans_dist_amount FROM Top_Trans
                            WHERE State = tamil-nadu
                            GROUP BY Year
                            ORDER BY Trans_dist_amount DESC LIMIT 10
                            """)
                result7 = cur.fetchall()
                df7 = pd.DataFrame(result7, columns=["District", "Transaction Amount"]).reset_index(drop=True)
                df7.index += 1
                df7["Transaction Value"] = df7["Transaction Amount"]
                df7["Transaction Amount"] = df7["Transaction Amount"].apply(lambda x: format_currency(x/10000000))
                df7["District"] = df7["District"].apply(lambda x: x.capitalize())
                st.dataframe(df7[["District", "Transaction Amount"]])

            with col2:
                fig = px.bar(df7, x= "District", y= "Transaction Amount", orientation= 'v', color= "Year", text_auto='.2s', title="Spending Pattern Across Tamil Nadu")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True) 

        elif selected_option == "8. Which state processes the highest total transaction value each year?":
            col1, col2 = st.columns(2)
            with col1:
                cur.execute("""SELECT State, Year, MAX(Transaction_amount) AS Transaction_value FROM Agg_Trans
                            GROUP BY Year
                            ORDER BY Year DESC LIMIT 10
                            """)
                result8 = cur.fetchall()
                df8 = pd.DataFrame(result8, columns=["State", "Year", "Transaction Value"]).reset_index(drop=True)
                df8.index += 1
                df8 = replace_state_names(df8, map_state_names)
                df8["Transaction Amount"] = df8["Transaction Value"]
                df8["Transaction Value"] = df8["Transaction Value"].apply(lambda x: format_currency(x/10000000))
                df8["Year"] = df8["Year"].apply(lambda x: str(x).replace(",", ""))
                st.dataframe(df8[["State", "Year", "Transaction Value"]])
            with col2:
                fig = px.bar(df8, x= "Year", y= "Transaction Amount", orientation= 'v', color= "State", text_auto='.2s', title="States with Highest Transactions")
                fig.update_traces(textfont_size= 16)
                fig.update_xaxes(title_font=dict(size= 20))
                fig.update_yaxes(title_font=dict(size= 20))
                fig.update_layout(title_font_color= '#1308C2 ', title_font=dict(size= 25))
                st.plotly_chart(fig, use_container_width=True)

        elif selected_option == "9. Top 10 transaction amount based on postal codes in year 2023?":
            cur.execute("""SELECT Pincode, Trans_pincode_amount from Top_Trans
                        WHERE Year = "2023"
                        GROUP BY Pincode
                        ORDER BY Trans_pincode_amount DESC LIMIT 10
                        """)
            result9 = cur.fetchall()
            df9 = pd.DataFrame(result9, columns=["Pincode", "Transaction Amount"]).reset_index(drop=True)
            df9.index += 1
            df9["Transaction Amount"] = df9["Transaction Amount"].apply(lambda x: format_currency(x/10000000))
            df9["Pincode"] = df9["Pincode"].apply(lambda x: str(x).replace(",", ""))
            st.dataframe(df9[["Pincode", "Transaction Amount"]])

        elif selected_option == "10. Top 10 postal codes with highest registered users  in the year 2023?":
            cur.execute("""SELECT Pincode, User_pincode_count from Top_Users
                        WHERE Year = "2023"
                        GROUP BY Pincode
                        ORDER BY User_pincode_count DESC LIMIT 10
                        """)
            result10 = cur.fetchall()
            df10 = pd.DataFrame(result10, columns=["Pincode", "User Count"]).reset_index(drop=True)
            df10.index += 1
            df10["User Count"] = df10["User Count"].apply(lambda x: format_num(x))
            df10["Pincode"] = df10["Pincode"].apply(lambda x: str(x).replace(",", ""))
            st.dataframe(df10)

    selected_option = st.selectbox(
        "Check out some fun facts about PhonePe here...",
        ["1. Top 10 spending categories by total transaction amount?", 
        "2. How many PhonePe users were registered in a quater year?",
        "3. Top 10 mobile brands based on PhonePe registrations?",
        "4. Top 10 registered users with respect to District?",
        "5. Least registered registered users with respect to District?",
        "6. Leading states in merchant trasnacations of year 2023?",
        "7. Reveal spending pattern across Tamil Nadu?",
        "8. Which state processes the highest total transaction value each year?",
        "9. Top 10 transaction amount based on postal codes in year 2023?",
        "10. Top 10 postal codes with highest registered users  in the year 2023?"],
        index=None,
        placeholder="Select your Question...")

    st.write("Question: ", selected_option)

    if selected_option:
        st.session_state["selectbox_enabled"] = True
        execute_query(selected_option)

elif selected == "Data APIs":

    with st.container(border= True):
        st.markdown("""
                    <div style="background-color:#673ab7; border:2px solid #ccc; border-radius:15px; padding:2px 10px; width:200px; height: 80px">
                    <h2 style="color:#ffffff;font-weight:bold;">DATA APIs</h2>
                    </div>
                    """, unsafe_allow_html=True)
        st.header("Introduction")
        st.write("""
                 Founded in 2015, **PhonePe** has been a key player in this digital transformation. By leveraging open APIs (Application Programming Interfaces), 
                 PhonePe has streamlined access to payment services for millions of users. APIs allowed PhonePe to integrate seamlessly with banks and 
                 other financial institutions, offering a wider range of services and simplifying the user experience.""")              
        st.write("""
                 This interactive webpage empowers you to delve into the fascinating world of PhonePe transactions across India. 
                 Visualize data trends and gain insights into how PhonePe is transforming the financial landscape at various geographical levels - 
                 from broad state-wise patterns to granular details within postal codes.
                 """)
        
    with st.container(border= True):
        st.header("Guide")
        st.write("""
                This data has been structured to provide details on data cuts of Transactions and Users on the Explore tab. 
                 Along with fun facts, showcasing it's reach, impact and interesting trends. 
                """)
        # Aggregated
        col1, col2, col3 = st.columns([4,3,3])
        # Column 1: Aggregated
        with col1:
            with st.container(border= True):
                st.subheader("Aggregated")
                st.write("Aggregated values of various payment categories as shown under Categories section")
                st.image("Data/pic1.png", use_column_width=False, width=300)
        # Column 2: Map
        with col2:
            with st.container(border= True):
                st.subheader("Map")
                st.write("Total values at the State and District levels")
                st.image("Data/pic3.png", use_column_width=False, width=300)
        # Column 3: Top
        with col3:
            with st.container(border= True):
                st.subheader("Top")
                st.write("Totals of top States / Districts / Postal Codes")
                st.image("Data/pic2.png", use_column_width=False, width=300)

    with st.container(border= True):
        st.header("GitHub")
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
                    A home for the data that powers the PhonePe Pulse website.
                    """)
        with col2:
            url = "https://github.com/PhonePe/pulse#readme"
            st.link_button(label="Open", url= url)