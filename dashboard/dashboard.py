import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_order_harian_df(df):
    order_harian_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    order_harian_df = order_harian_df.reset_index()
    order_harian_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return order_harian_df

def create_orders_bulanan_df(df):
    orders_bulanan_df = df.resample(rule="M", on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    orders_bulanan_df.index = orders_bulanan_df.index.strftime('%B-%Y')
    orders_bulanan_df = orders_bulanan_df.reset_index()
    orders_bulanan_df.rename(columns={
        "order_id": "order_count",
        "order_purchase_timestamp": "month_year",
        "price": "revenue"
    }, inplace=True)

    return orders_bulanan_df
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    return bycity_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique", 
        "price": "sum" 
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = gabungan_df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

gabungan_df = pd.read_csv("./dashboard/gabungan_df.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
gabungan_df.sort_values(by="order_purchase_timestamp", inplace=True)
gabungan_df.reset_index(inplace=True)
 
for column in datetime_columns:
    gabungan_df[column] = pd.to_datetime(gabungan_df[column])

min_date = gabungan_df["order_purchase_timestamp"].min()
max_date = gabungan_df["order_purchase_timestamp"].max()

with st.sidebar:
    option = st.radio("Pilih Mode",('Keseluruhan','Tahunan','Rentang Waktu'))
    if(option == 'Rentang Waktu'):
        start_date, end_date = st.date_input(
            label='Rentang Waktu',min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    elif(option == 'Tahunan'):
        list_tahun = list(range(min_date.year, max_date.year+1))
        tahun = st.selectbox("Pilih Tahun", list_tahun)

st.header("E-Commerce Public")
if(option == 'Rentang Waktu'):
    main_df = gabungan_df[(gabungan_df["order_purchase_timestamp"] >= str(start_date)) & (gabungan_df["order_purchase_timestamp"] <= str(end_date))]
    order_harian_df = create_order_harian_df(main_df)
    st.subheader('Order Harian')
    col1, col2 = st.columns(2)
    with col1:
        total_orders = round(order_harian_df.order_count.sum(),2)
        st.metric("Total Pesanan", value=total_orders)

    with col2:
        total_revenue = round(order_harian_df.revenue.sum(),3)
        st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(order_harian_df["order_purchase_timestamp"], order_harian_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
    ax.set_title("Jumlah Order Harian ("+ str(start_date)+" - "+str(end_date)+")", fontsize=16)
    ax.set_ylabel('Jumlah Order', fontsize=12)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    st.pyplot(fig)

    st.subheader("Customer Demographics")
    
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    bystate_df = create_bystate_df(main_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan States", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)
    bycity_df = create_bycity_df(main_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_city",
        data=bycity_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan City", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)

    st.subheader("Best Customer Based on RFM Parameters")

    rfm_df = create_rfm_df(main_df)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    
    with col3:
        avg_frequency = round(rfm_df.monetary.mean(), 3)
        st.metric("Average Monetary", value=avg_frequency)
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
    
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, fontsize=12) 
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, fontsize=12) 
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, fontsize=12) 
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35)
    
    st.pyplot(fig)
    

elif(option == 'Tahunan'):
    st.subheader('Order Tahunan - '+str(tahun))
    orders_bulanan_df = create_orders_bulanan_df(gabungan_df)
    orders_tahunan_df = orders_bulanan_df[orders_bulanan_df['month_year'].str.contains(str(tahun))]
    col1, col2 = st.columns(2)
    with col1:
        total_orders = round(orders_tahunan_df.order_count.sum(),2)
        st.metric("Total Pesanan", value=total_orders)

    with col2:
        total_revenue = round(orders_tahunan_df.revenue.sum(),3)
        st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(orders_tahunan_df["month_year"], orders_tahunan_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
    ax.set_title("Jumlah Order Bulanan - " + str(tahun), fontsize=16)
    ax.set_ylabel('Jumlah Order', fontsize=12)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    st.pyplot(fig)

    st.subheader("Customer Demographics")
    
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    byyear_df = gabungan_df[gabungan_df['order_purchase_timestamp'].dt.year == tahun]
    bystate_df = create_bystate_df(byyear_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan States", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)
    bycity_df = create_bycity_df(byyear_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_city",
        data=bycity_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan City", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)

    st.subheader("Best Customer Based on RFM Parameters")

    rfm_df = create_rfm_df(byyear_df)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    
    with col3:
        avg_frequency = round(rfm_df.monetary.mean(), 3)
        st.metric("Average Monetary", value=avg_frequency)
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
    
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, fontsize=12) 
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, fontsize=12) 
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, fontsize=12) 
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35)
    
    st.pyplot(fig)

else:
    st.subheader('Order Keseluruhan')
    orders_bulanan_df = create_orders_bulanan_df(gabungan_df)
    col1, col2 = st.columns(2)
    with col1:
        total_orders = round(orders_bulanan_df.order_count.sum(),2)
        st.metric("Total Pesanan", value=total_orders)

    with col2:
        total_revenue = round(orders_bulanan_df.revenue.sum(),3)
        st.metric("Total Revenue", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(orders_bulanan_df["month_year"], orders_bulanan_df["order_count"], marker='o', linewidth=2, color="#72BCD4") 
    ax.set_title("Jumlah Order Bulanan (" + str(min_date.year) +" - "+str(max_date.year+1)+")", fontsize=16)
    ax.set_ylabel('Jumlah Order', fontsize=12)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    st.pyplot(fig)

    st.subheader("Customer Demographics")
 
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    bystate_df = create_bystate_df(gabungan_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan States", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)
    bycity_df = create_bycity_df(gabungan_df)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        x="customer_id", 
        y="customer_city",
        data=bycity_df.sort_values(by="customer_id", ascending=False).head(5),
        palette=colors,
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer bedasarkan City", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis ='y', labelsize=30)
    st.pyplot(fig)

    st.subheader("Best Customer Based on RFM Parameters")

    rfm_df = create_rfm_df(gabungan_df)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    
    with col3:
        avg_frequency = round(rfm_df.monetary.mean(), 3)
        st.metric("Average Monetary", value=avg_frequency)
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
    
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, fontsize=12) 
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, fontsize=12) 
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35)
    
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, fontsize=12) 
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35)
    
    st.pyplot(fig)


