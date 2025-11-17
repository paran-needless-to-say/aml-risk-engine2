#!/bin/bash
# 전체 체인의 모든 거래 CSV를 일괄 변환하는 스크립트

set -e

# 환경변수 확인
if [ -z "$CMC_PRO_API_KEY" ]; then
    echo "❌ 오류: CMC_PRO_API_KEY 환경변수가 설정되지 않았습니다."
    echo "   export CMC_PRO_API_KEY='your-api-key'"
    exit 1
fi

echo "🚀 전체 체인 일괄 변환 시작..."
echo ""

# 각 체인별로 처리
for chain in ethereum polygon bsc; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 $chain 처리 중..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python scripts/convert_value_to_usd.py \
        --chain "$chain" \
        --input-dir data/transactions \
        --output-dir data/transactions_with_usd
    
    echo ""
done

echo "✅ 전체 변환 완료!"
echo ""
echo "📁 결과 디렉토리: data/transactions_with_usd/"

