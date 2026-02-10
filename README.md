# Vertex AI: Gemini 파인튜닝 및 프로젝트 간 복제 가이드

본 가이드는 Google Cloud Vertex AI 환경에서 기존 Gemini 모델(Flash/Pro 등)을 파인튜닝(지도 학습, Supervised Fine-Tuning)하고, 생성된 커스텀 모델을 다른 프로젝트로 복사 및 공유하는 전체 엔드투엔드(End-to-End) 절차를 안내합니다.

## 1. 사전 준비 (Prerequisites)

**[중요]** 작업을 시작하기 전에 아래 항목들이 모두 준비되어 있는지 확인해 주세요.

- **Google Cloud 프로젝트**: 파인튜닝을 진행할 메인 프로젝트 (예: `기존(Source) 프로젝트`)
- **결제(Billing) 활성화**: 해당 프로젝트에 결제 계정이 연결되어 있어야 합니다.
- **API 활성화**: 
  - Vertex AI API (`aiplatform.googleapis.com`)
  - Cloud Storage API (`storage.googleapis.com`)
- **Cloud Storage 버킷**: 학습 데이터(`.jsonl`)를 업로드할 GCS 버킷 생성 (예: `gs://my-gemini-tuning-bucket`)

---

## 2. 학습 데이터 준비 (JSONL 포맷)

Gemini 파인튜닝 데이터는 **JSON Lines (JSONL)** 형식을 사용해야 합니다. 
각 줄은 하나의 독립적인 대화 세트(JSON 객체)를 표현해야 합니다.

**[팁]** 품질 높은 데이터를 최소 **100개 ~ 500개** 이상 준비하는 것을 권장합니다.

**데이터 예시 (`train_data.jsonl`)**
```json
{"messages": [{"role": "system", "content": "너는 여행 전문가야."}, {"role": "user", "content": "제주도 2박3일 일정 추천해줘"}, {"role": "model", "content": "제주도 2박 3일 일정을 추천해 드릴게요..."}]}
{"messages": [{"role": "user", "content": "사과가 영어로 뭐야?"}, {"role": "model", "content": "사과는 영어로 Apple 입니다."}]}
```

작성이 완료된 파일은 생성해둔 GCS 버킷에 업로드합니다. (`gs://my-gemini-tuning-bucket/train_data.jsonl`)

---

## 3. 파인튜닝 실행 방법

### 방법 A: Google Cloud Console (UI) 이용하기
비개발자나 빠른 테스트를 원할 때 가장 직관적인 방법입니다.

1. Cloud Console에서 **Vertex AI > Vertex AI Studio > 언어(Language)** 로 이동합니다.
2. 좌측 메뉴 또는 탭에서 **튜닝(Tuning)** 을 선택합니다.
3. **새 튜닝 작업 만들기(Create tuned model)** 를 클릭합니다.
4. **작업 세부정보 입력**:
    - **Base Model**: `gemini-1.5-flash` 또는 `gemini-1.0-pro` 등 튜닝할 기초 모델 선택
    - **학습 데이터**: GCS에 업로드한 `train_data.jsonl` 파일 경로 선택
    - **모델 이름**: 파인튜닝 후 생성될 모델의 고유 이름 입력
5. **튜닝 시작**을 누르면 백그라운드 환경에서 학습이 진행됩니다. (데이터량에 따라 수십 분 ~ 수 시간 소요)

### 방법 B: Python SDK (코드) 이용하기
자동화 파이프라인(CI/CD)이나 개발 환경에서 직접 실행할 때 사용합니다.

```python
import vertexai
from vertexai.preview.tuning import sft

# 1. 초기화 (프로젝트 ID 및 리전 설정)
project_id = "your-source-project-id"  # 튜닝을 수행할 GCP 프로젝트 ID
location = "us-central1"
vertexai.init(project=project_id, location=location)

# 2. 파인튜닝 작업 실행 (Supervised Fine Tuning)
sft_tuning_job = sft.train(
    source_model="gemini-1.5-flash-002", # 튜닝할 기본 모델
    train_dataset="gs://my-gemini-tuning-bucket/train_data.jsonl", # GCS 데이터 경로
    tuned_model_display_name="my-custom-model-v1", # 생성될 모델 이름
    epochs=3, # 학습 에포크 수 (선택)
    learning_rate_multiplier=1.0 # 학습률 배수 (선택)
)

print(f"튜닝 작업 상태: {sft_tuning_job.state}")
# 튜닝이 완료될 때까지 대기 (필요시)
# sft_tuning_job.wait()
```

