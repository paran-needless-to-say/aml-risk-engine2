#!/usr/bin/env python3
"""
백엔드 서버 실행 스크립트

사용법:
    python3 run_server.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# api.app 모듈 실행
if __name__ == '__main__':
    from api.app import app
    
    print("=" * 70)
    print("🚀 AML Risk Engine API 서버 시작")
    print("=" * 70)
    print()
    print("📍 엔드포인트:")
    print("   POST http://localhost:5000/api/score/transaction")
    print("   POST http://localhost:5000/api/analyze/address")
    print("      - analysis_type: 'basic' (기본 스코어링, 빠름, 기본값)")
    print("      - analysis_type: 'advanced' (심층 분석, 느림)")
    print("   GET  http://localhost:5000/health")
    print()
    print("📚 API 문서:")
    print("   GET  http://localhost:5000/api-docs")
    print()
    
    # 포트 5000이 사용 중이면 5001로 변경
    import socket
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    if result == 0:
        print(f"⚠️  포트 {port}가 사용 중입니다. 포트 5001로 변경합니다.")
        port = 5001
    
    app.run(host='0.0.0.0', port=port, debug=True)

