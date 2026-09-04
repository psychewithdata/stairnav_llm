# Hướng Dẫn Chạy StairNav-HM3D Trên Colab

Đây là quy trình mới, đã bỏ phần graph MVP. Mục tiêu là chạy trực tiếp với:

```text
HM3D dataset + Habitat-Sim + command model training/testing + save/load model
```

## 1. Chuẩn bị trước khi mở Colab

Bạn cần có:

1. Một repo GitHub chứa thư mục `stairnav_llm`, hoặc file zip của thư mục này.
2. Tài khoản Matterport đã được cấp quyền dùng **Habitat-Matterport 3D Research Dataset**.
3. Matterport token gồm `MATTERPORT_TOKEN_ID` và `MATTERPORT_TOKEN_SECRET`.

Không đưa token lên GitHub.

Dataset HM3D: `https://github.com/matterport/habitat-matterport-3dresearch`

## 2. Mở Colab và chọn GPU

Trong Colab:

```text
Runtime -> Change runtime type -> T4 GPU
```

## 3. Đưa project vào Colab

### Cách A: clone GitHub

```python
!git clone https://github.com/YOUR_USERNAME/stairnav-llm.git
%cd stairnav-llm/stairnav_llm
```

Nếu repo của bạn đặt `stairnav_llm` ở root, dùng:

```python
%cd stairnav-llm
```

### Cách B: upload zip thủ công

Upload `stairnav_llm.zip`, rồi chạy:

```python
!unzip -q stairnav_llm.zip -d /content/
%cd /content/stairnav_llm
```

Kiểm tra:

```python
!ls
!ls notebooks
!ls src
```

Bạn cần thấy:

```text
notebooks/StairNav_HM3D_Colab.ipynb
src/hm3d_habitat_adapter.py
src/hm3d_dataset_builder.py
src/command_model.py
```

## 4. Mở notebook chính

Mở file:

```text
notebooks/StairNav_HM3D_Colab.ipynb
```

Sau đó chạy từ trên xuống.

## 5. Cài Python dependencies

```python
!pip install -q -r requirements.txt
```

## 6. Cài Habitat-Sim bằng conda

Trong Colab, chạy:

```python
!pip install -q condacolab
import condacolab
condacolab.install()
```

Colab sẽ restart runtime. Sau khi restart:

1. Chạy lại cell `%cd ...` để vào đúng project.
2. Chạy lại cell cài `requirements.txt`.
3. Chạy tiếp:

```python
!conda install -y -c conda-forge -c aihabitat habitat-sim
```

Kiểm tra:

```python
import habitat_sim
print("Habitat-Sim OK")
```

Nếu lỗi ở bước này, thường là do version Python/CUDA của Colab thay đổi. Khi đó thử runtime mới hoặc chuyển sang local Ubuntu/WSL2 bằng conda.

## 7. Test Habitat-Sim trước khi tải HM3D

```python
!python -m habitat_sim.utils.datasets_download \
  --uids habitat_test_scenes \
  --data-path data/
```

Nếu cell này lỗi, chưa tải HM3D. Sửa Habitat-Sim trước.

## 8. Nhập Matterport token

```python
import os
from getpass import getpass

os.environ["MATTERPORT_TOKEN_ID"] = getpass("Matterport token ID: ")
os.environ["MATTERPORT_TOKEN_SECRET"] = getpass("Matterport token secret: ")
```

## 9. Tải HM3D minival

Bắt đầu bằng minival:

```python
!python -m habitat_sim.utils.datasets_download \
  --username "$MATTERPORT_TOKEN_ID" \
  --password "$MATTERPORT_TOKEN_SECRET" \
  --uids hm3d_minival_v0.2 \
  --data-path data/
```

Sau khi tải, kiểm tra:

```python
!find data/scene_datasets/hm3d -maxdepth 3 -type f | head -30
```

Bạn cần thấy file dạng:

```text
*.basis.glb
*.basis.navmesh
hm3d_annotated_basis.scene_dataset_config.json
```

## 10. Tìm scene HM3D

Notebook sẽ tự tìm scene:

```python
hm3d_root = Path("data/scene_datasets/hm3d")
scene_dirs = sorted((hm3d_root / "minival").glob("[0-9]*-*"))
scene_id = next(scene_dirs[0].glob("*.basis.glb"))
scene_config = hm3d_root / "hm3d_annotated_basis.scene_dataset_config.json"
```

Nếu `scene_dirs` rỗng, dataset tải chưa đúng.

## 11. Test Habitat adapter

