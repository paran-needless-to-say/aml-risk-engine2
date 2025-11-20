#!/usr/bin/env python3
"""
2단계 스코어러 학습 스크립트
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.scoring.stage2_scorer import Stage2Scorer


def main():
    """메인 함수"""
    dataset_dir = project_root / "data" / "dataset"
    train_path = dataset_dir / "train.json"
    val_path = dataset_dir / "val.json"
    
    if not train_path.exists():
        print("❌ 학습 데이터셋 파일을 찾을 수 없습니다.")
        return
    
    print("📂 데이터 로드 중...")
    with open(train_path, 'r') as f:
        train_data = json.load(f)
    
    val_data = None
    if val_path.exists():
        with open(val_path, 'r') as f:
            val_data = json.load(f)
    
    print(f"   Train: {len(train_data)}개")
    if val_data:
        print(f"   Val: {len(val_data)}개")
    
    # 여러 모델 타입으로 학습
    model_types = ["logistic", "random_forest", "gradient_boosting"]
    results = {}
    
    for model_type in model_types:
        print(f"\n{'=' * 80}")
        print(f"{model_type.upper()} 모델 학습")
        print(f"{'=' * 80}")
        
        scorer = Stage2Scorer(model_type=model_type, use_ppr_features=True)
        train_results = scorer.train(train_data, val_data)
        
        results[model_type] = train_results
        
        # 모델 저장
        model_path = dataset_dir / f"stage2_scorer_{model_type}.pkl"
        scorer.save_model(model_path)
        print(f"\n💾 모델 저장: {model_path}")
    
    # 결과 저장
    output_path = dataset_dir / "stage2_scorer_training_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print("✅ 학습 완료")
    print(f"{'=' * 80}")
    print("\n📊 학습 결과 요약:")
    for model_type, result in results.items():
        print(f"\n  {model_type.upper()}:")
        print(f"    학습 Accuracy: {result.get('train_accuracy', 0):.4f}")
        if 'val_accuracy' in result:
            print(f"    검증 Accuracy: {result.get('val_accuracy', 0):.4f}")
            print(f"    검증 F1-Score: {result.get('val_f1', 0):.4f}")


if __name__ == "__main__":
    main()

