from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from database import get_db, engine, Base
from models import User, CasualtyMain, Insa
import os
import random
import requests
from contextlib import asynccontextmanager

# Pydantic model for request body
class LoginRequest(BaseModel):
    email: str
    password: str

class ReportRequest(BaseModel):
    srvno: str
    lat: float
    lng: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Drop tables to apply schema changes (Development only!)
        # CasualtyMain.__table__.drop(engine, checkfirst=True)
        # Insa.__table__.drop(engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)

        # Verify connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL Database connected successfully!")
        
        with Session(engine) as session:
            # Seed Casualties
            count = session.query(CasualtyMain).count()
            if count == 0:
                print("Seeding Casualties...")
                first_names = ["민수", "지훈", "현우", "준호", "민지", "서연", "지민", "지우", "예준", "도현"]
                last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
                ranks = ["이병", "일병", "상병", "병장", "하사", "중사", "상사", "소위", "중위", "대위", "소령"]
                units = ["제1보병사단", "제3기갑여단", "제5포병여단", "제7특수임무단", "수도방위사령부"]
                
                casualty_items = []
                # Seed 1000 casualties
                for i in range(1000):
                    casualty_items.append(CasualtyMain(
                        srvno=f"24-{100000+i}",
                        nm=f"{random.choice(last_names)}{random.choice(first_names)}",
                        rank=random.choice(ranks),
                        uc=random.choice(units),
                        # Random coordinates around Korea (approx 34-38N, 126-129E)
                        lat=random.uniform(34.0, 38.5),
                        lng=random.uniform(126.0, 129.5)
                    ))
                session.add_all(casualty_items)
                
                # Seed Insa (Personnel) - Overlap some service numbers for valid lookups
                insa_items = []
                print("Seeding Insa Data...")
                # Seed 2000 personnel (some will match casualties, others won't)
                for i in range(2000):
                    insa_items.append(Insa(
                        srvno=f"24-{100000+i}", # Matches casualty srvno range
                        nm=f"{random.choice(last_names)}{random.choice(first_names)}",
                        rank=random.choice(ranks),
                        uc=random.choice(units)
                    ))
                session.add_all(insa_items)
                
                session.commit()
                print("✅ Seeding complete!")



    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    yield
app = FastAPI(lifespan=lifespan)


# Enable CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/casualties")
def get_casualties(db: Session = Depends(get_db)):
    casualties = db.query(CasualtyMain).all()
    return casualties

@app.get("/insa/{srvno}")
def get_insa(srvno: str, db: Session = Depends(get_db)):
    person = db.query(Insa).filter(Insa.srvno == srvno).first()
    if not person:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return person

@app.post("/generate-report")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    # 1. Fetch Personnel Data
    person = db.query(Insa).filter(Insa.srvno == request.srvno).first()
    if not person:
        raise HTTPException(status_code=404, detail="Personnel not found")
    
    # 2. Get Weather (Google Weather API)
    weather_desc = "정보 없음"
    temp_desc = "정보 없음"
    
    # 2. Get Weather
    weather_desc = "정보 없음"
    temp_desc = "정보 없음"
    
    # Strategy 1: Google Weather API (User Provided Key)
    google_success = False
    try:
        api_key = "AIzaSyCD9Ulynn8Kav98eOoBTgbpnz0ymhQVaNo" 
        url = f"https://weather.googleapis.com/v1/currentConditions:lookup?location.latitude={request.lat}&location.longitude={request.lng}&key={api_key}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get('currentConditions', {})
            weather_desc = current.get('condition', "맑음") 
            temp_value = current.get('temperature', {}).get('value')
            if temp_value is not None:
                temp_desc = f"{temp_value}°C"
                google_success = True
        else:
            print(f"Google Weather API Failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Google Weather API Exception: {e}")

    # Strategy 2: Open-Meteo (Free, No Key) - Fallback if Google fails
    if not google_success:
        try:
            print("Falling back to Open-Meteo API...")
            om_url = f"https://api.open-meteo.com/v1/forecast?latitude={request.lat}&longitude={request.lng}&current_weather=true"
            om_response = requests.get(om_url, timeout=5)
            
            if om_response.status_code == 200:
                om_data = om_response.json()
                current_weather_data = om_data.get('current_weather', {})
                
                # Temperature
                temp_val = current_weather_data.get('temperature')
                if temp_val is not None:
                    temp_desc = f"{temp_val}°C"
                
                # Weather Code Mapping (WMO Code)
                wmo_code = current_weather_data.get('weathercode')
                # Simple mapping
                if wmo_code == 0: weather_desc = "맑음"
                elif 1 <= wmo_code <= 3: weather_desc = "구름 많음"
                elif 45 <= wmo_code <= 48: weather_desc = "안개"
                elif 51 <= wmo_code <= 67: weather_desc = "비"
                elif 71 <= wmo_code <= 77: weather_desc = "눈"
                elif 80 <= wmo_code <= 99: weather_desc = "악천후 (비/뇌우)"
                else: weather_desc = "흐림"
                
                print(f"Open-Meteo Success: {weather_desc}, {temp_desc}")
            else:
                print(f"Open-Meteo Failed: {om_response.status_code}")
                # Fallback to Random Mock
                weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
                weather_desc = random.choice(weather_conditions)
                temp_desc = f"{random.randint(-5, 30)}°C"
                
        except Exception as e:
            print(f"Open-Meteo Exception: {e}")
            # Final Fallback
            weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
            weather_desc = random.choice(weather_conditions)
            temp_desc = f"{random.randint(-5, 30)}°C"

    current_weather = weather_desc
    current_temp = temp_desc

    current_weather = weather_desc
    current_temp = temp_desc
    
    # 3. Generate Report (LLM Simulation)
    # real LLM call would be here using google.generativeai
    
    report_content = f"""
[사망자 발생 보고서]

1. 인적사항
   - 소속: {person.uc}
   - 계급: {person.rank}
   - 군번: {person.srvno}
   - 성명: {person.nm}

2. 발생일시 및 장소
   - 일시: 2026년 2월 7일 14:30 경
   - 장소: 위도 {request.lat:.4f}, 경도 {request.lng:.4f} 인근 작전지역

3. 환경 세부사항
   - 기상: {current_weather}, 기온 {current_temp}
   - 특이사항: 해당 지역은 기상 상황 {current_weather}로 인해 시야 확보가 필요한 상태임.

4. 보고내용
   상기 인원은 금일 작전 수행 중 원인 미상의 사고로 인하여 사망한 것으로 추정됨.
   현재 현장 보존 및 신원 확인 절차를 진행 중이며, 군의관의 검안 및 추가 조사가 필요함.
   
5. 조치사항
   - 현장 통제 및 접근 차단
   - 상급 부대 보고 완료
   - 유가족 통보 준비 중

위와 같이 보고합니다.
    """
    
    return {
        "report": report_content.strip(),
        "weather": f"{current_weather}, {current_temp}",
        "location": f"{request.lat:.4f}, {request.lng:.4f}",
        "person": person
    }

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # For dev simplicity, allow login if user doesn't exist yet but match hardcoded
        if request.email == "army@army.mil" and request.password == "password123":
             return {"message": "Login successful", "user": "Army Admin"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.password_hash != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "user": user.name}

@app.get("/")
def read_root():
    return {"Hello": "WSL FastAPI World!"}


