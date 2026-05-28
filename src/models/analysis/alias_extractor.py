import typing

class AliasExtractor:
    """
    FR-1.3: 세 파서의 출력에서 식별자 집합을 union
    """
    @staticmethod
    def extract_all_aliases(git_data: dict, ooxml_data: dict, messenger_data: dict) -> typing.Set[str]:
        aliases = set()
        
        # Git 데이터에서 추출
        if git_data:
            aliases.update(git_data.keys())
            
        # OOXML 데이터에서 추출
        if ooxml_data:
            for author in ooxml_data.keys():
                if author != "Unknown":
                    aliases.add(author)
                    
        # 메신저 데이터에서 추출
        if messenger_data and "records" in messenger_data:
            for record in messenger_data["records"]:
                aliases.add(record["author"])
                
        return aliases
