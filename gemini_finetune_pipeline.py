import vertexai
from vertexai.generative_models import GenerativeModel
import time

# [주의] 최신 버전에 따라 import 경로가 preview.tuning 에서 tuning 으로 승격될 수 있습니다.
from vertexai.preview.tuning import sft


def run_gemini_finetuning_pipeline():
    """
    Google Cloud Vertex AI에서 제공하는 Python SDK를 활용하여
    Gemini 모델의 Supervised Fine-Tuning(지도 학습) 파이프라인을 실행하는 샘플 스크립트.
    """
    print("🚀 Gemini SFT 파인튜닝 자동화 파이프라인 시작")
    
    # =========================================================================
    # 구성 정보 (본인의 프로젝트 환경에 맞게 수정 필수)
    # =========================================================================
    PROJECT_ID = "your-source-project-id"         # 모델 학습을 수행할 Google Cloud Project ID
    LOCATION = "us-central1"                      # 학습 파이프라인이 실행될 리전 (asia-northeast3 등)
    BASE_MODEL = "gemini-1.5-flash-002"           # 튜닝할 기본(Base) 모델 명칭
    
    # 사전에 준비된 GCS 상의 JSONL 형식 학습 데이터 경로
    TRAIN_DATASET_URI = "gs://my-gemini-tuning-bucket/train_data.jsonl"
    
    # 튜닝 완료 후 저장될 모델의 표시 이름 지정 (예: 용도나 버전으로 이름 기록)
    MODEL_DISPLAY_NAME = "my-custom-model-v1" 
    
    # =========================================================================
    # Step 1: Vertex AI Client 초기화
    # =========================================================================
    print(f"[{PROJECT_ID} / {LOCATION}] 환경으로 Vertex AI를 초기화합니다...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)


    # =========================================================================
    # Step 2: 파인튜닝(Tuning Job) 실행 시작
    # =========================================================================
    print(f"[{BASE_MODEL}] 모델 기반으로 학습을 시작합니다. (데이터: {TRAIN_DATASET_URI})")
    
    # sft.train() 함수는 비동기적으로 클라우드에 Job을 생성하고
    # SftTuningJob 객체를 반환합니다.
    sft_tuning_job = sft.train(
        source_model=BASE_MODEL,
        train_dataset=TRAIN_DATASET_URI,
        # 검증 데이터셋이 있다면 아래 주석을 풀고 사용 가능
        # validation_dataset="gs://my-gemini-tuning-bucket/valid_data.jsonl",
        tuned_model_display_name=MODEL_DISPLAY_NAME,
        epochs=3,                     # 데이터셋 반복 학습 횟수 (오버피팅을 방지하기 위해 조정)
        learning_rate_multiplier=1.0  # 기본 학습률 배수 지정
    )
    
    print(f"✅ Job 제출 완료! Job 리소스 이름: {sft_tuning_job.resource_name}")
    print("이제 Google Cloud에서 학습 컴퓨팅 자원이 할당되어 모델이 학습됩니다.")
    print("이 작업은 데이터 양에 따라 30분에서 수 시간이 소요될 수 있습니다.")


    # =========================================================================
    # Step 3: 작업 진행 상황 모니터링 (Polling)
    # =========================================================================
    # CI/CD 환경에서 파이프라인을 돌린다면, Job이 끝날때까지 대기(Wait) 처리를 할 수 있습니다.
    while not sft_tuning_job.has_ended:
        print(f"현재 상태: {sft_tuning_job.state} ... 대기 중")
        time.sleep(60) # 60초마다 상태 체크
        sft_tuning_job.refresh() # 객체 최신 상태 동기화
        
    print(f"\n🎉 튜닝 작업이 종료되었습니다. (종료 상태: {sft_tuning_job.state})")
    
    if sft_tuning_job.has_failed:
        print(f"❌ 튜닝이 실패했습니다. 에러: {sft_tuning_job.error}")
        return


    # =========================================================================
    # Step 4: 완료된 커스텀 모델(엔드포인트) 정보 조회 및 테스트
    # =========================================================================
    # Gemini 파인튜닝 모델은 완료 시 자동으로 공유 퍼블릭 엔드포인트에 배포됩니다.
    # 해당 엔드포인트의 리소스 경로를 조회합니다.
    tuned_model_endpoint_name = sft_tuning_job.tuned_model_endpoint_name
    print(f"✨ 생성된 커스텀 모델 엔드포인트 이름:\n{tuned_model_endpoint_name}")
    print("-> 이 경로를 타(Test) 프로젝트 서비스에서 참조하여 사용할 수 있습니다.\n")

    # 추론 테스트 수행
    print("배포된 파인튜닝 모델을 통해 테스트 질의를 수행합니다...")
    model = GenerativeModel(tuned_model_endpoint_name)
    
    test_prompt = "이 커스텀 모델이 잘 작동하는지 간단하게 테스트해 줘."
    print(f"User > {test_prompt}")
    
    try:
        response = model.generate_content(test_prompt)
        print(f"Model > {response.text}")
    except Exception as e:
        print(f"❌ 추론 테스트 중 에러 발생: {e}")
        
if __name__ == "__main__":
    run_gemini_finetuning_pipeline()
