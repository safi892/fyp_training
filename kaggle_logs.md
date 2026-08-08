FRESH START — training begins at step 0
After this run starts, set FRESH_START = False so a session restart resumes
instead of archiving your progress.
Checkpoints in the output dir: none






Sat Aug  8 14:10:20 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.159.04             Driver Version: 580.159.04     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla T4                       Off |   00000000:00:04.0 Off |                    0 |
| N/A   45C    P8              9W /   70W |       0MiB /  15360MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  Tesla T4                       Off |   00000000:00:05.0 Off |                    0 |
| N/A   43C    P8              9W /   70W |       0MiB /  15360MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
Python 3.12.13
Collecting uv
  Downloading uv-0.12.3-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (11 kB)
Downloading uv-0.12.3-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (22.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 22.3/22.3 MB 32.3 MB/s eta 0:00:0000:0100:01
Installing collected packages: uv
Successfully installed uv-0.12.3
add Codeadd Markdown





kaggle/working
/kaggle/working/project-files
Project copied to: /kaggle/working/project-files
Training dataset: /kaggle/input/datasets/saffiullah892/mydataset01/task_mixture.jsonl
add Codeadd Markdown



Resume-capable, task-aware project files detected
Working copy: /kaggle/working/project-files
add Codeadd Markdown



Uv install packages 

 + yarl==1.24.2
7.3G	/kaggle/temp/project-venv
7.3G	/kaggle/temp/uv-cache
732K	/kaggle/working/project-files
add Codeadd Markdown





Dataset      : ['/kaggle/input/datasets/saffiullah892/mydataset01/task_mixture.jsonl']
Output dir   : /kaggle/working/outputs/qwen2.5-coder-1.5b-cpp-review-qlora
Resume mode  : auto
Optimizer    : adamw_torch

Rows         : 66,103  (65,442 train / 661 eval)
Epochs       : 1
Seq length   : 1024
Batch        : 2 x 16 = 32 effective
Steps        : 2,045
Eval passes  : 8 x 661 rows

Rough wall-clock (the real rate is printed once training starts):
  at 3 samples/s : 6.2 h
  at 5 samples/s : 3.7 h
  at 8 samples/s : 2.3 h

Kaggle session limit is 9-12 h. If the estimate exceeds that, lower
num_train_epochs or raise eval_steps before starting.
add Codeadd Markdown






Dataset size GB: 0.065
Rows: 66103
Tasks:
  explanation      18939
  improve          18935
  complexity       14660
  line_comments    13569
add Codeadd Markdown







columns: ['prompt', 'completion']
train_on_inputs: False   packing: False

batch tensors: ['attention_mask', 'input_ids', 'labels']
batch shape: (4, 713)

[0] tokens=713 supervised=85 masked=628 ratio=11.9%
--- full sequence ---
<|im_start|>system
You are a senior C++ code review assistant. Produce accurate, structured, actionable review output for the given source code.<|im_end|>
<|im_start|>user
Analyze the following C++ code.

Language: cpp

Generate:
- Improved code

Return a single JSON object using the requested field names.

### Code

```cpp
bool ok(int x){
        while(x){
            if(x % 10 == 0) return false;
            x /= 10;
        }
        return true;
    }
```<|im_end|>
<|im_start|>assistant
{
  "improved_code": "bool ok(int x){\n    // Work on a copy to preserve the original argument semantics\n    for (auto n = x; n != 0; n /= 10) {\n        // Zero digit detected → early exit\n        if (n % 10 == 0) return false;\n    }\n    return true;\n}"
}<|im_end|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|><|endoftext|>
--- supervised span (labels != -100) ---
{
  "improved_code": "bool ok(int x){\n    // Work on a copy to preserve the original argument semantics\n    for (auto n = x; n != 0; n /= 10) {\n        // Zero digit detected → early exit\n        if (n % 10 == 0) return false;\n    }\n    return true;\n}"
}<|im_end|>

[1] tokens=713 supervised=389 masked=324 ratio=54.6%

[2] tokens=713 supervised=124 masked=589 ratio=17.4%

[3] tokens=713 supervised=29 masked=684 ratio=4.1%

========================================================================
LOSS MASKING VERIFIED
  supervised span is the target only, padding is masked, EOS present
Generating train split: 66103 examples [00:00, 217575.88 examples/s]
Rendering prompts (num_proc=2): 100%|██████████| 8/8 [00:00<00:00,  8.72 examples/s]
`torch_dtype` is deprecated! Use `dtype` instead!
Adding EOS to train dataset: 100%|██████████| 8/8 [00:00<00:00, 1490.25 examples/s]
Tokenizing train dataset: 100%|██████████| 8/8 [00:00<00:00, 372.47 examples/s]
Truncating train dataset: 100%|██████████| 8/8 [00:00<00:00, 2341.55 examples/s]
add Codeadd Markdown






Output dir : /kaggle/working/outputs/qwen2.5-coder-1.5b-cpp-review-qlora
Checkpoints: none
==============================================================================
RESUME MODE: SCRATCH  (fresh run from step 0)
  requested       : auto -> resolved to scratch
  starting step   : 0 (no checkpoint)
  optimizer state : fresh
  lr schedule     : restarts from warmup
  step counter    : restarts at 0
  note            : no checkpoint found, starting from step 0
==============================================================================
add Codeadd Markdown
