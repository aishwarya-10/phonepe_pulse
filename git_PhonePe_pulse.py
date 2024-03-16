import streamlit as st
from streamlit_option_menu import option_menu
import pymysql
import pandas as pd
import plotly.express as px
import json
import os


HOST = os.environ["host"]
USER  = os.environ["user"]
PASSWD = os.environ["passwd"]
PORT = os.environ["port"]

# Streamlit Page Configuration
st.set_page_config(
    page_title = "PhonePe Pulse Data",
    layout = "wide",
    initial_sidebar_state= "expanded"
    )
# Define custom CSS to hide default formatting elements
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
# Apply the custom CSS using Streamlit's markdown function
st.markdown(hide_default_format, unsafe_allow_html=True)

col1, col2 = st.columns(2)
# Column 1: Title
with col1:
    # Define title text
    title_text = ":white[PhonePe Pulse] :violet[| THE BEAT OF PROGRESS]"
    additional_text = ":violet[| THE BEAT OF PROGRESS]"
    combined_text = f"{title_text} {additional_text}"
    st.title(title_text)
    # st.title(":white[PhonePe Pulse] :violet[|THE BEAT OF PROGRESS]")

# Column 2: Navigation Menu
with col2:
    # Create an option menu for navigation
    selected = option_menu(
        menu_title = None,
        options=["Explore Data", "Reports", "Data APIs"],
        default_index= 0,
        icons = ["map", "bar-chart", "card-heading"],
        orientation = "horizontal",
        styles={
        "icon": {"color": "black", "font-size": "12px"},
        "nav-link": { "--hover-color": "#834da0","color": "black","width":"140px",
                        "text-align":"center","padding":"5px 0",
                        "border-bottom":"4px solid transparent","transition":"border-bottom 0.5 ease","font-size":"14px"},
        "nav-link:hover": {"color":"black"},
        "nav-link-selected": {"background-color": "#473480", "width":"140px","border-bottom":"4px solid #bc8c8c","color":"white"}
        }           
    )

st.write("")
st.write("")
st.write("")

