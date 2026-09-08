import io
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np

# Import ReportLab untuk Export PDF 2 Lembar Resmi
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="LPK Yutaka Education Center - Realtime Sheets",
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

# ID SPREADSHEET UTAMA ANDA
SPREADSHEET_ID = "1BaF_bDqgtKqLr9YF8P-DLOoSbN8ZO51fdfikaaFkLi8"


@st.cache_resource
def init_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  
  # Cek apakah dijalankan di lokal (file credentials.json tersedia di direktori)
  if os.path.exists("credentials.json"):
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
  else:
    # Jika dijalankan di Streamlit Cloud (menggunakan st.secrets)
    creds_dict = {
        "type": "service_account",
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
    }
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    
  client = gspread.authorize(creds)
  return client


def load_data_from_sheets():
  try:
    client = init_connection()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    
    sheet1 = spreadsheet.get_worksheet(0)
    rows1 = sheet1.get_all_values()
    df_loaded = pd.DataFrame()
    if rows1 and len(rows1) > 1:
      df_loaded = pd.DataFrame(rows1[1:], columns=rows1[0])
      
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
          "Tanggal", "Kelas", "NIS", "NIS Siswa", "Nama", "Jenis Kelamin", "Program", 
          "Bab", "Sub bab", "Sensei", "Keterangan", "Disiplin", 
          "Sopan santun", "Kebersihan (5S)", "Kerjasama",
          "Safety", "Persiapan kerja", "Penggunaan alat", "Teknik kerja", "Komunikasi tim", "Sikap kerja"
      ]
      for col in df_loaded.columns:
        if col not in skip_cols:
          df_loaded[col] = pd.to_numeric(df_loaded[col], errors="coerce")

    df_catatan_sheet2 = pd.DataFrame()
    try:
      sheet2 = spreadsheet.get_worksheet(1)
      rows2 = sheet2.get_all_values()
      if rows2 and len(rows2) > 1:
        df_catatan_sheet2 = pd.DataFrame(rows2[1:], columns=rows2[0])
    except Exception:
      pass

    return df_loaded, df_catatan_sheet2
  except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    return pd.DataFrame(), pd.DataFrame()


def save_row_to_sheets(new_row_dict):
  try:
    client = init_connection()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.get_worksheet(0)
    header = sheet.row_values(1)
    row_values = [str(new_row_dict.get(col, "")) for col in header]
    sheet.append_row(row_values)
    st.cache_resource.clear()
    return True
  except Exception as e:
    st.error(f"Gagal menyimpan ke Google Sheets: {e}")
    return False


df, df_sheet2 = load_data_from_sheets()


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


def get_fisik_keterangan(item_fisik, val):
  if val >= 85:
    return f"Performa sangat prima dan melampaui target standar pada {item_fisik}."
  elif val >= 70:
    return f"Kemampuan fisik baik dan memenuhi standar yang ditetapkan pada {item_fisik}."
  elif val >= 50:
    return f"Kemampuan fisik cukup pada {item_fisik}, perlu ditingkatkan daya tahannya."
  else:
    return f"Memerlukan latihan fisik tambahan dan peningkatan stamina pada {item_fisik}."


def generate_radar_chart_image(akad_data, title="Grafik Kompetensi Akademik"):
  labels = [item['sub'].split('(')[0].strip() for item in akad_data]
  stats = [item['val'] for item in akad_data]

  angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
  stats += stats[:1]
  angles += angles[:1]
  labels += labels[:1]

  fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw=dict(polar=True))
  ax.plot(angles, stats, color='#be185d', linewidth=2, linestyle='solid')
  ax.fill(angles, stats, color='#fb7185', alpha=0.3)
  ax.set_theta_offset(np.pi / 2)
  ax.set_theta_direction(-1)
  ax.set_rgrids([20, 40, 60, 80, 100], labels=["20", "40", "60", "80", "100"], fontsize=7, color="#64748b")
  ax.set_ylim(0, 100)
  ax.set_xticks(angles[:-1])
  ax.set_xticklabels(labels[:-1], fontsize=7, color="#1e293b")
  plt.title(title, size=9, color='#be185d', y=1.1, weight='bold')
  
  img_buf = io.BytesIO()
  plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=150, transparent=True)
  plt.close(fig)
  img_buf.seek(0)
  return img_buf


