import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="골판지 박스 외경 계산기 | 시디즈 생산팀", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data(ttl=300)
def load_items():
    p = os.path.join(DATA_DIR, "items.csv")
    return pd.read_csv(p, encoding="utf-8-sig") if os.path.exists(p) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_materials():
    p = os.path.join(DATA_DIR, "materials.csv")
    return pd.read_csv(p, encoding="utf-8-sig") if os.path.exists(p) else pd.DataFrame()

items_df = load_items()
mats_df = load_materials()

def get_mat(code):
    r = mats_df[mats_df["원자재코드"] == code]
    return r.iloc[0] if len(r) > 0 else None

def calc_outer(L, W, H, thick):
    return L + thick * 2, W + thick * 2, H + thick * 3

def calc_theo(L, W, H, mat, box_kind, process, box_subtype="A표준형"):
    t, thr = mat["골두께"], mat["소대경계"]
    if box_kind == "패드":
        pc = mat["패드보정_톰슨"] if process == "톰슨" else mat["패드보정_일반"]
        return W + pc, L + pc
    perim = (L + W) * 2
    is_big = perim >= thr
    if process == "톰슨":
        cL = mat["톰슨장보정_대"] if is_big else mat["톰슨장보정_소"]
        cW = mat["폭보정_톰슨"]
    else:
        cL = mat["일반장보정_대"] if is_big else mat["일반장보정_소"]
        cW = mat["폭보정_일반"]
    theo_L = perim + cL
    if box_subtype == "A1형":
        theo_W = H + W / 2 + cW
    elif box_subtype == "A2형":
        theo_W = H + W * 2 + cW
    else:
        theo_W = H + W + cW
    return theo_L, theo_W

