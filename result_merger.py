import json
from typing import List, Dict

class TranscriptionMerger:
    @staticmethod
    def merge_results(results: List[str], include_speaker: bool = False) -> str:
        """複数の文字起こし結果を統合"""
        merged_texts = []
        
        for result in results:
            try:
                # JSONとしてパースを試みる
                data = json.loads(result)
                if isinstance(data, list):
                    # タイムスタンプ付きの結果の場合
                    for entry in data:
                        text = entry.get('text', '')
                        if include_speaker and 'speaker' in entry:
                            text = f"{entry['speaker']}: {text}"
                        merged_texts.append(text)
                else:
                    # プレーンテキストとして扱う
                    merged_texts.append(result)
            except json.JSONDecodeError:
                # JSONでない場合はプレーンテキストとして扱う
                merged_texts.append(result)

        # 結果を結合
        return "\n".join(merged_texts)

    @staticmethod
    def merge_json_results(results: List[str]) -> str:
        """複数のJSON形式の文字起こし結果を統合"""
        merged_entries = []
        current_time_offset = 0.0
        
        for result in results:
            try:
                entries = json.loads(result)
                if isinstance(entries, list):
                    for entry in entries:
                        # タイムスタンプを調整
                        if 'start' in entry:
                            entry['start'] = entry['start'] + current_time_offset
                        if 'end' in entry:
                            entry['end'] = entry['end'] + current_time_offset
                        merged_entries.append(entry)
                    
                    # 次のチャンクのオフセットを更新
                    if entries and 'end' in entries[-1]:
                        current_time_offset = entries[-1]['end']
            except json.JSONDecodeError:
                continue

        return json.dumps(merged_entries, ensure_ascii=False, indent=2)
