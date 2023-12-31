
# tcttクラスの作成
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from Bio import SeqIO, Entrez

import os
import itertools

Entrez.email='dutsumi@med.u-ryukyu.ac.jp'

class Seq_count:     
    def tutorial(self):
        """
        使い方
        """
        print("<基本的な関数>")
        print("1. gbkファイルを読み込む")
        print("gbk.read_gbk('gbkファイルのパス')", end="\n\n")
        print("2. mRNAのIDを確認する")
        print("gbk.get_mrna_ids()", end="\n\n")
        print("3. mRNAのIDをセットする")
        print("gbk.set_mrna_id('mRNAのID')", end="\n\n")
        print("4. 興味のある配列をセットする")
        print("gbk.set_interest_seq('興味のある配列')", end="\n\n")
        print("5. 興味のある配列のヒートマップを作成する")
        print("gbk.heatmap_hist()", end="\n\n")
        print("<その他の関数>")
        print("各イントロンの興味ある配列の個数: gbk.intron_bar()")
        print("各イントロンの興味ある配列の100塩基あたりの個数: gbk.intron_bar_base()")
        print("各エクソンの興味ある配列の個数: gbk.exon_bar()")
        print("各エクソンの興味ある配列の100塩基あたりの個数: gbk.exon_bar_base()")
        print("各イントロンの両端50塩基に存在する興味ある配列の個数: gbk.interest_seq_count_edge()")


    def read_gbk(self, gbk):
        """
        gbkファイルを読み込む   
        """
        self.record = SeqIO.read(gbk, "genbank")
        self.gbk = gbk
        # バリアントidをkeyに、エクソン数をvalueにした辞書を作成
        var_exon_dic = {}
        for id in [feature.qualifiers['transcript_id'][0] for feature in self.record.features if feature.type == "mRNA"]:
            for feature in self.record.features:
                if feature.type == 'mRNA' and feature.qualifiers['transcript_id'][0] == id:
                    var_exon_dic[id] = len([[int(part.start), int(part.end)] for part in feature.location.parts])
        # 最長のバリアントidを取得
        self.longest = sorted(var_exon_dic, key=var_exon_dic.get)[-1]
        # デフォルトのmrna_idを最長のバリアントidに設定
        self.mrna_id = self.longest
        print(f"デフォルト値として、最もエクソンの多い{self.longest}を設定")

    def get_gbk(self, gene_id):
        self.gene_id = gene_id
        """
        gene_idからgbkファイルを取得
        """
        # efetchで当該遺伝子の概要情報の取得
        handle = Entrez.efetch(db="gene", id=gene_id, rettype="gb", retmode="text")
        for i in handle:
            if "NC_" in i:
                info = i
        # 染色体番号の取得
        ls = info.split()
        # chrom = int(ls[ls.index('Chromosome')+1])
        chrom = ls[ls.index('Chromosome')+1]
        # プラス鎖、マイナス鎖に分けて、遺伝子の開始および終止位置の取得
        if "complement" in info:
            strand = 2
            for j in info.split():
                if "NC_" in j:
                    gene_acc = j
                elif ".." in j:
                    start, end = map(int, j[1:-1].split(".."))
        else:
            strand = 1
            for i in info.split(" "):
                if "NC_" in i:
                    gene_acc =  i
                elif ".." in i:
                    tmp = i.rstrip()
                    tmp = i[1:-2]
                    start, end = map(int, tmp.split(".."))
        # 遺伝子長の取得
        length = end - start + 1 
        # 各種変数の取得
        self.length = length
        self.start = start
        self.end = end
        self.strand = strand
        self.chrom = chrom
        # gbkデータの取得するか、するか、すでにファイルがあるかで分岐
        file = f"../data/gbk/{gene_id}.gb"
        if os.path.exists(file):
            pass
        else:
            handle = Entrez.efetch(db="nucleotide", id=gene_acc, rettype="gb", retmode="text", seq_start=start, seq_stop=end, strand=strand)
            data = handle.read()
            handle.close()
            # dataをファイルに書き込み
            with open(file, "w") as f:
                f.write(data)
        # gbkファイルの読み込み
        self.record = SeqIO.read(file, "genbank")
        # バリアントidをkeyに、エクソン数をvalueにした辞書を作成
        var_exon_dic = {}
        for id in [feature.qualifiers['transcript_id'][0] for feature in self.record.features if feature.type == "mRNA"]:
            for feature in self.record.features:
                if feature.type == 'mRNA' and feature.qualifiers['transcript_id'][0] == id:
                    var_exon_dic[id] = len([[int(part.start), int(part.end)] for part in feature.location.parts])
        # 最長のバリアントidを取得
        self.longest = sorted(var_exon_dic, key=var_exon_dic.get)[-1]
        # デフォルトのmrna_idを最長のバリアントidに設定
        self.mrna_id = self.longest
        print(f"デフォルト値として、最もエクソンの多い{self.longest}を設定")

    def gDNA_seq(self):
        """
        gbkファイルのgDNAの塩基配列を返す
        """
        return self.record.seq

    def set_mrna_id(self, mrna_id):
        """
        mRNAのIDを設定する
        """
        self.mrna_id = mrna_id
    
    def get_mrna_ids(self):
        """
        gbkファイルに登録されているmRNAのIDを取得する
        """
        return [feature.qualifiers['transcript_id'][0] for feature in self.record.features if feature.type == "mRNA"]
    
    def variant_exons(self):
        """
        各バリアントのエクソン数を返す
        """
        var_exon_dic = {}
        for id in [feature.qualifiers['transcript_id'][0] for feature in self.record.features if feature.type == "mRNA"]:
            for feature in self.record.features:
                if feature.type == 'mRNA' and feature.qualifiers['transcript_id'][0] == id:
                    var_exon_dic[id] = len([[int(part.start), int(part.end)] for part in feature.location.parts])
        return var_exon_dic

    def exon_list(self):
        """
        セットしたmRNAのIDのexon領域のリストを返す
        """
        for feature in self.record.features:
            if feature.type == 'mRNA' and feature.qualifiers['transcript_id'][0] == self.mrna_id:
                return [[int(part.start), int(part.end)] for part in feature.location.parts]
            
    def intron_list(self):
        """
        セットしたmRNAのIDのintron領域のリストを返す
        """
        for feature in self.record.features:
            if feature.type == 'mRNA' and feature.qualifiers['transcript_id'][0] == self.mrna_id:
                intron_list = []
                for i in range(len(feature.location.parts)-1):
                    intron_list.append([int(feature.location.parts[i].end), int(feature.location.parts[i+1].start)])
                return intron_list
            
    def exon_num(self):
        """
        セットしたmRNAのエクソンの個数を返す
        """
        return len(self.exon_list())
    
    def intron_num(self):
        """
        セットしたmRNAのイントロンの個数を返す
        """
        return len(self.intron_list())
    
    def exon_len(self, exon_num):
        """
        セットしたmRNAの指定されたエクソンの塩基数を返す
        """
        if exon_num > self.exon_num():
            return "エラー：そのエクソンは存在しません"
        else:
            return self.exon_list()[exon_num-1][1] - self.exon_list()[exon_num-1][0]

    def intron_len(self, intron_num):
        """
        セットしたmRNAの指定されたエクソンの塩基数を返す
        """
        if intron_num > self.intron_num():
            return "エラー：そのエクソンは存在しません"
        else:
            return self.intron_list()[intron_num-1][1] - self.intron_list()[intron_num-1][0]
        
    def exon_seq(self, exon_num):
        """
        セットしたmRNAの指定されたエクソンの配列を返す
        """
        if exon_num > self.exon_num():
            return "エラー：そのエクソンは存在しません"
        else:
            return self.gDNA_seq()[self.exon_list()[exon_num-1][0]:self.exon_list()[exon_num-1][1]]
        
    def intron_seq(self, intron_num):
        """
        セットしたmRNAの指定されたイントロンの配列を返す
        """
        if intron_num > self.intron_num():
            return "エラー：そのエクソンは存在しません"
        else:
            return self.gDNA_seq()[self.intron_list()[intron_num-1][0]:self.intron_list()[intron_num-1][1]]
    
    def set_interest_seq(self, interest_seq):
        """
        興味のあるある配列のセット
        """
        self.interest_seq = interest_seq

    def interest_seq_index(self):
        """
        gDNAの中の興味のあるある配列のインデックスのリストを返す
        """
        index = self.gDNA_seq().find(self.interest_seq)
        index_list = []
        while index != -1:
            index_list.append(index)
            index = self.gDNA_seq().find(self.interest_seq, index+1)
        return index_list
    
    def interest_seq_num(self):
        """
        gDNAの中の興味のあるある配列の個数を返す
        """
        return len(self.interest_seq_index())
    
    def set_array(self):
        """
        ヒートマップ作成のため塩基配列情報からアレイを作成
        """
        # エクソン領域を1、イントロン領域を0とする配列を作成
        self.seq_arr = np.zeros(len(self.gDNA_seq()))
        for exon in self.exon_list():
            self.seq_arr[exon[0]:exon[1]] = 1
        # 興味のある配列を2とし、それ以外を0とする配列を作成    
        self.interest_seq_arr = np.zeros(len(self.gDNA_seq()))
        for index in self.interest_seq_index():
            self.interest_seq_arr[index:index+len(self.interest_seq)] = 2
        # 2つの配列を足し合わせる
        self.seq_arr += self.interest_seq_arr
        # 2以上の値を2にする
        self.seq_arr[self.seq_arr >= 2] = 2
    
    def get_seq_arr(self):
        """
        アレイを返す
        """
        return self.seq_arr

    def trans_2d(self, arr, n):
        """
        1次元配列を2次元配列に変換
        """
        arr_concat = np.concatenate((arr, np.full(n-len(arr)%500, np.nan)))
        arr_2d = arr_concat.reshape(len(arr_concat)//n,n)
        return arr_2d
    
    def heatmap_hist(self, cols=500):
        """
        plotlyで左側にヒートマップ、右側にヒストグラムを作成
        --オプション--
        cols='列数'
        """
        # アレイの作成
        self.set_array()

        ## メタデータの作成
        # 塩基配列アレイ作成
        self.base_arr = np.array(list(self.gDNA_seq()))
        # 塩基配列の位置アレイ作成
        self.base_loc_arr = np.arange(len(self.gDNA_seq()))
        # エクソン、イントロン番号アレイ作成
        self.exon_intron_no_arr = np.full(len(self.gDNA_seq()), "Not difined")
        for i in range(self.exon_num()):
            if i != self.exon_num()-1:
                self.exon_intron_no_arr[self.exon_list()[i][0]:self.exon_list()[i][1]] = f"Ex_{i+1}"
                self.exon_intron_no_arr[self.exon_list()[i][1]:self.exon_list()[i+1][0]] = f"In_{i+1}"
            else:
                self.exon_intron_no_arr[self.exon_list()[i][0]:self.exon_list()[i][1]] = f"Ex_{i+1}"
        # 塩基配列、位置、エクソン、イントロン番号アレイを結合
        self.meta_arr = np.array([self.base_arr, self.base_loc_arr, self.exon_intron_no_arr]).T
        # colsで割り切れるようにnp.nanのリストで穴埋めをする
        self.meta_arr_round = np.concatenate([self.meta_arr, np.array([[np.nan]*3 for i in range(cols - len(self.meta_arr)%cols)])])
        self.meta_arr_2d = self.meta_arr_round.reshape(len(self.meta_arr_round)//cols, cols, 3)

        # 興味ある配列の位置を取得
        self.interest_seq_index_arr = self.interest_seq_index()

        # ２つの図の描画
        self.seq_arr_2d = self.trans_2d(self.seq_arr,cols)
        self.hh_fig = make_subplots(rows=1, cols=2)
        self.hh_fig.add_trace(go.Heatmap(z=self.seq_arr_2d, colorscale="Viridis", showscale=False, text=self.meta_arr_2d, hovertemplate="Base: %{text[0]}<br>Base location: %{text[1]}<br>Region number: %{text[2]}"), row=1, col=1)
        self.hh_fig.add_trace(go.Histogram(y=self.interest_seq_index_arr, nbinsy=200, marker=dict(color='rgba(54,130,128,1)')), row=1, col=2)
        self.hh_fig.update_layout(height=1000, width=1000, title_text=f"{self.interest_seq} sequence map and distribution of mouse Ttn gene", title_x=0.5 )
        self.hh_fig.update_yaxes(autorange="reversed")
        self.hh_fig.show()

    def save_fig(self):
        """
        self.hh_figをhtmlファイルとして保存
        """
        if not os.path.exists("fig"):
            os.makedirs("fig")
        self.hh_fig.write_html(f"fig/heatmap_{self.mrna_id}.html")

    def heatmap(self, cols=500):
        """
        plotlyでヒートマップを作成
        --オプション--
        cols='列数'
        """
        # アレイの作成
        self.set_array()

        ## メタデータの作成
        # 塩基配列アレイ作成
        self.base_arr = np.array(list(self.gDNA_seq()))
        # 塩基配列の位置アレイ作成
        self.base_loc_arr = np.arange(len(self.gDNA_seq()))
        # エクソン、イントロン番号アレイ作成
        self.exon_intron_no_arr = np.full(len(self.gDNA_seq()), "Not difined")
        for i in range(self.exon_num()):
            if i != self.exon_num()-1:
                self.exon_intron_no_arr[self.exon_list()[i][0]:self.exon_list()[i][1]] = f"Ex_{i+1}"
                self.exon_intron_no_arr[self.exon_list()[i][1]:self.exon_list()[i+1][0]] = f"In_{i+1}"
            else:
                self.exon_intron_no_arr[self.exon_list()[i][0]:self.exon_list()[i][1]] = f"Ex_{i+1}"
        # 塩基配列、位置、エクソン、イントロン番号アレイを結合
        self.meta_arr = np.array([self.base_arr, self.base_loc_arr, self.exon_intron_no_arr]).T
        # colsで割り切れるようにnp.nanのリストで穴埋めをする
        self.meta_arr_round = np.concatenate([self.meta_arr, np.array([[np.nan]*3 for i in range(cols - len(self.meta_arr)%cols)])])
        self.meta_arr_2d = self.meta_arr_round.reshape(len(self.meta_arr_round)//cols, cols, 3)

        # 興味ある配列の位置を取得
        self.interest_seq_index_arr = self.interest_seq_index()

        # ２つの図の描画
        self.seq_arr_2d = self.trans_2d(self.seq_arr,cols)
        self.h_fig = make_subplots(rows=1, cols=1)
        self.h_fig.add_trace(go.Heatmap(z=self.seq_arr_2d, colorscale="Viridis", showscale=False, text=self.meta_arr_2d, hovertemplate="Base: %{text[0]}<br>Base location: %{text[1]}<br>Region number: %{text[2]}"))
        self.h_fig.update_layout(height=1000, width=1000, title_text=f"{self.interest_seq} sequence map and distribution of mouse Ttn gene", title_x=0.5 )
        self.h_fig.update_yaxes(autorange="reversed")
        self.h_fig.show()

    def intron_bar(self):
        """
        各イントロンにおける入力された興味ある配列のカウントの棒グラフを作成
        """
        # アレイの作成
        self.set_array()
        # イントロン領域の塩基配列を取得
        self.intron_seq_arr = []
        for intron in self.intron_list():
            self.intron_seq_arr.append(self.gDNA_seq()[intron[0]:intron[1]])
        # 各イントロン領域の興味ある配列の個数をカウント
        self.intron_interest_seq_num_arr = []
        for i, seq in enumerate(self.intron_seq_arr):
            index = seq.find(self.interest_seq)
            index_list = []
            while index != -1:
                index_list.append(index)
                index = seq.find(self.interest_seq, index+1)
            self.intron_interest_seq_num_arr.append(len(index_list))
        # plotlyで棒グラフ作成
        self.fig = px.bar(x=[f"In_{i+1}" for i in range(len(self.intron_seq_arr))], y=self.intron_interest_seq_num_arr)
        self.fig.update_layout(title={'text': f"{self.interest_seq} sequence count in each intron of mouse Ttn gene",'y':0.97,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        self.fig.update_traces(hovertemplate="Intron number: %{x}<br>Count: %{y}")
        self.fig.update_xaxes(title_text="Intron number")
        self.fig.update_yaxes(title_text="Count")
        self.fig.show()

    def intron_bar_base(self):
        """
        各イントロンにおける入力された興味ある配列の100塩基あたりのカウントの棒グラフを作成
        """
        # アレイの作成
        self.set_array()
        # イントロン領域の塩基配列を取得
        self.intron_seq_arr = []
        for intron in self.intron_list():
            self.intron_seq_arr.append(self.gDNA_seq()[intron[0]:intron[1]])
        # アクイントロン領域の興味ある配列の個数をカウント
        self.intron_interest_seq_num_arr_100 = []
        for i, seq in enumerate(self.intron_seq_arr):
            index = seq.find(self.interest_seq)
            index_list = []
            while index != -1:
                index_list.append(index)
                index = seq.find(self.interest_seq, index+1)
            self.intron_interest_seq_num_arr_100.append(len(index_list)*100/len(seq))
        # plotlyで棒グラフ作成
        self.fig = px.bar(x=[f"In_{i+1}" for i in range(len(self.intron_seq_arr))], y=self.intron_interest_seq_num_arr_100)
        self.fig.update_layout(title={'text': f"{self.interest_seq} sequence count per 100 bases in each intron of mouse Ttn gene",'y':0.97,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        self.fig.update_traces(hovertemplate="Intron number: %{x}<br>Count per 100 bases: %{y}")
        self.fig.update_xaxes(title_text="Intron number")
        self.fig.update_yaxes(title_text="Count per 100 bases")
        self.fig.show()

    def exon_bar(self):
        """
        各エクソンにおける入力された興味ある配列のカウントの棒グラフを作成
        """
        # アレイの作成
        self.set_array()
        # エクソン領域の塩基配列を取得
        self.exon_seq_arr = []
        for exon in self.exon_list():
            self.exon_seq_arr.append(self.gDNA_seq()[exon[0]:exon[1]])
        # 各エクソン領域の興味ある配列の個数をカウント
        self.exon_interest_seq_num_arr = []
        for i, seq in enumerate(self.exon_seq_arr):
            index = seq.find(self.interest_seq)
            index_list = []
            while index != -1:
                index_list.append(index)
                index = seq.find(self.interest_seq, index+1)
            self.exon_interest_seq_num_arr.append(len(index_list))
        # plotlyで棒グラフ作成
        self.fig = px.bar(x=[f"Ex_{i+1}" for i in range(len(self.exon_seq_arr))], y=self.exon_interest_seq_num_arr)
        self.fig.update_layout(title={'text': f"{self.interest_seq} sequence count in each exon of mouse Ttn gene",'y':0.97,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        self.fig.update_traces(hovertemplate="Exon number: %{x}<br>Count: %{y}")
        self.fig.update_xaxes(title_text="Exon number")
        self.fig.update_yaxes(title_text="Count")
        self.fig.show()

    def exon_bar_base(self):
        """
        各エクソンにおける入力された興味ある配列の100塩基あたりのカウントの棒グラフを作成
        """
        # アレイの作成
        self.set_array()
        # エクソン領域の塩基配列を取得
        self.exon_seq_arr = []
        for exon in self.exon_list():
            self.exon_seq_arr.append(self.gDNA_seq()[exon[0]:exon[1]])
        # アクイントロン領域の興味ある配列の個数をカウント
        self.exon_interest_seq_num_arr_100 = []
        for i, seq in enumerate(self.exon_seq_arr):
            index = seq.find(self.interest_seq)
            index_list = []
            while index != -1:
                index_list.append(index)
                index = seq.find(self.interest_seq, index+1)
            self.exon_interest_seq_num_arr_100.append(len(index_list)*100/len(seq))
        # plotlyで棒グラフ作成
        self.fig = px.bar(x=[f"Ex_{i+1}" for i in range(len(self.exon_seq_arr))], y=self.exon_interest_seq_num_arr_100)
        self.fig.update_layout(title={'text': f"{self.interest_seq} sequence count per 100 bases in each exon of mouse Ttn gene",'y':0.97,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        self.fig.update_traces(hovertemplate="Exon number: %{x}<br>Count per 100 bases: %{y}")
        self.fig.update_xaxes(title_text="Exon number")
        self.fig.update_yaxes(title_text="Count per 100 bases")
        self.fig.show()

    def interest_seq_count_edge(self):
        """
        各イントロンの両端50塩基に存在する興味ある配列をカウント
        """
        # アレイの作成
        self.set_array()
        # イントロン領域の塩基配列を取得
        self.intron_seq_arr = []
        for intron in self.intron_list():
            self.intron_seq_arr.append(self.gDNA_seq()[intron[0]:intron[1]])
        # イントロン領域の両端50塩基に存在する興味ある配列の個数をカウント
        self.intron_interest_seq_num_edge_arr = []
        for i, seq in enumerate(self.intron_seq_arr):
            index = seq.find(self.interest_seq)
            index_list = []
            while index != -1:
                if index < 50 or index > len(seq)-50:
                    index_list.append(index)
                index = seq.find(self.interest_seq, index+1)
            self.intron_interest_seq_num_edge_arr.append(len(index_list))
        # plotlyで棒グラフ作成
        self.fig = px.bar(x=[f"In_{i+1}" for i in range(len(self.intron_seq_arr))], y=self.intron_interest_seq_num_edge_arr)
        self.fig.update_layout(title={'text': f"{self.interest_seq} sequence count in each intron edge of mouse Ttn gene",'y':0.97,'x':0.5,'xanchor': 'center','yanchor': 'top'})
        self.fig.update_traces(hovertemplate="Intron number: %{x}<br>Count: %{y}")
        self.fig.update_xaxes(title_text="Intron number")
        self.fig.update_yaxes(title_text="Count")
        self.fig.show()

    def create_motif_dic(self, n=4):
        # n個の塩基配列の組み合わせを作成
        bases = ["A", "C", "T", "G"]
        combinations = list(itertools.product(bases, repeat=n))
        sequences = [''.join(comb) for comb in combinations]
        # keyを組み合わせとした辞書をさくせい
        dic = {}
        for i in sequences:
            dic[i] = 0
        return dic
    
    def intron_motif_stats(self, intron=1, n=4):
        # 配列の先頭から順番にn個の塩基配列をカウント
        dic = self.create_motif_dic(n=n)
        seq = str(self.intron_seq(intron))
        for i in range(len(seq)-n+1):
            
            dic[seq[i:i+n]] += 1

        df = pd.DataFrame({'Number':dic.values()})
        df.index = dic.keys()
        return df

    def transcript_variants(self, title="Transcript variants"):
        """
        # gbkに保存されているバリアントのエクソン領域の可視化
        """
        # バリアントIDを全エクソン数順に降順に並べ替える
        tv = Seq_count()
        tv.get_gbk(self.gene_id)
        var_exon = {}
        for i in tv.get_mrna_ids():
            tv.set_mrna_id(i)
            var_exon[i] = tv.exon_num()
        var_exon_sort = sorted(var_exon, key=var_exon.get, reverse=True)

        # 各バリアントの情報取得
        e_region = [] # エクソン領域情報
        e_numb = []#  エクソン番号
        y_ind = []# Y軸のインデックス
        var_id = [] # トランスクリプトバリアントID
        all_exon = [] # 全エクソン数
        for n,i in enumerate(var_exon_sort):
                tv.set_mrna_id(i)
                for j in tv.exon_list():
                    e_region += j +[None]
                for k in range(tv.exon_num()):
                    e_numb += [f"Exon{k+1}"]*3
                y_ind += [n for l in range(len(tv.exon_list())*3)]
                var_id += [i for m in range(len(tv.exon_list())*3) ]
                all_exon += [f"Total exon: {tv.exon_num()}" for o in range(len(tv.exon_list())*3)]
        fig = px.line(x=e_region, y=y_ind, title=title, hover_name=[i+"<br><br>"+j+"<br><br>"+k for i,j,k in zip(var_id, e_numb, all_exon)])
        fig.update_traces(line=dict(color="RoyalBlue", width=10))
        fig.show()

    def motif_std_bin(self, motif, bins=20):
        all_intron = ""
        for i in range(self.intron_num()):
            all_intron += self.intron_seq(i+1)

        motif_list = [0]*(len(all_intron)-len(motif))
        for i in range(len(all_intron)-len(motif)):
            if all_intron[i:i+len(motif)] == motif:
                motif_list[i] = 1

        # motifをn個のサブリストに分割
        bins = 20
        length = len(motif_list)
        base = length // bins
        remainder = length % bins

        # base個の要素を持つn個のリストと、余りを配分
        split_lists = [motif_list[i * base + min(i, remainder):(i + 1) * base + min(i + 1, remainder)] for i in range(bins)]

        one_counts = []
        for i in split_lists:
            one_counts.append(i.count(1))

        # 合計を100として標準偏差を求める
        arr = np.array(one_counts)*(100/np.array(one_counts).sum())
        return arr.std()       