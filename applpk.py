import io
import os
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import requests

# Pastikan matplotlib menggunakan backend 'Agg'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="LPK Yutaka Education Center - Realtime CSV",
    page_icon="🌸",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-image: linear-gradient(rgba(255, 245, 247, 0.92), rgba(253, 242, 244, 0.92)), 
                            url('https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=2000&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #1e293b;
        }
        .main { background: transparent; }
        .main-heading {
            font-size: 24px !important;
            font-weight: 800;
            color: #be185d;
            line-height: 1.2;
            margin-top: 0px;
            margin-bottom: 2px;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            letter-spacing: 0.5px;
        }
        .sub-heading {
            font-size: 10px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e1b2e 0%, #2e263d 100%);
            border-right: 1px solid #f472b6;
        }
        .ai-logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px 5px 5px 5px;
            text-align: center;
        }
        .ai-logo-icon {
            font-size: 38px;
            font-weight: 900;
            font-family: 'Segoe UI', sans-serif;
            color: #f43f5e;
            background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 10px rgba(244, 63, 94, 0.3);
            letter-spacing: 2px;
            margin-bottom: 2px;
            border-bottom: 2px dashed #fb7185;
            padding-bottom: 2px;
        }
        .ai-logo-text {
            font-size: 12px;
            font-weight: 700;
            color: #fdf2f8;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }
        section[data-testid="stSidebarNav"] { display: none; }
        div[data-testid="stMetricValue"] { color: #be185d !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# ================= URL GOOGLE SHEETS PER TAB SPESIFIK =================
URL_AKADEMIK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=2089137159&single=true&output=csv"
URL_SKILL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=1757021272&single=true&output=csv"
URL_FISIK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=584979880&single=true&output=csv"
URL_JFT = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=1299299093&single=true&output=csv"
URL_RAPORT = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=895668861&single=true&output=csv"
URL_KATEGORI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?gid=1122353673&single=true&output=csv"

@st.cache_data(ttl=10)
def load_sheet_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return pd.DataFrame()
            
        df = pd.read_csv(io.StringIO(response.text))
        
        clean_cols = []
        seen = {}
        for c in df.columns:
            c_cleaned = str(c).strip()
            if c_cleaned in seen:
                seen[c_cleaned] += 1
                c_cleaned = f"{c_cleaned}_{seen[c_cleaned]}"
            else:
                seen[c_cleaned] = 0
            clean_cols.append(c_cleaned)
        df.columns = clean_cols
        
        for col in df.columns:
            c_low = col.lower()
            if any(k in c_low for k in ["nis", "nis siswa", "id siswa", "no induk"]) and "nis" not in [x.lower() for x in df.columns if x != col]:
                df.rename(columns={col: "NIS"}, inplace=True)
            elif any(k in c_low for k in ["nama", "nama siswa", "name", "名前"]):
                df.rename(columns={col: "Nama"}, inplace=True)
            elif any(k in c_low for k in ["kelas", "class", "level"]):
                df.rename(columns={col: "Kelas"}, inplace=True)
            elif any(k in c_low for k in ["tanggal", "date"]):
                df.rename(columns={col: "Tanggal"}, inplace=True)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=10)
def load_all_sheets_data():
    df_akademik = load_sheet_from_url(URL_AKADEMIK)
    df_skill = load_sheet_from_url(URL_SKILL)
    df_fisik = load_sheet_from_url(URL_FISIK)
    df_jft = load_sheet_from_url(URL_JFT)
    df_raport = load_sheet_from_url(URL_RAPORT)
    df_kategori = load_sheet_from_url(URL_KATEGORI)
    return df_akademik, df_skill, df_fisik, df_jft, df_raport, df_kategori

df_akademik, df_skill, df_fisik, df_jft, df_raport, df_kategori = load_all_sheets_data()

def to_excel_bytes(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(output, index=False, sheet_name="Data_LPK")
    return output.getvalue()

def huruf_ke_angka(val):
    if pd.isna(val) or str(val).strip() == "": return 80.0
    val_str = str(val).strip().upper()
    if val_str == "A": return 90.0
    elif val_str == "B": return 80.0
    elif val_str == "C": return 70.0
    elif val_str == "D": return 60.0
    else:
        try: return float(val_str)
        except: return 80.0

def angka_ke_abjad(val):
    if pd.isna(val) or val == 0: return "C"
    if val >= 85: return "A"
    elif val >= 75: return "B"
    elif val >= 65: return "C"
    else: return "D"

def get_clean_keterangan(subtest, val):
    if val >= 85: return f"Sangat baik dalam penguasaan materi {subtest} serta menunjukkan performa tingkat tinggi."
    elif val >= 70: return f"Memahami materi {subtest} dengan baik serta mampu mengikuti proses pembelajaran secara aktif."
    elif val >= 50: return f"Memiliki pemahaman dasar pada {subtest}, namun memerlukan peningkatan konsistensi latihan."
    else: return f"Memerlukan perhatian khusus dan bimbingan intensif pada materi {subtest}."

def get_val_by_name(df_source, name_val, keywords):
    if df_source.empty: return 80.0
    sub_df = pd.DataFrame()
    if name_val and "Nama" in df_source.columns:
        sub_df = df_source[df_source["Nama"].astype(str).str.strip().str.lower() == str(name_val).strip().lower()]
        
    target_df = sub_df if not sub_df.empty else df_source
    
    for col in target_df.columns:
        if any(k.lower() in col.lower() for k in keywords):
            s = pd.to_numeric(target_df[col], errors="coerce").dropna()
            if not s.empty: return s.mean()
            else:
                val_str = target_df[col].dropna()
                if not val_str.empty: return huruf_ke_angka(val_str.iloc[-1])
    return 80.0

if "active_menu" not in st.session_state:
    st.session_state.active_menu = "📊 Dashboard"

# ================= SIDEBAR NAVIGASI =================
with st.sidebar:
    st.markdown(
        """
            <div class="ai-logo-container">
                <div class="ai-logo-icon">豊</div>
                <div class="ai-logo-text">LPK Yutaka Education Center</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(244, 114, 182, 0.3); margin: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #fda4af; font-size: 10px; font-weight: 700; padding-left: 5px; margin-bottom: 6px; letter-spacing: 1px;'>NAVIGASI UTAMA</p>", unsafe_allow_html=True)

    menus = [
        ("📊 Dashboard", "📊 Dashboard"),
        ("📄 Raport Siswa", "📄 Raport"),
        ("🎯 JFT Siswa", "🎯 JFT Siswa"),
        ("📤 Upload & Unduh", "📤 Upload/Unduh"),
    ]

    for label, menu_key in menus:
        if st.button(label, key=f"btn_{menu_key}", use_container_width=True):
            st.session_state.active_menu = menu_key
            st.rerun()

    if st.button("🔄 Refresh Data Realtime", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("<p style='color: #cbd5e1; font-size: 9px; text-align: center;'>SAKURA REALTIME CSV // v8.1</p>", unsafe_allow_html=True)

menu = st.session_state.active_menu

# ================= MENU 1: DASHBOARD =================
if menu == "📊 Dashboard":
    st.markdown("<div class='main-heading'>LAPORAN PERKEMBANGAN PENDIDIKAN & TRAINING</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-heading'>SAKURA SYSTEM REALTIME MONITORING — LPK YUTAKA</div>", unsafe_allow_html=True)

    df_ui = df_akademik.copy()
    for c in ["Kelas", "Nama", "Bab", "Sensei"]:
        if c not in df_ui.columns: df_ui[c] = "Semua"

    st.markdown("#### 🔍 Filter Data Siswa & Periode Tanggal (Bulan Berjalan)")
    
    fd1, fd2 = st.columns(2)
    with fd1:
        start_date_dash = st.date_input("Dari Tanggal", value=pd.to_datetime("2026-09-01"))
    with fd2:
        end_date_dash = st.date_input("Sampai Tanggal", value=pd.to_datetime("2026-09-30"))

    f1, f2, f3 = st.columns(3)
    with f1:
        list_kelas = sorted([str(x) for x in df_ui["Kelas"].dropna().unique() if str(x).strip() not in ["nan", ""]])
        sel_kelas = st.selectbox("Kelas", ["Semua Kelas"] + list_kelas)
    
    if sel_kelas != "Semua Kelas" and "Kelas" in df_ui.columns:
        list_nama = sorted([str(x) for x in df_ui[df_ui["Kelas"].astype(str) == sel_kelas]["Nama"].dropna().unique() if str(x).strip() not in ["nan", ""]])
    else:
        list_nama = sorted([str(x) for x in df_ui["Nama"].dropna().unique() if str(x).strip() not in ["nan", ""]])

    with f2:
        sel_nama = st.selectbox("Nama Siswa", ["Semua Nama"] + list_nama)
    with f3:
        list_bab = sorted([str(x) for x in df_ui["Bab"].dropna().unique() if str(x).strip() not in ["nan", ""]]) if "Bab" in df_ui.columns else []
        sel_bab = st.selectbox("Bab", ["Semua Bab"] + list_bab)

    f4, f5 = st.columns(2)
    with f4:
        list_sensei = sorted([str(x) for x in df_ui["Sensei"].dropna().unique() if str(x).strip() not in ["nan", ""]]) if "Sensei" in df_ui.columns else []
        sel_sensei = st.selectbox("Sensei", ["Semua Sensei"] + list_sensei)
    with f5:
        ignore_date = st.checkbox("Abaikan Filter Rentang Tanggal", value=False)

    df_v = df_akademik.copy()
    if sel_kelas != "Semua Kelas" and "Kelas" in df_v.columns: df_v = df_v[df_v["Kelas"].astype(str) == sel_kelas]
    if sel_nama != "Semua Nama" and "Nama" in df_v.columns: df_v = df_v[df_v["Nama"].astype(str) == sel_nama]
    if sel_bab != "Semua Bab" and "Bab" in df_v.columns: df_v = df_v[df_v["Bab"].astype(str) == sel_bab]
    if sel_sensei != "Semua Sensei" and "Sensei" in df_v.columns: df_v = df_v[df_v["Sensei"].astype(str) == sel_sensei]

    if not ignore_date and "Tanggal" in df_v.columns:
        df_v["ParsedDate"] = pd.to_datetime(df_v["Tanggal"], errors="coerce")
        df_v = df_v[(df_v["ParsedDate"] >= pd.to_datetime(start_date_dash)) & (df_v["ParsedDate"] <= pd.to_datetime(end_date_dash))]

    num_cols = df_v.select_dtypes(include=["number"]).columns
    score_col = "Pos Test" if "Pos Test" in df_v.columns else (num_cols[0] if len(num_cols) > 0 else None)
    tot_p = df_v["NIS"].nunique() if "NIS" in df_v.columns else (df_v["Nama"].nunique() if "Nama" in df_v.columns else len(df_v))
    avg_s = pd.to_numeric(df_v[score_col], errors="coerce").mean() if score_col and score_col in df_v.columns else 80.0
    if pd.isna(avg_s): avg_s = 80.0

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1: st.metric("TOTAL PESERTA (NIS)", f"{tot_p} Siswa")
    with m2: st.metric("RATA-RATA NILAI KESELURUHAN", f"{avg_s:.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    target_nama_filter = sel_nama if sel_nama != "Semua Nama" else None

    # 1. Rata-rata Kelas
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>1. 📊 Rata-rata Kelas</div>", unsafe_allow_html=True)
    if "Kelas" in df_v.columns and score_col in df_v.columns:
        chart_df = df_v.groupby("Kelas")[score_col].mean().reset_index()
        chart_df.columns = ["Kelas", "Rata-rata"]
        if not chart_df.empty:
            bar_base = alt.Chart(chart_df).mark_bar(color="#fb7185", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Kelas:N", title="Kelas", sort="-y"),
                y=alt.Y("Rata-rata:Q", title="Nilai Rata-rata", scale=alt.Scale(domain=[0, 100])),
                tooltip=["Kelas", "Rata-rata"],
            )
            text_labels = bar_base.mark_text(align="center", baseline="bottom", dy=-6, color="#1e293b", fontWeight="bold").encode(text=alt.Text("Rata-rata:Q", format=".1f"))
            kkm_line = alt.Chart(pd.DataFrame({"y": [90]})).mark_rule(color="#e11d48", strokeWidth=2.5, strokeDash=[4, 4]).encode(y="y:Q")
            st.altair_chart((bar_base + text_labels + kkm_line).properties(height=320, background="transparent").configure_view(stroke=None), use_container_width=True)

    st.markdown("---")

    # 2. Kemampuan Akademik (Berdasarkan Sub Bab & Pos Test, tanpa JFT)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>2. 📚 Kemampuan Akademik</div>", unsafe_allow_html=True)
    
    sub_bab_col = next((c for c in df_v.columns if any(k in c.lower() for k in ["sub bab", "sub_bab", "materi"])), None)
    pos_test_col = next((c for c in df_v.columns if any(k in c.lower() for k in ["pos test", "post test", "nilai"])), None)

    acad_data = []
    if sub_bab_col and pos_test_col and not df_v.empty:
        temp_acad = df_v.copy()
        temp_acad = temp_acad[~temp_acad[sub_bab_col].astype(str).str.lower().str.contains("jft", na=False)]
        temp_acad[pos_test_col] = pd.to_numeric(temp_acad[pos_test_col], errors="coerce")
        acad_grouped = temp_acad.groupby(sub_bab_col)[pos_test_col].mean().reset_index()
        acad_data = [{"Aspek": str(row[sub_bab_col]), "Nilai": row[pos_test_col]} for _, row in acad_grouped.iterrows() if not pd.isna(row[pos_test_col])]

    if not acad_data:
        acad_data = [
            {"Aspek": "Kosakata", "Nilai": get_val_by_name(df_akademik, target_nama_filter, ["kosakata", "goi"])},
            {"Aspek": "Bunpo", "Nilai": get_val_by_name(df_akademik, target_nama_filter, ["bunpou", "tata bahasa"])},
            {"Aspek": "Kanji", "Nilai": get_val_by_name(df_akademik, target_nama_filter, ["kanji"])},
            {"Aspek": "Mendengar", "Nilai": get_val_by_name(df_akademik, target_nama_filter, ["mendengar", "choukai"])},
            {"Aspek": "Membaca", "Nilai": get_val_by_name(df_akademik, target_nama_filter, ["membaca", "dokkai"])}
        ]

    df_acad_plot = pd.DataFrame(acad_data)
    fig_radar_acad = px.line_polar(df_acad_plot, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100])
    fig_radar_acad.update_traces(fill="toself", line_color="#be185d", marker_color="#fb7185", fillcolor="rgba(190, 24, 93, 0.2)", mode="lines+markers+text", texttemplate="%{r:.1f}", textposition="top center")
    fig_radar_acad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_radar_acad, use_container_width=True)

    st.markdown("---")

    # 3. Attitude (Grafik Lingkaran/Pie Chart untuk data siswa berdasarkan NIS yang memperoleh nilai sikap A, B, C, D)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>3. 🌟 Attitude</div>", unsafe_allow_html=True)
    
    att_cols = [c for c in df_v.columns if any(k in c.lower() for k in ["disiplin", "sopan", "kebersihan", "5s", "kerjasama"])]
    if not att_cols:
        att_cols = [c for c in df_v.columns if any(k in c.lower() for k in ["attitude", "sikap"])]

    if att_cols and "NIS" in df_v.columns and not df_v.empty:
        # Hitung rata-rata skor sikap per NIS
        temp_att = df_v[["NIS"] + att_cols].copy()
        for col in att_cols:
            temp_att[col] = temp_att[col].apply(huruf_ke_angka)
        temp_att["AvgScore"] = temp_att[att_cols].mean(axis=1)
        
        # Agregasi per NIS unik
        nis_att_grade = temp_att.groupby("NIS")["AvgScore"].mean().reset_index()
        nis_att_grade["Grade"] = nis_att_grade["AvgScore"].apply(angka_ke_abjad)
        
        grade_counts = nis_att_grade["Grade"].value_counts().reset_index()
        grade_counts.columns = ["Grade", "Jumlah Siswa"]
        total_nis_att = grade_counts["Jumlah Siswa"].sum()
        
        all_grades = pd.DataFrame({"Grade": ["A", "B", "C", "D"]})
        grade_counts = pd.merge(all_grades, grade_counts, on="Grade", how="left").fillna(0)
        grade_counts["Persentase (%)"] = (grade_counts["Jumlah Siswa"] / (total_nis_att if total_nis_att > 0 else 1)) * 100
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        grades_list = [
            ("Grade A (Sangat Baik)", grade_counts[grade_counts["Grade"]=="A"]["Jumlah Siswa"].values[0], grade_counts[grade_counts["Grade"]=="A"]["Persentase (%)"].values[0], "#10b981"),
            ("Grade B (Baik)", grade_counts[grade_counts["Grade"]=="B"]["Jumlah Siswa"].values[0], grade_counts[grade_counts["Grade"]=="B"]["Persentase (%)"].values[0], "#3b82f6"),
            ("Grade C (Cukup)", grade_counts[grade_counts["Grade"]=="C"]["Jumlah Siswa"].values[0], grade_counts[grade_counts["Grade"]=="C"]["Persentase (%)"].values[0], "#f59e0b"),
            ("Grade D (Kurang)", grade_counts[grade_counts["Grade"]=="D"]["Jumlah Siswa"].values[0], grade_counts[grade_counts["Grade"]=="D"]["Persentase (%)"].values[0], "#ef4444"),
        ]
        
        for col_obj, (g_title, g_jml, g_pct, g_color) in zip([col_c1, col_c2, col_c3, col_c4], grades_list):
            with col_obj:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; border-top: 5px solid {g_color}; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;">
                    <div style="font-size: 13px; font-weight: 700; color: #64748b;">{g_title}</div>
                    <div style="font-size: 24px; font-weight: 900; color: {g_color}; margin: 5px 0;">{int(g_jml)} Siswa</div>
                    <div style="font-size: 12px; font-weight: 600; color: #475569;">({g_pct:.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig_att_pie = px.pie(grade_counts, names="Grade", values="Jumlah Siswa", hole=0.45, color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#ef4444"])
        fig_att_pie.update_traces(textinfo='percent+label', textfont_size=15, marker=dict(line=dict(color='#ffffff', width=2)))
        fig_att_pie.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)", legend=dict(font=dict(size=14)))
        st.plotly_chart(fig_att_pie, use_container_width=True)
    else:
        st.info("💡 Data Attitude atau kolom NIS belum tersedia.")

    st.markdown("---")

    # 4. Skill Siswa
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>4. 🛠️ Skill Siswa</div>", unsafe_allow_html=True)
    skill_data = [
        {"Aspek Skill": "Keselamatan Kerja", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["keselamatan"])},
        {"Aspek Skill": "Persiapan Kerja", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["persiapan"])},
        {"Aspek Skill": "Penggunaan Alat", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["alat", "penggunaan"])},
        {"Aspek Skill": "Teknik Kerja", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["teknik"])},
        {"Aspek Skill": "Kerja di Genba", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["genba"])},
        {"Aspek Skill": "Komunikasi", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["komunikasi"])},
        {"Aspek Skill": "Sikap Kerja", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["sikap"])},
        {"Aspek Skill": "5S & Kerapihan", "Nilai": get_val_by_name(df_skill, target_nama_filter, ["5s", "kerapihan"])}
    ]
    df_skill_summary = pd.DataFrame(skill_data)
    fig_skill_radar = px.line_polar(df_skill_summary, r="Nilai", theta="Aspek Skill", line_close=True, range_r=[0, 100])
    fig_skill_radar.update_traces(fill="toself", line_color="#0d9488", marker_color="#14b8a6", fillcolor="rgba(13, 148, 136, 0.2)", mode="lines+markers+text", texttemplate="%{r:.1f}", textposition="top center")
    fig_skill_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_skill_radar, use_container_width=True)

    st.markdown("---")

    # 5. Fisik Siswa
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>5. 🏃 Kemampuan Fisik Siswa</div>", unsafe_allow_html=True)
    fisik_data = [
        {"Item Tes Fisik": "Lari", "Rata-rata Nilai": get_val_by_name(df_fisik, target_nama_filter, ["lari"])},
        {"Item Tes Fisik": "Push Up", "Rata-rata Nilai": get_val_by_name(df_fisik, target_nama_filter, ["push"])},
        {"Item Tes Fisik": "Sit Up", "Rata-rata Nilai": get_val_by_name(df_fisik, target_nama_filter, ["sit"])},
        {"Item Tes Fisik": "Squat", "Rata-rata Nilai": get_val_by_name(df_fisik, target_nama_filter, ["squat"])},
        {"Item Tes Fisik": "Plank", "Rata-rata Nilai": get_val_by_name(df_fisik, target_nama_filter, ["plank"])}
    ]
    fisik_summary = pd.DataFrame(fisik_data)
    fig_fisik_bar = px.bar(fisik_summary, x="Item Tes Fisik", y="Rata-rata Nilai", text="Rata-rata Nilai", color="Rata-rata Nilai", color_continuous_scale="Purples")
    fig_fisik_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_fisik_bar.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_fisik_bar, use_container_width=True)

    st.markdown("---")

    # 6. Database Utama
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>6. 📂 Database Utama</div>", unsafe_allow_html=True)
    st.dataframe(df_v, use_container_width=True)

# ================= MENU 2: RAPORT SISWA =================
elif menu == "📄 Raport":
    st.markdown("<div class='main-heading'>RAPORT RESMI LPK YUTAKA</div>", unsafe_allow_html=True)
    
    target_raport = df_raport if not df_raport.empty and "Nama" in df_raport.columns else df_akademik
    if not target_raport.empty and "Nama" in target_raport.columns:
        c_date1, c_date2 = st.columns(2)
        with c_date1:
            start_date = st.date_input("Dari Tanggal", value=pd.to_datetime("2026-09-01"))
        with c_date2:
            end_date = st.date_input("Sampai Tanggal", value=pd.to_datetime("2026-09-30"))

        list_opsi_siswa = sorted([str(x) for x in target_raport["Nama"].dropna().unique() if str(x).strip() not in ["nan", ""]])
        pilih_nama = st.selectbox("Cari & Pilih Nama Siswa:", list_opsi_siswa)
        
        kelas_val = "N5L1"
        row_match = target_raport[target_raport["Nama"].astype(str) == pilih_nama]
        if not row_match.empty and "Kelas" in row_match.columns:
            kelas_val = str(row_match["Kelas"].iloc[0])

        kesimpulan = st.selectbox("Status Kenaikan / Kelulusan:", ["NAIK KELAS", "TINGGAL KELAS", "LULUS"])
        
        if st.button("👁️ TAMPILKAN RAPORT LENGKAP & GRAFIK", use_container_width=True):
            st.markdown("---")
            val_huruf = get_val_by_name(df_akademik, pilih_nama, ["kosakata", "goi", "huruf"])
            val_tata = get_val_by_name(df_akademik, pilih_nama, ["bunpou", "tata bahasa"])
            val_baca = get_val_by_name(df_akademik, pilih_nama, ["membaca", "dokkai"])
            val_dengar = get_val_by_name(df_akademik, pilih_nama, ["mendengar", "choukai"])
            val_bicara = get_val_by_name(df_akademik, pilih_nama, ["berbicara", "kaiwa"])

            locked_akad_subs = [
                ("Kosakata & Huruf", val_huruf),
                ("Tata Bahasa (文法)", val_tata),
                ("Membaca (読解)", val_baca),
                ("Mendengar (聴解)", val_dengar),
                ("Berbicara (会話)", val_bicara)
            ]

            rows_akad = ""
            tot_akad = 0
            for idx, (sub_name, vnum) in enumerate(locked_akad_subs, 1):
                tot_akad += vnum
                huruf = angka_ke_abjad(vnum)
                ket = get_clean_keterangan(sub_name.split('(')[0].strip(), vnum)
                rows_akad += f"""
                <tr>
                    <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{idx}</td>
                    <td style="border: 1px solid #cbd5e1; padding: 5px;">{sub_name}</td>
                    <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{vnum:.1f}</td>
                    <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;"><b>{huruf}</b></td>
                    <td style="border: 1px solid #cbd5e1; padding: 5px; font-size: 11px;">{ket}</td>
                </tr>
                """
            avg_akad = tot_akad / 5

            st.markdown(f"### 📋 Hasil Evaluasi Raport: **{pilih_nama}** | Kelas: {kelas_val} (Periode: {start_date} s/d {end_date})")
            st.components.v1.html(f"""
            <table style="width: 100%; border-collapse: collapse; font-size: 13px; font-family: sans-serif;">
                <thead>
                    <tr style="background: #be185d; color: white;">
                        <th style="padding: 8px; border: 1px solid #cbd5e1;">No</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">Mata Pelajaran</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1;">Nilai</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1;">Predikat</th>
                        <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">Keterangan</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_akad}
                    <tr style="background: #f1f5f9; font-weight: bold;">
                        <td colspan="2" style="text-align: right; border: 1px solid #cbd5e1; padding: 8px;">RATA-RATA:</td>
                        <td style="text-align: center; border: 1px solid #cbd5e1; padding: 8px;">{avg_akad:.1f}</td>
                        <td style="text-align: center; border: 1px solid #cbd5e1; padding: 8px;"><b>{angka_ke_abjad(avg_akad)}</b></td>
                        <td style="border: 1px solid #cbd5e1; padding: 8px;"></td>
                    </tr>
                </tbody>
            </table>
            """, height=260)

            c_graf1, c_graf2 = st.columns(2)
            with c_graf1:
                df_graf_akad = pd.DataFrame([
                    {"Aspek": "Kosakata", "Nilai": val_huruf},
                    {"Aspek": "Tata Bahasa", "Nilai": val_tata},
                    {"Aspek": "Membaca", "Nilai": val_baca},
                    {"Aspek": "Mendengar", "Nilai": val_dengar},
                    {"Aspek": "Berbicara", "Nilai": val_bicara},
                ])
                fig_r_akad = px.line_polar(df_graf_akad, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100])
                fig_r_akad.update_traces(fill="toself", line_color="#be185d", marker_color="#fb7185", fillcolor="rgba(190, 24, 93, 0.2)", mode="lines+markers+text", texttemplate="%{r:.1f}", textposition="top center")
                fig_r_akad.update_layout(title="Grafik Akademik", height=320, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_r_akad, use_container_width=True)

            with c_graf2:
                df_graf_fisik = pd.DataFrame([
                    {"Item Fisik": "Lari", "Skor": get_val_by_name(df_fisik, pilih_nama, ["lari"])},
                    {"Item Fisik": "Push Up", "Skor": get_val_by_name(df_fisik, pilih_nama, ["push"])},
                    {"Item Fisik": "Sit Up", "Skor": get_val_by_name(df_fisik, pilih_nama, ["sit"])},
                    {"Item Fisik": "Squat", "Skor": get_val_by_name(df_fisik, pilih_nama, ["squat"])},
                    {"Item Fisik": "Plank", "Skor": get_val_by_name(df_fisik, pilih_nama, ["plank"])},
                ])
                fig_b_fisik = px.bar(df_graf_fisik, x="Item Fisik", y="Skor", text="Skor", color="Skor", color_continuous_scale="Teal")
                fig_b_fisik.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_b_fisik.update_layout(title="Grafik Fisik", height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_b_fisik, use_container_width=True)

            st.markdown(f"""
            <div style="font-size: 16px; font-weight: bold; color: #059669; padding: 15px; background: #ecfdf5; border-radius: 8px; border-left: 5px solid #10b981; margin-top: 10px; text-align: center;">
                STATUS KELULUSAN / KENAIKAN KELAS: {kesimpulan}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Data raport siswa belum tersedia di spreadsheet.")

# ================= MENU 3: JFT SISWA =================
elif menu == "🎯 JFT Siswa":
    st.markdown("<div class='main-heading'>DATA NILAI JFT SISWA</div>", unsafe_allow_html=True)
    
    if not df_jft.empty:
        bulan_col = next((c for c in df_jft.columns if any(k in c.lower() for k in ["bulan", "month"])), None)
        tahun_col = next((c for c in df_jft.columns if any(k in c.lower() for k in ["tahun", "year"])), None)
        
        st.markdown("#### 🔍 Filter JFT Siswa (Bulan & Tahun)")
        f_j1, f_j2 = st.columns(2)
        
        list_bulan = sorted([str(x) for x in df_jft[bulan_col].dropna().unique() if str(x).strip() not in ["nan", ""]]) if bulan_col else ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        list_tahun = sorted([str(x) for x in df_jft[tahun_col].dropna().unique() if str(x).strip() not in ["nan", ""]]) if tahun_col else ["2025", "2026"]

        with f_j1: pilih_bln = st.selectbox("Pilih Bulan:", ["Semua Bulan"] + list_bulan)
        with f_j2: pilih_thn = st.selectbox("Pilih Tahun:", ["Semua Tahun"] + list_tahun)

        df_jft_view = df_jft.copy()
        if pilih_bln != "Semua Bulan" and bulan_col: 
            df_jft_view = df_jft_view[df_jft_view[bulan_col].astype(str) == pilih_bln]
        if pilih_thn != "Semua Tahun" and tahun_col: 
            df_jft_view = df_jft_view[df_jft_view[tahun_col].astype(str) == pilih_thn]

        if bulan_col and not df_jft.empty:
            pie_data = df_jft_view[bulan_col].astype(str).value_counts().reset_index()
            pie_data.columns = ["Bulan", "Jumlah"]
            
            fig_pie = px.pie(pie_data, names="Bulan", values="Jumlah", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_traces(textinfo='percent+label', textfont_size=14)
            fig_pie.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>📂 Database JFT Siswa</div>", unsafe_allow_html=True)
        st.dataframe(df_jft_view, use_container_width=True)
    else:
        st.warning("⚠️ Data JFT Siswa belum tersedia.")

# ================= MENU 4: UPLOAD & UNDUH =================
elif menu == "📤 Upload/Unduh":
    st.markdown("<div class='main-heading'>DOWNLOAD DATA REALTIME</div>", unsafe_allow_html=True)
    if not df_akademik.empty:
        st.download_button(
            label="📥 DOWNLOAD REKAP LENGKAP (EXCEL)",
            data=to_excel_bytes(df_akademik),
            file_name="laporan_lpk_yutaka_realtime.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    else:
        st.warning("⚠️ Tidak ada data untuk diunduh.")