def generate_bar_chart_image(fisik_data, title="Grafik Kemampuan Fisik"):
  labels = [item['sub'].split('(')[0].strip()[:12] for item in fisik_data]
  stats = [item['val'] for item in fisik_data]

  fig, ax = plt.subplots(figsize=(5.5, 2.5))
  bars = ax.bar(labels, stats, color='#334155', width=0.55, edgecolor='#1e293b')
  
  ax.set_ylim(0, 105)
  ax.set_ylabel("Nilai", fontsize=8, color="#1e293b", weight='bold')
  ax.set_title(title, size=10, color='#be185d', weight='bold', pad=10)
  ax.tick_params(axis='x', rotation=15, labelsize=7)
  ax.tick_params(axis='y', labelsize=8)
  ax.grid(axis='y', linestyle='--', alpha=0.5)

  for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=7, weight='bold', color='#1e293b')

  plt.tight_layout()
  img_buf = io.BytesIO()
  plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=150, transparent=True)
  plt.close(fig)
  img_buf.seek(0)
  return img_buf


def generate_pdf_2_pages(nama, nis, kelas, jk, program_val, periode, akad_data, sikap_data, fisik_data, hadir_vals, catatan_akad, catatan_fisik, kesimpulan):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
  story = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#be185d'), alignment=1, spaceAfter=4)
  subtitle_style = ParagraphStyle('T2', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), alignment=1, spaceAfter=15)
  heading_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#be185d'), spaceBefore=8, spaceAfter=4)

  # ================= HALAMAN 1 =================
  story.append(Paragraph("<b>LPK YUTAKA EDUCATION CENTER</b>", title_style))
  story.append(Paragraph("LAPORAN HASIL BELAJAR SISWA (Evaluasi Akademik & Sikap)", subtitle_style))

  bio_data = [
      [Paragraph(f"<b>Nama Siswa:</b> {nama}", styles['Normal']), Paragraph(f"<b>Periode:</b> {periode}", styles['Normal'])],
      [Paragraph(f"<b>NIS Siswa:</b> {nis}", styles['Normal']), Paragraph(f"<b>Level / Kelas:</b> {kelas}", styles['Normal'])]
  ]
  t_bio = Table(bio_data, colWidths=[250, 250])
  t_bio.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
  story.append(t_bio)
  story.append(Spacer(1, 6))

  story.append(Paragraph("<b>1. KEMAMPUAN AKADEMIK</b>", heading_style))
  t_akad_rows = [["No", "Mata Pelajaran", "Nilai", "Predikat", "Keterangan"]]
  tot_val = 0
  for idx, item in enumerate(akad_data, 1):
    sub_name_clean = item['sub'].split('(')[0].strip()
    t_akad_rows.append([str(idx), sub_name_clean, f"{item['val']:.1f}", item['huruf'], item['ket']])
    tot_val += item['val']
  avg_val = (tot_val / len(akad_data)) if akad_data else 0
  t_akad_rows.append(["", "RATA-RATA", f"{avg_val:.1f}", angka_ke_abjad(avg_val), ""])

  t_akad = Table(t_akad_rows, colWidths=[30, 160, 50, 50, 210])
  t_akad.setStyle(TableStyle([
      ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#be185d')),
      ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
      ('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('ALIGN', (2,0), (3,-1), 'CENTER'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
      ('PADDING', (0,0), (-1,-1), 4),
      ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
      ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
  ]))
  story.append(t_akad)
  story.append(Spacer(1, 6))

  try:
    radar_img_buf = generate_radar_chart_image(akad_data, "Grafik Kompetensi Akademik")
    story.append(RLImage(radar_img_buf, width=130, height=130, hAlign='CENTER'))
    story.append(Spacer(1, 6))
  except Exception:
    pass

  story.append(Paragraph("<b>II. EVALUASI SIKAP & KARAKTER</b>", heading_style))
  t_sikap_rows = [["No", "Aspek Penilaian", "Predikat", "Catatan Perilaku"]]
  for idx, item in enumerate(sikap_data, 1):
    sub_sikap_clean = item['sub'].split('(')[0].strip()
    t_sikap_rows.append([str(idx), sub_sikap_clean, item['huruf'], item['ket']])
  t_sikap = Table(t_sikap_rows, colWidths=[30, 160, 50, 260])
  t_sikap.setStyle(TableStyle([
      ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
      ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
      ('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('ALIGN', (2,0), (2,-1), 'CENTER'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
      ('PADDING', (0,0), (-1,-1), 4),
  ]))
  story.append(t_sikap)
  story.append(Spacer(1, 6))

  story.append(Paragraph("<b>III. KEHADIRAN</b>", heading_style))
  t_hadir = Table([[f"Hadir: {hadir_vals[0]} Hari", f"Izin/Sakit: {hadir_vals[1]} Hari", f"Alpa: {hadir_vals[2]} Hari", f"Total: {sum(hadir_vals)} Hari"]], colWidths=[125, 125, 125, 125])
  t_hadir.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')), ('PADDING', (0,0), (-1,-1), 4), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
  story.append(t_hadir)
  story.append(Spacer(1, 6))

  story.append(Paragraph("<b>IV. CATATAN SENSEI</b>", heading_style))
  story.append(Table([[Paragraph(catatan_akad, styles['Normal'])]], colWidths=[500], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fdf2f8')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f472b6')), ('PADDING', (0,0), (-1,-1), 4)]))
  story.append(Spacer(1, 4))
  story.append(Paragraph(f"<b>V. KESIMPULAN: <font color='#059669'>{kesimpulan}</font></b>", styles['Normal']))

  story.append(PageBreak())

  # ================= HALAMAN 2 =================
  story.append(Paragraph("<b>LPK YUTAKA EDUCATION CENTER</b>", title_style))
  story.append(Paragraph("LAPORAN HASIL EVALUASI FISIK SISWA", subtitle_style))
  story.append(Spacer(1, 8))

  story.append(Paragraph("<b>I. KEMAMPUAN FISIK</b>", heading_style))
  t_fisik_rows = [["No", "Item Tes Fisik", "Nilai", "Predikat", "Keterangan"]]
  for idx, item in enumerate(fisik_data, 1):
    t_fisik_rows.append([str(idx), item['sub'], f"{item['val']:.1f}", item['huruf'], item['ket']])

  t_fisik = Table(t_fisik_rows, colWidths=[30, 180, 50, 50, 190])
  t_fisik.setStyle(TableStyle([
      ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#be185d')),
      ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
      ('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('ALIGN', (2,0), (3,-1), 'CENTER'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
      ('PADDING', (0,0), (-1,-1), 4),
  ]))
  story.append(t_fisik)
  story.append(Spacer(1, 8))

  try:
    bar_fisik_buf = generate_bar_chart_image(fisik_data, "Grafik Kemampuan Fisik (Vertical Bar)")
    story.append(RLImage(bar_fisik_buf, width=240, height=120, hAlign='CENTER'))
    story.append(Spacer(1, 8))
  except Exception:
    pass

  story.append(Paragraph("<b>II. CATATAN SARAN FISIK</b>", heading_style))
  story.append(Table([[Paragraph(catatan_fisik, styles['Normal'])]], colWidths=[500], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fdf2f8')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f472b6')), ('PADDING', (0,0), (-1,-1), 5)]))

  doc.build(story)
  buffer.seek(0)
  return buffer.getvalue()


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

  if st.button("🔄 Refresh Data Sheets", use_container_width=True):
    st.cache_resource.clear()
    st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='color: #cbd5e1; font-size: 9px; text-align: center;'>SAKURA"
      " REALTIME // v11.40</p>",
      unsafe_allow_html=True,
  )

