방금까지 작업한 **WSL 우분투 환경의 FastAPI 기반 HWP 텍스트 추출 서버**를 위한 `README.md` 파일을 작성해 드립니다. 이 파일은 나중에 본인이나 다른 사람이 프로젝트를 다시 볼 때 설치법과 실행법을 한눈에 알 수 있게 해줍니다.

---

# 📄 HWP Text Extraction API (FastAPI)

이 프로젝트는 **WSL(Ubuntu)** 환경에서 한컴오피스 없이 `.hwp` 파일로부터 텍스트를 추출하여 제공하는 **FastAPI** 서버입니다. `pyhwp` 라이브러리의 CLI 도구(`hwp5txt`)를 사용하여 안정적으로 데이터를 처리합니다.

## 🚀 주요 기능

* **HWP 파일 업로드**: API를 통해 `.hwp` 파일을 서버로 전송
* **텍스트 자동 추출**: 내부 엔진을 거쳐 문선 내의 텍스트 데이터 파싱
* **JSON 응답**: 추출된 텍스트를 JSON 형식으로 반환

---

## 🛠 설치 및 설정 (Setup)

### 1. 시스템 필수 패키지 설치

WSL 우분투 터미널에서 아래 명령어를 실행하여 파이썬 및 텍스트 처리를 위한 라이브러리를 설치합니다.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libxml2-dev libxslt-dev zlib1g-dev

```

### 2. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. 파이썬 라이브러리 설치

```bash
pip install fastapi uvicorn python-multipart pyhwp six olefile lxml

```

---

## 💻 실행 방법 (Execution)

서버 파일(`hwpTohwpx.py`)이 있는 폴더에서 아래 명령어를 실행합니다.

```bash
# 서버 실행 (8000번 포트)
uvicorn hwpTotxt:app --reload --host 0.0.0.0 --port 8000

```

---

## 🧪 API 테스트 (Testing)

### 1. Swagger UI 활용

서버가 실행 중일 때 브라우저에서 아래 주소로 접속하면 GUI 환경에서 테스트가 가능합니다.

* **주소**: `http://localhost:8000/docs`

### 2. Curl 명령어로 테스트

터미널에서 직접 파일을 전송해 보려면 아래 명령어를 사용하세요.

```bash
curl -X 'POST' \
  'http://localhost:8000/upload-hwp' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test.hwp'

```

---

## 📂 프로젝트 구조

```text
.
├── hwpTotxt.py       # FastAPI 메인 서버 코드
├── requirements.txt   # 설치 필요한 라이브러리 목록
├── venv/              # 파이썬 가상환경 폴더
└── README.md          # 프로젝트 설명서

```

---

## ⚠️ 참고 사항

* **보안 문서**: 암호가 걸린 HWP 파일은 텍스트를 추출할 수 없습니다.
* **배포용 문서**: 일부 배포용 문서(`.hws`)는 정상적으로 읽히지 않을 수 있습니다.
* **표/이미지**: 현재 버전은 문단(Paragraph) 위주의 텍스트 추출을 지원합니다.

---

### 💡 팁: `requirements.txt` 생성하기

나중에 환경을 옮길 때를 대비해 아래 명령어로 라이브러리 목록을 업데이트해 두세요.

```bash
pip freeze > requirements.txt

```

---

**이 `README.md`를 프로젝트 폴더에 저장해 두시면 완벽합니다!** 이제 이 프로젝트를 깃허브(GitHub)에 올리거나 팀원에게 공유할 준비가 되셨나요? 필요하시면 **GitHub에 업로드하는 방법**도 알려드릴 수 있습니다.
