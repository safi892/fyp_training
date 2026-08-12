# Base model vs fine-tuned checkpoint

Same twenty programs, same prompt, same decoding settings. The prompt is
rendered by the package rather than retyped, and both models share a chat
template, so the only variable is the weights.

| Measure | Base | Fine-tuned | Kind |
| --- | ---: | ---: | :---: |
| Valid JSON | 0/20 | 20/20 | `format` |
| Anchors proposed | 95 | 78 | `format` |
| Anchors surviving the check | 65/95 (68%) | 78/78 (100%) | `format` |
| Problems named | 9/55 (16%) | 7/55 (13%) | `content` |
| Confidently false descriptions | 8/20 | 10/20 | `content` |
| Text scored (chars) | 40,865 | 12,554 | `caveat` |

## What the training bought

- **Format compliance: +100%** valid JSON
- **Problems named: -3.6%** of concepts
- **Fewer false descriptions: -10%** of samples

Read the two kinds separately. A model that emits perfect JSON about code it
has misread has been improved on one axis and not the other, and averaging
them into a single score hides the distinction this project exists to make.

### Reading the content rows fairly

The base model's answers are **3.3x longer** than the fine-tuned
model's. Concepts are found by searching the text, so more text is more
chances to match one — the content comparison is tilted in the base model's
favour before either model says anything. A small apparent advantage there is
therefore not evidence of better understanding.

What can be said is the negative: **there is no evidence the fine-tuning
improved comprehension.** That is a real finding rather than a disappointing
one, because it locates precisely what the training did buy.