menu = st.session_state.active_menu

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

    f1, f2, f3, f4 = st.columns(4)
    with f1:
      sel_kelas = st.selectbox("Kelas", ["Semua Kelas"] + sorted(df_ui["Kelas"].astype(str).unique().tolist()))
    with f2:
      sel_nis = st.selectbox("NIS Siswa", ["Semua NIS"] + sorted(df_ui["NIS"].astype(str).unique().tolist()))
    with f3:
      sel_bab = st.selectbox("Bab", ["Semua Bab"] + sorted(df_ui["Bab"].astype(str).unique().tolist()))
    with f4:
      sel_sensei = st.selectbox("Sensei", ["Semua Sensei"] + sorted(df_ui["Sensei"].astype(str).unique().tolist()))

    df["Parsed_Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    min_date = df["Parsed_Tanggal"].min().date() if not df["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-01-01").date()
    max_date = df["Parsed_Tanggal"].max().date() if not df["Parsed_Tanggal"].isna().all() else pd.to_datetime("2026-12-31").date()

    t1, t2 = st.columns(2)
    with t1:
      start_date = st.date_input("Dari Tanggal", min_date, key="f_start")
    with t2:
      end_date = st.date_input("Sampai Tanggal", max_date, key="f_end")

    df_v = df.copy()
    if sel_kelas != "Semua Kelas":
      df_v = df_v[df_v["Kelas"].astype(str) == sel_kelas]
    if sel_nis != "Semua NIS":
      df_v = df_v[df_v["NIS"].astype(str) == sel_nis]
    if sel_bab != "Semua Bab":
      df_v = df_v[df_v["Bab"].astype(str) == sel_bab]
    if sel_sensei != "Semua Sensei":
      df_v = df_v[df_v["Sensei"].astype(str) == sel_sensei]

    df_v["Parsed_Tanggal"] = pd.to_datetime(df_v["Parsed_Tanggal"], errors="coerce")
    df_v = df_v[
        (df_v["Parsed_Tanggal"] >= pd.Timestamp(start_date)) & 
        (df_v["Parsed_Tanggal"] <= pd.Timestamp(end_date))
    ]

    score_col = "Pos Test" if "Pos Test" in df_v.columns and df_v["Pos Test"].dropna().count() > 0 else "Rata-rata nilai"
    if score_col not in df_v.columns:
      df_v["Nilai_Acu"] = 0
      score_col = "Nilai_Acu"

    tot_p = df_v["Nama"].nunique() if "Nama" in df_v.columns else len(df_v)
    avg_s = df_v[score_col].mean() if not df_v[score_col].dropna().empty else 0

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
      st.metric("TOTAL PESERTA", f"{tot_p} Siswa")
    with m2:
      st.metric("RATA-RATA NILAI KESELURUHAN", f"{avg_s:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. RATA-RATA SEMUA KELAS (DIAMBIL DARI POS TEST SEMUA SUB BAB)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>1. 📊 Rata-rata Semua Kelas (Target KKM: 90)</div>", unsafe_allow_html=True)
    
    main_score_col = "Pos Test" if "Pos Test" in df.columns else (score_col if score_col in df.columns else df.columns[-1])
    if main_score_col in df.columns:
      chart_df = df.groupby("Kelas")[main_score_col].mean().reset_index()
      chart_df.columns = ["Kelas", "Rata-rata"]
    else:
      chart_df = pd.DataFrame(columns=["Kelas", "Rata-rata"])

    if not chart_df.empty:
      bar_base = alt.Chart(chart_df).mark_bar(color="#fb7185", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
          x=alt.X("Kelas:N", title="Kelas", sort="-y", axis=alt.Axis(labelAngle=0)),
          y=alt.Y("Rata-rata:Q", title="Nilai", scale=alt.Scale(domain=[0, 100])),
          tooltip=["Kelas", "Rata-rata"],
      )
      text_labels = bar_base.mark_text(align="center", baseline="bottom", dy=-4, color="#1e293b", fontWeight="bold", fontSize=11).encode(text=alt.Text("Rata-rata:Q", format=".1f"))
      kkm_line = alt.Chart(pd.DataFrame({"y": [90]})).mark_rule(color="#e11d48", strokeWidth=2.5, strokeDash=[4, 4]).encode(y="y:Q")
      st.altair_chart((bar_base + text_labels + kkm_line).properties(height=280, background="transparent").configure_view(stroke=None), use_container_width=True)
    else:
      st.info("Data nilai untuk rekapitulasi kelas belum tersedia.")

    st.markdown("---")

    # 2. KEMAMPUAN AKADEMIK BERDASARKAN SUB TES (GRAFIK RADAR DENGAN FILTER KATA KUNCI TERTENTU)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>2. 📚 Kemampuan Akademik Berdasarkan Sub Tes (Grafik Radar)</div>", unsafe_allow_html=True)
    
    allowed_sub_keywords = ["言葉", "文法", "漢字", "聴解", "読解", "読む", "書く", "kotoba", "bunpou", "kanji", "choukai", "dokkai"]
    
    df_acad_all = df_v[df_v["Sub bab"].astype(str).str.lower().apply(lambda x: any(k in x.lower() for k in allowed_sub_keywords))]
    if not df_acad_all.empty and not df_acad_all[score_col].dropna().empty:
      sub_radar_df = df_acad_all.groupby("Sub bab")[score_col].mean().reset_index()
      sub_radar_df.columns = ["Aspek", "Nilai"]
      
      fig_radar_dash = px.line_polar(sub_radar_df, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100])
      fig_radar_dash.update_traces(fill="toself", line_color="#be185d", marker_color="#fb7185", fillcolor="rgba(190, 24, 93, 0.2)", text=sub_radar_df["Nilai"].apply(lambda x: f"{x:.1f}"), mode="lines+markers+text")
      fig_radar_dash.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
      st.plotly_chart(fig_radar_dash, use_container_width=True)
    else:
      st.info("Belum ada data sub tes akademik dengan kata kunci (言葉、文法、漢字、聴解、読解、読む、書く) yang tercatat.")

    st.markdown("---")

    # 3. ATTITUDE SISWA BERDASARKAN JUMLAH SISWA (PREDIKAT A, B, C, D — MENGIKUTI FILTER `df_v`)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>3. 🌟 Attitude / Sikap Siswa Berdasarkan Jumlah Siswa (Predikat A, B, C, D)</div>", unsafe_allow_html=True)
    
    attitude_cols = [c for c in ["Disiplin", "Sopan santun", "Kebersihan (5S)", "Kerjasama"] if c in df_v.columns]
    if attitude_cols and "Nama" in df_v.columns:
      student_att_grades = []
      for name_siswa, group in df_v.groupby("Nama"):
        grades_list = []
        for col in attitude_cols:
          val_series = group[col].dropna()
          if not val_series.empty:
            val = val_series.iloc[-1]
            val_str = str(val).strip().upper()
            if val_str in ["A", "B", "C", "D"]:
              grades_list.append(val_str)
            else:
              vnum = huruf_ke_angka(val)
              grades_list.append(angka_ke_abjad(vnum))
        
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
          st.markdown("##### Distribusi Berdasarkan Jumlah Siswa:")
          for _, row in att_series.iterrows():
            st.markdown(f"- **Predikat {row['Predikat']}**: **{row['Jumlah Siswa']} siswa** ({row['Persentase']:.1f}%)")
      else:
        st.info("Belum ada data nilai predikat sikap per siswa yang tercatat.")
    else:
      st.info("Kolom sikap atau nama siswa belum terdeteksi di data sheets.")

    st.markdown("---")

    # 4. SKILL / KEMAMPUAN FISIK SISWA
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>4. 🏃 Skill / Kemampuan Fisik Siswa</div>", unsafe_allow_html=True)
    
    fisik_keywords = ["lari", "push", "sit", "squat", "plank", "farmer", "beban", "fisik", "体力"]
    df_fisik_all = df_v[df_v["Sub bab"].astype(str).str.lower().apply(lambda x: any(k in x.lower() for k in fisik_keywords))]
    
    if df_fisik_all.empty:
      skip_cols_check = ["Tanggal", "Kelas", "NIS", "NIS Siswa", "Nama", "Jenis Kelamin", "Program", "Bab", "Sub bab", "Sensei", "Keterangan", "Disiplin", "Sopan santun", "Kebersihan (5S)", "Kerjasama", "Pos Test", "Safety", "Persiapan kerja", "Penggunaan alat", "Teknik kerja", "Komunikasi tim", "Sikap kerja"]
      potential_fisik_cols = [c for c in df_v.columns if c not in skip_cols_check and pd.api.types.is_numeric_dtype(df_v[c])]
      if potential_fisik_cols:
        fisik_summary = df_v[potential_fisik_cols].mean().reset_index()
        fisik_summary.columns = ["Item Tes Fisik", "Rata-rata Nilai"]
      else:
        fisik_summary = pd.DataFrame(columns=["Item Tes Fisik", "Rata-rata Nilai"])
    else:
      fisik_summary = df_fisik_all.groupby("Sub bab")[score_col].mean().reset_index()
      fisik_summary.columns = ["Item Tes Fisik", "Rata-rata Nilai"]

    if not fisik_summary.empty:
      fig_skil = px.bar(fisik_summary, x="Item Tes Fisik", y="Rata-rata Nilai", text="Rata-rata Nilai", color="Rata-rata Nilai", color_continuous_scale="Purples", range_y=[0, 105])
      fig_skil.update_traces(texttemplate='%{text:.1f}', textposition='outside')
      fig_skil.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-15)
      st.plotly_chart(fig_skil, use_container_width=True)
    else:
      st.info("Data rekapitulasi tes fisik belum tersedia.")

    st.markdown("---")

    # 5. KEMAMPUAN SKILL SISWA (GRAFIK RADAR)
    st.markdown("<div style='font-size:16px; font-weight:700; color:#be185d; margin-bottom:4px;'>5. 🛠️ Kemampuan Skill Siswa (Grafik Radar / Polar Chart)</div>", unsafe_allow_html=True)
    
    skill_cols_target = ["Safety", "Persiapan kerja", "Penggunaan alat", "Teknik kerja", "Komunikasi tim", "Sikap kerja"]
    found_skill_cols = [c for c in skill_cols_target if c in df_v.columns]

    if found_skill_cols:
      skill_data_list = []
      for sc in found_skill_cols:
        numeric_vals = []
        for val in df_v[sc].dropna():
          val_str = str(val).strip().upper()
          if val_str in ["A", "B", "C", "D"]:
            numeric_vals.append(huruf_ke_angka(val_str))
          else:
            try:
              numeric_vals.append(float(val))
            except:
              pass
        avg_sc = sum(numeric_vals) / len(numeric_vals) if numeric_vals else 0.0
        skill_data_list.append({"Aspek Skill": sc, "Nilai": avg_sc})

      df_skill_summary = pd.DataFrame(skill_data_list)
      if not df_skill_summary.empty:
        fig_skill_radar = px.line_polar(df_skill_summary, r="Nilai", theta="Aspek Skill", line_close=True, range_r=[0, 100])
        fig_skill_radar.update_traces(fill="toself", line_color="#0d9488", marker_color="#14b8a6", fillcolor="rgba(13, 148, 136, 0.2)", text=df_skill_summary["Nilai"].apply(lambda x: f"{x:.1f}"), mode="lines+markers+text")
        fig_skill_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_skill_radar, use_container_width=True)
      else:
        st.info("Data nilai pada aspek skill belum berisi angka/huruf valid.")
    else:
      st.info("Kolom skill (Safety, Persiapan kerja, Penggunaan alat, Teknik kerja, Komunikasi tim, Sikap kerja) belum terdeteksi di Sheets utama.")

