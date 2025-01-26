"""
会話分析モジュール
"""
import json
from typing import List, Dict
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

class ConversationAnalyzer:
    """会話分析クラス"""
    
    def __init__(self):
        self.speakers = []
        self.utterances = []
        self.total_duration = 0
        self.color_map = {}  # 話者ごとの色を保持
        
    def load_transcript(self, json_text: str):
        """文字起こし結果を読み込む"""
        data = json.loads(json_text)
        self.utterances = data
        
        # 話者リストを作成
        speakers = set()
        max_end = 0
        for utterance in data:
            speakers.add(utterance["speaker"])
            max_end = max(max_end, utterance["end"])
            
        self.speakers = sorted(list(speakers))
        self.total_duration = max_end
        
        # 話者ごとの色を設定
        colors = qualitative.Set3  # 12色のカラーパレット
        for i, speaker in enumerate(self.speakers):
            self.color_map[speaker] = colors[i % len(colors)]
        
    def create_timeline_graph(self) -> go.Figure:
        """発話量の時間変化グラフを作成"""
        # 時間軸の分割数（1分ごと）
        time_slots = int(np.ceil(self.total_duration / 60))
        
        # 話者ごとの発話量を計算
        speaker_data = {speaker: np.zeros(time_slots) for speaker in self.speakers}
        
        for utterance in self.utterances:
            speaker = utterance["speaker"]
            start_slot = int(utterance["start"] / 60)
            end_slot = int(utterance["end"] / 60)
            duration = utterance["end"] - utterance["start"]
            
            if start_slot == end_slot:
                speaker_data[speaker][start_slot] += duration
            else:
                # 発話が複数の時間枠にまたがる場合
                for slot in range(start_slot, end_slot + 1):
                    if slot == start_slot:
                        speaker_data[speaker][slot] += (60 - (utterance["start"] % 60))
                    elif slot == end_slot:
                        speaker_data[speaker][slot] += (utterance["end"] % 60)
                    else:
                        speaker_data[speaker][slot] += 60
        
        # グラフを作成
        fig = go.Figure()
        x = list(range(time_slots))
        
        # 積み上げ面グラフを作成
        for speaker in self.speakers:
            fig.add_trace(go.Scatter(
                x=x,
                y=speaker_data[speaker],
                name=speaker,
                stackgroup='one',
                mode='lines',
                line=dict(width=0.5),
                fillcolor=self.color_map[speaker],
                hovertemplate="時間: %{x}分<br>" +
                            f"話者: {speaker}<br>" +
                            "発話量: %{y:.1f}秒<extra></extra>"
            ))
        
        # レイアウトを設定
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(
                title="時間（分）",
                gridcolor='lightgray',
                title_font=dict(family="Noto Sans JP")
            ),
            yaxis=dict(
                title="発話量（秒）",
                gridcolor='lightgray',
                title_font=dict(family="Noto Sans JP")
            ),
            plot_bgcolor='white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )
        
        return fig
        
    def create_total_speech_graph(self) -> go.Figure:
        """話者ごとの総発話量グラフを作成"""
        # 話者ごとの総発話量を計算
        total_speech = {speaker: 0 for speaker in self.speakers}
        for utterance in self.utterances:
            duration = utterance["end"] - utterance["start"]
            total_speech[utterance["speaker"]] += duration
            
        # グラフを作成
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(self.speakers),
            y=[total_speech[speaker] for speaker in self.speakers],
            text=[f"{total_speech[speaker]:.1f}秒" for speaker in self.speakers],
            textposition='auto',
            marker_color=[self.color_map[speaker] for speaker in self.speakers],
            hovertemplate="話者: %{x}<br>発話量: %{y:.1f}秒<extra></extra>"
        ))
        
        # レイアウトを設定
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(
                title="話者",
                gridcolor='lightgray',
                title_font=dict(family="Noto Sans JP")
            ),
            yaxis=dict(
                title="発話量（秒）",
                gridcolor='lightgray',
                title_font=dict(family="Noto Sans JP")
            ),
            plot_bgcolor='white',
            showlegend=False
        )
        
        return fig
        
    def create_turn_taking_graph(self) -> go.Figure:
        """ターンテイクグラフを作成"""
        # 話者間の遷移回数を計算
        transitions = {s1: {s2: 0 for s2 in self.speakers} for s1 in self.speakers}
        
        for i in range(len(self.utterances) - 1):
            current_speaker = self.utterances[i]["speaker"]
            next_speaker = self.utterances[i + 1]["speaker"]
            transitions[current_speaker][next_speaker] += 1
            
        # ノードの位置を計算（円形に配置、話者数に応じて半径を調整）
        n_speakers = len(self.speakers)
        radius = 1.0 + (n_speakers - 4) * 0.1 if n_speakers > 4 else 1.0
        angles = np.linspace(0, 2*np.pi, n_speakers, endpoint=False)
        pos = {speaker: (radius * np.cos(angle), radius * np.sin(angle)) 
               for speaker, angle in zip(self.speakers, angles)}
        
        # エッジの最大値を計算
        max_transitions = max(max(row.values()) for row in transitions.values())
        
        # グラフを作成
        fig = go.Figure()
        
        # エッジを描画（曲線で表現）
        for s1, s1_pos in pos.items():
            for s2, s2_pos in pos.items():
                if transitions[s1][s2] > 0:
                    # エッジの太さと透明度を遷移回数に応じて変更
                    width = (transitions[s1][s2] / max_transitions) * 5
                    opacity = 0.3 + (transitions[s1][s2] / max_transitions) * 0.7
                    
                    # 自己ループの場合は円弧を描画
                    if s1 == s2:
                        t = np.linspace(0, 2*np.pi, 100)
                        r = 0.2
                        center_x = s1_pos[0] + r
                        center_y = s1_pos[1]
                        x = center_x + r * np.cos(t)
                        y = center_y + r * np.sin(t)
                    else:
                        # 異なるノード間は制御点を使用して曲線を描画
                        t = np.linspace(0, 1, 100)
                        control_scale = 0.3
                        dx = s2_pos[0] - s1_pos[0]
                        dy = s2_pos[1] - s1_pos[1]
                        control_x = (s1_pos[0] + s2_pos[0])/2 - dy * control_scale
                        control_y = (s1_pos[1] + s2_pos[1])/2 + dx * control_scale
                        x = (1-t)**2 * s1_pos[0] + 2*(1-t)*t * control_x + t**2 * s2_pos[0]
                        y = (1-t)**2 * s1_pos[1] + 2*(1-t)*t * control_y + t**2 * s2_pos[1]
                    
                    fig.add_trace(go.Scatter(
                        x=x,
                        y=y,
                        mode='lines',
                        line=dict(
                            width=width,
                            color='gray'
                        ),
                        opacity=opacity,
                        hovertemplate=f"{s1} → {s2}: {transitions[s1][s2]}回<extra></extra>",
                        showlegend=False
                    ))
        
        # ノードを描画
        for speaker, (x, y) in pos.items():
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(
                    size=40,
                    color=self.color_map[speaker],
                    line=dict(
                        color='gray',
                        width=2
                    )
                ),
                text=speaker,
                textposition="middle center",
                name=speaker,
                hovertemplate=f"{speaker}<extra></extra>"
            ))
        
        # レイアウトを設定
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.5, 1.5]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.5, 1.5],
                scaleanchor="x",
                scaleratio=1
            ),
            hovermode='closest'
        )
        
        return fig