if selected == "Explore Data":
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

    def format_num(number):
        number_str = str(number)
        sep = ","
        reversed_num = number_str[::-1]
        thousand = reversed_num[:3]
        bal = reversed_num[3:]
        if len(bal) < 3:
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
            if len(bal) < 3:
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
            if len(bal) < 3:
                formatted_int = thousand + "," + bal
                formatted_num = f"₹{formatted_int[::-1]} Cr"
            else:
                hundreds = sep.join(bal[i:i+2] for i in range(0, len(bal), 2))
                formatted_int = thousand + "," + hundreds
                formatted_num = f"₹{formatted_int[::-1]} Cr"
        return formatted_num

    def replace_state_names(df, old_state_names, new_state_names):

        # Vectorized replacement using list comprehension and conditional
        def replace_state(state):
            return new_state_names.get(state, state)  # Return original state if not found

        df['State'] = [replace_state(state) for state in df['State']]
        return df 
    
    def replace_name(current_name, names):
        for old_name, new_name in names.items():
            current_name = current_name.replace(new_name, old_name)
        return current_name

    state_names = ['andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar', 'chandigarh', 'chhattisgarh', 
                    'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 'jammu-&-kashmir', 
                    'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 
                    'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 'tripura', 
                    'uttar-pradesh', 'uttarakhand', 'west-bengal']
    map_state_names = {'andaman-&-nicobar-islands':'Andaman & Nicobar Island', 'andhra-pradesh':'Andhra Pradesh', 'arunachal-pradesh':'Arunanchal Pradesh', 'assam':'Assam', 'bihar':'Bihar', 'chandigarh':'Chandigarh', 'chhattisgarh':'Chhattisgarh',
                'dadra-&-nagar-haveli-&-daman-&-diu':'Dadara & Nagar Havelli', 'ladakh':'Daman & Diu', 'goa':'Goa', 'gujarat':'Gujarat', 'haryana':'Haryana', 'himachal-pradesh':'Himachal Pradesh', 'jammu-&-kashmir':'Jammu & Kashmir', 
                'jharkhand':'Jharkhand', 'karnataka':'Karnataka', 'kerala':'Kerala', 'lakshadweep':'Lakshadweep', 'madhya-pradesh':'Madhya Pradesh', 'maharashtra':'Maharashtra', 'manipur':'Manipur', 'meghalaya':'Meghalaya', 
                'mizoram':'Mizoram', 'delhi':'NCT of Delhi', 'nagaland':'Nagaland', 'odisha':'Odisha', 'puducherry':'Puducherry', 'punjab':'Punjab', 'rajasthan':'Rajasthan', 'sikkim':'Sikkim', 'tamil-nadu':'Tamil Nadu', 
                'telangana':'Telangana', 'tripura':'Tripura', 'uttar-pradesh':'Uttar Pradesh', 'uttarakhand':'Uttarakhand', 'west-bengal':'West Bengal'}


    # SQL Query
    Qconnection = pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        db="defaultdb",
        host=HOST,
        password=PASSWD,
        port=int(PORT),
        user=USER
        )
    cur = Qconnection.cursor()

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
        df3 = replace_state_names(df3, state_names, map_state_names)
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
            # Map
            cur.execute(f"""SELECT State, Transaction_count, Transaction_amount FROM Map_Trans 
                        WHERE Year = {year} AND Quater = {qua}
                        GROUP BY State
                        ORDER BY State
                        """)
            result10 = cur.fetchall()
            columns = ["State", "All PhonePe transactions", "Total payment value"]
            df10 = pd.DataFrame(result10, columns = columns).reset_index(drop=True)
            df10.index += 1
            # state_names = []
            # for i in range(len(df10["State"])):
            #     state_names.append(df10.iloc[i,0])
            # state_names = sorted(state_names)
            # print(state_names)

    

            # df10["State"] = df10["State"].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
            df10 = replace_state_names(df10, state_names, map_state_names)
            # df10["District"] = df10["District"].apply(lambda x: str(x)).apply(lambda x: x.replace("district", "")).apply(lambda x: x.capitalize())
            df10["Avg. payment value"] = (df10["Total payment value"]/df10["All PhonePe transactions"]).apply(lambda x: format_currency(x))
            df10["Avg. payment value"] = df10["Avg. payment value"].apply(lambda x: x.replace("Cr", ""))
            df10["All PhonePe transactions"] = df10["All PhonePe transactions"].apply(lambda x: format_num(x))
            df10["mapTransactions"] = df10["Total payment value"]
            df10["Total payment value"] = df10["Total payment value"].apply(lambda x: format_currency(x/10000000))
            # st.dataframe(df10)

            india_states = json.load(open("IITB India/states_india.geojson", "r"))
            # map_state_names = []
            # for i in range(36):
            #     map_state_names.append(india_states["features"][i]["properties"]["st_nm"])
            # map_state_names = sorted(map_state_names)
            # print(map_state_names)
            # map_state_names = {'andaman-&-nicobar-islands':'Andaman & Nicobar Island', 'andhra-pradesh':'Andhra Pradesh', 'arunachal-pradesh':'Arunanchal Pradesh', 'assam':'Assam', 'bihar':'Bihar', 'chandigarh':'Chandigarh', 'chhattisgarh':'Chhattisgarh',
            #                    'dadra-&-nagar-haveli-&-daman-&-diu':'Dadara & Nagar Havelli', 'ladakh':'Daman & Diu', 'goa':'Goa', 'gujarat':'Gujarat', 'haryana':'Haryana', 'himachal-pradesh':'Himachal Pradesh', 'jammu-&-kashmir':'Jammu & Kashmir', 
            #                    'jharkhand':'Jharkhand', 'karnataka':'Karnataka', 'kerala':'Kerala', 'lakshadweep':'Lakshadweep', 'madhya-pradesh':'Madhya Pradesh', 'maharashtra':'Maharashtra', 'manipur':'Manipur', 'meghalaya':'Meghalaya', 
            #                    'mizoram':'Mizoram', 'delhi':'NCT of Delhi', 'nagaland':'Nagaland', 'odisha':'Odisha', 'puducherry':'Puducherry', 'punjab':'Punjab', 'rajasthan':'Rajasthan', 'sikkim':'Sikkim', 'tamil-nadu':'Tamil Nadu', 
            #                    'telangana':'Telangana', 'tripura':'Tripura', 'uttar-pradesh':'Uttar Pradesh', 'uttarakhand':'Uttarakhand', 'west-bengal':'West Bengal'}

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
                # color_continuous_scale = px.colors.diverging.PuOr,
                color_continuous_scale = 'Viridis',
                zoom = 3.6,
                width = 800, 
                height = 800
            )
            fig.update_layout(coloraxis_colorbar=dict(title='Transaction Amount', showticklabels=True),
                            title={'font': {'size': 24}
                                    },hoverlabel_font={'size': 18})
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
                # st.markdown("""
                # <style>
                # table {boder: 0;}
                # th {display: none;}
                # td:first-child {
                #             text-align: right;
                #             width: 50px;
                #             padding-right: 10px;
                # }
                # </style>
                # """, unsafe_allow_html=True)
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
        df7 = replace_state_names(df7, state_names, map_state_names)
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
            # Map
            cur.execute(f"""SELECT State, Registered_users, App_opens FROM Map_Users 
                        WHERE Year = {year} AND Quater = {qua}
                        GROUP BY State
                        ORDER BY State
                        """)
            result11 = cur.fetchall()
            columns = ["State", "Registered Users", "App Opens"]
            df11 = pd.DataFrame(result11, columns = columns).reset_index(drop=True)
            df11.index += 1
            state_names = ['andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar', 'chandigarh', 'chhattisgarh', 
                        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 'jammu-&-kashmir', 
                        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 
                        'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 'tripura', 
                        'uttar-pradesh', 'uttarakhand', 'west-bengal']
            map_state_names = {'andaman-&-nicobar-islands':'Andaman & Nicobar Island', 'andhra-pradesh':'Andhra Pradesh', 'arunachal-pradesh':'Arunanchal Pradesh', 'assam':'Assam', 'bihar':'Bihar', 'chandigarh':'Chandigarh', 'chhattisgarh':'Chhattisgarh',
                        'dadra-&-nagar-haveli-&-daman-&-diu':'Dadara & Nagar Havelli', 'ladakh':'Daman & Diu', 'goa':'Goa', 'gujarat':'Gujarat', 'haryana':'Haryana', 'himachal-pradesh':'Himachal Pradesh', 'jammu-&-kashmir':'Jammu & Kashmir', 
                        'jharkhand':'Jharkhand', 'karnataka':'Karnataka', 'kerala':'Kerala', 'lakshadweep':'Lakshadweep', 'madhya-pradesh':'Madhya Pradesh', 'maharashtra':'Maharashtra', 'manipur':'Manipur', 'meghalaya':'Meghalaya', 
                        'mizoram':'Mizoram', 'delhi':'NCT of Delhi', 'nagaland':'Nagaland', 'odisha':'Odisha', 'puducherry':'Puducherry', 'punjab':'Punjab', 'rajasthan':'Rajasthan', 'sikkim':'Sikkim', 'tamil-nadu':'Tamil Nadu', 
                        'telangana':'Telangana', 'tripura':'Tripura', 'uttar-pradesh':'Uttar Pradesh', 'uttarakhand':'Uttarakhand', 'west-bengal':'West Bengal'}
            df11 = replace_state_names(df11, state_names, map_state_names)
            
            if df11.size != 0:
                Registered_users = format_num(df11.iloc[0,1])
                App_opens = format_num(df11.iloc[0,2])
            else: 
                Registered_users = 0
                App_opens = 0

            india_states = json.load(open("IITB India/states_india.geojson", "r"))
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
                # color_continuous_scale = 'Viridis',
                zoom = 3.6,
                width = 800, 
                height = 800
            )
            fig.update_layout(coloraxis_colorbar=dict(title='App Opens', showticklabels=True),
                            title={'font': {'size': 24}
                                    },hoverlabel_font={'size': 18})
            fig.update_geos(fitbounds = "locations", visible = False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
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
            attrs = ["Transaction_count", "Transaction_amount"]
            default_TA = attrs.index("Transaction_count")
            att = st.selectbox(
                "Select an attribute...",
                options = attrs,
                index = default_TA,
                label_visibility = "collapsed",
                key = "T_att-dist"
            )
        elif section == "Users":
            attrs = ["Registered_users", "App_opens"]
            default_UA = attrs.index("Registered_users")
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

    sub1, sub2 = st.columns((1,9))
    with sub1:
        # Sub-Column 1: State Map
        st.write("")
        # cur.execute(f"""SELECT State, Transaction_count, Transaction_amount FROM Map_Trans 
        #             WHERE State = "{State}" AND Year = {year} AND Quater = {qua}
        #             GROUP BY State
        #             ORDER BY State
        #             """)
        # result13 = cur.fetchall()
        # columns = ["State", "All PhonePe transactions", "Total payment value"]
        # df13 = pd.DataFrame(result13, columns = columns).reset_index(drop=True)
        # df13.index += 1
        # st.dataframe(df13)
        # india_states = json.load(open("IITB India/states_india.geojson", "r"))
        # # map geojson and dataframe using an id
        # state_id_map = {}
        # for feature in india_states["features"]:
        #     feature["id"] = feature["properties"]["state_code"]
        #     state_id_map[feature["properties"]["st_nm"]] = feature["id"]

        # df13["id"] = df13["State"].apply(lambda x: state_id_map[x])
        # fig = px.choropleth_mapbox(
        #     df13,
        #     locations = df13["State"],
        #     geojson = india_states,
        #     hover_name = "State",
        #     hover_data = {'All PhonePe transactions':True, 'Total payment value':True},
        #     title = f"PhonePe {section} in Q{qua}-{year}",
        #     mapbox_style = "carto-positron",
        #     center = {"lat":24, "lon":78},
        #     # featureidkey="properties.st_nm",
        #     color = "All PhonePe transactions",
        #     # color_continuous_scale = px.colors.diverging.PuOr,
        #     color_continuous_scale = 'Viridis',
        #     zoom = 3.6,
        #     width = 800, 
        #     height = 800
        # )
        # fig.update_layout(coloraxis_colorbar=dict(title='Transaction Amount', showticklabels=True),
        #                 title={'font': {'size': 24}
        #                         },hoverlabel_font={'size': 18})
        # fig.update_geos(fitbounds="locations", visible=False)
        # st.plotly_chart(fig, use_container_width=True)

    with sub2:
        # sub-column 2: Chart
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
            df12["Transaction_count"] = df12["Transaction_count"].apply(lambda x: format_num(x))
            df12["mapTransactions"] = df12["Transaction_amount"]
            df12["Transaction_amount"] = df12["Transaction_amount"].apply(lambda x: format_currency(x/10000000))

            if att == "Transaction_count":
                if chart == "line":
                    st.write(f"**{State.capitalize()}**")
                    figch = px.line(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
                else:
                    st.write(f"**{State.capitalize()}**")
                    figch = px.bar(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))

            elif att == "Transaction_amount":
                if chart == "line":
                    st.write(f"**{State.capitalize()}**")
                    figch = px.line(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
                else:
                    st.write(f"**{State.capitalize()}**")
                    figch = px.bar(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))

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

            if att == "Registered_users":
                if chart == "line":
                    st.write(f"**{State.capitalize()}**")
                    figch = px.line(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
                else:
                    st.write(f"**{State.capitalize()}**")
                    figch = px.bar(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))

            elif att == "App_opens":
                if chart == "line":
                    st.write(f"**{State.capitalize()}**")
                    figch = px.line(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
                else:
                    st.write(f"**{State.capitalize()}**")
                    figch = px.bar(df12, x='District', y=att,width=850, height=525)
                    st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))





# cd Projects/Project_2
# streamlit run PhonePe_pulse.py