import pandas as pd
import plotly.express as px


def build_base_df(data):
    df = pd.DataFrame(data).transpose()
    df['min_kWh'] = df['power_kW'] * df['min_h'] * df['presence']
    df['avg_kWh'] = df['power_kW'] * (df['min_h'] + df['max_h']) / 2 * df['presence']
    df['max_kWh'] = df['power_kW'] * df['max_h'] * df['presence']
    df['ratio_to_avg'] = df['avg_kWh'] / df['avg_kWh'].sum()
    df['ratio_to_max'] = df['max_kWh'] / df['max_kWh'].sum()
    df['ratio_to_min'] = df['min_kWh'] / df['min_kWh'].sum()

    return df


def first_estimation(df, e_tot):
    df['esti_kWh'] = df.apply(lambda x: min(e_tot * x['ratio_to_avg'], x['max_kWh']), axis=1)
    df['esti_kWh'] = df.apply(lambda x: max(x['esti_kWh'], x['min_kWh']), axis=1)
    df['esti_h'] = df['esti_kWh'] / df['power_kW']
    df = df.fillna(0)

    return df


def test_esti(df):
    df = df[(df['esti_kWh'] <= df['min_kWh']) & (df['esti_kWh'] != 0)]
    return df.shape[0] == 0


def test_esti_2(df):
    df = df[(df['esti_kWh'] >= df['max_kWh']) & (df['esti_kWh'] != 0)]
    return df.shape[0] == 0


def estimation_correction_type_1(df, e_tot):
    df_1 = df[df['esti_kWh'] == df['min_kWh']]

    df_2 = df[df['esti_kWh'] > df['min_kWh']]

    df_2 = df_2.drop(['ratio_to_avg'], axis=1)
    df_2['ratio_to_avg'] = df_2['avg_kWh'] / df_2['avg_kWh'].sum()

    e_tot_residual = e_tot - df_1['esti_kWh'].sum()

    df_2['new'] = df_2.apply(lambda x: min(e_tot_residual * x['ratio_to_avg'], x['max_kWh']), axis=1)
    df_2['new'] = df_2.apply(lambda x: max(x['new'], x['min_kWh']), axis=1)
    df_2 = df_2.drop(['esti_kWh'], axis=1).rename(columns={'new': 'esti_kWh'})

    return df_1, df_2, e_tot_residual


def estimation_correction_type_1_bis(df, e_tot):
    df_1 = df[df['esti_kWh'] == df['max_kWh']]

    df_2 = df[df['esti_kWh'] < df['max_kWh']]

    df_2 = df_2.drop(['ratio_to_avg'], axis=1)
    df_2['ratio_to_avg'] = df_2['avg_kWh'] / df_2['avg_kWh'].sum()

    e_tot_residual = e_tot - df_1['esti_kWh'].sum()

    df_2['new'] = df_2.apply(lambda x: min(e_tot_residual * x['ratio_to_avg'], x['max_kWh']), axis=1)
    df_2['new'] = df_2.apply(lambda x: max(x['new'], x['min_kWh']), axis=1)
    df_2 = df_2.drop(['esti_kWh'], axis=1).rename(columns={'new': 'esti_kWh'})

    return df_1, df_2, e_tot_residual


def estimation_correction_type_2(df, e_tot):
    if df['esti_kWh'].sum() < e_tot:
        print('Correction because underestimating')
        df['esti_kWh'] = e_tot * df['ratio_to_max']
        df['esti_h'] = df['esti_kWh'] / df['power_kW']
    elif df['esti_kWh'].sum() > e_tot:
        print('Correction because overestimating')
        df['esti_kWh'] = df.apply(lambda x: min(e_tot * x['ratio_to_min'], x['min_kWh']), axis=1)
        df['esti_h'] = df['esti_kWh'] / df['power_kW']
    else:
        print('Estimation correct')

    return df


def estimate(df, e_tot):
    df = first_estimation(df, e_tot)

    if not test_esti(df):
        df_1, df_2, e_tot_residual = estimation_correction_type_1(df, e_tot)

        if not test_esti(df_2):
            df_21, df_22, e_tot_residual = estimation_correction_type_1(df_2, e_tot_residual)
            df = pd.concat([df_1, df_21, df_22])
        else:
            df = pd.concat([df_1, df_2])

    if not test_esti_2(df):
        df_1, df_2, e_tot_residual = estimation_correction_type_1_bis(df, e_tot)

        if not test_esti(df_2):
            df_21, df_22, e_tot_residual = estimation_correction_type_1_bis(df_2, e_tot_residual)
            df = pd.concat([df_1, df_21, df_22])
        else:
            df = pd.concat([df_1, df_2])

    return estimation_correction_type_2(df, e_tot)


def print_summary(df, e_tot=None):
    e_tot = e_tot if e_tot else 'no input yet'
    if 'esti_kWh' in df.columns:
        print(f"""min:       {df['min_kWh'].sum()} kWh
avg:       {df['avg_kWh'].sum()} kWh
max:       {df['max_kWh'].sum()} kWh
estimated: {df['esti_kWh'].sum()} kWh
input:     {e_tot} kWh
        """)
    else:
        print(f"""min:       {df['min_kWh'].sum()} kWh
avg:       {df['avg_kWh'].sum()} kWh
max:       {df['max_kWh'].sum()} kWh
input:     {e_tot} kWh
        """)


def bargraph(df, third_field='esti_kWh', third_field_long='Estimation consumption', e_tot=None):
    df_display = pd.concat(
        [
            pd.concat(
                (df[['min_kWh']].rename(columns={'min_kWh': 'Energy'}),
                df.apply(lambda x: 'Minimum consumption', axis=1).rename('Type')), axis=1
            ),
            pd.concat(
                (df[['max_kWh']].rename(columns={'max_kWh': 'Energy'}),
                df.apply(lambda x: 'Maximum consumption', axis=1).rename('Type')), axis=1
            ),
            pd.concat(
                (df[[third_field]].rename(columns={third_field: 'Energy'}),
                df.apply(lambda x: third_field_long, axis=1).rename('Type')), axis=1
            )
        ],
        axis=0
    )
    print_summary(df, e_tot)
    return px.bar(
        df_display,
        x=df_display.index,
        y='Energy',
        color='Type',
        barmode='group',
        labels={
                 "Energy": "Consumption in kWh",
                 "index": "Appliances"
             },
        title="Electrical consumption per appliance",
        text_auto='.2f'
    )


