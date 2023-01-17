import streamlit as st
import re
import calcul
import plotly.express as px

st.set_page_config(
    page_title="Tilt case"
)

st.title('Breakdown of electricity consumption')
email_pattern = r'\w+\.*-*\w*@[\w+.-]+\.\w+'

if 'user' not in st.session_state or 'email' not in st.session_state:
    username = st.text_input(
        'Please, enter a username :',
        placeholder='username'
    )

    st.session_state['user'] = username

    email = st.text_input(
        'Please, enter your email address :',
        placeholder='email.addresse@tilt.fr'
    )

    validation_1 = st.button('Ok', key='ok_1')

    if validation_1 and (not username or not email):
        st.error('Please, enter a username and email address.')
        st.stop()

    if not username or not email:
        st.stop()

    if email and not re.match(email_pattern, email):
        st.error('Email format is not valid.')
        st.stop()

    st.session_state['email'] = email


st.write(f'Hello {st.session_state["user"].capitalize()}, let see how your electrical consumption is distributed.')
# if 'data' not in st.session_state:
st.write('Please, select your appliances in the following list :')

category_F, category_A, category_L = st.columns(3)

with category_F:
    fridge = st.checkbox('Fridge')
    freezer = st.checkbox('Freezer')

with category_A:
    washing_machine = st.checkbox('Washing machine')
    dishwasher = st.checkbox('Dishwasher')
    induction_stove = st.checkbox('Induction stove')

with category_L:
    tv = st.checkbox('tv')
    small_lignt = st.checkbox('Small lignt')
    big_light = st.checkbox('Big light')

# validation_2 = st.button('Ok', key='ok_2')

if not fridge and not freezer and not washing_machine and not dishwasher \
        and not induction_stove and not tv and not small_lignt and not big_light:
    st.write('Select at least one appliance.')
    st.stop()

# if 'data' not in st.session_state:
#     if not validation_2:
#         st.stop()

data = {
        'fridge': {
            'presence': fridge,
            'category': 'F',
            'power_kW': 2,
            'min_h': 6,
            'max_h': 8
        },
        'freezer': {
            'presence': freezer,
            'category': 'F',
            'power_kW': 2.5,
            'min_h': 6,
            'max_h': 8
        },
        'washing_machine': {
            'presence': washing_machine,
            'category': 'A',
            'power_kW': 1.5,
            'min_h': 1,
            'max_h': 4
        },
        'dishwasher': {
            'presence': dishwasher,
            'category': 'A',
            'power_kW': 2.5,
            'min_h': 1,
            'max_h': 4
        },
        'induction_stove': {
            'presence': induction_stove,
            'category': 'A',
            'power_kW': 3,
            'min_h': 1,
            'max_h': 4
        },
        'tv': {
            'presence': tv,
            'category': 'L',
            'power_kW': .5,
            'min_h': 4,
            'max_h': 24
        },
        'small_light': {
            'presence': small_lignt,
            'category': 'L',
            'power_kW': .1,
            'min_h': 4,
            'max_h': 24
        },
        'big_light': {
            'presence': big_light,
            'category': 'L',
            'power_kW': .8,
            'min_h': 4,
            'max_h': 24
        },
    }

    # st.session_state['data'] = data

# data = st.session_state['data']

df = calcul.build_base_df(data)

min_consumption = int(round(df['min_kWh'].sum(), 0))
max_consumption = int(round(min(df['max_kWh'].sum(), 75), 0))
consumption_avg = int(round((min_consumption + max_consumption) / 2, 0))

e_tot = st.number_input(
    f"Please, enter your measured consumption which is expected to be at least \
{min_consumption} kWh and at most {max_consumption} kWh :",
    min_value=min_consumption,
    max_value=max_consumption,
    value=consumption_avg
)

validation_3 = st.button('Ok', key='ok_3')

if not validation_3:
    st.stop()

df = calcul.estimate(df, e_tot)

fig = px.bar(
    df,
    x=df.index,
    y='esti_kWh',
    labels={
             "esti_kWh": "Consumption in kWh",
             "index": "Appliances"
         },
    title="Electrical consumption per appliance",
    text_auto='.2f'
)

st.plotly_chart(fig)
