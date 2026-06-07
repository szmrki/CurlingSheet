# CurlingSheet

*(English version: [README_EN.md](README_EN.md))*

カーリングのシート上にストーンを配置・表示できるアプリケーションです。
デスクトップアプリとしても、Python ライブラリとしても利用できます。

## クイックスタート
最新版は [Releases ページ](https://github.com/szmrki/CurlingSheet/releases) から入手できます。

- `CurlingSheet-vX.Y.Z.exe` をダウンロードしてください。

## 主な機能
- シート上の任意の位置にストーンを自由に配置
- 通常ルールとミックスダブルス(MD)の両方に対応
- ストーンを含めたシートを画像として保存
- ストーン配置を JSON ファイルにエクスポート
- JSON ファイルからストーン配置をインポート([JSON フォーマット](#json-フォーマット))
- ハウスの色をカスタマイズ
- MD ポイント(ポチ)・外枠の表示/非表示を切り替え
- ライブラリとして他スクリプトから利用(matplotlib や独自の描画にも対応)

## 動作環境
- Windows 11
- Python 3.12 以上
- ディスプレイ解像度: **高さ 945 ピクセル以上**
    > 注: アプリのウィンドウ高さは 945 ピクセル固定です。
    > 解像度が十分なのにウィンドウ全体が表示されない場合は、
    > [ディスプレイ設定](#ディスプレイ設定) を確認してください。

## pip でのインストール

~~~cmd
pip install git+https://github.com/szmrki/CurlingSheet.git
~~~

インストール後、次のコマンドでアプリを起動できます。

~~~cmd
curlingsheet
~~~

他のプロジェクトからライブラリとして利用することもできます。

~~~python
from curlingsheet.sheet import Sheet
from curlingsheet import sheet2pos as sp
~~~

matplotlib や独自レンダラでの描画、MD ポイント・外枠の切り替えについては
[ライブラリとして利用する](#ライブラリとして利用する) を参照してください。

## ソースからのインストール(Windows)

ソースコードからアプリを実行したい場合は次の手順に従ってください。

### リポジトリのクローン
~~~cmd
git clone https://github.com/szmrki/CurlingSheet.git
cd CurlingSheet
~~~

### 仮想環境の作成
~~~cmd
python -m venv .venv
.venv\Scripts\activate.bat      #cmd
.\.venv\Scripts\Activate.ps1    #PowerShell
(.venv) pip install -e .
~~~

### 動作確認
~~~cmd
python main.py
~~~

### .exe ファイルの作成
~~~cmd
pyinstaller main.spec
~~~

- `dist` フォルダを開くと `CurlingSheet.exe`(最新版)が生成されています。
- `build` フォルダは削除して構いません。

### ディスプレイ設定
アプリの実行ファイル向けに表示スケールを 100% にする手順です。

1. デスクトップを右クリックし、**ディスプレイ設定** を選択します。
1. **拡大縮小とレイアウト** のセクションまでスクロールします。
1. **拡大/縮小** のドロップダウンから **100%** を選択します。
> 注: スケール設定の変更はシステム全体に影響します。
> アプリを閉じた後は、推奨設定に戻すことをおすすめします。

## ライブラリとして利用する

描画は「**何を描くか**」と「**どう描くか**」の2層に分かれています。

1. **spec 層**(`curlingsheet.spec` / `curlingsheet.primitives`) … 描画器に
   依存しません。`build_sheet_spec()` がオプションとストーンから、画面座標系
   (原点は左上、y は下向き、単位は px、シートサイズ 300×600)の図形リスト
   (`Circle` / `Line` / `Rect`)を生成します。**この層は PyQt6 を読み込みません。**
2. **レンダラ層**(`curlingsheet.renderers`) … spec を受け取って実際に描画します。
   `render_qt`(PyQt6)はデスクトップアプリが使い、`render_matplotlib` は
   matplotlib の `Axes` に描きます。独自レンダラも図形リストを回すだけで作れます。

### オプション(MD ポイント / 外枠 / ハウスの色)

`SheetOptions` で描画内容を切り替えます。各トグルのデフォルトはデスクトップ
アプリと同じ見た目なので、何も指定しなければ従来通りの描画になります。

~~~python
from curlingsheet import SheetOptions

opts = SheetOptions(
    show_pochi=False,     # MD ポイント(ポチ)の表示 ON/OFF
    show_frame=False,     # 外枠の表示 ON/OFF
    show_background=True, # 背景(白塗り)の ON/OFF
    color12=2,            # 12 フィートサークルの色 (0=赤, 1=青, 2=緑)
    color4=0,             # 4 フィートサークルの色
)
~~~

> `SheetOptions` は「デフォルトと違う描き方をしたいとき」だけ使います。
> デフォルトでよければ `build_sheet_spec()` に渡さなくても構いません
> (内部でデフォルト値が使われます)。

---

## ライブラリでシート画像を作る

他のスクリプトからシート画像を生成する方法は2通りあります。用途に応じて選んでください。

| やりたいこと | おすすめ |
|------|------|
| デスクトップアプリと**寸分違わぬ画像**が欲しい / すでに Qt アプリ内 | **ルート A** |
| Qt 非依存のスクリプトで画像生成したい / matplotlib の図に組み込みたい | **ルート B** |
| GUI でマウス操作・編集したい | `Sheet` をウィジェットとして使用 |
| 独自の描画ライブラリで描きたい | [独自レンダラ](#独自レンダラを書く) |

### ルート A: `Sheet` + `grab()`(Qt レンダリング)

デスクトップアプリとピクセル単位で一致する画像が欲しい場合に使います。
GUI を表示しなくても `QApplication` は必要です。

~~~python
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"   # 画面を表示せずに動かす
from PyQt6.QtWidgets import QApplication
from curlingsheet.sheet import Sheet

app = QApplication([])

# オプションはコンストラクタ引数 or プロパティで指定
sheet = Sheet(show_pochi=False, show_frame=True)

# ストーンを追加 (x, y, team) ※ team は 0/"red"、1/"yellow"
sheet.add_stone([(149, 159, "red"), (120, 300, "yellow")])

sheet.grab().save("out.png")     # アプリの「画像のエクスポート」と同じ仕組み
~~~

`Sheet` 利用時は `SheetOptions` を自分で作る必要はありません。次のように
コンストラクタ引数やプロパティで設定できます。

~~~python
sheet = Sheet(show_pochi=False, show_frame=False)
sheet.show_pochi = True    # 変更すると自動で再描画される
sheet.show_frame = False
~~~

### ルート B: `build_sheet_spec` + `render_matplotlib`(Qt 不要)

スクリプトでの画像出力や、論文・資料用の図に向いています。
**PyQt6 をインストールせずに**動かせます。

任意依存の matplotlib をインストールしてください。

~~~cmd
pip install "curlingsheet[mpl]"
~~~

~~~python
import matplotlib
matplotlib.use("Agg")            # 画面を表示せずに保存する場合
import matplotlib.pyplot as plt
from curlingsheet import build_sheet_spec, SheetOptions
from curlingsheet.renderers.mpl import render_matplotlib

# x, y, team を持つオブジェクトなら何でもストーンとして渡せる
class Stone:
    def __init__(self, x, y, team):
        self.x, self.y, self.team = x, y, team

spec = build_sheet_spec(
    SheetOptions(show_pochi=False, show_frame=False),
    [Stone(149, 159, "red"), Stone(120, 300, "yellow")],
)

fig, ax = plt.subplots()
render_matplotlib(spec, ax)
fig.savefig("out.png", dpi=100)  # plt.show() で表示も可
~~~

`render_matplotlib(spec, ax, set_view=False)` を指定すると、表示範囲・
アスペクト比・軸の非表示を自分で制御できます。

### 独自レンダラを書く

レンダラは図形リストを回すだけで作れます(継承不要)。色は `RGBA(r, g, b, a)`
(各 0〜255、`None` は「塗りなし / 枠線なし」)です。

~~~python
from curlingsheet import build_sheet_spec, SheetOptions, Circle, Line, Rect

for shape in build_sheet_spec(SheetOptions()):
    if isinstance(shape, Circle):
        my_canvas.circle(shape.cx, shape.cy, shape.r, shape.fill, shape.stroke)
    elif isinstance(shape, Line):
        my_canvas.line(shape.x1, shape.y1, shape.x2, shape.y2, shape.color)
    elif isinstance(shape, Rect):
        my_canvas.rect(shape.x, shape.y, shape.w, shape.h, shape.fill, shape.stroke)
~~~

図形リストは描画順(背景 → 外枠 → ハウス → ライン → ポチ → ストーン)で並んでいます。
ハウスのリング径・各ラインの位置・MD ポイント座標などの寸法定数は
`curlingsheet.geometry` に集約されているので、必要に応じて参照できます。

## JSON フォーマット
### 例
~~~json
[
  {
    "x": 2.1049331104,
    "y": 32.1341428571,
    "team": "red"
  },
  {
    "x": -0.0079431438,
    "y": 37.7441008403,
    "team": "yellow"
  },
  ...
]
~~~

- `x` : ストーンの水平位置(float、範囲: -2.375 〜 2.375)
- `y` : ストーンの垂直位置(float、範囲: 32.004 〜 40.234)
- `team` : ストーンのチーム色(`"red"` または `"yellow"`)

座標系は [DigitalCurling3](https://digitalcurling.github.io/DigitalCurling3/md_coordinate.html)に従います。
