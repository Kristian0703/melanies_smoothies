# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input('Name on Smoothie:')
#st.write('The name on the Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()
st_df(pd_df)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    #max_selections = 5 
)

# Validate the number of ingredients selected
if len(ingredients_list) > 5:
    st.warning("You can only select up to 5 ingredients. Please deselect one to proceed.")
else:
    if ingredients_list:
        ingredients_string = ''
    
        for fruit_choosen in ingredients_list:
            ingredients_string += fruit_choosen + ' '

            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
            
            st.subheader(fruit_choosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon" + fruit_choosen)
            fv_df = st.dataframe(fruityvice_response.json(), use_container_width=True)

        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
        #st.write(my_insert_stmt)
        #st.stop()
        
        time_to_insert = st.button('Submit Order')
        
        if time_to_insert:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}',  icon="✅")


