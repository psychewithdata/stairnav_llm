# Hướng Dẫn Chạy StairNav-LLM Trên Colab

Tài liệu này là hướng dẫn thực hành từ đầu đến cuối cho project:

**StairNav-LLM: robot giao hàng trong tòa nhà, nhận lệnh tiếng Việt/voice, hỏi đáp trước khi di chuyển, dùng HM3D + Habitat-Sim để mô phỏng.**

## 0. Bạn sẽ chạy theo 2 mức

Đừng bắt đầu ngay bằng HM3D, vì Habitat-Sim và dataset khá nặng. Làm theo đúng thứ tự:

```text
Mức A: Graph MVP
  Chạy nhanh trên Colab Free.
  Mục tiêu: kiểm tra parser, hỏi đáp, route planner, SayCan-lite.

Mức B: HM3D + Habitat-Sim
  Cần tải dataset HM3D và cài Habitat-Sim.
  Mục tiêu: robot nhìn môi trường 3D thật hơn bằng RGB/depth/semantic.
```

Nếu Mức A chưa chạy ổn, chưa nên làm Mức B.

## 1. Cấu trúc file hiện tại

```text
stairnav_llm/
  README.md
  HUONG_DAN_CHAY_COLAB.md
  requirements.txt

  notebooks/
    StairNav_LLM_delivery_starter.ipynb

  src/
    __init__.py
    dialogue_policy.py
    hm3d_dataset_builder.py
    hm3d_habitat_adapter.py
    interactive_delivery_loop.py
    vision_map_fusion.py

  configs/
    hm3d_paths.example.json

  docs/
    colab_setup.md
    hm3d_habitat_setup.md
    technical_contribution_proposal.md
```

File quan trọng nhất lúc bắt đầu:

```text
notebooks/StairNav_LLM_delivery_starter.ipynb
```

## 2. Cách đưa project lên Colab

Bạn có 2 cách.

### Cách 1: Dùng GitHub

Trên máy local, tạo repo GitHub rồi push thư mục `stairnav_llm`.

Sau đó trong Colab:

```python
!git clone https://github.com/YOUR_USERNAME/stairnav-llm.git
%cd stairnav-llm
```

Nếu repo của bạn đặt tên khác thì đổi URL tương ứng.

### Cách 2: Upload thủ công

Nén thư mục `stairnav_llm` thành `.zip`, upload lên Colab, rồi giải nén:

```python
!unzip stairnav_llm.zip -d /content/
%cd /content/stairnav_llm
```

## 3. Mức A - chạy Graph MVP trước

### 3.1. Mở notebook

Trong Colab, upload hoặc mở file:

```text
notebooks/StairNav_LLM_delivery_starter.ipynb
```

### 3.2. Chọn runtime

Nếu chỉ chạy rule-based baseline:

```text
Runtime -> Change runtime type -> CPU
```

Nếu chạy local LLM:

```text
Runtime -> Change runtime type -> T4 GPU
```

### 3.3. Cài thư viện

Notebook đã có cell cài đặt. Nếu muốn cài bằng tay:

```python
!pip install -q -r requirements.txt
```

### 3.4. Chạy lần đầu không dùng LLM

Trong notebook, để:

```python
USE_LOCAL_LLM = False
```

Sau đó chọn:

```text
Runtime -> Run all
```

Bạn cần thấy các phần sau chạy được:

```text
building graph
dataset lệnh tiếng Việt
rule-based parser
route planner
clarification dialogue
vision-map fusion mock
SayCan-lite
evaluation metrics
```

### 3.5. Chạy với local LLM

Sau khi bản rule-based chạy ổn, đổi:

```python
USE_LOCAL_LLM = True
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
```

Rồi chạy lại từ đầu trên T4 GPU.

Nếu bị thiếu GPU RAM, dùng model nhỏ hơn:

```python
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
```

## 4. Mức B - setup HM3D + Habitat-Sim

HM3D không phải dataset tải tự do ngay lập tức. Bạn cần token từ Matterport.

