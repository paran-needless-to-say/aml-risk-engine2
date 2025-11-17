"""
스코어링 API 라우트
"""
from flask import Blueprint, request, jsonify
from core.scoring.engine import TransactionScorer, TransactionInput, ScoringResult

scoring_bp = Blueprint("scoring", __name__)


@scoring_bp.route("/transaction", methods=["POST"])
def score_transaction():
    """
    트랜잭션을 스코어링합니다
    단일 트랜잭션의 리스크 분석
    ---
    tags:
      - Transaction Scoring
    summary: 트랜잭션을 스코어링합니다
    description: 단일 트랜잭션의 리스크 분석
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - tx_hash
            - chain
            - timestamp
            - block_height
            - target_address
            - counterparty_address
            - entity_type
            - is_sanctioned
            - is_known_scam
            - is_mixer
            - is_bridge
            - amount_usd
            - asset_contract
          properties:
            tx_hash:
              type: string
              example: "0x123..."
            chain:
              type: string
              example: "ethereum"
            timestamp:
              type: string
              format: date-time
              description: UTC 타임스탬프
              example: "2025-11-17T12:34:56Z"
            block_height:
              type: integer
              description: 정렬용
              example: 21039493
            target_address:
              type: string
              description: 점수를 매기려는 기준 주소(스코어링 대상)
              example: "0xabc123..."
            counterparty_address:
              type: string
              description: 타겟주소와 거래한 상대방 주소
              example: "0xdef456..."
            entity_type:
              type: string
              enum: [mixer, bridge, cex, dex, defi, unknown]
              description: 라벨 붙이는 거 백엔드가?
              example: "mixer"
            is_sanctioned:
              type: boolean
              description: OFAC/제재 리스트 매핑 결과(팩트) 스코어링은 이걸 이용해 risk 계산
              example: true
            is_known_scam:
              type: boolean
              description: Scam/phishing 블랙리스트 매핑(팩트)
              example: false
            is_mixer:
              type: boolean
              description: entity_type에서 파생되는 사실 정보
              example: true
            is_bridge:
              type: boolean
              description: entity_type에서 파생되는 사실 정보
              example: false
            amount_usd:
              type: number
              description: 시세 기반 환산 금액(지금은 시세 기반 아님)
              example: 123.45
            asset_contract:
              type: string
              description: 자산 종류(Ethereum native, ERC-20 등) 구분 라벨링
              example: "0x..."
    responses:
      200:
        description: 스코어링 성공
        schema:
          type: object
          properties:
            target_address:
              type: string
              example: "0xabc123..."
            risk_score:
              type: integer
              description: 0~100 점수 (연속값)
              example: 78
            risk_level:
              type: string
              enum: [low, medium, high, critical]
              example: "high"
            risk_tags:
              type: array
              description: 이 거래가 왜 위험한지 한눈에 보이는 태그들
              items:
                type: string
              example: ["mixer_inflow", "sanction_exposure", "high_value_transfer"]
            fired_rules:
              type: array
              description: 어떤 룰이 얼마만큼 점수에 기여했는지
              items:
                type: object
                properties:
                  rule_id:
                    type: string
                    example: "E-101"
                  score:
                    type: integer
                    example: 25
              example:
                - rule_id: "E-101"
                  score: 25
                - rule_id: "C-001"
                  score: 30
            explanation:
              type: string
              example: "1-hop sanctioned mixer에서 1,000USD 이상 유입된 거래로, 세탁 자금 유입 패턴에 해당하여 high로 분류됨."
      400:
        description: 잘못된 요청
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required field: tx_hash"
      500:
        description: 서버 오류
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Scoring failed: ..."
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
        
        # JSON 응답 생성 (입출력 포맷에 맞춤)
        return jsonify({
            "target_address": result.target_address,
            "risk_score": int(result.risk_score),  # 정수로 변환
            "risk_level": result.risk_level,
            "risk_tags": result.risk_tags,
            "fired_rules": [
                {"rule_id": rule.rule_id, "score": int(rule.score)}  # 정수로 변환
                for rule in result.fired_rules
            ],
            "explanation": result.explanation
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Scoring failed: {str(e)}"}), 500

