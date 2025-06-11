import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import umap.umap_ as umap

# 1. 디렉토리 경로 설정
graph_dir = './Graph'
out_dir = './Graph_embedding'
os.makedirs(out_dir, exist_ok=True)

# 2. 모델 준비
model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. 디렉토리 내 파일 반복
for filename in os.listdir(graph_dir):
    if not filename.endswith('_graph.json'):
        continue

    filepath = os.path.join(graph_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            graph = json.load(f)
        except Exception as e:
            print(f"파일 {filename} 읽기 오류: {e}")
            continue

    nodes = graph.get('nodes', [])
    if not nodes:
        print(f"{filename}: nodes 없음, 건너뜀")
        continue

    node_ids = [n['id'] for n in nodes]
    print(f"{filename}: {len(node_ids)} nodes 처리 중...")

    # BERT 임베딩
    embeddings = model.encode(node_ids)

    # UMAP 2D
    umap_model = umap.UMAP(n_components=2, random_state=42)
    umap_coords = umap_model.fit_transform(embeddings)

    # 색상 매핑 (x: hue, y: lightness)
    x = umap_coords[:, 0]
    y = umap_coords[:, 1]
    x_norm = (x - x.min()) / (x.max() - x.min() + 1e-8)
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-8)

    def hsl_color(h, l):
        # h: 0~1 → 0~360, l: 0~1 → 50~85, s: 고정 60%
        return f"hsl({int(h*360)}, 60%, {int(50 + l*35)}%)"

    colors = [hsl_color(h, l) for h, l in zip(x_norm, y_norm)]

    # 좌표/색상 추가
    for i, node in enumerate(nodes):
        node['x_norm'] = float(x_norm[i])
        node['y_norm'] = float(y_norm[i])
        node['color'] = colors[i]

    # 결과 저장
    outpath = os.path.join(out_dir, filename.replace('.json', '_embed.json'))
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"→ 저장 완료: {outpath}")

print("모든 파일 처리 완료!")