### 4.1. Xin quyền HM3D

Bạn cần:

1. Tạo tài khoản Matterport.
2. Xin quyền dùng **Habitat-Matterport 3D Research Dataset**.
3. Tạo API token.
4. Lưu lại:

```text
MATTERPORT_TOKEN_ID
MATTERPORT_TOKEN_SECRET
```

Không commit token lên GitHub.

### 4.2. Cài conda trong Colab

Trong notebook Colab mới:

```python
!pip install -q condacolab
import condacolab
condacolab.install()
```

Colab sẽ restart kernel. Sau restart, chạy tiếp từ bước dưới.

### 4.3. Cài Habitat-Sim

```python
!conda install -y -c conda-forge -c aihabitat habitat-sim
```

Kiểm tra:

```python
import habitat_sim
print("Habitat-Sim OK")
```

Nếu lệnh cài bị lỗi, khả năng cao là do version Python/CUDA của Colab thay đổi. Khi đó giải pháp tốt hơn là chạy trong local Ubuntu/WSL2 bằng conda environment.

### 4.4. Tải test scene nhỏ trước

Chưa tải HM3D vội. Test Habitat trước:

```python
!python -m habitat_sim.utils.datasets_download \
  --uids habitat_test_scenes \
  --data-path data/
```

Nếu cell này lỗi, dừng lại sửa Habitat-Sim trước.

### 4.5. Nhập token HM3D

```python
import os
from getpass import getpass

os.environ["MATTERPORT_TOKEN_ID"] = getpass("Matterport token ID: ")
os.environ["MATTERPORT_TOKEN_SECRET"] = getpass("Matterport token secret: ")
```

### 4.6. Tải HM3D minival

Chỉ tải `minival` trước:

```python
!python -m habitat_sim.utils.datasets_download \
  --username "$MATTERPORT_TOKEN_ID" \
  --password "$MATTERPORT_TOKEN_SECRET" \
  --uids hm3d_minival_v0.2 \
  --data-path data/
```

Sau khi tải xong, cấu trúc thường sẽ là:

```text
data/
  scene_datasets/
    hm3d/
      hm3d_annotated_basis.scene_dataset_config.json
      minival/
        SCENE_FOLDER/
          *.basis.glb
          *.basis.navmesh
```

## 5. Test HM3D Adapter

Trong Colab, chạy:

```python
from pathlib import Path
import sys

sys.path.append("/content/stairnav-llm/stairnav_llm/src")

hm3d_root = Path("data/scene_datasets/hm3d")
scene_dirs = sorted((hm3d_root / "minival").glob("[0-9]*-*"))

print("Số scene:", len(scene_dirs))
scene_dir = scene_dirs[0]
scene_id = next(scene_dir.glob("*.basis.glb"))
scene_config = hm3d_root / "hm3d_annotated_basis.scene_dataset_config.json"

print("Scene:", scene_id)
print("Config:", scene_config)
```

Nếu bạn upload project thủ công và folder khác `/content/stairnav-llm`, sửa dòng:

```python
sys.path.append("/content/stairnav-llm/stairnav_llm/src")
```

cho đúng đường dẫn thực tế.

Tiếp theo:

```python
from hm3d_habitat_adapter import HabitatHM3DConfig, HabitatHM3DSimulator

cfg = HabitatHM3DConfig(
    scene_id=str(scene_id),
    scene_dataset_config=str(scene_config),
    width=320,
    height=240,
)

sim = HabitatHM3DSimulator(cfg)
obs = sim.reset()

print("Agent position:", obs.agent_state.position)
print("RGB shape:", None if obs.rgb is None else obs.rgb.shape)
print("Depth shape:", None if obs.depth is None else obs.depth.shape)
print("Semantic shape:", None if obs.semantic is None else obs.semantic.shape)

sim.close()
```

Nếu đoạn này chạy được, bạn đã nối thành công HM3D + Habitat-Sim.

## 6. Tạo một phần dataset HM3D để train/evaluate

Chạy:

```python
from hm3d_dataset_builder import sample_delivery_episodes, save_jsonl

sim = HabitatHM3DSimulator(cfg)

episodes = sample_delivery_episodes(
    sim,
    scene_id=str(scene_id),
    count=20,
    seed=7,
    min_distance=2.0,
)

save_jsonl(episodes, "data/stairnav_hm3d_minival_20.jsonl")
sim.close()

print("Số episode:", len(episodes))
print(episodes[0])
```

Kết quả là file:

```text
data/stairnav_hm3d_minival_20.jsonl
```

Mỗi dòng là một episode:

```json
{
  "episode_id": "...",
  "scene_id": "...basis.glb",
  "start_position": [0.0, 0.0, 0.0],
  "goal_position": [1.0, 0.0, 2.0],
  "geodesic_distance": 5.2,
  "instruction_vi": "Đem tài liệu tới khu văn phòng ở cuối hành lang.",
  "item": "tài liệu",
  "needs_clarification": false
}
```

## 7. Vòng hỏi đáp trước khi robot di chuyển

Ví dụ:

```python
from dialogue_policy import DeliveryIntent, clarification_question, apply_user_clarification

intent = DeliveryIntent(item=None, destination="R503")

q = clarification_question(intent)
print("Robot:", q)

intent = apply_user_clarification(intent, "tài liệu seminar")
print("Intent sau khi hỏi đáp:", intent)
```

Ý tưởng:

```text
User: Mang lên phòng 503 giúp tôi.
Robot: Robot cần mang món gì?
User: Tài liệu seminar.
Robot: Xác nhận. Tôi sẽ giao tài liệu seminar tới phòng 503.
```

Chỉ khi đủ thông tin, robot mới di chuyển.

## 8. Lộ trình thực nghiệm cho paper

Sau khi setup chạy được, làm theo thứ tự:

```text
Tuần 1:
  Graph MVP + dialogue + SayCan-lite chạy ổn.

Tuần 2:
  HM3D minival chạy được, tạo 20-100 episode.

Tuần 3:
  Tạo 300-500 câu lệnh tiếng Việt.

Tuần 4:
  Thêm voice-to-text bằng faster-whisper.

Tuần 5:
  So sánh baseline:
    rule-based
    LLM direct path
    LLM intent + planner
    LLM intent + SayCan-lite
    LLM + SayCan-lite + vision-map fusion

Tuần 6:
  Viết kết quả, bảng metric, error analysis.
```

## 9. Lỗi thường gặp

### Không import được habitat_sim

Nguyên nhân:

```text
Habitat-Sim chưa cài đúng môi trường conda.
```

Cách xử lý:

```python
!conda install -y -c conda-forge -c aihabitat habitat-sim
```

Nếu vẫn lỗi, chuyển sang local Ubuntu/WSL2.

### Không tải được HM3D

Nguyên nhân thường gặp:

```text
Token sai, chưa có quyền dataset, hoặc biến môi trường chưa set.
```

Kiểm tra lại:

```python
import os
print(bool(os.environ.get("MATTERPORT_TOKEN_ID")))
print(bool(os.environ.get("MATTERPORT_TOKEN_SECRET")))
```

### Scene list rỗng

Kiểm tra thư mục:

```python
!find data/scene_datasets/hm3d -maxdepth 3 -type f | head
```

Nếu không thấy `.basis.glb`, dataset chưa tải đúng.

## 10. Thứ tự bạn nên làm ngay

Làm đúng 5 bước này trước:

```text
1. Đưa folder stairnav_llm lên GitHub hoặc upload zip lên Colab.
2. Mở notebook StairNav_LLM_delivery_starter.ipynb.
3. Chạy USE_LOCAL_LLM=False.
4. Nếu ổn, chạy USE_LOCAL_LLM=True với Qwen 1.5B hoặc 3B.
5. Sau đó mới setup Habitat-Sim và tải HM3D minival.
```

Đừng tải HM3D train full ngay. Bắt đầu bằng minival để tiết kiệm thời gian và tránh vỡ setup.
