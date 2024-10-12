import streamlit as st
import networkx as nx
import yaml
import matplotlib.pyplot as plt
import os
from datetime import datetime

# 保存用フォルダの名前
SAVE_FOLDER = "saved_topologies"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# セッションにノードとリンクの情報を保持する関数
if "nodes" not in st.session_state:
    st.session_state["nodes"] = []
if "links" not in st.session_state:
    st.session_state["links"] = []

# ノードを追加する関数
def add_node(node_id, cpu_capacity, memory_capacity, queue_size, failure_rate):
    node_data = {
        "id": node_id,
        "cpu_capacity": cpu_capacity,
        "memory_capacity": memory_capacity,
        "queue_size": queue_size,
        "failure_rate": failure_rate,
    }
    st.session_state["nodes"].append(node_data)

# リンクを追加する関数
def add_link(node1, node2, delay, bandwidth, jitter_range, failure_rate):
    link_data = {
        "node1": node1,
        "node2": node2,
        "delay": delay,
        "bandwidth": bandwidth,
        "jitter_range": jitter_range,
        "failure_rate": failure_rate,
    }
    st.session_state["links"].append(link_data)

# サイドバーでノードを追加するためのセクション
st.sidebar.header("ノード追加")

# ノードの入力フィールド
node_id = st.sidebar.text_input("ノードID")
cpu_capacity = st.sidebar.number_input("CPU能力 (%)", min_value=1, max_value=100, value=100)
memory_capacity = st.sidebar.number_input("メモリ容量 (MB)", min_value=1000, value=8000)
queue_size = st.sidebar.number_input("キューサイズ (パケット数)", min_value=1, value=100)
failure_rate = st.sidebar.number_input("障害発生率 (%)", min_value=0.0, max_value=1.0, value=0.01)

# ノードを追加するボタン
if st.sidebar.button("ノード追加"):
    add_node(node_id, cpu_capacity, memory_capacity, queue_size, failure_rate)
    st.sidebar.success(f"ノード {node_id} が追加されました。")

# サイドバーでリンクを追加するためのセクション
st.sidebar.header("リンク追加")
node1 = st.sidebar.selectbox("ノード1", [node["id"] for node in st.session_state["nodes"]])
node2 = st.sidebar.selectbox("ノード2", [node["id"] for node in st.session_state["nodes"]])
delay = st.sidebar.number_input("遅延 (ms)", min_value=1, value=10)
bandwidth = st.sidebar.number_input("帯域幅 (Mbps)", min_value=1, value=100)
jitter_range = st.sidebar.slider("ジッター範囲", min_value=0.5, max_value=2.0, value=(0.8, 1.2))
link_failure_rate = st.sidebar.number_input("リンク障害発生率 (%)", min_value=0.0, max_value=1.0, value=0.01)

if st.sidebar.button("リンク追加"):
    add_link(node1, node2, delay, bandwidth, jitter_range, link_failure_rate)
    st.sidebar.success(f"リンク {node1} と {node2} が追加されました。")

# トポロジの可視化
st.header("ネットワークトポロジの可視化")
G = nx.Graph()

# ノードとリンクのデータからグラフを再構築
for node in st.session_state["nodes"]:
    G.add_node(node["id"], cpu_capacity=node["cpu_capacity"], memory_capacity=node["memory_capacity"],
               queue_size=node["queue_size"], failure_rate=node["failure_rate"])

for link in st.session_state["links"]:
    G.add_edge(link["node1"], link["node2"], delay=link["delay"], bandwidth=link["bandwidth"],
               jitter_range=link["jitter_range"], failure_rate=link["failure_rate"])

# トポロジの可視化
pos = nx.spring_layout(G)
fig, ax = plt.subplots()
nx.draw(G, pos, with_labels=True, node_size=1500, node_color="lightblue", ax=ax)
st.pyplot(fig)

# YAMLエクスポートのオプションを選択
st.header("YAMLとしてエクスポート")

# ファイル名を指定して保存するか、自動的に時間ベースで保存するか選択
save_option = st.radio("YAMLファイル名の選択", ("現在の時間で保存", "名前を付けて保存"))

if save_option == "名前を付けて保存":
    yaml_filename = st.text_input("保存するファイル名を入力 (拡張子不要)") + ".yaml"
else:
    yaml_filename = f"topology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

# YAMLファイルのエクスポート
if st.button("YAMLエクスポート"):
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    
    # トポロジデータの収集
    topology_data = {
        'nodes': st.session_state["nodes"],
        'links': st.session_state["links"]
    }

    # YAMLファイルの保存
    full_yaml_path = os.path.join(SAVE_FOLDER, yaml_filename)
    with open(full_yaml_path, 'w') as file:
        yaml.dump(topology_data, file)

    st.success(f"YAMLファイルが {full_yaml_path} に保存されました。")

# YAMLファイルをアップロードしてトポロジを読み込む
st.sidebar.header("YAMLファイルからトポロジを読み込む")
uploaded_file = st.sidebar.file_uploader("YAMLファイルをアップロード", type=['yaml'])

if uploaded_file is not None:
    topology_data = yaml.safe_load(uploaded_file)

    st.session_state["nodes"] = topology_data.get("nodes", [])
    st.session_state["links"] = topology_data.get("links", [])
    st.sidebar.success("YAMLファイルからトポロジが読み込まれました。")

# トポロジを再描画
st.header("ネットワークトポロジの可視化 (更新済み)")
pos = nx.spring_layout(G)
fig, ax = plt.subplots()
nx.draw(G, pos, with_labels=True, node_size=1500, node_color="lightgreen", ax=ax)
st.pyplot(fig)