# ================= MENU 2: INPUT NILAI =================
elif menu == "✍️ Input":
  st.markdown("<div class='main-heading'>FORM INPUT NILAI & KOMPETENSI</div>", unsafe_allow_html=True)
  
  raw_senseis = df["Sensei"].dropna().astype(str).unique().tolist() if "Sensei" in df.columns and not df.empty else ["Sensei A"]
  existing_senseis = [s for s in raw_senseis if s.strip().upper() != "REXSY"]
  if not existing_senseis:
    existing_senseis = ["Sensei A"]

  with st.form("form_in", clear_on_submit=True):
    tanggal = st.date_input("Tanggal Penilaian")
    kelas = st.selectbox("Kelas", ["JFT", "N5L1", "N5L2", "N4L1", "N4L2", "PCL"])
    program = st.selectbox("Program", ["Magang", "Reguler"])
    nis_siswa = st.text_input("NIS Siswa")
    nama_siswa = st.text_input("Nama Lengkap Peserta")
    jk_siswa = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    bab = st.text_input("Bab / Materi")
    
    kategori_input = st.selectbox("Kategori Penilaian", ["Akademik (Bahasa)", "Fisik (体力評価)", "Sikap & Karakter (生活態度)", "Skill Kerja (実習スキル)"])
    
    if kategori_input == "Akademik (Bahasa)":
      sub_bab = st.selectbox("Mata Pelajaran Bahasa", [
          "Huruf & Kosakata (文字・語彙)", 
          "Tata Bahasa (文法)", 
          "Membaca (読解)", 
          "Mendengar (聴解)", 
          "Berbicara (会話)",
          "Kotoba", 
          "Kanji"
      ])
    elif kategori_input == "Fisik (体力評価)":
      sub_bab = st.selectbox("Mata Pelajaran Fisik", [
          "LARI (3KM 15MENIT)", 
          "PUSH UP (55X 1MENIT)", 
          "SIT UP (60X1MENIT)", 
          "SQUAT (70X1MENIT)", 
          "PLANK (4MENIT)", 
          "FARMER WALK (25kg, 30 METER)", 
          "ANGKAT BEBAN (35kg, 50X)"
      ])
    elif kategori_input == "Sikap & Karakter (生活態度)":
      sub_bab = st.selectbox("Aspek Sikap", [
          "Disiplin", 
          "Sopan santun", 
          "Kebersihan (5S)", 
          "Kerjasama"
      ])
    else:
      sub_bab = st.selectbox("Aspek Skill Kerja", [
          "Safety", 
          "Persiapan kerja", 
          "Penggunaan alat", 
          "Teknik kerja", 
          "Komunikasi tim", 
          "Sikap kerja"
      ])

    sensei = st.selectbox("Nama Sensei / Pengajar", existing_senseis)
    pos_test = st.number_input("Nilai / Hasil Tes", 0.0, 200.0, 80.0, step=0.1)
    keterangan = st.text_area("Keterangan / Catatan Evaluasi")

    if st.form_submit_button("💾 SIMPAN DATA KE GOOGLE SHEETS", use_container_width=True):
      if nama_siswa.strip() == "":
        st.error("⚠️ Nama lengkap peserta wajib diisi!")
      else:
        new_row_dict = {
            "Tanggal": str(tanggal),
            "Kelas": kelas,
            "NIS": nis_siswa.strip(),
            "Nama": nama_siswa,
            "Jenis Kelamin": jk_siswa,
            "Program": program,
            "Bab": bab,
            "Sub bab": sub_bab,
            "Sensei": sensei,
            "Pos Test": pos_test,
            "Keterangan": keterangan,
        }
        if save_row_to_sheets(new_row_dict):
          st.success("🎉 Data berhasil disimpan secara realtime!")
          st.rerun()

