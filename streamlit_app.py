# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# from snowflake.snowpark.context import get_active_session


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)


# session = get_active_session()
# -- Added for SniS changes --
cnx = st.connection("snowflake")
session = cnx.session()
# ----------------------------
my_dataframe = session.table("smoothies.public.fruit_options").select(
                                col('FRUIT_NAME'),
                                col('SEARCH_ON')
                            )

# Convert to Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5,
)
if ingredients_list:
    # Concat selected fruits as a string
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        cond = pd_df['FRUIT_NAME'] == fruit_chosen
        search_on = pd_df.loc[cond, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        # Display more information for each fruit
        st.header(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
  

  
    # Insert Notes: columns not included in the insert command
    # - order_id happens automatically because the ORDERS table uses Unique ID SEQUENCES
    # - order_filled is default to FALSE
    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
                         values (
                            '""" + ingredients_string + """'
                           ,'""" + name_on_order + """'
                         )"""

    # Submit Order        
    time_to_insert = st.button("Submit Order")

    success_message = 'Your Smoothie is ordered, ' + name_on_order + '!'
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(success_message, icon="✅")

