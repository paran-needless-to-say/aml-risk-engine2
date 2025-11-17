#!/bin/bash
# 백엔드 API로 가격 변환 테스트 스크립트

set -e

echo "🧪 백엔드 API 가격 변환 테스트"
echo ""

# 환경변수 확인
if [ -z "$CMC_PRO_API_KEY" ]; then
    echo "❌ 오류: CMC_PRO_API_KEY 환경변수가 설정되지 않았습니다."
    echo ""
    echo "설정 방법:"
    echo "  export CMC_PRO_API_KEY='your-api-key'"
    echo ""
    echo "또는 이 스크립트 실행 전에:"
    echo "  CMC_PRO_API_KEY='your-api-key' bash scripts/test_conversion.sh"
    exit 1
fi

echo "✅ API 키 확인됨"
echo ""

# 테스트할 파일 (작은 샘플)
TEST_CONTRACT="0x0a3b078561daf7458251857e28cab93ef608339f"
TEST_CHAIN="bsc"

echo "📄 테스트 파일: $TEST_CHAIN/$TEST_CONTRACT.csv"
echo ""

# 변환 실행
python scripts/convert_value_to_usd.py \
    --chain "$TEST_CHAIN" \
    --contract "$TEST_CONTRACT" \
    --input-dir data/transactions \
    --output-dir data/transactions_with_usd

echo ""
echo "✅ 테스트 완료!"
echo "📁 결과 파일: data/transactions_with_usd/$TEST_CHAIN/$TEST_CONTRACT.csv"
echo ""
echo "결과 확인:"
echo "  head -5 data/transactions_with_usd/$TEST_CHAIN/$TEST_CONTRACT.csv"

