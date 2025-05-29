import pandas as pd
import cv2
import numpy as np

WIDTH = 299
TLINE = 159
BACKLINE = 40
CENTER_X = 149
DIAMETER = 239
DC3_WIDTH = 4.75
DC3_TLINE = 38.405
DC3_BACKLINE = 40.234
DC3_CENTER_X = 0
DC3_RADIUS = 1.829

def get_stones_pos(img_path=None, img=None) -> pd.DataFrame: 
     if isinstance(img_path, str) and img_path.strip():
          img = cv2.imread(img_path)
     if img is None:
          raise ValueError(f"Failed to load image from path: {img_path}")

    #ハウスが画像の上側に来るように条件付きで上下反転を行う
     row20 = img[20,:,:]
     black_pixels = np.all(row20==0, axis=1) 
     if np.all(black_pixels[1:WIDTH]):  #左右1ピクセルが余白の可能性があるため
          img = cv2.flip(img, 0)
     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #RGBに変換

     #1. 特定のRGB値を持つエリアを抽出
     #https://github.com/jwmyslik/curling-analytics/blob/master/pdf_parsing_functions.py
     #のget_rock_positionsメソッドを参照
     red_bin = cv2.inRange(img, (240,0,0), (255,0,0)) #赤を取得
     yellow_bin = cv2.inRange(img, (240,192,0), (255,255,30)) #黄色を取得

     #2. エリアの輪郭情報を取得
     rock_bin_dict = {"red": red_bin, "yellow":yellow_bin}.items()

     row_list = []
     for color, rock_bin in rock_bin_dict:
          #輪郭情報を取得する
          #cv2.RETR_TREE: 輪郭の階層構造をすべて取得する
          #cv2.CHAIN_APPROX_NONE: 輪郭の点をすべて保持する
          #contours: タプル、各要素は輪郭を構成する座標のnp.array
          #hierarchy: 輪郭の階層構造
          contours, hierarchy = cv2.findContours(rock_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

          #3. 重心のRGB値の条件を満たさないものを除外(中空の円)
          #本アプリでは不必要のため削除済

          for cnt in contours:
               M = cv2.moments(cnt) #各ストーンのモーメントを求める
               #m00: 面積, m10: x座標に関する1次モーメント, m01: y座標に関する1次モーメント
               cx = M['m10']/max(M['m00'], 1) #重心のx座標を取得
               cy = M['m01']/max(M['m00'], 1) #重心のy座標を取得
                    
               row_list.append({"team":color, "x":cx, "y":cy, "size":M['m00']})
          
     #空のデータフレームになった際にバグらないようにするためcolumnsを明示的に指定
     stones = pd.DataFrame(row_list, columns=["team", "x", "y", "size"]) 

     if not stones.empty:
          #4. ストーンのサイズが範囲外のものを除外(未使用のストーンを除く)
          stones = stones[stones["size"] >= 50].reset_index(drop=True)

          #5. エリア外のものを除外(使用済みのストーンを除く)
          stones = stones[(19 < stones["y"]) & (stones["y"] <= 581)].reset_index(drop=True)
          #6. 残った輪郭情報の重心をストーンの座標とする
     
     return stones

#7. デジタルカーリングの座標系に変換する
def curlit_to_dc3(stones: pd.DataFrame) -> pd.DataFrame:
     dc3_stones = stones.copy()
     XA = (DC3_WIDTH / WIDTH); XB = (DC3_WIDTH / 2)   
     YA = ((DC3_TLINE - DC3_BACKLINE) / (TLINE - BACKLINE))
     YB = DC3_TLINE - YA * TLINE

     dc3_stones["x"] = XA * dc3_stones["x"] - XB
     dc3_stones["y"] = YA * dc3_stones["y"] + YB

     return dc3_stones

#appx. Curlitの座標系に変換する
def dc3_to_curlit(dc3_stones: pd.DataFrame) -> pd.DataFrame:
     stones = dc3_stones.copy()
     XA = (WIDTH / DC3_WIDTH); XB = (WIDTH / 2)
     YA = ((TLINE - BACKLINE) / (DC3_TLINE - DC3_BACKLINE))
     YB = TLINE - YA * DC3_TLINE

     stones["x"] = XA * stones["x"] + XB
     stones["y"] = YA * stones["y"] + YB

     return stones

#appx. jsonに変換する
def df_to_json(df, filename) -> None:
     df[["x", "y", "team"]].to_json(filename, orient="records", indent=2)

#appx. 中心との距離を計算する
def distance_pow(df, is_dc3=False) -> pd.Series:
     if is_dc3:
          dist = (df["x"] - DC3_CENTER_X)**2 + (df["y"] - DC3_TLINE)**2
     else:
          dist = (df["x"] - CENTER_X)**2 + (df["y"] - TLINE)**2
     return dist

#appx. No.1ストーンを取得する
def get_no1_stone(df, is_dc3=False) -> tuple[str,float,float]:
    dist = distance_pow(df, is_dc3)
    min_stone = df.loc[dist.idxmin()]
    return min_stone["team"], min_stone["x"], min_stone["y"]

#appx. ハウスにストーンがあるか判定する
def is_in_house(df, is_dc3=False) -> pd.Series:
     dist = distance_pow(df, is_dc3)
     if is_dc3:
          STONE_RADIUS = 0.145
          return dist <= (DC3_RADIUS + STONE_RADIUS + 0.0255)**2
     else:
          STONE_RADIUS = 9.5
          return dist <= (DIAMETER / 2 + STONE_RADIUS)**2

#appx. 得点を計算する
def score(df, is_dc3=False) -> tuple[str, int]:
     in_house = is_in_house(df, is_dc3)
     if in_house.any():
          in_house_index = in_house[in_house].index
          df_in_house = df.loc[in_house_index]  #ハウス内のストーンのみ抽出
          df_in_house["dist"] = distance_pow(df_in_house, is_dc3)
          df_in_house = df_in_house.sort_values(by="dist")
          no1_team = df_in_house["team"].iloc[0]
          #no1_teamと一致する色が何回続くかを累積積を用いて判定し、合計する
          no1_score = (df_in_house["team"] == no1_team).cumprod().sum()
          return no1_team, no1_score
     else:  
          return "Draw", 0