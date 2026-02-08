import subprocess
import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from bs4 import BeautifulSoup

app = FastAPI()

def extract_text_including_tables(file_path):
    try:
        # 1. hwp5html 실행 
        # (stdout으로 결과를 받기 위해 인자를 설정하지만, 
        # 일부 버전은 파일로 생성하므로 체크가 필요합니다.)
        result = subprocess.run(
            ['hwp5html', file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore' # 인코딩 에러 방지
        )

        # hwp5html이 자동으로 만든 .html 파일을 찾습니다.
        print(file_path)
        html_dir = file_path.replace('.hwp', '')
        print(html_dir)
        html_file = os.path.join(html_dir, 'index.xhtml')
        print(html_file)

        # 2. 디렉토리 삭제 (중요!)
        # 폴더 안의 내용까지 모두 삭제.
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            if os.path.exists(html_dir):
                shutil.rmtree(html_dir)
                print(f"임시 디렉토리 삭제 완료: {html_dir}")

        # 2. BeautifulSoup 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 3. 표(table) 태그를 직접 찾아서 텍스트 추출
        # get_text()가 놓치는 경우를 대비해 직접 순회하는 로직 포함
        extracted_chunks = []
        for element in soup.find_all(['p', 'table', 'tr', 'td']):
            text = element.get_text(strip=True)
            if text and text not in extracted_chunks:
                extracted_chunks.append(text)

        return "\n".join(extracted_chunks)
            
    except Exception as e:
        return f"처리 중 예외 발생: {str(e)}"

@app.post("/upload-hwp")
async def upload_hwp(file: UploadFile = File(...)):
    if not file.filename.endswith(".hwp"):
        raise HTTPException(status_code=400, detail="HWP 파일만 업로드 가능합니다.")

    # 파일명을 안전하게 관리 (공백 제거 등)
    safe_filename = file.filename.replace(" ", "_")
    temp_name = f"temp_{safe_filename}"
    
    try:
        with open(temp_name, "wb") as buffer:
            buffer.write(await file.read())

        extracted_text = extract_text_including_tables(temp_name)

        return {
            "filename": file.filename,
            "content": extracted_text if extracted_text else "텍스트를 추출하지 못했습니다."
        }
    
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        # 생성되었을지 모르는 임시 html 파일도 삭제
        temp_html = temp_name.replace('.hwp', '.html')
        if os.path.exists(temp_html):
            os.remove(temp_html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
