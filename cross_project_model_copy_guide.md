# Cross-Project Vertex AI Model Copy Guide

이 문서는 Google Cloud Platform(GCP)에서 하나의 프로젝트(Source)에 있는 Vertex AI 모델을 다른 프로젝트(Target)로 복사할 때 필요한 권한(Permission), 서비스 계정(Service Account), 버킷 설정 등을 총정리한 가이드입니다.

---

## 1. 프로젝트 (Projects)
명령어 실행 결과를 기반으로 한 두 프로젝트의 역할입니다.

*   **Source Project (출발지)**
    *   **Project ID:** `gemini-fine-tuning-source`
    *   **Project Number:** `585790463155`
    *   역할: 원본 모델 자산(Artifacts)이 저장된 프로젝트.
*   **Target Project (도착지)**
    *   **Project ID:** `gemini-fine-tuning-target`
    *   **Project Number:** `676700407951`
    *   역할: 복사된 모델을 등록하고 향후 엔드포인트(Endpoint) 배포에 사용할 프로젝트.

---

## 2. 서비스 계정 (Service Accounts) 및 역할
모델 복사 과정에는 **두 종류의 서비스 계정**이 협력하여 작동합니다. 이들의 역할을 구분하는 것이 가장 중요합니다.

### A. 커스텀 서비스 계정 (Custom Service Account) - "명령자"
*   **설명:** 사용자가 직접 생성하고 `.json` 키를 발급받아 파이썬 스크립트(`copy_model.py`) 인증에 사용하는 계정.
*   **역할:** Vertex AI API를 호출하여 "Source 모델을 Target으로 복사하라"는 **API 명령**을 내립니다.
*   **필요 권한 (IAM):**
    *   **Source Project:** `Vertex AI 뷰어(Viewer)` 권한 (원본 모델 리소스를 읽어야 하므로)
    *   **Target Project:** `Vertex AI 관리자(Admin)` 권한 (새로운 모델을 생성해야 하므로)

### B. 관리형 AI Platform 에이전트 (Managed AI Platform Service Agent) - "실제 작업자"
*   **계정명:** `service-676700407951@gcp-sa-aiplatform.iam.gserviceaccount.com`
    *   *형식: `service-[Target_Project_Number]@gcp-sa-aiplatform.iam.gserviceaccount.com`*
*   **설명:** Target 프로젝트에서 Vertex AI API를 활성화하면 GCP가 **자동으로 생성하여 백그라운드에 숨겨두는** 구글 관리형 서비스 계정.
*   **역할:** 커스텀 서비스 계정으로부터 복사 명령이 떨어지면, **실제로 디스크(GCS 버킷)에 접근하여 기가바이트 단위의 모델 파일 데이터를 Source에서 Target으로 퍼 나르는** 진짜 실행 주체.

---

## 3. GCS 버킷 권한 (Storage Permissions) - 핵심 장애 포인트
에이전트(작업자)가 데이터를 정상적으로 읽어오려면 **Source 프로젝트의 모델 파일이 저장된 GCS 버킷(Cloud Storage)**에 권한을 열어주어야 합니다.

*   **설정 위치:** Source Project의 GCS 버킷 (모델 경로)
*   **부여할 역할:** `저장소 객체 뷰어 (Storage Object Viewer)`
*   **권한을 받을 대상(Principals):**  아래 두 계정을 **모두** 추가해야 합니다.
    1.  파이썬 코드를 실행한 **커스텀 서비스 계정** (경로 검증용)
    2.  Target 프로젝트의 **관리형 AI Platform 에이전트 (`service-676700407951@...`)** (데이터 다운로드용)

---

## 4. 전체 요약 아키텍처 (Workflow)

1.  로컬 환경(`copy_model.py`)에서 **커스텀 서비스 계정 Key**를 사용해 Target 프로젝트의 Vertex AI API에 접근합니다.
2.  이때, Source 모델의 경로(`projects/gemini-fine-tuning-source/.../7704127342733426688`)를 매개변수로 전달하며 복사를 명령합니다.
3.  명령을 받은 **Target 프로젝트의 AI Platform 에이전트(`service-676700407951@...`)**가 Source 프로젝트로 출동합니다.
4.  Source 프로젝트의 **GCS 버킷 설정**이 에이전트의 출입을 허용(`Storage Object Viewer`)하므로, 무사히 데이터를 읽어(Pull) 옵니다.
5.  가져온 데이터를 바탕으로 Target 프로젝트(`676700407951`)에 `target-model-260213`이라는 이름으로 새 모델을 성공적으로 등록합니다.
