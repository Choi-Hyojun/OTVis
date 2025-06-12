import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import umap.umap_ as umap
import colorsys

# 1. 디렉토리 경로 설정
graph_dir = './Graph'
out_dir = './Graph_embedding'
os.makedirs(out_dir, exist_ok=True)

# 2. 모델 준비
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_hue_light_sat(x, y, xc, yc, max_r, min_light=0.5, max_light=0.85, min_sat=0.7, max_sat=1.0):
    dx = x - xc
    dy = y - yc
    theta = np.arctan2(dy, dx)      # -pi ~ pi
    hue = ((theta + np.pi) / (2 * np.pi))    # 0~1
    r = np.sqrt(dx**2 + dy**2)
    dist = r / max_r if max_r > 0 else 0
    light = min_light + (max_light - min_light) * dist
    sat = min_sat + (max_sat - min_sat) * dist
    # HLS → RGB
    rgb = colorsys.hls_to_rgb(hue, light, sat)
    color = '#%02x%02x%02x' % tuple(int(255 * v) for v in rgb)
    return color

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

    x = umap_coords[:, 0]
    y = umap_coords[:, 1]
    # 0~1 정규화 좌표 (fixed layout용)
    x_norm = (x - x.min()) / (x.max() - x.min() + 1e-8)
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-8)
    # 중심점 계산 (각도/거리용)
    xc = x.mean()
    yc = y.mean()
    max_r = np.sqrt(((x - xc)**2 + (y - yc)**2).max())

    # 색상 (중앙 기준 각도/거리 기반)
    colors = [get_hue_light_sat(xi, yi, xc, yc, max_r) for xi, yi in zip(x, y)]

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
