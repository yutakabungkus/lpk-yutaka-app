import io
import os
import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="LPK Yutaka Education Center - Sakura Theme",
    page_icon="🌸",
    layout="wide",
)

# Custom Styling (Tanpa Pembatas, Layout Bersih & Sejajar ke Bawah)
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

        /* Sidebar Styling */
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

DATA_FILE = "data_lpk_yutaka_v2.csv"


@st.cache_data
def load_data_cached(file_path):
  if os.path.exists(file_path):
    df_loaded = pd.read_csv(file_path)
    numeric_cols = [
        "Pos Test",
        "PreTest",
        "Rata-rata nilai",
        "Membaca",
        "Menulis",
        "Berbicara",
        "Mendengar",
        "Disiplin",
        "Sopan santun",
        "Kebersihan (5S)",
        "Kerjasama",
        "Safety",
        "Persiapan kerja",
        "Penggunaan alat",
        "Teknik kerja",
        "Komunikasi tim",
        "Sikap kerja",
    ]
    for col in numeric_cols:
      if col in df_loaded.columns:
        df_loaded[col] = pd.to_numeric(df_loaded[col], errors="coerce")
    return df_loaded
  else:
    df_default = pd.DataFrame(
        columns=[
            "Tanggal",
            "Kelas",
            "Nama",
            "Program",
            "Bab",
            "Sensei",
            "Pos Test",
            "Membaca",
            "Menulis",
            "Berbicara",
            "Mendengar",
            "Disiplin",
            "Sopan santun",
            "Kebersihan (5S)",
            "Kerjasama",
            "Safety",
            "Persiapan kerja",
            "Penggunaan alat",
            "Teknik kerja",
            "Komunikasi tim",
            "Sikap kerja",
        ]
    )
    df_default.to_csv(file_path, index=False)
    return df_default


df = load_data_cached(DATA_FILE)


def to_excel_bytes(dataframe):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    dataframe.to_excel(writer, index=False, sheet_name="Data_LPK")
  return output.getvalue()


# Konversi Nilai Angka ke Abjad (A, B, C, D, E) untuk Attitude
def angka_ke_abjad(val):
  if pd.isna(val):
    return "E"
  if val >= 90:
    return "A"
  elif val >= 80:
    return "B"
  elif val >= 70:
    return "C"
  elif val >= 60:
    return "D"
  else:
    return "E"


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
      ("📂 Database Peserta", "📂 Database"),
      ("📤 Upload & Unduh", "📤 Upload/Unduh"),
  ]

  for label, menu_key in menus:
    if st.button(label, key=f"btn_{menu_key}", use_container_width=True):
      st.session_state.active_menu = menu_key
      st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='color: #cbd5e1; font-size: 9px; text-align: center;'>SAKURA"
      " THEME // v5.4</p>",
      unsafe_allow_html=True,
  )

menu = st.session_state.active_menu

# ================= MENU 1: DASHBOARD =================
if menu == "📊 Dashboard":
  st.markdown(
      "<div class='main-heading'>LAPORAN PERKEMBANGAN PENDIDIKAN &"
      " TRAINING</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<div class='sub-heading'>SAKURA SYSTEM MONITORING — LPK YUTAKA"
      " EDUCATION CENTER</div>",
      unsafe_allow_html=True,
  )

  if df.empty:
    st.warning(
        "Sistem belum mendeteksi data. Silakan input atau upload file Excel di"
        " menu navigasi."
    )
  else:
    for col_chk in ["Kelas", "Bab", "Sensei", "Tanggal"]:
      if col_chk not in df.columns:
        df[col_chk] = "Semua"
    df_ui = df.fillna("Semua")

    f1, f2, f3 = st.columns(3)
    with f1:
      sel_kelas = st.selectbox(
          "Kelas",
          ["Semua Kelas"]
          + sorted(df_ui["Kelas"].astype(str).unique().tolist()),
          key="f_kelas",
      )
    with f2:
      sel_bab = st.selectbox(
          "Bab",
          ["Semua Bab"] + sorted(df_ui["Bab"].astype(str).unique().tolist()),
          key="f_bab",
      )
    with f3:
      sel_sensei = st.selectbox(
          "Sensei",
          ["Semua Sensei"]
          + sorted(df_ui["Sensei"].astype(str).unique().tolist()),
          key="f_sensei",
      )

    df["Parsed_Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    min_date = (
        df["Parsed_Tanggal"].min().date()
        if not df["Parsed_Tanggal"].isna().all()
        else pd.to_datetime("2026-01-01").date()
    )
    max_date = (
        df["Parsed_Tanggal"].max().date()
        if not df["Parsed_Tanggal"].isna().all()
        else pd.to_datetime("2026-12-31").date()
    )

    t1, t2 = st.columns(2)
    with t1:
      start_date = st.date_input("Dari Tanggal", min_date, key="f_start")
    with t2:
      end_date = st.date_input("Sampai Tanggal", max_date, key="f_end")

    # Filter Data
    df_v = df.copy()
    if sel_kelas != "Semua Kelas":
      df_v = df_v[df_v["Kelas"].astype(str) == sel_kelas]
    if sel_bab != "Semua Bab":
      df_v = df_v[df_v["Bab"].astype(str) == sel_bab]
    if sel_sensei != "Semua Sensei":
      df_v = df_v[df_v["Sensei"].astype(str) == sel_sensei]

    df_v["Parsed_Tanggal"] = pd.to_datetime(df_v["Tanggal"], errors="coerce")
    df_v = df_v[
        (df_v["Parsed_Tanggal"].dt.date >= start_date)
        & (df_v["Parsed_Tanggal"].dt.date <= end_date)
    ]

    score_col = (
        "Pos Test"
        if "Pos Test" in df_v.columns and df_v["Pos Test"].dropna().count() > 0
        else "Rata-rata nilai"
    )
    if score_col not in df_v.columns:
      df_v["Nilai_Acu"] = 0
      score_col = "Nilai_Acu"

    tot_p = df_v["Nama"].nunique() if "Nama" in df_v.columns else len(df_v)
    avg_s = (
        df_v[score_col].mean() if not df_v[score_col].dropna().empty else 0
    )

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
      st.metric("TOTAL PESERTA", f"{tot_p} Siswa")
    with m2:
      st.metric("RATA-RATA NILAI", f"{avg_s:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    if not df_v.empty:
      # ================= GRAFIK SEJAJAR KE BAWAH (VERTIKAL) =================

      # 1. RATA-RATA KELAS (BAR CHART)
      st.markdown(
          "<div style='font-size:14px; font-weight:700; color:#be185d;"
          " margin-bottom:6px;'>📊 Rata-rata Nilai Kelas (Target KKM:"
          " 90)</div>",
          unsafe_allow_html=True,
      )
      chart_df = df_v.groupby("Kelas")[score_col].mean().reset_index()
      chart_df.columns = ["Kelas", "Rata-rata"]

      if not chart_df.empty:
        bar_base = (
            alt.Chart(chart_df)
            .mark_bar(
                color="#fb7185", cornerRadiusTopLeft=6, cornerRadiusTopRight=6
            )
            .encode(
                x=alt.X(
                    "Kelas:N",
                    title="Kelas",
                    sort="-y",
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y(
                    "Rata-rata:Q", title="Nilai", scale=alt.Scale(domain=[0, 100])
                ),
                tooltip=["Kelas", "Rata-rata"],
            )
        )
        text_labels = (
            bar_base.mark_text(
                align="center",
                baseline="bottom",
                dy=-4,
                color="#1e293b",
                fontWeight="bold",
                fontSize=11,
            )
            .encode(text=alt.Text("Rata-rata:Q", format=".1f"))
        )
        kkm_line = (
            alt.Chart(pd.DataFrame({"y": [90]}))
            .mark_rule(color="#e11d48", strokeWidth=2, strokeDash=[4, 4])
            .encode(y="y:Q")
        )

        st.altair_chart(
            (bar_base + text_labels + kkm_line)
            .properties(height=280, background="transparent")
            .configure_view(stroke=None),
            use_container_width=True,
        )

      st.markdown("<br>", unsafe_allow_html=True)

      # 2. KOMPETENSI BAHASA (RADAR CHART)
      st.markdown(
          "<div style='font-size:14px; font-weight:700; color:#be185d;"
          " margin-bottom:6px;'>📚 Kompetensi Bahasa (Dengan Nilai"
          " Angka)</div>",
          unsafe_allow_html=True,
      )
      skill_cols = ["Membaca", "Menulis", "Mendengar", "Berbicara"]
      active_skills = [
          s for s in skill_cols if s in df_v.columns and df_v[s].dropna().sum() > 0
      ]
      if active_skills:
        lang_df = df_v[active_skills].mean().reset_index()
        lang_df.columns = ["Aspek", "Nilai"]

        fig_radar1 = px.line_polar(
            lang_df, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100]
        )
        fig_radar1.update_traces(
            fill="toself",
            line_color="#e11d48",
            marker_color="#fb7185",
            fillcolor="rgba(251, 113, 133, 0.25)",
            text=lang_df["Nilai"].apply(lambda x: f"{x:.1f}"),
            mode="lines+markers+text",
        )
        fig_radar1.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 100], gridcolor="#fbcfe8"
                ),
                angularaxis=dict(gridcolor="#fbcfe8"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155", family="Segoe UI", size=11),
            margin=dict(t=20, b=20, l=30, r=30),
            height=320,
        )
        st.plotly_chart(fig_radar1, use_container_width=True)

      st.markdown("<br>", unsafe_allow_html=True)

      # 3. PENILAIAN ATTITUDE (RADAR CHART BERBASIS ABJAD A-E & ANGKA)
      st.markdown(
          "<div style='font-size:14px; font-weight:700; color:#be185d;"
          " margin-bottom:6px;'>⭐ Penilaian Attitude (Predikat Abjad A, B, C,"
          " D, E)</div>",
          unsafe_allow_html=True,
      )
      att_cols = ["Disiplin", "Sopan santun", "Kebersihan (5S)", "Kerjasama"]
      active_att = [
          a for a in att_cols if a in df_v.columns and df_v[a].dropna().sum() > 0
      ]
      if active_att:
        att_df = df_v[active_att].mean().reset_index()
        att_df.columns = ["Aspek", "Nilai"]
        att_df["Abjad"] = att_df["Nilai"].apply(angka_ke_abjad)
        att_df["Label_Display"] = att_df.apply(
            lambda r: f"{r['Nilai']:.1f} ({r['Abjad']})", axis=1
        )

        fig_radar2 = px.line_polar(
            att_df, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100]
        )
        fig_radar2.update_traces(
            fill="toself",
            line_color="#059669",
            marker_color="#34d399",
            fillcolor="rgba(52, 211, 153, 0.25)",
            text=att_df["Label_Display"],
            mode="lines+markers+text",
        )
        fig_radar2.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 100], gridcolor="#a7f3d0"
                ),
                angularaxis=dict(gridcolor="#a7f3d0"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155", family="Segoe UI", size=11),
            margin=dict(t=20, b=20, l=30, r=30),
            height=320,
        )
        st.plotly_chart(fig_radar2, use_container_width=True)

      st.markdown("<br>", unsafe_allow_html=True)

      # 4. SKILL PRAKTEK SISWA (RADAR CHART)
      st.markdown(
          "<div style='font-size:14px; font-weight:700; color:#be185d;"
          " margin-bottom:6px;'>🛠️ Skill Praktik Siswa (Dengan Nilai"
          " Angka)</div>",
          unsafe_allow_html=True,
      )
      skill_praktik_cols = [
          "Safety",
          "Persiapan kerja",
          "Penggunaan alat",
          "Teknik kerja",
          "Komunikasi tim",
          "Sikap kerja",
      ]
      active_praktek = [
          p
          for p in skill_praktik_cols
          if p in df_v.columns and df_v[p].dropna().sum() > 0
      ]
      if active_praktek:
        prak_df = df_v[active_praktek].mean().reset_index()
        prak_df.columns = ["Aspek", "Nilai"]

        fig_radar3 = px.line_polar(
            prak_df, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100]
        )
        fig_radar3.update_traces(
            fill="toself",
            line_color="#d97706",
            marker_color="#fbbf24",
            fillcolor="rgba(251, 191, 36, 0.25)",
            text=prak_df["Nilai"].apply(lambda x: f"{x:.1f}"),
            mode="lines+markers+text",
        )
        fig_radar3.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 100], gridcolor="#fde68a"
                ),
                angularaxis=dict(gridcolor="#fde68a"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155", family="Segoe UI", size=11),
            margin=dict(t=20, b=20, l=30, r=30),
            height=320,
        )
        st.plotly_chart(fig_radar3, use_container_width=True)

    else:
      st.info("Tidak ada data yang cocok dengan parameter filter.")

    st.markdown("---")
    with st.expander("📋 LIHAT TABEL DATA MENTAH (SESUAI FILTER)"):
      st.dataframe(df_v, use_container_width=True)
      if not df_v.empty:
        st.download_button(
            label="📥 DOWNLOAD EXCEL (DATA TERFILTER)",
            data=to_excel_bytes(df_v),
            file_name="laporan_lpk_yutaka_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ================= MENU 2: INPUT NILAI =================
elif menu == "✍️ Input":
  st.markdown(
      "<div class='main-heading'>FORM INPUT NILAI & KOMPETENSI</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<div class='sub-heading'>SILAKAN MASUKKAN DATA PESERTA DIDIK DAN NILAI"
      " ASPEK TERKAIT</div>",
      unsafe_allow_html=True,
  )

  raw_senseis = (
      df["Sensei"].dropna().astype(str).unique().tolist()
      if "Sensei" in df.columns and not df.empty
      else ["Sensei A", "Sensei B"]
  )
  existing_senseis = [
      s for s in raw_senseis if s.strip().upper() != "REXSY"
  ]
  if not existing_senseis:
    existing_senseis = ["Sensei A", "Sensei B"]

  with st.form("form_in", clear_on_submit=True):
    st.markdown(
        "<h4 style='color: #be185d; margin-top:0;'>📌 Informasi Umum</h4>",
        unsafe_allow_html=True,
    )
    tanggal = st.date_input("1. Tanggal Penilaian")
    list_kelas = (
        sorted(df["Kelas"].dropna().astype(str).unique().tolist())
        if "Kelas" in df.columns and not df.empty
        else ["JFT", "N5L1", "N5L2", "N4L1", "N4L2", "PCL"]
    )
    kelas = st.selectbox("2. Kelas", list_kelas)
    program = st.selectbox("3. Program", ["Magang", "Reguler"])
    nama_siswa = st.text_input("4. Nama Lengkap Peserta")
    bab = st.text_input("5. Bab / Materi")
    sensei = st.selectbox("6. Nama Sensei / Pengajar", existing_senseis)

    st.markdown(
        "<h4 style='color: #be185d; margin-top:15px;'>📚 1. Kompetensi Bahasa"
        " (Skala 0-100)</h4>",
        unsafe_allow_html=True,
    )
    i1, i2, i3, i4, i5 = st.columns(5)
    pos_test = i1.number_input("Pos Test", 0, 100, 80)
    membaca = i2.number_input("Membaca", 0, 100, 80)
    menulis = i3.number_input("Menulis", 0, 100, 80)
    mendengar = i4.number_input("Mendengar", 0, 100, 80)
    berbicara = i5.number_input("Berbicara", 0, 100, 80)

    st.markdown(
        "<h4 style='color: #be185d; margin-top:15px;'>⭐ 2. Penilaian Attitude /"
        " Sikap (Skala 0-100)</h4>",
        unsafe_allow_html=True,
    )
    j1, j2, j3, j4 = st.columns(4)
    disiplin = j1.number_input("Disiplin", 0, 100, 85)
    sopan = j2.number_input("Sopan santun", 0, 100, 85)
    kebersihan = j3.number_input("Kebersihan (5S)", 0, 100, 85)
    kerjasama = j4.number_input("Kerjasama", 0, 100, 85)

    st.markdown(
        "<h4 style='color: #be185d; margin-top:15px;'>🛠️ 3. Skill Praktik"
        " Siswa (Skala 0-100)</h4>",
        unsafe_allow_html=True,
    )
    k1, k2, k3 = st.columns(3)
    safety = k1.number_input("Safety", 0, 100, 85)
    persiapan = k2.number_input("Persiapan kerja", 0, 100, 85)
    alat = k3.number_input("Penggunaan alat", 0, 100, 85)

    k4, k5, k6 = st.columns(3)
    teknik = k4.number_input("Teknik kerja", 0, 100, 85)
    komunikasi = k5.number_input("Komunikasi tim", 0, 100, 85)
    sikap_kerja = k6.number_input("Sikap kerja", 0, 100, 85)

    if st.form_submit_button(
        "💾 SIMPAN DATA NILAI PESERTA", use_container_width=True
    ):
      if nama_siswa.strip() == "":
        st.error(
            "⚠️ Nama lengkap peserta wajib diisi sebelum menyimpan data!"
        )
      else:
        new_row = pd.DataFrame({
            "Tanggal": [str(tanggal)],
            "Kelas": [kelas],
            "Nama": [nama_siswa],
            "Program": [program],
            "Bab": [bab],
            "Sensei": [sensei],
            "Pos Test": [pos_test],
            "Membaca": [membaca],
            "Menulis": [menulis],
            "Berbicara": [berbicara],
            "Mendengar": [mendengar],
            "Disiplin": [disiplin],
            "Sopan santun": [sopan],
            "Kebersihan (5S)": [kebersihan],
            "Kerjasama": [kerjasama],
            "Safety": [safety],
            "Persiapan kerja": [persiapan],
            "Penggunaan alat": [alat],
            "Teknik kerja": [teknik],
            "Komunikasi tim": [komunikasi],
            "Sikap kerja": [sikap_kerja],
        })
        m = pd.concat([df, new_row], ignore_index=True)
        m.to_csv(DATA_FILE, index=False)
        st.cache_data.clear()
        st.success(
            "🎉 Data nilai peserta berhasil disimpan ke database sistem!"
        )
        st.rerun()

# ================= MENU 3: DATABASE =================
elif menu == "📂 Database":
  st.markdown(
      "<div class='main-heading'>DATABASE PESERTA</div>",
      unsafe_allow_html=True,
  )
  if df.empty:
    st.info("Database kosong.")
  else:
    q = st.text_input("Cari Nama, Kelas, atau Sensei:")
    res = (
        df[
            df["Nama"].str.contains(q, case=False, na=False)
            | df["Kelas"].str.contains(q, case=False, na=False)
            | df["Sensei"].str.contains(q, case=False, na=False)
        ]
        if q
        else df
    )
    st.dataframe(res, use_container_width=True)

    st.download_button(
        label="📥 DOWNLOAD DATABASE (EXCEL)",
        data=to_excel_bytes(res),
        file_name="database_lpk_yutaka.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    if st.button("🗑️ KOSONGKAN DATABASE", use_container_width=True):
      if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
      st.cache_data.clear()
      st.rerun()

# ================= MENU 4: UPLOAD / UNDUH =================
elif menu == "📤 Upload/Unduh":
  st.markdown(
      "<div class='main-heading'>UPLOAD & DOWNLOAD DATA</div>",
      unsafe_allow_html=True,
  )
  up = st.file_uploader("Upload File Excel (.xlsx)", type=["xlsx", "xls"])
  if up:
    shs = pd.ExcelFile(up).sheet_names
    sh = st.selectbox("Pilih Sheet", shs)
    pdf = pd.read_excel(up, sheet_name=sh)
    st.dataframe(pdf.head(3), use_container_width=True)
    if st.button("🚀 GABUNGKAN KE SISTEM", use_container_width=True):
      if "Nama" in pdf.columns:
        m = pd.concat([df, pdf], ignore_index=True).dropna(subset=["Nama"])
        m.to_csv(DATA_FILE, index=False)
        st.cache_data.clear()
        st.success("Data berhasil digabungkan!")
        st.rerun()
      else:
        st.error("Kolom 'Nama' tidak ditemukan.")

  st.markdown("---")
  if not df.empty:
    st.download_button(
        label="📥 DOWNLOAD REKAP LENGKAP (EXCEL)",
        data=to_excel_bytes(df),
        file_name="laporan_lpk_yutaka_lengkap.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )