"""
주소 기반 분석 API 라우트

수동 탐지용: 주소의 거래 히스토리를 분석하여 리스크 스코어 계산
"""
from flask import Blueprint, request, jsonify
from core.scoring.address_analyzer import AddressAnalyzer, AddressAnalysisResult

address_analysis_bp = Blueprint("address_analysis", __name__)


@address_analysis_bp.route("/address", methods=["POST"])
def analyze_address():
    """
    주소를 분석합니다
    주소의 거래 히스토리를 분석하여 리스크 스코어 계산
    ---
    tags:
      - Manual Analysis
    summary: 주소를 분석합니다
    description: 주소의 거래 히스토리를 분석하여 리스크 스코어 계산
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
            - address
            - chain
            - transactions
          properties:
            address:
              type: string
              description: 분석 대상 주소 (또는 target_address)
              example: "0xabc123..."
            target_address:
              type: string
              description: 분석 대상 주소 (address와 동일, 둘 중 하나 필수)
              example: "0xabc123..."
            chain:
              type: string
              description: 체인 이름
              example: "ethereum"
            transactions:
              type: array
              description: 거래 히스토리
              items:
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
                    description: 스코어링 대상 주소
                    example: "0xabc123..."
                  counterparty_address:
                    type: string
                    description: 상대방 주소
                    example: "0xdef456..."
                  entity_type:
                    type: string
                    enum: [mixer, bridge, cex, dex, defi, unknown]
                    example: "mixer"
                  is_sanctioned:
                    type: boolean
                    description: OFAC/제재 리스트 매핑 결과
                    example: true
                  is_known_scam:
                    type: boolean
                    description: Scam/phishing 블랙리스트 매핑
                    example: false
                  is_mixer:
                    type: boolean
                    description: entity_type에서 파생
                    example: true
                  is_bridge:
                    type: boolean
                    description: entity_type에서 파생
                    example: false
                  amount_usd:
                    type: number
                    description: 시세 기반 환산 금액
                    example: 123.45
                  asset_contract:
                    type: string
                    description: 자산 종류
                    example: "0x..."
            time_range:
              type: object
              description: 선택 필드 - 시간 범위
              properties:
                start:
                  type: string
                  format: date-time
                  example: "2024-01-01T00:00:00Z"
                end:
                  type: string
                  format: date-time
                  example: "2024-12-31T23:59:59Z"
            analysis_type:
              type: string
              enum: [basic, advanced]
              description: 분석 타입 (기본값: basic)
                - basic: 기본 룰만 평가 (빠름, 1-2초)
                - advanced: 모든 룰 평가 (느림, 5-30초, 그래프 구조 분석 포함)
              example: "basic"
    responses:
      200:
        description: 분석 성공
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
              example: "Missing required field: address"
      500:
        description: 서버 오류
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Analysis failed: ..."
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # 필수 필드 검증
        # address 또는 target_address 모두 허용
        address = data.get("address") or data.get("target_address")
        chain = data.get("chain")
        transactions = data.get("transactions", [])
        
        if not address:
            return jsonify({"error": "Missing required field: address or target_address"}), 400
        if not chain:
            return jsonify({"error": "Missing required field: chain"}), 400
        
        # 선택 필드
        time_range = data.get("time_range")
        analysis_type = data.get("analysis_type", "basic")  # 기본값: "basic"
        
        # 주소 분석 수행
        analyzer = AddressAnalyzer()
        result = analyzer.analyze_address(
            address=address,
            chain=chain,
            transactions=transactions,
            time_range=time_range,
            analysis_type=analysis_type
        )
        
        # 기존 JSON 포맷에 맞춰 응답 생성
        return jsonify({
            "target_address": result.address,  # 기존 포맷에 맞춤
            "risk_score": int(result.risk_score),  # 정수로 변환
            "risk_level": result.risk_level,
            "risk_tags": result.risk_tags,
            "fired_rules": result.fired_rules,  # {rule_id, score} 형태
            "explanation": result.explanation
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

