from ast import While
from cmath import inf
from concurrent.futures import thread
from faulthandler import disable
from operator import index, le
from platform import node
import random
import tkinter
import time
import threading
import math
from turtle import distance, down, left, pos, right
from unittest import case


"""
---配列内のブロック情報の記録形式---
壁  :wall
通路:passage
現在作成中の壁:extendingWall
"""

#キャンバスの大きさ
CANVAS_WIDTH = 630
CANVAS_HEIGHT = 510

#  !!注意!!  縦、横ともに5以上の奇数に設定
MAZE_WIDTTH = 31
MAZE_HEIGHT = 25

#1回あたりのスリープ時間
SLEEP_TIME = 0.01

#2次元配列を作成する
maze = [["wall" for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTTH)]

#クラスの定義
class Application(tkinter.Frame):
    #コンストラクタの定義
    def __init__(self, root=None):
        #継承したオブジェクトの__init__を実行
        super().__init__(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,borderwidth=0, relief='groove')
        self.root = root
        self.place(x=85, y=30)
        
        #現在、迷路を作成中かどうかを記録する変数
        self.playing = False
        
        #迷路が作成されているかの変数
        self.mazeCompleted = False
        
        #Canvasの作成(枠内に表示)
        self.canvas = tkinter.Canvas(self,bg="#ffffff" , width=CANVAS_WIDTH, height=CANVAS_HEIGHT, highlightthickness=0)     #highlightthicknessはCanvasの囲み線をなくすため
        self.canvas.place(x=0, y=0)
        
        #壁伸ばし法Buttonの作成
        self.extend_btn = tkinter.Button(root, width=25, height=2)
        self.extend_btn["text"] = "壁伸ばし法"
        self.extend_btn["command"] = self.exWallButton_clicked
        self.extend_btn.place(x=100, y=600)
        
        #穴掘り法Buttonの作成
        self.digging_btn = tkinter.Button(root, width=25, height=2)
        self.digging_btn["text"] = "穴掘り法"
        self.digging_btn["command"] = self.DigWallButton_clicked
        self.digging_btn.place(x=300, y=600)
        
        #棒倒し法Buttonの作成
        self.topple_btn = tkinter.Button(root, width=25, height=2)
        self.topple_btn["text"] = "棒倒し法"
        self.topple_btn["command"] = self.ToppleStickButton_clicked
        self.topple_btn.place(x=500, y=600)
        
        #ダイクストラ法Buttonの作成
        self.dijkstra_btn = tkinter.Button(root, width=25, height=2)
        self.dijkstra_btn["text"] = "ダイクストラ法"
        self.dijkstra_btn["command"] = self.DijkstraButton_clicked
        self.dijkstra_btn.place(x=200, y=650)
        
        #A*アルゴリズムButtonの作成
        self.aStar_btn = tkinter.Button(root, width=25, height=2)
        self.aStar_btn["text"] = "A*アルゴリズム"
        self.aStar_btn["command"] = self.AStarButton_clicked
        self.aStar_btn.place(x=400, y=650)
     
        
    #迷路作成----------------------------------------------------------------------------------------
    
    #迷路を表示するメソッド
    def MakeMazeMap(self):
        #迷路ブロックの描画
        for i in range(MAZE_HEIGHT):
            for j in range(MAZE_WIDTTH):
                if maze[j][i] == "wall":
                    self.MakeBlock(j, i, "black", "wall")
                else:
                    self.MakeBlock(j, i, "white", "passage")
        
        
    #迷路のブロックを作成するメソッド       引数:(始点X座標, 始点Y座標, 色, タグ)
    def MakeBlock(self, x, y, color, tag):
        self.canvas.create_rectangle( x * CANVAS_WIDTH / MAZE_WIDTTH,
                                      y * CANVAS_HEIGHT / MAZE_HEIGHT,
                                      (x + 1) * CANVAS_WIDTH / MAZE_WIDTTH,
                                      (y + 1) * CANVAS_HEIGHT / MAZE_HEIGHT,
                                      width=0,
                                      fill=color,
                                      tag=tag)

    #スタートとゴールを作成するメソッド
    def MakeStartAndGoal(self):
        self.MakeBlock(1, 1, "yellow", "start")
        self.MakeBlock(MAZE_WIDTTH - 2, MAZE_HEIGHT - 2, "red", "goal")
        

    #壁伸ばし法のボタンが押されたときの処理--------------------------------------------------------
    def exWallButton_clicked(self):
        if not self.playing:
            self.playing = True
            thread = threading.Thread(target=self.ExtendWallMethod)
            thread.start()
            self.extend_btn["state"] = "disable"
        
    #壁伸ばし法
    def ExtendWallMethod(self):
        print("壁伸ばし法で迷路を作成します")
        #初期化
        for i in range(MAZE_HEIGHT):
            for j in range(MAZE_WIDTTH):
                maze[j][i] = "wall"
        for i in range(MAZE_HEIGHT - 2):
            for j in range(MAZE_WIDTTH - 2):
                maze[j + 1][i + 1] = "passage"       
                    
        self.MakeMazeMap()
        
        #壁を設置する候補を配列にまとめる
        candidate = []
        for i in range(2, MAZE_HEIGHT - 1, 2):
            for j in range(2, MAZE_WIDTTH - 1, 2):
                candidate.append([j, i])
        #順番をシャッフルする
        random.shuffle(candidate)
        
        #上下左右の数値を定義する
        dir = [[0, 1], [0, -1], [-1, 0], [1, 0]]
        
        #候補の座標を順に処理する
        for i in range(len(candidate)) :
            pos_x = candidate[i][0]
            pos_y = candidate[i][1]
            
            #現在の座標が壁なら次の候補の座標に移る
            if maze[pos_x][pos_y] == "wall":
                continue
            
            #現在の座標を壁にする
            maze[pos_x][pos_y] = "extendingWall"
            #拡張の終了フラグをfalseにする
            finish = False
            
            #壁を伸ばす処理
            while True:
                random.shuffle(dir)
                for i in range(len(dir)):
                    one_x = pos_x + dir[i][0]
                    one_y = pos_y + dir[i][1]
                    two_x = one_x + dir[i][0]
                    two_y = one_y + dir[i][1]
                    #壁を伸ばせるかを確認する
                    if maze[one_x][one_y] == "passage" and maze[two_x][two_y] != "extendingWall":
                        #2マス先が元から壁なら拡張の終了フラグをtrueにする
                        if maze[two_x][two_y] == "wall":
                            finish = True
                        
                        #壁を伸ばす
                        maze[one_x][one_y] = "extendingWall"
                        maze[two_x][two_y] = "extendingWall"
                        
                        #壁を表示する
                        self.MakeBlock(pos_x, pos_y, "black", "wall")
                        self.MakeBlock(one_x, one_y, "black", "wall")
                        self.MakeBlock(two_x, two_y, "black", "wall")
                        
                        #現在地を変更する
                        pos_x = two_x
                        pos_y = two_y
                        
                        time.sleep(SLEEP_TIME)
                        
                        break   
                    #どの方向にも進めなくなったら拡張の終了フラグをtrueにする  
                    if i == 3:
                        finish = True
                if finish:
                    for i in range(MAZE_HEIGHT):
                        for j in range(MAZE_WIDTTH):
                            if maze[j][i] == "extendingWall":
                                maze[j][i] = "wall"
                    break
         
        print("迷路作成完了!")
        self.mazeCompleted = True
        self.playing = False
        self.extend_btn["state"] = "normal"
        self.MakeStartAndGoal()
        
    #穴掘り法のボタンが押されたときの処理---------------------------------------------------------
    def DigWallButton_clicked(self):
        if not self.playing:
            self.playing = True
            thread = threading.Thread(target=self.DiggingMethod)
            thread.start()
            self.digging_btn["state"] = "disable"
        
    #穴掘り法
    def DiggingMethod(self):
        print("穴掘り法で迷路を作成します")
        #初期化
        for i in range(MAZE_HEIGHT):
            for j in range(MAZE_WIDTTH):
                maze[j][i] = "wall"
        self.MakeMazeMap()
        
        #掘り始める座標を決める
        dig_x = random.randint(0, int((MAZE_WIDTTH - 2) / 2)) * 2 + 1
        dig_y = random.randint(0, int((MAZE_HEIGHT - 2) / 2)) * 2 + 1
        
        #穴掘りを始める
        maze[dig_x][dig_y] = "passage"
        self.MakeBlock(dig_x, dig_y, "white", "passage")
        self.Dig(dig_x, dig_y)     
        
        print("迷路作成完了!")
        self.mazeCompleted = True
        self.playing = False
        self.digging_btn["state"] = "normal"
        self.MakeStartAndGoal()
        
    #穴を掘るメソッド 引数:(現在地のX座標, 現在地のY座標)
    def Dig(self, pos_x, pos_y):
        #その方向を確認したか記録する変数
        up = False
        down = False
        left = False
        right = False
        
        #すべての方向を確認するまで行う
        while not up or not down or not left or not right:
            #ランダムに進行方向を決める
            dir = random.randint(0,3)
            
            #選ばれた方向に進めるなら進める
            if dir == 0:
                if pos_y - 2 >= 0 and maze[pos_x][pos_y - 2] == "wall":
                    self.ShowDigWall(pos_x, pos_y, 0, -1)
                up = True
            elif dir == 1:
                if pos_y + 2 < MAZE_HEIGHT and maze[pos_x][pos_y + 2] == "wall":
                    self.ShowDigWall(pos_x, pos_y, 0, 1)
                down = True
            elif dir == 2:
                if pos_x - 2 >= 0 and maze[pos_x - 2][pos_y] == "wall":
                    self.ShowDigWall(pos_x, pos_y, -1, 0)
                left = True
            elif dir == 3:
                if pos_x + 2 < MAZE_WIDTTH and maze[pos_x + 2][pos_y] == "wall":
                    self.ShowDigWall(pos_x, pos_y, 1, 0)
                right = True
    
    #穴を掘って、描画するメソッド　引数:(現在地のX座標, 現在地のY座標, X方向の移動量, Y方向の移動量)
    def ShowDigWall(self, pos_x, pos_y, dx, dy):
        #1,2マス先の座標を計算する
        one_x = pos_x + dx
        one_y = pos_y + dy
        two_x = pos_x + dx * 2
        two_y = pos_y + dy * 2
        
        #1,2マス先まで掘る
        maze[one_x][one_y] = "passage"
        maze[two_x][two_y] = "passage"
        self.MakeBlock(one_x, one_y, "white", "passage")
        self.MakeBlock(two_x, two_y, "white", "passage")
        
        time.sleep(SLEEP_TIME)
        
        #現在地を変更して掘る
        self.Dig(two_x, two_y)
    
    #棒倒し法のボタンが押されたときの処理---------------------------------------------------------
    def ToppleStickButton_clicked(self):
        if not self.playing:
            self.playing = True
            thread = threading.Thread(target=self.ToppleStickMethod)
            thread.start()
            self.topple_btn["state"] = "disable"
    
    #棒倒し法
    def ToppleStickMethod(self):
        print("棒倒し法で迷路を作成します")
        #初期化
        pivot = []
        for i in range(MAZE_HEIGHT):
            for j in range(MAZE_WIDTTH):
                maze[j][i] = "wall"
        for i in range(MAZE_HEIGHT - 2):
            for j in range(MAZE_WIDTTH - 2):
                maze[j + 1][i + 1] = "passage"
        for i in range(int((MAZE_HEIGHT - 3) / 2)):
            for j in range(int((MAZE_WIDTTH - 3) / 2)):
                point_x = (j + 1) * 2
                point_y = (i + 1) * 2  
                pivot.append([point_x, point_y])
                maze[point_x][point_y] = "wall" 
        self.MakeMazeMap()

        for i in range(len(pivot)):
            if pivot[i][1] != 2:
                #下左右の数値を定義する
                dir3 = [[0, 1], [-1, 0], [1, 0]]
                
                random.shuffle(dir3)
                
                #下左右の方向を調べる
                for j in range(len(dir3)):
                    topple_x = pivot[i][0] + dir3[j][0]
                    topple_y = pivot[i][1] + dir3[j][1]
                    if maze[topple_x][topple_y] != "wall":
                        maze[topple_x][topple_y] = "wall"
                        self.MakeBlock(topple_x, topple_y, "black", "wall")
                        break
            else:
                #上下左右の数値を定義する
                dir4 = [[0, -1], [0, 1], [-1, 0], [1, 0]]
                
                random.shuffle(dir4)
                
                #上下左右の方向を調べる
                for j in range(len(dir4)):
                    topple_x = pivot[i][0] + dir4[j][0]
                    topple_y = pivot[i][1] + dir4[j][1]
                    if maze[topple_x][topple_y] != "wall":
                        maze[topple_x][topple_y] = "wall"
                        self.MakeBlock(topple_x, topple_y, "black", "wall")
                        break
            
            time.sleep(SLEEP_TIME)
            
        print("迷路作成完了!")
        self.mazeCompleted = True
        self.playing = False
        self.topple_btn["state"] = "normal"
        self.MakeStartAndGoal()
        
    #経路探索------------------------------------------------------------------------------------------
        
    #テキストを表示するメソッド     引数:(X座標, Y座標, 表示するテキスト)
    def DrawText(self, x, y, text):
        self.canvas.create_text((x + 0.5) * CANVAS_WIDTH / MAZE_WIDTTH,
                                (y + 0.5) * CANVAS_HEIGHT / MAZE_HEIGHT,
                                text=text, 
                                anchor="center",
                                font=("メイリオ", int((10 * 21 / MAZE_WIDTTH + 1) * (1 + (2 - len(str(text))) * 0.2)), "bold"),
                                tag="text")
        
    #求めた経路を表示するメソッド   引数:(ノード情報が入った配列)
    def DrawRoute(self, node):
        #ゴールから始める
        pos_x = MAZE_WIDTTH - 2
        pos_y = MAZE_HEIGHT - 2
        
        #スタートに戻るまで繰り返す
        for i in range (MAZE_HEIGHT * MAZE_WIDTTH):
            #1つ前の地点の座標を取得する
            before_x = node[pos_x][pos_y]["before_x"]
            before_y = node[pos_x][pos_y]["before_y"]
            
            #現在地を変更する
            pos_x = before_x
            pos_y = before_y
            
            #スタート地点に戻ったら終了   
            if node[pos_x][pos_y]["before_x"] == 0 and node[pos_x][pos_y]["before_y"] == 0:
                break
        
            #現在地を表示する
            self.MakeBlock(pos_x, pos_y, "green", "ans_route")
                
                
    #ダイクストラ法のボタンが押されたときの処理---------------------------------------------------------
    def DijkstraButton_clicked(self):
        if not self.playing and self.mazeCompleted:
            self.playing = True
            thread = threading.Thread(target=self.DijkstraMethod)
            thread.start()
            self.dijkstra_btn["state"] = "disable"
    
    #ダイクストラ法
    def DijkstraMethod(self):
        print("ダイクストラ法で最短経路を探索します")
        self.canvas.delete("text")
        self.canvas.delete("ans_route")
        
        #各座標の情報(壁か通路か, 確定済みか,ひとつ前の座標)を持った配列
        node = [[{"status":maze[j][i], "checked":False, "before_x":0, "before_y":0} for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTTH)]
        
        #各ノードの時間を保存する配列(Y座標 * MAZE_WIDTH + X座標)
        required_time = [inf for i in range(MAZE_WIDTTH * MAZE_HEIGHT)]
        
        #確定したノードの数を記録する変数
        check_count = 0
        
        #存在するノードの数を記録する変数
        all_node = 0
        
        #調べる必要があるノードの数を数える
        for i in range(MAZE_HEIGHT):
            for j in range(MAZE_WIDTTH):
                if node[j][i]["status"] == "passage":
                    all_node += 1
        
                
        #スタート地点に0を書き込む
        required_time[MAZE_WIDTTH + 1] = 0
              
        #すべての地点を調べるまで続ける
        while check_count < all_node:
            #最小値のインデックスを取得する
            min_index = required_time.index(min(required_time))
            
            #確認中の座標を計算
            pos_x = int(min_index % MAZE_WIDTTH)
            pos_y = int(min_index / MAZE_WIDTTH)
            
            #ウィンドウに表示
            self.DrawText(pos_x, pos_y, required_time[min_index])
            
            #確定させる
            node[pos_x][pos_y]["checked"] = True
            check_count += 1
            
            #上下左右の数値を定義する
            dir = [[0, -1], [0, 1], [-1, 0], [1, 0]]
            
            
            #上下左右の方向を調べる
            for i in range(len(dir)):
                next_x = pos_x + dir[i][0]
                next_y = pos_y + dir[i][1]
                
                #次の座標までの時間が書かれている配列番号を計算する
                next_timeIndex = next_y * MAZE_WIDTTH + next_x
                
                #次の座標が通路で未確定の地点かつ元の時間よりも速いならその地点までの時間を書き換える
                if node[next_x][next_y]["status"] == "passage" and node[next_x][next_y]["checked"] == False:
                    if required_time[min_index] + 1 < required_time[next_timeIndex]:
                        #次の座標までの時間を書き換える
                        required_time[next_timeIndex] = required_time[min_index] + 1
                        node[next_x][next_y]["before_x"] = pos_x
                        node[next_x][next_y]["before_y"] = pos_y
                        
                        time.sleep(SLEEP_TIME)
                       
            #調べた地点の時間が最小値にならないように無限に戻す 
            required_time[min_index] = inf
        
        print("経路探索完了!")
        self.playing = False
        self.dijkstra_btn["state"] = "normal"  
        self.DrawRoute(node) 
        
        
    #A*アルゴリズムのボタンが押されたときの処理----------------------------------------------------------------
    def AStarButton_clicked(self):
        if not self.playing and self.mazeCompleted:
            self.playing = True
            thread = threading.Thread(target=self.AStarMethod)
            thread.start()
            self.aStar_btn["state"] = "disable"    
    
    #A*アルゴリズム
    def AStarMethod(self):
        print("A*アルゴリズムで最短経路を探索します")
        self.canvas.delete("text")
        self.canvas.delete("ans_route")
        
        #各座標の情報(壁か通路か, 確認済みか, スタートからの距離, ひとつ前の座標)を持った配列
        node = [[{"status":maze[j][i], "checked":False, "distance":0, "before_x":0, "before_y":0} for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTTH)]
        
        #各ノードのコストを保存する配列(Y座標 * MAZE_WIDTH + X座標)
        cost = [inf for i in range(MAZE_WIDTTH * MAZE_HEIGHT)]
        
        #スタートにコストを書き込む
        cost[MAZE_WIDTTH + 1] = self.CalcDistance(1, 1)
        
        pos_x = 1
        pos_y = 1
        
        #ゴールに着くまで繰り返す
        while pos_x != MAZE_WIDTTH - 2 or pos_y != MAZE_HEIGHT - 2:
            #最小値のインデックスを取得する
            min_index = cost.index(min(cost))
            
            #確認中の座標を計算
            pos_x = int(min_index % MAZE_WIDTTH)
            pos_y = int(min_index / MAZE_WIDTTH)
            
            #ウィンドウに表示
            self.DrawText(pos_x, pos_y, cost[min_index])
        
            #確認済みにする
            node[pos_x][pos_y]["checked"] = True
            
            #上下左右の数値を定義する
            dir = [[0, -1], [0, 1], [-1, 0], [1, 0]]
            
            
            #上下左右の方向を調べる
            for i in range(len(dir)):
                next_x = pos_x + dir[i][0]
                next_y = pos_y + dir[i][1]
                
                #次の座標までの時間が書かれている配列番号を計算する
                next_timeIndex = next_y * MAZE_WIDTTH + next_x
                
                #次の座標が通路で未確認の地点ならスタートからの距離とコストを書き込む
                if node[next_x][next_y]["status"] == "passage" and node[next_x][next_y]["checked"] == False:
                    #スタートからの距離を記録する
                    node[next_x][next_y]["distance"] = node[pos_x][pos_y]["distance"] + 1
                    
                    #コストを計算する
                    cost[next_timeIndex] = node[next_x][next_y]["distance"] + self.CalcDistance(next_x, next_y)
                    node[next_x][next_y]["checked"] = True
                    
                    #どの座標からつながっている場所か記録する
                    node[next_x][next_y]["before_x"] = pos_x
                    node[next_x][next_y]["before_y"] = pos_y
            
            #調べた地点のコストが最小値にならないように無限に戻す 
            cost[min_index] = inf
            
            time.sleep(SLEEP_TIME)
            
        print("経路探索完了!")
        self.playing = False
        self.aStar_btn["state"] = "normal"  
        self.DrawRoute(node)       
    
    #ゴールまでの直線距離を求め、その距離を返すメソッド     引数:(X座標, Y座標)
    def CalcDistance(self, x, y):
        dis_x = MAZE_WIDTTH - 2 - x
        dis_y = MAZE_HEIGHT - 2 - y
        
        #ゴールまでの直線距離を計算する
        distance = int(math.sqrt(dis_x ** 2 + dis_y ** 2))
        
        return distance
    

#画面表示用--------------------------------------------------------------------------------------------------
root = tkinter.Tk()
#表示ウィンドウの設定
root.title("迷路")
root.geometry("800x700")

app = Application(root=root)
app.mainloop()
