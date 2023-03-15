import streamlit as st  # web development
import pandas as pd  # read csv, df manipulation
from sklearn.preprocessing import StandardScaler
import plotly.express as px  # interactive charts
from millify import millify
import requests
# import time
import json

st.set_page_config(
    page_title='Time Series Dashboard',
    page_icon='⏳',
    layout='wide'
)

# dashboard title
st.title("Timeseries Anomaly Detection")
st.write('''
Real-time anomaly detection for **timeseries** in terms of credit card fraud transaction detection.
#### ***Description***
The dataset contains transactions made by credit cards in ***September 2013*** by European cardholders.
''')
st.markdown("""---""")
file = st.sidebar.file_uploader('## Upload your data', type='csv')
if file is not None:
    data_store = pd.read_csv(file)
    data_store = data_store.drop_duplicates()
else:
    st.warning('Warning, Upload Csv File format to begin...')

def plot_time_graph(data):
    plot = px.bar(data, x='Time (second)', y='Amount',color='Class', color_discrete_sequence=['green', "red"])
    plot.update_layout(width=1300, height=500)
    return plot
def plot_scatter_plot(data):
    plot = px.scatter(data, x='Time (second)', y='Amount',size='Amount',symbol='Class')
    plot.update_layout(width=1300, height=500)
    return plot
def plot_amount_graph(data):
    plot = px.bar(data, x='Class', y='Amount',
                   color='Class', color_discrete_sequence=['green', "red"])
    return plot

def data_preprocessing(row):
    sc = StandardScaler()
    chosen_features = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13',
                       'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27',
                       'V28']
    data=data_store
    X = data[chosen_features]
    X = sc.fit_transform(X)
    X = pd.DataFrame(X, columns=chosen_features)
    first_row = X.iloc[row]
    data = data.drop('Class', axis=1)
    original_df = data.iloc[row]
    # convert the first row to a dictionary with column names as keys
    row_dict = first_row.to_dict()
    return [row_dict, original_df]

def predict_model(row):
    url = 'https://dnn-api.onrender.com/predict'
    data = data_preprocessing(row)
    input_json = json.dumps(data[0])
    response = requests.post(url, data=input_json)
    pred = round(eval(eval(response.text)))
    pred = pd.DataFrame([pred], columns=['Class'])
    X=pd.DataFrame(data[1].to_frame().T)
    X.reset_index(drop=True, inplace=True)
    result = X.join(pred)
    return result

# creating a single-element container.
frame = st.empty()
def count_function(num):
    subset = pd.DataFrame()
    subset2 = pd.DataFrame()
    fraud_df = pd.DataFrame(columns=['Time (second)','Amount'])
    fraud = 0
    valid = 0
    for x in range(num):
        X = predict_model(x)
        for i, row in X.iterrows():
            subset = pd.concat([subset, row.to_frame().T], ignore_index=True)
            subset2 = pd.concat([subset2, row.to_frame().T], ignore_index=True)
            avg=subset["Amount"].mean()
            if subset.loc[0, 'Class'] == 1:
                fraud += 1
                fraud_df = pd.concat([fraud_df, subset.loc[0].to_frame().T], ignore_index=True)
                fraud_df.loc[fraud, 'Time (second)'] = pd.to_datetime(subset.loc[0, 'Time (second)'], unit='s')
                fraud_df = fraud_df.drop(['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13',
                                          'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24',
                                          'V25', 'V26', 'V27', 'V28', 'Class'], axis=1)
            elif subset.loc[0, 'Class'] == 0:
                valid += 1
            if len(subset) < 15:
                pass
            else:
                subset.drop(index=subset.index[0], axis=0, inplace=True)

            with frame.container():
                # create three columns
                avg_amt, valid_count, fraud_count = st.columns(3)
                # fill in those three columns with respective metrics
                avg_amt.metric(label="Average Amount 💲",
                               value=f"$ {round(avg)}",)
                valid_count.metric(
                    label="Number of Legitimate transactions ✅", value=f'{millify(valid)}',delta=1)
                fraud_count.metric(
                    label="Number of Fraudulent transctions ❌", value=f'{millify(fraud)}', delta=1, delta_color="inverse")
                st.markdown("""---""")
                fig_col1, fig_col2 = st.columns(2)
                with fig_col1:
                    st.markdown("### Transactions over time")
                    st.write(plot_time_graph(subset))
                # with fig_col2:
                st.markdown("""---""")
                st.write(plot_scatter_plot(subset))
                tab_col1, tab_col2 = st.columns(2)
                with tab_col1:
                    st.markdown('### Fraudulent transactions')
                    st.write(fraud_df)
                with tab_col2:
                    st.markdown('### Sum Total Amounts')
                    st.write(plot_amount_graph(subset2))
        # time.sleep(0.9)

# count_function()


def begin():
    count_function(len(data_store))
    # pass


if file:
    button1=st.sidebar.button('Launch', type='primary', use_container_width=True)
else:
    button1=st.sidebar.button('Launch',disabled=True, type='primary', use_container_width=True)

button2=st.sidebar.button('Interrupt', type='secondary', use_container_width=True)
st.sidebar.markdown("""
# GROUP 25

 Raphael Egbudom K2272303

 Ehiaghe Oziegbe K2257084

 Amiede Iyamu K2225150
""")
if button1:
    begin()

if button2:
    st.stop()
