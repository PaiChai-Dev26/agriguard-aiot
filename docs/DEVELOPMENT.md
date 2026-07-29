# 개발 착수 기준선

이 코드는 교수님 피드백의 P0 흐름을 팀이 병렬로 확장하기 위한 최소 기준선이다.

## 구현된 범위

- 시간대가 포함된 IMU/GPS 텔레메트리 스키마
- 설명 가능한 규칙 기반 위험점수(`rules-v1`)
- `NORMAL -> SUSPECTED -> PENDING_CONFIRMATION -> DETECTED/CANCELLED`
- REST 수신, 장치/사고 조회, 취소 및 초기화 API
- 관제용 WebSocket 브로드캐스트
- 정상·경사·진동·전도 가상 장치 시나리오
- 계약 확인용 최소 관제 화면과 자동 테스트

현재 저장소는 팀원 구현 전 계약 검증을 위해 인메모리 저장소를 사용한다. DB 담당자는
API 응답 형식을 유지한 채 PostgreSQL/PostGIS 저장소로 교체한다.

## 실행

Python 3.12 환경에서:

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

브라우저에서 `http://localhost:8000`을 연 뒤 다른 터미널에서 전도 시나리오를 실행한다.

```bash
python simulator/simulate.py rollover --count 12 --interval 1
```

Docker를 사용한다면:

```bash
docker compose up --build
```

## 테스트

```bash
python -m pytest -q
```

## 팀원이 확장할 경계

- 펌웨어: `simulator/simulate.py`와 같은 JSON을 ESP32에서 전송한다.
- 프론트엔드: `/ws/control-room`의 `telemetry.processed` 메시지를 React 화면에서 소비한다.
- 백엔드/DB: `latest_by_device`, `events` 인메모리 자료구조를 저장소 계층으로 교체한다.
- AI: `assess_rollover_risk()` 함수의 입력·출력 계약을 유지한 채 모델 어댑터를 연결한다.

위험점수만으로 사고를 확정하지 않는다. 취소 확인과 상태 머신은 계속 서버 정책 계층에 둔다.