---

## 4. 커스텀 모델 배포 및 엔드포인트 구성

튜닝이 성공적으로 완료되면 Vertex AI **Model Registry(모델 레지스트리)** 에 등록됩니다. 
Gemini 커스텀 모델은 전용 VM 셋팅이 생략되며, **공유 퍼블릭 엔드포인트**를 통해 서빙됩니다.

1. **Vertex AI > 모델 레지스트리** 로 이동하여 생성된 커스텀 모델을 클릭합니다.
2. **[배포 및 테스트] > [엔드포인트에 배포]** 를 클릭하여 모델을 활성화합니다.
3. 배포가 완료되면 생성된 **엔드포인트 ID** 및 **모델 리소스 경로**(`projects/.../locations/.../models/...`)를 복사합니다.

**Python에서 파인튜닝(배포 완료) 모델 호출하기**
```python
from vertexai.generative_models import GenerativeModel

# 배포된 파인튜닝 모델의 Endpoint 경로를 사용하여 인스턴스화
# 형식: projects/{project}/locations/{location}/endpoints/{endpoint_id}
tuned_model_path = "projects/your-project-number/locations/us-central1/endpoints/your-endpoint-id"
model = GenerativeModel(tuned_model_path)

response = model.generate_content("사과가 영어로 뭐야?")
print(response.text)
```

---

## 5. 타 프로젝트로 모델 복제 (Cross-Project Copy)

학습이 끝난 `기존(Source)` 프로젝트의 모델을 `신규/타겟(Target)` 프로젝트로 이전 또는 공유해야 할 때의 가이드입니다.

### 5.1 GCS 및 IAM 권한 열어주기
`신규명/타겟명` 프로젝트가 `기존명/소스명` 프로젝트의 모델 또는 학습 데이터에 접근하려면 IAM 작업이 필요합니다.

1. `타겟` 프로젝트의 Vertex AI 서비스 에이전트 계정 확인
   - 형식: `service-[TARGET_프로젝트_번호]@gcp-sa-aiplatform.iam.gserviceaccount.com`
   - **[팁]** IAM 화면에서 해당 계정이 보이지 않는다면 화면 우측 상단의 **'Google 제공 역할 부여 포함(Include Google-provided role grants)'** 체크박스를 켜주세요. (타겟 프로젝트에서 Vertex AI API가 활성화되어 있어야 자동 생성됩니다.)
2. `소스` 프로젝트 IAM 설정에서 위 계정에 다음 권한 부여:
   - `Vertex AI 사용자` (필수)
   - `저장소 하위 폴더/객체 뷰어` (GCS 에셋 접근용)

### 5.2 Model Registry 복사 (UI 방식)
1. `소스` 프로젝트의 **Model Registry** 에 접속합니다.
2. 튜닝된 모델의 **추가 작업(점 3개)** 버튼 클릭 -> **모델 복사(Copy model)** 선택
3. **다른 프로젝트로 복사**를 선택하고, 대상 프로젝트를 `타겟` 프로젝트로 지정합니다.

**[주의]** 타겟 프로젝트에도 사용자의 Vertex AI 관리자 권한이 있어야 복사가 가능합니다. 이 복사 과정을 통해 아티팩트가 이전되며 평가 지표 등은 넘어가지 않습니다.

### 5.3 (대안) 재학습을 통한 분리 아키텍처 (권장)
UI 복사가 제약되거나 완벽한 독립/분리 관리가 필요한 경우, 아티팩트를 복사하기보다 **공유된 GCS 학습 데이터를 바탕으로 `타겟` 프로젝트 내에서 직접 신규 파인튜닝 Job을 구동하는 것**이 운영 관리상 훨씬 유리합니다.
