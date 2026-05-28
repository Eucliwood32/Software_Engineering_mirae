import os
import json
import typing

class StopwordDictionary:
    """
    FR-3.3: 시스템 내장 자동 불용어 분류 (사용자 편집 UI 제공 금지).
    ConOps §6.4 / RR FR-3.3: 사용자(조장)에게 불용어 사전 편집 UI를 제공하지 않는다.
    동일 입력에 대해 동일 불용어 분류 결과가 산출된다 (NFR-1.3 결정론 부합).
    """
    # 시스템 내장 불용어 사전 (수정 불가)
    STOPWORDS = {
        "단순리액션": [
            "ㅇㅇ", "ㅋㅋ", "ㅎㅎ", "ㄱㄱ", "ㄴㄴ", "ㄷㄷ", "ㅠㅠ",
            "ㅋㅋㅋ", "ㅎㅎㅎ", "ㅠㅠㅠ", "ㅋㅋㅋㅋ", "ㅎㅎㅎㅎ",
            "ㅇㅋ", "ㅇㅇㅇ", "ㄱㄱㄱ"
        ],
        "미디어태그": [
            "(이모티콘)", "(사진)", "(동영상)", "(파일)",
            "이모티콘", "사진", "동영상", "첨부파일"
        ],
        "1글자단순응답": [
            "네", "예", "응", "굳", "넵", "넹", "욥", "옹"
        ]
    }
    
    def __init__(self):
        # 불변 사전 — 사용자 편집 없음
        self._all_stopwords = set()
        for words in self.STOPWORDS.values():
            self._all_stopwords.update(words)

    def is_meaningful_message(self, message: str) -> bool:
        """메시지가 유효(의미 있는)한지 판별한다."""
        msg = message.strip()
        if not msg:
            return False
        
        # 전체 메시지가 단일 불용어와 정확히 일치하는 경우
        if msg in self._all_stopwords:
            return False
        
        # 메시지를 공백 기준 토큰화 후, 모든 토큰이 불용어이면 무의미
        tokens = msg.split()
        if not tokens:
            return False
            
        for t in tokens:
            if t not in self._all_stopwords:
                return True
                
        return False
