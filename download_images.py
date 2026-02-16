import requests
import os
from pathlib import Path

def download_images():
    # img.py 파일에서 URL 읽기
    with open('img.py', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    # 저장 폴더
    output_dir = Path('team_logos')
    output_dir.mkdir(exist_ok=True)

    print(f"총 {len(urls)}개의 이미지를 다운로드합니다...\n")

    success_count = 0
    fail_count = 0

    for idx, url in enumerate(urls, 1):
        try:
            # 팀 ID 추출 (URL에서 숫자 부분)
            team_id = url.split('/')[-1].replace('.png', '')
            filename = f"team_{team_id}.png"

            # 이미지 다운로드
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 파일 저장
            file_path = output_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)

            print(f"[{idx}/{len(urls)}] OK - {filename} 다운로드 완료")
            success_count += 1

        except Exception as e:
            print(f"[{idx}/{len(urls)}] FAIL - {url} 다운로드 실패: {str(e)}")
            fail_count += 1

    print(f"\n다운로드 완료: 성공 {success_count}개, 실패 {fail_count}개")

if __name__ == "__main__":
    download_images()
