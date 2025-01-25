import PySimpleGUI as sg

def create_window():
    # テーマ設定
    sg.theme('LightGrey1')
    
    # レイアウト定義
    left_column = [
        [sg.Text('メディアファイル:')],
        [sg.Input(key='-FILE-'), sg.FileBrowse('ファイルを選択')],
        [sg.Frame('オプション', [
            [sg.Checkbox('話者分離', key='-SPEAKER-')],
            [sg.Checkbox('タイムスタンプ', key='-TIMESTAMP-')],
            [sg.Checkbox('句読点の自動挿入', key='-PUNCTUATION-')]
        ])],
        [sg.Button('文字起こし開始', key='-START-')],
        [sg.Text('状態: 待機中', key='-STATUS-')]
    ]

    right_column = [
        [sg.Text('文字起こし結果:')],
        [sg.Multiline(size=(60, 30), key='-RESULT-', disabled=True)]
    ]

    layout = [
        [
            sg.Column(left_column),
            sg.VSeparator(),
            sg.Column(right_column)
        ]
    ]

    return sg.Window('MocoVoice 文字起こし', layout, finalize=True)

def main():
    window = create_window()
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
        elif event == '-START-':
            window['-STATUS-'].update('状態: テスト中...')
            window['-RESULT-'].update('GUIのテスト\n表示テスト')
    
    window.close()

if __name__ == '__main__':
    main()
