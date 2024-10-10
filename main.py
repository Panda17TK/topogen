import streamlit as st
import networkx as nx
import yaml
import matplotlib.pyplot as plt
import os

# トポロジの可視化やYAML出力のために使用するグラフを初期化
G = nx.Graph()

# 保存用フォルダの名前
SAVE_FOLDER = "saved_topologies"

# サイドバーでノードを追加するためのセクション
st.sidebar.header("ノード追加")  # サイドバーのヘッダー

# ユーザーが入力するノードの各種パラメータを取得
node_id = st.sidebar.text_input("ノードID")  # ノードの識別ID
cpu_capacity = st.sidebar.number_input("CPU能力 (%)", min_value=1, max_value=100, value=100)  # CPU能力（％）
memory_capacity = st.sidebar.number_input("メモリ容量 (MB)", min_value=1000, value=8000)  # メモリ容量（MB）
queue_size = st.sidebar.number_input("キューサイズ (パケット数)", min_value=1, value=100)  # キューサイズ（パケット数）
failure_rate = st.sidebar.number_input("障害発生率 (%)", min_value=0.0, max_value=1.0, value=0.01)  # 障害発生率

# ノードを追加するボタンを表示し、押されたときにノードをグラフに追加
if st.sidebar.button("ノード追加"):
    G.add_node(node_id, cpu_capacity=cpu_capacity, memory_capacity=memory_capacity,
			queue_size=queue_size, failure_rate=failure_rate)
    st.sidebar.success(f"ノード {node_id} が追加されました。")  # 成功メッセージ

# サイドバーでリンクを追加するためのセクション
st.sidebar.header("リンク追加")  # サイドバーのヘッダー

# ノード間を接続するリンクのパラメータを取得
node1 = st.sidebar.selectbox("ノード1", list(G.nodes))  # 接続先ノード1
node2 = st.sidebar.selectbox("ノード2", list(G.nodes))  # 接続先ノード2
delay = st.sidebar.number_input("遅延 (ms)", min_value=1, value=10)  # リンク遅延（ms）
bandwidth = st.sidebar.number_input("帯域幅 (Mbps)", min_value=1, value=100)  # 帯域幅（Mbps）
jitter_range = st.sidebar.slider("ジッター範囲", min_value=0.5, max_value=2.0, value=(0.8, 1.2))  # ジッター範囲
link_failure_rate = st.sidebar.number_input("リンク障害発生率 (%)", min_value=0.0, max_value=1.0, value=0.01)  # リンクの障害発生率

# リンクを追加するボタンを表示し、押されたときにリンクをグラフに追加
if st.sidebar.button("リンク追加"):
    G.add_edge(node1, node2, delay=delay, bandwidth=bandwidth, jitter_range=jitter_range, failure_rate=link_failure_rate)
    st.sidebar.success(f"リンク {node1} と {node2} が追加されました。")  # 成功メッセージ

# メインセクションでグラフを可視化
st.header("ネットワークトポロジの可視化")  # メインヘッダー

# NetworkXのレイアウトを使用してノードの位置を決定し、グラフを描画
pos = nx.spring_layout(G)  # ノードの位置計算（spring_layoutを使用）
fig, ax = plt.subplots()  # グラフ描画のためのMatplotlibのセットアップ
nx.draw(G, pos, with_labels=True, node_size=1500, node_color="lightblue", ax=ax)  # ノードとエッジを描画
st.pyplot(fig)  # Streamlitでグラフを表示

# YAML形式でトポロジをエクスポートするためのボタン
if st.button("YAMLとしてエクスポート"):
    # 保存先フォルダが存在しなければ作成
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    # 現在のグラフのノードとリンク情報を収集し、YAML形式に変換
    topology_data = {
        'nodes': [
            {
                'id': node,
                'cpu_capacity': G.nodes[node]['cpu_capacity'],
                'memory_capacity': G.nodes[node]['memory_capacity'],
                'queue_size': G.nodes[node]['queue_size'],
                'failure_rate': G.nodes[node]['failure_rate']
            }
            for node in G.nodes
        ],
        'links': [
            {
                'id': f"Link{i+1}",
                'node1': edge[0],
                'node2': edge[1],
                'delay': G.edges[edge]['delay'],
                'bandwidth': G.edges[edge]['bandwidth'],
                'jitter_range': G.edges[edge]['jitter_range'],
                'failure_rate': G.edges[edge]['failure_rate']
            }
            for i, edge in enumerate(G.edges)
        ]
    }

    # YAMLファイルの保存
    yaml_filename = os.path.join(SAVE_FOLDER, 'topology.yaml')
    with open(yaml_filename, 'w') as file:
        yaml.dump(topology_data, file)
    st.success(f"YAMLファイルが {yaml_filename} に保存されました。")

# YAMLファイルをアップロードしてトポロジを読み込む機能
st.sidebar.header("YAMLファイルからトポロジを読み込む")
uploaded_file = st.sidebar.file_uploader("YAMLファイルをアップロード", type=['yaml'])

if uploaded_file is not None:
    # YAMLファイルを読み込み、ノードとリンクをグラフに追加
    topology_data = yaml.safe_load(uploaded_file)

    for node in topology_data['nodes']:
        G.add_node(node['id'],
				cpu_capacity=node['cpu_capacity'],
				memory_capacity=node['memory_capacity'],
				queue_size=node['queue_size'],
				failure_rate=node['failure_rate'])

    for link in topology_data['links']:
        G.add_edge(link['node1'], link['node2'],
					delay=link['delay'],
					bandwidth=link['bandwidth'],
					jitter_range=link['jitter_range'],
					failure_rate=link['failure_rate'])

    st.sidebar.success("YAMLファイルからトポロジが読み込まれました。")

# 再度、トポロジを可視化して表示（ファイルを読み込んだ場合も同様）
st.header("ネットワークトポロジの可視化 (更新済み)")
fig, ax = plt.subplots()
nx.draw(G, pos, with_labels=True, node_size=1500, node_color="lightgreen", ax=ax)
st.pyplot(fig)