st.markdown("""
<style>
.block-container{padding:1.5rem 2rem 3rem;max-width:1200px;}
.app-header{text-align:center;padding:1rem 0 .6rem;}
.app-header h1{font-size:1.6rem;font-weight:800;color:#1e293b;margin:0;}
.app-header p{font-size:.78rem;color:#64748b;margin-top:.15rem;}
.app-header .badge{display:inline-block;background:#eff6ff;color:#3b82f6;font-size:.62rem;font-weight:600;padding:2px 10px;border-radius:12px;margin-top:.25rem;}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:.7rem;}
.card-dark{background:#f8fafc;}
.card-title{font-size:.75rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.7rem;display:flex;align-items:center;gap:6px;}
.card-title .icon{width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;}
.result-box{background:linear-gradient(135deg,#f0fdf4,#ecfdf5);border:2px solid #86efac;border-radius:12px;padding:1.1rem;text-align:center;}
.result-box .label{font-size:.68rem;font-weight:600;color:#16a34a;text-transform:uppercase;letter-spacing:1px;margin-bottom:.25rem;}
.result-box .value{font-size:1.7rem;font-weight:800;color:#15803d;letter-spacing:-.5px;}
.result-box .sub{font-size:.62rem;color:#6b7280;margin-top:.15rem;}
.input-box{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:1.1rem;text-align:center;}
.input-box .label{font-size:.68rem;font-weight:600;color:#3b82f6;text-transform:uppercase;letter-spacing:1px;margin-bottom:.25rem;}
.input-box .value{font-size:1.35rem;font-weight:700;color:#1e293b;}
.detail-table{width:100%;border-collapse:collapse;font-size:.78rem;margin-top:.3rem;}
.detail-table th{background:#f1f5f9;color:#475569;font-weight:600;font-size:.68rem;text-transform:uppercase;letter-spacing:.5px;padding:7px 12px;text-align:left;border-bottom:2px solid #e2e8f0;}
.detail-table td{padding:7px 12px;border-bottom:1px solid #f1f5f9;color:#334155;}
.detail-table .num{font-family:'Consolas',monospace;font-weight:600;}
.detail-table .highlight{color:#16a34a;font-weight:700;}
.detail-table .correction{color:#3b82f6;font-weight:600;}
.chip{display:inline-block;padding:2px 9px;border-radius:6px;font-size:.68rem;font-weight:600;margin-right:3px;}
.chip-blue{background:#eff6ff;color:#2563eb;}.chip-green{background:#f0fdf4;color:#16a34a;}
.chip-amber{background:#fffbeb;color:#d97706;}.chip-gray{background:#f1f5f9;color:#475569;}
.section-label{font-size:.68rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1.5px;margin:1rem 0 .5rem;padding-bottom:.25rem;border-bottom:1px solid #e2e8f0;}
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px 16px;font-size:.75rem;}
.info-grid .lbl{color:#94a3b8;font-size:.65rem;}.info-grid .val{color:#1e293b;font-weight:600;margin-bottom:5px;}
.formula-block{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;font-family:'Consolas',monospace;font-size:.75rem;color:#475569;line-height:1.8;}
.formula-block .hi{color:#2563eb;font-weight:600;}.formula-block .result{color:#16a34a;font-weight:700;}
div[data-testid="stMetric"]{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;}
div[data-testid="stMetric"] label{color:#64748b!important;font-size:.68rem!important;text-transform:uppercase;letter-spacing:.8px;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{font-size:1.2rem!important;color:#1e293b!important;}
button[data-baseweb="tab"]{font-size:.82rem!important;font-weight:600!important;}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-header"><h1>📦 골판지 박스 내경 → 외경 계산기</h1><p>시디즈 생산팀 · 박스 자재코드 또는 원자재코드로 외경 즉시 계산</p><span class="badge">자재코드 {c}개 · 원자재 {m}종</span></div>'.format(c=f"{len(items_df):,}", m=len(mats_df)), unsafe_allow_html=True)
st.markdown("")

def render_result(L, W, H, t, mat, box_kind=None, process=None, subtype=None):
    oL, oW, oH = calc_outer(L, W, H, t)
    st.markdown('<div class="section-label">📊 계산 결과</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="input-box"><div class="label">내경 사이즈</div><div class="value">{L:.0f} × {W:.0f} × {H:.0f}</div><div style="font-size:.6rem;color:#94a3b8;margin-top:2px;">L × W × H (mm)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="result-box"><div class="label">외경 사이즈</div><div class="value">{oL:.1f} × {oW:.1f} × {oH:.1f}</div><div class="sub">L × W × H (mm) · {mat["골종"]}골 {t}mm</div></div>', unsafe_allow_html=True)
    st.markdown("")
    st.markdown(f'<div class="section-label">📐 상세 계산 근거</div>', unsafe_allow_html=True)
    st.markdown(f"""<table class="detail-table"><thead><tr><th>항목</th><th>내경(mm)</th><th>골두께 보정</th><th>외경(mm)</th></tr></thead><tbody>
    <tr><td>가로(L)</td><td class="num">{L:.0f}</td><td class="correction">+{t*2:.1f} <span style="color:#94a3b8;font-weight:400">(t×2)</span></td><td class="num highlight">{oL:.1f}</td></tr>
    <tr><td>세로(W)</td><td class="num">{W:.0f}</td><td class="correction">+{t*2:.1f} <span style="color:#94a3b8;font-weight:400">(t×2)</span></td><td class="num highlight">{oW:.1f}</td></tr>
    <tr><td>높이(H)</td><td class="num">{H:.0f}</td><td class="correction">+{t*3:.1f} <span style="color:#94a3b8;font-weight:400">(t×3 벽면2+플랩1)</span></td><td class="num highlight">{oH:.1f}</td></tr>
    </tbody></table>""", unsafe_allow_html=True)
    st.markdown("")
    st.markdown(f'<div class="formula-block"><span class="hi">외경(L)</span> = {L:.0f} + {t}×2 = <span class="result">{oL:.1f}</span> · <span class="hi">외경(W)</span> = {W:.0f} + {t}×2 = <span class="result">{oW:.1f}</span> · <span class="hi">외경(H)</span> = {H:.0f} + {t}×3 = <span class="result">{oH:.1f}</span> <span style="color:#94a3b8;">← 벽면2+플랩1</span></div>', unsafe_allow_html=True)
    st.markdown("")
    sum3 = (oL + oW + oH) / 10
    if sum3 > 160: st.error(f"⚠️ **3변합 {sum3:.1f}cm** — 택배 과대 사이즈")
    elif sum3 > 120: st.warning(f"⚠️ **3변합 {sum3:.1f}cm** — 택배 대형 사이즈")
    else: st.success(f"✅ **3변합 {sum3:.1f}cm** — 택배 규격 이내")
    if box_kind and process:
        with st.expander("📐 이론장/이론폭 (전개 사이즈)"):
            theo_L, theo_W = calc_theo(L, W, H, mat, box_kind, process, subtype or "A표준형")
            tc1, tc2 = st.columns(2)
            tc1.metric("이론장", f"{theo_L:.0f} mm")
            tc2.metric("이론폭", f"{theo_W:.0f} mm")
            if subtype == "A1형": st.caption("⚠️ A1형: 플랩 미접합 → 이론폭 = H + W/2 + 보정")
            elif subtype == "A2형": st.caption("⚠️ A2형: 오버플랩 → 이론폭 = H + W×2 + 보정")
            else: st.caption("A표준형(0201): 플랩 중심 접합 → 이론폭 = H + W + 보정")

tab1, tab2, tab3, tab4 = st.tabs(["🔍  박스 자재코드로 계산", "📐  원자재코드 + 수동입력", "🏭  원자재 마스터 관리", "📖  KS 규격 참조"])

with tab1:
    st.markdown('<div class="card"><div class="card-title"><div class="icon" style="background:#eff6ff;color:#3b82f6;">🔍</div> 박스 자재코드 검색</div><p style="font-size:.75rem;color:#64748b;margin:0;"><strong>박스 자재코드</strong>는 시디즈 포장 자재 관리 코드입니다 (예: <code>C41-6B-7003</code>). 원자재코드(<code>PPRPRP...</code>)와는 다릅니다.</p></div>', unsafe_allow_html=True)
    if len(items_df) > 0:
        search = st.text_input("검색", placeholder="박스 자재코드 또는 자재명 입력 (예: C41-6B, T50, 포장박스)", label_visibility="collapsed", key="item_search")
        if search and len(search) >= 2:
            mask = items_df["자재코드"].astype(str).str.upper().str.contains(search.upper(), na=False) | items_df["자재명"].astype(str).str.upper().str.contains(search.upper(), na=False)
            results = items_df[mask].head(30)
            if len(results) > 0:
                selected = st.selectbox(f"검색 결과 ({len(results)}건)", results["자재코드"].tolist(), format_func=lambda x: f"{x}  —  {items_df[items_df['자재코드']==x]['자재명'].values[0]}")
                item = items_df[items_df["자재코드"] == selected].iloc[0]
                mat = get_mat(item["원자재코드"])
                if mat is not None:
                    t = mat["골두께"]
                    L, W, H = float(item["가로"] or 0), float(item["세로"] or 0), float(item["높이"] or 0)
                    st.markdown(f'<div class="card card-dark"><div class="card-title"><div class="icon" style="background:#f0fdf4;color:#16a34a;">📋</div> 자재 정보</div><div class="info-grid"><div><span class="lbl">자재명</span><div class="val">{item["자재명"]}</div></div><div><span class="lbl">박스 자재코드</span><div class="val" style="font-family:monospace;">{item["자재코드"]}</div></div><div><span class="lbl">구분</span><div class="val"><span class="chip chip-gray">{item["박스구분"]}</span><span class="chip chip-gray">{item["박스형태"]}</span><span class="chip chip-gray">{item["박스유형"]}</span></div></div><div><span class="lbl">가공방법</span><div class="val"><span class="chip chip-amber">{item["가공방법"]}</span></div></div><div><span class="lbl">원자재코드</span><div class="val" style="font-family:monospace;color:#3b82f6;">{item["원자재코드"]}</div></div><div><span class="lbl">벽체/골종/두께</span><div class="val"><span class="chip chip-blue">{mat["벽체"]}</span><span class="chip chip-green">{mat["골종"]}골 {t}mm</span></div></div><div><span class="lbl">내경(L×W×H)</span><div class="val">{L:.0f} × {W:.0f} × {H:.0f} mm</div></div><div><span class="lbl">라이너</span><div class="val">{mat["라이너"]}</div></div></div></div>', unsafe_allow_html=True)
                    if L > 0 or W > 0 or H > 0:
                        render_result(L, W, H, t, mat, box_kind=item["박스구분"], process=item["가공방법"], subtype=str(item["박스유형"]))
                else:
                    st.error(f"원자재코드 `{item['원자재코드']}`가 마스터에 없습니다.")
            else:
                st.info("🔍 검색 결과 없음")

with tab2:
    st.markdown('<div class="card"><div class="card-title"><div class="icon" style="background:#faf5ff;color:#8b5cf6;">📐</div> 원자재코드 + 내경 직접 입력</div><p style="font-size:.75rem;color:#64748b;margin:0;">원자재코드를 선택하고 내경만 입력하면 <strong>외경이 즉시 계산</strong>됩니다. 박스형태·가공방법 없이도 외경 계산 가능.</p></div>', unsafe_allow_html=True)
    if len(mats_df) > 0:
        mat_opts = mats_df["원자재코드"].tolist()
        mat_lbls = {r["원자재코드"]: f'{r["원자재코드"]}  —  {r["벽체"]} {r["골종"]}골 {r["골두께"]}mm  ({r["라이너"]})' for _, r in mats_df.iterrows()}
        sel = st.selectbox("원자재코드", mat_opts, format_func=lambda x: mat_lbls.get(x, x), help="골판지 원자재 코드 선택 → 골종·두께 자동 적용")
        mat = get_mat(sel)
        if mat is not None:
            t = mat["골두께"]
            st.markdown(f'<div style="display:flex;gap:5px;margin:.3rem 0 .8rem;"><span class="chip chip-blue">{mat["벽체"]}</span><span class="chip chip-green">{mat["골종"]}골</span><span class="chip chip-amber">두께 {t}mm</span><span class="chip chip-gray">{mat["라이너"]}</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">📏 내경 사이즈 입력</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            L = c1.number_input("가로(L)", min_value=0, step=10, key="mL", help="mm")
            W = c2.number_input("세로(W)", min_value=0, step=10, key="mW", help="mm")
            H = c3.number_input("높이(H)", min_value=0, step=10, key="mH", help="mm")
            if L > 0 or W > 0 or H > 0:
                render_result(L, W, H, t, mat)
                with st.expander("📐 이론장/이론폭도 계산 (선택)"):
                    ec1, ec2 = st.columns(2)
                    bk = ec1.radio("박스 구분", ["박스", "패드"], horizontal=True, key="mk")
                    pr = ec2.radio("가공방법", ["일반", "톰슨"], horizontal=True, key="mp")
                    sub = st.radio("박스유형", ["A표준형", "A1형", "A2형"], horizontal=True, help="날개 형태", key="ms") if bk == "박스" else "A표준형"
                    tL, tW = calc_theo(L, W, H, mat, bk, pr, sub)
                    tc1, tc2 = st.columns(2)
                    tc1.metric("이론장", f"{tL:.0f} mm")
                    tc2.metric("이론폭", f"{tW:.0f} mm")
            else:
                st.markdown('<div style="text-align:center;padding:1.5rem;color:#94a3b8;font-size:.82rem;">⬆️ 내경 사이즈를 입력하면 외경이 즉시 계산됩니다</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card"><div class="card-title"><div class="icon" style="background:#fef3c7;color:#d97706;">🏭</div> 원자재 마스터 관리</div><p style="font-size:.75rem;color:#64748b;margin:0;">원자재 추가·수정·삭제 후 <strong>저장</strong> 버튼으로 반영. <span style="color:#3b82f6;">n8n → GitHub 자동 배포 시 함께 배포.</span></p></div>', unsafe_allow_html=True)
    if len(mats_df) > 0:
        edited = st.data_editor(mats_df, num_rows="dynamic", use_container_width=True, key="me")
        c1, c2, c3 = st.columns([1, 1, 3])
        if c1.button("💾 저장", type="primary", use_container_width=True):
            edited.to_csv(os.path.join(DATA_DIR, "materials.csv"), index=False, encoding="utf-8-sig")
            st.cache_data.clear()
            st.success("✅ 저장 완료!")
            st.rerun()
        c2.download_button("📥 CSV", mats_df.to_csv(index=False, encoding="utf-8-sig"), "materials.csv", "text/csv", use_container_width=True)

with tab4:
    st.markdown('<div class="card"><div class="card-title"><div class="icon" style="background:#fce7f3;color:#db2777;">📖</div> KS 규격 참조 문서</div><p style="font-size:.75rem;color:#64748b;margin:0;">FP-KS-REF-001 · Rev.1.0 · 2026-03-24 · 시디즈 생산팀 · 실데이터 1,813건 기반</p></div>', unsafe_allow_html=True)
    st.markdown("#### 1. 참조 규격")
    st.dataframe(pd.DataFrame({"규격번호":["KS T 1034","KS A 1003","KS T 1061","KS M 7063","FEFCO/ESBO"],"규격명":["골판지 포장 상자","골판지 상자의 형식","수출용 골판지 상자","골판지 원지","국제 골판지 상자 형식"],"제정/개정":["2019 확인"]*3+["—"]*2,"비고":["치수 허용차","형식 코드","수출 포장","라이너·골심지","국제 표준"]}), use_container_width=True, hide_index=True)
    st.markdown("#### 2. 골종별 두께")
    st.dataframe(pd.DataFrame({"골종":["A골","B골","C골","E골","F골","BA골","BB골","EB골"],"구분":["SW"]*5+["DW"]*3,"골높이(mm)":["4.5~4.8","2.5~2.8","3.5~3.8","1.1~1.4","0.6~0.8","7.0~8.0","5.0~5.6","3.6~4.2"],"두께(mm)":["약5.0","약3.0","약4.0","약1.5","약0.8","약8.0","약6.0","약4.5"],"적용":["~10kg","~5kg","~10kg","~3kg","~1kg","10kg+","8kg+","8kg+"]}), use_container_width=True, hide_index=True)
    st.markdown("#### 3. 외경 공식")
    st.markdown("| 항목 | 계산식 | 비고 |\n|------|--------|------|\n| **외경(L)** | 내경L + 골두께×2 | 좌우 벽면 각 1겹 |\n| **외경(W)** | 내경W + 골두께×2 | 전후 벽면 각 1겹 |\n| **외경(H)** | 내경H + 골두께×3 | 벽면2+플랩1 |\n\n> ✅ 외경은 박스유형(A표준/A1/A2)에 무관하게 동일")
    st.markdown("#### 4. 이론장 보정")
    st.markdown("`이론장 = (L+W)×2 + 보정값`")
    st.dataframe(pd.DataFrame({"벽체":["DW","DW","SW","SW"],"가공":["일반","톰슨","일반","톰슨"],"소형(mm)":["+76","+116","+64","+104"],"대형(mm)":["+116","+156","+104","+144"],"경계":["2,440mm"]*2+["2,500mm"]*2}), use_container_width=True, hide_index=True)
    st.markdown("#### 5. 이론폭 보정 (박스유형별)")
    st.markdown("| 유형 | 공식 | 설명 |\n|------|------|------|\n| **A표준** | H+W+보정 | 플랩 중심접합 |\n| **A1형** | H+W/2+보정 | 플랩 미접합 |\n| **A2형** | H+W×2+보정 | 오버플랩 |")
    st.dataframe(pd.DataFrame({"벽체":["DW","DW","SW","SW"],"가공":["일반","톰슨","일반","톰슨"],"폭보정":["+33","+73","+25","+65"],"N":[713,110,29,17]}), use_container_width=True, hide_index=True)
    st.markdown("#### 6. 패드형")
    st.markdown("`이론장=세로+보정` · `이론폭=가로+보정`")
    st.dataframe(pd.DataFrame({"가공":["톰슨","일반"],"보정":["+40","+20"],"N":[642,162]}), use_container_width=True, hide_index=True)
    st.markdown("#### 7. 이음여유 (KS T 1034)")
    st.markdown("SW: **30mm↑** / DW: **35mm↑** / 허용차: SW ±3mm, DW ±5mm")
    st.divider()
    st.markdown("#### 8. 유지보수")
    st.markdown("- **KS 개정 시:** 이 탭 + 🏭 마스터 갱신\n- **원자재 변경:** 🏭 탭 수정\n- **자재코드 갱신:** 태블로→PA→n8n→GitHub→자동배포")
    st.error("⚠️ KS 개정 시 이 문서 + 마스터를 함께 갱신하세요.")
    st.markdown("#### 9. 개정이력")
    st.dataframe(pd.DataFrame({"Rev":["1.0"],"일자":["2026-03-24"],"내용":["최초 작성. 실데이터 1,813건 기반."],"작성":["시디즈 생산팀"]}), use_container_width=True, hide_index=True)

with st.sidebar:
    st.markdown("### 📦 시디즈 생산팀")
    st.caption("골판지 박스 외경 계산기")
    st.divider()
    st.metric("박스 자재코드", f"{len(items_df):,}개")
    st.metric("원자재 마스터", f"{len(mats_df)}종")
    st.divider()
    st.caption("태블로→PA→n8n→GitHub→Streamlit")
    st.caption("FP-KS-REF-001 Rev.1.0")
