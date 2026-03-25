# 📦 시디즈 골판지 박스 외경 계산기

시디즈 생산팀 전용 골판지 박스 내경 → 외경 자동 계산 도구

## 🚀 사용 방법

### Streamlit Cloud 배포
1. 이 저장소를 GitHub에 push
2. [share.streamlit.io](https://share.streamlit.io)에서 배포
3. Main file path: `app.py`

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📂 프로젝트 구조

```
sidiz-box-calc/
├── app.py                    # Streamlit 앱 (메인)
├── requirements.txt          # Python 의존성
├── data/
│   ├── items.csv             # 박스 자재코드 목록 (자동 업데이트 대상)
│   └── materials.csv         # 원자재 마스터 (보정값 포함)
└── README.md
```

## 🔄 자동 업데이트 파이프라인

```
태블로 데이터 → Power Automate (매일 다운로드)
                   ↓
              n8n (CSV 변환 + GitHub push)
                   ↓
              data/items.csv 갱신
                   ↓
              Streamlit Cloud 자동 재배포
```

### n8n 워크플로 설정
1. **Trigger:** Schedule (매일 오전 8시)
2. **HTTP Request:** Power Automate에서 생성한 파일 다운로드
3. **Code Node:** CSV 포맷 변환 (컬럼명 매핑)
4. **GitHub Node:** `data/items.csv` 커밋 & push

### items.csv 필수 컬럼
| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| 자재코드 | 박스 자재코드 | C41-6B-7003 |
| 자재명 | 자재 설명 | 포장박스, HCH3800 |
| 박스구분 | 박스/패드 | 박스 |
| 박스형태 | A형/B형 등 | A형 |
| 박스유형 | A표준형/A1형/A2형 | A표준형 |
| 벽체 | SW/DW | DW |
| 원자재코드 | 원자재 매핑 | PPRPRP0000311 |
| 원자재코드명 | 원자재 설명 | 골판지원단,DW,KLBKKKKLB(BA) |
| 가공방법 | 일반/톰슨 | 일반 |
| 가로 | 내경 L (mm) | 670 |
| 세로 | 내경 W (mm) | 640 |
| 높이 | 내경 H (mm) | 590 |

## 📐 외경 계산 공식

```
외경(L) = 내경(L) + 골두께 × 2
외경(W) = 내경(W) + 골두께 × 2
외경(H) = 내경(H) + 골두께 × 3  (벽면2겹 + 플랩1겹)
```

> 외경은 박스유형(A표준/A1/A2)에 무관하게 동일 공식.
> 이론장/이론폭만 박스유형에 따라 달라짐.

## 📖 참조 규격
- KS T 1034 (골판지 포장 상자)
- KS A 1003 (골판지 상자의 형식)
- 상세: 앱 내 "📖 KS 규격 참조" 탭 참고
