import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Mapping nama provinsi
NAMA_PROVINSI = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba",
    "PE": "Pernambuco", "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "SE": "Sergipe",
    "SP": "São Paulo", "TO": "Tocantins"
}

# Memuat Data (Ganti dengan path dataset yang sesuai)
@st.cache_data
def muat_data():
    df = pd.read_csv("dashboard/ecommerce_final.csv")  # Ganti dengan dataset yang sesuai
    df["customer_state"] = df["customer_state"].map(NAMA_PROVINSI)  # Ubah kode provinsi menjadi nama lengkap
    df["order_date"] = pd.to_datetime(df["order_date"])  # Pastikan order_date dalam format datetime
    return df

df = muat_data()

# Sidebar untuk filter
st.sidebar.header("Filter")
provinsi_terpilih = st.sidebar.multiselect("Pilih Provinsi", df["customer_state"].unique(), default=df["customer_state"].unique())
df_terfilter = df[df["customer_state"].isin(provinsi_terpilih)]

# Mengelompokkan data untuk visualisasi
data_pembelian_kota = df_terfilter.groupby("customer_state").agg(
    total_belanja=("price", "sum"),
    total_pelanggan=("customer_unique_id", "nunique")
).reset_index()
data_pembelian_kota = data_pembelian_kota.sort_values(by="total_belanja", ascending=False)

# Tata Letak
st.title("Dasbor Penjualan E-Commerce")
st.markdown("### Gambaran Kinerja Penjualan di Berbagai Provinsi di Brasil")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Belanja")
with col2:
    st.subheader("Total Pelanggan")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    provinsi_teratas = data_pembelian_kota.head(10)
    ax.pie(provinsi_teratas["total_belanja"], labels=provinsi_teratas["customer_state"], autopct="%1.1f%%",
           colors=sns.color_palette("pastel"), wedgeprops={'edgecolor': 'black'})
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    ax.pie(provinsi_teratas["total_pelanggan"], labels=provinsi_teratas["customer_state"], autopct="%1.1f%%",
           colors=sns.color_palette("coolwarm"), wedgeprops={'edgecolor': 'black'})
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribusi Status Pesanan")
    status_terpilih = ['delivered', 'shipped', 'processing', 'approved']
    hitung_status_pesanan = df[df["order_status"].isin(status_terpilih)]["order_status"].value_counts()
    st.bar_chart(hitung_status_pesanan)

with col4:
    st.subheader("Histogram Repeat Order")
    customer_orders = df.groupby("customer_unique_id").agg(
        first_purchase=("order_date", "min"),
        last_purchase=("order_date", "max"),
        total_orders=("order_id", "count")
    ).reset_index()
    customer_orders["order_span_days"] = (customer_orders["last_purchase"] - customer_orders["first_purchase"]).dt.days
    bins = [0, 7, 14, 30, 90, 180, 365, float('inf')]
    labels = ["≤ 1 minggu", "≤ 2 minggu", "≤ 1 bulan", "≤ 3 bulan", "≤ 6 bulan", "≤ 1 tahun", "> 1 tahun"]
    customer_orders["repeat_order_category"] = pd.cut(customer_orders["order_span_days"], bins=bins, labels=labels)
    repeat_order_counts = customer_orders["repeat_order_category"].value_counts().sort_index()
    st.bar_chart(repeat_order_counts)

# Scatter Plot Pola Belanja Bulanan
st.subheader("Scatter Plot: Pola Belanja Bulanan")
df_bulanan = df.groupby([df["order_date"].dt.to_period("M"), "customer_unique_id", "customer_state"]).agg(
    total_belanja=("price", "sum")
).reset_index()
df_bulanan["order_date"] = df_bulanan["order_date"].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(
    x=df_bulanan["order_date"], 
    y=df_bulanan["total_belanja"], 
    hue=df_bulanan["customer_state"],
    palette="viridis",
    alpha=0.7
)
plt.xlabel("Bulan Order")
plt.ylabel("Total Belanja per Customer")
plt.title("Scatter Plot: Pola Belanja Bulanan")
plt.xticks(rotation=45, fontsize=8)  # Mengecilkan ukuran teks
st.pyplot(fig)

# Tabel - Statistik Pelanggan per Provinsi
st.subheader("Statistik Pelanggan per Provinsi")
statistik_pelanggan = df.groupby("customer_state").agg(
    pelanggan_unik=("customer_unique_id", "nunique"),
    rata_rata_belanja=("price", "mean")
).reset_index()
st.dataframe(statistik_pelanggan)
