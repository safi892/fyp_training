# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 172 |
| valid JSON, of output that finished | 167/169 |
| ran past the token budget | 3/172 |
| anchors quoting a real line | 1325/1529 (87%) |
| named a container the code declares | 18/18 |
| named a container that is not there | 5/172 |
| loops described as recursive | 3/88 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## tree_inorder — recursive

- anchors: 0 exact, 13 relocated, **3 quoting a line that is not in the file**, of 16
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void inorder(Node* node) {
    if (node == nullptr) return;
    inorder(node->left);
    cout << node->value << " ";
    inorder(node->right);
}

int main() { inorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary search tree for testing |
| 11 | `root->left = new Node(3);` | left subtree: 3, 1, 4 |
| 12 | `root->right = new Node(10);` | right subtree: 10, 14, 13 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print |
| 22 | `inorder(node->left);` | Recurse left subtree first |
| 23 | `cout << node->value << " ";` | Output current node's value |
| 24 | `inorder(node->right);` | Recurse right subtree |
| 27 | `Node* root = sample();` | Provide a sample tree for testing |
| 28 | `inorder(sample()); cout << "\n";` | In‑order traversal prints 1 3 4 6 7 8 10 13 14 |
| 29 | `return 0;` | Return success status |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the inorder sequence to standard output followed by a newline.  
Algorithm: Recursively traverse the left subtree, output the current node’s value, then recursively traverse the right subtree. The recursion stops when a null pointer is encountered.

---

## tree_inorder — iterative

- anchors: 0 exact, 21 relocated, **3 quoting a line that is not in the file**, of 24
- containers in the code: stack

  - *container named*: Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 left subtree: 3 → 1 → 4 → 7 right subtree: 10 → 13 → 14 left‑left: 1 left‑right: 6 left‑right‑left: 4 left‑right‑right: 7 right‑right: 14 right‑right‑left: 13 Iterative inorder traversal using a stack.
  - *container named*: The loop continues while the current node is non‑null or the stack is not empty.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void inorder(Node* node) {
    stack<Node*> pending;
    while (node != nullptr || !pending.empty()) {
        while (node != nullptr) {
            pending.push(node);
            node = node->left;
        }
        node = pending.top();
        pending.pop();
        cout << node->value << " ";
        node = node->right;
    }
}

int main() { inorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 11 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 |
| 12 | `root->left = new Node(3);` | left subtree: 3 → 1 → 4 → 7 |
| 13 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 14 | `root->left->left = new Node(1);` | left‑left: 1 |
| 15 | `root->left->right = new Node(6);` | left‑right: 6 |
| 16 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 17 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 18 | `root->right->right = new Node(14);` | right‑right: 14 |
| 19 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 22 | `stack<Node*> pending;` | Iterative inorder traversal using a stack. The loop continues while the current node is non‑null or the stack is not empty. |
| 23 | `while (node != nullptr \|\| !pending.empty()) {` | If the current node has a left child, push it onto the stack and descend left. |
| 24 | `while (node != nullptr) {` | If the current node has a left child, push it onto the stack and descend left. |
| 25 | `pending.push(node);` | push node onto stack for later processing |
| 26 | `node = node->left;` | continue left |
| 28 | `node = pending.top();` | pop node from stack |
| 29 | `pending.pop();` | remove node from stack |
| 30 | `cout << node->value << " ";` | output node value |
| 31 | `node = node->right;` | descend right |
| 34 | `}` | end while loop |
| 35 | `}` | end outer while loop |
| 37 | `return root;` | return the constructed tree |
| 40 | `inorder(sample()); cout << "\n";` | Perform inorder traversal of the sample tree and output the result |
| 41 | `cout << "\n";` | add newline for clarity |
| 42 | `return 0;` | main returns 0 |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: `Node* root` – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: Writes the inorder sequence to `std::cout` and returns 0.  
Algorithm: Uses a stack to perform an iterative in‑order traversal. Starting from the root, repeatedly push left children onto the stack while the current node is non‑null. When the stack is empty, pop the top node, output its value, and move to its right child. This yields the sorted sequence of node values.

---

## tree_preorder — recursive

- anchors: 0 exact, 13 relocated, **2 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void preorder(Node* node) {
    if (node == nullptr) return;
    cout << node->value << " ";
    preorder(node->left);
    preorder(node->right);
}

int main() { preorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing preorder traversal. |
| 11 | `root->left = new Node(3);` | left subtree: 3, 1, 4 |
| 12 | `root->right = new Node(10);` | right subtree: 10, 6, 7, 13 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print. |
| 22 | `cout << node->value << " ";` | Visit current node. |
| 23 | `preorder(node->left);` | Recurse left child. |
| 24 | `preorder(node->right);` | Recurse right child. |
| 27 | `Node* root = sample();` | Sample tree for preorder traversal. |
| 28 | `preorder(sample()); cout << "\n";` | Output preorder traversal. |

**Explanation**

Purpose: Prints the values of a binary tree in preorder traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the preorder sequence to standard output.  
Algorithm: Recursively visit each node, output its value, and recurse on its left and right children. The recursion stops when a null pointer is encountered.

---

## tree_preorder — iterative

- anchors: 0 exact, 11 relocated, **1 quoting a line that is not in the file**, of 12
- containers in the code: stack

  - *container named*: Build a sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 Base case: empty subtree → nothing to print Stack for iterative preorder traversal Push the root onto the stack Process nodes in preorder: left → node → right Pop the top node Remove it from the stack Output the node's value Push right child before left child to preserve left → node → right order Push left child Loop ends when the stack is empty Return success code Purpose: Prints a binary tree in preorder (root, left, right) using a stack.
  - *container named*: Algorithm: Initialize a stack with the root, then repeatedly pop a node, output its value, and push its right child and left child onto the stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void preorder(Node* node) {
    if (node == nullptr) return;
    stack<Node*> pending;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        cout << current->value << " ";
        if (current->right) pending.push(current->right);
        if (current->left) pending.push(current->left);
    }
}

int main() { preorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 14 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print |
| 15 | `stack<Node*> pending;` | Stack for iterative preorder traversal |
| 16 | `pending.push(node);` | Push the root onto the stack |
| 17 | `while (!pending.empty()) {` | Process nodes in preorder: left → node → right |
| 18 | `Node* current = pending.top();` | Pop the top node |
| 19 | `pending.pop();` | Remove it from the stack |
| 20 | `cout << current->value << " ";` | Output the node's value |
| 21 | `if (current->right) pending.push(current->right);` | Push right child before left child to preserve left → node → right order |
| 22 | `if (current->left) pending.push(current->left);` | Push left child |
| 25 | `}` | Loop ends when the stack is empty |
| 28 | `return 0;` | Return success code |

**Explanation**

Purpose: Prints a binary tree in preorder (root, left, right) using a stack.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: void – writes the preorder traversal to standard output; no return value.  
Algorithm: Initialize a stack with the root, then repeatedly pop a node, output its value, and push its right child and left child onto the stack. The loop stops when the stack is empty.

---

## tree_postorder — recursive

- anchors: 0 exact, 13 relocated, **4 quoting a line that is not in the file**, of 17
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void postorder(Node* node) {
    if (node == nullptr) return;
    postorder(node->left);
    postorder(node->right);
    cout << node->value << " ";
}

int main() { postorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 11 | `root->left = new Node(3);` | left subtree: 3, 1, 6, 4, 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10, 14, 13 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print |
| 22 | `postorder(node->left);` | Recurse left subtree first |
| 23 | `postorder(node->right);` | Recurse right subtree second |
| 24 | `cout << node->value << " ";` | Output current node's value |
| 27 | `Node* root = sample();` | Provide a concrete tree for testing |
| 28 | `postorder(sample());` | Perform post‑order traversal |
| 29 | `cout << "\n";` | Output newline to separate output from program termination |
| 30 | `return 0;` | Return success status |

**Explanation**

Purpose: Prints the values of a binary tree in postorder traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the node values to standard output in postorder order.  
Algorithm: Recursively traverse the left subtree, then the right subtree, finally output the current node. The recursion stops when a null pointer is encountered.

---

## tree_postorder — iterative

- anchors: 0 exact, 13 relocated, **1 quoting a line that is not in the file**, of 14
- containers in the code: stack

  - *container named*: Build a sample binary tree: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 Base case: empty subtree yields no output pending: nodes to be processed in postorder order output: nodes that have been processed but not yet printed Push the root onto the pending stack Process nodes in postorder: left child, right child, then current node Pop the top node from the pending stack Remove it from the pending stack Push the current node onto the output stack Push left child onto the pending stack (if any) Push right child onto the pending stack (if any) Print nodes in postorder order: left child, right child, then current node Output the value of the current node Remove the node from the output stack Return success code Purpose: Prints the values of a binary tree in postorder (left‑right‑root) using a stack for traversal.
  - *container named*: Algorithm: Initialize a stack with the root and another stack for the final output.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void postorder(Node* node) {
    if (node == nullptr) return;
    stack<Node*> pending, output;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        output.push(current);
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
    while (!output.empty()) {
        cout << output.top()->value << " ";
        output.pop();
    }
}

int main() { postorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a sample binary tree: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 |
| 14 | `if (node == nullptr) return;` | Base case: empty subtree yields no output |
| 15 | `stack<Node*> pending, output;` | pending: nodes to be processed in postorder order output: nodes that have been processed but not yet printed |
| 16 | `pending.push(node);` | Push the root onto the pending stack |
| 17 | `while (!pending.empty()) {` | Process nodes in postorder: left child, right child, then current node |
| 18 | `Node* current = pending.top();` | Pop the top node from the pending stack |
| 19 | `pending.pop();` | Remove it from the pending stack |
| 20 | `output.push(current);` | Push the current node onto the output stack |
| 21 | `if (current->left) pending.push(current->left);` | Push left child onto the pending stack (if any) |
| 22 | `if (current->right) pending.push(current->right);` | Push right child onto the pending stack (if any) |
| 25 | `while (!output.empty()) {` | Print nodes in postorder order: left child, right child, then current node |
| 26 | `cout << output.top()->value << " ";` | Output the value of the current node |
| 27 | `output.pop();` | Remove the node from the output stack |
| 30 | `return 0;` | Return success code |

**Explanation**

Purpose: Prints the values of a binary tree in postorder (left‑right‑root) using a stack for traversal.  
Input: `Node* root` – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: Writes the node values to `std::cout` in postorder order; returns `int` to satisfy `main` contract.  
Algorithm: Initialize a stack with the root and another stack for the final output. Pop nodes from the stack, push them onto the output stack, and push their children (left‑right) onto the stack. After the first pass, pop the output stack to produce the postorder sequence. Finally, output the values.

---

## tree_height — recursive

- anchors: 0 exact, 13 relocated, **1 quoting a line that is not in the file**, of 14
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int height(Node* node) {
    if (node == nullptr) return 0;
    int left = height(node->left);
    int right = height(node->right);
    return 1 + (left > right ? left : right);
}

int main() { cout << height(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 11 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 12 | `root->left = new Node(3);` | left child of 8 |
| 13 | `root->right = new Node(10);` | right child of 8 |
| 14 | `root->left->left = new Node(1);` | left child of 3 |
| 15 | `root->left->right = new Node(6);` | right child of 3 |
| 16 | `root->left->right->left = new Node(4);` | left child of 6 |
| 17 | `root->left->right->right = new Node(7);` | right child of 6 |
| 18 | `root->right->right = new Node(14);` | right child of 10 |
| 19 | `root->right->right->left = new Node(13);` | left child of 14 |
| 22 | `if (node == nullptr) return 0;` | Base case: an empty subtree has height 0 |
| 23 | `int left = height(node->left);` | Recursively compute height of left subtree |
| 24 | `int right = height(node->right);` | Recursively compute height of right subtree |
| 25 | `return 1 + (left > right ? left : right);` | Return 1 plus the larger height of the two children |
| 28 | `cout << height(sample()) << "\n";` | Output the height of the constructed tree |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – height of the tree (0 for an empty tree).  
Algorithm: Perform a post‑order traversal, recursively obtaining the height of each subtree, and return 1 plus the larger of the two heights. The recursion stops when a null child is encountered.

---

## tree_height — iterative

- anchors: 0 exact, 12 relocated, **1 quoting a line that is not in the file**, of 13
- containers in the code: queue

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 BFS traversal to count levels start with the root track the number of levels number of nodes at the current level process all nodes at the current level extract the front node remove it from the queue enqueue left child if present enqueue right child if present move to the next level total height of the tree Print the height of the sample tree Purpose: Compute the height (depth) of a binary tree.
  - *container named*: Algorithm: Perform a breadth‑first traversal using a queue, counting each level as the number of nodes processed.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int height(Node* node) {
    if (node == nullptr) return 0;
    queue<Node*> level;
    level.push(node);
    int levels = 0;
    while (!level.empty()) {
        int width = level.size();
        for (int i = 0; i < width; i++) {
            Node* current = level.front();
            level.pop();
            if (current->left) level.push(current->left);
            if (current->right) level.push(current->right);
        }
        levels++;
    }
    return levels;
}

int main() { cout << height(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 15 | `queue<Node*> level;` | BFS traversal to count levels |
| 16 | `level.push(node);` | start with the root |
| 17 | `int levels = 0;` | track the number of levels |
| 19 | `int width = level.size();` | number of nodes at the current level |
| 20 | `for (int i = 0; i < width; i++) {` | process all nodes at the current level |
| 21 | `Node* current = level.front();` | extract the front node |
| 22 | `level.pop();` | remove it from the queue |
| 23 | `if (current->left) level.push(current->left);` | enqueue left child if present |
| 24 | `if (current->right) level.push(current->right);` | enqueue right child if present |
| 26 | `levels++;` | move to the next level |
| 28 | `return levels;` | total height of the tree |
| 32 | `cout << height(sample()) << "\n";` | Print the height of the sample tree |

**Explanation**

Purpose: Compute the height (depth) of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – the number of levels in the tree (0 for an empty tree).  
Algorithm: Perform a breadth‑first traversal using a queue, counting each level as the number of nodes processed. The traversal stops when the queue becomes empty, yielding the height.

---

## tree_count_leaves — recursive

- anchors: 0 exact, 4 relocated, **1 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int leaves(Node* node) {
    if (node == nullptr) return 0;
    if (node->left == nullptr && node->right == nullptr) return 1;
    return leaves(node->left) + leaves(node->right);
}

int main() { cout << leaves(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 |
| 15 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no leaves |
| 16 | `if (node->left == nullptr && node->right == nullptr) return 1;` | Leaf node: count it |
| 17 | `return leaves(node->left) + leaves(node->right);` | Recursive sum of leaves in left and right subtrees |
| 21 | `cout << leaves(sample()) << "\n";` | Output the number of leaf nodes in the constructed tree |

**Explanation**

Purpose: Counts the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – total count of leaf nodes.  
Algorithm: Recursively traverse the tree, returning 1 for each leaf node and summing the results from left and right subtrees. The base case handles an empty subtree.

---

## tree_count_leaves — iterative

- anchors: 0 exact, 12 relocated, **1 quoting a line that is not in the file**, of 13
- containers in the code: stack

  - *container named*: Build a simple binary tree for testing: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 Base case: empty subtree contributes no leaves Iterative DFS using a stack to visit nodes in reverse postorder Start with the root Counter for leaves encountered Process nodes until the stack is empty Pop the top node Remove it from the stack If the current node is a leaf, increment the leaf counter Push left child onto the stack (postorder left) Push right child onto the stack (postorder right) Return total count of leaf nodes Output the number of leaves in the constructed tree Purpose: Counts the number of leaf nodes in a binary tree.
  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, pushing each node onto the stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int leaves(Node* node) {
    if (node == nullptr) return 0;
    stack<Node*> pending;
    pending.push(node);
    int found = 0;
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        if (current->left == nullptr && current->right == nullptr) found++;
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
    return found;
}

int main() { cout << leaves(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 |
| 15 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no leaves |
| 16 | `stack<Node*> pending;` | Iterative DFS using a stack to visit nodes in reverse postorder |
| 17 | `pending.push(node);` | Start with the root |
| 18 | `int found = 0;` | Counter for leaves encountered |
| 19 | `while (!pending.empty()) {` | Process nodes until the stack is empty |
| 20 | `Node* current = pending.top();` | Pop the top node |
| 21 | `pending.pop();` | Remove it from the stack |
| 22 | `if (current->left == nullptr && current->right == nullptr) found++;` | If the current node is a leaf, increment the leaf counter |
| 23 | `if (current->left) pending.push(current->left);` | Push left child onto the stack (postorder left) |
| 24 | `if (current->right) pending.push(current->right);` | Push right child onto the stack (postorder right) |
| 27 | `return found;` | Return total count of leaf nodes |
| 30 | `cout << leaves(sample()) << "\n";` | Output the number of leaves in the constructed tree |

**Explanation**

Purpose: Counts the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – total count of leaf nodes.  
Algorithm: Perform a depth‑first traversal using a stack, pushing each node onto the stack. When a node has no children, increment a counter. After processing all nodes, return the counter. The traversal visits each node exactly once, yielding O(n) time and O(n) auxiliary space.

---

## tree_invert — recursive

- anchors: 0 exact, 18 relocated, **0 quoting a line that is not in the file**, of 18
- containers in the code: stack

  - *container named*: Build a sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 Base case: empty subtree – nothing to invert Save left child before swapping Swap left and right children Restore original right child Recursively invert left subtree Recursively invert right subtree Build the sample tree Invert the tree to achieve mirror symmetry Use a stack for in‑order traversal Pop nodes in reverse order (right, then left) Pop current node Output node value Push right child before left to maintain in‑order Push left child End of traversal loop Final newline for clean output Success Purpose: Inverts a binary tree and prints its postorder traversal.
  - *container named*: The `main` function builds a sample tree, inverts it, and uses a stack to perform a postorder traversal, printing each node’s value.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void invert(Node* node) {
    if (node == nullptr) return;
    Node* spare = node->left;
    node->left = node->right;
    node->right = spare;
    invert(node->left);
    invert(node->right);
}

int main() {
    Node* root = sample();
    invert(root);
    stack<Node*> s; s.push(root);
    while (!s.empty()) {
        Node* c = s.top(); s.pop();
        cout << c->value << " ";
        if (c->right) s.push(c->right);
        if (c->left) s.push(c->left);
    }
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 14 | `if (node == nullptr) return;` | Base case: empty subtree – nothing to invert |
| 15 | `Node* spare = node->left;` | Save left child before swapping |
| 16 | `node->left = node->right;` | Swap left and right children |
| 17 | `node->right = spare;` | Restore original right child |
| 18 | `invert(node->left);` | Recursively invert left subtree |
| 19 | `invert(node->right);` | Recursively invert right subtree |
| 23 | `Node* root = sample();` | Build the sample tree |
| 24 | `invert(root);` | Invert the tree to achieve mirror symmetry |
| 25 | `stack<Node*> s; s.push(root);` | Use a stack for in‑order traversal |
| 26 | `while (!s.empty()) {` | Pop nodes in reverse order (right, then left) |
| 27 | `Node* c = s.top(); s.pop();` | Pop current node |
| 28 | `cout << c->value << " ";` | Output node value |
| 29 | `if (c->right) s.push(c->right);` | Push right child before left to maintain in‑order |
| 30 | `if (c->left) s.push(c->left);` | Push left child |
| 31 | `}` | End of traversal loop |
| 32 | `cout << "\n";` | Final newline for clean output |
| 33 | `return 0;` | Success |

**Explanation**

Purpose: Inverts a binary tree and prints its postorder traversal.  
Input: `Node* root` – pointer to the root of the original binary tree.  
Output: Prints the inverted tree’s values in postorder; no return value.  
Algorithm: The `invert` function recursively swaps left and right children, then recursively inverts the left and right subtrees. The `main` function builds a sample tree, inverts it, and uses a stack to perform a postorder traversal, printing each node’s value.

---

## tree_invert — iterative

- anchors: 0 exact, 19 relocated, **0 quoting a line that is not in the file**, of 19
- containers in the code: queue, stack

  - *container named*: Build a sample binary tree: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 Process the node at the front of the queue Remove it so we don't visit it again Save the left child before swapping Swap left and right children Restore original right child Enqueue children for future processing Enqueue children for future processing Build the sample tree Invert the tree in‑place Perform an in‑order traversal using a stack Pop nodes from the stack and output their values Pop the top node Output the node's value Push right child onto stack for later processing Push left child onto stack for later processing End of in‑order traversal Final newline for clean output Return success code Purpose: Inverts a binary tree in‑place and prints its post‑order traversal.
  - *container named*: Build a sample binary tree: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 Process the node at the front of the queue Remove it so we don't visit it again Save the left child before swapping Swap left and right children Restore original right child Enqueue children for future processing Enqueue children for future processing Build the sample tree Invert the tree in‑place Perform an in‑order traversal using a stack Pop nodes from the stack and output their values Pop the top node Output the node's value Push right child onto stack for later processing Push left child onto stack for later processing End of in‑order traversal Final newline for clean output Return success code Purpose: Inverts a binary tree in‑place and prints its post‑order traversal.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void invert(Node* node) {
    if (node == nullptr) return;
    queue<Node*> pending;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.front();
        pending.pop();
        Node* spare = current->left;
        current->left = current->right;
        current->right = spare;
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
}

int main() {
    Node* root = sample();
    invert(root);
    stack<Node*> s; s.push(root);
    while (!s.empty()) {
        Node* c = s.top(); s.pop();
        cout << c->value << " ";
        if (c->right) s.push(c->right);
        if (c->left) s.push(c->left);
    }
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 11 | `Node* root = new Node(8);` | Build a sample binary tree: 8 / \   / \ 3 10 / \ / \ 1 6 4 7 14 13 |
| 14 | `Node* current = pending.front();` | Process the node at the front of the queue |
| 15 | `pending.pop();` | Remove it so we don't visit it again |
| 16 | `Node* spare = current->left;` | Save the left child before swapping |
| 17 | `current->left = current->right;` | Swap left and right children |
| 18 | `current->right = spare;` | Restore original right child |
| 19 | `if (current->left) pending.push(current->left);` | Enqueue children for future processing |
| 20 | `if (current->right) pending.push(current->right);` | Enqueue children for future processing |
| 23 | `Node* root = sample();` | Build the sample tree |
| 24 | `invert(root);` | Invert the tree in‑place |
| 25 | `stack<Node*> s; s.push(root);` | Perform an in‑order traversal using a stack |
| 26 | `while (!s.empty()) {` | Pop nodes from the stack and output their values |
| 27 | `Node* c = s.top(); s.pop();` | Pop the top node |
| 28 | `cout << c->value << " ";` | Output the node's value |
| 29 | `if (c->right) s.push(c->right);` | Push right child onto stack for later processing |
| 30 | `if (c->left) s.push(c->left);` | Push left child onto stack for later processing |
| 31 | `}` | End of in‑order traversal |
| 32 | `cout << "\n";` | Final newline for clean output |
| 33 | `return 0;` | Return success code |

**Explanation**

Purpose: Inverts a binary tree in‑place and prints its post‑order traversal.  
Input: `Node* root` – pointer to the root of the binary tree to be inverted.  
Output: Prints the values of the inverted tree in post‑order; no return value.  
Algorithm: Uses a breadth‑first search (BFS) to traverse the tree level‑by‑level, swapping each node’s left and right children. After the BFS, a depth‑first traversal visits the inverted tree in post‑order, printing each node’s value. The BFS ensures that the leftmost node of each level is processed before its right sibling, yielding the correct post‑order sequence.

---

## quicksort_ranges — recursive

- anchors: 0 exact, 15 relocated, **0 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int partition(vector<int>& values, int low, int high) {
    int pivot = values[high];
    int boundary = low - 1;
    for (int i = low; i < high; i++)
        if (values[i] <= pivot) swap(values[++boundary], values[i]);
    swap(values[boundary + 1], values[high]);
    return boundary + 1;
}

void quicksort(vector<int>& values, int low, int high) {
    if (low >= high) return;
    int split = partition(values, low, high);
    quicksort(values, low, split - 1);
    quicksort(values, split + 1, high);
}

int main() {
    vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};
    quicksort(values, 0, values.size() - 1);
    for (int v : values) cout << v << " ";
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `int pivot = values[high];` | choose the last element as pivot |
| 11 | `int boundary = low - 1;` | boundary tracks the last element that is <= pivot |
| 12 | `for (int i = low; i < high; i++)` | scan from low to high‑1 |
| 13 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | if current element <= pivot, move it to the boundary slot |
| 14 | `swap(values[boundary + 1], values[high]);` | place pivot after the boundary |
| 15 | `return boundary + 1;` | pivot's final position |
| 20 | `if (low >= high) return;` | base case: empty or single element sub‑array |
| 21 | `int split = partition(values, low, high);` | partition to obtain pivot at split |
| 22 | `quicksort(values, low, split - 1);` | recursively sort left half |
| 23 | `quicksort(values, split + 1, high);` | recursively sort right half |
| 26 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | example data |
| 27 | `quicksort(values, 0, values.size() - 1);` | sort the whole array |
| 28 | `for (int v : values) cout << v << " ";` | output sorted sequence |
| 29 | `cout << "\n";` | newline for clarity |
| 30 | `return 0;` | success |

**Explanation**

Purpose: Sort a vector of integers in ascending order using the quicksort algorithm.  
Input: A reference to a vector<int> containing the data to be sorted, and two indices defining the current sub‑array.  
Output: The vector is reordered in‑place; the function returns the final index of the pivot after partitioning.  
Algorithm: A helper partition function selects the last element as pivot, moves all elements ≤ pivot to the left of a boundary, swaps the pivot into its correct position, and returns the boundary index. The main quicksort recursively sorts the sub‑arrays defined by the pivot and its left/right neighbors. The main loop stops when the sub‑array size is ≤1.

---

## quicksort_ranges — iterative

> **describes this loop as recursive**

- anchors: 4 exact, 7 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: stack

  - *recursion claim*: Recursively sort the left sub‑array.
  - *recursion claim*: Recursively sort the right sub‑array.
  - *container named*: Algorithm: A stack is used to perform a depth‑first traversal of the array, recursively selecting a pivot and partitioning the sub‑array.
  - *container named*: The pivot is placed at the correct position, and the stack pushes the two resulting sub‑arrays for further processing.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int partition(vector<int>& values, int low, int high) {
    int pivot = values[high];
    int boundary = low - 1;
    for (int i = low; i < high; i++)
        if (values[i] <= pivot) swap(values[++boundary], values[i]);
    swap(values[boundary + 1], values[high]);
    return boundary + 1;
}

void quicksort(vector<int>& values, int low, int high) {
    stack<pair<int, int>> ranges;
    ranges.push({low, high});
    while (!ranges.empty()) {
        pair<int, int> range = ranges.top();
        ranges.pop();
        if (range.first >= range.second) continue;
        int split = partition(values, range.first, range.second);
        ranges.push({range.first, split - 1});
        ranges.push({split + 1, range.second});
    }
}

int main() {
    vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};
    quicksort(values, 0, values.size() - 1);
    for (int v : values) cout << v << " ";
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = low; i < high; i++)` | Move elements ≤ pivot to the left side of the partition. |
| 11 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | If the current element is ≤ pivot, it belongs to the left side. |
| 12 | `swap(values[boundary + 1], values[high]);` | Place the pivot after the last element ≤ pivot. |
| 13 | `return boundary + 1;` | Return the final position of the pivot. |
| 18 | `ranges.push({range.first, split - 1});` | Recursively sort the left sub‑array. |
| 19 | `ranges.push({split + 1, range.second});` | Recursively sort the right sub‑array. |
| 23 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Initial sample data. |
| 24 | `quicksort(values, 0, values.size() - 1);` | Sort the entire array in‑place. |
| 25 | `for (int v : values) cout << v << " ";` | Output the sorted array. |
| 26 | `cout << "\n";` | Ensure newline for proper output. |
| 27 | `return 0;` | Success. |

**Explanation**

Purpose: Sort a vector of integers in ascending order using the quicksort algorithm.  
Input: A reference to a vector<int> containing the data to be sorted, and two indices defining the current sub‑array.  
Output: The vector is reordered in‑place; the function returns the number of comparisons made.  
Algorithm: A stack is used to perform a depth‑first traversal of the array, recursively selecting a pivot and partitioning the sub‑array. The pivot is placed at the correct position, and the stack pushes the two resulting sub‑arrays for further processing. The recursion stops when a sub‑array is empty or consists of a single element.

---

## graph_dfs — recursive

> **names a container the code does not use**

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

  - *container NOT in the code*: Algorithm: Initialize a stack with the start node and a boolean vector marking all nodes unvisited.
  - *container NOT in the code*: While the stack is non‑empty, pop a node, mark it visited, output it, then push all its unvisited neighbors onto the stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <vector>
using namespace std;

vector<vector<int>> graph = {
    {1, 2}, {0, 3, 4}, {0, 5}, {1}, {1, 5}, {2, 4, 6}, {5}
};

void dfs(int node, vector<bool>& seen) {
    if (seen[node]) return;
    seen[node] = true;
    cout << node << " ";
    for (int next : graph[node]) dfs(next, seen);
}

int main() {
    vector<bool> seen(graph.size(), false);
    dfs(0, seen);
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (seen[node]) return;` | skip already visited nodes to avoid cycles |
| 11 | `seen[node] = true;` | mark current node as visited |
| 12 | `cout << node << " ";` | output node label (0‑based index) |
| 13 | `for (int next : graph[node]) dfs(next, seen);` | recurse on each neighbor; assumes graph[node] is a vector of neighbors |
| 17 | `vector<bool> seen(graph.size(), false);` | initialize visited flags for all vertices |
| 18 | `dfs(0, seen);` | start DFS from vertex 0 |
| 19 | `cout << "\n";` | output newline after traversal |

**Explanation**

Purpose: Perform a depth‑first search on an undirected graph and print each visited node.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited nodes.  
Output: Prints node values in the order they are visited, followed by a newline.  
Algorithm: Initialize a stack with the start node and a boolean vector marking all nodes unvisited. While the stack is non‑empty, pop a node, mark it visited, output it, then push all its unvisited neighbors onto the stack. The recursion naturally yields a depth‑first traversal.

---

## graph_dfs — iterative

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: stack

  - *container named*: push start node onto stack push start node onto stack pop current node skip already visited nodes mark as visited output node visit successors in reverse order to preserve original DFS order push successor only if it hasn't been visited yet initialize visited flags for all vertices start DFS from vertex 0 terminate output with newline Purpose: Perform a depth‑first traversal of an undirected graph starting from node 0, printing each visited vertex.
  - *container named*: Algorithm: Initialize a stack with the start node and a boolean vector marking all vertices unvisited.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <vector>
using namespace std;

vector<vector<int>> graph = {
    {1, 2}, {0, 3, 4}, {0, 5}, {1}, {1, 5}, {2, 4, 6}, {5}
};

void dfs(int node, vector<bool>& seen) {
    stack<int> pending;
    pending.push(node);
    while (!pending.empty()) {
        int current = pending.top();
        pending.pop();
        if (seen[current]) continue;
        seen[current] = true;
        cout << current << " ";
        for (int i = graph[current].size() - 1; i >= 0; i--)
            if (!seen[graph[current][i]]) pending.push(graph[current][i]);
    }
}

int main() {
    vector<bool> seen(graph.size(), false);
    dfs(0, seen);
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `pending.push(node);` | push start node onto stack |
| 11 | `pending.push(node);` | push start node onto stack |
| 12 | `pending.pop();` | pop current node |
| 13 | `if (seen[current]) continue;` | skip already visited nodes |
| 14 | `seen[current] = true;` | mark as visited |
| 15 | `cout << current << " ";` | output node |
| 16 | `for (int i = graph[current].size() - 1; i >= 0; i--)` | visit successors in reverse order to preserve original DFS order |
| 17 | `if (!seen[graph[current][i]]) pending.push(graph[current][i]);` | push successor only if it hasn't been visited yet |
| 21 | `vector<bool> seen(graph.size(), false);` | initialize visited flags for all vertices |
| 22 | `dfs(0, seen);` | start DFS from vertex 0 |
| 23 | `cout << "\n";` | terminate output with newline |

**Explanation**

Purpose: Perform a depth‑first traversal of an undirected graph starting from node 0, printing each visited vertex.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited vertices.  
Output: Prints the vertices in the order they are visited, followed by a newline.  
Algorithm: Initialize a stack with the start node and a boolean vector marking all vertices unvisited. While the stack is non‑empty, pop the top vertex, mark it as visited, output it, then push all its unvisited neighbors onto the stack in reverse order to preserve post‑order traversal. The loop terminates when the stack is empty.

---

## flood_fill — recursive

- anchors: 4 exact, 10 relocated, **0 quoting a line that is not in the file**, of 14
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int rows, cols;
vector<vector<int>> grid;

void fill(int row, int col, int from, int to) {
    if (row < 0 || row >= rows || col < 0 || col >= cols) return;
    if (grid[row][col] != from) return;
    grid[row][col] = to;
    fill(row + 1, col, from, to);
    fill(row - 1, col, from, to);
    fill(row, col + 1, from, to);
    fill(row, col - 1, from, to);
}

int main() {
    cin >> rows >> cols;
    grid.assign(rows, vector<int>(cols));
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++) cin >> grid[r][c];
    fill(0, 0, grid[0][0], 9);
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";
        cout << "\n";
    }
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (row < 0 \|\| row >= rows \|\| col < 0 \|\| col >= cols) return;` | Guard against out‑of‑bounds coordinates; early exit avoids unnecessary work. |
| 11 | `if (grid[row][col] != from) return;` | Only fill cells that currently hold the source value. |
| 12 | `grid[row][col] = to;` | Replace the source value with the target value. |
| 13 | `fill(row + 1, col, from, to);` | Recurse into all four orthogonal neighbours. |
| 14 | `fill(row - 1, col, from, to);` | Note: the original code had a typo here – it should be `fill(row - 1, col, from, to);`. |
| 15 | `fill(row, col + 1, from, to);` | Note: the original code had a typo here – it should be `fill(row, col + 1, from, to);`. |
| 16 | `fill(row, col - 1, from, to);` | Note: the original code had a typo here – it should be `fill(row, col - 1, from, to);`. |
| 20 | `cin >> rows >> cols;` | Read the grid dimensions. |
| 21 | `grid.assign(rows, vector<int>(cols));` | Allocate the grid with the specified dimensions. |
| 22 | `for (int r = 0; r < rows; r++)` | Read the grid values row‑wise. |
| 25 | `fill(0, 0, grid[0][0], 9);` | Start filling from the top‑left corner with the initial value. |
| 26 | `for (int r = 0; r < rows; r++) {` | Output the transformed grid. |
| 27 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Note: the original code had a typo here – it should be `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";`. |
| 28 | `cout << "\n";` | Note: the original code had a typo here – it should be `cout << "\n";`. |

**Explanation**

Purpose: Replace all occurrences of a specified value in a 2‑D grid with another value.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of integers; `from` – value to find; `to` – value to replace.  
Output: The grid is modified in‑place; the function returns `int` (0).  
Algorithm: Perform a depth‑first search from the start cell, marking each cell with `to` when it matches `from`. The search recurses to all four orthogonal neighbors, ensuring all reachable cells are updated. The main loop prints the final grid.

---

## flood_fill — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first search using a stack, pushing each cell onto the stack only if it is within bounds and matches the original value.
  - *container named*: The process repeats until the stack is empty.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int rows, cols;
vector<vector<int>> grid;

void fill(int row, int col, int from, int to) {
    if (from == to) return;
    stack<pair<int, int>> pending;
    pending.push({row, col});
    while (!pending.empty()) {
        pair<int, int> cell = pending.top();
        pending.pop();
        int r = cell.first, c = cell.second;
        if (r < 0 || r >= rows || c < 0 || c >= cols) continue;
        if (grid[r][c] != from) continue;
        grid[r][c] = to;
        pending.push({r - 1, c});
        pending.push({r, c - 1});
        pending.push({r, c + 1});
        pending.push({r + 1, c});
    }
}

int main() {
    cin >> rows >> cols;
    grid.assign(rows, vector<int>(cols));
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++) cin >> grid[r][c];
    fill(0, 0, grid[0][0], 9);
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";
        cout << "\n";
    }
    return 0;
}
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Flood‑fill a 2‑D grid from a starting cell to a target value.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of integers; `fill` parameters – start row, start col, original value, and target value.  
Output: Modifies `grid` in‑place; prints the filled grid to `stdout`.  
Algorithm: Perform a depth‑first search using a stack, pushing each cell onto the stack only if it is within bounds and matches the original value. When a cell is popped, it is replaced with the target value and its four neighbours are pushed. The process repeats until the stack is empty.

---

## sum_digits_tree — recursive

- anchors: 0 exact, 13 relocated, **1 quoting a line that is not in the file**, of 14
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int paths(Node* node, int carried) {
    if (node == nullptr) return 0;
    carried = carried * 10 + node->value;
    if (node->left == nullptr && node->right == nullptr) return carried;
    return paths(node->left, carried) + paths(node->right, carried);
}

int main() { cout << paths(sample(), 0) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 11 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 1, 6, 4, 7 → 10 → 14 → 13 |
| 12 | `root->left = new Node(3);` | left child of 8 |
| 13 | `root->right = new Node(10);` | right child of 8 |
| 14 | `root->left->left = new Node(1);` | left child of 3 |
| 15 | `root->left->right = new Node(6);` | right child of 3 |
| 16 | `root->left->right->left = new Node(4);` | left child of 6 |
| 17 | `root->left->right->right = new Node(7);` | right child of 6 |
| 18 | `root->right->right = new Node(14);` | right child of 10 |
| 19 | `root->right->right->left = new Node(13);` | left child of 14 |
| 22 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no paths |
| 23 | `carried = carried * 10 + node->value;` | Update the running number with the current node's value |
| 24 | `if (node->left == nullptr && node->right == nullptr) return carried;` | Leaf reached: the number formed by the path is a valid candidate |
| 25 | `return paths(node->left, carried) + paths(node->right, carried);` | Propagate the accumulated value to children |
| 28 | `cout << paths(sample(), 0) << "\n";` | Output the total number of paths in the tree |

**Explanation**

Purpose: Counts all root‑to‑leaf paths whose values form a multiple of 10.  
Input: Node* root – pointer to the binary tree’s root (or nullptr for an empty tree). int carried – accumulator of the current path value (initially 0).  
Output: int – total number of such paths.  
Algorithm: Perform a depth‑first traversal, maintaining the accumulated value. When a leaf is reached, check if the accumulated value is a multiple of 10; if so, increment the result. The recursion accumulates paths from each node, yielding the final count.

---

## sum_digits_tree — iterative

- anchors: 0 exact, 6 relocated, **1 quoting a line that is not in the file**, of 7
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, maintaining the current accumulated sum.
  - *container named*: The traversal continues until the stack is empty, yielding the total count.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int paths(Node* node, int carried) {
    if (node == nullptr) return 0;
    stack<pair<Node*, int>> pending;
    pending.push({node, carried});
    int total = 0;
    while (!pending.empty()) {
        pair<Node*, int> item = pending.top();
        pending.pop();
        Node* current = item.first;
        int running = item.second * 10 + current->value;
        if (current->left == nullptr && current->right == nullptr) {
            total += running;
            continue;
        }
        if (current->left) pending.push({current->left, running});
        if (current->right) pending.push({current->right, running});
    }
    return total;
}

int main() { cout << paths(sample(), 0) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 1, 6, 4, 7 → 10 → 14 → 13 |
| 14 | `Node* current = item.first;` | Process the node with accumulated value |
| 15 | `int running = item.second * 10 + current->value;` | Build the current number as a decimal string |
| 16 | `if (current->left == nullptr && current->right == nullptr) {` | Leaf reached: add the number to the total |
| 19 | `if (current->left) pending.push({current->left, running});` | Push children for further processing |
| 22 | `return total;` | Return the total count of paths |
| 25 | `cout << paths(sample(), 0) << "\n";` | Sample tree: 8 → 3 → 1, 6, 4, 7 → 10 → 14 → 13 |

**Explanation**

Purpose: Counts all root‑to‑leaf paths whose total value equals a given sum.  
Input: Node* root – pointer to the binary tree root; int carried – accumulated sum of the current path.  
Output: int – total number of such paths.  
Algorithm: Perform a depth‑first traversal using a stack, maintaining the current accumulated sum. When a leaf is reached, add the sum to the result if it matches the target. The traversal continues until the stack is empty, yielding the total count.

---

## DATASET.json#10 — recursive

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>

using namespace std;

class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        if (l1 == NULL && l2 == NULL) return NULL;
        else if (l1 == NULL) return l2;
        else if (l2 == NULL) return l1;

        int a = l1->val + l2->val;
        ListNode* p = new ListNode(a % 10);
        p->next = addTwoNumbers(l1->next, l2->next);

        if (a >= 10)
            p->next = addTwoNumbers(p->next, new ListNode(1));

        return p;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (l1 == NULL && l2 == NULL) return NULL;` | If both input lists are empty, the result is also empty. |
| 4 | `else if (l1 == NULL) return l2;` | If only l1 is empty, the result is l2. |
| 5 | `else if (l2 == NULL) return l1;` | If only l2 is empty, the result is l1. |
| 7 | `int a = l1->val + l2->val;` | Compute the sum of the current digits. |
| 8 | `ListNode* p = new ListNode(a % 10);` | Create a new node with the least‑significant digit of the sum. |
| 9 | `p->next = addTwoNumbers(l1->next, l2->next);` | Recursively add the remaining digits. |
| 11 | `if (a >= 10)` | If the sum was >= 10, propagate the carry to the next node. |
| 12 | `p->next = addTwoNumbers(p->next, new ListNode(1));` | Append a new node with value 1 to represent the carry. |
| 13 | `return p;` | Return the head of the constructed result list. |

**Explanation**

Purpose: Adds two non‑negative numbers represented as singly‑linked lists, each node containing a single digit.  
Input: ListNode* l1 – head of the first number; ListNode* l2 – head of the second number.  
Output: ListNode* – head of a new list representing the sum, with no leading zero.  
Algorithm: Recursively traverse both lists, adding corresponding digits and carrying over any overflow. When a carry is needed, a new node with value 1 is appended to the result list. The recursion stops when both input lists become null.

---

## DATASET.json#10 — iterative

- anchors: 0 exact, 13 relocated, **0 quoting a line that is not in the file**, of 13
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>

using namespace std;

class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode* dummyHead = new ListNode(0);
        ListNode* tail = dummyHead;
        int carry = 0;

        while (l1 != nullptr || l2 != nullptr || carry != 0) {
            int digit1 = (l1 != nullptr) ? l1->val : 0;
            int digit2 = (l2 != nullptr) ? l2->val : 0;

            int sum = digit1 + digit2 + carry;
            int digit = sum % 10;
            carry = sum / 10;

            ListNode* newNode = new ListNode(digit);
            tail->next = newNode;
            tail = tail->next;

            l1 = (l1 != nullptr) ? l1->next : nullptr;
            l2 = (l2 != nullptr) ? l2->next : nullptr;
        }

        ListNode* result = dummyHead->next;
        delete dummyHead;
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (l1 != nullptr \|\| l2 != nullptr \|\| carry != 0) {` | Continue processing while either list has remaining nodes or there is a carry left over from previous addition. |
| 11 | `int digit1 = (l1 != nullptr) ? l1->val : 0;` | Retrieve value from l1; if l1 is nullptr, treat it as 0. |
| 12 | `int digit2 = (l2 != nullptr) ? l2->val : 0;` | Retrieve value from l2; if l2 is nullptr, treat it as 0. |
| 13 | `int sum = digit1 + digit2 + carry;` | Sum the current digits and any carry from the previous step. |
| 14 | `int digit = sum % 10;` | Extract the least‑significant digit of the sum. |
| 15 | `carry = sum / 10;` | Compute the carry for the next iteration. |
| 16 | `ListNode* newNode = new ListNode(digit);` | Create a new node for the result list. |
| 17 | `tail->next = newNode;` | Append the new node to the list. |
| 18 | `tail = tail->next;` | Move the tail pointer forward. |
| 19 | `l1 = (l1 != nullptr) ? l1->next : nullptr;` | Advance l1 if it exists; otherwise set to nullptr. |
| 20 | `l2 = (l2 != nullptr) ? l2->next : nullptr;` | Advance l2 if it exists; otherwise set to nullptr. |
| 22 | `ListNode* result = dummyHead->next;` | Skip the dummy head node and return the actual result list. |
| 23 | `delete dummyHead;` | Clean up the dummy head node. |

**Explanation**

Purpose: Adds two non‑negative numbers represented as linked lists, each node containing a single digit.  
Input: ListNode* l1 – head of the first number; ListNode* l2 – head of the second number.  
Output: ListNode* – head of a new list representing the sum, with a leading zero if the sum is zero.  
Algorithm: Walk both lists simultaneously, handling carry from previous digits. For each pair of digits, compute the sum, extract the least‑significant digit, and propagate any carry to the next iteration. Continue until both lists are exhausted and the carry is zero. Finally, reconstruct the result list and clean up the dummy head.

---

## DATASET.json#11 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    bool isMatch(string s, string p) {
        if (p.empty())    return s.empty();
        
        if ('*' == p[1])
            // x* matches empty string or at least one character: x* -> xx*
            // *s is to ensure s is non-empty
            return (isMatch(s, p.substr(2)) || !s.empty() && (s[0] == p[0] || '.' == p[0]) && isMatch(s.substr(1), p));
        else
            return !s.empty() && (s[0] == p[0] || '.' == p[0]) && isMatch(s.substr(1), p.substr(1));
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (p.empty())    return s.empty();` | Base case: if pattern is empty, only a matching empty string is allowed. |
| 5 | `if ('*' == p[1])` | If the second character of the pattern is '*', it can match zero or more preceding characters. |
| 6 | `return (isMatch(s, p.substr(2)) \|\| !s.empty() && (s[0] == p[0] \|\| '.' == p[0]) && isMatch(s.substr(1), p));` | Try two possibilities: 1) skip the '*' and the preceding character; 2) consume the first character of s if it matches the current character or is a '.'. The second condition ensures that the '*' can match an empty string. |
| 9 | `return !s.empty() && (s[0] == p[0] \|\| '.' == p[0]) && isMatch(s.substr(1), p.substr(1));` | If the second character is not '*', the current characters must match exactly. |

**Explanation**

Purpose: Determines whether the pattern string `p` matches the string `s`.
Input: Two strings `s` and `p`.
Output: A boolean indicating whether `s` matches `p`.
Algorithm: Uses recursion to explore all possible matches between `s` and `p`. It handles the special case where the second character of `p` is '*', which can match zero or more characters in `s`.

---

## DATASET.json#11 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstring>
using namespace std;

class Solution {
public:
    bool isMatch(string s, string p) {
        int n = s.length(), m = p.length();
        bool dp[n+1][m+1];
        memset(dp, false, sizeof(dp));
        dp[0][0] = true;
        
        for(int i=0; i<=n; i++){
            for(int j=1; j<=m; j++){
                if(p[j-1] == '*'){
                    dp[i][j] = dp[i][j-2] || (i > 0 && (s[i-1] == p[j-2] || p[j-2] == '.') && dp[i-1][j]);
                }
                else{
                    dp[i][j] = i > 0 && dp[i-1][j-1] && (s[i-1] == p[j-1] || p[j-1] == '.');
                }
            }
        }
        
        return dp[n][m];
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for(int i=0; i<=n; i++){` | Build the DP table row by row. dp[i][j] will store whether s[0..i) matches p[0..j). |
| 11 | `for(int j=1; j<=m; j++){` | First column (j==0) is always false because a pattern with no characters cannot match an empty string. |
| 12 | `if(p[j-1] == '*'){` | If the current pattern character is '*', we have two choices: 1) skip the '*': dp[i][j] = dp[i][j-2] (i.e., ignore the '*' and the preceding character). 2) match the preceding character: dp[i][j] = dp[i][j-2] && (i > 0 && (s[i-1] == p[j-2] \|\| p[j-2] == '.') && dp[i-1][j]). The second condition checks that the preceding character in s matches the current character in p or is a '.'. |
| 13 | `else{` | If the current pattern character is not '*', we can only match if the preceding characters in s and p match and the preceding s character is not '*' (to avoid infinite loops). |
| 14 | `dp[i][j] = i > 0 && dp[i-1][j-1] && (s[i-1] == p[j-1] \|\| p[j-1] == '.');` | dp[i][j] = dp[i-1][j-1] && (s[i-1] == p[j-1] \|\| p[j-1] == '.'); |
| 17 | `return dp[n][m];` | The final result is dp[n][m]. |

**Explanation**

Purpose: Determines whether string s matches pattern p.  
Input: s – source string; p – pattern string possibly containing ‘*’ as a wildcard.  
Output: bool – true if s can be made to equal p by inserting ‘*’ where needed.  
Algorithm: Uses dynamic programming where dp[i][j] stores whether s[0..i) matches p[0..j). For each character, if p[j] is ‘*’, it can either skip the preceding character in s or match the current character if they match or are either ‘.’ or ‘*’. Otherwise, it must match the current characters and the preceding state. The result is dp[n][m].

---

## DATASET.json#12 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode *mergeTwoLists(ListNode *l1, ListNode *l2) {
        if(l1 == NULL) return l2;
        if(l2 == NULL) return l1;
        
        if(l1->val < l2->val) {
            l1->next = mergeTwoLists(l1->next, l2);
            return l1;
        } else {
            l2->next = mergeTwoLists(l2->next, l1);
            return l2;
        }
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(l1 == NULL) return l2;` | If the first list is empty, the merge is already complete. |
| 4 | `if(l2 == NULL) return l1;` | If the second list is empty, the merge is already complete. |
| 6 | `if(l1->val < l2->val) {` | Choose the smaller head node as the new merged list head. |
| 7 | `l1->next = mergeTwoLists(l1->next, l2);` | Recursively merge the rest of the lists. |
| 8 | `return l1;` | Return the merged list starting with the chosen node. |
| 10 | `l2->next = mergeTwoLists(l2->next, l1);` | Choose the smaller head node as the new merged list head. |
| 11 | `return l2;` | Return the merged list starting with the chosen node. |

**Explanation**

Purpose: Merge two sorted singly‑linked lists into a single sorted list.  
Input: ListNode* l1 – head of the first sorted list; ListNode* l2 – head of the second sorted list.  
Output: ListNode* – head of the merged sorted list.  
Algorithm: Recursively compare the current nodes of l1 and l2; if l1’s value is smaller, link it to the result of merging the rest of l1 with l2; otherwise link l2 to the result of merging l1 with the rest of l2. The recursion terminates when either list becomes null, yielding the merged list.

---

## DATASET.json#12 — iterative

- anchors: 9 exact, 3 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
        ListNode* dummy = new ListNode(0);
        ListNode* cur = dummy;

        while (list1 && list2) {
            if (list1->val > list2->val) {
                cur->next = list2;
                list2 = list2->next;
            } else {
                cur->next = list1;
                list1 = list1->next;
            }
            cur = cur->next;
        }

        cur->next = list1 ? list1 : list2;

        ListNode* head = dummy->next;
        delete dummy;
        return head;        
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (list1 && list2) {` | Merge the two sorted lists while both remain non‑null |
| 11 | `if (list1->val > list2->val) {` | Choose the smaller node for the merged list |
| 12 | `cur->next = list2;` | Insert list2 node after cur |
| 13 | `list2 = list2->next;` | Advance list2 pointer |
| 14 | `} else {` | list1->val <= list2->val |
| 15 | `cur->next = list1;` | Insert list1 node after cur |
| 16 | `list1 = list1->next;` | Advance list1 pointer |
| 17 | `}` | list1->val > list2->val |
| 18 | `cur = cur->next;` | Move to the newly inserted node |
| 20 | `cur->next = list1 ? list1 : list2;` | Append any remaining nodes from the non‑exhausted list |
| 21 | `ListNode* head = dummy->next;` | dummy is a dummy node; the real head is dummy->next |
| 22 | `delete dummy;` | Free the dummy node to avoid memory leak |

**Explanation**

Purpose: Merge two sorted singly‑linked lists into a single sorted list.  
Input: ListNode* list1 – head of the first sorted list; ListNode* list2 – head of the second sorted list.  
Output: ListNode* – head of the merged sorted list.  
Algorithm: Use a dummy node to build the result list, then repeatedly pick the smaller of the two heads and advance the corresponding list. After the loop, append the remaining nodes of the non‑empty list. Finally, detach the dummy and return the merged list.

---

## DATASET.json#13 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        if(!head || !head->next) return head;
        ListNode* temp;
        temp = head->next;
        head->next = swapPairs(head->next->next);
        temp->next = head;
        
        return temp;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(!head \|\| !head->next) return head;` | Base case: if the list has fewer than two nodes, nothing to swap. |
| 5 | `temp = head->next;` | Store the first node of the next pair for later linkage. |
| 6 | `head->next = swapPairs(head->next->next);` | Recursively swap the next pair; the result becomes the new head of the current pair. |
| 7 | `temp->next = head;` | Link the stored node back to the current head, completing the swap. |

**Explanation**

Purpose: To swap every two adjacent nodes in a singly linked list.
Input: A pointer to the head of the linked list.
Output: A pointer to the head of the modified linked list with swapped pairs.
Algorithm: Recursively traverse the list, swapping each pair of nodes until the end is reached.

---

## DATASET.json#13 — iterative

> **names a container the code does not use**

- anchors: 0 exact, 21 relocated, **0 quoting a line that is not in the file**, of 21
- containers in the code: none

  - *container NOT in the code*: Use a stack to process pairs in reverse order.
  - *container NOT in the code*: Push the current node and its successor onto the stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        if(head == nullptr || head->next == nullptr) {
            return head;
        }

        ListNode* newHead = head->next;

        vector<ListNode*> stack;
        ListNode* node = head;

        while(node != nullptr && node->next != nullptr) {
            ListNode* cur = node;
            ListNode* next = cur->next;
            stack.push_back(cur);
            stack.push_back(next);
            node = next->next;
        }

        while(!stack.empty()) {
            ListNode* next = stack.back();
            stack.pop_back();
            ListNode* cur = stack.back();
            stack.pop_back();

            cur->next = next->next;
            next->next = cur;

            if(!stack.empty()) {
                ListNode* prev = stack.back();
                prev->next = next;
            }
        }

        return newHead;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(head == nullptr \|\| head->next == nullptr) {` | If the list is empty or has only one node, no swaps are needed. |
| 6 | `ListNode* newHead = head->next;` | The first pair will become the new head after swapping. |
| 8 | `vector<ListNode*> stack;` | Use a stack to process pairs in reverse order. |
| 9 | `ListNode* node = head;` | Start processing from the original head. |
| 11 | `while(node != nullptr && node->next != nullptr) {` | Process pairs until we reach the end of the list. |
| 12 | `ListNode* cur = node;` | Current node of the pair. |
| 13 | `ListNode* next = cur->next;` | Next node of the pair. |
| 14 | `stack.push_back(cur);` | Push the current node and its successor onto the stack. |
| 15 | `stack.push_back(next);` | Push the successor node onto the stack. |
| 16 | `node = next->next;` | Move to the next pair. |
| 19 | `while(!stack.empty()) {` | Pop pairs from the stack and swap them. |
| 20 | `ListNode* next = stack.back();` | Current node of the pair. |
| 21 | `stack.pop_back();` | Remove the current node from the stack. |
| 22 | `ListNode* cur = stack.back();` | Previous node of the pair. |
| 23 | `stack.pop_back();` | Remove the previous node from the stack. |
| 24 | `cur->next = next->next;` | Connect the previous node to the next node of the current pair. |
| 25 | `next->next = cur;` | Connect the current node to the previous node of the next pair. |
| 26 | `if(!stack.empty()) {` | If there is a remaining node after the current pair, connect it to the next node of the previous pair. |
| 27 | `ListNode* prev = stack.back();` | Previous node of the pair. |
| 28 | `prev->next = next;` | Connect the previous node to the next node of the current pair. |
| 30 | `return newHead;` | Return the new head of the list. |

**Explanation**

Purpose: To swap every pair of adjacent nodes in a singly linked list.
Input: A pointer to the head of the linked list.
Output: A pointer to the head of the modified linked list with swapped pairs.
Algorithm: Uses a stack to temporarily store nodes for swapping and then iterates through the list to connect these nodes back together.

---

## DATASET.json#14 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        ListNode* cursor = head;
        for(int i = 0; i < k; i++){
            if(cursor == nullptr) return head;
            cursor = cursor->next;
        }
        ListNode* curr = head;
        ListNode* prev = nullptr;
        ListNode* nxt = nullptr;
        for(int i = 0; i < k; i++){
            nxt = curr->next;
            curr->next = prev;
            prev = curr;
            curr = nxt;
        }
        head->next = reverseKGroup(curr, k);
        return prev;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if(cursor == nullptr) return head;` | If the remaining list length is insufficient to form a k‑group, stop recursion. |
| 14 | `for(int i = 0; i < k; i++){` | Separate the first k nodes from the rest of the list. |
| 18 | `for(int i = 0; i < k; i++){` | Reverse the k‑group in‑place. |
| 22 | `head->next = reverseKGroup(curr, k);` | Recursively reverse the next k‑group and attach the reversed segment. |

**Explanation**

Purpose: Reverses every k‑length group of a singly‑linked list.  
Input: `head` – pointer to the first node of the list; `k` – size of each group.  
Output: Pointer to the new head of the list after all groups have been reversed.  
Algorithm: First locate the k‑th node; if it is null, the list cannot be split into groups of k. Then reverse the first k nodes, recursively reverse the remaining part, and link the reversed segment back to the original head.

---

## DATASET.json#14 — iterative

- anchors: 0 exact, 15 relocated, **0 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        ListNode* dummy = new ListNode(0);
        dummy->next = head;
        ListNode* before = dummy;
        ListNode* after = head;
        ListNode* curr = nullptr;
        ListNode* prev = nullptr;
        ListNode* nxt = nullptr;
        while(true){
            ListNode* cursor = after;
            for(int i = 0; i < k; i++){
                if(cursor == nullptr) return dummy->next;
                cursor = cursor->next;
            }
            curr = after;
            prev = before;
            for(int i = 0; i < k; i++){
                nxt = curr->next;
                curr->next = prev;
                prev = curr;
                curr = nxt;
            }
            after->next = curr;
            before->next = prev;
            before = after;
            after = curr;
        }
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while(true){` | Iterate until the list is fully processed. |
| 11 | `ListNode* cursor = after;` | Find the k‑th node from the current position. |
| 12 | `for(int i = 0; i < k; i++){` | Advance the cursor k steps. |
| 13 | `if(cursor == nullptr) return dummy->next;` | If the list is shorter than k, reverse the remaining nodes and return. |
| 16 | `curr = after;` | Store the k‑th node as the new head of the reversed segment. |
| 17 | `prev = before;` | Move the segment's tail to the previous node. |
| 18 | `for(int i = 0; i < k; i++){` | Reverse the segment in‑place. |
| 19 | `nxt = curr->next;` | Keep the next node for the next iteration. |
| 20 | `curr->next = prev;` | Reverse the link. |
| 21 | `prev = curr;` | Advance the segment's tail. |
| 22 | `curr = nxt;` | Move to the next node. |
| 24 | `after->next = curr;` | Connect the reversed segment to the rest of the list. |
| 25 | `before->next = prev;` | Update the previous segment's tail. |
| 26 | `before = after;` | Move to the next group. |
| 27 | `after = curr;` | Start the next iteration from the new head. |

**Explanation**

Purpose: Reverses every k‑length group in a singly‑linked list.  
Input: `head` – pointer to the first node of the list; `k` – size of each group.  
Output: Pointer to the new head of the list after all groups have been reversed.  
Algorithm: A dummy node acts as a sentinel for the reversal process. Two pointers (`before` and `after`) traverse the list, stopping after each k‑node segment. Inside the segment, the nodes are reversed in‑place, and the pointers advance accordingly. The loop repeats until the end of the list is reached.

---

## DATASET.json#15 — recursive

- anchors: 1 exact, 14 relocated, **0 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    bool isMatch(string s, string p) {
        return solve(s.size() - 1, p.size() - 1, s, p);
    }

private:
    bool solve(int i, int j, string &s, string &p) {
        if (i < 0 && j < 0)
            return true;

        if (i >= 0 && j < 0)
            return false;

        if (i < 0 && j >= 0)
            return isAllStars(p, j);

        if (s[i] == p[j] || p[j] == '?')
            return solve(i - 1, j - 1, s, p);

        if (p[j] == '*')
            return solve(i - 1, j, s, p) ||
                   solve(i, j - 1, s, p);

        return false;
    }

    bool isAllStars(string &p, int j) {
        for (int k = 0; k <= j; k++) {
            if (p[k] != '*')
                return false;
        }
        return true;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return solve(s.size() - 1, p.size() - 1, s, p);` | delegate to the full‑length helper; handles empty strings correctly |
| 14 | `if (i < 0 && j < 0)` | both strings exhausted – success only if pattern is also empty |
| 15 | `return false;` | pattern exhausted before source |
| 16 | `if (i >= 0 && j < 0)` | source exhausted before pattern – failure |
| 17 | `return isAllStars(p, j);` | source exhausted, pattern still has stars – only if all remaining stars are at the end |
| 18 | `if (s[i] == p[j] \|\| p[j] == '?')` | current characters match or pattern is '?' |
| 19 | `return solve(i - 1, j - 1, s, p);` | consume both characters |
| 20 | `if (p[j] == '*')` | pattern is '*' |
| 21 | `return solve(i - 1, j, s, p) \|\|` | either skip source or skip pattern |
| 22 | `solve(i, j - 1, s, p);` | skip source and keep pattern |
| 23 | `return false;` | no match possible |
| 26 | `for (int k = 0; k <= j; k++) {` | verify that the remaining pattern stars are all '*' |
| 27 | `if (p[k] != '*')` | first non‑star breaks the pattern |
| 28 | `return false;` | pattern cannot be satisfied |
| 29 | `return true;` | all stars are '*' |

**Explanation**

Purpose: Determines whether a given string `s` matches a pattern `p` where `p` may contain `*` as a wildcard for any character.
Input: Two strings `s` and `p`.
Output: A boolean indicating whether `s` matches `p`.
Algorithm: Uses recursion to explore all possible matches between `s` and `p`. It handles different scenarios such as matching characters, ignoring characters, and using `*` as a wildcard.

---

## DATASET.json#15 — iterative

- anchors: 2 exact, 16 relocated, **0 quoting a line that is not in the file**, of 18
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    bool isMatch(string s, string p) {
        int i = 0;
        int j = 0;

        int last_match = 0;
        int star = -1;

        while (i < s.length()) {
            if (j < p.length() && (s[i] == p[j] || p[j] == '?')) {
                i++;
                j++;
            }
            else if (j < p.length() && p[j] == '*') {
                last_match = i;
                star = j;
                j++;
            }
            else if (star != -1) {
                j = star + 1;
                i = last_match + 1;
                last_match++;
            }
            else {
                return false;
            }
        }

        while (j < p.length() && p[j] == '*') {
            j++;
        }

        return j == p.length();
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (i < s.length()) {` | Scan both strings until the end of the shorter one |
| 11 | `if (j < p.length() && (s[i] == p[j] \|\| p[j] == '?')) {` | If characters match or '?' is encountered, consume both strings |
| 12 | `i++;` | Advance s pointer |
| 13 | `j++;` | Advance p pointer |
| 14 | `else if (j < p.length() && p[j] == '*') {` | If current p character is '*', we can either skip the current s character or consume the whole s string |
| 15 | `last_match = i;` | Remember position of last match |
| 16 | `star = j;` | Remember position of '*' |
| 17 | `j++;` | Advance p pointer |
| 18 | `else if (star != -1) {` | If we have a saved '*' position, we can consume the s string from the last match |
| 19 | `j = star + 1;` | Advance p pointer past '*' |
| 20 | `i = last_match + 1;` | Reset s pointer to last match position |
| 21 | `last_match++;` | Advance last match position |
| 22 | `else {` | No match found |
| 23 | `return false;` | Return false immediately |
| 24 | `}` | Note: star == -1 when no '*' was seen before |
| 26 | `while (j < p.length() && p[j] == '*') {` | After scanning, consume any remaining '*' characters |
| 27 | `j++;` | Advance p pointer |
| 28 | `}` | Return true if all characters of p have been consumed |

**Explanation**

Purpose: Determines whether string s matches pattern p, where ‘?’ can represent any single character and ‘*’ can represent zero or more characters.  
Input: two std::string objects s and p.  
Output: bool indicating whether s matches p.  
Algorithm: Uses a three‑pointer scan that tracks the last successful character in s and the position of the previous ‘*’ (star). When a character mismatch occurs, it either skips the next character in s or jumps to the next ‘*’ and resets the scan. After the scan, it checks for trailing ‘*’ characters.

---

## DATASET.json#16 — recursive

- anchors: 3 exact, 8 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <climits>
using namespace std;

class Solution {
private:
    double power(double x, int n){
        if(n==0){
            return 1;
        }
        return x * power(x, n-1);
    }
public:
    double myPow(double x, int n) {
        if (n == INT_MAX) return (x == 1) ? 1 : (x == -1) ? -1 : 0;
        if (n == INT_MIN) return (x == 1 || x == -1) ? 1 : 0;
        double num = 1;
        if(n>=0){
            num = power(x, n);
        }
        else{
            n = -n;
            num = power(x, n);
            num = 1.0/num;
        }
        return num;
    }
};

/*

    Time Complexity : O(N), because we loop until we multiply the base exponent times. Thus the time complexity
    is linear.

    Space Complexity : O(1), Constant space.

*/
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return 1;` | base case: any number raised to the power 0 equals 1 |
| 12 | `return x * power(x, n-1);` | recursive step: multiply current base by result of smaller exponent |
| 16 | `if (n == INT_MAX) return (x == 1) ? 1 : (x == -1) ? -1 : 0;` | handle overflow for INT_MAX exponent |
| 17 | `if (n == INT_MIN) return (x == 1 \|\| x == -1) ? 1 : 0;` | handle underflow for INT_MIN exponent |
| 18 | `double num = 1;` | initialize result accumulator |
| 19 | `if(n>=0){` | positive exponent: compute power iteratively |
| 20 | `num = power(x, n);` | recursive call |
| 22 | `n = -n;` | negative exponent: convert to positive and invert result |
| 23 | `num = power(x, n);` | compute positive power |
| 24 | `num = 1.0/num;` | invert result to achieve correct sign |
| 25 | `return num;` | return final result |

**Explanation**

Purpose: Compute x raised to the power n using recursion.  
Input: double x – base; int n – exponent (may be negative, zero, or INT_MAX/INT_MIN).  
Output: double – the result of xⁿ.  
Algorithm: Handles the special cases of n == INT_MAX or n == INT_MIN directly. For other n, it recursively multiplies x by itself n times, handling the negative exponent by inverting the result after the recursive call. The recursion depth is bounded by the magnitude of n.

---

## DATASET.json#16 — iterative

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <cmath>
using namespace std;

class Solution {
public:
    double myPow(double x, int n) {
        double val = (double) pow(x, n);
        return val;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `double val = (double) pow(x, n);` | Convert the integer exponent to a double to avoid overflow when x is large. |
| 4 | `return val;` | Return the computed power as a double. |

**Explanation**

Purpose: Computes x raised to the power n using the standard library pow.  
Input: double x – base; int n – exponent.  
Output: double – the result of xⁿ.  
Algorithm: The function casts the result of std::pow to double and returns it. No special handling for negative exponents or overflow is performed; the library’s implementation may truncate or overflow.

---

## DATASET.json#17 — recursive

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Solution {
public:
    string getPermutation(int n, int k) {
        vector<int> nums;
        for (int i = 1; i <= n; i++) {
            nums.push_back(i);
        }

        return solve(nums, k);
    }

private:
    string solve(vector<int>& nums, int k) {
        if (nums.size() == 1) {
            return to_string(nums[0]);
        }

        int fact = 1;
        for (int i = 1; i < nums.size(); i++) {
            fact *= i;
        }

        k = k - 1;
        int index = k / fact;
        k = k % fact;

        int num = nums[index];
        nums.erase(nums.begin() + index);

        return to_string(num) + solve(nums, k + 1);
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return solve(nums, k);` | start recursion with the full list |
| 14 | `if (nums.size() == 1) {` | base case: only one element left |
| 15 | `return to_string(nums[0]);` | single element permutation is the element itself |
| 18 | `k = k - 1;` | convert 1‑based index to 0‑based for selection |
| 19 | `int index = k / fact;` | choose element that would be at position k in a full permutation |
| 20 | `k = k % fact;` | remaining elements after selection |
| 21 | `int num = nums[index];` | extract the chosen element |
| 22 | `nums.erase(nums.begin() + index);` | remove the chosen element from the list |
| 23 | `return to_string(num) + solve(nums, k + 1);` | recurse on the reduced list, offsetting k by 1 to account for the chosen element |

**Explanation**

Purpose: Generate the k‑th lexicographic permutation of the numbers 1…n.  
Input: int n – size of the set; int k – 1‑based index of the desired permutation.  
Output: string – the k‑th permutation as a decimal string.  
Algorithm: Build a list of numbers 1…n, then repeatedly select the smallest remaining element, remove it, and recurse on the reduced list, accumulating the result. The recursion uses factorial to compute the position of the selected element efficiently.

---

## DATASET.json#17 — iterative

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Solution {
public:
    string getPermutation(int n, int k) {

        // First Creating the array, and finding (n-1)!
        vector<int> nums;
        int fact = 1;

        for (int i = 1; i < n; i++) {
            nums.push_back(i);
            fact *= i;
        }
        nums.push_back(n);

        string ans = "";
        k = k - 1; // 0 index based

        while (true) {

            ans = ans + to_string(nums[k / fact]);

            nums.erase(nums.begin() + k / fact);

            if (nums.size() == 0) {
                break;
            }

            k = k % fact;

            fact = fact / nums.size();
        }

        return ans;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = 1; i < n; i++) {` | Build the sequence of numbers 1..n, storing them in a vector and computing (n-1)! |
| 11 | `nums.push_back(i);` | add current number |
| 12 | `fact *= i;` | update factorial for next position |
| 14 | `nums.push_back(n);` | append the last number |
| 17 | `k = k - 1; // 0 index based` | convert to 0‑based index for the loop |
| 18 | `while (true) {` | Iterate through the sequence, removing each element at position k/fact! |
| 19 | `ans = ans + to_string(nums[k / fact]);` | append the selected digit |
| 20 | `nums.erase(nums.begin() + k / fact);` | remove the selected digit |
| 21 | `if (nums.size() == 0) {` | when only one element remains, we have the permutation |
| 24 | `k = k % fact;` | reduce k for the next iteration |
| 25 | `fact = fact / nums.size();` | update factorial for the next position |
| 27 | `return ans;` | return the generated permutation |

**Explanation**

Purpose: Generate the k‑th lexicographic permutation of the digits 1…n.  
Input: int n – size of the set; int k – 1‑based index of the desired permutation.  
Output: string – the k‑th permutation as a decimal string.  
Algorithm: Build a list of digits 1…n, compute factorials up to (n‑1)! to map each position to a unique digit, then repeatedly extract the digit at position k / fact, remove it from the list, and reduce k modulo the remaining factorial. The loop stops when only one element remains.

---

## DATASET.json#18 — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
private:
    ListNode* left;
    bool stop;

    void reorder(ListNode* right) {
        if (right == nullptr) {
            return;
        }
        
        reorder(right->next);
        
        if (stop) {
            return;
        }

        if (left == right || left->next == right) {
            right->next = nullptr;
            stop = true;
            return;
        }
        
        ListNode* temp = left->next;
        left->next = right;
        right->next = temp;
        
        left = temp;
    }

public:
    void reorderList(ListNode* head) {
        if (head == nullptr || head->next == nullptr) return;
        
        left = head;
        stop = false;
        
        reorder(head);
    }
};
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Reorder a singly‑linked list so that elements alternate between the front and back halves.  
Input: ListNode* head – pointer to the first node of the list (may be nullptr).  
Output: void – the list is reordered in‑place; no return value.  
Algorithm: Perform a classic merge‑sort‑like traversal, stopping when the list is fully reordered. The helper `reorder` recursively processes the right half, then swaps the current left node with the right node, advancing the left pointer and marking the list as fully reordered when the left node reaches the right node or its successor.

---

## DATASET.json#18 — iterative

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:

    void reorderList(ListNode* head) {

        if(head == nullptr || head->next == nullptr){
            return;
        }

        // Step 1: Find Middle

        ListNode* slow = head;
        ListNode* fast = head;

        while(fast->next != nullptr && fast->next->next != nullptr){
            slow = slow->next;
            fast = fast->next->next;
        }

        // Step 2: Split List

        ListNode* second = slow->next;
        slow->next = nullptr;

        // Step 3: Reverse Second Half

        ListNode* prev = nullptr;

        while(second != nullptr){

            ListNode* next = second->next;

            second->next = prev;

            prev = second;
            second = next;
        }

        second = prev;

        // Step 4: Merge

        ListNode* first = head;

        while(second != nullptr){

            ListNode* temp1 = first->next;
            ListNode* temp2 = second->next;

            first->next = second;
            second->next = temp1;

            first = temp1;
            second = temp2;
        }
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if(head == nullptr \|\| head->next == nullptr){` | If the list is empty or has only one node, nothing to reorder. |
| 14 | `while(fast->next != nullptr && fast->next->next != nullptr){` | Find the middle of the list using the slow/fast pointer technique. |
| 18 | `slow = slow->next;` | Move slow one step forward. |
| 19 | `fast = fast->next->next;` | Move fast two steps forward. |
| 22 | `ListNode* second = slow->next;` | Split the list into two halves: first half up to slow, second half starting at slow->next. |
| 25 | `ListNode* prev = nullptr;` | Reverse the second half of the list using the iterative reverse technique. |
| 30 | `second = prev;` | Reconnect the two halves: first half's tail points to the reversed second half's head. |
| 33 | `while(second != nullptr){` | Merge the two halves back together. |
| 37 | `first->next = second;` | Connect the first half's tail to the reversed second half's head. |
| 38 | `second->next = temp1;` | Connect the reversed second half's tail to the remaining part of the first half. |
| 39 | `first = temp1;` | Move to the next node in the first half. |
| 40 | `second = temp2;` | Move to the next node in the reversed second half. |

**Explanation**

Purpose: Reorder a singly‑linked list so that the first half is placed before the second half, maintaining relative order within each half.  
Input: ListNode* head – pointer to the first node of the list (may be nullptr).  
Output: void – the list is reordered in‑place; no return value.  
Algorithm: Locate the middle of the list using slow/fast pointers, split the list at that point, reverse the second half, and merge the two halves by alternating nodes from each side. Edge cases (empty or single‑node lists) are handled by early exit.

---

## DATASET.json#19 — recursive

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* removeElements(ListNode* head, int val) {
        if (head == nullptr) return nullptr;
        head->next = removeElements(head->next, val);
        return head->val == val ? head->next : head;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (head == nullptr) return nullptr;` | If the list is empty, nothing to remove. |
| 4 | `head->next = removeElements(head->next, val);` | Recursively remove all nodes with the target value from the rest of the list. |
| 5 | `return head->val == val ? head->next : head;` | If the current node matches the target, skip it by returning the next node; otherwise keep the current node. |

**Explanation**

Purpose: Remove all nodes from a singly‑linked list whose value equals a given target.  
Input: `head` – pointer to the first ListNode of the list; `val` – integer to match against.  
Output: Pointer to the head of the modified list (or nullptr if the list became empty).  
Algorithm: If the list is empty, return nullptr. Otherwise recursively traverse the rest of the list, replacing each node whose value equals `val` with its successor. Finally, if the current node’s value equals `val`, return its successor; otherwise return the current node unchanged.

---

## DATASET.json#19 — iterative

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* removeElements(ListNode* head, int val) {
        if (head == nullptr) {
            return nullptr;
        }

        ListNode* dummy = new ListNode();
        dummy->next = head;
        ListNode* cur = head;
        ListNode* prev = dummy;

        while (cur != nullptr) {
            if (cur->val == val) {
                prev->next = cur->next;
            } else {
                prev = cur;
            }
            cur = cur->next;
        }

        return dummy->next;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (head == nullptr) {` | If the list is empty, nothing to remove. |
| 6 | `ListNode* dummy = new ListNode();` | Create a dummy node to simplify edge cases where the head needs to be removed. |
| 7 | `dummy->next = head;` | Connect the dummy to the original head. |
| 8 | `ListNode* cur = head;` | Iterate through the list starting from the original head. |
| 9 | `ListNode* prev = dummy;` | Track the node before the current one to facilitate deletion. |
| 11 | `if (cur->val == val) {` | If the current node's value matches the target value, skip it. |
| 12 | `prev->next = cur->next;` | Update the next pointer of the previous node to skip the current node. |
| 14 | `prev = cur;` | Move the previous pointer forward to the current node. |
| 15 | `cur = cur->next;` | Move the current pointer forward to the next node. |
| 17 | `return dummy->next;` | Return the new head of the list after removing all occurrences of val. |

**Explanation**

Purpose: Remove all nodes from a singly‑linked list whose value equals a given target.  
Input: `head` – pointer to the first ListNode of the list; `val` – integer to match against.  
Output: Pointer to the head of the modified list (or nullptr if the list became empty).  
Algorithm: Create a dummy node to simplify edge‑case handling, then traverse the list with two pointers (`cur` and `prev`). When `cur` matches `val`, skip it by updating `prev->next` to `cur->next`; otherwise, advance `prev` and `cur`. Finally, return the dummy’s next pointer.

---

## DATASET.json#20 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        if(head == NULL || head->next == NULL) return head;
        ListNode* prev = NULL;
        ListNode* h2 = reverseList(head->next);
        head->next->next = head;
        head->next = prev;
        return h2;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(head == NULL \|\| head->next == NULL) return head;` | Base case: if the list is empty or has only one node, it is already reversed. |
| 4 | `ListNode* prev = NULL;` | Initialize the previous node to null. |
| 5 | `ListNode* h2 = reverseList(head->next);` | Recursively reverse the rest of the list starting from the second node. |
| 6 | `head->next->next = head;` | Connect the current node to the reversed part. |
| 7 | `head->next = prev;` | Reverse the direction of the link between the current node and the previous node. |
| 8 | `return h2;` | Return the new head of the reversed list. |

**Explanation**

Purpose: Reverses a singly‑linked list in place.  
Input: ListNode* head – pointer to the first node of the list (may be nullptr).  
Output: ListNode* – pointer to the new head of the reversed list.  
Algorithm: Recursively reverse the rest of the list, then attach the current node as the new tail. The recursion stops when the original head becomes null or the next node is null, yielding the reversed list.

---

## DATASET.json#20 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    ListNode* reverseList(ListNode* head) {

        ListNode* prev = NULL;
        ListNode* curr = head;

        while(curr != NULL){
            ListNode* forward = curr->next;
            curr->next = prev;
            prev = curr;
            curr = forward;
            
        }
        return prev;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while(curr != NULL){` | Iterate through the list, reversing each node's next pointer. |
| 11 | `ListNode* forward = curr->next;` | Store the next node before overwriting the current node's next pointer. |
| 12 | `curr->next = prev;` | Reverse the link: the current node's next points to the previous node. |
| 13 | `prev = curr;` | Advance the previous pointer to the current node. |
| 14 | `curr = forward;` | Move to the next node in the original list. |
| 16 | `return prev;` | Return the new head of the reversed list. |

**Explanation**

Purpose: Reverses a singly‑linked list in place.  
Input: ListNode* head – pointer to the first node of the list (may be nullptr).  
Output: ListNode* – pointer to the new head of the reversed list (nullptr if original was empty).  
Algorithm: Iterate through the list, maintaining three pointers: prev (previous node), curr (current node), and forward (next node). For each node, temporarily store the next pointer, reverse the link to point to prev, advance prev to curr, and finally advance curr to forward. The loop ends when curr becomes nullptr, yielding the reversed list.

---

## DATASET.json#21 — recursive

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    int solve(string &s, int &i) {
        long long result = 0;
        long long num = 0;
        int sign = 1;

        while (i < s.size()) {

            if (isdigit(s[i])) {
                num = num * 10 + (s[i] - '0');
            }

            else if (s[i] == '+') {
                result += sign * num;
                num = 0;
                sign = 1;
            }

            else if (s[i] == '-') {
                result += sign * num;
                num = 0;
                sign = -1;
            }

            else if (s[i] == '(') {
                i++;
                num = solve(s, i);
            }

            else if (s[i] == ')') {
                result += sign * num;
                return result;
            }

            i++;
        }

        result += sign * num;
        return result;
    }

    int calculate(string s) {
        int i = 0;
        return solve(s, i);
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (i < s.size()) {` | Iterate through the string, parsing tokens and accumulating the result. |
| 11 | `if (isdigit(s[i])) {` | Digit: extend the current number. |
| 14 | `else if (s[i] == '+') {` | Operator: add the accumulated number to the result and reset for the next operand. |
| 17 | `else if (s[i] == '-') {` | Operator: add the accumulated number to the result and reset for the next operand. |
| 20 | `else if (s[i] == '(') {` | Nested expression: recurse to evaluate the inner expression and add it to the result. |
| 23 | `else if (s[i] == ')') {` | Closing parenthesis: terminate the current number and return the accumulated result. |
| 26 | `i++;` | Move to the next character. |
| 29 | `result += sign * num;` | Add the final accumulated number to the result. |
| 32 | `return solve(s, i);` | Initial call to parse the entire string. |

**Explanation**

Purpose: Evaluate a simple arithmetic expression built from digits, '+' and '-' enclosed in parentheses.  
Input: A reference to a std::string containing the expression, and an int reference tracking the current position.  
Output: An int representing the computed value of the expression.  
Algorithm: Scan the string left‑to‑right, accumulating numbers while digits are found. When an operator or '(' is encountered, the accumulated number is added to the result with the appropriate sign, and the number is reset. When a ')' is encountered, the nested expression is evaluated recursively and added to the result. The final result is returned.

---

## DATASET.json#21 — iterative

- anchors: 0 exact, 19 relocated, **0 quoting a line that is not in the file**, of 19
- containers in the code: stack

  - *container named*: Algorithm: Scan the string left‑to‑right, tracking the current number, sign, and a stack that holds the result and sign for any innermost expression.
  - *container named*: When a '(' is encountered, the current result and sign are pushed onto the stack, and the sign and result are reset for the inner expression.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
#include <stack>
using namespace std;

class Solution {
public:
    int calculate(string s) {
        stack<int> stack;
        int result = 0;
        int number = 0;
        int sign = 1;

        for(int i = 0; i < s.length(); i++){
            char c = s[i];

            if(isdigit(c)){
                number = 10 * number + (int)(c - '0');
            }
            else if(c == '+'){
                result += sign * number;
                number = 0;
                sign = 1;
            }
            else if(c == '-'){
                result += sign * number;
                number = 0;
                sign = -1;
            }
            else if(c == '('){
                //we push the result first, then sign;
                stack.push(result);
                stack.push(sign);
                //reset the sign and result for the value in the parenthesis
                sign = 1;
                result = 0;
            }
            else if(c == ')'){
                result += sign * number;
                number = 0;
                result *= stack.top();
                stack.pop();
                result += stack.top();
                stack.pop();
            }
        }

        if(number != 0) result += sign * number;
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `number = 10 * number + (int)(c - '0');` | accumulate digit characters into the current number |
| 12 | `result += sign * number;` | apply the previous sign to the accumulated number |
| 13 | `number = 0;` | reset for the next operand |
| 14 | `sign = 1;` | start a new operand with positive sign |
| 16 | `result += sign * number;` | close a '+' or '-' pair |
| 17 | `number = 0;` | reset for the next operand |
| 18 | `sign = -1;` | start a new operand with negative sign |
| 20 | `stack.push(result);` | push the result and sign encountered before '(' |
| 21 | `stack.push(sign);` | push the sign encountered before '(' |
| 22 | `sign = 1;` | reset sign for the value inside the parenthesis |
| 23 | `result = 0;` | reset result for the value inside the parenthesis |
| 25 | `result += sign * number;` | close a '(' |
| 26 | `number = 0;` | reset for the next operand |
| 27 | `result *= stack.top();` | apply the sign of the outer '+'/'-' |
| 28 | `stack.pop();` | discard the sign of the outer '+'/'-' |
| 29 | `result += stack.top();` | apply the sign of the inner '+'/'-' |
| 30 | `stack.pop();` | discard the sign of the inner '+'/'-' |
| 32 | `if(number != 0) result += sign * number;` | handle trailing operand |
| 33 | `return result;` | final result |

**Explanation**

Purpose: Evaluate a simple arithmetic expression with nested parentheses and optional sign changes.  
Input: A std::string s containing digits, '+', '-', '(', ')', and ' '.  
Output: An int representing the computed value of the expression.  
Algorithm: Scan the string left‑to‑right, tracking the current number, sign, and a stack that holds the result and sign for any innermost expression. When a '(' is encountered, the current result and sign are pushed onto the stack, and the sign and result are reset for the inner expression. When a ')' is encountered, the inner result is popped, multiplied by the outer sign, added to the outer result, and the outer sign and result are popped from the stack. Finally, any trailing number is added.

---

## DATASET.json#22 — recursive

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

class Solution {
public:
    int solve(string &s, int &i) {
        long long result = 0;
        long long num = 0;
        int sign = 1;
        while (i < s.size()) {
            if (isdigit(s[i])) num = num * 10 + (s[i] - '0');
            else if (s[i] == '+') { result += sign * num; num = 0; sign = 1; }
            else if (s[i] == '-') { result += sign * num; num = 0; sign = -1; }
            else if (s[i] == '(') { i++; num = solve(s, i); }
            else if (s[i] == ')') { result += sign * num; return result; }
            i++;
        }
        result += sign * num;
        return result;
    }
    int calculate(string s) { int i = 0; return solve(s, i); }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (i < s.size()) {` | Iterate through the input string character by character. |
| 11 | `if (isdigit(s[i])) num = num * 10 + (s[i] - '0');` | Build the current operand by accumulating digits. |
| 12 | `else if (s[i] == '+') { result += sign * num; num = 0; sign = 1; }` | Encounter a '+' sign: add the accumulated operand to the result. |
| 13 | `else if (s[i] == '-') { result += sign * num; num = 0; sign = -1; }` | Encounter a '-' sign: subtract the accumulated operand from the result. |
| 14 | `else if (s[i] == '(') { i++; num = solve(s, i); }` | Encounter an '(' sign: recursively evaluate the sub‑expression. |
| 15 | `else if (s[i] == ')') { result += sign * num; return result; }` | Encounter a ')' sign: terminate the current sub‑expression and return its value. |
| 16 | `i++;` | Move to the next character. |
| 17 | `}` | If the loop finishes without a matching ')', the remaining operand is added. |
| 18 | `result += sign * num;` | Add the final operand to the result. |
| 19 | `return result;` | Return the final computed value. |

**Explanation**

Purpose: Evaluate a simple arithmetic expression built from digits, operators, and parentheses.  
Input: A reference to a std::string containing the expression, and an int reference tracking the current position.  
Output: An int representing the final result of the parsed expression.  
Algorithm: Scan the string left‑to‑right, accumulating numbers while encountering digits. When an operator or '(' is encountered, recursively evaluate the enclosed sub‑expression and add it to the running total. When a ')' is encountered, terminate recursion and return the accumulated result. The loop ends when the end of the string is reached.

---

## DATASET.json#22 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

class Solution {
public:
    bool isPowerOfTwo(int n) {
        if (n <= 0) return false;
        while (n % 2 == 0) n = n / 2;
        return n == 1;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n <= 0) return false;` | Return false immediately for non‑positive inputs; they cannot be powers of two. |
| 4 | `while (n % 2 == 0) n = n / 2;` | Repeatedly divide by 2 while the number remains even. This isolates the highest set bit. |
| 5 | `return n == 1;` | After the loop, n is 1 only if the original n was a power of two; otherwise it is a multiple of 2. |

**Explanation**

Purpose: Determines whether an integer is a power of two.  
Input: An `int n` representing the number to test.  
Output: `bool` – `true` if `n` is a power of two, otherwise `false`.  
Algorithm: Reject non‑positive inputs immediately. Repeatedly divide `n` by two while it is even, stopping when `n` becomes odd. Finally, return `true` only if `n` is reduced to one.

---

## DATASET.json#23 — recursive

- anchors: 0 exact, 0 relocated, **10 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <cmath>
using namespace std;
class Solution { public: int countDigitOne(int n) { if(n==0) return 0; else if(n<=9) return 1; int len=log10(n)+1; int base=pow(10,len-1); int mult=n/base; int rem=n%base; int noOfOnesInBase=0; if(mult==1) noOfOnesInBase=n-base+1; else noOfOnesInBase=base; return countDigitOne(base-1)*mult + noOfOnesInBase + countDigitOne(rem); } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(n==0) return 0;` | Base case: zero has exactly one digit '1'. |
| 4 | `else if(n<=9) return 1;` | Single‑digit numbers: they all contain exactly one '1'. |
| 5 | `int len=log10(n)+1;` | Determine the number of decimal digits in n. |
| 6 | `int base=pow(10,len-1);` | Compute the highest power of 10 that fits into n. |
| 7 | `int mult=n/base;` | Number of complete full‑digit blocks in n. |
| 8 | `int rem=n%base;` | Remaining part after removing the full‑digit blocks. |
| 9 | `int noOfOnesInBase=0;` | Count '1's in the current block. |
| 10 | `if(mult==1) noOfOnesInBase=n-base+1;` | If the block consists of only one digit, the count is n‑base+1. |
| 11 | `else noOfOnesInBase=base;` | Otherwise the block contributes base ones. |
| 12 | `return countDigitOne(base-1)*mult + noOfOnesInBase + countDigitOne(rem);` | Recursively count '1's in the remaining part and add the contribution of the current block. |

**Explanation**

Purpose: Count how many times the digit 1 appears in all numbers from 1 to n.  
Input: int n – the inclusive upper bound of the range.  
Output: int – total count of digit 1 appearances in the range [1, n].  
Algorithm: Recursively decompose n into its most‑significant digit (base) and its remainder (rem). For each recursive call, compute the number of digit 1 appearances in the base‑10 representation of the remaining part (rem). The recursion builds the answer from the contribution of the current base, the number of full‑base repetitions, and the contribution of the remainder. The base case handles n = 0 and n ≤ 9.

---

## DATASET.json#23 — iterative

- anchors: 0 exact, 0 relocated, **10 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <cmath>
using namespace std;
class Solution { public: int countDigitOne(int n) { int p=0,ans=0,prev=1; int num=n%10; if(num>=1) ans++; n=n/10; while(n!=0) { int x=n%10,y=pow(10,prev-1); n=n/10; if(x>1) ans+=y*(x*prev+10); if(x==1) ans+=x*prev*y+num+1; num=x*y*10+num; prev++; } return ans; } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `n=n/10;` | remove the processed digit |
| 11 | `while(n!=0) {` | iterate over remaining digits |
| 12 | `int x=n%10,y=pow(10,prev-1);` | current digit and its positional weight |
| 13 | `n=n/10;` | shift to next digit |
| 14 | `if(x>1) ans+=y*(x*prev+10);` | if current digit is 2 or greater, add all numbers with this digit at the current position |
| 15 | `if(x==1) ans+=x*prev*y+num+1;` | if current digit is 1, add numbers with this digit at the current position and the ones that can be extended by the remaining digits |
| 16 | `num=x*y*10+num;` | update the number formed so far |
| 17 | `prev++;` | move to the next positional weight |
| 18 | `}` | end of digit processing |
| 19 | `return ans;` | total count of numbers with exactly one '1' |

**Explanation**

Purpose: Count how many times the digit 1 appears in all numbers from 1 to n.  
Input: int n – the upper bound (inclusive) of the range.  
Output: int – total count of digit 1 in the range [1, n].  
Algorithm: Iterate through each decimal digit of n, accumulating the count of 1s based on the current digit and the number of higher‑order digits. The loop uses a helper variable to track the current power of ten, which is updated after each digit is processed.

---

## DATASET.json#24 — recursive

- anchors: 0 exact, 0 relocated, **7 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;
class Solution { ListNode* ref; public: bool isPalindrome(ListNode* head) { ref=head; return check(head); } bool check(ListNode* node) { if(node==nullptr) return true; bool ans=check(node->next); bool isEqual=(ref->val==node->val); ref=ref->next; return ans&&isEqual; } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `ref=head;` | store the original head so we can compare node values later |
| 4 | `return check(head);` | delegate to the recursive helper; the original head is passed as the start of the list |
| 7 | `if(node==nullptr) return true;` | base case: an empty list is trivially a palindrome |
| 8 | `bool ans=check(node->next);` | recursively verify the rest of the list |
| 9 | `bool isEqual=(ref->val==node->val);` | compare the current node's value with the stored reference |
| 10 | `ref=ref->next;` | advance the reference pointer to the next node |
| 11 | `return ans&&isEqual;` | return the combined result of the recursive check and the value comparison |

**Explanation**

Purpose: Determines whether a singly‑linked list reads the same forward and backward.  
Input: `ListNode* head` – pointer to the first node of the list.  
Output: `bool` – `true` if the list is a palindrome, `false` otherwise.  
Algorithm: The list is traversed recursively; each node’s value is compared to the stored reference node’s value. The recursion stops when the current node is null, and the final result is the logical AND of the recursive result and the equality check. The reference node is updated after each recursive call.

---

## DATASET.json#24 — iterative

- anchors: 0 exact, 0 relocated, **9 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;
class Solution { public: bool isPalindrome(ListNode* head) { vector<int> listVals; while(head) { listVals.push_back(head->val); head=head->next; } int left=0,right=listVals.size()-1; while(left<right&&listVals[left]==listVals[right]) { left++; right--; } return left>=right; } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `vector<int> listVals;` | Collect all node values into a vector so we can easily compare the front and back elements. |
| 4 | `while(head) {` | Traverse the list, appending each node's value to the vector. |
| 5 | `listVals.push_back(head->val);` | Note: if the list is empty, this loop body is skipped, leaving listVals empty. |
| 6 | `head=head->next;` | Move to the next node. |
| 8 | `int left=0,right=listVals.size()-1;` | Initialize two indices: left at the start and right at the end of the vector. |
| 9 | `while(left<right&&listVals[left]==listVals[right]) {` | Compare the values at the two indices; if they match, move inward. |
| 10 | `left++; right--;` | Advance left and decrement right to examine the next pair. |
| 11 | `}` | If any pair differs, the list is not a palindrome. |
| 12 | `return left>=right;` | Return true only when all pairs matched. |

**Explanation**

Purpose: Determines whether a singly‑linked list reads the same forward and backward.  
Input: ListNode* head – pointer to the first node of the list (may be nullptr).  
Output: bool – true if the list is a palindrome, false otherwise.  
Algorithm: Traverse the list, storing each node’s value in a vector. Then use two indices to compare mirrored positions from both ends; the list is a palindrome when the indices meet or cross.

---

## DATASET.json#25 — recursive

- anchors: 0 exact, 0 relocated, **10 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;
class Solution { public: int perform(int x,int y,char op) { if(op=='+') return x+y; if(op=='-') return x-y; if(op=='*') return x*y; return 0; } vector<int> diffWaysToCompute(string exp) { vector<int> results; bool isNumber=1; for(int i=0;i<exp.length();i++) { if(!isdigit(exp[i])) { isNumber=0; vector<int> left=diffWaysToCompute(exp.substr(0,i)); vector<int> right=diffWaysToCompute(exp.substr(i+1)); for(int x:left) for(int y:right) results.push_back(perform(x,y,exp[i])); } } if(isNumber==1) results.push_back(stoi(exp)); return results; } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if(op=='+') return x+y;` | Handle addition case |
| 11 | `if(op=='-') return x-y;` | Handle subtraction case |
| 12 | `if(op=='*') return x*y;` | Handle multiplication case |
| 13 | `return 0;` | Invalid operator – should never happen |
| 18 | `if(!isdigit(exp[i])) { isNumber=0; vector<int> left=diffWaysToCompute(exp.substr(0,i)); vector<int> right=diffWaysToCompute(exp.substr(i+1)); for(int x:left) for(int y:right) results.push_back(perform(x,y,exp[i])); } }` | If current character is not a digit, the expression splits at this position |
| 19 | `isNumber=0;` | Mark the substring as non‑numeric |
| 20 | `vector<int> left=diffWaysToCompute(exp.substr(0,i));` | Recursively compute results for the left part |
| 21 | `vector<int> right=diffWaysToCompute(exp.substr(i+1));` | Recursively compute results for the right part |
| 22 | `for(int x:left) for(int y:right) results.push_back(perform(x,y,exp[i]));` | Combine every possible pair of results with the operator |
| 24 | `if(isNumber==1) results.push_back(stoi(exp));` | If the whole string consists solely of digits, convert it to an integer |

**Explanation**

Purpose: Compute all possible integer results of arithmetic expressions built from the input string using +, -, and *.  
Input: A std::string exp containing only digits and the operators ‘+’, ‘-’, and ‘*’.  
Output: A std::vector<int> containing every distinct integer that can be formed by parsing exp as a sequence of numbers and operators.  
Algorithm: The function recursively splits the string at each operator, recursively solving the sub‑expressions, and for each pair of sub‑results it applies the operator to obtain all possible results. The recursion stops when a number is encountered, and the results are collected. The final vector is returned.

---

## DATASET.json#25 — iterative

- anchors: 0 exact, 0 relocated, **4 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;
class Solution { public: void tabular(vector<int>& nums,int n) { for(int i=0;i<n;i++) { if(nums[i]>=101) dp[i][i]={}; dp[i][i]={nums[i]}; } for(int d=1;d<n;d++) { int r; for(int l=0;l+d<n;l++) { r=l+d; vector<int> ans; for(int i=l;i<=r;i++) { if(nums[i]<100) continue; vector<int> Left=dp[l][i-1]; vector<int> Right=dp[i+1][r]; for(int L:Left) for(int R:Right) { switch(nums[i]) { case 101: ans.push_back(L+R); break; case 102: ans.push_back(L-R); break; case 103: ans.push_back(L*R); break; } } } dp[l][r]=ans; } } } vector<int> diffWaysToCompute(string& expression) { vector<int> nums=convert(expression); const int n=nums.size(); tabular(nums,n); return dp[0][n-1]; } };
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `dp[i][i]={};` | Handle the trivial case: a single element that is not 101. |
| 11 | `dp[i][i]={nums[i]};` | Handle the trivial case: a single element that is 101. |
| 16 | `int r; for(int l=0;l+d<n;l++) { r=l+d; vector<int> ans; for(int i=l;i<=r;i++) { if(nums[i]<100) continue; vector<int> Left=dp[l][i-1]; vector<int> Right=dp[i+1][r]; for(int L:Left) for(int R:Right) { switch(nums[i]) { case 101: ans.push_back(L+R); break; case 102: ans.push_back(L-R); break; case 103: ans.push_back(L*R); break; } } } dp[l][r]=ans; }` | Build the answer for the sub‑expression [l, r]. For each possible operator position i, compute all possible results by combining results from the left and right sub‑expressions. Skip operands that are not 101; otherwise, apply the operator to the left and right results and store the result in dp[l][r]. |
| 20 | `vector<int> nums=convert(expression); const int n=nums.size(); tabular(nums,n); return dp[0][n-1];` | Convert the string expression into a list of integers and compute the diffWaysToCompute for the whole expression. The dp table is built in‑place; the final result is the single element of dp[0][n‑1]. |

**Explanation**

Purpose: Compute all possible ways to evaluate an arithmetic expression containing only digits and the operators ‘+’, ‘-’, ‘*’.  
Input: `string& expression` – the expression to parse.  
Output: `vector<int>` – list of all distinct integer results that can be obtained by any combination of the expression’s digits and operators.  
Algorithm: Convert the string into a numeric array, then build a DP table `dp[l][r]` that stores the set of results for the sub‑expression `nums[l..r]`. For each length `d` from 1 to `n‑1`, expand the table by combining each pair of sub‑expressions `dp[l][i]` and `dp[i+1][r]` for each `i` in `[l, r]`. Finally, return `dp[0][n‑1]` which holds all distinct results.

---

## DATASET.json#26 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    TreeNode* trimBST(TreeNode* root, int minimum, int maximum) {
        if (!root) return root;
        if (root->val > maximum) return trimBST(root->left, minimum, maximum);
        if (root->val < minimum) return trimBST(root->right, minimum, maximum);
        root->left = trimBST(root->left, minimum, maximum);
        root->right = trimBST(root->right, minimum, maximum);
        return root;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (!root) return root;` | Base case: empty subtree – nothing to trim. |
| 4 | `if (root->val > maximum) return trimBST(root->left, minimum, maximum);` | If the current node's value exceeds the upper bound, discard the whole subtree rooted at this node. |
| 5 | `if (root->val < minimum) return trimBST(root->right, minimum, maximum);` | If the current node's value is below the lower bound, discard the whole subtree rooted at this node. |
| 6 | `root->left = trimBST(root->left, minimum, maximum);` | Recursively trim the left child; the result becomes the new left child of the current node. |
| 7 | `root->right = trimBST(root->right, minimum, maximum);` | Recursively trim the right child; the result becomes the new right child of the current node. |
| 8 | `return root;` | Return the trimmed subtree rooted at the original node. |

**Explanation**

Purpose: Trims a binary search tree so that all nodes have values between `minimum` and `maximum`.
Input: `TreeNode* root` (the root of the tree), `int minimum` (inclusive lower bound), `int maximum` (inclusive upper bound).
Output: `TreeNode*` (the trimmed root of the tree).
Algorithm: Recursively traverse the tree. If the current node's value is outside the range, discard it and continue searching in the appropriate subtree. Otherwise, recursively trim both left and right subtrees and return the current node.

---

## DATASET.json#26 — iterative

> **describes this loop as recursive**

- anchors: 0 exact, 13 relocated, **0 quoting a line that is not in the file**, of 13
- containers in the code: none

  - *recursion claim*: Then, recursively prune the left subtree by moving the left child to the right if it exists, and similarly prune the right subtree by moving the right child to the left.

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    TreeNode* trimBST(TreeNode* root, int minimum, int maximum) {
        while (root && (root->val < minimum || root->val > maximum)) {
            if (root->val < minimum) root = root->right;
            else root = root->left;
        }
        if (!root) return nullptr;

        TreeNode* curr = root;
        while (curr) {
            while (curr->left && curr->left->val < minimum)
                curr->left = curr->left->right;
            curr = curr->left;
        }

        curr = root;
        while (curr) {
            while (curr->right && curr->right->val > maximum)
                curr->right = curr->right->left;
            curr = curr->right;
        }
        return root;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `TreeNode* trimBST(TreeNode* root, int minimum, int maximum) {` | Iterative in‑order traversal to locate the first node whose value is within [minimum, maximum]. The loop stops when a node falls outside the range, and the function returns the trimmed subtree rooted at that node. |
| 4 | `while (root && (root->val < minimum \|\| root->val > maximum)) {` | Skip nodes that are too small or too large. |
| 5 | `if (root->val < minimum) root = root->right;` | If the current node is smaller, move to the right child. |
| 6 | `else root = root->left;` | If the current node is larger, move to the left child. |
| 8 | `if (!root) return nullptr;` | If the loop finishes without finding a suitable node, the original tree is empty. |
| 10 | `TreeNode* curr = root;` | Recurse left to remove all nodes smaller than minimum. |
| 11 | `while (curr->left && curr->left->val < minimum)` | Traverse left subtree until a node >= minimum is found. |
| 12 | `curr->left = curr->left->right;` | Remove the node by redirecting its left child to its right child. |
| 14 | `curr = curr->left;` | Move to the left child of the current node. |
| 17 | `curr = root;` | Recurse right to remove all nodes larger than maximum. |
| 18 | `while (curr->right && curr->right->val > maximum)` | Traverse right subtree until a node <= maximum is found. |
| 19 | `curr->right = curr->right->left;` | Remove the node by redirecting its right child to its left child. |
| 21 | `return root;` | Return the trimmed subtree rooted at the original root. |

**Explanation**

Purpose: Trims a binary search tree so that all nodes have values between minimum and maximum.  
Input: TreeNode* root – pointer to the tree’s root; int minimum, int maximum – inclusive bounds for the trimmed range.  
Output: TreeNode* – pointer to the trimmed root (or nullptr if the tree is empty).  
Algorithm: First, walk the tree to locate the first node whose value lies outside the range. Then, recursively prune the left subtree by moving the left child to the right if it exists, and similarly prune the right subtree by moving the right child to the left. Finally, return the trimmed root.

---

## DATASET.json#27 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> postorderTraversal(TreeNode* root) {
        vector<int> result;
        if (!root) return result;
        vector<int> left = postorderTraversal(root->left);
        vector<int> right = postorderTraversal(root->right);
        result.insert(result.end(), left.begin(), left.end());
        result.insert(result.end(), right.begin(), right.end());
        result.push_back(root->val);
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `vector<int> result;` | Initialize result vector to store the postorder traversal sequence |
| 4 | `if (!root) return result;` | If the current node is null, return an empty result |
| 5 | `vector<int> left = postorderTraversal(root->left);` | Recursively traverse the left subtree and store its elements in 'left' |
| 6 | `vector<int> right = postorderTraversal(root->right);` | Recursively traverse the right subtree and store its elements in 'right' |
| 7 | `result.insert(result.end(), left.begin(), left.end());` | Insert elements from 'left' into 'result' in reverse order (right subtree first) |
| 8 | `result.insert(result.end(), right.begin(), right.end());` | Insert elements from 'right' into 'result' in reverse order (left subtree first) |
| 9 | `result.push_back(root->val);` | Append the value of the current node to 'result' |
| 10 | `return result;` | Return the fully populated postorder traversal sequence |

**Explanation**

Purpose: To perform a postorder traversal on a binary tree and return the values in a vector.
Input: A pointer to the root node of the binary tree.
Output: A vector containing the values of the nodes in postorder traversal order.
Algorithm: Recursively traverse the left subtree, then the right subtree, and finally append the current node's value to the result vector.

---

## DATASET.json#27 — iterative

- anchors: 0 exact, 14 relocated, **1 quoting a line that is not in the file**, of 15
- containers in the code: stack

  - *container named*: start with the root tracks the last node processed current node being examined empty tree yields empty result push the root so we can start the traversal process nodes in postorder peek at the top of the stack if we are at a node that has not been processed yet push left child if it exists push right child if it exists if we are at the left child of the previous node if a right child exists, push it current node is the next postorder element remove the processed node from the stack update the previous node Purpose: To perform a postorder traversal of a binary tree.
  - *container named*: Algorithm: Uses a stack to simulate the postorder traversal process.

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> postorderTraversal(TreeNode* root) {
        vector<int> result;
        stack<TreeNode*> st;
        TreeNode* prev = nullptr;
        TreeNode* curr = root;
        if (!root) return result;
        st.push(root);
        while (!st.empty()) {
            curr = st.top();
            if (!prev || prev->left == curr || prev->right == curr) {
                if (curr->left) st.push(curr->left);
                else if (curr->right) st.push(curr->right);
            } else if (curr->left == prev) {
                if (curr->right) st.push(curr->right);
            } else {
                result.push_back(curr->val);
                st.pop();
            }
            prev = curr;
        }
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `st.push(root);` | start with the root |
| 11 | `TreeNode* prev = nullptr;` | tracks the last node processed |
| 12 | `TreeNode* curr = root;` | current node being examined |
| 13 | `if (!root) return result;` | empty tree yields empty result |
| 15 | `st.push(root);` | push the root so we can start the traversal |
| 16 | `while (!st.empty()) {` | process nodes in postorder |
| 17 | `curr = st.top();` | peek at the top of the stack |
| 18 | `if (!prev \|\| prev->left == curr \|\| prev->right == curr) {` | if we are at a node that has not been processed yet |
| 19 | `if (curr->left) st.push(curr->left);` | push left child if it exists |
| 20 | `else if (curr->right) st.push(curr->right);` | push right child if it exists |
| 22 | `else if (curr->left == prev) {` | if we are at the left child of the previous node |
| 23 | `if (curr->right) st.push(curr->right);` | if a right child exists, push it |
| 25 | `result.push_back(curr->val);` | current node is the next postorder element |
| 26 | `st.pop();` | remove the processed node from the stack |
| 27 | `prev = curr;` | update the previous node |

**Explanation**

Purpose: To perform a postorder traversal of a binary tree.
Input: TreeNode* root - Pointer to the root of the binary tree.
Output: vector<int> - A vector containing the values of the nodes in postorder traversal order.
Algorithm: Uses a stack to simulate the postorder traversal process. It keeps track of the previous node to determine when to visit a node.

---

## DATASET.json#28 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> postorderTraversal(TreeNode* root) {
        vector<int> result;
        if (!root) return result;
        vector<int> left = postorderTraversal(root->left);
        vector<int> right = postorderTraversal(root->right);
        result.insert(result.end(), left.begin(), left.end());
        result.insert(result.end(), right.begin(), right.end());
        result.push_back(root->val);
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `vector<int> result;` | Initialize result vector to store the postorder traversal sequence |
| 4 | `if (!root) return result;` | If the current node is null, return an empty result |
| 5 | `vector<int> left = postorderTraversal(root->left);` | Recursively traverse the left subtree and store its elements in 'left' |
| 6 | `vector<int> right = postorderTraversal(root->right);` | Recursively traverse the right subtree and store its elements in 'right' |
| 7 | `result.insert(result.end(), left.begin(), left.end());` | Insert elements from 'left' into 'result' in reverse order (right subtree first) |
| 8 | `result.insert(result.end(), right.begin(), right.end());` | Insert elements from 'right' into 'result' in reverse order (left subtree first) |
| 9 | `result.push_back(root->val);` | Append the value of the current node to 'result' |
| 10 | `return result;` | Return the fully populated postorder traversal sequence |

**Explanation**

Purpose: To perform a postorder traversal on a binary tree and return the values in a vector.
Input: A pointer to the root node of the binary tree.
Output: A vector containing the values of the nodes in postorder traversal order.
Algorithm: Recursively traverse the left subtree, then the right subtree, and finally append the current node's value to the result vector.

---

## DATASET.json#28 — iterative

- anchors: 0 exact, 14 relocated, **1 quoting a line that is not in the file**, of 15
- containers in the code: stack

  - *container named*: start with the root tracks the last node processed current node being examined empty tree yields empty result push the root so we can start the traversal process nodes in postorder peek at the top of the stack if we are at a node that has not been processed yet push left child if it exists push right child if it exists if we are at the left child of the previous node if a right child exists, push it current node is the next postorder element remove the processed node from the stack update the previous node Purpose: To perform a postorder traversal of a binary tree.
  - *container named*: Algorithm: Uses a stack to simulate the postorder traversal process.

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> postorderTraversal(TreeNode* root) {
        vector<int> result;
        stack<TreeNode*> st;
        TreeNode* prev = nullptr;
        TreeNode* curr = root;
        if (!root) return result;
        st.push(root);
        while (!st.empty()) {
            curr = st.top();
            if (!prev || prev->left == curr || prev->right == curr) {
                if (curr->left) st.push(curr->left);
                else if (curr->right) st.push(curr->right);
            } else if (curr->left == prev) {
                if (curr->right) st.push(curr->right);
            } else {
                result.push_back(curr->val);
                st.pop();
            }
            prev = curr;
        }
        return result;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `st.push(root);` | start with the root |
| 11 | `TreeNode* prev = nullptr;` | tracks the last node processed |
| 12 | `TreeNode* curr = root;` | current node being examined |
| 13 | `if (!root) return result;` | empty tree yields empty result |
| 15 | `st.push(root);` | push the root so we can start the traversal |
| 16 | `while (!st.empty()) {` | process nodes in postorder |
| 17 | `curr = st.top();` | peek at the top of the stack |
| 18 | `if (!prev \|\| prev->left == curr \|\| prev->right == curr) {` | if we are at a node that has not been processed yet |
| 19 | `if (curr->left) st.push(curr->left);` | push left child if it exists |
| 20 | `else if (curr->right) st.push(curr->right);` | push right child if it exists |
| 22 | `else if (curr->left == prev) {` | if we are at the left child of the previous node |
| 23 | `if (curr->right) st.push(curr->right);` | if a right child exists, push it |
| 25 | `result.push_back(curr->val);` | current node is the next postorder element |
| 26 | `st.pop();` | remove the processed node from the stack |
| 27 | `prev = curr;` | update the previous node |

**Explanation**

Purpose: To perform a postorder traversal of a binary tree.
Input: TreeNode* root - Pointer to the root of the binary tree.
Output: vector<int> - A vector containing the values of the nodes in postorder traversal order.
Algorithm: Uses a stack to simulate the postorder traversal process. It keeps track of the previous node to determine when to visit a node.

---

## DATASET.json#29 — recursive

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int uniquePaths(int m, int n) {
        if (m == 1 || n == 1) return 1;
        return uniquePaths(m - 1, n) + uniquePaths(m, n - 1);
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (m == 1 \|\| n == 1) return 1;` | Base case: a single‑row or single‑column grid has exactly one path. |
| 4 | `return uniquePaths(m - 1, n) + uniquePaths(m, n - 1);` | Recursive case: sum of paths from the cell above and from the cell left. |

**Explanation**

Purpose: Compute the number of unique paths from the top‑left to the bottom‑right of an m×n grid moving only down or right.  
Input: two integers m and n representing the grid dimensions.  
Output: an integer indicating the count of distinct paths.  
Algorithm: Uses a classic recursive backtracking approach where the function returns 1 for a 1×1 grid, otherwise it recursively adds the results of moving one step down and one step right. The recursion naturally yields the Catalan number C(m+n‑2) for the grid size, leading to exponential time complexity.

---

## DATASET.json#29 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int uniquePaths(int m, int n) {
        if (m == 1 || n == 1) return 1;
        if (m > n) swap(m, n);
        long long temp = 1, res = 1;
        for (int i = 1; i < m; i++) temp *= i;
        for (int i = n; i < m + n - 1; i++) res *= i;
        return res / temp;
    }
};
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (m == 1 \|\| n == 1) return 1;` | If either dimension is 1, there is exactly one unique path. |
| 4 | `if (m > n) swap(m, n);` | Ensure m is the smaller dimension; swapping avoids unnecessary factorials. |
| 5 | `long long temp = 1, res = 1;` | temp accumulates m!; res accumulates (m+n-1)! to cancel out m!. |
| 6 | `for (int i = 1; i < m; i++) temp *= i;` | Compute m! using a loop. |
| 7 | `for (int i = n; i < m + n - 1; i++) res *= i;` | Compute (m+n-1)! using a loop. |
| 8 | `return res / temp;` | Divide to obtain the binomial coefficient C(m+n-2, m-1). |

**Explanation**

Purpose: Compute the number of unique paths from the top‑left to the bottom‑right of an m×n grid.  
Input: two integers m and n representing the grid dimensions.  
Output: an integer indicating the count of distinct paths.  
Algorithm: If either dimension is 1, there is exactly one path. Otherwise, the problem reduces to choosing m‑1 upward moves and n‑1 rightward moves from a total of m+n‑2 steps. The code calculates the binomial coefficient using factorials, which yields the correct result for all m,n ≥ 1.

---

## DATASET.json#30 — recursive

- anchors: 0 exact, 0 relocated, **4 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;
bool isOdd(int n){if(n==0)return false;if(n==1)return true;return isOdd(n-2);}int main(){int n=5;if(isOdd(n))cout<<n<<" is odd";else cout<<n<<" is even";return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(n==0)return false;` | Base case: zero is even |
| 4 | `if(n==1)return true;` | Base case: one is odd |
| 5 | `return isOdd(n-2);` | Recursive step: reduce by 2 each call, stopping when n reaches 0 or 1 |
| 9 | `if(isOdd(n))cout<<n<<" is odd";` | Determine parity and output accordingly |

**Explanation**

Purpose: Determines whether an integer is odd and prints the result.  
Input: An integer n (passed to the isOdd helper).  
Output: Prints “n is odd” or “n is even” to std::cout.  
Algorithm: The isOdd function uses recursion to repeatedly subtract 2 from n until it reaches 0 or 1, returning true for odd numbers and false for even. The main function calls this helper with n=5 and prints the result based on the boolean return value.

---

## DATASET.json#30 — iterative

- anchors: 0 exact, 0 relocated, **6 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;
bool isOdd(int n){while(n>1)n-=2;return n==1;}int main(){int n=5;if(isOdd(n))cout<<n<<" is odd";else cout<<n<<" is even";return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `while(n>1)n-=2;` | Reduce n by 2 repeatedly until it becomes 1 or less. This effectively counts how many odd numbers fit into n. |
| 4 | `return n==1;` | After the loop, n == 1 if n was odd; otherwise it is 0 or negative. |
| 7 | `int n=5;` | Initial value; the function will determine if it is odd. |
| 8 | `if(isOdd(n))cout<<n<<" is odd";` | Output the original value followed by a descriptive label. |
| 9 | `else cout<<n<<" is even";` | Output the original value followed by a descriptive label. |
| 10 | `return 0;` | Return success status. |

**Explanation**

Purpose: Determines whether an integer is odd and prints the result.  
Input: An integer n (passed to the function).  
Output: Prints “n is odd” or “n is even” to std::cout.  
Algorithm: The function repeatedly subtracts 2 from n while n is greater than 1, effectively halving n. After the loop, it checks if n equals 1; if so, n is odd and the function returns true, otherwise false. The main function then uses this predicate to decide which message to output.

---

## DATASET.json#31 — recursive

> **names a container the code does not use**

- anchors: 0 exact, 0 relocated, **7 quoting a line that is not in the file**, of 7
- containers in the code: none

  - *container NOT in the code*: If the k-th bit is set, it clears it; otherwise, it propagates the value up the recursion stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int turnOffKthBit(int n,int k){if(k==1)return n&~1;return turnOffKthBit(n,k-1)|0;}int main(){int n=20,k=3;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;cout<<"Turning k'th bit off\n";n=turnOffKthBit(n,k);cout<<n<<" in binary is "<<bitset<8>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(k==1)return n&~1;` | Base case: when k equals 1, the only bit to turn off is the LSB. The expression n & ~1 effectively clears that bit. |
| 4 | `return turnOffKthBit(n,k-1)\|0;` | Recursive case: decrement k and propagate the result of the recursive call. The \|0 ensures the result is non‑zero even when the recursive call returns 0. |
| 7 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Display the original number in binary. |
| 8 | `cout<<"Turning k'th bit off\n";` | Inform the user about the operation. |
| 9 | `n=turnOffKthBit(n,k);` | Call the helper to turn off the k‑th bit. |
| 10 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Display the modified number in binary. |
| 11 | `return 0;` | Return success. |

**Explanation**

Purpose: To turn off the k-th bit of an integer n.
Input: An integer n and an integer k.
Output: An integer with the k-th bit turned off.
Algorithm: Recursively checks each bit from the least significant bit to the k-th bit. If the k-th bit is set, it clears it; otherwise, it propagates the value up the recursion stack.

---

## DATASET.json#31 — iterative

- anchors: 0 exact, 0 relocated, **6 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int turnOffKthBit(int n,int k){return n&~(1<<(k-1));}int main(){int n=20,k=3;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;cout<<"Turning k'th bit off\n";n=turnOffKthBit(n,k);cout<<n<<" in binary is "<<bitset<8>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `return n&~(1<<(k-1));` | Clear the k‑th bit of n. The expression 1<<(k-1) creates a mask with a 1 at position k‑1, and the bitwise AND clears that bit. The cast to int is unnecessary because the result is already an int. |
| 6 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Display the original number in binary. |
| 7 | `cout<<"Turning k'th bit off\n";` | Inform the user that the k‑th bit is being cleared. |
| 8 | `n=turnOffKthBit(n,k);` | Apply the bit‑clearing operation. |
| 9 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Display the number after the bit has been cleared. |
| 10 | `return 0;` | Return success status. |

**Explanation**

Purpose: To turn off the k-th bit of an integer n and display the result in binary.
Input: An integer n and an integer k representing the position of the bit to be turned off.
Output: An integer with the k-th bit turned off.
Algorithm: Uses bitwise AND operation to clear the k-th bit of n.
Edge Cases: Handles cases where k is out of bounds by returning n unchanged.

---

## DATASET.json#32 — recursive

- anchors: 0 exact, 0 relocated, **4 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int positionOfRightmostSetBit(int n,int pos=1){if(n&1)return pos;return positionOfRightmostSetBit(n>>1,pos+1);}int main(){int n=20;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;cout<<"The position of the rightmost set bit is "<<positionOfRightmostSetBit(n);return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(n&1)return pos;` | Base case: if the least‑significant bit is set, return its position. |
| 4 | `return positionOfRightmostSetBit(n>>1,pos+1);` | Otherwise, shift the number right and recurse with the next position. |
| 7 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Display the original number in 8‑bit binary. |
| 8 | `cout<<"The position of the rightmost set bit is "<<positionOfRightmostSetBit(n);` | Compute and output the position of the rightmost set bit. |

**Explanation**

Purpose: Find the position of the rightmost set bit in an integer.  
Input: `int n` – the integer to examine; `int pos` – current bit position (default 1).  
Output: `int` – 1‑based index of the rightmost set bit, or 0 if none.  
Algorithm: Uses a recursive helper that checks the least‑significant bit; if it is set, returns the current position. Otherwise it shifts the number right and increments the position. The main function prints the binary representation and the computed position.

---

## DATASET.json#32 — iterative

- anchors: 0 exact, 0 relocated, **5 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int positionOfRightmostSetBit(int n){int pos=1;while(!(n&1)){n>>=1;pos++;}return pos;}int main(){int n=20;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;cout<<"The position of the rightmost set bit is "<<positionOfRightmostSetBit(n);return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int pos=1;` | start counting from the least‑significant bit |
| 4 | `while(!(n&1)){n>>=1;pos++;}` | skip leading zeros; loop stops when the first set bit is found |
| 5 | `return pos;` | returns 1‑based position of the rightmost set bit |
| 8 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | display n in 8‑bit binary |
| 9 | `cout<<"The position of the rightmost set bit is "<<positionOfRightmostSetBit(n);` | compute and output the position of the rightmost set bit |

**Explanation**

Purpose: Compute the 1‑based position of the rightmost set bit in an integer.  
Input: An integer n (typically the value whose least‑significant bit is examined).  
Output: An integer representing the position of the rightmost set bit (1‑based).  
Algorithm: Starting from the least‑significant bit, repeatedly shift right while the current bit is zero, counting shifts; the count at that point is the position of the rightmost set bit.  
Edge cases: If n is zero, the loop never executes and the function returns 0. The bitset conversion is unnecessary for the final result.

---

## DATASET.json#33 — iterative

- anchors: 0 exact, 0 relocated, **9 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;
int findMin(int x,int y){return y^((x^y)&-(x<y));}int findMax(int x,int y){return x^((x^y)&-(x<y));}int main(){int x=2,y=4;cout<<"min("<<x<<", "<<y<<") is "<<findMin(x,y)<<endl;cout<<"max("<<x<<", "<<y<<") is "<<findMax(x,y)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(x==y)return x;` | If both values are equal, the minimum is the same as the maximum. |
| 4 | `if(x<y)return x;` | Otherwise, the smaller value is the minimum. |
| 5 | `return y;` | The larger value is the minimum. |
| 9 | `if(x==y)return x;` | If both values are equal, the minimum is the same as the maximum. |
| 10 | `if(x>y)return x;` | Otherwise, the smaller value is the minimum. |
| 11 | `return y;` | The larger value is the minimum. |
| 15 | `cout<<"min("<<x<<", "<<y<<") is "<<findMin(x,y)<<endl;` | Output the minimum of x and y. |
| 16 | `cout<<"max("<<x<<", "<<y<<") is "<<findMax(x,y)<<endl;` | Output the maximum of x and y. |
| 17 | `return 0;` | Return success status. |

**Explanation**

Purpose: To determine the minimum and maximum values between two integers.
Input: Two integers `x` and `y`.
Output: Two integers representing the minimum and maximum values respectively.
Algorithm: Compare the two integers and return the smaller one as the minimum and the larger one as the maximum.
Edge Cases: Handles the case where both integers are equal by returning either one.

---

## DATASET.json#33 — iterative

- anchors: 0 exact, 0 relocated, **3 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;
int findMin(int x,int y){return y^((x^y)&-(x<y));}int findMax(int x,int y){return x^((x^y)&-(x<y));}int main(){int x=2,y=4;cout<<"min("<<x<<", "<<y<<") is "<<findMin(x,y)<<endl;cout<<"max("<<x<<", "<<y<<") is "<<findMax(x,y)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `return y^((x^y)&-(x<y));` | Compute the minimum using the XOR‑XOR trick: y ^ (x ^ y) isolates the differing bit, and the mask (x < y) ensures the result is the smaller of the two values. |
| 4 | `return x^((x^y)&-(x<y));` | Compute the maximum using the same XOR‑XOR trick: x ^ (x ^ y) isolates the differing bit, and the mask (x < y) ensures the result is the larger of the two values. |
| 6 | `cout<<"min("<<x<<", "<<y<<") is "<<findMin(x,y)<<endl;` | Output the minimum and maximum values. |

**Explanation**

Purpose: Compute the minimum and maximum of two integers using bitwise operations.  
Input: Two integers x and y.  
Output: Two integers – the minimum and maximum of the inputs.  
Algorithm: The minimum is obtained by XOR‑ing the inputs with the bitwise complement of the XOR of the inputs and the sign of the difference. The maximum is obtained similarly, but with the sign of the difference flipped.  
Edge cases: If either argument is zero, the result is the non‑zero operand. If both arguments are zero, the result is zero. The implementation assumes the inputs are non‑negative; negative inputs would cause undefined behavior.

---

## DATASET.json#34 — recursive

- anchors: 0 exact, 0 relocated, **8 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
unsigned short multiply8bit(unsigned char m,unsigned char n){if(n==0)return 0;return m+multiply8bit(m,n-1);}int multiply16bit(int m,int n){unsigned char mLow=m&0xFF,mHigh=(m>>8)&0xFF,nLow=n&0xFF,nHigh=(n>>8)&0xFF;unsigned short a=multiply8bit(mLow,nLow),b=multiply8bit(mHigh,nLow),c=multiply8bit(mLow,nHigh),d=multiply8bit(mHigh,nHigh);return a+((b+c)<<8)+(d<<16);}int main(){int m=23472,n=2600;cout<<m<<" in binary is "<<bitset<16>(m)<<endl;cout<<n<<" in binary is "<<bitset<16>(n)<<endl<<endl;cout<<"Normal multiplication m × n = "<<m*n<<endl;cout<<"Using 8–bit multiplier m × n = "<<multiply16bit(m,n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return m+multiply8bit(m,n-1);` | Recursive addition of m with itself n times; assumes n > 0 |
| 14 | `unsigned char mLow=m&0xFF,mHigh=(m>>8)&0xFF,nLow=n&0xFF,nHigh=(n>>8)&0xFF;` | Extract low/high bytes of both operands |
| 15 | `unsigned short a=multiply8bit(mLow,nLow),b=multiply8bit(mHigh,nLow),c=multiply8bit(mLow,nHigh),d=multiply8bit(mHigh,nHigh);` | Compute 8‑bit products for each 1‑byte pair |
| 16 | `return a+((b+c)<<8)+(d<<16);` | Combine the 8‑bit results into a 16‑bit product |
| 20 | `cout<<m<<" in binary is "<<bitset<16>(m)<<endl;` | Display operands in 16‑bit binary form |
| 21 | `cout<<n<<" in binary is "<<bitset<16>(n)<<endl<<endl;` | Note: the <<16 shift is unnecessary for 16‑bit multiplication |
| 22 | `cout<<"Normal multiplication m × n = "<<m*n<<endl;` | Naive 32‑bit multiplication |
| 23 | `cout<<"Using 8–bit multiplier m × n = "<<multiply16bit(m,n)<<endl;` | Call the 16‑bit multiplexer |

**Explanation**

Purpose: Compute the 16‑bit product of two 16‑bit integers using a 8‑bit recursive multiplier.  
Input: Two 16‑bit integers m and n.  
Output: An 16‑bit integer representing m·n.  
Algorithm: Split each 16‑bit operand into 8‑bit parts, multiply each pair of 8‑bit parts using a 8‑bit recursive helper, and combine the results into a 16‑bit product. The helper recursively adds the 8‑bit products, shifting higher‑order bits left to accumulate the full 16‑bit result.

---

## DATASET.json#34 — iterative

- anchors: 0 exact, 0 relocated, **8 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
unsigned short multiply8bit(unsigned char m,unsigned char n){unsigned short result=0;while(n){if(n&1)result+=m;m<<=1;n>>=1;}return result;}int multiply16bit(int m,int n){unsigned char mLow=m&0xFF,mHigh=(m>>8)&0xFF,nLow=n&0xFF,nHigh=(n>>8)&0xFF;unsigned short a=multiply8bit(mLow,nLow),b=multiply8bit(mHigh,nLow),c=multiply8bit(mLow,nHigh),d=multiply8bit(mHigh,nHigh);return a+((b+c)<<8)+(d<<16);}int main(){int m=23472,n=2600;cout<<m<<" in binary is "<<bitset<16>(m)<<endl;cout<<n<<" in binary is "<<bitset<16>(n)<<endl<<endl;cout<<"Normal multiplication m × n = "<<m*n<<endl;cout<<"Using 8–bit multiplier m × n = "<<multiply16bit(m,n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while(n){if(n&1)result+=m;m<<=1;n>>=1;}return result;` | Iteratively add the product of the current LSB of m and n to the result. The loop runs while n is non‑zero; each iteration multiplies the least‑significant bits of m and n, shifts m right to align the next bit, and shifts n right to process the next bit. |
| 14 | `unsigned char mLow=m&0xFF,mHigh=(m>>8)&0xFF,nLow=n&0xFF,nHigh=(n>>8)&0xFF;` | Extract the 8‑bit halves of m and n, preserving the original 16‑bit value. |
| 15 | `unsigned short a=multiply8bit(mLow,nLow),b=multiply8bit(mHigh,nLow),c=multiply8bit(mLow,nHigh),d=multiply8bit(mHigh,nHigh);` | Compute four 8‑bit products: a = mLow * nLow, b = mHigh * nLow, c = mLow * nHigh, d = mHigh * nHigh. The four products are combined into a 16‑bit result by shifting and adding. |
| 16 | `return a+((b+c)<<8)+(d<<16);` | Combine the four 8‑bit products into a 16‑bit result: a + (b+c)<<8 + (d<<16). This yields the 16‑bit product using 8‑bit multiplications. |
| 20 | `cout<<m<<" in binary is "<<bitset<16>(m)<<endl;` | Output the original 16‑bit numbers in binary. |
| 21 | `cout<<n<<" in binary is "<<bitset<16>(n)<<endl<<endl;` | Output the original 16‑bit numbers in binary. |
| 22 | `cout<<"Normal multiplication m × n = "<<m*n<<endl;` | Perform the 16‑bit multiplication using the 8‑bit helper. |
| 23 | `cout<<"Using 8–bit multiplier m × n = "<<multiply16bit(m,n)<<endl;` | Output the 16‑bit multiplication using the 8‑bit helper. |

**Explanation**

Purpose: Compute the 16‑bit product of two 16‑bit integers using a 8‑bit‑based 8‑bit multiplier.  
Input: Two 16‑bit integers m and n.  
Output: An 16‑bit integer representing m·n.  
Algorithm: Split each 16‑bit operand into two 8‑bit halves, multiply each 8‑bit half with the other 8‑bit half using a 8‑bit‑based 8‑bit multiplier, and combine the results into a 16‑bit product. The 8‑bit multiplier is implemented via a loop that adds the 8‑bit product to the running total when the high‑order bit of the multiplier is set.

---

## DATASET.json#35 — recursive

- anchors: 0 exact, 0 relocated, **5 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <stdio.h>
int findOddOccuring(int arr[],int n){if(n==0)return 0;return arr[n-1]^findOddOccuring(arr,n-1);}int main(){int arr[]={4,3,6,2,6,4,2,3,4,3,3};int n=sizeof(arr)/sizeof(arr[0]);printf("The odd occurring element is %d",findOddOccuring(arr,n));return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(n==0)return 0;` | Base case: when the array is empty, the only element is considered odd. |
| 4 | `return arr[n-1]^findOddOccuring(arr,n-1);` | Recursive step: XOR the current element with the result of the sub‑array excluding the last element. This exploits the property that XOR cancels out matching pairs, leaving only the odd element. |
| 7 | `int arr[]={4,3,6,2,6,4,2,3,4,3,3};` | Array containing an even number of elements; the odd element is 3. |
| 8 | `int n=sizeof(arr)/sizeof(arr[0]);` | Determine the number of elements; this is used as the recursion depth. |
| 9 | `printf("The odd occurring element is %d",findOddOccuring(arr,n));` | Print the computed odd element. |

**Explanation**

Purpose: Find the element that appears an odd number of times in an array.  
Input: `int arr[]` – the array to examine; `int n` – number of elements in `arr`.  
Output: `int` – the element with an odd count, or `0` if none exists.  
Algorithm: The function recursively XORs each element with the result of the same operation on the rest of the array. The recursion stops when only one element remains, which is the odd‑occurring element. The base case handles the empty array.

---

## DATASET.json#35 — iterative

- anchors: 0 exact, 0 relocated, **6 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <stdio.h>
int findOddOccuring(int arr[],int n){int xor=0;for(int i=0;i<n;i++)xor=xor^arr[i];return xor;}int main(){int arr[]={4,3,6,2,6,4,2,3,4,3,3};int n=sizeof(arr)/sizeof(arr[0]);printf("The odd occurring element is %d",findOddOccuring(arr,n));return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int xor=0;` | initialise accumulator with 0 (will hold XOR of all elements) |
| 4 | `for(int i=0;i<n;i++)xor=xor^arr[i];` | iterate over the array; each XOR operation cancels out matching pairs, leaving the odd element |
| 5 | `return xor;` | returns the single odd element (or 0 if all elements are even) |
| 8 | `int arr[]={4,3,6,2,6,4,2,3,4,3,3};` | array containing an even number of repetitions of each element |
| 9 | `int n=sizeof(arr)/sizeof(arr[0]);` | compute number of elements; division truncates, yielding 11 for the array above |
| 10 | `printf("The odd occurring element is %d",findOddOccuring(arr,n));` | output the result; the function assumes the array contains at least one odd element |

**Explanation**

Purpose: Find the element that appears an odd number of times in an array.  
Input: `int arr[]` – the array to examine; `int n` – number of elements in `arr`.  
Output: `int` – the value of the element occurring an odd number of times.  
Algorithm: Initialise a variable to zero, then XOR each element into it. After the loop, the result holds the odd‑occurring element. The function returns this value.  
Edge cases: If the array contains fewer than two elements, the loop never runs and the function returns 0. The main function uses a fixed, non‑standard array and computes `n` as `sizeof(arr)/sizeof(arr[0])`, which is incorrect for the array size.

---

## DATASET.json#36 — iterative

- anchors: 0 exact, 0 relocated, **8 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int swapBits(int n,int p,int q){if(((n>>p)&1)^((n>>q)&1)){n^=(1<<p);n^=(1<<q);}return n;}int main(){int n=31,p=2,q=6;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;n=swapBits(n,p,q);cout<<n<<" in binary is "<<bitset<8>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(p==q)return n;` | If the positions are identical, no swap is needed. |
| 4 | `int bp=(n>>p)&1,bq=(n>>q)&1;` | Extract the bits at positions p and q. |
| 5 | `if(bp!=bq)n^=(1<<p)\|(1<<q);` | If the bits differ, flip them using a single XOR. |
| 6 | `return n;` | Return the modified integer. |
| 10 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Output the original and final values in binary. |
| 12 | `n=swapBits(n,p,q);` | Swap bits at positions p and q. |
| 13 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Output the original and final values in binary. |
| 15 | `return 0;` | Return success. |

**Explanation**

Purpose: Swaps the bits at positions p and q in an integer n.  
Input: int n – the original integer; int p, q – 1‑based indices of the bits to swap.  
Output: int – the integer with bits p and q exchanged.  
Algorithm: Compute the bits at p and q, XOR them into the original value to toggle their positions, and return the result.  
Edge case: If p equals q, the function returns n unchanged because no swap is needed.  
Side‑effect: The function modifies n in‑place; the original value is printed before and after the swap.

---

## DATASET.json#36 — iterative

- anchors: 0 exact, 0 relocated, **5 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int swapBits(int n,int p,int q){if(((n>>p)&1)^((n>>q)&1)){n^=(1<<p);n^=(1<<q);}return n;}int main(){int n=31,p=2,q=6;cout<<n<<" in binary is "<<bitset<8>(n)<<endl;n=swapBits(n,p,q);cout<<n<<" in binary is "<<bitset<8>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(((n>>p)&1)^((n>>q)&1)){n^=(1<<p);n^=(1<<q);}return n;` | If the bits at positions p and q differ, flip them; otherwise leave n unchanged. This effectively toggles the bits at p and q. |
| 10 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Output the original number in binary. |
| 11 | `n=swapBits(n,p,q);` | Swap bits at positions p and q. |
| 12 | `cout<<n<<" in binary is "<<bitset<8>(n)<<endl;` | Output the modified number in binary. |
| 13 | `return 0;` | Return success. |

**Explanation**

Purpose: Swaps the bits at positions p and q in an integer n.  
Input: int n – the original integer; int p, q – 1‑based indices of the bits to swap.  
Output: int – the resulting integer after swapping the specified bits.  
Algorithm: Extract the bits at p and q, XOR them to toggle them, then OR the result back into n. The function assumes p and q are within the valid range for an 8‑bit integer.

---

## DATASET.json#37 — recursive

- anchors: 0 exact, 0 relocated, **7 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int swapAdjacentBits(int n,int pos=0){if(pos>=32)return n;int a=(n>>pos)&1,b=(n>>(pos+1))&1;if(a!=b){n^=(1<<pos);n^=(1<<(pos+1));}return swapAdjacentBits(n,pos+2);}int main(){int n=761622921;cout<<n<<" in binary is "<<bitset<32>(n)<<endl;n=swapAdjacentBits(n);cout<<"\nAfter Swapping… "<<endl;cout<<n<<" in binary is "<<bitset<32>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(pos>=32)return n;` | Base case: if the position index exceeds the total bits in an int, stop recursion. |
| 4 | `int a=(n>>pos)&1,b=(n>>(pos+1))&1;` | Extract the bits at the current and next positions. |
| 5 | `if(a!=b){n^=(1<<pos);n^=(1<<(pos+1));}` | If the bits differ, flip them using XOR to swap them. |
| 6 | `return swapAdjacentBits(n,pos+2);` | Recursively process the next two positions. |
| 10 | `cout<<n<<" in binary is "<<bitset<32>(n)<<endl;` | Original number in binary. |
| 12 | `cout<<"After Swapping… "<<endl;` | After swapping adjacent bits. |
| 13 | `cout<<n<<" in binary is "<<bitset<32>(n)<<endl;` | Swapped number in binary. |

**Explanation**

Purpose: Swap adjacent bits of an integer starting from a given position.  
Input: `int n` – the integer whose bits are to be swapped; `int pos` – optional starting position (default 0).  
Output: `int` – the integer with adjacent bits swapped.  
Algorithm: Recursively examine each pair of adjacent bits starting at `pos`. If they differ, flip them using XOR. The recursion stops when the position exceeds 31 (the highest bit index). The main function demonstrates swapping bits in the decimal number 761622921.

---

## DATASET.json#37 — iterative

- anchors: 0 exact, 0 relocated, **6 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <bitset>
using namespace std;
int swapAdjacentBits(int n){return ((n&0xAAAAAAAA)>>1)|((n&0x55555555)<<1);}int main(){int n=761622921;cout<<n<<" in binary is "<<bitset<32>(n)<<endl;n=swapAdjacentBits(n);cout<<"\nAfter Swapping… "<<endl;cout<<n<<" in binary is "<<bitset<32>(n)<<endl;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `return ((n&0xAAAAAAAA)>>1)\|((n&0x55555555)<<1);` | Swaps adjacent bits of n. The mask 0xAAAAAAAA isolates the even‑indexed bits, shifts them right by one position, and the mask 0x55555555 isolates the odd‑indexed bits, shifts them left by one position. Bitwise OR combines the two halves, effectively swapping adjacent bits. |
| 10 | `cout<<n<<" in binary is "<<bitset<32>(n)<<endl;` | Output original number in binary. |
| 11 | `n=swapAdjacentBits(n);` | Apply the swap operation. |
| 12 | `cout<<"After Swapping… "<<endl;` | Output the swapped number. |
| 13 | `cout<<n<<" in binary is "<<bitset<32>(n)<<endl;` | Output the swapped number in binary. |
| 14 | `return 0;` | Return success. |

**Explanation**

Purpose: Swaps adjacent bits of an integer and prints the results in binary.  
Input: An integer `n` to be processed.  
Output: Prints the original and swapped values in binary format.  
Algorithm: Uses a bitwise trick to isolate the bits at positions 0 and 1, shifts them to opposite positions, and ORs them back together. The original value is printed before the swap, and the swapped value is printed after the operation.

---

## DATASET.json#38 — recursive

- anchors: 0 exact, 0 relocated, **10 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;
pair<int,int> findMissingAndDuplicate(vector<int> const& arr){int n=arr.size();int result=n;function<void(int)> xorArray=[&](int i){if(i==n)return;result^=arr[i]^i;xorArray(i+1);};xorArray(0);int x=0,y=0,k=log2(result&-result);function<void(int)> splitArr=[&](int i){if(i==n)return;if(arr[i]&(1<<k))x^=arr[i];else y^=arr[i];splitArr(i+1);};splitArr(0);function<void(int)> splitRange=[&](int i){if(i>n)return;if(i&(1<<k))x^=i;else y^=i;splitRange(i+1);};splitRange(1);if(find(arr.begin(),arr.end(),x)==arr.end())return {y,x};return {x,y};}int main(){vector<int> arr={4,3,6,5,2,4};auto p=findMissingAndDuplicate(arr);cout<<"The duplicate and missing elements are "<<p.first<<" and "<<p.second;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `result^=arr[i]^i;` | xor all elements with their indices to isolate the missing and duplicate values |
| 11 | `xorArray(i+1);` | recurse to process the rest of the array |
| 16 | `x^=arr[i];` | collect elements that have the k‑th bit set in the split value |
| 17 | `y^=arr[i];` | collect elements that have the k‑th bit clear |
| 18 | `splitArr(i+1);` | continue splitting the array |
| 22 | `x^=i;` | collect elements that have the k‑th bit set in the split range |
| 23 | `y^=i;` | collect elements that have the k‑th bit clear |
| 24 | `splitRange(i+1);` | continue splitting the range |
| 28 | `if(find(arr.begin(),arr.end(),x)==arr.end())return {y,x};` | if x is not present in the array, it is the duplicate; otherwise y is the duplicate |
| 31 | `vector<int> arr={4,3,6,5,2,4};` | example input: duplicate = 4, missing = 2 |

**Explanation**

Purpose: Find the duplicate and missing numbers in an array of 1‑to‑n+1 integers.  
Input: const vector<int>& arr – a vector containing n+1 distinct integers from 1 to n+1.  
Output: pair<int,int> – the first element is the duplicate, the second is the missing.  
Algorithm: Compute the XOR of all indices and the array elements, isolating the differing bit to split the array into two groups. Each group is then XOR‑ed to isolate the duplicate and missing values. Finally, locate the missing value using the XOR of the range [1, n+1].

---

## DATASET.json#38 — iterative

- anchors: 0 exact, 0 relocated, **5 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;
pair<int,int> findMissingAndDuplicate(vector<int> const& arr){int n=arr.size(),result=n;for(int i=0;i<n;i++)result^=arr[i]^i;int x=0,y=0,k=log2(result&-result);for(int val:arr)if(val&(1<<k))x^=val;else y^=val;for(int i=1;i<=n;i++)if(i&(1<<k))x^=i;else y^=i;if(find(arr.begin(),arr.end(),x)==arr.end())return {y,x};return {x,y};}int main(){vector<int> arr={4,3,6,5,2,4};auto p=findMissingAndDuplicate(arr);cout<<"The duplicate and missing elements are "<<p.first<<" and "<<p.second;return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `int x=0,y=0,k=log2(result&-result);` | Find the least significant set bit in result. This bit will be the difference between the duplicate and the missing. |
| 11 | `for(int val:arr)if(val&(1<<k))x^=val;else y^=val;` | Separate elements into two groups based on the k‑th bit: those with the bit set belong to the duplicate group, those without belong to the missing group. |
| 12 | `for(int i=1;i<=n;i++)if(i&(1<<k))x^=i;else y^=i;` | Finally, XOR all numbers from 1 to n to isolate the missing element. |
| 13 | `if(find(arr.begin(),arr.end(),x)==arr.end())return {y,x};` | If x is not present in the array, it is the missing element; otherwise it is the duplicate. |
| 17 | `vector<int> arr={4,3,6,5,2,4};` | Example input: four numbers with a duplicate and a missing value. |

**Explanation**

Purpose: Find the single duplicate and the missing element in an array of 1..n+1 integers.  
Input: const vector<int>& arr – a vector containing n+1 integers from 1 to n+1.  
Output: pair<int,int> – the duplicate and the missing values.  
Algorithm: Compute the XOR of all indices and all elements, isolating the differing bit position k. Then iterate over the array to XOR the elements into two groups based on the k‑th bit, finally XOR the expected range 1..n+1 to isolate the duplicate and the missing. The pair with the missing element is returned.

---

## DATASET.json#39 — recursive

- anchors: 0 exact, 0 relocated, **4 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;
void generate(int n,int i=1,string s="1"){if(i>n)return;cout<<s<<' ';generate(n,i+1,s+"0");}int main(){int n=16;generate(n);return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if(i>n)return;` | Base case: stop recursion when the current length exceeds n |
| 4 | `cout<<s<<' ';` | Output the current prefix followed by a space |
| 5 | `generate(n,i+1,s+"0");` | Recurse with the next index and the current prefix extended by "0" |
| 9 | `int n=16;generate(n);return 0;` | Start generating numbers from 1 up to 16 inclusive |

**Explanation**

Purpose: Prints all binary strings of length n with leading ‘1’ followed by ‘0’ recursively.  
Input: An integer n specifying the desired string length.  
Output: Writes each generated string to standard output, each on a separate line.  
Algorithm: Uses a depth‑first recursion that appends ‘0’ to the current string and increments the index. The recursion stops when the index reaches n, at which point the accumulated string is printed. The base case ensures termination.

---

## DATASET.json#39 — iterative

- anchors: 0 exact, 0 relocated, **11 quoting a line that is not in the file**, of 11
- containers in the code: queue

  - *container named*: initialize a FIFO queue with the initial binary string "1" start with the smallest binary number counter for the number of elements to generate iterate n times, each time doubling the size of the queue duplicate the current front element by appending "0" duplicate the current front element by appending "1" output the newly added element remove the element that was just printed number of elements to generate; default 16 start the generation process success Purpose: Prints the first n binary strings of length 1, followed by a space.
  - *container named*: Algorithm: Starts with the string “1” in a FIFO queue.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
#include <queue>
using namespace std;
void generate(int n){queue<string> q;q.push("1");int i=1;while(i++<=n){q.push(q.front()+"0");q.push(q.front()+"1");cout<<q.front()<<' ';q.pop();}}int main(){int n=16;generate(n);return 0;}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `queue<string> q;` | initialize a FIFO queue with the initial binary string "1" |
| 4 | `q.push("1");` | start with the smallest binary number |
| 5 | `int i=1;` | counter for the number of elements to generate |
| 6 | `while(i++<=n){` | iterate n times, each time doubling the size of the queue |
| 7 | `q.push(q.front()+"0");` | duplicate the current front element by appending "0" |
| 8 | `q.push(q.front()+"1");` | duplicate the current front element by appending "1" |
| 9 | `cout<<q.front()<<' ';` | output the newly added element |
| 10 | `q.pop();` | remove the element that was just printed |
| 13 | `int n=16;` | number of elements to generate; default 16 |
| 14 | `generate(n);` | start the generation process |
| 15 | `return 0;` | success |

**Explanation**

Purpose: Prints the first n binary strings of length 1, followed by a space.  
Input: An integer n specifying the number of strings to output.  
Output: Writes the strings to standard output, each followed by a space.  
Algorithm: Starts with the string “1” in a FIFO queue. Repeatedly duplicates the front string by appending “0” and “1”, prints the front string, and removes it. This repeats n times, producing the required sequence.

---

## dataset.jsonl#40 — recursive

- anchors: 0 exact, 3 relocated, **1 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int getMin(const vector<int>& arr, int n)
{
    // If there is a single element, return it.
    // Else, return the minimum of the first element and the minimum of the remaining array.
    if (n == 1) {
        return arr[0];
    }
    return min(arr[n - 1], getMin(arr, n - 1));
}

int getMax(const vector<int>& arr, int n)
{
    // If there is a single element, return it.
    // Else, return the maximum of the first element and the maximum of the remaining array.
    if (n == 1) {
        return arr[0];
    }
    return max(arr[n - 1], getMax(arr, n - 1));
}

int main()
{
    vector<int> arr = {1, 423, 6, 46, 34, 23, 13, 53, 4};
    int n = arr.size();

    cout << "Minimum element of array: " << getMin(arr, n) << "\n";
    cout << "Maximum element of array: " << getMax(arr, n) << "\n";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return arr[0];` | If there is a single element, return it. |
| 11 | `return min(arr[n - 1], getMin(arr, n - 1));` | Else, return the minimum of the first element and the minimum of the remaining array. |
| 17 | `return max(arr[n - 1], getMax(arr, n - 1));` | Else, return the maximum of the first element and the maximum of the remaining array. |
| 22 | `cout << "Minimum element of array: " << getMin(arr, n) << '\n';` | Output the minimum and maximum values. |

**Explanation**

Purpose: Compute the minimum and maximum values in a vector using recursion.  
Input: const vector<int>& arr – the vector to examine; int n – number of elements to consider (typically arr.size()).  
Output: int – the minimum (or maximum) element of the selected subset.  
Algorithm: For each recursive call, if the subset size is 1, return the sole element. Otherwise, recursively obtain the minimum or maximum of the tail of the vector and combine it with the current element using std::min or std::max. The base case ensures termination.

---

## dataset.jsonl#40 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int getMin(const vector<int>& arr)
{
    int res = arr[0];
    for (int i = 1; i < arr.size(); i++)
        res = min(res, arr[i]);
    return res;
}

int getMax(const vector<int>& arr)
{
    int res = arr[0];
    for (int i = 1; i < arr.size(); i++)
        res = max(res, arr[i]);
    return res;
}

int main()
{
    vector<int> arr = {1, 423, 6, 46, 34, 23, 13, 53, 4};

    cout << "Minimum element of array: " << getMin(arr) << "\n";
    cout << "Maximum element of array: " << getMax(arr) << "\n";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cout << "Minimum element of array: " << getMin(arr) << "\n";` | Print the smallest value in the vector. |
| 11 | `cout << "Maximum element of array: " << getMax(arr) << "\n";` | Print the largest value in the vector. |
| 12 | `return 0;` | Return success status. |

**Explanation**

Purpose: Compute the smallest and largest values in a vector.  
Input: const vector<int>& arr – the collection of integers to examine.  
Output: int – the minimum value (first call) and the maximum value (second call).  
Algorithm: Initialize a result variable with the first element, then iterate from the second element to the end, updating the result with the minimum and maximum of each element. The final result is returned.  
Edge cases: If the vector is empty, the first loop will not execute, and the function will return the default‑initialized int. The second loop will also not execute, yielding the default‑initialized int.

---

## dataset.jsonl#41 — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Purpose: Reverses the order of elements in a stack using recursion.
  - *container named*: Input: A reference to a `stack<int>` containing the elements to be reversed.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
using namespace std;

void insertAtBottom(stack<int> &st, int x) {
    if (st.empty()) {
        st.push(x);
        return;
    }

    int top = st.top();
    st.pop();

    insertAtBottom(st, x);

    st.push(top);
}

void reverseStack(stack<int> &st) {
    if (st.empty()) return;

    int top = st.top();
    st.pop();

    reverseStack(st);

    insertAtBottom(st, top);
}

int main() {
    stack<int> st;
    st.push(1);
    st.push(2);
    st.push(3);
    st.push(4);

    reverseStack(st);

    while (!st.empty()) {
        cout << st.top() << " ";
        st.pop();
    }

    return 0;
}
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Reverses the order of elements in a stack using recursion.  
Input: A reference to a `stack<int>` containing the elements to be reversed.  
Output: The stack is modified in place; the function returns `void`.  
Algorithm: `reverseStack` pops the top element, recursively reverses the remaining stack, then inserts it back at the bottom. The recursion stops when the stack is empty. The `insertAtBottom` helper performs the actual reversal by recursively moving elements to the bottom of the stack.

---

## dataset.jsonl#41 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: stack

  - *container named*: swap the two stacks; the original stack now holds the reversed order initialise the stack with four elements push elements in reverse order to demonstrate reversal push elements in reverse order to demonstrate reversal push elements in reverse order to demonstrate reversal swap the two stacks; the original stack now holds the reversed order output the reversed elements Purpose: Reverses the order of elements in a stack in place.
  - *container named*: Input: A reference to a `stack<int>` containing the elements to be reversed.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
using namespace std;

void reverseStack(stack<int> &st) {
    stack<int> aux;

    while (!st.empty()) {
        aux.push(st.top());
        st.pop();
    }

    swap(st, aux);
}

int main() {
    stack<int> st;
    st.push(1);
    st.push(2);
    st.push(3);
    st.push(4);

    reverseStack(st);

    while (!st.empty()) {
        cout << st.top() << " ";
        st.pop();
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `swap(st, aux);` | swap the two stacks; the original stack now holds the reversed order |
| 14 | `st.push(1);` | initialise the stack with four elements |
| 15 | `st.push(2);` | push elements in reverse order to demonstrate reversal |
| 16 | `st.push(3);` | push elements in reverse order to demonstrate reversal |
| 17 | `st.push(4);` | push elements in reverse order to demonstrate reversal |
| 20 | `swap(st, aux);` | swap the two stacks; the original stack now holds the reversed order |
| 22 | `cout << st.top() << " ";` | output the reversed elements |

**Explanation**

Purpose: Reverses the order of elements in a stack in place.  
Input: A reference to a `stack<int>` containing the elements to be reversed.  
Output: The same stack, now with its elements in descending order.  
Algorithm: The function copies all elements from the original stack into a temporary auxiliary stack, then swaps the two stacks. The auxiliary stack holds the original elements in reverse order, so the swap moves them back into the original stack.  
Edge cases: If the stack is empty, the loop body never executes and the original stack remains unchanged. The `swap` call is safe because it swaps two references; no extra work is performed.

---

## dataset.jsonl#42 — recursive

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
// Recursive CPP program to count total number of consonants
#include <iostream>
using namespace std;

bool isConsonant(char ch)
{
    ch = toupper(ch);

    return !(ch == 'A' || ch == 'E' ||
            ch == 'I' || ch == 'O' ||
            ch == 'U') && ch >= 65 && ch <= 90;
}

int totalConsonants(string str, int n)
{
    if (n == 1)
        return isConsonant(str[0]);

    return totalConsonants(str, n - 1) +
           isConsonant(str[n-1]);
}

int main()
{
    string str = "abc de";
    cout << totalConsonants(str, str.length());
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `ch = toupper(ch);` | Convert to uppercase to match the vowel list |
| 11 | `return !(ch == 'A' \|\| ch == 'E' \|\|` | Return true if the character is a consonant |
| 12 | `ch == 'I' \|\| ch == 'O' \|\|` | Note: the list misses 'Y' and 'W' which are sometimes considered consonants |
| 13 | `ch == 'U') && ch >= 65 && ch <= 90;` | and ensure it is an uppercase letter |
| 17 | `if (n == 1)` | Base case: single character |
| 18 | `return isConsonant(str[0]);` | Return true if the character is a consonant |
| 20 | `return totalConsonants(str, n - 1) +` | Recursive case: count consonants in the rest of the string |
| 21 | `isConsonant(str[n-1]);` | Add the consonant at the current position |
| 24 | `string str = "abc de";` | Test the function with a sample string |
| 25 | `cout << totalConsonants(str, str.length());` | Output the total number of consonants |

**Explanation**

Purpose: Counts the total number of consonants in a given string.  
Input: `string str` – the string to examine; `int n` – length of the string (or the index of the last character).  
Output: `int` – total count of consonants in the substring `str[0..n-1]`.  
Algorithm: Uses a simple recursive helper that checks each character against a predefined consonant mask. The base case returns the result for the single character, otherwise it adds the result of the recursive call for the rest of the string. The main function calls this helper with the full string length.

---

## dataset.jsonl#42 — iterative

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
// Iterative CPP program to count total number of consonants
#include <iostream>
using namespace std;

bool isConsonant(char ch)
{
    ch = toupper(ch);

    return !(ch == 'A' || ch == 'E' ||
            ch == 'I' || ch == 'O' ||
            ch == 'U') && ch >= 65 && ch <= 90;
}

int totalConsonants(string str)
{
    int count = 0;
    for (int i = 0; i < str.length(); i++)
        if (isConsonant(str[i]))
            ++count;
    return count;
}

int main()
{
    string str = "abc de";
    cout << totalConsonants(str);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `ch = toupper(ch);` | convert to uppercase to match the expected consonant set |
| 12 | `return !(ch == 'A' \|\| ch == 'E' \|\|` | exclude vowels and non‑alphabetic characters |
| 13 | `ch == 'I' \|\| ch == 'O' \|\|` | exclude vowels and non‑alphabetic characters |
| 14 | `ch == 'U') && ch >= 65 && ch <= 90;` | exclude vowels and non‑alphabetic characters |
| 18 | `for (int i = 0; i < str.length(); i++)` | iterate over each character; assumes the string contains only ASCII characters |
| 19 | `if (isConsonant(str[i]))` | count only if the character is a consonant |
| 21 | `return count;` | returns the total number of consonants in the string |
| 24 | `cout << totalConsonants(str);` | output the result; assumes the string is non‑empty |

**Explanation**

Purpose: Counts the total number of consonants in a given string.  
Input: A std::string `str` containing the text to analyze.  
Output: An int representing the count of consonants in `str`.  
Algorithm: Iterates over each character, converts it to uppercase, and tests whether it is a consonant using a helper predicate. If so, increments a counter. Finally, returns the counter value.

---

## dataset.jsonl#43 — recursive

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
// C++ program to find the first uppercase letter.
#include <bits/stdc++.h>
using namespace std;

char first(string str, int i=0)
{
    if (str[i] == '\0')
        return 0;
    if (isupper(str[i]))
        return str[i];
    return first(str, i+1);
}

int main()
{
    string str = "geeksforGeeKS";
    char res = first(str);
    if (res == 0)
        cout << "No uppercase letter";
    else
        cout << res << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (str[i] == '\0')` | Base case: if the current character is the null terminator, the string is exhausted. |
| 4 | `return 0;` | Return 0 to indicate that no uppercase letter was found. |
| 5 | `if (isupper(str[i]))` | If the current character is an uppercase letter, return it immediately. |
| 6 | `return str[i];` | Return the uppercase letter. |
| 7 | `return first(str, i+1);` | Recurse to the next character. |
| 11 | `string str = "geeksforGeeKS";` | Example string to search for the first uppercase letter. |
| 12 | `char res = first(str);` | Call the recursive helper; it will stop at the first uppercase letter. |
| 13 | `if (res == 0)` | If the helper returned 0, no uppercase letter was found. |
| 14 | `cout << "No uppercase letter";` | Output the appropriate message. |
| 15 | `else` | Otherwise, output the found uppercase letter. |
| 16 | `cout << res << "\n";` | Note: the original code prints the character as a single character; the newline is missing. |
| 17 | `return 0;` | Return 0 to indicate successful execution. |

**Explanation**

Purpose: To locate the first uppercase letter in a given string.
Input: A string `str`.
Output: The first uppercase letter as a character, or `0` if none exists.
Algorithm: Recursively checks each character starting from the first index. If a character is uppercase, it is returned; otherwise, the function continues searching in the rest of the string.

---

## dataset.jsonl#43 — iterative

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
// C++ program to find the first uppercase letter using linear search
#include <bits/stdc++.h>
using namespace std;

char first(string str)
{
    for (int i = 0; i < str.length(); i++)
        if (isupper(str[i]))
            return str[i];
    return 0;
}

int main()
{
    string str = "geeksforGeeKS";
    char res = first(str);
    if (res == 0)
        cout << "No uppercase letter";
    else
        cout << res << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `for (int i = 0; i < str.length(); i++)` | Iterate over each character in the string. |
| 4 | `if (isupper(str[i]))` | Check if the current character is an uppercase letter. |
| 5 | `return str[i];` | Return the first uppercase character immediately. |
| 7 | `return 0;` | If no uppercase character is found, return 0 (undefined behavior). |
| 11 | `string str = "geeksforGeeKS";` | Example string to demonstrate the function. |
| 12 | `char res = first(str);` | Call the first function to find the first uppercase letter. |
| 13 | `if (res == 0)` | If the result is 0, no uppercase letter was found. |
| 14 | `cout << "No uppercase letter";` | Output a message indicating that no uppercase letter was found. |
| 15 | `else` | Otherwise, output the found uppercase letter. |
| 17 | `return 0;` | Return 0 to indicate successful execution. |

**Explanation**

Purpose: To locate the first uppercase letter in a given string.
Input: A single `std::string` parameter `str`.
Output: Returns the first uppercase character as a `char`, or `0` if none exists.
Algorithm: Iterates through each character of the string, checking if it is uppercase using `isupper`. Returns the first uppercase character found; otherwise, returns `0`.

---

## dataset.jsonl#44 — recursive

- anchors: 0 exact, 18 relocated, **0 quoting a line that is not in the file**, of 18
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

bool isValid(string num)
{
    if (num.size() > 1 && num[0] == '0')
        return false;
    return true;
}

int val(string a, int pos)
{
    if (pos < 0)
        return 0;
    return (a[pos] - '0');
}

string addString(string a, string b)
{
    string sum = "";
    int i = a.length() - 1;
    int j = b.length() - 1;
    int carry = 0;

    while (i >= 0 || j >= 0) {
        int t = val(a, i) + val(b, j) + carry;
        sum += (t % 10 + '0');
        carry = t / 10;
        i--;
        j--;
    }

    if (carry)
        sum += (carry + '0');

    reverse(sum.begin(), sum.end());
    return sum;
}

bool checkAddition(string a, string b, string c)
{
    if (!isValid(a) || !isValid(b))
        return false;

    string sum = addString(a, b);

    if (sum == c)
        return true;

    if (c.size() <= sum.size() || sum != c.substr(0, sum.size()))
        return false;
    else {
        return checkAddition(b, sum, c.substr(sum.size()));
    }
}

bool isAdditive(string &s)
{
    int n = s.length();

    for (int i = 1; i <= n / 2; i++) {
        for (int j = 1; j <= (n - i) / 2; j++) {
            if (checkAddition(s.substr(0, i), s.substr(i, j), s.substr(i + j)))
                return true;
        }
    }

    return false;
}

int main()
{
    string s = "235813";

    if (isAdditive(s))
        cout << "true" << endl;
    else
        cout << "false" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return false;` | If the first character is '0', the number cannot start with zero. |
| 14 | `if (pos < 0)` | If the requested position is negative, the string does not contain that character. |
| 18 | `if (pos < 0)` | If the requested position is negative, the string does not contain that character. |
| 22 | `sum += (t % 10 + '0');` | Append the least‑significant digit of the sum to the result. |
| 23 | `carry = t / 10;` | Propagate any carry to the next digit. |
| 24 | `i--;` | Move to the next digit of the first operand. |
| 25 | `j--;` | Move to the next digit of the second operand. |
| 29 | `sum += (carry + '0');` | Append the final carry digit. |
| 32 | `reverse(sum.begin(), sum.end());` | Reverse the accumulated result to obtain the correct order. |
| 35 | `if (!isValid(a) \|\| !isValid(b))` | If either operand is not a valid number, the addition cannot be performed. |
| 39 | `if (sum == c)` | If the direct addition yields the target, the string is additive. |
| 42 | `if (c.size() <= sum.size() \|\| sum != c.substr(0, sum.size()))` | If the target string is shorter than the sum or does not start with the same digits, the addition cannot be performed. |
| 45 | `return checkAddition(b, sum, c.substr(sum.size()));` | Otherwise, try the remaining part of the target string. |
| 50 | `int n = s.length();` | Iterate over all possible lengths for the first additive component. |
| 51 | `for (int j = 1; j <= (n - i) / 2; j++) {` | Iterate over all possible lengths for the second additive component. |
| 53 | `if (checkAddition(s.substr(0, i), s.substr(i, j), s.substr(i + j)))` | If the first two substrings form a valid additive pair, the string is additive. |
| 57 | `return false;` | No valid additive pair was found. |
| 61 | `string s = "235813";` | Test the function with the example string. |

**Explanation**

Purpose: Determines whether a given string can be expressed as the sum of two additive number strings.  
Input: `s` – a decimal string to test.  
Output: `true` if `s` can be written as `a + b` where `a` and `b` are additive number strings; otherwise `false`.  
Algorithm: The function `isAdditive` enumerates all possible lengths for `a` and `b` and recursively checks `checkAddition`, which uses `addString` to compute `a + b` and `checkAddition` to verify the equality. The recursion stops when a valid pair is found or when the remaining part cannot be split further.

---

## dataset.jsonl#44 — iterative

> **describes this loop as recursive**

- anchors: 5 exact, 18 relocated, **0 quoting a line that is not in the file**, of 23
- containers in the code: none

  - *recursion claim*: Recursively test the split.

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

string strAdd(string s1, string s2){
    string sum;
    int c = 0;

    for(int i = s1.size()-1, j = s2.size()-1; i >= 0 || j >= 0; i--, j--){
        int a = i >= 0 ? (s1[i] - '0') : 0;
        int b = j >= 0 ? (s2[j] - '0') : 0;
        sum = to_string((a + b + c) % 10) + sum;
        c = (a + b + c) / 10;
    }

    return c ? "1" + sum : sum;
}

bool isAdditiveNumberUtil(string &num, string f, string s){
    int i = f.size() + s.size();

    while(i < num.size()){
        if((f.size() > 1 && f[0] == '0') || (s.size() > 1 && s[0] == '0'))
            break;

        string sum = strAdd(f, s);

        if(sum == num.substr(i, num.size() - i))
            return true;

        f = s;
        s = sum;
        i += sum.size();
    }

    return false;
}

bool isAdditive(string &s) {
    int len = s.size();

    if(len < 3) return false;

    for(int i = 0; i < len; i++)
        for(int j = i + 1; j < len; j++)
            if(isAdditiveNumberUtil(s, s.substr(0, i+1), s.substr(i+1, j-i)))
                return true;

    return false;
}

int main()
{
    string s = "235813";

    if (isAdditive(s))
        cout << "true" << endl;
    else
        cout << "false" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for(int i = s1.size()-1, j = s2.size()-1; i >= 0 \|\| j >= 0; i--, j--){` | Iterate from the least‑significant digit, accumulating the sum of the two numbers. |
| 11 | `int a = i >= 0 ? (s1[i] - '0') : 0;` | Extract digit from s1 (or 0 if i is out of bounds). |
| 12 | `int b = j >= 0 ? (s2[j] - '0') : 0;` | Extract digit from s2 (or 0 if j is out of bounds). |
| 13 | `sum = to_string((a + b + c) % 10) + sum;` | Append the least‑significant digit of the sum to the result. |
| 14 | `c = (a + b + c) / 10;` | Carry for the next digit. |
| 18 | `return c ? "1" + sum : sum;` | If a carry remains, prepend "1" to the result. |
| 22 | `int i = f.size() + s.size();` | Start searching from the position after the two numbers. |
| 23 | `while(i < num.size()){` | Continue while the remaining characters can form a valid sum. |
| 24 | `if((f.size() > 1 && f[0] == '0') \|\| (s.size() > 1 && s[0] == '0'))` | Prevent leading zeros in the first two numbers. |
| 26 | `string sum = strAdd(f, s);` | Compute the sum of the current prefix. |
| 27 | `if(sum == num.substr(i, num.size() - i))` | If the sum matches the remainder of the string, we have a valid additive number. |
| 28 | `return true;` | Return early to avoid unnecessary work. |
| 31 | `f = s;` | Advance to the next candidate. |
| 32 | `s = sum;` | Update the second number. |
| 33 | `i += sum.size();` | Move the search position forward by the length of the sum. |
| 37 | `return false;` | No valid additive number was found. |
| 41 | `int len = s.size();` | Handle the trivial case where the string is too short. |
| 43 | `for(int i = 0; i < len; i++)` | Try every possible split point for the first two numbers. |
| 44 | `if(isAdditiveNumberUtil(s, s.substr(0, i+1), s.substr(i+1, j-i)))` | Recursively test the split. |
| 46 | `return true;` | Return early to avoid unnecessary work. |
| 49 | `return false;` | No additive number was found. |
| 53 | `string s = "235813";` | Test the example string. |
| 54 | `if (isAdditive(s))` | Output the result. |

**Explanation**

Purpose: Determines whether a given string can be expressed as the sum of two or more additive numbers.  
Input: A single std::string s containing the digits to test.  
Output: Returns true if s can be written as a sum of additive numbers, false otherwise.  
Algorithm: For each possible split point i, the function tries to construct a sum of the first two substrings (f and s) using strAdd. If the constructed sum matches the remainder of s, the function returns true; otherwise it backtracks. The search continues for all possible splits, returning true on the first successful match.

---

## dataset.jsonl#45 — recursive

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <cstring>
using namespace std;

void printCombinations(char* input, int index, char* output, int outLength)
{
    if (input[index] == '\0')
    {
        output[outLength] = '\0';
        cout << output << endl;
        return;
    }

    output[outLength] = input[index];
    output[outLength + 1] = ' ';

    printCombinations(input, index + 1, output, outLength + 2);

    if(input[index + 1] != '\0')
        printCombinations(input, index + 1, output, outLength + 1);
}

int main()
{
    char input[] = "1214";
    char *output = new char[100];
    output[0] = '\0';

    printCombinations(input, 0, output, 0);
    return 0;
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Generate all possible combinations of characters from the input string, separated by spaces.  
Input: `char* input` – the source string; `int index` – current position in `input`; `char* output` – buffer for the current combination; `int outLength` – length of `output` so far.  
Output: Prints each combination to `std::cout`.  
Algorithm: Recursively walk the input, appending each character to `output` and a space, then recurse to the next character. When the end of `input` is reached, terminate `output` with a null terminator and output the combination. If the next character exists, recurse again without the trailing space.

---

## dataset.jsonl#45 — iterative

- anchors: 0 exact, 14 relocated, **0 quoting a line that is not in the file**, of 14
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void printCombinations(char s[]){
    int l = strlen(s);

    for(int i = 0; i < pow(2, l - 1); i++){
        int k = i, x = 0;

        cout << s[x];
        x++;

        for(int j = 0; j < strlen(s) - 1; j++){
            if(k & 1)
                cout << " ";
            k = k >> 1;
            cout << s[x];
            x++;
        }
        cout << "\n";
    }
}

int main() {
    char input[] = "1214";
    printCombinations(input);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int l = strlen(s);` | Determine the length of the input string. |
| 5 | `for(int i = 0; i < pow(2, l - 1); i++){` | Generate all possible combinations of the string's characters. |
| 6 | `int k = i, x = 0;` | k tracks the current bit position; x indexes the current character. |
| 7 | `cout << s[x];` | Output the first character of the current combination. |
| 8 | `x++;` | Advance to the next character. |
| 10 | `for(int j = 0; j < strlen(s) - 1; j++){` | Process the remaining bits to decide whether to output a space. |
| 11 | `if(k & 1)` | If the least‑significant bit is 1, output a space. |
| 12 | `k = k >> 1;` | Shift right to examine the next bit. |
| 13 | `cout << s[x];` | Output the next character of the current combination. |
| 14 | `x++;` | Advance to the next character. |
| 16 | `cout << "\n";` | End the line after each combination. |
| 20 | `char input[] = "1214";` | Example input string; the function assumes it is non‑empty. |
| 21 | `printCombinations(input);` | Print all combinations of the input string. |
| 22 | `return 0;` | Return success. |

**Explanation**

Purpose: Prints all possible binary‑like combinations of the characters in a string.  
Input: A null‑terminated character array `s` containing the characters to combine.  
Output: Writes each combination to `stdout`, each on a separate line.  
Algorithm: For each of the 2^(|s|-1) possible bit patterns, it prints the first character of `s`, then iterates over the rest, printing a space when the current bit is set and the next character, otherwise printing the character directly. The loop repeats for all patterns.

---

## dataset.jsonl#46 — recursive

- anchors: 1 exact, 14 relocated, **0 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
#include <climits>
using namespace std;

int parseDigits(const string &s, int idx, int res, int sign) {
    if (idx >= s.size() || s[idx] < '0' || s[idx] > '9')
        return res * sign;

    int digit = s[idx] - '0';

    if (res > (INT_MAX - digit) / 10)
        return sign == 1 ? INT_MAX : INT_MIN;

    return parseDigits(s, idx + 1, res * 10 + digit, sign);
}

int myAtoi(string &s) {
    int idx = 0;

    while (idx < s.size() && s[idx] == ' ')
        idx++;

    int sign = 1;

    if (idx < s.size() && (s[idx] == '-' || s[idx] == '+')) {
        if (s[idx] == '-')
            sign = -1;
        idx++;
    }

    return parseDigits(s, idx, 0, sign);
}

int main() {
    string s = " -0012g4";
    cout << myAtoi(s) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (idx >= s.size() \|\| s[idx] < '0' \|\| s[idx] > '9')` | Base case: either we have reached the end of the string or the current character is not a digit. |
| 11 | `return res * sign;` | If the digit is out of range, clamp the result to INT_MAX or INT_MIN. |
| 14 | `int digit = s[idx] - '0';` | Convert the character digit to its numeric value. |
| 15 | `if (res > (INT_MAX - digit) / 10)` | Prevent overflow by checking the next digit before multiplying. |
| 16 | `return sign == 1 ? INT_MAX : INT_MIN;` | If the next digit would cause overflow, clamp the result. |
| 17 | `return parseDigits(s, idx + 1, res * 10 + digit, sign);` | Recurse with the next index, updating the accumulated result. |
| 21 | `int idx = 0;` | Skip leading spaces. |
| 22 | `while (idx < s.size() && s[idx] == ' ')` | Skip leading spaces. |
| 24 | `int sign = 1;` | Determine the sign based on the first non‑space character. |
| 25 | `if (idx < s.size() && (s[idx] == '-' \|\| s[idx] == '+')) {` | Determine the sign based on the first non‑space character. |
| 26 | `if (s[idx] == '-')` | Determine the sign based on the first non‑space character. |
| 27 | `sign = -1;` | Determine the sign based on the first non‑space character. |
| 28 | `idx++;` | Determine the sign based on the first non‑space character. |
| 31 | `return parseDigits(s, idx, 0, sign);` | Start parsing the number from the first non‑space character. |
| 34 | `string s = " -0012g4";` | Test the function with a string containing a leading space and a non‑digit character. |

**Explanation**

Purpose: Convert a string representation of an integer to its numeric value, handling optional sign and leading zeros.  
Input: `string &s` – the string to parse.  
Output: `int` – the parsed integer, or `INT_MAX`/`INT_MIN` if overflow occurs.  
Algorithm: Skip leading spaces, detect optional sign, then recursively parse each digit, accumulating the result while enforcing overflow checks.

---

## dataset.jsonl#46 — iterative

- anchors: 2 exact, 6 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <climits>
using namespace std;

int myAtoi(string &s) {
    int sign = 1, res = 0, idx = 0;

    while (idx < s.size() && s[idx] == ' ') {
        idx++;
    }

    if (idx < s.size() && (s[idx] == '-' || s[idx] == '+')) {
        if (s[idx++] == '-')
            sign = -1;
    }

    while (idx < s.size() && s[idx] >= '0' && s[idx] <= '9') {
        if (res > INT_MAX / 10 || (res == INT_MAX / 10 && s[idx] - '0' > 7)) {
            return sign == 1 ? INT_MAX : INT_MIN;
        }

        res = 10 * res + (s[idx++] - '0');
    }
    return res * sign;
}

int main() {
    string s = " -0012g4";
    cout << myAtoi(s);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (idx < s.size() && s[idx] == ' ') {` | Skip leading spaces; this is the first non‑whitespace position. |
| 12 | `if (idx < s.size() && (s[idx] == '-' \|\| s[idx] == '+')) {` | Determine sign: '-' means negative, '+' means positive. |
| 13 | `if (s[idx++] == '-')` | If the next character is a sign, consume it. |
| 15 | `while (idx < s.size() && s[idx] >= '0' && s[idx] <= '9') {` | Process digits; overflow detection is performed after each addition. |
| 16 | `if (res > INT_MAX / 10 \|\| (res == INT_MAX / 10 && s[idx] - '0' > 7)) {` | If adding the next digit would cause overflow, clamp to INT_MAX or INT_MIN. |
| 19 | `res = 10 * res + (s[idx++] - '0');` | Build the integer value. |
| 21 | `return res * sign;` | Return the final result, applying the sign. |
| 24 | `string s = " -0012g4";` | Test case: leading spaces, sign, and trailing garbage. |

**Explanation**

Purpose: Convert a string representation of an integer to its numeric value, handling optional sign and leading zeros.  
Input: A reference to a std::string containing the integer text.  
Output: An int representing the parsed integer, clamped to INT_MAX/INT_MIN for overflow.  
Algorithm: Skip leading spaces, detect optional sign, then iterate over the remaining characters, accumulating the numeric value while enforcing overflow checks. Finally apply the sign and return the result.

---

## dataset.jsonl#47 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void myCopy(char s1[], char s2[], int index = 0)
{
    s2[index] = s1[index];

    if (s1[index] == '\0')
        return;

    myCopy(s1, s2, index + 1);
}

int main()
{
    char s1[100] = "GEEKSFORGEEKS";
    char s2[100] = "";
    myCopy(s1, s2);
    cout << s2;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `s2[index] = s1[index];` | Copy the current character from s1 to s2 at the same position. |
| 4 | `if (s1[index] == '\0')` | If the source string ends, we have copied all characters. |
| 5 | `return;` | No further recursion needed. |
| 6 | `myCopy(s1, s2, index + 1);` | Recursively copy the next character. |
| 10 | `char s1[100] = "GEEKSFORGEEKS";` | Source string containing the characters to copy. |
| 11 | `char s2[100] = "";` | Destination string that will receive the copy. |
| 12 | `myCopy(s1, s2);` | Start the recursive copy from the first character. |
| 13 | `cout << s2;` | Output the resulting copy. |

**Explanation**

Purpose: Copies characters from the first string to the second string, stopping at the null terminator.  
Input: Two character arrays `s1` and `s2`, with `s2` initialized to an empty string. An optional `index` parameter defaults to 0.  
Output: Writes the copied characters into `s2` and returns the length of the copied segment.  
Algorithm: Recursively walks `s1` starting at `index`, copying each character to `s2` until a null terminator is encountered, then returns. The recursion depth is limited by the length of `s1`.

---

## dataset.jsonl#47 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void myCopy(char s1[], char s2[])
{
    int i = 0;
    for (i = 0; s1[i] != '\0'; i++)
        s2[i] = s1[i];
    s2[i] = '\0';
}

int main()
{
    char s1[100] = "GEEKSFORGEEKS";
    char s2[100] = "";
    myCopy(s1, s2);
    cout << s2;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 4 | `for (i = 0; s1[i] != '\0'; i++)` | Copy characters from s1 to s2 until the terminating null character is encountered. |
| 5 | `s2[i] = s1[i];` | Copy the character from s1 to s2. |
| 6 | `s2[i] = '\0';` | Terminate s2 with a null character to ensure it is a valid C string. |
| 10 | `char s1[100] = "GEEKSFORGEEKS";` | s1 is a C‑string literal; it is immutable after initialization. |
| 11 | `char s2[100] = "";` | s2 is a zero‑initialized array; it will contain the copied characters. |
| 12 | `myCopy(s1, s2);` | Copy s1 into s2; the function assumes s1 is null‑terminated. |
| 13 | `cout << s2;` | Output the copied string; s2 is a C‑string, so it is printed as a C‑string. |

**Explanation**

*none produced*

---

## dataset.jsonl#48 — recursive

- anchors: 0 exact, 15 relocated, **0 quoting a line that is not in the file**, of 15
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

struct Node
{
    int data;
    Node *left, *right;

    Node(int val)
    {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};

void printLeafNodes(Node *root)
{
    if (!root)
        return;

    if (!root->left && !root->right)
    {
        cout << root->data << " ";
        return;
    }

    if (root->left)
        printLeafNodes(root->left);

    if (root->right)
        printLeafNodes(root->right);
}

int main()
{
    Node *root = new Node(1);
    root->left = new Node(2);
    root->right = new Node(3);
    root->left->left = new Node(4);
    root->right->left = new Node(5);
    root->right->right = new Node(8);
    root->right->left->left = new Node(6);
    root->right->left->right = new Node(7);
    root->right->right->left = new Node(9);
    root->right->right->right = new Node(10);

    printLeafNodes(root);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (!root)` | Base case: empty subtree – nothing to print. |
| 13 | `if (!root->left && !root->right)` | Leaf node: output its value. |
| 16 | `if (root->left)` | Non‑leaf node: recurse into left child. |
| 17 | `if (root->right)` | Recurse into right child. |
| 20 | `Node *root = new Node(1);` | Build a simple binary tree: 1 / \   / \ 2 3 / \ / \ 4 5 6 7 8 9 10 |
| 21 | `root->left = new Node(2);` | left child |
| 22 | `root->right = new Node(3);` | right child |
| 23 | `root->left->left = new Node(4);` | left child of left child |
| 24 | `root->right->left = new Node(5);` | left child of right child |
| 25 | `root->right->right = new Node(8);` | right child of right child |
| 26 | `root->right->left->left = new Node(6);` | left child of left child of right child |
| 27 | `root->right->left->right = new Node(7);` | right child of left child of right child |
| 28 | `root->right->right->left = new Node(9);` | left child of right child of right child |
| 29 | `root->right->right->right = new Node(10);` | right child of right child of right child |
| 32 | `printLeafNodes(root);` | Output leaf node values. |

**Explanation**

Purpose: Prints all leaf nodes of a binary tree in ascending order of their data values.  
Input: A pointer to the root of a binary tree (Node*).  
Output: Writes the leaf node values to standard output separated by spaces.  
Algorithm: Perform a depth‑first traversal; when a node has no children, output its data. Recursively traverse the left and right subtrees, skipping null pointers. The traversal ensures that leaf nodes are printed in ascending order.

---

## dataset.jsonl#48 — iterative

- anchors: 0 exact, 21 relocated, **0 quoting a line that is not in the file**, of 21
- containers in the code: queue

  - *container named*: Remove the node from the queue.
  - *container named*: Algorithm: Perform a breadth‑first search using a queue, starting from the root.

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node
{
    int data;
    Node *left, *right;

    Node(int d)
    {
        data = d;
        left = right = NULL;
    }
};

void printLeafNodes(Node *root)
{
    if (!root)
        return;

    queue<Node*> q;
    q.push(root);

    while (!q.empty())
    {
        root = q.front();
        q.pop();

        if (!root->left && !root->right)
            cout << root->data << " ";

        if (root->left)
            q.push(root->left);

        if (root->right)
            q.push(root->right);
    }
}

int main()
{
    Node *root = new Node(1);
    root->left = new Node(2);
    root->right = new Node(3);
    root->left->left = new Node(4);
    root->right->left = new Node(5);
    root->right->right = new Node(8);
    root->right->left->left = new Node(6);
    root->right->left->right = new Node(7);
    root->right->right->left = new Node(9);
    root->right->right->right = new Node(10);

    printLeafNodes(root);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 11 | `if (!root)` | If the current node is null, there are no leaf nodes to print. |
| 14 | `q.push(root);` | Start BFS from the root. |
| 16 | `while (!q.empty())` | Process each level of the tree. |
| 17 | `root = q.front();` | Dequeue the front node. |
| 18 | `q.pop();` | Remove the node from the queue. |
| 19 | `if (!root->left && !root->right)` | If the current node is a leaf, output its data. |
| 22 | `if (root->left)` | If the node has a left child, enqueue it. |
| 23 | `q.push(root->left);` | Enqueue the left child. |
| 24 | `if (root->right)` | If the node has a right child, enqueue it. |
| 25 | `q.push(root->right);` | Enqueue the right child. |
| 30 | `Node *root = new Node(1);` | Build a simple binary tree for testing. |
| 31 | `root->left = new Node(2);` | 1's left child is 2. |
| 32 | `root->right = new Node(3);` | 1's right child is 3. |
| 33 | `root->left->left = new Node(4);` | 2's left child is 4. |
| 34 | `root->right->left = new Node(5);` | 3's left child is 5. |
| 35 | `root->right->right = new Node(8);` | 3's right child is 8. |
| 36 | `root->right->left->left = new Node(6);` | 8's left child is 6. |
| 37 | `root->right->left->right = new Node(7);` | 8's right child is 7. |
| 38 | `root->right->right->left = new Node(9);` | 8's right child is 9. |
| 39 | `root->right->right->right = new Node(10);` | 8's right child is 10. |
| 41 | `printLeafNodes(root);` | Output all leaf node values. |

**Explanation**

Purpose: Prints all leaf nodes of a binary tree in inorder traversal.  
Input: A pointer to the root of a binary tree (Node*).  
Output: Writes leaf node values to standard output separated by spaces.  
Algorithm: Perform a breadth‑first search using a queue, starting from the root. For each node, if it has no children, output its data; otherwise enqueue its left and right children. The loop stops when the queue is empty.

---

## dataset.jsonl#49 — recursive

- anchors: 0 exact, 24 relocated, **0 quoting a line that is not in the file**, of 24
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

void lcsLength(string &s1, string &s2, vector<vector<int>> &dp) {
    int m = s1.size(), n = s2.size();
    for (int i = m - 1; i >= 0; --i) {
        for (int j = n - 1; j >= 0; --j) {
            if (s1[i] == s2[j])
                dp[i][j] = dp[i + 1][j + 1] + 1;
            else
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1]);
        }
    }
}

void backtrack(string &s1, string &s2, int i, int j, int lcsLen,
               vector<vector<int>> &dp, string &cur, vector<string> &res) {
    if (cur.size() == lcsLen) {
        res.push_back(cur);
        return;
    }

    if (i == (int)s1.size() || j == (int)s2.size())
        return;

    int built = cur.size();

    for (char ch = 'a'; ch <= 'z'; ++ch) {
        bool found = false;

        for (int ii = i; ii < (int)s1.size(); ++ii) {
            if (s1[ii] != ch) continue;

            for (int jj = j; jj < (int)s2.size(); ++jj) {
                if (s2[jj] == ch && dp[ii][jj] == lcsLen - built) {
                    cur.push_back(ch);
                    backtrack(s1, s2, ii + 1, jj + 1, lcsLen, dp, cur, res);
                    cur.pop_back();
                    found = true;
                    break;
                }
            }

            if (found) break;
        }
    }
}

vector<string> allLCS(string &s1, string &s2) {
    int n = s1.size(), m = s2.size();
    vector<vector<int>> dp(n + 1, vector<int>(m + 1));

    lcsLength(s1, s2, dp);

    int lcsLen = dp[0][0];

    vector<string> res;
    string cur;
    backtrack(s1, s2, 0, 0, lcsLen, dp, cur, res);

    return res;
}

int main() {
    string s1 = "abac";
    string s2 = "aabca";

    vector<string> res = allLCS(s1, s2);

    cout << "[";
    for (int i = 0; i < res.size(); ++i) {
        cout << "\"" << res[i] << "\"";
        if (i + 1 < res.size()) cout << ", ";
    }
    cout << "]\n";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = m - 1; i >= 0; --i) {` | Build the LCS length table from bottom‑up; dp[i][j] stores LCS length of s1[0..i] and s2[0..j] |
| 14 | `if (s1[i] == s2[j])` | If characters match, extend the diagonal entry |
| 15 | `dp[i][j] = dp[i + 1][j + 1] + 1;` | dp[i+1][j+1] already holds the length of the diagonal LCS |
| 16 | `else` | Otherwise, the best length is the maximum of extending either direction |
| 20 | `if (cur.size() == lcsLen) {` | When the current prefix matches the required length, store it |
| 21 | `res.push_back(cur);` | Note: cur is a mutable reference; the caller must ensure it is copied or moved before reuse |
| 22 | `return;` | No further characters can extend this LCS |
| 25 | `if (i == (int)s1.size() \|\| j == (int)s2.size())` | If either string is exhausted, backtrack to the next character |
| 28 | `for (char ch = 'a'; ch <= 'z'; ++ch) {` | Try every possible character that could extend the current prefix |
| 30 | `for (int ii = i; ii < (int)s1.size(); ++ii) {` | Scan s1 for the first occurrence of ch starting at i |
| 31 | `if (s1[ii] != ch) continue;` | Skip if the character does not match |
| 32 | `for (int jj = j; jj < (int)s2.size(); ++jj) {` | Scan s2 for the first occurrence of ch starting at jj |
| 33 | `if (s2[jj] == ch && dp[ii][jj] == lcsLen - built) {` | If the character matches and the diagonal entry equals the remaining LCS length, we have a valid extension |
| 34 | `cur.push_back(ch);` | Append the character to the current prefix |
| 35 | `backtrack(s1, s2, ii + 1, jj + 1, lcsLen, dp, cur, res);` | Recurse with the extended prefix |
| 36 | `cur.pop_back();` | Backtrack to try the next character |
| 37 | `found = true;` | Mark that a valid extension was found |
| 38 | `break;` | No need to continue scanning s2 for this character |
| 40 | `if (found) break;` | No character can extend the current prefix further |
| 43 | `int n = s1.size(), m = s2.size();` | Compute LCS length using the previously built table |
| 46 | `lcsLength(s1, s2, dp);` | dp[i][j] now holds LCS length of s1[0..i] and s2[0..j] |
| 49 | `int lcsLen = dp[0][0];` | The length of the longest common subsequence |
| 52 | `string cur;` | Recurse to collect all possible LCSs of length lcsLen |
| 55 | `cout << "[";` | Output the collected LCSs |

**Explanation**

Purpose: Find all longest common subsequences (LCS) between two strings.  
Input: Two std::string objects `s1` and `s2`.  
Output: A std::vector<std::string> containing every LCS of `s1` and `s2`.  
Algorithm: Compute the LCS length using a bottom‑up DP table, then perform a depth‑first backtracking search that tries each character from `s1` and `s2` that matches the current LCS length, pruning when a mismatch is encountered. The backtracking builds candidate LCS strings incrementally and backtracks when a mismatch is found.

---

## dataset.jsonl#49 — iterative

- anchors: 1 exact, 21 relocated, **2 quoting a line that is not in the file**, of 24
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <set>
using namespace std;

bool isSubseq(string &t, string &s) {
    int i = 0, j = 0;

    while (i < t.size() && j < s.size()) {
        if (t[i] == s[j])
            ++i;
        ++j;
    }

    return i == t.size();
}

vector<string> allLCS(string &s1, string &s2) {
    int n = s1.size();
    int best = 0;
    set<string> st;

    for (int mask = 0; mask < (1 << n); ++mask) {
        string sub;

        for (int i = 0; i < n; ++i) {
            if (mask & (1 << i))
                sub.push_back(s1[i]);
        }

        int len = sub.size();

        if (len < best)
            continue;

        if (isSubseq(sub, s2)) {
            if (len > best) {
                best = len;
                st.clear();
            }
            st.insert(sub);
        }
    }

    vector<string> ans;

    for (auto i : st)
        ans.push_back(i);

    return ans;
}

int main() {
    string s1 = "abac";
    string s2 = "aabca";

    auto res = allLCS(s1, s2);

    cout << "[";
    for (int i = 0; i < res.size(); ++i) {
        cout << "\"" << res[i] << "\"";
        if (i + 1 < res.size())
            cout << ", ";
    }
    cout << "]\n";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (i < t.size() && j < s.size()) {` | Scan both strings in lock‑step; stop when either string runs out. |
| 11 | `if (t[i] == s[j])` | If characters match, advance the position in t. |
| 12 | `++i;` | t is a subsequence of s. |
| 13 | `++j;` | Move s forward. |
| 16 | `return i == t.size();` | true iff t is a subsequence of s. |
| 20 | `for (int mask = 0; mask < (1 << n); ++mask) {` | Enumerate every possible subset of s1. |
| 21 | `string sub;` | Build the candidate LCS from the selected bits. |
| 22 | `for (int i = 0; i < n; ++i) {` | Append characters from s1 that are present in the mask. |
| 23 | `if (mask & (1 << i))` | Bit mask checks if the i‑th character of s1 is included. |
| 24 | `sub.push_back(s1[i]);` | Append the character to the candidate. |
| 27 | `int len = sub.size();` | Compute length of the current candidate. |
| 28 | `if (len < best)` | Discard shorter candidates; they cannot be the longest. |
| 31 | `if (isSubseq(sub, s2)) {` | Check if the candidate is also a subsequence of s2. |
| 32 | `if (len > best) {` | Update best length and clear the set when a longer LCS is found. |
| 35 | `st.insert(sub);` | Store the LCS in a set to avoid duplicates. |
| 40 | `for (auto i : st)` | Convert the set back to a vector for the final output. |
| 41 | `ans.push_back(i);` | Append each LCS to the result vector. |
| 42 | `}` | Note: the original code does not handle the case where s1 is empty. |
| 45 | `cout << "["` | Print the list of LCS enclosed in square brackets. |
| 46 | `for (int i = 0; i < res.size(); ++i) {` | Iterate over the result vector and print each LCS. |
| 47 | `cout << "" << res[i] << '"';` | Output each LCS enclosed in double quotes. |
| 48 | `if (i + 1 < res.size())` | Add comma and space between elements except for the last one. |
| 49 | `}` | Note: the original code does not handle the case where s1 is empty. |
| 52 | `return 0;` | Return success. |

**Explanation**

Purpose: Finds all longest common subsequences (LCS) between two strings.  
Input: two std::string objects `s1` and `s2`.  
Output: a std::vector<std::string> containing every LCS of `s1` and `s2`.  
Algorithm: Enumerate every subset of `s1` using bitmasks, build each candidate LCS, and use `isSubseq` to test membership in `s2`. Keep the longest LCS found so far; if a longer one is discovered, clear the set and insert the new LCS. Finally, collect and return all LCS.

---

## dataset.jsonl#50 — recursive

- anchors: 1 exact, 25 relocated, **1 quoting a line that is not in the file**, of 27
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

void generateNumbers(int remainingDigits, int currentDigit, int currentNumber, vector<int> &result)
{
    if (remainingDigits == 0)
    {
        result.push_back(currentNumber);
        return;
    }

    for (int nextDigit = currentDigit + 1; nextDigit <= 9; nextDigit++)
    {
        generateNumbers(remainingDigits - 1, nextDigit,
                        currentNumber * 10 + nextDigit, result);
    }
}

vector<int> increasingNumbers(int n)
{
    vector<int> result;

    if (n == 1)
    {
        for (int digit = 0; digit <= 9; digit++)
            result.push_back(digit);

        return result;
    }

    if (n > 9)
        return result;

    for (int firstDigit = 1; firstDigit <= 9; firstDigit++)
    {
        generateNumbers(n - 1, firstDigit, firstDigit, result);
    }

    return result;
}

int main()
{
    int n = 1;

    vector<int> result = increasingNumbers(n);

    cout << "[";
    for (int i = 0; i < result.size(); i++)
    {
        cout << result[i];
        if (i != result.size() - 1)
            cout << ", ";
    }
    cout << "]";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `result.push_back(currentNumber);` | Base case: when all digits have been assigned, store the complete number. |
| 12 | `for (int nextDigit = currentDigit + 1; nextDigit <= 9; nextDigit++)` | Recurse for each possible next digit, ensuring the number remains strictly increasing. |
| 16 | `if (remainingDigits == 0)` | Base case: when all digits have been assigned, store the complete number. |
| 17 | `result.push_back(currentNumber);` | Base case: when all digits have been assigned, store the complete number. |
| 20 | `for (int nextDigit = currentDigit + 1; nextDigit <= 9; nextDigit++)` | Recurse for each possible next digit, ensuring the number remains strictly increasing. |
| 24 | `if (n == 1)` | Handle the trivial case: only one digit can be used. |
| 25 | `for (int digit = 0; digit <= 9; digit++)` | Generate all single‑digit numbers. |
| 28 | `if (n > 9)` | If n exceeds 9, no valid numbers exist. |
| 31 | `for (int firstDigit = 1; firstDigit <= 9; firstDigit++)` | Generate numbers starting with each possible first digit. |
| 34 | `generateNumbers(n - 1, firstDigit, firstDigit, result);` | Recurse for the remaining digits, ensuring the number remains strictly increasing. |
| 38 | `return result;` | Return the collected numbers. |
| 41 | `vector<int> result;` | Initialize result container. |
| 42 | `if (n == 1)` | Handle the trivial case: only one digit can be used. |
| 43 | `for (int digit = 0; digit <= 9; digit++)` | Generate all single‑digit numbers. |
| 46 | `if (n > 9)` | If n exceeds 9, no valid numbers exist. |
| 49 | `for (int firstDigit = 1; firstDigit <= 9; firstDigit++)` | Generate numbers starting with each possible first digit. |
| 52 | `generateNumbers(n - 1, firstDigit, firstDigit, result);` | Recurse for the remaining digits, ensuring the number remains strictly increasing. |
| 56 | `return result;` | Return the collected numbers. |
| 59 | `int n = 1;` | Test case: generate numbers for n = 1. |
| 60 | `vector<int> result = increasingNumbers(n);` | Call the function to obtain the result. |
| 61 | `cout << "["` | Output the result in a readable format. |
| 62 | `for (int i = 0; i < result.size(); i++)` | Iterate over the result vector. |
| 63 | `cout << result[i];` | Print each number. |
| 64 | `if (i != result.size() - 1)` | Add comma and space except for the last element. |
| 65 | `}` | End of loop. |
| 66 | `cout << "]";` | End of output. |
| 67 | `return 0;` | Return success. |

**Explanation**

Purpose: Generate all n‑digit positive integers where each subsequent digit is greater than or equal to the previous one.  
Input: int n – the desired length of the numbers.  
Output: vector<int> containing every possible increasing n‑digit number.  
Algorithm: Uses a depth‑first backtracking approach; for n = 1 it enumerates all single‑digit numbers, for n > 1 it enumerates numbers starting with each possible first digit, recursively generating numbers of length n‑1 with the next digit ≥ the current one. The recursion stops when n becomes zero, and the collected numbers are returned.

---

## dataset.jsonl#50 — iterative

- anchors: 1 exact, 8 relocated, **1 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
using namespace std;

bool hasIncreasingDigits(int num, int n)
{
    string s = to_string(num);

    if (s.length() != n)
        return false;

    for (int i = 1; i < n; i++)
    {
        if (s[i] <= s[i - 1])
            return false;
    }

    return true;
}

vector<int> increasingNumbers(int n)
{
    vector<int> result;

    if (n > 9)
        return result;

    int start = (n == 1) ? 0 : pow(10, n - 1);
    int end = pow(10, n) - 1;

    for (int num = start; num <= end; num++)
    {
        if (hasIncreasingDigits(num, n))
            result.push_back(num);
    }

    return result;
}

int main()
{
    int n = 1;
    vector<int> ans = increasingNumbers(n);

    cout << "[";
    for (int i = 0; i < ans.size(); i++)
    {
        cout << ans[i];
        if (i != ans.size() - 1)
            cout << ", ";
    }
    cout << "]" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (s.length() != n)` | If the number of digits does not match the requested length, it cannot be composed of exactly n digits. |
| 14 | `for (int i = 1; i < n; i++)` | Verify that each digit is strictly greater than the previous one. |
| 18 | `return true;` | All digits satisfy the increasing condition. |
| 22 | `if (n > 9)` | For n > 9 no number can be composed of exactly n digits because the smallest n‑digit number is 10^(n‑1) and the largest is 10^n‑1. |
| 26 | `int start = (n == 1) ? 0 : pow(10, n - 1);` | Compute the smallest n‑digit number (10^(n‑1)) and the largest (10^n‑1). |
| 27 | `int end = pow(10, n) - 1;` | Note: pow(10, n) yields 10^n, which is an integer; casting to int truncates, yielding 10^n‑1. |
| 30 | `if (hasIncreasingDigits(num, n))` | Collect numbers that satisfy the increasing digit property. |
| 34 | `return result;` | Return the list of qualifying numbers. |
| 38 | `int n = 1;` | Test the smallest n‑digit number (n = 1) for increasing digits. |
| 40 | `cout << "["` | Output the collected numbers in a readable format. |

**Explanation**

Purpose: Generate all n‑digit positive integers whose decimal digits strictly increase.  
Input: An integer n specifying the digit length.  
Output: A vector<int> containing every such integer.  
Algorithm: Compute the smallest and largest n‑digit numbers (start and end). Iterate from start to end, testing each with hasIncreasingDigits. Collect and return numbers that pass the test.  
Defects: The function assumes n > 9, which yields an empty result for n ≤ 9; the loop over num is unnecessary for n > 9, and the loop body is unreachable for n ≤ 9. The main function incorrectly prints the result as a single integer.

---

## dataset.jsonl#51 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void subsetSums(vector<int> &arr, int l, int r, int sum = 0)
{
    if (l > r)
    {
        cout << sum << " ";
        return;
    }

    subsetSums(arr, l + 1, r, sum + arr[l]);
    subsetSums(arr, l + 1, r, sum);
}

int main()
{
    vector<int> arr = { 5, 4, 3 };
    int n = arr.size();

    subsetSums(arr, 0, n - 1);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cout << sum << " ";` | Output the accumulated sum for the current subset. |
| 11 | `return;` | Base case: when the left index exceeds the right, the current subset sum is complete. |
| 14 | `subsetSums(arr, l + 1, r, sum + arr[l]);` | Include the element at index l in the current subset. |
| 15 | `subsetSums(arr, l + 1, r, sum);` | Exclude the element at index l from the current subset. |
| 19 | `vector<int> arr = { 5, 4, 3 };` | Initialise the input array with three integers. |
| 20 | `int n = arr.size();` | Determine the number of elements in the array. |
| 22 | `subsetSums(arr, 0, n - 1);` | Start the recursive subset sum generation from the first element. |

**Explanation**

Purpose: Prints all possible subset sums of the given integer array.  
Input: `vector<int> &arr` – the array to process; `int l` and `int r` – start and end indices of the current sub‑array (inclusive).  
Output: Writes each subset sum to `std::cout` separated by spaces.  
Algorithm: Uses a depth‑first recursion that adds the current element to the running sum and skips it, exploring both possibilities for each index. The recursion terminates when the sub‑array is exhausted, yielding all sums.

---

## dataset.jsonl#51 — iterative

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void subsetSums(vector<int> &arr, int n)
{
    long long total = 1 << n;

    for (long long i = 0; i < total; i++)
    {
        long long sum = 0;

        for (int j = 0; j < n; j++)
            if (i & (1 << j))
                sum += arr[j];

        cout << sum << " ";
    }
}

int main()
{
    vector<int> arr = { 5, 4, 3 };
    int n = arr.size();

    subsetSums(arr, n);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `long long total = 1 << n;` | total number of subsets (2^n) |
| 5 | `for (long long i = 0; i < total; i++)` | iterate over each subset bitmask |
| 6 | `long long sum = 0;` | accumulate sum of elements in the current subset |
| 7 | `for (int j = 0; j < n; j++)` | examine each element |
| 8 | `if (i & (1 << j))` | if the j‑th bit of i is set, add arr[j] to the sum |
| 11 | `cout << sum << " ";` | output the computed subset sum |
| 14 | `vector<int> arr = { 5, 4, 3 };` | example input: three integers |
| 15 | `int n = arr.size();` | number of elements in the array |
| 17 | `subsetSums(arr, n);` | generate and print all subset sums |

**Explanation**

Purpose: Prints all possible subset sums of a given integer array.  
Input: `vector<int> &arr` – the array whose subsets are summed; `int n` – number of elements in `arr`.  
Output: Writes each subset sum to `std::cout`, separated by spaces.  
Algorithm: Compute 2ⁿ (total number of subsets) using a bitmask. For each bitmask, iterate over the array, add elements whose corresponding bit is set, and output the accumulated sum. The loop runs O(2ⁿ) time.

---

## dataset.jsonl#52 — recursive

- anchors: 2 exact, 5 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

void printRec(string number, int extraOnes, int remainingPlaces)
{
    if (remainingPlaces == 0)
    {
        cout << number << " ";
        return;
    }

    printRec(number + "1", extraOnes + 1, remainingPlaces - 1);

    if (extraOnes > 0)
        printRec(number + "0", extraOnes - 1, remainingPlaces - 1);
}

void printNums(int n)
{
    string str = "";
    printRec(str, 0, n);
}

int main()
{
    int n = 4;
    printNums(n);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cout << number << " ";` | output the constructed number followed by a space |
| 11 | `return;` | base case: no more places left |
| 14 | `printRec(number + "1", extraOnes + 1, remainingPlaces - 1);` | try appending "1" and recurse |
| 16 | `printRec(number + "0", extraOnes - 1, remainingPlaces - 1);` | try appending "0" and recurse, only if extraOnes > 0 |
| 20 | `string str = "";` | start with an empty string |
| 21 | `printRec(str, 0, n);` | generate all n‑digit numbers using the helper |
| 24 | `int n = 4;` | example call: generate numbers of length 4 |

**Explanation**

Purpose: Generates and prints all binary strings of length n.  
Input: An integer n specifying the desired string length.  
Output: Prints each generated binary string to standard output, each on a separate line.  
Algorithm: Uses a depth‑first recursion that builds the string incrementally, appending either ‘1’ or ‘0’ at each step. When the remaining length reaches zero, the built string is printed. The recursion explores all possible combinations, yielding O(2ⁿ) total strings.

---

## dataset.jsonl#52 — iterative

- anchors: 1 exact, 35 relocated, **0 quoting a line that is not in the file**, of 36
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
#include <iostream>
using namespace std;

string getBinaryRep(int N, int num_of_bits)
{
    string r = "";
    num_of_bits--;

    while (num_of_bits >= 0)
    {
        if (N & (1 << num_of_bits))
            r.append("1");
        else
            r.append("0");
        num_of_bits--;
    }
    return r;
}

vector<string> NBitBinary(int N)
{
    vector<string> r;
    int first = 1 << (N - 1);
    int last = first * 2;

    for (int i = last - 1; i >= first; --i)
    {
        int zero_cnt = 0;
        int one_cnt = 0;
        int t = i;
        int num_of_bits = 0;

        while (t)
        {
            if (t & 1)
                one_cnt++;
            else
                zero_cnt++;
            num_of_bits++;
            t = t >> 1;
        }

        if (one_cnt >= zero_cnt)
        {
            bool all_prefix_match = true;
            int msk = (1 << num_of_bits) - 2;
            int prefix_shift = 1;

            while (msk)
            {
                int prefix = (msk & i) >> prefix_shift;
                int prefix_one_cnt = 0;
                int prefix_zero_cnt = 0;

                while (prefix)
                {
                    if (prefix & 1)
                        prefix_one_cnt++;
                    else
                        prefix_zero_cnt++;
                    prefix = prefix >> 1;
                }

                if (prefix_zero_cnt > prefix_one_cnt)
                {
                    all_prefix_match = false;
                    break;
                }

                prefix_shift++;
                msk = msk & (msk << 1);
            }

            if (all_prefix_match)
                r.push_back(getBinaryRep(i, num_of_bits));
        }
    }
    return r;
}

int main()
{
    int n = 4;
    vector<string> results = NBitBinary(n);

    for (int i = 0; i < results.size(); ++i)
        cout << results[i] << " ";

    cout << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (num_of_bits >= 0)` | Build the binary representation by iterating over each bit position from most‑significant to least‑significant. |
| 11 | `if (N & (1 << num_of_bits))` | If the current bit is set, append '1'; otherwise append '0'. |
| 14 | `num_of_bits--;` | Move to the next bit position. |
| 18 | `int first = 1 << (N - 1);` | Compute the highest power of two ≤ N (i.e., 2^(N‑1)). |
| 19 | `int last = first * 2;` | The range of numbers we need to consider is from 2^(N‑1) down to 2^N‑1. |
| 22 | `int zero_cnt = 0;` | Count the number of bits set to 0 and 1 in the current number. |
| 23 | `int one_cnt = 0;` | Initialize counters for zero and one bits. |
| 24 | `int t = i;` | Work on a copy of the number to avoid modifying the original. |
| 25 | `int num_of_bits = 0;` | Track the current bit position. |
| 26 | `while (t)` | Iterate over each bit of the number. |
| 27 | `if (t & 1)` | If the least‑significant bit is 1, increment the one‑bit counter. |
| 28 | `else` | Otherwise, increment the zero‑bit counter. |
| 30 | `num_of_bits++;` | Move to the next bit position. |
| 31 | `t = t >> 1;` | Shift right to examine the next bit. |
| 34 | `if (one_cnt >= zero_cnt)` | If the number of ones is greater than or equal to the number of zeros, it can be expressed as a single binary number. |
| 35 | `bool all_prefix_match = true;` | Verify that all prefixes of the number have at least as many ones as zeros. |
| 36 | `int msk = (1 << num_of_bits) - 2;` | Mask to isolate the most‑significant bit of the current number. |
| 37 | `int prefix_shift = 1;` | Track the current position within the prefix. |
| 38 | `while (msk)` | Iterate over each prefix of the number. |
| 39 | `int prefix = (msk & i) >> prefix_shift;` | Extract the current prefix from the number. |
| 40 | `int prefix_one_cnt = 0;` | Count the number of ones and zeros in the current prefix. |
| 41 | `int prefix_zero_cnt = 0;` | Initialize counters for zero and one bits in the current prefix. |
| 42 | `while (prefix)` | Iterate over each bit of the prefix. |
| 43 | `if (prefix & 1)` | If the least‑significant bit is 1, increment the one‑bit counter. |
| 44 | `else` | Otherwise, increment the zero‑bit counter. |
| 46 | `if (prefix_zero_cnt > prefix_one_cnt)` | If the number of zeros exceeds the number of ones in the current prefix, the number cannot be expressed as a single binary number. |
| 47 | `all_prefix_match = false;` | Exit early if any prefix fails the check. |
| 48 | `break;` | No need to check further prefixes. |
| 49 | `prefix_shift++;` | Move to the next bit position within the prefix. |
| 50 | `msk = msk & (msk << 1);` | Shift the mask left to consider the next bit. |
| 52 | `if (all_prefix_match)` | If all prefixes satisfy the condition, add the binary representation of the number to the result vector. |
| 53 | `r.push_back(getBinaryRep(i, num_of_bits));` | Compute the binary representation of the number using the helper function. |
| 56 | `int n = 4;` | Example usage: compute binary representations for numbers with up to 4 bits. |
| 57 | `vector<string> results = NBitBinary(n);` | Call the function to obtain the result. |
| 58 | `for (int i = 0; i < results.size(); ++i)` | Print each binary representation. |
| 60 | `cout << endl;` | End the output with a newline. |

**Explanation**

Purpose: Generate all binary strings of length N that contain at least one ‘1’ and have a maximal number of ‘1’s.  
Input: int N – desired length of the binary strings.  
Output: vector<string> – list of qualifying binary strings.  
Algorithm: Enumerate all integers in the range [2^(N‑1), 2^N‑1] (inclusive). For each integer, count its set bits and the number of bits. If the count of ‘1’s is ≥ the count of ‘0’s, compute the maximal prefix that can be formed by shifting the integer left while maintaining the same count of ‘1’s and ‘0’s. If the prefix satisfies the condition, convert the integer to its binary representation and store it. The final list is returned.

---

## dataset.jsonl#53 — recursive

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int sumOfDigits(int n)
{
    if (n == 0)
        return 0;

    return (n % 10) + sumOfDigits(n / 10);
}

int main()
{
    cout << sumOfDigits(12345);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: when n becomes zero, the recursion unwinds and the accumulated sum is returned. |
| 5 | `return (n % 10) + sumOfDigits(n / 10);` | Recursive step: extract the least‑significant digit with n % 10, add it to the sum of the remaining digits obtained by dividing n by 10. |
| 8 | `cout << sumOfDigits(12345);` | Print the sum of the decimal digits of 12345; the result is 15. |

**Explanation**

Purpose: Computes the sum of the decimal digits of a non‑negative integer.  
Input: An `int n` representing the number whose digit sum is required.  
Output: An `int` equal to the sum of the digits of `n`.  
Algorithm: Handles the base case `n == 0` by returning 0. For other values it extracts the least‑significant digit with `n % 10` and recursively adds it to the sum of the remaining digits obtained by `n / 10`. The recursion unwinds, accumulating the total sum.

---

## dataset.jsonl#53 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

int sumOfDigits(int n)
{
    string s = to_string(n);
    int sum = 0;

    for (char ch : s)
    {
        sum += ch - '0';
    }

    return sum;
}

int main()
{
    int n = 12345;
    cout << sumOfDigits(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `string s = to_string(n);` | Convert the integer to its decimal string representation. |
| 4 | `int sum = 0;` | Accumulator for the digit sum. |
| 6 | `for (char ch : s)` | Iterate over each character in the string. |
| 7 | `sum += ch - '0';` | Convert the character back to its numeric value and add to the sum. |
| 9 | `return sum;` | Return the total digit sum. |
| 12 | `int n = 12345;` | Example usage: sum of digits of 12345. |

**Explanation**

Purpose: Computes the sum of the decimal digits of an integer.  
Input: An `int n` representing the number whose digit sum is required.  
Output: An `int` containing the total sum of the digits.  
Algorithm: Convert `n` to a string, iterate over each character, convert each character back to its numeric value, and accumulate the sum. The loop runs O(log |n|) times, yielding O(1) time complexity.

---

## dataset.jsonl#54 — recursive

- anchors: 1 exact, 6 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

void dfs(int pos, int n, int prevBit, int num, vector<int> &ans)
{
    if (pos == n)
    {
        ans.push_back(num);
        return;
    }

    dfs(pos + 1, n, 0, num << 1, ans);

    if (prevBit == 0)
    {
        dfs(pos + 1, n, 1, (num << 1) | 1, ans);
    }
}

vector<int> noConsecutiveOnes(int n)
{
    vector<int> ans;
    dfs(0, n, 0, 0, ans);

    ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());
    return ans;
}

int main()
{
    int n = 3;

    vector<int> ans = noConsecutiveOnes(n);

    for (int x : ans)
        cout << x << " ";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `ans.push_back(num);` | Base case: all bits filled, store the generated number |
| 13 | `dfs(pos + 1, n, 0, num << 1, ans);` | Include the current bit as 0 and recurse |
| 15 | `dfs(pos + 1, n, 1, (num << 1) \| 1, ans);` | Include the current bit as 1 and recurse, ensuring no two consecutive 1s |
| 20 | `ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());` | Remove any leading zeros that were added during the DFS |
| 24 | `int n = 3;` | Generate all binary numbers with exactly 3 bits, each differing from the previous one |
| 25 | `vector<int> ans = noConsecutiveOnes(n);` | Call the helper to collect all distinct numbers |
| 26 | `for (int x : ans)` | Output each number |

**Explanation**

Purpose: Generate all binary numbers of length n that contain no two consecutive 1s.  
Input: An integer n specifying the number of bits.  
Output: A vector<int> containing every feasible number as a decimal.  
Algorithm: Perform a depth‑first search from position 0, maintaining a bitmask of the previous bit. When the position reaches n, store the number. After the search, remove any leading zeros and return the result.  
Defects: The original code does not handle the case where n is 0, leading to an empty vector. The recursive call to dfs does not propagate the bitmask, causing incorrect results. The final removal of zeros is performed after the search, which may leave trailing zeros.

---

## dataset.jsonl#54 — iterative

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <vector>
#include <iostream>
#include <algorithm>
using namespace std;

bool isValid(int num)
{
    while (num > 0)
    {
        if ((num & 1) && (num & 2))
            return false;
        num >>= 1;
    }
    return true;
}

vector<int> noConsecutiveOnes(int n)
{
    vector<int> ans;

    for (int num = 0; num < (1 << n); num++)
    {
        if (isValid(num))
            ans.push_back(num);
    }

    ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());
    return ans;
}

int main()
{
    int n = 3;

    vector<int> ans = noConsecutiveOnes(n);

    for (int x : ans)
        cout << x << " ";

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `num >>= 1;` | shift right to examine the next bit |
| 12 | `return true;` | all bits examined without two consecutive ones |
| 17 | `for (int num = 0; num < (1 << n); num++)` | iterate over all possible n‑bit numbers |
| 18 | `if (isValid(num))` | keep only those whose bits are valid |
| 21 | `ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());` | remove any leading zeros that were accidentally included |
| 24 | `int n = 3;` | number of bits for the generated numbers |
| 25 | `vector<int> ans = noConsecutiveOnes(n);` | generate all n‑bit numbers with no consecutive ones |
| 26 | `for (int x : ans)` | print each valid number |

**Explanation**

Purpose: Generate all non‑consecutive‑1‑bit numbers of length n.  
Input: An integer n representing the number of bits.  
Output: A vector<int> containing every integer with no two consecutive 1‑bits.  
Algorithm: Enumerate all 2ⁿ numbers using a loop, test each with the helper isValid that rejects numbers with both LSB and second LSB set, collect valid ones, then remove the zero entry using erase‑remove idiom.

---

## dataset.jsonl#55 — recursive

- anchors: 1 exact, 4 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

int countRec(int choc, int wrap)
{
    if (choc < wrap)
        return 0;

    int newChoc = choc / wrap;

    return newChoc + countRec(newChoc + choc % wrap, wrap);
}

int countChocolates(int money, int price, int wrap)
{
    int choc = money / price;
    return choc + countRec(choc, wrap);
}

int main()
{
    int money = 15;
    int price = 2;
    int wrap = 3;

    cout << countChocolates(money, price, wrap);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `int newChoc = choc / wrap;` | Compute how many complete chocolates can be made from the initial stock. |
| 11 | `return newChoc + countRec(newChoc + choc % wrap, wrap);` | Recurse with the remainder chocolates and the same wrap count; the recursive call adds any leftover chocolates that can be wrapped into new chocolates. |
| 14 | `int choc = money / price;` | Compute the maximum number of chocolates that can be bought with the given money. |
| 15 | `return choc + countRec(choc, wrap);` | Add the chocolates produced by the initial purchase to the chocolates produced by the recursive call. |
| 18 | `cout << countChocolates(money, price, wrap);` | Output the total number of chocolates that can be obtained. |

**Explanation**

Purpose: Compute the total number of chocolates that can be obtained from a given amount of money, assuming each chocolate costs $2 and each wrapper can be exchanged for one additional chocolate.  
Input: `money` (int) – total money available; `price` (int) – cost per chocolate; `wrap` (int) – number of wrappers needed to get one extra chocolate.  
Output: `int` – total number of chocolates that can be obtained.  
Algorithm: First compute the initial number of chocolates from the money. Then recursively add chocolates obtained from exchanging wrappers until no more wrappers can be exchanged. The recursion stops when the number of chocolates is less than the number of wrappers needed to obtain another chocolate.

---

## dataset.jsonl#55 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int countChocolates(int money, int price, int wrap)
{
    if (money < price)
        return 0;

    int choc = money / price;
    choc = choc + (choc - 1) / (wrap - 1);

    return choc;
}

int main()
{
    int money = 15;
    int price = 1;
    int wrap = 3;

    cout << countChocolates(money, price, wrap);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (money < price)` | If the initial amount of money is insufficient to buy at least one chocolate, there are no chocolates. |
| 6 | `int choc = money / price;` | Compute the number of chocolates that can be bought without considering wrapping. |
| 7 | `choc = choc + (choc - 1) / (wrap - 1);` | Apply the wrapping rule: each chocolate bought gives one extra chocolate, but only wrap - 1 of those extra chocolates can be bought. The formula (choc - 1) / (wrap - 1) counts the extra chocolates that can be bought after the initial purchase. |
| 10 | `int money = 15;` | Example usage: 15 coins, each costing 1 coin, and each chocolate gives 1 coin plus one extra (wrap = 3). |
| 11 | `int price = 1;` | price per chocolate |
| 12 | `int wrap = 3;` | number of chocolates that can be bought for each extra chocolate |
| 14 | `cout << countChocolates(money, price, wrap);` | Output the total number of chocolates that can be bought. |

**Explanation**

Purpose: Compute the maximum number of chocolates that can be bought with a given amount of money, considering a wrap‑reward scheme.  
Input: three integers – `money` (total cash), `price` (cost per chocolate), `wrap` (number of chocolates that can be obtained for each wrapped chocolate).  
Output: an integer representing the total count of chocolates that can be obtained.  
Algorithm: Start with the initial number of chocolates equal to `money / price`. Then repeatedly add chocolates from the wrapped ones until no more wrap‑reward chocolates can be obtained. The final count is returned.

---

## dataset.jsonl#56 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

int minRecur(int curr, int steps, int d)
{
    if (abs(curr) > d)
        return INT_MAX;

    if (curr == d)
        return steps;

    int left = minRecur(curr - steps - 1, steps + 1, d);
    int right = minRecur(curr + steps + 1, steps + 1, d);

    return min(left, right);
}

int minSteps(int d)
{
    d = abs(d);
    return minRecur(0, 0, d);
}

int main()
{
    int d = 2;
    cout << minSteps(d);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (abs(curr) > d)` | If the current position exceeds the target distance, no further moves are possible. |
| 13 | `if (curr == d)` | If we have reached the target, the number of steps taken is the answer. |
| 16 | `int left = minRecur(curr - steps - 1, steps + 1, d);` | Explore the left side: decrement by one step, increment by one step. |
| 17 | `int right = minRecur(curr + steps + 1, steps + 1, d);` | Explore the right side: increment by one step, increment by one step. |
| 19 | `return min(left, right);` | Return the minimum number of steps required to reach the target. |
| 23 | `d = abs(d);` | Convert the distance to its absolute value; the problem assumes a non‑negative target. |
| 24 | `return minRecur(0, 0, d);` | Start the recursive search from position 0 with an initial step count of 0. |
| 27 | `int d = 2;` | Example usage: compute the minimum number of steps to reach distance 2. |

**Explanation**

Purpose: Compute the minimum number of steps required to reach exactly d from 0, moving either left or right by 1 step each time.  
Input: int d – the target distance (positive or negative).  
Output: int – the minimal step count, or INT_MAX if the target is unreachable.  
Algorithm: minSteps first normalizes d to its absolute value, then calls minRecur starting from 0 with an initial step count of 0. minRecur recursively explores both possible moves, pruning branches where the absolute value of the current position exceeds d, and returns the smallest step count found.

---

## dataset.jsonl#56 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <cstdlib>
using namespace std;

int minSteps(int d)
{
    d = abs(d);

    int sum = 0, step = 0;

    while (sum < d || (sum - d) % 2 != 0)
    {
        step++;
        sum += step;
    }

    return step;
}

int main()
{
    int d = 2;
    cout << minSteps(d);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `d = abs(d);` | ensure distance is non‑negative for the loop condition |
| 5 | `int sum = 0, step = 0;` | sum accumulates the total distance covered so far; step counts the current step |
| 6 | `while (sum < d \|\| (sum - d) % 2 != 0)` | continue until the accumulated distance is at least d and the remainder when subtracted from d is odd |
| 7 | `step++;` | advance to the next step |
| 8 | `sum += step;` | add the new step length to the total |
| 10 | `return step;` | return the minimal number of steps required |
| 13 | `int d = 2;` | example distance; the function will always produce 2 steps for this input |

**Explanation**

Purpose: Compute the minimum number of steps required to reach a target distance by repeatedly adding consecutive integers.  
Input: An integer d representing the target distance.  
Output: An integer indicating the minimal step count.  
Algorithm: Start with sum = 0 and step = 0. Repeatedly add step to sum until sum ≥ d or (sum − d) is odd. The loop stops when the condition is satisfied, and the current step count is returned.

---

## dataset.jsonl#57 — recursive

> **names a container the code does not use**

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

  - *container NOT in the code*: The recursion depth grows exponentially, leading to exponential time and stack overflow for large n.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int fibonacci(int n)
{
    if (n <= 1)
        return n;

    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main()
{
    int n;
    cin >> n;
    cout << fibonacci(n);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n <= 1)` | Base case: for n <= 1 the sequence is defined as n itself. |
| 5 | `return fibonacci(n - 1) + fibonacci(n - 2);` | Recursive step: sum of the two preceding Fibonacci numbers. This is the classic iterative definition, but the original code lacks a loop or memoization, leading to exponential time. |
| 9 | `cin >> n;` | Read the desired index from standard input. |
| 10 | `cout << fibonacci(n);` | Output the n‑th Fibonacci number. |

**Explanation**

Purpose: Computes the n‑th Fibonacci number using a naive recursive definition.  
Input: An integer n representing the index of the desired Fibonacci term.  
Output: An integer containing the Fibonacci value at position n.  
Algorithm: The function checks for the base cases (n ≤ 1) and returns n directly. For larger n it recursively calls itself to obtain the two preceding Fibonacci numbers, sums them, and returns the result. The recursion depth grows exponentially, leading to exponential time and stack overflow for large n.

---

## dataset.jsonl#57 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int fibonacci(int n)
{
    if (n <= 1)
        return n;

    int prev2 = 0;
    int prev1 = 1;
    int current = 0;

    for (int i = 2; i <= n; ++i)
    {
        current = prev1 + prev2;
        prev2 = prev1;
        prev1 = current;
    }

    return current;
}

int main()
{
    int n;
    cin >> n;
    cout << fibonacci(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n <= 1)` | Base case: for n <= 1 the sequence is defined as 0 or 1. |
| 10 | `for (int i = 2; i <= n; ++i)` | Iterate from 2 up to n, updating the three consecutive Fibonacci numbers. |
| 12 | `prev2 = prev1;` | Shift the window forward: prev2 becomes prev1, prev1 becomes current. |
| 14 | `return current;` | After the loop, current holds the n‑th Fibonacci number. |
| 18 | `cin >> n;` | Read the desired index from standard input. |
| 19 | `cout << fibonacci(n) << endl;` | Output the computed Fibonacci number. |

**Explanation**

Purpose: Compute the n‑th Fibonacci number.  
Input: An integer n representing the index (0‑based).  
Output: An integer containing the Fibonacci value at position n.  
Algorithm: Handles the trivial cases n ≤ 1 directly. For n > 1 it iteratively builds the sequence using three variables (prev2, prev1, current) until the nth term is reached, then returns it. The loop runs from 2 up to n, updating the three variables each iteration.

---

## dataset.jsonl#58 — recursive

- anchors: 3 exact, 9 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <bits/stdc++.h>
using namespace std;

int memo[37] = {0};

int stepPerms(int n)
{
    if (n == 0)
        return 1;

    if (n < 0)
        return 0;

    if (memo[n] != 0)
        return memo[n];

    long long MOD = 10000000007LL;

    long long totalWays = ((long long)stepPerms(n - 1) +
                           (long long)stepPerms(n - 2) +
                           (long long)stepPerms(n - 3)) % MOD;

    memo[n] = totalWays;
    return memo[n];
}

int main()
{
    int s;
    cin >> s;

    while (s--)
    {
        int n;
        cin >> n;
        cout << stepPerms(n) << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (n == 0)` | Base case: exactly one way to stay at the ground floor (do nothing). |
| 12 | `if (n < 0)` | Negative floors are impossible; return 0. |
| 14 | `if (memo[n] != 0)` | Return cached result if already computed. |
| 17 | `long long MOD = 10000000007LL;` | Modulus for the final answer to avoid overflow. |
| 19 | `long long totalWays = ((long long)stepPerms(n - 1) +` | Sum of ways to reach the floor directly above, two floors above, and three floors above. |
| 21 | `(long long)stepPerms(n - 2) +` | Note: casting to long long is redundant because the operands are already integers. |
| 23 | `(long long)stepPerms(n - 3)) % MOD;` | Apply modulus to keep the result within the required range. |
| 25 | `memo[n] = totalWays;` | Cache the result for future calls. |
| 28 | `int s;` | Number of test cases. |
| 30 | `while (s--)` | Process each test case. |
| 32 | `int n;` | Current floor number. |
| 34 | `cout << stepPerms(n) << endl;` | Output the number of distinct ways to reach the nth floor. |

**Explanation**

Purpose: Compute the number of distinct ways to climb a staircase with n steps, where each step can be taken in one of three possible ways.  
Input: An integer s indicating how many test cases follow, followed by each test case’s step count n.  
Output: For each n, prints the count modulo 1 000 000 007.  
Algorithm: Uses a recursive memoization table to avoid recomputing sub‑problems. The base cases handle n = 0, n < 0, and n = 1. For n ≥ 2, it recursively sums the results of stepping one, two, or three steps back, applying modulo 1 000 000 007 to keep the result within bounds. The table is reused across calls to avoid redundant work.

---

## dataset.jsonl#58 — iterative

- anchors: 0 exact, 18 relocated, **0 quoting a line that is not in the file**, of 18
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int stepPerms(int n)
{
    if (n == 1)
        return 1;

    if (n == 2)
        return 2;

    if (n == 3)
        return 4;

    long long a = 1;
    long long b = 2;
    long long c = 4;
    long long current = 0;
    long long MOD = 10000000007LL;

    for (int i = 4; i <= n; i++)
    {
        current = (a + b + c) % MOD;
        a = b;
        b = c;
        c = current;
    }

    return current;
}

int main()
{
    int n;
    cin >> n;
    cout << stepPerms(n) << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 1)` | Base case: only one way to climb to the 1st step |
| 6 | `if (n == 2)` | Base case: two ways to climb to the 2nd step (1+1 or 2) |
| 9 | `if (n == 3)` | Base case: four ways to climb to the 3rd step (1+1+1, 1+2, 2+1, 3) |
| 12 | `long long a = 1;` | Initialize DP state: a = ways to reach step 1, b = ways to reach step 2, c = ways to reach step 3 |
| 13 | `long long b = 2;` | Initialise DP state: a = ways to reach step 1, b = ways to reach step 2, c = ways to reach step 3 |
| 14 | `long long c = 4;` | Initialise DP state: a = ways to reach step 1, b = ways to reach step 2, c = ways to reach step 3 |
| 15 | `long long current = 0;` | Current number of ways to reach step i |
| 16 | `long long MOD = 10000000007LL;` | Modulus to keep the result within 64-bit range |
| 18 | `for (int i = 4; i <= n; i++)` | Iterate from step 4 to n, updating DP state |
| 19 | `current = (a + b + c) % MOD;` | New number of ways to reach step i = sum of ways to reach steps 1, 2, and 3 |
| 20 | `a = b;` | Shift DP state forward |
| 21 | `b = c;` | Shift DP state forward |
| 22 | `c = current;` | Shift DP state forward |
| 25 | `return current;` | Return the number of ways to reach step n |
| 28 | `int n;` | Read input step count |
| 29 | `cin >> n;` | Read input step count |
| 30 | `cout << stepPerms(n) << endl;` | Output result |
| 33 | `return 0;` | Return success |

**Explanation**

Purpose: Compute the number of distinct ways to climb a staircase with n steps, where each step can be taken in one of three possible ways.  
Input: An integer n representing the total number of steps.  
Output: An integer representing the total number of distinct stepping sequences modulo 1 000 000 007.  
Algorithm: Handles the base cases n = 1, 2, 3 directly. For n ≥ 4 it iteratively builds the sequence using the recurrence a = b + c, updating the previous three values modulo 1 000 000 007. The final result is returned.

---

## dataset.jsonl#59 — recursive

- anchors: 1 exact, 7 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

int getSuperDigit(long long modernSum)
{
    if (modernSum < 10)
        return modernSum;

    long long nextSum = 0;
    while (modernSum > 0)
    {
        nextSum += modernSum % 10;
        modernSum /= 10;
    }

    return getSuperDigit(nextSum);
}

int superDigit(string n, int k)
{
    long long initialSum = 0;

    for (char digit : n)
        initialSum += (digit - '0');

    initialSum *= k;

    return getSuperDigit(initialSum);
}

int main()
{
    string n;
    int k;
    cin >> n >> k;
    cout << superDigit(n, k) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (modernSum < 10)` | Base case: a single‑digit sum is already the super‑digit. |
| 14 | `while (modernSum > 0)` | Reduce the current sum to a single‑digit by repeatedly adding its digits. |
| 18 | `return getSuperDigit(nextSum);` | Recursively compute the super‑digit of the reduced sum. |
| 23 | `for (char digit : n)` | Convert each character of the input string into its numeric value. |
| 26 | `initialSum *= k;` | Multiply the accumulated sum by the multiplier k. |
| 29 | `return getSuperDigit(initialSum);` | Compute the super‑digit of the final product. |
| 33 | `cin >> n >> k;` | Read the input number and multiplier from standard input. |
| 34 | `cout << superDigit(n, k) << endl;` | Output the super‑digit of the combined sum. |

**Explanation**

Purpose: Compute the super‑digit of a number formed by concatenating k copies of n.  
Input: A string n representing the original number, and an integer k indicating how many times n should be concatenated.  
Output: An integer equal to the super‑digit of the concatenated product.  
Algorithm: First, compute the sum of the digits of n, multiply it by k, then repeatedly reduce the sum to a single digit using the classic super‑digit algorithm until a single‑digit result is obtained.

---

## dataset.jsonl#59 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <string>
using namespace std;

int superDigit(string n, int k)
{
    long long initial_sum = 0;

    for (char c : n)
        initial_sum += (c - '0');

    long long total_sum = initial_sum * k;

    if (total_sum == 0)
        return 0;

    long long result = total_sum % 9;
    return (result == 0) ? 9 : result;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `for (char c : n)` | Iterate over each character in the input string, convert it to its numeric value, and accumulate the sum. |
| 4 | `initial_sum += (c - '0');` | Convert character to digit and add to running total. |
| 6 | `long long total_sum = initial_sum * k;` | Multiply the accumulated sum by the multiplier k. |
| 7 | `if (total_sum == 0)` | If the product is zero, the super digit is defined as 0. |
| 9 | `long long result = total_sum % 9;` | Compute the remainder when the product is divided by 9. This gives the super digit. |
| 10 | `return (result == 0) ? 9 : result;` | If the remainder is 0, the super digit is 9; otherwise it is the remainder itself. |

**Explanation**

Purpose: Compute the super‑digit of a number formed by repeating a string k times.  
Input: `n` – a decimal string representing the original number; `k` – an integer repeat count.  
Output: An `int` representing the super‑digit (0‑9).  
Algorithm: Convert the string to a numeric sum, multiply by k, then reduce modulo 9 to obtain the super‑digit. Edge case: if the initial sum is zero, the result is 0.

---

## dataset.jsonl#60 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printRecursion(int n)
{
    if (n == 0)
        return;

    printRecursion(n - 1);
    cout << "I love Recursion" << endl;
}

int main()
{
    int n;
    cin >> n;

    printRecursion(n);

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: recursion stops when n reaches zero. |
| 5 | `printRecursion(n - 1);` | Recurse first to handle the smaller problem. |
| 6 | `cout << "I love Recursion" << endl;` | Output the final message after the recursive call. |
| 9 | `int n;` | Read the number of iterations from the user. |
| 10 | `cin >> n;` | Note: no validation or error handling for non‑positive inputs. |
| 11 | `printRecursion(n);` | Start the recursion chain. |
| 12 | `return 0;` | Normal exit. |

**Explanation**

Purpose: Prints the string "I love Recursion" n times, using recursion.  
Input: An integer n – the number of repetitions.  
Output: No return value; writes n lines to standard output.  
Algorithm: If n is zero, the function returns immediately. Otherwise it recursively calls itself with n‑1, then prints the message. The recursion depth grows linearly with n, leading to exponential time complexity.

---

## dataset.jsonl#60 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    for (int i = 0; i < n; i++)
    {
        cout << "I love Recursion" << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | Read the number of repetitions from standard input |
| 5 | `cout << "I love Recursion" << endl;` | Output the phrase exactly n times |
| 7 | `return 0;` | Normal exit from main |

**Explanation**

Purpose: Prints a fixed message to standard output n times.  
Input: Reads an integer n from standard input; the loop runs n times.  
Output: Writes n copies of the message "I love Recursion" followed by a newline to standard output.  
Algorithm: Reads n, then iterates i from 0 to n‑1, each time outputting the message. The loop body is executed n times, so the total output length is n * "I love Recursion". No error handling is performed.

---

## dataset.jsonl#61 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printNumbers(int n)
{
    if (n == 0)
        return;

    printNumbers(n - 1);
    cout << n << endl;
}

int main()
{
    int n;
    cin >> n;

    printNumbers(n);

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: stop recursion when n reaches zero |
| 6 | `printNumbers(n - 1);` | Recursively print numbers from 1 to n-1 |
| 7 | `cout << n << endl;` | Output the current number after the recursive call |
| 10 | `cin >> n;` | Read the input integer |
| 11 | `printNumbers(n);` | Start the recursive printing process |
| 12 | `return 0;` | Return success status |

**Explanation**

Purpose: Prints all integers from 1 to n in ascending order.  
Input: An integer n – the upper bound of the sequence.  
Output: Writes each integer from 1 to n to standard output, each followed by a newline.  
Algorithm: Recursively calls itself with n‑1, then prints n after the recursive call returns. The recursion stops when n reaches 0, ensuring the sequence starts at 1.

---

## dataset.jsonl#61 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    for (int i = 1; i <= n; i++)
    {
        cout << i << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | Read the number of integers to output. |
| 5 | `cout << i << endl;` | Output each integer from 1 to n, each followed by a newline. |
| 7 | `return 0;` | Normal exit from main. |

**Explanation**

Purpose: Prints the first n positive integers to standard output.  
Input: An integer n read from standard input.  
Output: Writes each integer from 1 to n to standard output, each followed by a newline.  
Algorithm: Reads n, then iterates i from 1 to n, outputting i each iteration. No error handling is performed.

---

## dataset.jsonl#62 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printNumbers(int n)
{
    if (n == 0)
        return;

    cout << n << endl;
    printNumbers(n - 1);
}

int main()
{
    int n;
    cin >> n;

    printNumbers(n);

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: stop recursion when the countdown reaches zero. |
| 6 | `cout << n << endl;` | Output the current number followed by a newline. |
| 7 | `printNumbers(n - 1);` | Recurse with the decremented value, printing each intermediate result. |
| 10 | `cin >> n;` | Read the input integer; the function expects a non‑negative value. |
| 11 | `printNumbers(n);` | Start the recursive printing sequence. |

**Explanation**

Purpose: Prints all integers from 1 to n in ascending order.  
Input: An integer n – the upper bound of the sequence.  
Output: Writes each integer from 1 to n to standard output, each followed by a newline.  
Algorithm: Uses a simple recursive loop that decrements n each call, printing the current value and recursing until n reaches 0. The loop naturally handles the base case n == 0.

---

## dataset.jsonl#62 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    for (int i = n; i >= 1; i--)
    {
        cout << i << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | Read the number of integers to output. |
| 5 | `for (int i = n; i >= 1; i--)` | Loop from n down to 1, printing each value followed by a newline. |
| 8 | `return 0;` | Success exit code. |

**Explanation**

Purpose: Prints the sequence of integers from n down to 1, each followed by a newline.  
Input: An integer n read from standard input.  
Output: No return value; writes n lines to standard output.  
Algorithm: Reads n, then iterates i from n down to 1, outputting i each iteration. The loop body is executed exactly once per iteration.

---

## dataset.jsonl#63 — recursive

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printDigits(long long n)
{
    if (n < 10)
    {
        cout << n << " ";
        return;
    }

    printDigits(n / 10);
    cout << n % 10 << " ";
}

int main()
{
    int T;
    cin >> T;

    while (T--)
    {
        long long n;
        cin >> n;
        printDigits(n);
        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n < 10)` | Base case: single‑digit numbers are printed directly. |
| 4 | `cout << n << " ";` | Output the digit followed by a space. |
| 5 | `return;` | No further recursion needed. |
| 8 | `printDigits(n / 10);` | Recursively print the digits of the number. |
| 9 | `cout << n % 10 << " ";` | Output the least‑significant digit. |
| 13 | `cin >> T;` | Read the number of test cases. |
| 14 | `while (T--)` | Process each test case sequentially. |
| 15 | `long long n;` | Read the integer to be printed. |
| 16 | `cin >> n;` | Read the integer to be printed. |
| 17 | `printDigits(n);` | Print the digits of n. |
| 18 | `cout << endl;` | Output a newline after each case. |
| 22 | `return 0;` | Normal exit. |

**Explanation**

Purpose: Prints each decimal digit of a given integer in ascending order.  
Input: A single integer `n` (signed 64‑bit) read from standard input.  
Output: For each input, the digits of `n` are printed to standard output, each followed by a space, and a newline.  
Algorithm: Uses recursion to repeatedly extract the least‑significant digit (`n % 10`) and output it, then recursively processes the rest of `n` until only single‑digit numbers remain, which are printed directly.

---

## dataset.jsonl#63 — iterative

- anchors: 1 exact, 6 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

int main()
{
    int T;
    cin >> T;

    while (T--)
    {
        string n;
        cin >> n;

        for (char digit : n)
        {
            cout << digit << " ";
        }

        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> T;` | read number of test cases |
| 5 | `while (T--)` | process each test case |
| 6 | `{` | read the integer representation of the next number |
| 10 | `cout << digit << " ";` | output each digit followed by a space |
| 11 | `}` | note: no newline after the loop for the last line |
| 12 | `cout << endl;` | output a newline after each test case |
| 14 | `return 0;` | success exit code |

**Explanation**

Purpose: Reads a series of integers, each followed by a corresponding string, then prints each character of the string on a separate line.  
Input: An integer T indicating how many lines follow, followed by T strings.  
Output: Prints each character of each string on a separate line, followed by a newline.  
Algorithm: Reads T, then for each line reads the integer and the string, then iterates over the characters of the string, outputting each character followed by a space. Finally, prints a newline.

---

## dataset.jsonl#64 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void decimalToBinary(int n)
{
    if (n == 0)
        return;

    decimalToBinary(n / 2);
    cout << n % 2;
}

int main()
{
    int T;
    cin >> T;

    while (T--)
    {
        int n;
        cin >> n;

        decimalToBinary(n);
        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: when n becomes 0, recursion unwinds and the accumulated bits are printed. |
| 6 | `decimalToBinary(n / 2);` | Recurse with the higher‑order digit. |
| 7 | `cout << n % 2;` | Output the current least‑significant bit. |
| 11 | `cin >> T;` | Read number of test cases. |
| 13 | `while (T--)` | Process each test case. |
| 14 | `int n;` | Read decimal number. |
| 16 | `decimalToBinary(n);` | Convert to binary and output. |
| 17 | `cout << endl;` | End of line for each test case. |

**Explanation**

Purpose: Convert an integer to its binary representation and print it.  
Input: An integer `n` to be converted.  
Output: Prints each bit of `n` as a decimal digit to `std::cout`, followed by a newline.  
Algorithm: Recursively divide `n` by 2, printing the remainder each time, until `n` becomes 0. The recursion builds the binary string from least‑significant bit to most‑significant bit.

---

## dataset.jsonl#64 — iterative

- anchors: 5 exact, 5 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

string decimalToBinary(int n)
{
    string result;

    while (n > 0)
    {
        result += char('0' + (n % 2));
        n /= 2;
    }

    reverse(result.begin(), result.end());
    return result;
}

int main()
{
    int T;
    cin >> T;

    while (T--)
    {
        int n;
        cin >> n;
        cout << decimalToBinary(n) << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `while (n > 0)` | Convert the decimal number to binary by repeatedly dividing by 2 and collecting remainders. |
| 12 | `result += char('0' + (n % 2));` | Append the least‑significant bit (0 or 1) as a character. |
| 13 | `n /= 2;` | Remove the processed bit from the number. |
| 16 | `reverse(result.begin(), result.end());` | Reverse the collected bits to obtain the correct binary representation. |
| 17 | `return result;` | Return the binary string. |
| 22 | `cin >> T;` | Read the number of test cases. |
| 24 | `int n;` | Read the decimal number for the current test case. |
| 25 | `cin >> n;` | Read the decimal number for the current test case. |
| 26 | `cout << decimalToBinary(n) << endl;` | Output the binary representation of the number. |
| 28 | `return 0;` | Return success. |

**Explanation**

Purpose: Convert an integer to its binary representation as a string.  
Input: An integer `n` to be converted.  
Output: A `std::string` containing the binary digits of `n` in little‑endian order.  
Algorithm: Repeatedly divide `n` by 2, appending the remainder (0 or 1) to a result string, until `n` becomes zero. Finally, reverse the string to obtain the correct binary order.

---

## dataset.jsonl#65 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

void printEvenIndices(vector<long long>& a, int index)
{
    if (index < 0)
        return;

    if (index % 2 == 0)
        cout << a[index] << " ";

    printEvenIndices(a, index - 1);
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    printEvenIndices(a, n - 1);
    cout << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cout << a[index] << " ";` | Output the element at the current even index. |
| 11 | `printEvenIndices(a, index - 1);` | Recurse with the next index, ensuring the recursion stops when the base case is reached. |
| 16 | `cin >> n;` | Read the number of elements from standard input. |
| 17 | `vector<long long> a(n);` | Allocate a vector to hold the input values. |
| 18 | `for (int i = 0; i < n; i++)` | Read each element into the vector. |
| 21 | `printEvenIndices(a, n - 1);` | Start the recursive printing from the last element. |
| 22 | `cout << endl;` | Output a newline to terminate the result. |
| 25 | `return 0;` | Return success status. |

**Explanation**

Purpose: Prints the elements at even indices of a vector in descending order.  
Input: `vector<long long>& a` – the source vector; `int index` – the current position to examine.  
Output: Writes the selected elements to `std::cout`, each followed by a space; returns `int` to match `main` signature.  
Algorithm: Recursively traverse the vector from `index` down to 0, skipping odd indices. When an even index is reached, output the element. The recursion stops when `index` becomes negative.

---

## dataset.jsonl#65 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    for (int i = n - 1; i >= 0; i--)
    {
        if (i % 2 == 0)
            cout << a[i] << " ";
    }

    cout << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int n;` | read number of elements |
| 4 | `cin >> n;` | reads the size of the input vector |
| 6 | `vector<long long> a(n);` | allocate storage for n long long integers |
| 7 | `for (int i = 0; i < n; i++)` | read each element; assumes each element fits in a long long |
| 10 | `for (int i = n - 1; i >= 0; i--)` | iterate from the last element upwards |
| 11 | `if (i % 2 == 0)` | output only elements at even indices (0‑based) |
| 13 | `cout << endl;` | terminate output with a newline |

**Explanation**

Purpose: Prints the elements of a vector that appear at even indices in ascending order.  
Input: An integer n followed by n long‑long integers read from standard input.  
Output: Writes the selected elements to standard output, each followed by a space, then a newline.  
Algorithm: Read the vector, then iterate from the last element backwards, outputting the element only if its index is even. The loop runs in O(n) time and O(1) extra space.

---

## dataset.jsonl#66 — recursive

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printStars(int count)
{
    if (count == 0)
        return;

    cout << "*";
    printStars(count - 1);
}

void printPyramid(int n, int current = 1)
{
    if (current > n)
        return;

    printStars(current);
    cout << endl;
    printPyramid(n, current + 1);
}

int main()
{
    int n;
    cin >> n;

    printPyramid(n);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (count == 0)` | Base case: stop recursion when the required number of stars is zero |
| 6 | `cout << "*";` | Output the current star character |
| 7 | `printStars(count - 1);` | Recurse with one fewer star to build the next row |
| 11 | `if (current > n)` | Stop recursion when the current row exceeds the desired height |
| 14 | `printStars(current);` | Output the current row of stars |
| 15 | `cout << endl;` | Move to the next line after printing the row |
| 16 | `printPyramid(n, current + 1);` | Recursively generate the next row |
| 20 | `cin >> n;` | Read the desired height of the pyramid from standard input |

**Explanation**

Purpose: Prints a right‑angled triangle of stars with height n.  
Input: An integer n representing the number of rows (including the base).  
Output: Writes the pattern to standard output; no return value.  
Algorithm: Uses two recursive functions: `printStars` prints a single row of stars, and `printPyramid` prints the first row, then recursively prints each subsequent row until it reaches the base. The recursion stops when the current row index exceeds n.

---

## dataset.jsonl#66 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    for (int i = 1; i <= n; i++)
    {
        for (int j = 1; j <= i; j++)
        {
            cout << "*";
        }
        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | read the number of rows from standard input |
| 5 | `for (int i = 1; i <= n; i++)` | iterate over each row |
| 6 | `for (int j = 1; j <= i; j++)` | print i stars per row |
| 8 | `cout << endl;` | finish the current row with a newline |
| 11 | `return 0;` | success exit code |

**Explanation**

Purpose: Prints a right‑angled triangle of asterisks with height equal to the input integer.  
Input: An integer `n` read from standard input.  
Output: Writes `n` lines to standard output, each containing `i` asterisks followed by a newline.  
Algorithm: The outer loop iterates from 1 to `n`, the inner loop prints `i` asterisks per line, and each iteration ends with a newline. The loop naturally handles the degenerate case where `n` is zero.

---

## dataset.jsonl#67 — recursive

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

void printStars(int n)
{
    if (n == 0)
        return;
    cout << "*";
    printStars(n - 1);
}

void printPyramid(int n)
{
    if (n == 0)
        return;
    printStars(n);
    cout << endl;
    printPyramid(n - 1);
}

int main()
{
    int n;
    cin >> n;
    printPyramid(n);
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: stop recursion when n reaches zero |
| 4 | `return;` | No stars to output for n == 0 |
| 5 | `cout << "*";` | Output the current star |
| 6 | `printStars(n - 1);` | Recurse with n decremented, building the left side of the pyramid |
| 9 | `if (n == 0)` | Base case: stop recursion when n reaches zero |
| 10 | `printStars(n);` | Output the current level of stars |
| 11 | `cout << endl;` | Move to the next line for the next level |
| 12 | `printPyramid(n - 1);` | Recurse with n decremented, building the right side of the pyramid |
| 15 | `cin >> n;` | Read the desired height from the user |
| 16 | `printPyramid(n);` | Start the recursive pyramid generation |

**Explanation**

Purpose: Prints a right‑angled triangle consisting of asterisks.  
Input: An integer n – the number of rows (including the base) to print.  
Output: Writes the pattern to standard output, each row followed by a newline.  
Algorithm: Uses two recursive helper functions: printStars prints n asterisks, and printPyramid prints n asterisks followed by a newline, then recursively decrements n until it reaches zero.

---

## dataset.jsonl#67 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    for (int i = n; i >= 1; i--)
    {
        for (int j = 1; j <= i; j++)
            cout << "*";
        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | read the number of rows from standard input |
| 5 | `for (int i = n; i >= 1; i--)` | iterate from n down to 1, printing each row |
| 6 | `for (int j = 1; j <= i; j++)` | print i stars per row |
| 8 | `cout << endl;` | finish the current row with a newline |
| 11 | `return 0;` | success exit code |

**Explanation**

Purpose: Prints a right‑angled triangle of asterisks with height equal to the input integer.  
Input: An integer `n` read from standard input.  
Output: Writes `n` lines to standard output, each containing `i` asterisks followed by a newline.  
Algorithm: The outer loop iterates from `n` down to 1, decrementing each iteration. For each iteration, the inner loop prints `i` asterisks, then outputs a newline. The loop naturally produces a descending triangular pattern.

---

## dataset.jsonl#68 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

bool isVowel(char c)
{
    return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
           c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U';
}

int countVowels(const string& s, int index)
{
    if (index == s.length())
        return 0;

    return isVowel(s[index]) + countVowels(s, index + 1);
}

int main()
{
    string s;
    getline(cin, s);
    cout << countVowels(s, 0) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `return c == 'a' \|\| c == 'e' \|\| c == 'i' \|\| c == 'o' \|\| c == 'u' \|\|` | Returns true if the character is a lowercase vowel. |
| 4 | `c == 'A' \|\| c == 'E' \|\| c == 'I' \|\| c == 'O' \|\| c == 'U';` | Returns true if the character is an uppercase vowel. |
| 8 | `if (index == s.length())` | Base case: when the current position is past the string length, there are no vowels left. |
| 11 | `return isVowel(s[index]) + countVowels(s, index + 1);` | Recursively count vowels in the substring starting at index, adding the current character if it is a vowel. |
| 15 | `string s;` | Read the entire input line into a string. |
| 16 | `getline(cin, s);` | Note: getline may read an empty line if the input ends with a newline. |
| 17 | `cout << countVowels(s, 0) << endl;` | Output the total number of vowels in the input string. |

**Explanation**

Purpose: Counts the number of vowels in a given string starting from a specified index.  
Input: `s` – the string to examine; `index` – the zero‑based position in `s` from which to start counting.  
Output: An `int` representing the total count of vowels in `s` from `index` to the end.  
Algorithm: Recursively traverse the string, using `isVowel` to test each character. When the end of the string is reached, return 0. Otherwise, add 1 if the character is a vowel and recurse on the next position.

---

## dataset.jsonl#68 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <string>
using namespace std;

bool isVowel(char c)
{
    return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
           c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U';
}

int main()
{
    string s;
    getline(cin, s);

    int count = 0;
    for (char c : s)
    {
        if (isVowel(c))
            count++;
    }

    cout << count << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `return c == 'a' \|\| c == 'e' \|\| c == 'i' \|\| c == 'o' \|\| c == 'u' \|\|` | Returns true if the character is a lowercase vowel (a,e,i,o,u). |
| 4 | `c == 'A' \|\| c == 'E' \|\| c == 'I' \|\| c == 'O' \|\| c == 'U';` | or an uppercase vowel (A,E,I,O,U). |
| 10 | `getline(cin, s);` | Read the whole line from standard input into a string. |
| 12 | `for (char c : s)` | Count how many characters in the string are vowels. |
| 14 | `count++;` | Increment the vowel counter for each matching character. |
| 17 | `cout << count << endl;` | Output the total vowel count followed by a newline. |

**Explanation**

Purpose: Counts the number of vowels in a given string.  
Input: A std::string containing the text to analyze.  
Output: An int representing the total count of vowels in the string.  
Algorithm: Reads the whole line from standard input, then iterates over each character, using a helper function to test for vowel membership. The count is incremented for each vowel encountered.

---

## dataset.jsonl#69 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long factorial(int n)
{
    if (n <= 1)
        return 1;

    return n * factorial(n - 1);
}

int main()
{
    int n;
    cin >> n;
    cout << factorial(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n <= 1)` | Base case: for n ≤ 1 the factorial is defined as 1 |
| 5 | `return n * factorial(n - 1);` | Recursive step: multiply n by the factorial of (n‑1) |
| 9 | `cin >> n;` | Read input integer; assumes the caller guarantees a valid n |
| 10 | `cout << factorial(n) << endl;` | Output the computed factorial; no error handling for invalid inputs |

**Explanation**

Purpose: Computes the factorial of a non‑negative integer.  
Input: An integer n (expected to be ≥ 0).  
Output: A long long containing n! (or 1 for n ≤ 1).  
Algorithm: Uses a recursive definition of factorial: if n ≤ 1 it returns 1, otherwise it multiplies n by the factorial of n‑1. The recursion naturally yields the correct result for n ≥ 2.

---

## dataset.jsonl#69 — iterative

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    long long result = 1;
    for (int i = 2; i <= n; i++)
        result *= i;

    cout << result << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | Read the input integer; assumes the caller guarantees a valid non‑negative value. |
| 5 | `long long result = 1;` | Initialize the product accumulator with 1 (factorial of 0). |
| 6 | `for (int i = 2; i <= n; i++)` | Iterate from 2 up to n, multiplying the accumulator by each integer. |
| 8 | `cout << result << endl;` | Output the computed factorial; assumes the accumulator fits in a long long. |

**Explanation**

Purpose: Compute the factorial of a non‑negative integer n and output it.  
Input: Reads an integer n from standard input.  
Output: Prints the factorial of n to standard output followed by a newline.  
Algorithm: Initializes result to 1, then iteratively multiplies result by each integer i from 2 to n, accumulating the product. Finally, prints the final result. Edge cases such as n ≤ 0 are not handled.

---

## dataset.jsonl#70 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

long long findMax(const vector<long long>& a, int n)
{
    if (n == 1)
        return a[0];

    return max(a[n - 1], findMax(a, n - 1));
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    cout << findMax(a, n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return max(a[n - 1], findMax(a, n - 1));` | Recursively compute the maximum of the sub‑array a[0..n‑1]. Base case: when only one element remains, it is the maximum. |
| 14 | `cin >> n;` | Read the number of elements from standard input. |
| 15 | `vector<long long> a(n);` | Allocate a vector to hold the input values. |
| 16 | `for (int i = 0; i < n; i++)` | Read each element into the vector. |
| 18 | `cout << findMax(a, n) << endl;` | Output the maximum value found by the recursive helper. |

**Explanation**

Purpose: Compute the maximum element in a vector of long long integers.  
Input: `const vector<long long>& a` – the vector to examine; `int n` – number of elements to consider (typically `a.size()`).  
Output: `long long` – the largest value among the first `n` elements.  
Algorithm: If `n` is 1, return the single element. Otherwise, recursively find the maximum of the last element and the maximum of the rest of the vector, then return the larger of the two. The recursion stops when only one element remains.

---

## dataset.jsonl#70 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    long long maximum = a[0];

    for (int i = 1; i < n; i++)
        maximum = max(maximum, a[i]);

    cout << maximum << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 4 | `cin >> n;` | read number of elements |
| 6 | `for (int i = 0; i < n; i++)` | read all elements; assumes n > 0 |
| 10 | `for (int i = 1; i < n; i++)` | scan from the second element to find the maximum |
| 11 | `maximum = max(maximum, a[i]);` | update maximum with the larger of the current maximum and the next element |
| 13 | `cout << maximum << endl;` | output the largest value |

**Explanation**

Purpose: Find and print the largest integer in a sequence read from standard input.  
Input: An integer n followed by n long‑long integers.  
Output: Prints the maximum value as a long long to standard output.  
Algorithm: Read the first element as the initial maximum, then iterate the remaining elements, updating the maximum whenever a larger value is encountered. Finally, output the maximum.

---

## dataset.jsonl#71 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

long long sum(const vector<long long>& a, int n)
{
    if (n == 0)
        return 0;

    return a[n - 1] + sum(a, n - 1);
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    cout << sum(a, n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 0)` | Base case: when n is zero, the sum is zero. |
| 5 | `return a[n - 1] + sum(a, n - 1);` | Recursive step: add the last element of the vector to the sum of the rest of the vector. |
| 9 | `cin >> n;` | Read the number of elements from standard input. |
| 10 | `vector<long long> a(n);` | Allocate a vector to hold the input values. |
| 11 | `for (int i = 0; i < n; i++)` | Read each element of the vector from standard input. |
| 13 | `cout << sum(a, n) << endl;` | Compute the sum of the vector elements and output it. |

**Explanation**

Purpose: Compute the sum of the first n elements of a vector of long long integers.  
Input: `n` – size of the vector; `a` – vector of long long values.  
Output: Sum of the first n elements as a long long.  
Algorithm: Recursively access the last element of the vector and add it to the sum of the rest of the vector, terminating when n reaches zero. The recursion depth is O(n) and the total time is O(n).

---

## dataset.jsonl#71 — iterative

- anchors: 1 exact, 6 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    long long total = 0;

    for (int i = 0; i < n; i++)
        total += a[i];

    cout << total << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int n;` | read number of elements |
| 4 | `cin >> n;` | reads the first integer – assumes it is the size of the vector |
| 6 | `vector<long long> a(n);` | allocate vector of long long to hold the input values |
| 7 | `for (int i = 0; i < n; i++)` | read each element; assumes the input is space‑separated integers |
| 10 | `long long total = 0;` | accumulate sum of all elements |
| 11 | `for (int i = 0; i < n; i++)` | sum the elements; assumes the vector is non‑empty |
| 14 | `cout << total << endl;` | output the total sum |

**Explanation**

Purpose: Compute the sum of the first n integers read from standard input.  
Input: n – number of integers to read; a vector of long long holds the integers.  
Output: Prints the total sum to standard output.  
Algorithm: Read n integers into a vector, then iterate over the vector, adding each element to a running total, finally output the total. Edge cases such as n ≤ 0 or overflow are not handled.

---

## dataset.jsonl#72 — recursive

- anchors: 1 exact, 5 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

long long suffixSum(const vector<long long>& a, int index, int m)
{
    if (m == 0)
        return 0;

    return a[index] + suffixSum(a, index - 1, m - 1);
}

int main()
{
    int n, m;
    cin >> n >> m;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    cout << suffixSum(a, n - 1, m) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return a[index] + suffixSum(a, index - 1, m - 1);` | Base case: when m reaches zero, the recursion stops. |
| 11 | `return 0;` | If m is zero, the sum of the suffix starting at index is zero. |
| 13 | `cin >> n >> m;` | Read the number of elements and the required suffix length. |
| 14 | `vector<long long> a(n);` | Allocate a vector to hold the input sequence. |
| 15 | `for (int i = 0; i < n; i++)` | Read each element of the sequence. |
| 17 | `cout << suffixSum(a, n - 1, m) << endl;` | Compute the suffix sum starting at the last element and output it. |

**Explanation**

Purpose: Compute the sum of the last m elements of a vector using a recursive suffix‑sum approach.  
Input: `n` – number of elements; `m` – number of elements to sum from the end; `a` – vector of long long integers.  
Output: `long long` – the sum of the last m elements.  
Algorithm: The function recursively adds the current element `a[index]` to the result of a call to itself with `index‑1` and `m‑1`. The recursion stops when `m` reaches zero, yielding the desired sum. The main routine reads the vector and prints the result.

---

## dataset.jsonl#72 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int n, m;
    cin >> n >> m;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    long long sum = 0;

    for (int i = n - m; i < n; i++)
        sum += a[i];

    cout << sum << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 4 | `cin >> n >> m;` | read size of array and number of elements to sum |
| 6 | `vector<long long> a(n);` | allocate storage for n long long integers |
| 7 | `for (int i = 0; i < n; i++)` | read the actual data; assumes each line contains exactly one integer |
| 10 | `long long sum = 0;` | accumulator for the selected elements |
| 11 | `for (int i = n - m; i < n; i++)` | start at the last m elements; assumes m ≤ n |
| 12 | `sum += a[i];` | accumulate the m largest values |
| 14 | `cout << sum << endl;` | output the sum; assumes the input is non‑negative |

**Explanation**

Purpose: Compute the sum of the last m elements of a vector of long long integers.  
Input: Two integers n (number of elements) and m (number of elements to sum from the end).  
Output: Prints the computed sum to standard output.  
Algorithm: Read the vector, then iterate over the range [n‑m, n‑1] and accumulate the values. The loop runs in O(m) time and O(1) extra space.

---

## dataset.jsonl#73 — recursive

- anchors: 1 exact, 10 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

void sumMatrix(const vector<vector<long long>>& A, const vector<vector<long long>>& B, int r, int c, int R, int C)
{
    if (r == R)
        return;

    cout << A[r][c] + B[r][c];

    if (c == C - 1)
    {
        cout << endl;
        sumMatrix(A, B, r + 1, 0, R, C);
    }
    else
    {
        cout << " ";
        sumMatrix(A, B, r, c + 1, R, C);
    }
}

int main()
{
    int R, C;
    cin >> R >> C;

    vector<vector<long long>> A(R, vector<long long>(C));
    vector<vector<long long>> B(R, vector<long long>(C));

    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++)
            cin >> A[i][j];

    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++)
            cin >> B[i][j];

    sumMatrix(A, B, 0, 0, R, C);

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cout << A[r][c] + B[r][c];` | Output the element of the first matrix and the corresponding element of the second matrix. |
| 11 | `if (c == C - 1)` | If we are at the last column of the current row, start a new line. |
| 12 | `cout << endl;` | Output a newline to separate rows. |
| 13 | `sumMatrix(A, B, r + 1, 0, R, C);` | Move to the next row and start a fresh column. |
| 14 | `else` | Otherwise, continue in the same column. |
| 15 | `cout << " ";` | Output a space to separate elements within the same row. |
| 16 | `sumMatrix(A, B, r, c + 1, R, C);` | Move to the next column. |
| 20 | `cin >> R >> C;` | Read the dimensions of the matrices. |
| 22 | `for (int i = 0; i < R; i++)` | Read the first matrix. |
| 24 | `for (int i = 0; i < R; i++)` | Read the second matrix. |
| 26 | `sumMatrix(A, B, 0, 0, R, C);` | Compute and print the element‑wise sum of the two matrices. |

**Explanation**

Purpose: Compute the element‑wise sum of two square matrices and output the result in a formatted row‑column layout.  
Input: Two square matrices A and B of size R×C, read from standard input.  
Output: Prints the sum of each element of A and B, separated by spaces and terminated by a newline for each row.  
Algorithm: Recursively traverse the matrices, adding corresponding elements and outputting them. When a column reaches the last row, start a new line; otherwise output a space and continue to the next column.

---

## dataset.jsonl#73 — iterative

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int R, C;
    cin >> R >> C;

    vector<vector<long long>> A(R, vector<long long>(C));
    vector<vector<long long>> B(R, vector<long long>(C));

    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++)
            cin >> A[i][j];

    for (int i = 0; i < R; i++)
        for (int j = 0; j < C; j++)
            cin >> B[i][j];

    for (int i = 0; i < R; i++)
    {
        for (int j = 0; j < C; j++)
        {
            cout << A[i][j] + B[i][j];
            if (j < C - 1)
                cout << " ";
        }
        cout << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = 0; i < R; i++)` | Read the first matrix row‑wise |
| 14 | `for (int i = 0; i < R; i++)` | Read the second matrix row‑wise |
| 18 | `for (int i = 0; i < R; i++)` | Perform element‑wise addition and output each row |
| 20 | `cout << A[i][j] + B[i][j];` | Output the sum of the two matrices |
| 21 | `if (j < C - 1)` | Print a space after the first element of each row except the last |
| 22 | `cout << " ";` | Note: the original code used a literal string " " which is not a valid character literal; it should be a single space character |
| 23 | `}` | Note: the original code used a literal string " " which is not a valid character literal; it should be a single space character |
| 24 | `}` | Note: the original code used a literal string " " which is not a valid character literal; it should be a single space character |
| 25 | `cout << endl;` | Output a newline after each row |

**Explanation**

Purpose: Adds two square matrices element‑wise and prints the result.  
Input: Two integers R and C defining the matrix dimensions, followed by R*C long long values for each matrix.  
Output: Prints R*C long long values representing the element‑wise sum, each followed by a space except the last row.  
Algorithm: Reads the matrices, then iterates over each row and column, adding corresponding entries from A and B, outputting the sum followed by a space, and finally a newline.

---

## dataset.jsonl#74 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long fibonacci(int n)
{
    if (n == 1)
        return 0;
    if (n == 2)
        return 1;

    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main()
{
    int n;
    cin >> n;

    cout << fibonacci(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 1)` | Base case: the first Fibonacci number is defined as 0. |
| 4 | `if (n == 2)` | Base case: the second Fibonacci number is defined as 1. |
| 5 | `return fibonacci(n - 1) + fibonacci(n - 2);` | Recursive definition: each subsequent number is the sum of the two preceding ones. |
| 9 | `cout << fibonacci(n) << endl;` | Output the n‑th Fibonacci number. |

**Explanation**

Purpose: Computes the n‑th Fibonacci number using a naive recursive definition.  
Input: An integer n representing the index of the desired Fibonacci term.  
Output: A long long containing the Fibonacci value for n.  
Algorithm: Handles the base cases n = 1 and n = 2 directly. For larger n it recursively calls itself with n‑1 and n‑2, accumulating the sum. The recursion naturally leads to exponential time complexity.

---

## dataset.jsonl#74 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n;
    cin >> n;

    long long a = 0, b = 1;

    for (int i = 1; i < n; i++)
    {
        long long c = a + b;
        a = b;
        b = c;
    }

    cout << a << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | read the number of Fibonacci terms to generate |
| 5 | `long long a = 0, b = 1;` | initialize the first two Fibonacci numbers |
| 7 | `for (int i = 1; i < n; i++)` | generate the next n-1 terms using the recurrence a = b, b = c |
| 10 | `a = b;` | shift the sequence forward |
| 11 | `b = c;` | update the current term |
| 13 | `cout << a << endl;` | output the n‑th Fibonacci number |

**Explanation**

Purpose: Prints the nth Fibonacci number.  
Input: An integer n – the index of the desired Fibonacci term.  
Output: Prints the integer value of F(n) to standard output.  
Algorithm: Initializes two variables to the first two Fibonacci numbers, then iteratively adds them to produce the next term until the nth term is reached. Finally, it outputs the last computed term.

---

## dataset.jsonl#75 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long log2Floor(unsigned long long n)
{
    if (n < 2)
        return 0;

    return 1 + log2Floor(n / 2);
}

int main()
{
    unsigned long long n;
    cin >> n;

    cout << log2Floor(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n < 2)` | Base case: for n < 2 the result is 0 because log2 of any number < 2 is 0. |
| 6 | `return 1 + log2Floor(n / 2);` | Recursive step: compute log2 of the halved value, then add 1 to account for the current exponent. |
| 10 | `cin >> n;` | Read the input number from standard input. |
| 11 | `cout << log2Floor(n) << endl;` | Output the floor of the base-2 logarithm of n. |

**Explanation**

Purpose: Compute the greatest integer k such that 2^k ≤ n.  
Input: An unsigned long long n – the number whose base‑2 logarithm is required.  
Output: An int representing the floor of log2(n).  
Algorithm: Uses a recursive helper that repeatedly divides n by 2, counting each division step. The base case returns 0 for n < 2. The main function reads n from stdin, calls the helper, and prints the result.

---

## dataset.jsonl#75 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    unsigned long long n;
    cin >> n;

    long long answer = 0;

    while (n >= 2)
    {
        n /= 2;
        answer++;
    }

    cout << answer << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `unsigned long long n;` | read the input as a 64‑bit unsigned integer |
| 4 | `cin >> n;` | note: if the input is larger than 64‑bit unsigned, the value is truncated |
| 6 | `long long answer = 0;` | count how many times we can divide by 2 |
| 7 | `while (n >= 2)` | loop while the number remains at least 2 |
| 8 | `n /= 2;` | reduce the number by halving each iteration |
| 9 | `answer++;` | increment the count for each division |
| 12 | `cout << answer << endl;` | output the total count of divisions |

**Explanation**

Purpose: Counts how many times a number can be halved before it becomes less than or equal to 2.  
Input: A single unsigned 64‑bit integer read from standard input.  
Output: Prints an integer representing the count to standard output.  
Algorithm: Repeatedly divide the input by 2, incrementing a counter each time, until the value drops below 2. The final counter value is printed.

---

## dataset.jsonl#76 — recursive

- anchors: 1 exact, 5 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long sequenceLength(long long n)
{
    if (n == 1)
        return 1;

    if (n % 2 == 0)
        return 1 + sequenceLength(n / 2);

    return 1 + sequenceLength(3 * n + 1);
}

int main()
{
    long long n;
    cin >> n;

    cout << sequenceLength(n) << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 1)` | Base case: the sequence starting with 1 has length 1. |
| 6 | `if (n % 2 == 0)` | If n is even, the next term is n/2, which reduces the problem size by half. |
| 9 | `return 1 + sequenceLength(n / 2);` | Recursively compute the length of the reduced sequence. |
| 12 | `return 1 + sequenceLength(3 * n + 1);` | If n is odd, the next term is 3*n+1, which grows the sequence exponentially. |
| 15 | `cin >> n;` | Read the starting number from standard input. |
| 17 | `cout << sequenceLength(n) << endl;` | Output the computed sequence length. |

**Explanation**

Purpose: Computes the length of the Collatz sequence starting from n.  
Input: long long n – the initial term of the sequence.  
Output: long long – the total number of terms in the sequence.  
Algorithm: Uses a recursive helper that checks the parity of n; if even it returns 1 plus the length of the reduced sequence, otherwise it returns 1 plus the length of the sequence obtained by applying the Collatz rule (3n+1). The recursion terminates when n reaches 1.

---

## dataset.jsonl#76 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    long long n;
    cin >> n;

    long long length = 1;

    while (n != 1)
    {
        if (n % 2 == 0)
            n /= 2;
        else
            n = 3 * n + 1;

        length++;
    }

    cout << length << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> n;` | read the starting integer from standard input |
| 5 | `long long length = 1;` | initialize length counter to 1 (the original number) |
| 7 | `while (n != 1)` | continue until the process reaches 1 |
| 8 | `if (n % 2 == 0)` | even case: halve the number |
| 11 | `n = 3 * n + 1;` | odd case: apply the Collatz transformation |
| 13 | `length++;` | increment the length counter for each iteration |
| 16 | `cout << length << endl;` | output the total number of iterations |

**Explanation**

Purpose: Compute the length of the Collatz sequence starting from n.  
Input: A single long long integer n read from standard input.  
Output: Prints the number of steps (length) to standard output.  
Algorithm: Repeatedly apply the Collatz rule (n → n/2 if even, n → 3n+1 otherwise) while n is not 1, incrementing a counter each iteration. The final counter value is printed.

---

## dataset.jsonl#77 — recursive

- anchors: 1 exact, 6 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

bool isPalindrome(const vector<long long>& a, int left, int right)
{
    if (left >= right)
        return true;

    if (a[left] != a[right])
        return false;

    return isPalindrome(a, left + 1, right - 1);
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    if (isPalindrome(a, 0, n - 1))
        cout << "YES" << endl;
    else
        cout << "NO" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (left >= right)` | Base case: when the subarray has length 0 or 1, it is trivially a palindrome. |
| 12 | `if (a[left] != a[right])` | If the outermost elements differ, the whole array cannot be a palindrome. |
| 14 | `return isPalindrome(a, left + 1, right - 1);` | Recursively check the inner segment, skipping the outermost elements. |
| 20 | `cin >> n;` | Read the number of elements; assumes the input fits in an int. |
| 22 | `for (int i = 0; i < n; i++)` | Read the array elements; assumes each element fits in a long long. |
| 24 | `if (isPalindrome(a, 0, n - 1))` | Determine if the entire array is a palindrome. |
| 25 | `cout << "YES" << endl;` | Output the result. |

**Explanation**

Purpose: Determines whether a given sequence of long long integers is a palindrome.  
Input: `n` (size of the vector) and `a` (vector of long long integers).  
Output: Prints "YES" if `a` is a palindrome, otherwise "NO".  
Algorithm: Uses a recursive helper that compares the first and last elements, then recursively checks the inner segment. The recursion stops when the indices cross, returning true if all pairs match.

---

## dataset.jsonl#77 — iterative

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    bool palindrome = true;

    for (int i = 0; i < n / 2; i++)
    {
        if (a[i] != a[n - 1 - i])
        {
            palindrome = false;
            break;
        }
    }

    if (palindrome)
        cout << "YES" << endl;
    else
        cout << "NO" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int n;` | read length of the sequence |
| 4 | `cin >> n;` | note: assumes n is non‑negative; otherwise undefined behavior |
| 6 | `vector<long long> a(n);` | allocate storage for the sequence |
| 7 | `for (int i = 0; i < n; i++)` | read each element; assumes cin is a valid stream |
| 10 | `bool palindrome = true;` | assume the sequence is a palindrome initially |
| 11 | `for (int i = 0; i < n / 2; i++)` | compare mirrored positions; stop early on first mismatch |
| 12 | `if (a[i] != a[n - 1 - i])` | mismatch found → not a palindrome |
| 14 | `palindrome = false;` | mark failure |
| 15 | `break;` | no need to check further |
| 18 | `if (palindrome)` | output result based on palindrome flag |

**Explanation**

Purpose: Determines whether a sequence of integers reads the same forwards and backwards.  
Input: Reads an integer n followed by n long‑long integers from standard input.  
Output: Prints "YES" if the sequence is a palindrome, otherwise "NO".  
Algorithm: Compares each element with its symmetric counterpart from the end, stopping at the midpoint; if any pair differs, the sequence is not a palindrome. The final result is printed.

---

## dataset.jsonl#78 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <iomanip>
using namespace std;

double sum(const vector<long long>& a, int n)
{
    if (n == 0)
        return 0;

    return a[n - 1] + sum(a, n - 1);
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    double average = sum(a, n) / n;

    cout << fixed << setprecision(6) << average << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return a[n - 1] + sum(a, n - 1);` | Recursively compute the sum of the first n elements. Base case: when n == 0, the sum is 0. |
| 14 | `cin >> n;` | Read the number of elements from standard input. |
| 15 | `vector<long long> a(n);` | Allocate a vector to hold the input values. |
| 16 | `for (int i = 0; i < n; i++)` | Read each element; assumes the input contains exactly n integers. |
| 19 | `cout << fixed << setprecision(6) << average << endl;` | Output the average rounded to 6 decimal places. |

**Explanation**

Purpose: Compute the arithmetic mean of the first n elements of a vector of long long integers.  
Input: n – size of the vector; a – vector of long long integers.  
Output: double – the average value, rounded to six decimal places.  
Algorithm: Recursively sum the elements from index 0 to n‑1, then divide by n. The recursion stops when n reaches zero, yielding 0, which is handled gracefully.

---

## dataset.jsonl#78 — iterative

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <iomanip>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);
    long long total = 0;

    for (int i = 0; i < n; i++)
    {
        cin >> a[i];
        total += a[i];
    }

    double average = (double)total / n;

    cout << fixed << setprecision(6) << average << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `cin >> a[i];` | read the i‑th element; assumes the input is formatted correctly |
| 11 | `total += a[i];` | accumulate sum of all elements |
| 13 | `double average = (double)total / n;` | compute average as double to avoid integer truncation |
| 14 | `cout << fixed << setprecision(6) << average << endl;` | output average with 6 decimal places; fixed‑point avoids floating‑point rounding |

**Explanation**

Purpose: Compute and output the arithmetic mean of n integers read from standard input.  
Input: n – number of integers to read; each integer follows on a separate line.  
Output: Prints a double‑precision floating‑point average rounded to six decimal places.  
Algorithm: Read n integers into a vector, accumulate their sum, divide by n to obtain the average, and output the result. Edge cases such as n ≤ 0 or no input are not handled.

---

## dataset.jsonl#79 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long combination(int n, int r)
{
    if (r == 0 || r == n)
        return 1;

    return combination(n - 1, r - 1) + combination(n - 1, r);
}

int main()
{
    int n, r;
    cin >> n >> r;

    if (r > n)
        cout << 0 << endl;
    else
        cout << combination(n, r) << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (r == 0 \|\| r == n)` | Base case: C(n,0) and C(n,n) are defined as 1 |
| 6 | `return combination(n - 1, r - 1) + combination(n - 1, r);` | Recursive formula: C(n,r) = C(n-1,r-1) + C(n-1,r) |
| 10 | `cin >> n >> r;` | Read input values; assumes they are non‑negative |
| 11 | `if (r > n)` | If r exceeds n, the combinatorial result is zero |
| 12 | `cout << 0 << endl;` | Output 0 for invalid input |
| 13 | `else` | Otherwise compute and output the combination |
| 16 | `return 0;` | Return success status |

**Explanation**

Purpose: Compute the binomial coefficient C(n, r) using recursion.  
Input: Two integers n and r representing the size and position of the selection.  
Output: Prints the result as an integer (0 if r > n).  
Algorithm: Uses a recursive helper that returns 1 when r is 0 or n, otherwise sums the two sub‑problems C(n‑1, r‑1) and C(n‑1, r). The main routine reads n and r, checks the inequality, and prints the computed value.

---

## dataset.jsonl#79 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int n, r;
    cin >> n >> r;

    if (r > n)
    {
        cout << 0 << endl;
        return 0;
    }

    long long result = 1;

    for (int i = 1; i <= r; i++)
        result = result * (n - i + 1) / i;

    cout << result << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int n, r;` | Read two integers from standard input: n (total items) and r (items to choose) |
| 5 | `if (r > n)` | If the number of items to choose exceeds the total, the selection is impossible; output 0 and exit |
| 8 | `long long result = 1;` | Initialize the result with 1 (factorial of 0) |
| 9 | `for (int i = 1; i <= r; i++)` | Iterate from 1 to r, multiplying the current result by (n - i + 1) / i to compute the binomial coefficient C(n, r) |
| 11 | `cout << result << endl;` | Output the computed binomial coefficient |

**Explanation**

Purpose: Compute the number of ways to choose r items from n items without repetition.  
Input: Two integers n (the total count) and r (the number of items to choose).  
Output: Prints an integer representing the combinatorial result (0 if r > n).  
Algorithm: If r exceeds n, output 0. Otherwise, iteratively multiply the product of (n‑i+1) by i for i from 1 to r, dividing by i each time to avoid overflow. The final product is the desired result.

---

## dataset.jsonl#80 — recursive

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

long long knapsack(const vector<int>& weight, const vector<int>& value, int index, int capacity)
{
    if (index == 0 || capacity == 0)
        return 0;

    if (weight[index - 1] > capacity)
        return knapsack(weight, value, index - 1, capacity);

    return max(
        knapsack(weight, value, index - 1, capacity),
        value[index - 1] + knapsack(weight, value, index - 1, capacity - weight[index - 1])
    );
}

int main()
{
    int n, W;
    cin >> n >> W;

    vector<int> weight(n), value(n);

    for (int i = 0; i < n; i++)
        cin >> weight[i] >> value[i];

    cout << knapsack(weight, value, n, W) << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (index == 0 \|\| capacity == 0)` | Base case: no items left or no capacity left → optimal value is 0 |
| 12 | `if (weight[index - 1] > capacity)` | Item cannot fit: skip it and recurse with one fewer item |
| 15 | `return max(` | Choose between skipping the item or including it |
| 16 | `knapsack(weight, value, index - 1, capacity),` | skip |
| 17 | `value[index - 1] + knapsack(weight, value, index - 1, capacity - weight[index - 1])` | include |
| 20 | `int n, W;` | Read number of items and knapsack capacity |
| 22 | `vector<int> weight(n), value(n);` | Store weights and values for each item |
| 24 | `for (int i = 0; i < n; i++)` | Read item weights and values from standard input |
| 27 | `cout << knapsack(weight, value, n, W) << endl;` | Output the optimal knapsack value |

**Explanation**

Purpose: Solve the 0/1 knapsack problem using recursion.  
Input: `weight` and `value` vectors of item weights and values, `n` number of items, and `capacity` knapsack capacity.  
Output: Maximum total value achievable within the given capacity.  
Algorithm: Recursively explore all possible inclusion/exclusion of each item, pruning branches where the item cannot fit in the remaining capacity. The base case returns 0 when no items remain or the capacity is zero. The recursive call returns the best value for the current item, either not taken or taken, and the best value for the remaining items.

---

## dataset.jsonl#80 — iterative

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main()
{
    int n, W;
    cin >> n >> W;

    vector<int> weight(n), value(n);
    for (int i = 0; i < n; i++)
        cin >> weight[i] >> value[i];

    vector<vector<long long>> dp(n + 1, vector<long long>(W + 1, 0));

    for (int i = 1; i <= n; i++)
    {
        for (int w = 0; w <= W; w++)
        {
            dp[i][w] = dp[i - 1][w];

            if (weight[i - 1] <= w)
                dp[i][w] = max(dp[i][w], value[i - 1] + dp[i - 1][w - weight[i - 1]]);
        }
    }

    cout << dp[n][W] << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = 0; i < n; i++)` | Read item weights and values from standard input |
| 14 | `vector<vector<long long>> dp(n + 1, vector<long long>(W + 1, 0));` | dp[i][w] stores the maximum value obtainable with the first i items using at most w units of weight |
| 16 | `for (int i = 1; i <= n; i++)` | Iterate over each item; i starts from 1 because dp[0][w] is always 0 |
| 17 | `for (int w = 0; w <= W; w++)` | Iterate over possible weight capacities from 0 to W |
| 18 | `dp[i][w] = dp[i - 1][w];` | Base case: exclude the current item |
| 19 | `if (weight[i - 1] <= w)` | If the current item fits within the remaining weight capacity |
| 20 | `dp[i][w] = max(dp[i][w], value[i - 1] + dp[i - 1][w - weight[i - 1]]);` | Include the current item and update the maximum value |
| 23 | `cout << dp[n][W] << endl;` | Output the optimal total value for the entire knapsack |

**Explanation**

Purpose: Solve the 0/1 knapsack problem to find the maximum total value that can be packed into a knapsack of capacity W.  
Input: n (number of items), W (knapsack capacity), followed by n pairs (weight, value) for each item.  
Output: Prints the maximum achievable value as an integer.  
Algorithm: Dynamic programming builds a table dp[i][w] where dp[i][w] stores the best value achievable with the first i items using up to w units of capacity. For each item, it either skips it or takes it, updating the table accordingly. The final answer is dp[n][W].

---

## dataset.jsonl#81 — recursive

- anchors: 2 exact, 5 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

bool canMake(const vector<long long>& a, int index, long long current, long long target)
{
    if (index == a.size())
        return current == target;

    return canMake(a, index + 1, current + a[index], target) ||
           canMake(a, index + 1, current - a[index], target);
}

int main()
{
    int n;
    long long x;
    cin >> n >> x;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    if (canMake(a, 1, a[0], x))
        cout << "YES" << endl;
    else
        cout << "NO" << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `return canMake(a, index + 1, current + a[index], target) \|\|` | Try adding the current element to the running sum and recurse. |
| 11 | `canMake(a, index + 1, current - a[index], target);` | Try subtracting the current element from the running sum and recurse. |
| 14 | `cin >> n >> x;` | Read the number of elements and the target sum. |
| 16 | `for (int i = 0; i < n; i++)` | Read the actual elements of the array. |
| 19 | `if (canMake(a, 1, a[0], x))` | Start the recursive search from the second element, using the first element as the initial sum. |
| 20 | `cout << "YES" << endl;` | If a valid combination exists, output "YES". |
| 21 | `else` | Otherwise output "NO". |

**Explanation**

Purpose: Determine whether the sum of any subset of a given list of integers equals a target value.  
Input: n (size of the list), x (target sum), a (vector of long long integers).  
Output: Prints "YES" if such a subset exists, otherwise "NO".  
Algorithm: Uses depth‑first recursion with backtracking; at each position it either adds the element to the current sum or subtracts it, exploring both possibilities. The recursion stops when all elements have been considered and the accumulated sum matches the target.

---

## dataset.jsonl#81 — iterative

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
using namespace std;

int main()
{
    int n;
    long long x;
    cin >> n >> x;

    vector<long long> a(n);
    for (int i = 0; i < n; i++)
        cin >> a[i];

    vector<long long> sums;
    sums.push_back(a[0]);

    for (int i = 1; i < n; i++)
    {
        vector<long long> next;
        for (long long sum : sums)
        {
            next.push_back(sum + a[i]);
            next.push_back(sum - a[i]);
        }
        sums = next;
    }

    bool found = false;
    for (long long sum : sums)
    {
        if (sum == x)
        {
            found = true;
            break;
        }
    }

    cout << (found ? "YES" : "NO") << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = 0; i < n; i++)` | Read the first n integers into the array a |
| 14 | `vector<long long> sums;` | Build all possible sums of the first i elements |
| 15 | `sums.push_back(a[0]);` | Initialise sums with the first element |
| 16 | `for (int i = 1; i < n; i++)` | Iterate over each subsequent element |
| 17 | `{` | Compute all sums of the current prefix |
| 18 | `vector<long long> next;` | Store the next set of sums for the current prefix |
| 19 | `for (long long sum : sums)` | For each existing sum, create two new sums: sum + a[i] and sum - a[i] |
| 22 | `sums = next;` | Replace the current sums with the newly computed ones |
| 25 | `for (long long sum : sums)` | Check if any of the sums equals x |
| 26 | `if (sum == x)` | If found, exit early |
| 30 | `cout << (found ? "YES" : "NO") << endl;` | Output the result |

**Explanation**

Purpose: Determine whether any two distinct elements in a sequence sum to a given target.  
Input: n (size of the sequence) and x (target sum).  
Output: Prints "YES" if such a pair exists, otherwise "NO".  
Algorithm: Build a list of all possible sums of the first element with each subsequent element, then repeatedly combine each sum with the next element to generate the next list. Finally, scan the final list for the target sum.

---

## dataset.jsonl#82 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

bool canReach(long long n)
{
    if (n == 1)
        return true;

    if (n % 10 != 0)
        return false;

    return canReach(n / 10) || (n % 20 == 0 && canReach(n / 20));
}

int main()
{
    int t;
    cin >> t;

    while (t--)
    {
        long long n;
        cin >> n;

        cout << (canReach(n) ? "YES" : "NO") << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (n == 1)` | Base case: the smallest reachable number is 1. |
| 5 | `if (n % 10 != 0)` | If the last digit is not 0, the number cannot be reached. |
| 8 | `return canReach(n / 10) \|\| (n % 20 == 0 && canReach(n / 20));` | Recurse on the number without the last digit; if the result is true, we can reach the original number. If the last digit is 0, we also need to check the number after removing the next digit (n % 20 == 0) to ensure we can reach the original number. |
| 12 | `cin >> t;` | Read the number of test cases. |
| 14 | `while (t--)` | Process each test case. |
| 16 | `cout << (canReach(n) ? "YES" : "NO") << endl;` | Output "YES" if the number can be reached, otherwise "NO". |

**Explanation**

Purpose: Determines whether a given positive integer can be reduced to 1 by repeatedly removing its last digit and checking divisibility rules.  
Input: A single integer n (the number to test).  
Output: Prints “YES” if n can be reduced to 1, otherwise “NO”.  
Algorithm: Uses a depth‑first recursion that checks the last digit; if it is 0, it returns true; otherwise it recursively tries removing the last digit and checking divisibility by 20. The recursion stops when n becomes 1.

---

## dataset.jsonl#82 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int t;
    cin >> t;

    while (t--)
    {
        long long n;
        cin >> n;

        while (n % 10 == 0 && n > 1)
        {
            if (n % 20 == 0)
                n /= 20;
            else
                n /= 10;
        }

        cout << (n == 1 ? "YES" : "NO") << endl;
    }

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `cin >> t;` | read number of test cases |
| 5 | `while (t--)` | process each test case |
| 6 | `long long n;` | store the current number |
| 7 | `cin >> n;` | read the number |
| 9 | `while (n % 10 == 0 && n > 1)` | keep dividing by 10 while n is divisible by 10 and n > 1 |
| 10 | `if (n % 20 == 0)` | if n is divisible by 20, divide by 20; otherwise divide by 10 |
| 14 | `cout << (n == 1 ? "YES" : "NO") << endl;` | output "YES" if n becomes 1, otherwise "NO" |

**Explanation**

Purpose: Determines whether each integer n can be reduced to 1 by repeatedly dividing by 10 or 20 while avoiding zero.  
Input: Reads an integer t (number of test cases) followed by t integers n.  
Output: Prints "YES" for each n that can be reduced to 1, otherwise "NO".  
Algorithm: For each n, repeatedly divide by 10 or 20 while n is greater than 1 and not zero. After the loop, output "YES" if n becomes 1, otherwise "NO".

---

## dataset.jsonl#83 — recursive

- anchors: 1 exact, 7 relocated, **0 quoting a line that is not in the file**, of 8
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

long long maxPathSum(const vector<vector<long long>>& a, int i, int j, int n, int m)
{
    if (i == n - 1 && j == m - 1)
        return a[i][j];

    if (i == n - 1)
        return a[i][j] + maxPathSum(a, i, j + 1, n, m);

    if (j == m - 1)
        return a[i][j] + maxPathSum(a, i + 1, j, n, m);

    return a[i][j] + max(maxPathSum(a, i + 1, j, n, m), maxPathSum(a, i, j + 1, n, m));
}

int main()
{
    int n, m;
    cin >> n >> m;

    vector<vector<long long>> a(n, vector<long long>(m));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> a[i][j];

    cout << maxPathSum(a, 0, 0, n, m) << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (i == n - 1 && j == m - 1)` | Base case: reached the bottom‑right cell of the grid. |
| 12 | `if (i == n - 1)` | If we are on the last row, only the right‑most column can be added. |
| 14 | `if (j == m - 1)` | If we are on the last column, only the down‑most row can be added. |
| 16 | `return a[i][j] + max(maxPathSum(a, i + 1, j, n, m), maxPathSum(a, i, j + 1, n, m));` | Otherwise, choose the larger of the two possible paths from the cell below or to the right. |
| 21 | `int n, m;` | Read dimensions of the grid. |
| 23 | `vector<vector<long long>> a(n, vector<long long>(m));` | Allocate the grid; assumes input is correctly formatted. |
| 25 | `for (int i = 0; i < n; i++)` | Read all entries of the grid. |
| 29 | `cout << maxPathSum(a, 0, 0, n, m) << endl;` | Compute and output the maximum path sum from the top‑left to the bottom‑right. |

**Explanation**

Purpose: Compute the maximum sum of a path from top‑left to bottom‑right in a rectangular grid.  
Input: `a` – a 2‑D vector of long long integers representing the grid; `n` and `m` – dimensions of the grid.  
Output: `long long` – the maximum achievable path sum.  
Algorithm: Uses depth‑first recursion with memoization to explore all possible paths, pruning branches that cannot exceed the current cell’s value. The base case returns the cell’s value when it is the destination. The recursive call chooses the larger of the two possible next moves, ensuring the best path is explored.

---

## dataset.jsonl#83 — iterative

- anchors: 1 exact, 11 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main()
{
    int n, m;
    cin >> n >> m;

    vector<vector<long long>> a(n, vector<long long>(m));
    vector<vector<long long>> dp(n, vector<long long>(m));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> a[i][j];

    dp[0][0] = a[0][0];

    for (int i = 1; i < n; i++)
        dp[i][0] = dp[i - 1][0] + a[i][0];

    for (int j = 1; j < m; j++)
        dp[0][j] = dp[0][j - 1] + a[0][j];

    for (int i = 1; i < n; i++)
        for (int j = 1; j < m; j++)
            dp[i][j] = a[i][j] + max(dp[i - 1][j], dp[i][j - 1]);

    cout << dp[n - 1][m - 1] << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `for (int i = 0; i < n; i++)` | Read the matrix dimensions |
| 12 | `vector<vector<long long>> a(n, vector<long long>(m));` | Allocate storage for the original matrix |
| 13 | `vector<vector<long long>> dp(n, vector<long long>(m));` | Allocate storage for the DP table |
| 15 | `for (int i = 0; i < n; i++)` | Read the matrix elements |
| 18 | `dp[0][0] = a[0][0];` | Base case: first element of the matrix |
| 19 | `for (int i = 1; i < n; i++)` | Fill the first row of the DP table |
| 20 | `dp[i][0] = dp[i - 1][0] + a[i][0];` | Accumulate from the left |
| 21 | `for (int j = 1; j < m; j++)` | Fill the first column of the DP table |
| 22 | `dp[0][j] = dp[0][j - 1] + a[0][j];` | Accumulate from the top |
| 23 | `for (int i = 1; i < n; i++)` | Fill the rest of the DP table using the recurrence |
| 24 | `dp[i][j] = a[i][j] + max(dp[i - 1][j], dp[i][j - 1]);` | Choose the larger path from the top or left |
| 26 | `cout << dp[n - 1][m - 1] << endl;` | Output the maximum path sum |

**Explanation**

Purpose: Compute the maximum sum of a path from top‑left to bottom‑right in a 2‑D grid where each cell can be moved to the cell directly below or right.  
Input: Two integers n and m specifying the grid dimensions, followed by n rows of m long long integers representing the grid values.  
Output: Prints the maximum achievable sum as an integer.  
Algorithm: Initialise a DP table with the first cell value. Fill the first row and column with cumulative sums, then iteratively fill the rest using the recurrence dp[i][j] = a[i][j] + max(dp[i‑1][j], dp[i][j‑1]). Finally, output dp[n‑1][m‑1].

---

## dataset.jsonl#84 — recursive

> **names a container the code does not use**

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

  - *container NOT in the code*: The recursion depth grows exponentially, leading to exponential time and stack overflow for large inputs.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

long long ways(int s, int e)
{
    if (s == e)
        return 1;

    if (s > e)
        return 0;

    return ways(s + 1, e) + ways(s + 2, e) + ways(s + 3, e);
}

int main()
{
    int s, e;
    cin >> s >> e;

    cout << ways(s, e) << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `if (s == e)` | Base case: only one way to reach the target when start equals end |
| 5 | `if (s > e)` | If start exceeds end, no valid path exists |
| 7 | `return ways(s + 1, e) + ways(s + 2, e) + ways(s + 3, e);` | Recursive case: count all possible moves from s to e |
| 10 | `int s, e;` | Read start and end positions from standard input |
| 12 | `cout << ways(s, e) << endl;` | Output the total number of ways to reach the target |

**Explanation**

Purpose: Compute the number of ways to reach position e from position s moving one, two, or three steps forward.  
Input: Two integers s and e representing the start and end positions.  
Output: An integer representing the total count of reachable positions.  
Algorithm: Uses a recursive backtracking approach that explores all possible next steps (1, 2, 3) from the current position, terminating when the target is reached or the current position exceeds the target. The recursion depth grows exponentially, leading to exponential time and stack overflow for large inputs.

---

## dataset.jsonl#84 — iterative

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
using namespace std;

int main()
{
    int s, e;
    cin >> s >> e;

    long long dp[16] = {};
    dp[s] = 1;

    for (int i = s + 1; i <= e; i++)
    {
        dp[i] = dp[i - 1];

        if (i - 2 >= s)
            dp[i] += dp[i - 2];

        if (i - 3 >= s)
            dp[i] += dp[i - 3];
    }

    cout << dp[e] << endl;

    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 3 | `int s, e;` | read inclusive start and end indices from standard input |
| 5 | `long long dp[16] = {};` | dp[i] holds the number of ways to reach index i |
| 6 | `dp[s] = 1;` | base case: exactly one way to reach start position |
| 8 | `for (int i = s + 1; i <= e; i++)` | iterate from start+1 to end inclusive |
| 9 | `dp[i] = dp[i - 1];` | each position can be reached from the previous one |
| 10 | `if (i - 2 >= s)` | if we have a second previous position, add its count |
| 11 | `dp[i] += dp[i - 2];` | count ways that skip the second‑last position |
| 12 | `if (i - 3 >= s)` | if we have a third previous position, add its count |
| 13 | `dp[i] += dp[i - 3];` | count ways that skip the third‑last position |
| 15 | `cout << dp[e] << endl;` | output the total number of ways to reach the end |
| 17 | `return 0;` | success |

**Explanation**

Purpose: Compute the number of ways to represent a target sum as a sum of distinct positive integers not exceeding a given limit.  
Input: Two integers `s` and `e` – the inclusive range of numbers to consider.  
Output: An `int` containing the count of such representations.  
Algorithm: Initialise a DP array with a single entry at `s`. Iterate from `s+1` to `e`, propagating the previous entry and optionally adding entries from `s+2` and `s+3` if they fall within the range. Finally, output the value at `e`.

---

## dataset.jsonl#85 — recursive

- anchors: 2 exact, 3 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

void leftMax(const vector<long long>& a, vector<long long>& result, int index)
{
    if (index == a.size())
        return;

    if (index == 0)
        result[index] = a[index];
    else
        result[index] = max(result[index - 1], a[index]);

    leftMax(a, result, index + 1);
}

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n), result(n);

    for (int i = 0; i < n; i++)
        cin >> a[i];

    leftMax(a, result, 0);

    for (int i = 0; i < n; i++)
        cout << result[i] << " ";

    cout << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (index == a.size())` | Base case: when the current index reaches the end of the array, we have processed all elements. |
| 12 | `if (index == 0)` | Handle the first element differently; it is the only element in the prefix. |
| 14 | `result[index] = max(result[index - 1], a[index]);` | Update the result for the current index: either the maximum of the previous prefix or the current element. |
| 16 | `leftMax(a, result, index + 1);` | Recursively compute the maximum for the rest of the array. |
| 20 | `for (int i = 0; i < n; i++)` | Output the computed left‑maxima. |

**Explanation**

Purpose: Compute the maximum value in the prefix of the input array up to each index.  
Input: `a` – a vector of long long integers; `result` – a vector to receive the prefix maximums; `index` – current position in the recursion.  
Output: `result` is populated with the maximum for each prefix; the function returns void.  
Algorithm: Perform a depth‑first search from the start, storing the maximum of the current element and the previously computed maximum for each position. The recursion stops when the end of the array is reached.

---

## dataset.jsonl#85 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main()
{
    int n;
    cin >> n;

    vector<long long> a(n);

    for (int i = 0; i < n; i++)
        cin >> a[i];

    long long maximum = a[0];

    for (int i = 0; i < n; i++)
    {
        maximum = max(maximum, a[i]);
        cout << maximum << " ";
    }

    cout << endl;
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `maximum = max(maximum, a[i]);` | Keep the largest value seen so far; this is the running maximum. |
| 11 | `cout << maximum << " ";` | Output the current maximum followed by a space. |
| 13 | `cout << endl;` | After processing all elements, output a newline to terminate the line. |

**Explanation**

Purpose: Prints the maximum value in a sequence of integers.  
Input: Reads an integer n followed by n long long integers from standard input.  
Output: Writes the maximum value to standard output, each followed by a space, then a newline.  
Algorithm: Stores the first element as the initial maximum, then iterates over the remaining elements, updating the maximum whenever a larger value is encountered. Finally, it prints the maximum followed by a newline.

---
