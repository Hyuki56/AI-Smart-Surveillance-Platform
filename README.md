# AI Smart Surveillance Platform

YOLO11 기반 사람 객체 탐지와 ByteTrack을 이용한 제한구역 침입 감지 서비스입니다.

영상에서 사람을 탐지하고 추적한 뒤, 제한구역 내부 진입 여부를 판단하여 침입 이벤트를 생성합니다.

침입이 발생하면 Snapshot을 저장하고 SQLite에 이벤트를 기록하며, FastAPI를 통해 서비스 상태와 침입 이력을 조회할 수 있도록 구현했습니다.

---

## 1. Project Overview

### 프로젝트 목적

CCTV 영상에서 사람의 움직임을 실시간으로 분석하여 특정 제한구역에 사람이 진입했는지 자동으로 감지하는 AI 영상 분석 서비스를 구현했습니다.

단순히 객체 탐지 모델을 실행하는 것에서 끝내지 않고,

```text
영상 입력
   ↓
YOLO11 사람 탐지
   ↓
ByteTrack 객체 추적
   ↓
제한구역 판정
   ↓
ENTER / EXIT 이벤트 생성
   ↓
Snapshot 저장
   ↓
SQLite 이벤트 저장
   ↓
FastAPI API 제공

전체 AI 서비스 파이프라인을 직접 구현했습니다.