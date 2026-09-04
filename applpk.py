import os
import altair as alt
import pandas as pd
import streamlit as st

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="LPK Yutaka Education Center", page_icon="🎓", layout="wide"
)

# Custom Styling (CSS Modern & Judul Biru Dongker > 50px)
st.markdown(
    """
    <style>
        /* Main background */
        .main {
            background-color: #f8fafc;
        }
        /* Judul Utama Laporan Biru Dongker & Besar (> 50px) */
        .main-heading {
            font-size: 52px;
            font-weight: 800;
            color: #1e3a8a;
            line-height: 1.1;
            margin-top: 10px;
            margin-bottom: 5px;
            letter-spacing: -1px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .sub-heading {
            font-size: 16px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 25px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .app-title {
            font-size: 26px;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 0px;
        }
        .app-subtitle {
            font-size: 14px;
            font-weight: 500;
            color: #64748b;
            margin-top: 4px;
            margin-bottom: 20px;
        }
        .sidebar-title {
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            text-align: center;
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: #ffffff;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Nama File Penyimpanan Database Lokal
DATA_FILE = "data_lpk_yutaka.csv"


# Fungsi Load Data
def load_data():
  if os.path.exists(DATA_FILE):
    df_loaded = pd.read_csv(DATA_FILE)
    for col in [
        "Pos Test",
        "PreTest",
        "Rata-rata nilai",
        "Membaca",
        "Menulis",
        "Berbicara",
        "Mendengar",
        "Attitude",
    ]:
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
            "Sub bab",
            "Hari",
            "Minggu",
            "Pos Test",
            "Membaca",
            "Menulis",
            "Berbicara",
            "Mendengar",
            "Attitude",
            "Sensei",
        ]
    )
    df_default.to_csv(DATA_FILE, index=False)
    return df_default


df = load_data()

# ================= SIDEBAR NAVIGASI MODERN =================
st.sidebar.markdown(
    "<p class='sidebar-title'>🎓 LPK YUTAKA</p>", unsafe_allow_html=True
)
st.sidebar.markdown(
    "<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:"
    " -10px;'>Education & Training Div.</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigasi Menu Utama",
    [
        "📊 Dashboard Eksekutif",
        "✍️ Input Nilai & Laporan",
        "📂 Database & Pencarian",
        "📥 Rekap & Unduh Data",
        "📤 Upload Excel LPK",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tips:** Gunakan filter di Dashboard untuk menyaring laporan per"
    " kelas, bab, atau minggu."
)

# ================= MENU 1: DASHBOARD EKSEKUTIF =================
if menu == "📊 Dashboard Eksekutif":
  # Judul Besar Warna Biru Dongker > 50px
  st.markdown(
      "<div class='main-heading'>Laporan Perkembangan Pendidikan &"
      " Training</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<div class='sub-heading'>LPK Yutaka Education Center — Div. Education &"
      " Training</div>",
      unsafe_allow_html=True,
  )

  if df.empty:
    st.warning(
        "Belum ada data akademik yang tersedia. Silakan unggah file Excel atau"
        " isi data melalui menu Input."
    )
  else:
    # Kontainer Filter (Kelas, Bab, Hari, Minggu)
    with st.container():
      st.markdown("### 🎛️ Panel Filter Data Akademik")

      for col_chk in ["Kelas", "Bab", "Hari", "Minggu"]:
        if col_chk not in df.columns:
          df[col_chk] = "Semua"

      df_ui = df.fillna("Tidak Diketahui")

      f1, f2, f3, f4 = st.columns(4)
      with f1:
        sel_kelas = st.selectbox(
            "Pilih Kelas",
            ["Semua Kelas"]
            + sorted(df_ui["Kelas"].astype(str).unique().tolist()),
        )
      with f2:
        sel_bab = st.selectbox(
            "Pilih Bab",
            ["Semua Bab"]
            + sorted(df_ui["Bab"].astype(str).unique().tolist()),
        )
      with f3:
        sel_hari = st.selectbox(
            "Pilih Hari",
            ["Semua Hari"]
            + sorted(df_ui["Hari"].astype(str).unique().tolist()),
        )
      with f4:
        sel_minggu = st.selectbox(
            "Pilih Minggu",
            ["Semua Minggu"]
            + sorted(df_ui["Minggu"].astype(str).unique().tolist()),
        )

    # Filter Logika DataFrame
    df_v = df.copy()
    if sel_kelas != "Semua Kelas":
      df_v = df_v[df_v["Kelas"].astype(str) == sel_kelas]
    if sel_bab != "Semua Bab":
      df_v = df_v[df_v["Bab"].astype(str) == sel_bab]
    if sel_hari != "Semua Hari":
      df_v = df_v[df_v["Hari"].astype(str) == sel_hari]
    if sel_minggu != "Semua Minggu":
      df_v = df_v[df_v["Minggu"].astype(str) == sel_minggu]

    st.markdown("---")

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
    max_s = (
        df_v[score_col].max() if not df_v[score_col].dropna().empty else 0
    )
    min_s = (
        df_v[score_col].min() if not df_v[score_col].dropna().empty else 0
    )

    # Kartu Metrik Utama (Rata-rata Kelas, Nilai Tertinggi, Nilai Terendah)
    st.markdown(
        f"### 📈 Ringkasan Nilai & Performa ({len(df_v)} Data Terpilih)"
    )
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Peserta", f"{tot_p} Orang")
    m2.metric("Rata-rata Kelas", f"{avg_s:.2f}")
    m3.metric("Nilai Tertinggi", f"{max_s}")
    m4.metric("Nilai Terendah", f"{min_s}")
    m5.metric("Total Rekaman", f"{len(df_v)}")

    st.markdown("---")

    # ================= VISUALISASI GRAFIK DENGAN GARIS KKM & ASPEK KEMAMPUAN =================

    st.markdown("### 📊 Visualisasi Grafik Analitik")

    if not df_v.empty and "Kelas" in df_v.columns:
      # 1. Grafik Rata-rata Nilai per Kelas dengan Garis KKM 90
      st.markdown("##### 📌 Rata-rata Nilai Kelas (Dilengkapi Garis KKM 90)")
      chart_df = df_v.groupby("Kelas")[score_col].mean().reset_index()
      chart_df.columns = ["Kelas", "Rata-rata Nilai"]

      base_chart = (
          alt.Chart(chart_df)
          .mark_bar(color="#1e3a8a", cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
          .encode(
              x=alt.X("Kelas:N", title="Kelas", sort="-y"),
              y=alt.Y("Rata-rata Nilai:Q", title="Rata-rata Nilai"),
              tooltip=["Kelas", "Rata-rata Nilai"],
          )
      )

      # Garis KKM 90
      kkm_line = (
          alt.Chart(pd.DataFrame({"y": [90]}))
          .mark_rule(color="red", strokeWidth=2, strokeDash=[5, 5])
          .encode(y="y:Q")
      )

      kkm_text = (
          alt.Chart(pd.DataFrame({"y": [90], "label": ["KKM (90)"]}))
          .mark_text(align="left", dx=5, dy=-5, color="red", fontWeight="bold")
          .encode(y="y:Q", text="label:N")
      )

      st.altair_chart(
          (base_chart + kkm_line + kkm_text).properties(height=350),
          use_container_width=True,
      )

      st.markdown("---")

      # 2. Grafik Kompetensi (Membaca, Menulis, Berbicara, Mendengar)
      st.markdown(
          "##### 📚 Grafik Perbandingan Kompetensi (Membaca, Menulis, Berbicara,"
          " Mendengar)"
      )
      skill_cols = ["Membaca", "Menulis", "Berbicara", "Mendengar"]
      active_skills = [
          s
          for s in skill_cols
          if s in df_v.columns and df_v[s].dropna().sum() > 0
      ]

      if active_skills:
        skill_df = df_v.groupby("Kelas")[active_skills].mean().reset_index()
        skill_melted = skill_df.melt(
            id_vars=["Kelas"],
            value_vars=active_skills,
            var_name="Aspek",
            value_name="Nilai",
        )

        skill_chart = (
            alt.Chart(skill_melted)
            .mark_bar()
            .encode(
                x=alt.X("Kelas:N", title="Kelas"),
                y=alt.Y("Nilai:Q", title="Nilai Rata-rata"),
                color=alt.Color(
                    "Aspek:N", title="Kompetensi", scale=alt.Scale(scheme="blues")
                ),
                column="Aspek:N",
                tooltip=["Kelas", "Aspek", "Nilai"],
            )
            .properties(width=150, height=300)
        )
        st.altair_chart(skill_chart, use_container_width=True)
      else:
        st.info(
            "Belum ada data nilai membaca, menulis, berbicara, atau mendengar"
            " yang terisi untuk filter ini."
        )

      st.markdown("---")

      # 3. Grafik Attitude
      st.markdown("##### ⭐ Grafik Penilaian Attitude (Sikap)")
      if "Attitude" in df_v.columns and df_v["Attitude"].dropna().sum() > 0:
        att_df = df_v.groupby("Kelas")["Attitude"].mean().reset_index()
        att_df.columns = ["Kelas", "Nilai Attitude"]

        att_chart = (
            alt.Chart(att_df)
            .mark_bar(color="#10b981", cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Kelas:N", title="Kelas", sort="-y"),
                y=alt.Y("Nilai Attitude:Q", title="Rata-rata Attitude"),
                tooltip=["Kelas", "Nilai Attitude"],
            )
            .properties(height=300)
        )
        st.altair_chart(att_chart, use_container_width=True)
      else:
        st.info("Belum ada data Attitude yang terisi untuk filter ini.")

    else:
      st.info("Data belum mencukupi untuk menampilkan grafik analitik.")

    st.markdown("---")
    st.markdown("### 📋 Tabel Rincian Data Laporan")
    st.dataframe(df_v, use_container_width=True)

# ================= MENU 2: INPUT NILAI & LAPORAN =================
elif menu == "✍️ Input Nilai & Laporan":
  st.markdown(
      "<p class='app-title'>LPK Yutaka Education Center</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p class='app-subtitle'>Div. Education & Training — Form Input Nilai &"
      " Laporan</p>",
      unsafe_allow_html=True,
  )

  with st.form("form_modern", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
      tanggal = st.date_input("Tanggal Pelaporan")
      nama_siswa = st.text_input(
          "Nama Lengkap Peserta", placeholder="Contoh: Budi Santoso"
      )
      kelas = st.text_input("Kelas", placeholder="Contoh: N3 Magang / PCL")
      program = st.selectbox(
          "Program", ["Reguler", "Magang", "Kaigo", "Knit", "Lainnya"]
      )
      bab = st.text_input("Bab / Materi", placeholder="Contoh: Bab 5")

    with c2:
      sub_bab = st.text_input("Sub Bab", placeholder="Contoh: Bunkei & Renshuu")
      hari = st.text_input("Hari", placeholder="Contoh: Senin")
      minggu = st.text_input("Minggu", placeholder="Contoh: Minggu ke-2")
      sensei = st.text_input("Nama Sensei", placeholder="Contoh: Pak Regi")

    st.markdown("---")
    st.markdown(
        "##### 🔢 Penilaian Aspek & Kompetensi (Membaca, Menulis, Berbicara,"
        " Mendengar, Attitude - Skala 0 s.d 100)"
    )
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)

    with sc1:
      pos_test = st.number_input(
          "Pos Test", min_value=0, max_value=100, value=80
      )
    with sc2:
      membaca = st.number_input(
          "Membaca", min_value=0, max_value=100, value=80
      )
    with sc3:
      menulis = st.number_input(
          "Menulis", min_value=0, max_value=100, value=80
      )
    with sc4:
      berbicara = st.number_input(
          "Berbicara", min_value=0, max_value=100, value=80
      )
    with sc5:
      mendengar = st.number_input(
          "Mendengar", min_value=0, max_value=100, value=80
      )
    with sc6:
      attitude = st.number_input(
          "Attitude", min_value=0, max_value=100, value=85
      )

    submitted = st.form_submit_button(
        "💾 Simpan Data ke Sistem", use_container_width=True
    )

    if submitted:
      if nama_siswa.strip() == "":
        st.error("Nama peserta wajib diisi!")
      else:
        new_row = pd.DataFrame({
            "Tanggal": [str(tanggal)],
            "Kelas": [kelas],
            "Nama": [nama_siswa],
            "Program": [program],
            "Bab": [bab],
            "Sub bab": [sub_bab],
            "Hari": [hari],
            "Minggu": [minggu],
            "Pos Test": [pos_test],
            "Membaca": [membaca],
            "Menulis": [menulis],
            "Berbicara": [berbicara],
            "Mendengar": [mendengar],
            "Attitude": [attitude],
            "Sensei": [sensei],
        })

        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False)
        st.success(
            f"Berhasil! Data nilai untuk **{nama_siswa}** tersimpan dengan"
            " aman."
        )
        st.rerun()

# ================= MENU 3: DATABASE & PENCARIAN =================
elif menu == "📂 Database & Pencarian":
  st.markdown(
      "<p class='app-title'>LPK Yutaka Education Center</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p class='app-subtitle'>Div. Education & Training — Database & Pencarian"
      " Peserta</p>",
      unsafe_allow_html=True,
  )

  if df.empty:
    st.info("Belum ada data dalam database.")
  else:
    search_q = st.text_input(
        "🔍 Kata Kunci Pencarian (Nama, Kelas, Bab, atau Sensei):",
        placeholder="Ketik untuk mencari...",
    )

    f_df = df
    if search_q:
      f_df = df[
          df["Nama"].str.contains(search_q, case=False, na=False)
          | df["Kelas"].str.contains(search_q, case=False, na=False)
          | df["Bab"].str.contains(search_q, case=False, na=False)
          | df["Sensei"].str.contains(search_q, case=False, na=False)
      ]

    st.dataframe(f_df, use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Reset / Kosongkan Seluruh Database", type="secondary"):
      if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
      st.warning("Database berhasil dikosongkan!")
      st.rerun()

# ================= MENU 4: REKAP & UNDUH DATA =================
elif menu == "📥 Rekap & Unduh Data":
  st.markdown(
      "<p class='app-title'>LPK Yutaka Education Center</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p class='app-subtitle'>Div. Education & Training — Unduh Laporan"
      " Akademik</p>",
      unsafe_allow_html=True,
  )

  if df.empty:
    st.warning("Tidak ada data yang dapat diunduh.")
  else:
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data CSV Lengkap",
        data=csv_bytes,
        file_name="rekap_akademik_lpk_yutaka.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ================= MENU 5: UPLOAD EXCEL LPK =================
elif menu == "📤 Upload Excel LPK":
  st.markdown(
      "<p class='app-title'>LPK Yutaka Education Center</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p class='app-subtitle'>Div. Education & Training — Unggah File Excel"
      " LPK</p>",
      unsafe_allow_html=True,
  )

  up_file = st.file_uploader(
      "Pilih file Excel (.xlsx / .xls)", type=["xlsx", "xls"]
  )

  if up_file is not None:
    try:
      xls_reader = pd.ExcelFile(up_file)
      sheets = xls_reader.sheet_names

      chosen_sheet = st.selectbox(
          "Pilih Lembar Kerja (Sheet) dari File Excel:", sheets
      )
      preview_df = pd.read_excel(up_file, sheet_name=chosen_sheet)

      st.markdown(f"**Pratinjau Data dari Sheet: `{chosen_sheet}`**")
      st.dataframe(preview_df.head(), use_container_width=True)

      if st.button(
          "🚀 Proses & Gabungkan ke Database Utama", type="primary"
      ):
        if "Nama" in preview_df.columns:
          merged_df = pd.concat([df, preview_df], ignore_index=True)
          merged_df = merged_df.dropna(subset=["Nama"])
          merged_df.to_csv(DATA_FILE, index=False)
          st.success("Sukses! Data Excel berhasil digabungkan ke sistem.")
          st.rerun()
        else:
          st.error(
              "Kesalahan: Kolom 'Nama' tidak ditemukan di dalam sheet Excel"
              " tersebut. Periksa kembali format file Anda."
          )
    except Exception as exc:
      st.error(f"Gagal memproses file: {exc}")