"""
Flask 서버: 트랜잭션 스코어링 API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from api.routes.scoring import scoring_bp

app = Flask(__name__)
CORS(app)  # CORS 허용 (프론트엔드에서 호출 가능)

# Blueprint 등록
app.register_blueprint(scoring_bp, url_prefix="/api/score")


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({"status": "ok", "service": "aml-risk-engine"}), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AML Risk Engine API 서버 시작")
    print("=" * 70)
    print()
    print("📍 엔드포인트:")
    print("   POST http://localhost:5000/api/score/transaction")
    print("   GET  http://localhost:5000/health")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
    """
    트랜잭션 스코어링 API 엔드포인트
    
    Request Body:
        {
            "tx_hash": "string",
            "chain": "string",
            "timestamp": "2025-11-17T12:34:56Z",
            "block_height": 21039493,
            "target_address": "string",
            "counterparty_address": "string",
            "entity_type": "mixer | bridge | cex | dex | defi | unknown",
            "is_sanctioned": true,
            "is_known_scam": false,
            "is_mixer": true,
            "is_bridge": false,
            "amount_usd": 123.45,
            "asset_contract": "0x..."
        }
    
    Response:
        {
            "target_address": "0x...",
            "risk_score": 78.0,
            "risk_level": "high",
            "risk_tags": ["mixer_inflow", "sanction_exposure"],
            "fired_rules": [
                {"rule_id": "MIXER_INFLOW_1HOP", "score": 50},
                {"rule_id": "SANCTIONED_ENTITY", "score": 40}
            ],
            "explanation": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        result = score_transaction_api(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 트랜잭션 스코어링 API 서버 시작")
    print("=" * 70)
    print()
    print("📍 엔드포인트:")
    print("   POST http://localhost:5000/api/score/transaction")
    print("   GET  http://localhost:5000/health")
    print()
    print("📝 사용 예시:")
    print("   curl -X POST http://localhost:5000/api/score/transaction \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{...}'")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)