```python
cfg = HabitatHM3DConfig(
    scene_id=str(scene_id),
    scene_dataset_config=str(scene_config),
    width=320,
    height=240,
)

sim = HabitatHM3DSimulator(cfg)
obs = sim.reset()

print(obs.agent_state.position)
print(obs.rgb.shape)
print(obs.depth.shape)
print(obs.semantic.shape)

sim.close()
```

Nếu chạy được, robot đã đọc được observation từ HM3D scene.

## 12. Tạo dataset episode từ HM3D

```python
episodes = sample_delivery_episodes(
    sim,
    scene_id=str(scene_id),
    count=80,
    seed=7,
    min_distance=2.0,
    clarification_ratio=0.25,
)
```

File sinh ra:

```text
data/stairnav_hm3d_minival_80.jsonl
```

## 13. Train/test command model

```python
result = train_command_models(
    episode_jsonl=episode_file,
    output_dir=MODEL_DIR,
)
```

Model được train để dự đoán:

```text
needs_clarification_label
item_label
goal_label
```

Kết quả lưu ở:

```text
outputs/models/command_model.joblib
outputs/models/command_model_metrics.json
```

## 14. Lưu model vào Google Drive

```python
from google.colab import drive

drive.mount('/content/drive')

DRIVE_OUT = Path('/content/drive/MyDrive/stairnav_llm_outputs')
DRIVE_OUT.mkdir(parents=True, exist_ok=True)

!cp -r outputs/models "$DRIVE_OUT/"
!cp -r data "$DRIVE_OUT/"
```

Sau khi chạy, model sẽ nằm ở:

```text
MyDrive/stairnav_llm_outputs/models/command_model.joblib
```

## 15. Load model để chạy câu lệnh mới

```python
from command_model import predict_command

model_file = MODEL_DIR / "command_model.joblib"

command = "Đem tài liệu tới khu văn phòng ở cuối hành lang."
print(predict_command(model_file, command))
```

Output ví dụ:

```python
{
  "needs_clarification_label": "False",
  "item_label": "tài liệu",
  "goal_label": "khu văn phòng ở cuối hành lang"
}
```

## 16. Robot hỏi đáp trước khi di chuyển

```python
from dialogue_policy import DeliveryIntent, clarification_question, apply_user_clarification

intent = DeliveryIntent(item=None, destination=None, recipient=None)

question = clarification_question(intent)
print("Robot:", question)

intent = apply_user_clarification(intent, "phòng 503")
question = clarification_question(intent)
print("Robot:", question)

intent = apply_user_clarification(intent, "tài liệu seminar")
question = clarification_question(intent)
print("Đủ thông tin để đi:", question is None)
```

Ý nghĩa:

```text
User: Mang lên giúp tôi.
Robot: Bạn muốn robot giao tới phòng nào hoặc cho người nhận nào?
User: Phòng 503.
Robot: Robot cần mang món gì?
User: Tài liệu seminar.
Robot: Đã đủ thông tin, bắt đầu planning.
```

## 17. Test đường đi bằng Habitat pathfinder

```python
distance = sim.geodesic_distance(sample["start_position"], sample["goal_position"])
print("Reachable:", distance < float("inf"))
```

Ở giai đoạn này, Habitat pathfinder là oracle để xác nhận đường đi khả thi. Giai đoạn sau mới thay bằng learned navigation policy.

## 18. Thứ tự cell cần chạy

```text
1. Clone/upload project
2. pip install requirements
3. condacolab install
4. sau runtime restart: cd lại project
5. conda install habitat-sim
6. download habitat_test_scenes
7. nhập Matterport token
8. download hm3d_minival_v0.2
9. tìm scene HM3D
10. test Habitat adapter
11. sample HM3D episodes
12. train/test command model
13. save model to Drive
14. load model and predict new command
15. dialogue-before-move demo
16. geodesic reachability test
```

## 19. Chạy lại model ở Colab session sau

Mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Copy model về runtime:

```python
!mkdir -p outputs/models
!cp /content/drive/MyDrive/stairnav_llm_outputs/models/command_model.joblib outputs/models/
```

Load model:

```python
from command_model import predict_command

print(predict_command(
    "outputs/models/command_model.joblib",
    "Giao laptop tới khu văn phòng ở cuối hành lang."
))
```

## 20. Khi nào tăng quy mô training?

Sau khi notebook chạy ổn với 80 episode, tăng dần:

```python
count=500
```

rồi:

```python
count=1000
```

Không tăng ngay từ đầu. Hãy đảm bảo pipeline tải scene, sample episode, train model, save model đều ổn trước.
