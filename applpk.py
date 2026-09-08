import io
import os
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Pastikan matplotlib menggunakan backend 'Agg'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Import ReportLab untuk Export PDF 2 Lembar Resmi
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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

# LINK CSV GOOGLE SHEETS UTAMA YANG AMAN DAN VALID
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTY21UPg0GRdL5tHy-mPc-xPR7ZHdNz3o_qFnl7QVA5mMC0-wQJOb55niQe1_M1d6kT44wKXsFDEzVw/pub?output=csv"

@st.cache_data(ttl=30)
def load_data_from_csv():
  try:
    df_loaded = pd.read_csv(CSV_URL)
    
    df_s2 = df_loaded.copy()
    df_skill = df_loaded.copy()
    df_fisik = df_loaded.copy()

    nis_col_found = None
    for col in df_loaded.columns:
      c_low = col.strip().lower()
      if c_low in ["nis", "nis siswa", "id siswa"]:
        nis_col_found = col
        break
    
    if nis_col_found and nis_col_found != "NIS":
      df_loaded.rename(columns={nis_col_found: "NIS"}, inplace=True)
    
    if "NIS" in df_loaded.columns:
      df_loaded["NIS"] = df_loaded["NIS"].astype(str).str.strip()
    else:
      df_loaded["NIS"] = "-"

    skip_cols = [
        "Tanggal", "Kelas", "NIS", "NIS Siswa", "Nama", "Nama Siswa", "Jenis Kelamin", "Program", 
        "Bab", "Sub bab", "Sensei", "Keterangan", "Disiplin", 
        "Sopan santun", "Kebersihan (5S)", "Kerjasama",
        "Keselamatan Kerja", "Persiapan Kerja", "Penggunaan ALat", "Teknik Kerja", "Kerja di Genba", "Komunikasi dan Kerja Tim", "Sikap Kerja", "5S & Kerapihan",
        "Lari", "Push Up", "Sit Up", "Squat", "Plank", "Farmer Walk", "Angkat Beban"
    ]
    for target_df in [df_loaded, df_s2, df_skill, df_fisik]:
      if not target_df.empty:
        for col in target_df.columns:
          if col not in skip_cols:
            target_df[col] = pd.to_numeric(target_df[col], errors="coerce")

    return df_loaded, df_s2, df_skill, df_fisik
  except Exception as e:
    st.warning(f"⚠️ Belum terhubung ke Link CSV Google Sheets. Detail: {e}")
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df, df_sheet2, df_skill_sheet, df_fisik_sheet = load_data_from_csv()

def to_excel_bytes(dataframe):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    dataframe.to_excel(writer, index=False, sheet_name="Data_LPK")
  return output.getvalue()

def huruf_ke_angka(val):
  if pd.isna(val) or str(val).strip() == "":
    return 80.0
  val_str = str(val).strip().upper()
  if val_str == "A":
    return 85.0
  elif val_str == "B":
    return 75.0
  elif val_str == "C":
    return 65.0
  elif val_str == "D":
    return 50.0
  else:
    try:
      return float(val_str)
    except:
      return 80.0

def angka_ke_abjad(val):
  if pd.isna(val) or val == 0:
    return "D"
  if val >= 85:
    return "A"
  elif val >= 70:
    return "B"
  elif val >= 55:
    return "C"
  else:
    return "D"

def get_catatan_perilaku_from_sheet2(aspect_title, predikat, df_s2):
  p = str(predikat).strip().upper()
  clean_name = aspect_title.split('(')[0].strip().lower()
  
  bank_catatan = {
      "kedisiplinan": {
          "A": "Umumnya disiplin dan mematuhi peraturan, meskipun terkadang masih perlu diingatkan.",
          "B": "Memiliki kedisiplinan yang cukup, namun konsistensi masih perlu ditingkatkan.",
          "C": "Sering terlambat atau kurang mematuhi peraturan sehingga memerlukan perhatian dan arahan.",
          "D": "Tidak disiplin dan sering melanggar peraturan sehingga memerlukan pembinaan khusus."
      },
      "sopan": {
          "A": "Bersikap sopan dan menghormati orang lain dengan baik meskipun terkadang masih perlu diingatkan.",
          "B": "Memiliki sikap sopan yang cukup baik namun konsistensi masih perlu ditingkatkan.",
          "C": "Kadang kurang memperhatikan sopan santun dan etika dalam berperilaku.",
          "D": "Sering menunjukkan sikap yang kurang sopan dan membutuhkan pembinaan khusus."
      },
      "kebersihan": {
          "A": "Mampu menjaga kebersihan dengan baik, meskipun terkadang masih perlu diingatkan.",
          "B": "Menjaga kebersihan pada tingkat dasar, namun kepedulian dan konsistensi masih perlu ditingkatkan.",
          "C": "Kurang menjaga kebersihan sehingga memerlukan perhatian dan arahan.",
          "D": "Tidak menjaga kebersihan diri maupun lingkungan dan memerlukan pembinaan khusus."
      },
      "kerjasama": {
          "A": "Dapat bekerja sama dengan baik bersama teman atau kelompok.",
          "B": "Kerja sama cukup baik namun masih kurang aktif.",
          "C": "Kurang aktif dalam kerja kelompok.",
          "D": "Sulit bekerja sama dengan orang lain."
      }
  }

  for key in bank_catatan:
    if key in clean_name:
      return bank_catatan[key].get(p, f"Memiliki {aspect_title} dengan predikat {p}.")
  
  return f"Memiliki {aspect_title} yang baik dan patuh pada aturan."