class ConversationAnalysisWidget(QWidget):
    """会話分析ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = ConversationAnalyzer()
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # タイムライングラフ
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_label = QLabel("発話量の時間変化")
        timeline_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        timeline_layout.addWidget(timeline_label)
        self.timeline_view = QWebEngineView()
        self.timeline_view.setMinimumHeight(300)
        timeline_layout.addWidget(self.timeline_view)
        layout.addWidget(timeline_container)
        
        # 下部のグラフを横に並べる
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        
        # 総発話量グラフ
        speech_container = QWidget()
        speech_layout = QVBoxLayout(speech_container)
        speech_label = QLabel("話者ごとの総発話量")
        speech_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        speech_layout.addWidget(speech_label)
        self.total_speech_view = QWebEngineView()
        self.total_speech_view.setMinimumHeight(300)
        self.total_speech_view.setMinimumWidth(400)
        speech_layout.addWidget(self.total_speech_view)
        bottom_layout.addWidget(speech_container)
        
        # ターンテイクグラフ
        turn_container = QWidget()
        turn_layout = QVBoxLayout(turn_container)
        turn_label = QLabel("発話の遷移パターン")
        turn_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        turn_layout.addWidget(turn_label)
        self.turn_taking_view = QWebEngineView()
        self.turn_taking_view.setMinimumHeight(300)
        self.turn_taking_view.setMinimumWidth(400)
        turn_layout.addWidget(self.turn_taking_view)
        bottom_layout.addWidget(turn_container)
        
        layout.addWidget(bottom_container)
        
    def update_analysis(self, json_text: str):
        """分析結果を更新"""
        try:
            # 新しい分析を実行
            self.analyzer.load_transcript(json_text)
            
            # タイムライングラフ
            timeline_fig = self.analyzer.create_timeline_graph()
            self.timeline_view.setHtml(timeline_fig.to_html(include_plotlyjs='cdn'))
            
            # 総発話量グラフ
            total_speech_fig = self.analyzer.create_total_speech_graph()
            self.total_speech_view.setHtml(total_speech_fig.to_html(include_plotlyjs='cdn'))
            
            # ターンテイクグラフ
            turn_taking_fig = self.analyzer.create_turn_taking_graph()
            self.turn_taking_view.setHtml(turn_taking_fig.to_html(include_plotlyjs='cdn'))
            
        except Exception as e:
            print(f"分析エラー: {str(e)}")
