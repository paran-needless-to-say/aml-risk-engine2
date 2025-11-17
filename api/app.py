"""
Flask 서버: 트랜잭션 스코어링 API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from api.routes.scoring import scoring_bp
from api.routes.address_analysis import address_analysis_bp

app = Flask(__name__)
CORS(app)  # CORS 허용 (프론트엔드에서 호출 가능)

# Swagger 설정
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "info": {
        "title": "AML Risk Engine API",
        "description": "CEX를 위한 주소 추적 및 리스크 스코어링 시스템",
        "version": "1.0.0",
        "contact": {
            "name": "AML Risk Engine Team"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Manual Analysis",
            "description": "수동 탐지 - 주소 기반 리스크 분석"
        },
        {
            "name": "Transaction Scoring",
            "description": "단일 트랜잭션 리스크 스코어링"
        },
        {
            "name": "Health",
            "description": "서버 상태 확인"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Blueprint 등록
app.register_blueprint(scoring_bp, url_prefix="/api/score")
app.register_blueprint(address_analysis_bp, url_prefix="/api/analyze")


@app.route('/health', methods=['GET'])
def health_check():
    """
    서버 상태 확인
    ---
    tags:
      - Health
    summary: 서버 상태 확인
    description: 헬스 체크 엔드포인트
    responses:
      200:
        description: 서버 정상
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
            service:
              type: string
              example: "aml-risk-engine"
    """
    return jsonify({"status": "ok", "service": "aml-risk-engine"}), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AML Risk Engine API 서버 시작")
    print("=" * 70)
    print()
    print("📍 엔드포인트:")
    print("   POST http://localhost:5000/api/score/transaction")
    print("   POST http://localhost:5000/api/analyze/address")
    print("   GET  http://localhost:5000/health")
    print()
    print("📚 API 문서:")
    print("   GET  http://localhost:5000/api-docs")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)