def get_clean_keterangan(subtest, val):
  if val >= 85:
    return f"Sangat baik dalam penguasaan materi {subtest} serta menunjukkan performa tingkat tinggi."
  elif val >= 70:
    return f"Memahami materi {subtest} dengan baik serta mampu mengikuti proses pembelajaran secara aktif."
  elif val >= 50:
    return f"Memiliki pemahaman dasar pada {subtest}, namun memerlukan peningkatan konsistensi latihan."
  else:
    return f"Memerlukan perhatian khusus dan bimbingan intensif pada materi {subtest}."

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
    """,
      unsafe_allow_html=True,
  )
  st.markdown(
      "<hr style='border-color: rgba(244, 114, 182, 0.3); margin: 10px 0;'>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #fda4af; font-size: 10px; font-weight: 700; padding-left:"
      " 5px; margin-bottom: 6px; letter-spacing: 1px;'>NAVIGASI SISTEM</p>",
      unsafe_allow_html=True,
  )

  menus = [
      ("📊 Command Dashboard", "📊 Dashboard"),
      ("✍️ Input Nilai", "✍️ Input"),
      ("📄 Raport Siswa", "📄 Raport"),
      ("📂 Database Peserta", "📂 Database"),
      ("📤 Upload & Unduh", "📤 Upload/Unduh"),
  ]

  for label, menu_key in menus:
    if st.button(label, key=f"btn_{menu_key}", use_container_width=True):
      st.session_state.active_menu = menu_key
      st.rerun()

  if st.button("🔄 Refresh Data Google Sheets", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='color: #cbd5e1; font-size: 9px; text-align: center;'>SAKURA"
      " REALTIME CSV // v3.2</p>",
      unsafe_allow_html=True,
  )

menu = st.session_state.active_menu

def get_universal_val(df_source, keywords, score_col="Pos Test"):
    if df_source.empty: return 0.0
    if "Sub bab" in df_source.columns:
        mask = False
        sub_col_str = df_source["Sub bab"].astype(str)
        for k in keywords:
            mask = mask | sub_col_str.str.contains(k, case=False, na=False)
        sub_df = df_source[mask]
        if not sub_df.empty and score_col in sub_df.columns and not sub_df[score_col].dropna().empty:
            return sub_df[score_col].mean()
            
    for col in df_source.columns:
        if any(k.lower() in col.lower() for k in keywords) and not df_source[col].dropna().empty:
            numeric_series = pd.to_numeric(df_source[col], errors="coerce")
            v = huruf_ke_angka(numeric_series.dropna().iloc[-1] if not numeric_series.dropna().empty else df_source[col].dropna().iloc[-1])
            if not pd.isna(v): return v
    return 0.0

# ================= MENU 1: DASHBOARD =================
if menu == "📊 Dashboard":
  st.markdown("<div class='main-heading'>LAPORAN PERKEMBANGAN PENDIDIKAN & TRAINING</div>", unsafe_allow_html=True)
  st.markdown("<div class='sub-heading'>SAKURA SYSTEM REALTIME MONITORING — LPK YUTAKA</div>", unsafe_allow_html=True)

  if df.empty or "Nama" not in df.columns or df["Nama"].dropna().empty:
    st.warning("⚠️ Data Google Sheets belum terbaca.")
  else:
    for col_chk in ["Kelas", "Bab", "Sub bab", "Sensei", "Tanggal", "NIS"]:
      if col_chk not in df.columns:
        df[col_chk] = "Semua"
    df_ui = df.fillna("Semua")

    df["Parsed_Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    min_date = df["Parsed_Tanggal"].min().date() if not df["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-01-01").date()
    max_date = df["Parsed_Tanggal"].max().date() if not df["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-12-31").date()

    st.markdown("#### 🔍 Filter Data Siswa")
    
    f1, f2, f3 = st.columns(3)
    with f1:
      sel_kelas = st.selectbox("Kelas", ["Semua Kelas"] + sorted(df_ui["Kelas"].astype(str).unique().tolist()))
    
    if sel_kelas != "Semua Kelas":
      list_nis_filtered = sorted(df_ui[df_ui["Kelas"].astype(str) == sel_kelas]["NIS"].astype(str).unique().tolist())
    else:
      list_nis_filtered = sorted(df_ui["NIS"].astype(str).unique().tolist())

    with f2:
      sel_nis = st.selectbox("NIS Siswa", ["Semua NIS"] + list_nis_filtered)
    with f3:
      sel_bab = st.selectbox("Bab", ["Semua Bab"] + sorted(df_ui["Bab"].astype(str).unique().tolist()))

    f4, f5 = st.columns(2)
    with f4:
      sel_sensei = st.selectbox("Sensei", ["Semua Sensei"] + sorted(df_ui["Sensei"].astype(str).unique().tolist()))
    with f5:
      ignore_date = st.checkbox("Tampilkan Semua Tanggal (Abaikan Rentang Tanggal)", value=True)

    t1, t2 = st.columns(2)
    with t1:
      start_date = st.date_input("Dari Tanggal", min_date)
    with t2:
      end_date = st.date_input("Sampai Tanggal", max_date)

    df_v = df.copy()
    if sel_kelas != "Semua Kelas":
      df_v = df_v[df_v["Kelas"].astype(str) == sel_kelas]
    if sel_nis != "Semua NIS":
      df_v = df_v[df_v["NIS"].astype(str) == sel_nis]
    if sel_bab != "Semua Bab":
      df_v = df_v[df_v["Bab"].astype(str) == sel_bab]
    if sel_sensei != "Semua Sensei":
      df_v = df_v[df_v["Sensei"].astype(str) == sel_sensei]

    if not ignore_date:
      df_v["Parsed_Tanggal"] = pd.to_datetime(df_v["Parsed_Tanggal"], errors="coerce")
      df_v = df_v[
          (df_v["Parsed_Tanggal"].dt.date >= start_date) & 
          (df_v["Parsed_Tanggal"].dt.date <= end_date)
      ]

    numeric_cols = [c for c in df_v.columns if c not in ["Tanggal", "Kelas", "NIS", "NIS Siswa", "Nama", "Jenis Kelamin", "Program", "Bab", "Sub bab", "Sensei", "Keterangan"]]
    score_col = "Pos Test" if "Pos Test" in df_v.columns and df_v["Pos Test"].dropna().count() > 0 else (numeric_cols[0] if numeric_cols else "Rata-rata nilai")
    if score_col not in df_v.columns:
      df_v["Nilai_Acu"] = 0
      score_col = "Nilai_Acu"

    tot_p = df_v["NIS"].nunique() if "NIS" in df_v.columns else len(df_v)
    avg_s = df_v[score_col].mean() if not df_v[score_col].dropna().empty else 0

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
      st.metric("TOTAL PESERTA", f"{tot_p} Siswa")
    with m2:
      st.metric("RATA-RATA NILAI KESELURUHAN", f"{avg_s:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # URUTAN 1: RATA-RATA KELAS (DIPERBAIKI AGAR SEMUA KELAS MUNCUL TANPA TERLEWAT)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>1. 📊 Rata-rata Kelas (Target KKM: 90)</div>", unsafe_allow_html=True)
    
    df_chart_clean = df_v.copy()
    if "Kelas" in df_chart_clean.columns:
        df_chart_clean["Kelas"] = df_chart_clean["Kelas"].astype(str).str.strip()
        df_chart_clean = df_chart_clean[~df_chart_clean["Kelas"].isin(["nan", "NaN", "Semua", "None", ""])]

    chart_df = df_chart_clean.groupby("Kelas")[score_col].mean().reset_index()
    chart_df.columns = ["Kelas", "Rata-rata"]

    if not chart_df.empty and not chart_df["Rata-rata"].isna().all():
      bar_base = alt.Chart(chart_df).mark_bar(color="#fb7185", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
          x=alt.X("Kelas:N", title="Kelas", sort="-y", axis=alt.Axis(labelAngle=0, labelColor="#1e293b", labelFontSize=12, labelFontWeight="bold", titleColor="#1e293b")),
          y=alt.Y("Rata-rata:Q", title="Nilai Rata-rata", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(labelColor="#1e293b", titleColor="#1e293b")),
          tooltip=["Kelas", "Rata-rata"],
      )
      text_labels = bar_base.mark_text(align="center", baseline="bottom", dy=-6, color="#1e293b", fontWeight="bold", fontSize=12).encode(text=alt.Text("Rata-rata:Q", format=".1f"))
      kkm_line = alt.Chart(pd.DataFrame({"y": [90]})).mark_rule(color="#e11d48", strokeWidth=2.5, strokeDash=[4, 4]).encode(y="y:Q")
      
      st.altair_chart((bar_base + text_labels + kkm_line).properties(height=320, background="transparent").configure_view(stroke=None), use_container_width=True)
    else:
      st.info("Data nilai untuk rekapitulasi kelas belum tersedia pada filter ini.")

    st.markdown("---")

    # URUTAN 2: KEMAMPUAN AKADEMIK SISWA
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>2. 📚 Kemampuan Akademik Siswa (Grafik Radar)</div>", unsafe_allow_html=True)
    
    akad_data = []
    for title, kw in [("Huruf & Kosakata", ["huruf", "kosakata", "kotoba", "kanji", "文字", "漢字", "言葉"]), 
                      ("Tata Bahasa", ["tata bahasa", "bunpou", "文法"]), 
                      ("Membaca", ["membaca", "dokkai", "読解"]), 
                      ("Mendengar", ["mendengar", "choukai", "聴解"]), 
                      ("Berbicara", ["berbicara", "kaiwa", "会話"])]:
        val = get_universal_val(df_v, kw, score_col)
        if val > 0:
            akad_data.append({"Aspek": title, "Nilai": val})

    df_acad_plot = pd.DataFrame(akad_data)
    if not df_acad_plot.empty:
      fig_radar_dash = px.line_polar(df_acad_plot, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100])
      fig_radar_dash.update_traces(fill="toself", line_color="#be185d", marker_color="#fb7185", fillcolor="rgba(190, 24, 93, 0.2)", text=df_acad_plot["Nilai"].apply(lambda x: f"{x:.1f}"), mode="lines+markers+text")
      fig_radar_dash.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
      st.plotly_chart(fig_radar_dash, use_container_width=True)
    else:
      st.info("Belum ada data sub tes akademik yang tercatat.")

    st.markdown("---")

    # URUTAN 3: ATTITUDE
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>3. 🌟 Attitude / Sikap Siswa</div>", unsafe_allow_html=True)
    
    if "Nama" in df_v.columns:
      student_att_grades = []
      for name_siswa, group in df_v.groupby("Nama"):
        grades_list = []
        att_keys = ["disiplin", "sopan", "kebersihan", "5s", "kerjasama"]
        mask_att = False
        sub_col_str = group["Sub bab"].astype(str)
        for k in att_keys:
            mask_att = mask_att | sub_col_str.str.contains(k, case=False, na=False)
        sub_df = group[mask_att]
        
        for val in sub_df[score_col].dropna():
            grades_list.append(angka_ke_abjad(float(val)))
            
        for col in ["Disiplin", "Sopan santun", "Kebersihan (5S)", "Kerjasama"]:
             if col in group.columns:
                 for val in group[col].dropna():
                     if str(val).strip().upper() in ["A","B","C","D"]:
                         grades_list.append(str(val).strip().upper())
                     else:
                         grades_list.append(angka_ke_abjad(huruf_ke_angka(val)))
                         
        if grades_list:
          from collections import Counter
          c_counts = Counter(grades_list)
          dominant_grade = c_counts.most_common(1)[0][0]
          student_att_grades.append(dominant_grade)

      if student_att_grades:
        att_series = pd.Series(student_att_grades).value_counts().reindex(["A", "B", "C", "D"], fill_value=0).reset_index()
        att_series.columns = ["Predikat", "Jumlah Siswa"]
        att_series["Persentase"] = (att_series["Jumlah Siswa"] / att_series["Jumlah Siswa"].sum()) * 100 if att_series["Jumlah Siswa"].sum() > 0 else 0

        c_pie1, c_pie2 = st.columns([1.5, 1])
        with c_pie1:
          fig_pie = px.pie(att_series, names="Predikat", values="Jumlah Siswa", hole=0.4, color="Predikat", color_discrete_map={"A": "#2563eb", "B": "#10b981", "C": "#d97706", "D": "#dc2626"})
          fig_pie.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
          st.plotly_chart(fig_pie, use_container_width=True)
        with c_pie2:
          st.markdown("##### Distribusi Predikat:")
          for _, row in att_series.iterrows():
            st.markdown(f"- **Predikat {row['Predikat']}**: **{row['Jumlah Siswa']} data** ({row['Persentase']:.1f}%)")
      else:
        st.info("Belum ada data nilai predikat sikap per siswa yang tercatat.")
    else:
      st.info("Kolom nama siswa belum terdeteksi.")

    st.markdown("---")

    # URUTAN 4: SKILL SISWA (8 ASPEK LENGKAP)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>4. 🛠️ Skill Siswa (Grafik Radar - 8 Aspek Lengkap)</div>", unsafe_allow_html=True)
    
    skill_data = []
    skill_cols_mapping = [
        ("Keselamatan Kerja", ["Keselamatan Kerja", "keselamatan"]),
        ("Persiapan Kerja", ["Persiapan Kerja", "persiapan"]),
        ("Penggunaan Alat", ["Penggunaan ALat", "Penggunaan Alat", "penggunaan"]),
        ("Teknik Kerja", ["Teknik Kerja", "teknik"]),
        ("Kerja di Genba", ["Kerja di Genba", "genba"]),
        ("Komunikasi dan Kerja Tim", ["Komunikasi dan Kerja Tim", "Komunikasi tim", "komunikasi"]),
        ("Sikap Kerja", ["Sikap Kerja", "sikap kerja"]),
        ("5S & Kerapihan", ["5S & Kerapihan", "5s", "kerapihan"])
    ]
    
    target_skill_df = df_skill_sheet if not df_skill_sheet.empty else df_v
    for title, kws in skill_cols_mapping:
      val_mean = 0.0
      for col in target_skill_df.columns:
        if any(kw.lower() in col.lower() for kw in kws):
          numeric_series = pd.to_numeric(target_skill_df[col], errors="coerce")
          val_mean = numeric_series.dropna().mean()
          break
      if pd.isna(val_mean): val_mean = 0.0
      if val_mean == 0:
        val_mean = get_universal_val(target_skill_df, kws, score_col)
      if val_mean == 0:
        val_mean = 75.0

      skill_data.append({"Aspek Skill": title, "Nilai": val_mean})

    df_skill_summary = pd.DataFrame(skill_data)
    if not df_skill_summary.empty:
      fig_skill_radar = px.line_polar(df_skill_summary, r="Nilai", theta="Aspek Skill", line_close=True, range_r=[0, 100])
      fig_skill_radar.update_traces(fill="toself", line_color="#0d9488", marker_color="#14b8a6", fillcolor="rgba(13, 148, 136, 0.2)", text=df_skill_summary["Nilai"].apply(lambda x: f"{x:.1f}"), mode="lines+markers+text")
      fig_skill_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
      st.plotly_chart(fig_skill_radar, use_container_width=True)
    else:
      st.info("Belum ada data nilai pada aspek skill yang tercatat.")

    st.markdown("---")

    # URUTAN 5: KEMAMPUAN FISIK SISWA
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>5. 🏃 Kemampuan Fisik Siswa (Standar Target & Grafik Batang)</div>", unsafe_allow_html=True)
    
    fisik_data = []
    target_fisik_df = df_fisik_sheet if not df_fisik_sheet.empty else df_v
    
    fisik_cols_mapping = [
        ("Lari", ["lari", "3km", "1.5km"]),
        ("Push Up", ["push up", "pushup", "push"]),
        ("Sit Up", ["sit up", "situp", "sit"]),
        ("Squat", ["squat"]),
        ("Plank", ["plank"]),
        ("Farmer Walk", ["farmer walk", "farmer"]),
        ("Angkat Beban", ["angkat beban", "beban"])
    ]
    
    for title, kws in fisik_cols_mapping:
      val_mean = 0.0
      for col in target_fisik_df.columns:
        if any(kw.lower() in col.lower() for kw in kws):
          numeric_series = pd.to_numeric(target_fisik_df[col], errors="coerce")
          val_mean = numeric_series.dropna().mean()
          break
      if pd.isna(val_mean): val_mean = 0.0
      if val_mean == 0:
        val_mean = get_universal_val(target_fisik_df, kws, score_col)
      if val_mean == 0:
        val_mean = 75.0
        
      fisik_data.append({"Item Tes Fisik": title, "Rata-rata Nilai": val_mean})
        
    fisik_summary = pd.DataFrame(fisik_data)
    
    if not fisik_summary.empty:
      fig_fisik_bar = px.bar(fisik_summary, x="Item Tes Fisik", y="Rata-rata Nilai", text="Rata-rata Nilai", color="Rata-rata Nilai", color_continuous_scale="Purples", range_y=[0, 105])
      fig_fisik_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
      fig_fisik_bar.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-15)
      st.plotly_chart(fig_fisik_bar, use_container_width=True)
    else:
      st.info("Data rekapitulasi tes fisik belum tersedia.")

    st.markdown("---")

    # 6. REKAPAN NILAI BERDASARKAN FILTER
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>6. 📋 Rekapan Nilai Berdasarkan Filter Aktif</div>", unsafe_allow_html=True)
    if not df_v.empty:
      st.dataframe(df_v, use_container_width=True)
    else:
      st.info("Tidak ada data yang sesuai dengan filter yang dipilih.")

# ================= MENU 2: INPUT NILAI =================
elif menu == "✍️ Input":
  st.markdown("<div class='main-heading'>FORM INPUT NILAI & KOMPETENSI</div>", unsafe_allow_html=True)
  st.info("💡 **Informasi**: Karena menggunakan mode Publikasi CSV Link, Anda dapat langsung menginput data baru secara *realtime* melalui tabel Google Spreadsheet Anda di browser. Setelah diinput di Google Sheets, klik tombol **'Refresh Data Google Sheets'** di sidebar sebelah kiri.")

# ================= MENU 3: RAPORT SISWA =================
elif menu == "📄 Raport":
  st.markdown("<div class='main-heading'>RAPORT RESMI LPK YUTAKA (評価報告書 & 体力評価)</div>", unsafe_allow_html=True)

  if df.empty or "Nama" not in df.columns or df["Nama"].dropna().empty:
    st.info("Database Google Sheets masih kosong.")
  else:
    df_peserta_unique = df[["Nama", "NIS"]].dropna(subset=["Nama"]).drop_duplicates()
    list_opsi_siswa = [f"{row['Nama']} (NIS: {row['NIS']})" for _, row in df_peserta_unique.iterrows()]
    
    pilih_opsi = st.selectbox("Pilih Peserta (Berdasarkan Nama & NIS):", list_opsi_siswa)
    pilih_nama = pilih_opsi.split(" (NIS:")[0]
    pilih_nis = pilih_opsi.split(" (NIS:")[1].replace(")", "").strip()

    df_siswa = df[(df["Nama"].astype(str) == pilih_nama) & (df["NIS"].astype(str) == pilih_nis)]
    if df_siswa.empty:
      df_siswa = df[df["Nama"].astype(str) == pilih_nama]

    if not df_siswa.empty:
      latest_data = df_siswa.iloc[-1]
      nis_val = pilih_nis if pilih_nis and pilih_nis != "-" else str(latest_data.get("NIS", "-"))
      kelas_val = str(latest_data.get("Kelas", "-"))
      
      if "(" in kelas_val:
        kelas_val = kelas_val.split("(")[0].strip()

      jk_raw = str(latest_data.get("Jenis Kelamin", "Laki-laki")).strip()
      jk_val = jk_raw
      program_val = str(latest_data.get("Program", "Reguler"))

      df_siswa["Parsed_Tanggal"] = pd.to_datetime(df_siswa["Tanggal"], errors="coerce")
      min_date_s = df_siswa["Parsed_Tanggal"].min().date() if not df_siswa["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-07-13").date()
      max_date_s = df_siswa["Parsed_Tanggal"].max().date() if not df_siswa["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-08-05").date()

      with st.form("form_raport_official"):
        st.markdown(f"#### 🛠️ Input Periode, Kehadiran & Catatan Sensei (NIS: {nis_val})")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
          start_p = st.date_input("Periode Dari Tanggal", min_date_s)
        with c_p2:
          end_p = st.date_input("Periode Sampai Tanggal", max_date_s)

        c1, c2, c3 = st.columns(3)
        with c1:
          hadir_val = st.number_input("Hadir (Hari)", 0, 30, 17)
        with c2:
          izin_val = st.number_input("Izin/Sakit (Hari)", 0, 30, 1)
        with c3:
          alpa_val = st.number_input("Alpa (Hari)", 0, 30, 0)

        catatan_umum = st.text_area("Catatan Umum Sensei (Akademik):", value=f"Peserta {pilih_nama} (NIS: {nis_val}) memiliki kemampuan dan pemahaman yang baik.")
        catatan_fisik = st.text_area("Catatan Saran Fisik:", value="Memiliki kemampuan fisik yang cukup baik dengan konsistensi latihan yang perlu ditingkatkan.")
        kesimpulan = st.selectbox("Kesimpulan Kenaikan", ["NAIK KELAS", "TINGGAL KELAS"])
        show_preview = st.form_submit_button("👁️ TAMPILKAN RAPORT LENGKAP RESMI", use_container_width=True)

      if show_preview:
        st.markdown("---")
        
        df_per = df_siswa[(df_siswa["Parsed_Tanggal"].dt.date >= start_p) & (df_siswa["Parsed_Tanggal"].dt.date <= end_p)]
        if df_per.empty:
          df_per = df_siswa

        def get_akad_val(keywords):
            val = get_universal_val(df_per, keywords)
            if val == 0: val = get_universal_val(df_siswa, keywords)
            return val

        locked_akad_subs = [
            ("Huruf & Kosakata", get_akad_val(["huruf", "kosakata", "kotoba", "kanji", "文字", "漢字", "言葉"])),
            ("Tata Bahasa (文法)", get_akad_val(["tata bahasa", "bunpou", "文法"])),
            ("Membaca (読解)", get_akad_val(["membaca", "dokkai", "読解"])),
            ("Mendengar (聴解)", get_akad_val(["mendengar", "choukai", "聴解"])),
            ("Berbicara (会話)", get_akad_val(["berbicara", "kaiwa", "会話"]))
        ]

        list_sikap_config = [
            {"title": "Disiplin", "kw": ["disiplin"]},
            {"title": "Sopan santun", "kw": ["sopan"]},
            {"title": "Kebersihan (5S)", "kw": ["kebersihan", "5s"]},
            {"title": "Kerjasama", "kw": ["kerjasama"]}
        ]

        is_female = jk_raw.lower().startswith("p") or jk_raw.lower() == "perempuan"
        if is_female:
          list_fisik_cols = [
              ("LARI (1,5KM 15MENIT)", ["1,5", "1.5", "lari"]),
              ("PUSH UP (40X 1MENIT)", ["push up", "pushup"]),
              ("SIT UP (40X 1MENIT)", ["sit up", "situp"]),
              ("SQUAT (45X 1MENIT)", ["squat"]),
              ("PLANK (4MENIT)", ["plank"]),
              ("FARMER WALK (8kg)", ["farmer"]),
              ("ANGKAT BEBAN (10kg)", ["beban", "angkat beban"])
          ]
        else:
          list_fisik_cols = [
              ("LARI (3KM 15MENIT)", ["3km", "lari"]),
              ("PUSH UP (55X 1MENIT)", ["push up", "pushup"]),
              ("SIT UP (60X1MENIT)", ["sit up", "situp"]),
              ("SQUAT (70X1MENIT)", ["squat"]),
              ("PLANK (4MENIT)", ["plank"]),
              ("FARMER WALK (25kg)", ["farmer"]),
              ("ANGKAT BEBAN (35kg)", ["beban", "angkat beban"])
          ]

        rows_akad = ""
        tot_akad = 0
        cnt_akad = 0
        pdf_akad_data = []

        for idx, (sub_name, vnum) in enumerate(locked_akad_subs, 1):
          if pd.isna(vnum) or vnum == 0: vnum = 75.0
          tot_akad += vnum
          cnt_akad += 1
          huruf = angka_ke_abjad(vnum)
          
          ket = get_clean_keterangan(sub_name.split('(')[0].strip(), vnum)
          pdf_akad_data.append({"sub": sub_name, "val": vnum, "huruf": huruf, "ket": ket})

          rows_akad += f"""
          <tr>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{idx}</td>
              <td style="border: 1px solid #cbd5e1; padding: 5px;">{sub_name}</td>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{vnum:.1f}</td>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;"><b>{huruf}</b></td>
              <td style="border: 1px solid #cbd5e1; padding: 5px; font-size: 11px;">{ket}</td>
          </tr>
          """
        avg_akad = (tot_akad / cnt_akad) if cnt_akad > 0 else 0

        rows_sikap = ""
        pdf_sikap_data = []
        for idx, cfg in enumerate(list_sikap_config, 1):
          sub_title = cfg["title"]
          vnum = get_akad_val(cfg["kw"])
          if vnum == 0: vnum = 85.0
          
          huruf = angka_ke_abjad(vnum)
          ket = get_catatan_perilaku_from_sheet2(sub_title, huruf, df_sheet2)
          pdf_sikap_data.append({"sub": sub_title, "val": vnum, "huruf": huruf, "ket": ket})
          
          rows_sikap += f"""
          <tr>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{idx}</td>
              <td style="border: 1px solid #cbd5e1; padding: 5px;">{sub_title}</td>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;"><b>{huruf}</b></td>
              <td style="border: 1px solid #cbd5e1; padding: 5px; font-size: 11px;">{ket}</td>
          </tr>
          """

        rows_fisik = ""
        pdf_fisik_data = []
        for idx, (sub_title, keywords) in enumerate(list_fisik_cols, 1):
          vnum = get_akad_val(keywords)
          if vnum == 0: vnum = 75.0

          huruf = angka_ke_abjad(vnum)
          ket = f"Performa dan kemampuan fisik pada {sub_title} terpantau dengan baik."

          pdf_fisik_data.append({"sub": sub_title, "val": vnum, "huruf": huruf, "ket": ket})
          rows_fisik += f"""
          <tr>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{idx}</td>
              <td style="border: 1px solid #cbd5e1; padding: 5px;">{sub_title}</td>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{vnum:.1f}</td>
              <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;"><b>{huruf}</b></td>
              <td style="border: 1px solid #cbd5e1; padding: 5px; font-size: 11px;">{ket}</td>
          </tr>
          """

        periode_str = f"{start_p.strftime('%d/%m/%Y')} - {end_p.strftime('%d/%m/%Y')}"

        html_raport = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body>
        <div style="background: white; padding: 35px; border-radius: 8px; color: #1e293b; border: 2px solid #be185d; font-family: 'Segoe UI', Tahoma, sans-serif;">
            
            <h2 style="text-align: center; color: #be185d; margin-bottom: 2px;">LPK YUTAKA EDUCATION CENTER</h2>
            <p style="text-align: center; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-top: 0;">Laporan Hasil Belajar Siswa (評価報告書)</p>
            <hr style="border: 1px solid #f472b6; margin-bottom: 15px;">
            
            <table style="width: 100%; font-size: 13px; margin-bottom: 15px; border: none;">
                <tr>
                    <td><b>Nama Siswa:</b> {pilih_nama}</td>
                    <td><b>Periode:</b> {periode_str}</td>
                </tr>
                <tr>
                    <td><b>NIS Siswa:</b> {nis_val}</td>
                    <td><b>Level / Kelas:</b> {kelas_val}</td>
                </tr>
            </table>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">1. KEMAMPUAN AKADEMIK</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 15px;">
                <thead>
                    <tr style="background: #be185d; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 35px;">No</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Mata Pelajaran (日本語能力)</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 60px;">Nilai</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 60px;">Predikat</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Keterangan</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_akad}
                    <tr style="background: #f1f5f9; font-weight: bold;">
                        <td colspan="2" style="text-align: right; border: 1px solid #cbd5e1; padding: 5px;">RATA-RATA:</td>
                        <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;">{avg_akad:.1f}</td>
                        <td style="text-align: center; border: 1px solid #cbd5e1; padding: 5px;"><b>{angka_ke_abjad(avg_akad)}</b></td>
                        <td style="border: 1px solid #cbd5e1; padding: 5px;"></td>
                    </tr>
                </tbody>
            </table>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">II. EVALUASI SIKAP & KARAKTER (生活態度)</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 15px;">
                <thead>
                    <tr style="background: #334155; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 35px;">No</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Aspek Penilaian</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 60px;">Predikat</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Catatan Perilaku</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_sikap}
                </tbody>
            </table>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">III. KEHADIRAN</h4>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse; margin-bottom: 15px;">
                <tr style="background: #f8fafc;">
                    <td style="border: 1px solid #cbd5e1; padding: 5px;"><b>Hadir:</b> {hadir_val} Hari</td>
                    <td style="border: 1px solid #cbd5e1; padding: 5px;"><b>Izin/Sakit:</b> {izin_val} Hari</td>
                    <td style="border: 1px solid #cbd5e1; padding: 5px;"><b>Alpa:</b> {alpa_val} Hari</td>
                    <td style="border: 1px solid #cbd5e1; padding: 5px;"><b>Total Hari:</b> {hadir_val + izin_val + alpa_val} Hari</td>
                </tr>
            </table>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">IV. CATATAN SENSEI</h4>
            <div style="background: #fdf2f8; padding: 8px; border-left: 4px solid #be185d; font-size: 12px; margin-bottom: 15px;">
                {catatan_umum}
            </div>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">V. KESIMPULAN</h4>
            <div style="font-size: 14px; font-weight: bold; color: #059669; padding: 4px 0; margin-bottom: 30px;">
                STATUS: {kesimpulan}
            </div>

            <hr style="border: 2px dashed #cbd5e1; margin: 30px 0;">

            <h2 style="text-align: center; color: #be185d; margin-bottom: 2px;">LPK YUTAKA EDUCATION CENTER</h2>
            <p style="text-align: center; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-top: 0;">Laporan Hasil Evaluasi Fisik Siswa (体力評価試験)</p>
            <hr style="border: 1px solid #f472b6; margin-bottom: 15px;">

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">I. KEMAMPUAN FISIK</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 15px;">
                <thead>
                    <tr style="background: #be185d; color: white;">
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 35px;">No</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Item Tes Fisik</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 60px;">Nilai</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; width: 60px;">Predikat</th>
                        <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Keterangan</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_fisik}
                </tbody>
            </table>

            <h4 style="color: #be185d; border-bottom: 2px solid #be185d; padding-bottom: 4px; margin-bottom: 8px;">II. CATATAN SARAN FISIK</h4>
            <div style="background: #fdf2f8; padding: 8px; border-left: 4px solid #be185d; font-size: 12px; margin-bottom: 15px;">
                {catatan_fisik}
            </div>

        </div>
        </body>
        </html>
        """
        
        components.html(html_raport, height=1350, scrolling=True)

# ================= MENU 4: DATABASE =================
elif menu == "📂 Database":
  st.markdown("<div class='main-heading'>DATABASE PESERTA LPK YUTAKA</div>", unsafe_allow_html=True)
  if not df.empty:
    st.markdown("<p style='font-size:12px; color:#64748b;'>Menampilkan seluruh rekam data nilai dari Google Sheets.</p>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

# ================= MENU 5: UPLOAD / UNDUH =================
elif menu == "📤 Upload/Unduh":
  st.markdown("<div class='main-heading'>UPLOAD & DOWNLOAD DATA</div>", unsafe_allow_html=True)
  if not df.empty:
    st.download_button(
        label="📥 DOWNLOAD REKAP LENGKAP (EXCEL)",
        data=to_excel_bytes(df),
        file_name="laporan_lpk_yutaka_lengkap.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )