import pandas as pd


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
    df = df[df['esti_kWh'] <= df['min_kWh']]
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

    return estimation_correction_type_2(df, e_tot)


def print_summary(df, e_tot):
    print(f"""min:       {df['min_kWh'].sum()} kWh
avg:       {df['avg_kWh'].sum()} kWh
max:       {df['max_kWh'].sum()} kWh
estimated: {df['esti_kWh'].sum()} kWh
input:     {e_tot} kWh
    """)

