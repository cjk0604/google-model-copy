import json
import random

def generate_dummy_jsonl():
    output_file = "/Users/changjoon/Documents/04_Coupang/01_model_copy/train_data.jsonl"
    
    system_review = "너는 이커머스 상품 리뷰를 핵심만 짧게 1문장으로 요약하는 어시스턴트야."
    system_cs = "너는 쇼핑몰 고객 문의를 처리하는 친절한 AI 챗봇이야."

    products = ["무선 이어폰", "노트북 파우치", "게이밍 마우스", "기계식 키보드", "스마트 워치 필름", 
                "캠핑용 의자", "텀블러", "바람막이 자켓", "운동화", "블루투스 스피커", 
                "고양이 간식", "강아지 배변패드", "대용량 보조배터리", "차량용 방향제", "실내 디퓨저", "게이밍 모니터", "요가매트"]
    
    speeds = ["정말 총알같이 빠르고", "생각보다 엄청 빠르고", "예상했던 날짜에 도착했고", "하루 정도 늦었지만", "배송이 너무 늦어서"]
    conditions = ["포장도 꼼꼼히 이중으로 잘 되어 있네요.", "안전하게 파손 전혀 없이 잘 왔습니다.", "박스가 조금 찌그러져서 아쉬워요.", "포장이 너무 부실해서 내용물이 걱정됐습니다.", "제품 외관에 잔기스가 조금 있네요."]
    evaluations = [
        "색상도 화면과 완벽히 똑같고 가성비 최고입니다! 주변에도 적극 추천해요.",
        "마감이 정말 훌륭해서 다음에도 여기서 무조건 구매할게요.",
        "생각보다 무게감이 꽤 있어서 매일 휴대하긴 조금 아쉽습니다.",
        "기대한 것과는 재질이 많이 달라서 조금 실망입니다.",
        "전처음부터 전혀 작동하지 않네요. 당장 환불해주세요.",
        "친구 생일 선물용으로 샀는데 받는 분이 너무 좋아하셔서 덩달아 기쁩니다.",
        "딱 가격 대비 품질이라서 그럭저럭 무난하게 쓸만합니다.",
        "인터넷에서 본 것보다 실물이 훨씬 고급스럽고 예뻐서 대만족입니다.",
        "마감 처리가 너무 아쉽습니다. 금방 망가질 것 같아요."
    ]

    cs_topics = [
        ("배송지 변경", "상품이 '결제 완료' 또는 '상품 준비 중' 상태일 경우에만 마이페이지 주문 내역에서 배송지 변경이 가능합니다. 이미 '배송 중' 상태로 전환되었다면 택배사로 직접 문의하셔야 합니다."),
        ("환불 처리 기간", "환불 처리는 반품하신 상품이 물류에 정상 회수된 후 영업일 기준 3~5일 정도 소요됩니다. 결제하신 카드사의 사정에 따라 영수증 취소 반영은 다소 지연될 수 있습니다."),
        ("비밀번호 분실", "로그인 화면 하단의 '비밀번호 찾기' 링크를 클릭하신 후, 가입 시 등록하신 이메일 주소를 입력하시면 비밀번호 재설정 메일을 즉시 발송해 드립니다."),
        ("상품 교환 방법", "상품 교환은 배송 수령 후 7일 이내에 마이페이지의 '교환/반품' 메뉴에서 신청 가능하며, 단순 변심의 경우 왕복 배송비가 고객님께 청구될 수 있습니다."),
        ("현금영수증 발급 방법", "마이페이지의 '주문/배송 내역'에서 해당 주문건을 선택하신 후 '영수증 출력' 버튼을 통해 현금영수증 확인 및 인쇄가 언제든지 가능합니다."),
        ("포인트 결제", "결제 화면의 '결제수단 선택' 단계에서 현재 보유하신 포인트를 조회하고 원하시는 금액만큼 전액 또는 일부 적용해 결제하실 수 있습니다."),
        ("품절 상품 재입고", "품절된 상품별 상세 페이지에서 '재입고 알림 신청' 버튼을 눌러주시면, 상품이 다시 입고되는 즉시 카카오톡 또는 문자로 알림을 보내드립니다.")
    ]
    cs_intros = ["궁금한 게 하나 있는데요. ", "안녕하세요 관리자님, ", "빠르게 문의드립니다! ", "저기요, 확인 좀 해주세요. ", "도움이 필요해서 글 남깁니다. ", ""]

    data = []

    # 1. 리뷰 요약 데이터 생성 (150개)
    for _ in range(150):
        prod = random.choice(products)
        spd = random.choice(speeds)
        cond = random.choice(conditions)
        ev = random.choice(evaluations)
        
        user_text = f"리뷰: [{prod}] {spd} {cond} {ev}"
        
        # 긍정/부정 판단 휴리스틱 롤
        if "최고" in ev or "훌륭" in ev or "좋아하" in ev or "대만족" in ev:
            sentiment = "아주 만족하며 추천하는"
        elif "실망" in ev or "환불" in ev or "기스" in cond or "부실" in cond or "망가질" in ev or "늦어" in spd:
            sentiment = "강한 불만을 표시하며 아쉬워하는"
        else:
            sentiment = "가격 및 품질에 대해 무난하게 평가하는"
            
        model_text = f"고객이 구매한 [{prod}] 상품에 대해 배송 기간과 포장 상태를 언급하며 전반적으로 {sentiment} 성향의 리뷰입니다."
        
        data.append({
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": system_review}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_text}]
                },
                {
                    "role": "model",
                    "parts": [{"text": model_text}]
                }
            ]
        })

    # 2. CS 문의 답변 데이터 생성 (50개)
    for _ in range(50):
        topic, answer = random.choice(cs_topics)
        intro = random.choice(cs_intros)
        
        user_text = f"{intro}{topic} 절차가 어떻게 되나요?"
        model_text = f"안녕하세요 고객님! 문의하신 [{topic}] 관련하여 친절히 안내해 드립니다. {answer}"
        
        data.append({
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": system_cs}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_text}]
                },
                {
                    "role": "model",
                    "parts": [{"text": model_text}]
                }
            ]
        })

    # 데이터 순서 무작위 셔플 (다양한 데이터 분포)
    random.shuffle(data)

    # 지정된 경로에 JSONL 형태로 파일 덮어쓰기 (200줄)
    with open(output_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"✅ 총 {len(data)}개의 파인튜닝 데이터 셋(JSONL)이 성공적으로 생성되었습니다.")
    print(f"✅ 저장 경로: {output_file}")

if __name__ == "__main__":
    generate_dummy_jsonl()
