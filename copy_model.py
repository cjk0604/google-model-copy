import os
from google.cloud import aiplatform

# =========================================================================
# [사전 준비 작업]
# 스크립트 실행 전 터미널에서 아래 gcloud 명령어를 반드시 실행해야 합니다.
# 1. ADC(Application Default Credentials) 로그인 (권한 획득)
#    $ gcloud auth application-default login
# 2. Quota Project(할당량 프로젝트) 설정 (Target 프로젝트 권장)
#    $ gcloud auth application-default set-quota-project gemini-fine-tuning-target
# =========================================================================

print("Initializing Vertex AI Client...")

TARGET_PROJECT = "gemini-fine-tuning-target"
SOURCE_PROJECT = "gemini-fine-tuning-source"
# 모델 복사를 위해 대상 프로젝트를 지정하여 초기화합니다.
aiplatform.init(project=TARGET_PROJECT, location="us-central1")

SOURCE_MODEL_ID = "7704127342733426688"

# [선택 사항] 특정 버전 복사하기
# 기본적으로 버전을 명시하지 않으면 default(일반적으로 최신) 버전이 복사됩니다.
# 특정 버전을 복사하고 싶다면 모델 ID 뒤에 `@버전아이디` 또는 `@버전별칭`을 붙여줍니다.
# 예: SOURCE_MODEL_ID = "7704127342733426688@2" 또는 "7704127342733426688@default"
source_model_path = f"projects/{SOURCE_PROJECT}/locations/us-central1/models/{SOURCE_MODEL_ID}"

print(f"Instantiating Source Model: {source_model_path}")
source_model_obj = aiplatform.Model(model_name=source_model_path)

print(f"Initiating copy to Target Project: {TARGET_PROJECT}...")
try:
    copied_model = source_model_obj.copy(
        destination_location="us-central1",
        destination_model_id="target-model-260213"
    )
    print(f"\n✅ Copy Successful! Copied Model Resource Name:")
    print(copied_model.resource_name)
except Exception as e:
    print(f"\n❌ Copy Failed!")
    print(e)
