from google.cloud import aiplatform

# =========================================================================
# [사전 준비 작업]
# $ gcloud auth application-default login
# $ gcloud auth application-default set-quota-project gemini-fine-tuning-target
# =========================================================================

print("Initializing Vertex AI Client...")

TARGET_PROJECT = "gemini-fine-tuning-target"
LOCATION = "us-central1"
aiplatform.init(project=TARGET_PROJECT, location=LOCATION)

# 앞서 복사하여 생성된 커스텀 모델의 ID 또는 리소스 이름
MODEL_ID = "faker-251230-model" 
# 또는 "projects/676700407951/locations/us-central1/models/faker-251230-model"

print(f"[{TARGET_PROJECT}] 환경의 모델 [{MODEL_ID}] 인스턴스화...")
model = aiplatform.Model(model_name=MODEL_ID)

print("\n엔드포인트 생성 및 모델 배포 진행 중...")
print("(이 과정은 백그라운드에서 컴퓨팅 리소스를 할당하므로 완료까지 수 분 이상 소요될 수 있습니다)")
try:
    # Gemini 모델은 공유 엔드포인트에 배포됩니다.
    endpoint = model.deploy()
    print(f"\n✅ Deploy Successful! Endpoint Resource Name:")
    print(endpoint.resource_name)
    print("\n👉 추론에 사용할 경로 (GenerativeModel 인스턴스에 전달):")
    print(endpoint.resource_name)
except Exception as e:
    print(f"\n❌ Deploy Failed!")
    print(e)