# ================= MENU 3: RAPORT SISWA & PREVIEW CETAK (DIKUNCI KETAT) =================
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

        def get_sub_val(keywords):
          sub_df = df_per[df_per["Sub bab"].astype(str).str.lower().apply(lambda x: any(k in x for k in keywords))]
          if not sub_df.empty and not sub_df["Pos Test"].dropna().empty:
            return sub_df["Pos Test"].mean()
          sub_df_all = df_siswa[df_siswa["Sub bab"].astype(str).str.lower().apply(lambda x: any(k in x for k in keywords))]
          if not sub_df_all.empty and not sub_df_all["Pos Test"].dropna().empty:
            return sub_df_all["Pos Test"].mean()
          return 0.0

        val_kotoba = get_sub_val(["kotoba", "kosakata", "言葉", "語彙"])
        val_kanji = get_sub_val(["kanji", "漢字"])
        val_hk_direct = get_sub_val(["huruf & kosakata", "文字", "vocabulary"])
        
        valid_kanji_kotoba = [v for v in [val_kotoba, val_kanji] if v > 0]
        if len(valid_kanji_kotoba) > 0:
          val_hk = sum(valid_kanji_kotoba) / len(valid_kanji_kotoba)
        elif val_hk_direct > 0:
          val_hk = val_hk_direct
        else:
          val_hk = 0.0

        locked_akad_subs = [
            ("Huruf & Kosakata (文字・語彙)", val_hk),
            ("Tata Bahasa (文法)", get_sub_val(["tata bahasa", "bunpou", "文法"])),
            ("Membaca (読解)", get_sub_val(["membaca", "dokkai", "読解"])),
            ("Mendengar (聴解)", get_sub_val(["mendengar", "choukai", "聴解"])),
            ("Berbicara (会話)", get_sub_val(["berbicara", "kaiwa", "会話"]))
        ]

        list_sikap_config = [
            {"title": "Disiplin", "val_cols": ["Disiplin"]},
            {"title": "Sopan santun", "val_cols": ["Sopan santun"]},
            {"title": "Kebersihan (5S)", "val_cols": ["Kebersihan (5S)"]},
            {"title": "Kerjasama", "val_cols": ["Kerjasama"]}
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
          if pd.isna(vnum): vnum = 0.0
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
          raw_val = None

          for col in df_siswa.columns:
            if any(vc.lower() == col.strip().lower() for vc in cfg["val_cols"]):
              c_vals = df_siswa[col].dropna()
              if not c_vals.empty:
                raw_val = c_vals.iloc[-1]
              break

          if raw_val is not None and str(raw_val).strip() != "":
            huruf = str(raw_val).strip().upper()
            if huruf not in ["A", "B", "C", "D"]:
              vnum = huruf_ke_angka(raw_val)
              huruf = angka_ke_abjad(vnum)
            vnum = huruf_ke_angka(huruf)
          else:
            vnum = 85.0
            huruf = "A"

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
          vnum = 0.0
          
          matched_col = None
          for col in df_siswa.columns:
            col_l = col.strip().lower()
            if any(k in col_l for k in keywords):
              matched_col = col
              break

          if matched_col and not df_siswa[matched_col].dropna().empty:
            raw_f = df_siswa[matched_col].dropna().iloc[-1]
            vnum = huruf_ke_angka(raw_f)
            if pd.isna(vnum): vnum = 0.0

          huruf = angka_ke_abjad(vnum)
          ket = get_fisik_keterangan(sub_title, vnum)

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

        st.markdown("<br><h4>📊 Grafik Kompetensi Akademik Siswa</h4>", unsafe_allow_html=True)
        df_radar_plot = pd.DataFrame(locked_akad_subs, columns=["Aspek", "Nilai"])
        if not df_radar_plot.empty:
          fig_radar_sis = px.line_polar(df_radar_plot, r="Nilai", theta="Aspek", line_close=True, range_r=[0, 100])
          fig_radar_sis.update_traces(fill="toself", line_color="#be185d", marker_color="#fb7185", fillcolor="rgba(190, 24, 93, 0.2)", text=df_radar_plot["Nilai"].apply(lambda x: f"{x:.1f}"), mode="lines+markers+text")
          fig_radar_sis.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
          st.plotly_chart(fig_radar_sis, use_container_width=True)

        st.markdown("<br><h4>📊 Grafik Kemampuan Fisik Siswa (Kolom Vertikal)</h4>", unsafe_allow_html=True)
        df_fisik_plot = pd.DataFrame(pdf_fisik_data)[["sub", "val"]]
        df_fisik_plot.columns = ["Item Fisik", "Nilai"]
        if not df_fisik_plot.empty:
          fig_bar_sis = px.bar(df_fisik_plot, x="Item Fisik", y="Nilai", text="Nilai", color="Nilai", color_continuous_scale="Reds", range_y=[0, 105])
          fig_bar_sis.update_traces(texttemplate='%{text:.1f}', textposition='outside')
          fig_bar_sis.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-20)
          st.plotly_chart(fig_bar_sis, use_container_width=True)

        pdf_bytes = generate_pdf_2_pages(
            nama=pilih_nama,
            nis=nis_val,
            kelas=kelas_val,
            jk=jk_val,
            program_val=program_val,
            periode=periode_str,
            akad_data=pdf_akad_data,
            sikap_data=pdf_sikap_data,
            fisik_data=pdf_fisik_data,
            hadir_vals=[hadir_val, izin_val, alpa_val],
            catatan_akad=catatan_umum,
            catatan_fisik=catatan_fisik,
            kesimpulan=kesimpulan
        )

        st.download_button(
            label=f"📥 DOWNLOAD RAPORT RESMI PDF (2 HALAMAN) - {pilih_nama} (NIS: {nis_val})",
            data=pdf_bytes,
            file_name=f"Raport_Resmi_{pilih_nama.replace(' ', '_')}_{nis_val}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ================= MENU 4: DATABASE =================
elif menu == "📂 Database":
  st.markdown("<div class='main-heading'>DATABASE PESERTA LPK YUTAKA</div>", unsafe_allow_html=True)
  if not df.empty:
    st.markdown("<p style='font-size:12px; color:#64748b;'>Menampilkan seluruh rekam data nilai dan NIS dari Google Sheets utama.</p>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

# ================= MENU 5: UPLOAD / UNDUH =================
elif menu == "📤 Upload/Unduh":
  st.markdown("<div class='main-heading'>UPLOAD & DOWNLOAD DATA</div>", unsafe_allow_html=True)
  if not df.empty:
    st.download_button(
        label="📥 DOWNLOAD REKAP LENGKAP (EXCEL) DENGAN NIS",
        data=to_excel_bytes(df),
        file_name="laporan_lpk_yutaka_lengkap_dengan_nis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )