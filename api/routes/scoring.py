"""
스코어링 API 라우트
"""
from flask import Blueprint, request, jsonify
from core.scoring.engine import TransactionScorer, TransactionInput, ScoringResult

scoring_bp = Blueprint("scoring", __name__)


@scoring_bp.route("/transaction", methods=["POST"])
def score_transaction():
    """
    트랜잭션 스코어링 API
    
    Request Body:
        {
            "tx_hash": "string",
            "chain": "ethereum",
            "timestamp": "2025-11-17T12:34:56Z",
            "block_height": 21039493,
            "target_address": "0x...",
            "counterparty_address": "0x...",
            "entity_type": "mixer",
            "is_sanctioned": true,
            "is_known_scam": false,
            "is_mixer": true,
            "is_bridge": false,
            "amount_usd": 1234.56,
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
        
        # 입력 데이터 검증 및 변환
        try:
            tx_input = TransactionInput(
                tx_hash=data["tx_hash"],
                chain=data["chain"],
                timestamp=data["timestamp"],
                block_height=data["block_height"],
                target_address=data["target_address"],
                counterparty_address=data["counterparty_address"],
                entity_type=data["entity_type"],
                is_sanctioned=data["is_sanctioned"],
                is_known_scam=data["is_known_scam"],
                is_mixer=data["is_mixer"],
                is_bridge=data["is_bridge"],
                amount_usd=float(data["amount_usd"]),
                asset_contract=data["asset_contract"]
            )
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e}"}), 400
        
        # 스코어링 수행
        scorer = TransactionScorer()
        result = scorer.score_transaction(tx_input)
        
        # JSON 응답 생성
        return jsonify({
            "target_address": result.target_address,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "risk_tags": result.risk_tags,
            "fired_rules": [
                {"rule_id": rule.rule_id, "score": rule.score}
                for rule in result.fired_rules
            ],
            "explanation": result.explanation
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Scoring failed: {str(e)}"}), 500

