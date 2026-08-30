# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 20 |
| valid JSON, of output that finished | 20/20 |
| ran past the token budget | 0/20 |
| anchors quoting a real line | 307/328 (94%) |
| named a container the code declares | 11/11 |
| named a container that is not there | 1/20 |
| loops described as recursive | 1/10 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## tree_inorder — recursive

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 13 | `root->left->left = new Node(1);` | left‑left subtree: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right subtree: 6 → 4 → 7 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left subtree: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right subtree: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right subtree: 13 → 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left subtree: 13 |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 22 | `inorder(node->left);` | Visit left subtree first (in‑order traversal) |
| 23 | `cout << node->value << " ";` | Output current node's value |
| 24 | `inorder(node->right);` | Visit right subtree next |
| 27 | `Node* root = sample();` | Build the sample tree |
| 28 | `inorder(sample()); cout << "\n";` | Perform inorder traversal and output result |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr).  
Output: void – writes the inorder sequence to standard output followed by a newline.  
Algorithm: Recursively visits the left subtree, outputs the current node’s value, then visits the right subtree. The recursion stops when a null pointer is encountered.

---

## tree_inorder — iterative

- anchors: 1 exact, 18 relocated, **1 quoting a line that is not in the file**, of 20
- containers in the code: stack

  - *container named*: Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 left subtree: 3 → 1 → 6 → 4 → 7 right subtree: 10 → 13 → 14 left‑left: 1 left‑right: 6 left‑right‑left: 4 left‑right‑right: 7 right‑right: 14 right‑right‑left: 13 Iterative inorder traversal using a stack Continue until all nodes are processed Reach the leftmost node of the current subtree Push the current node onto the stack Move to the left child Pop the node from the stack Remove the node from the stack Output the node's value Move to the right child If the stack is empty, we have processed the entire tree main function Purpose: Perform an in‑order traversal of a binary tree and print node values.
  - *container named*: Algorithm: Initialize a stack and repeatedly push nodes onto it while they have left children, then pop the top node, output its value, and push its right child.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 21 | `stack<Node*> pending;` | Iterative inorder traversal using a stack |
| 22 | `while (node != nullptr \|\| !pending.empty()) {` | Continue until all nodes are processed |
| 23 | `while (node != nullptr) {` | Reach the leftmost node of the current subtree |
| 24 | `pending.push(node);` | Push the current node onto the stack |
| 25 | `node = node->left;` | Move to the left child |
| 27 | `node = pending.top();` | Pop the node from the stack |
| 28 | `pending.pop();` | Remove the node from the stack |
| 29 | `cout << node->value << " ";` | Output the node's value |
| 30 | `node = node->right;` | Move to the right child |
| 32 | `}` | If the stack is empty, we have processed the entire tree |
| 34 | `return 0;` | main function |

**Explanation**

Purpose: Perform an in‑order traversal of a binary tree and print node values.  
Input: Node* root – pointer to the root of the binary tree (sample() builds a predefined tree).  
Output: void – writes the inorder traversal to standard output followed by a newline.  
Algorithm: Initialize a stack and repeatedly push nodes onto it while they have left children, then pop the top node, output its value, and push its right child. Continue until the stack is empty and the current node is null.

---

## tree_preorder — recursive

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 22 | `cout << node->value << " ";` | Visit the current node |
| 23 | `preorder(node->left);` | Recurse left subtree |
| 24 | `preorder(node->right);` | Recurse right subtree |
| 27 | `preorder(sample()); cout << \n; return 0;}` | Print preorder traversal of the constructed tree |

**Explanation**

Purpose: Generates a binary tree and prints its preorder traversal.  
Input: None (main calls sample() to obtain the root).  
Output: Prints the preorder sequence of the tree to std::cout; returns 0.  
Algorithm: sample() constructs a predefined binary tree; preorder() recursively visits nodes in the order root, left, right, terminating when a null pointer is encountered.

---

## tree_preorder — iterative

- anchors: 0 exact, 18 relocated, **4 quoting a line that is not in the file**, of 22
- containers in the code: stack

  - *container named*: Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of 8 right child of 8 left child of 3 right child of 3 left child of 6 right child of 6 right child of 10 left child of 14 Base case: empty subtree → nothing to print Stack for iterative preorder traversal Push the root onto the stack Process nodes until the stack is empty Pop the top node from the stack Remove the node from the stack Print the current node's value Push right child onto the stack (postorder left child is processed later) Push left child onto the stack (postorder right child is processed later) Build the sample tree Perform preorder traversal and output the result Add newline for readability Return success status Purpose: Prints the preorder traversal of a binary tree.
  - *container named*: Algorithm: A stack is used to perform a depth‑first traversal, pushing nodes in reverse preorder order so that the first node popped is the next to be printed.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print |
| 22 | `stack<Node*> pending;` | Stack for iterative preorder traversal |
| 23 | `pending.push(node);` | Push the root onto the stack |
| 24 | `while (!pending.empty()) {` | Process nodes until the stack is empty |
| 25 | `Node* current = pending.top();` | Pop the top node from the stack |
| 26 | `pending.pop();` | Remove the node from the stack |
| 27 | `cout << current->value << " ";` | Print the current node's value |
| 28 | `if (current->right) pending.push(current->right);` | Push right child onto the stack (postorder left child is processed later) |
| 29 | `if (current->left) pending.push(current->left);` | Push left child onto the stack (postorder right child is processed later) |
| 32 | `Node* root = sample();` | Build the sample tree |
| 33 | `preorder(sample());` | Perform preorder traversal and output the result |
| 34 | `cout << "\n";` | Add newline for readability |
| 35 | `return 0;` | Return success status |

**Explanation**

Purpose: Prints the preorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr).  
Output: void – writes the preorder sequence to standard output.  
Algorithm: A stack is used to perform a depth‑first traversal, pushing nodes in reverse preorder order so that the first node popped is the next to be printed. The loop continues until the stack is empty, printing each node’s value and pushing its children (right then left) onto the stack.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 22 | `postorder(node->left);` | Recurse left subtree first |
| 23 | `postorder(node->right);` | Recurse right subtree second |
| 24 | `cout << node->value << " ";` | Output current node's value |
| 27 | `Node* root = sample();` | Build the sample tree |
| 28 | `postorder(sample());` | Perform postorder traversal |
| 29 | `cout << "\n";` | Output newline for clarity |
| 30 | `return 0;` | Success |

**Explanation**

Purpose: Prints the values of a binary tree in postorder traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr).  
Output: void – writes the postorder sequence to standard output followed by a newline.  
Algorithm: Recursively visits left and right subtrees, then outputs the current node's value. The recursion stops when a null pointer is encountered.

---

## tree_postorder — iterative

- anchors: 0 exact, 21 relocated, **1 quoting a line that is not in the file**, of 22
- containers in the code: stack

  - *container named*: Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of 8 right child of 8 left child of 3 right child of 3 left child of 6 right child of 6 right child of 10 left child of 14 Base case: empty subtree → nothing to output pending: nodes to be processed in postorder; output: nodes in reverse postorder push the root onto the pending stack process all nodes in postorder current node to be processed remove from pending stack push to output stack (will be printed later) left child exists → push for later processing right child exists → push for later processing output the nodes in reverse postorder print value followed by a space remove from output stack Invoke postorder traversal and output the result Purpose: Prints the postorder traversal of a binary tree.
  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, pushing nodes onto the stack in postorder order (left, right, then current).

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to output |
| 22 | `stack<Node*> pending, output;` | pending: nodes to be processed in postorder; output: nodes in reverse postorder |
| 23 | `pending.push(node);` | push the root onto the pending stack |
| 24 | `while (!pending.empty()) {` | process all nodes in postorder |
| 25 | `Node* current = pending.top();` | current node to be processed |
| 26 | `pending.pop();` | remove from pending stack |
| 27 | `output.push(current);` | push to output stack (will be printed later) |
| 28 | `if (current->left) pending.push(current->left);` | left child exists → push for later processing |
| 29 | `if (current->right) pending.push(current->right);` | right child exists → push for later processing |
| 32 | `while (!output.empty()) {` | output the nodes in reverse postorder |
| 33 | `cout << output.top()->value << " ";` | print value followed by a space |
| 34 | `output.pop();` | remove from output stack |
| 37 | `postorder(sample()); cout << \n; return 0;` | Invoke postorder traversal and output the result |

**Explanation**

Purpose: Prints the postorder traversal of a binary tree.  
Input: `sample()` returns a pointer to the root of a predefined binary tree.  
Output: Writes the node values in postorder to `std::cout`, each followed by a space.  
Algorithm: Perform a depth‑first traversal using a stack, pushing nodes onto the stack in postorder order (left, right, then current). After the initial traversal, pop nodes from the stack and push them onto an output stack in reverse postorder order (right, left, then current). Finally, output the values from the output stack.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree has height 0 |
| 22 | `int left = height(node->left);` | Recursively compute height of left subtree |
| 23 | `int right = height(node->right);` | Recursively compute height of right subtree |
| 24 | `return 1 + (left > right ? left : right);` | Return 1 plus the larger of the two heights |
| 27 | `cout << height(sample()) << "\n";` | Print the height of the constructed tree |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – the maximum depth of the tree (0 for an empty tree).  
Algorithm: Perform a post‑order traversal, recursively calculating the height of each subtree and returning the larger of the two heights plus one. The recursion stops when a null pointer is encountered.

---

## tree_height — iterative

- anchors: 0 exact, 22 relocated, **1 quoting a line that is not in the file**, of 23
- containers in the code: queue

  - *container named*: Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of 8 right child of 8 left child of 3 right child of 3 left child of 6 right child of 6 right child of 10 left child of 14 Base case: an empty subtree has height 0 BFS traversal queue start BFS from the root counter for the number of levels continue until all levels are processed number of nodes in the current BFS level process each node in the current level front node of the queue remove the front node from the queue enqueue left child if it exists enqueue right child if it exists increment level counter total number of levels in the tree Print the height of the constructed tree Purpose: Compute the maximum number of nodes at any depth in a binary tree.
  - *container named*: Algorithm: Perform a breadth‑first traversal using a queue, counting nodes per level until the queue becomes empty.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: an empty subtree has height 0 |
| 22 | `queue<Node*> level;` | BFS traversal queue |
| 23 | `level.push(node);` | start BFS from the root |
| 24 | `int levels = 0;` | counter for the number of levels |
| 25 | `while (!level.empty()) {` | continue until all levels are processed |
| 26 | `int width = level.size();` | number of nodes in the current BFS level |
| 27 | `for (int i = 0; i < width; i++) {` | process each node in the current level |
| 28 | `Node* current = level.front();` | front node of the queue |
| 29 | `level.pop();` | remove the front node from the queue |
| 30 | `if (current->left) level.push(current->left);` | enqueue left child if it exists |
| 31 | `if (current->right) level.push(current->right);` | enqueue right child if it exists |
| 33 | `levels++;` | increment level counter |
| 36 | `return levels;` | total number of levels in the tree |
| 40 | `cout << height(sample()) << "\n";` | Print the height of the constructed tree |

**Explanation**

Purpose: Compute the maximum number of nodes at any depth in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: int – height of the tree (0 for an empty tree).  
Algorithm: Perform a breadth‑first traversal using a queue, counting nodes per level until the queue becomes empty. Each time the queue size changes, increment the depth counter. The final counter value is the height.

---

## tree_count_leaves — recursive

- anchors: 0 exact, 12 relocated, **1 quoting a line that is not in the file**, of 13
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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no leaves |
| 22 | `if (node->left == nullptr && node->right == nullptr) return 1;` | Leaf node: count it |
| 23 | `return leaves(node->left) + leaves(node->right);` | Recursive sum of left and right subtrees |
| 26 | `cout << leaves(sample()) << "\n";` | Print the number of leaf nodes in the constructed tree |

**Explanation**

Purpose: Count the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes.  
Algorithm: Perform a depth‑first traversal, recursively counting nodes that have both left and right children as leaf nodes. The recursion stops when a null child is encountered, yielding a depth‑first leaf‑count.

---

## tree_count_leaves — iterative

- anchors: 0 exact, 20 relocated, **1 quoting a line that is not in the file**, of 21
- containers in the code: stack

  - *container named*: Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of 8 right child of 8 left child of 3 right child of 3 left child of 6 right child of 6 right child of 10 left child of 14 Base case: empty subtree has no leaves Use a stack for post-order traversal Push the root onto the stack Counter for leaves found Process nodes in post-order Peek at the top of the stack Remove the node from the stack If the current node is a leaf, increment the counter Push left child onto the stack (post-order left) Push right child onto the stack (post-order right) Return the total number of leaves Print the number of leaves in the constructed tree Purpose: Count the number of leaf nodes in a binary tree.
  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, pushing nodes onto the stack in post‑order (left, right, then current).

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
| 10 | `Node* root = new Node(8);` | Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree has no leaves |
| 22 | `stack<Node*> pending;` | Use a stack for post-order traversal |
| 23 | `pending.push(node);` | Push the root onto the stack |
| 24 | `int found = 0;` | Counter for leaves found |
| 25 | `while (!pending.empty()) {` | Process nodes in post-order |
| 26 | `Node* current = pending.top();` | Peek at the top of the stack |
| 27 | `pending.pop();` | Remove the node from the stack |
| 28 | `if (current->left == nullptr && current->right == nullptr) found++;` | If the current node is a leaf, increment the counter |
| 29 | `if (current->left) pending.push(current->left);` | Push left child onto the stack (post-order left) |
| 30 | `if (current->right) pending.push(current->right);` | Push right child onto the stack (post-order right) |
| 33 | `return found;` | Return the total number of leaves |
| 36 | `cout << leaves(sample()) << "\n";` | Print the number of leaves in the constructed tree |

**Explanation**

Purpose: Count the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes.  
Algorithm: Perform a depth‑first traversal using a stack, pushing nodes onto the stack in post‑order (left, right, then current). For each node, if both children are null, increment a counter; otherwise push the children onto the stack. The loop stops when the stack is empty, yielding the leaf count.

---

## tree_invert — recursive

- anchors: 0 exact, 26 relocated, **0 quoting a line that is not in the file**, of 26
- containers in the code: stack

  - *container named*: Build a simple binary tree for testing left child right child left‑left child left‑right child left‑right‑left child left‑right‑right child right‑right child right‑right‑left child Base case: stop recursion when reaching a null pointer Save left child before swapping Swap left and right children Restore saved left child Recurse on the new left subtree Recurse on the new right subtree Build the tree Invert the tree Use a stack for post‑order traversal Pop nodes in post‑order Current node Print value Push right child first to simulate left‑right traversal Push left child next Loop ends when stack is empty Final newline Success Purpose: Inverts a binary tree and prints its post-order traversal.
  - *container named*: main() uses a stack to perform a post‑order traversal, printing each node’s value after pushing its children onto the stack.

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
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 11 | `root->left = new Node(3);` | left child |
| 12 | `root->right = new Node(10);` | right child |
| 13 | `root->left->left = new Node(1);` | left‑left child |
| 14 | `root->left->right = new Node(6);` | left‑right child |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left child |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right child |
| 17 | `root->right->right = new Node(14);` | right‑right child |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left child |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 22 | `Node* spare = node->left;` | Save left child before swapping |
| 23 | `node->left = node->right;` | Swap left and right children |
| 24 | `node->right = spare;` | Restore saved left child |
| 25 | `invert(node->left);` | Recurse on the new left subtree |
| 26 | `invert(node->right);` | Recurse on the new right subtree |
| 30 | `Node* root = sample();` | Build the tree |
| 31 | `invert(root);` | Invert the tree |
| 32 | `stack<Node*> s; s.push(root);` | Use a stack for post‑order traversal |
| 33 | `while (!s.empty()) {` | Pop nodes in post‑order |
| 34 | `Node* c = s.top(); s.pop();` | Current node |
| 35 | `cout << c->value << " ";` | Print value |
| 36 | `if (c->right) s.push(c->right);` | Push right child first to simulate left‑right traversal |
| 37 | `if (c->left) s.push(c->left);` | Push left child next |
| 38 | `}` | Loop ends when stack is empty |
| 39 | `cout << "\n";` | Final newline |
| 40 | `return 0;` | Success |

**Explanation**

Purpose: Inverts a binary tree and prints its post-order traversal.  
Input: None (main reads a pre‑constructed sample tree).  
Output: Prints the tree’s post‑order sequence to std::cout.  
Algorithm: The sample() function builds a complete binary tree with a root value 8 and 15 children. invert() recursively swaps each node’s left and right pointers, effectively reversing the tree. main() uses a stack to perform a post‑order traversal, printing each node’s value after pushing its children onto the stack.

---

## tree_invert — iterative

- anchors: 0 exact, 29 relocated, **0 quoting a line that is not in the file**, of 29
- containers in the code: queue, stack

  - *container named*: Build a simple binary tree for testing left subtree: 3, 1, 6, 4, 7 right subtree: 10, 14, 13 left‑left: 1 left‑right: 6 left‑right‑left: 4 left‑right‑right: 7 right‑right: 14 right‑right‑left: 13 Base case: stop recursion when reaching a null node BFS traversal to invert subtrees start BFS from the root Process nodes level‑by‑level Dequeue current node Remove it from the queue Save left child before swapping Swap left and right children Restore saved left child Enqueue left child if it exists Enqueue right child if it exists Build the test tree Invert the tree to simulate a mirror image Iterative inorder traversal using a stack Process nodes in inorder order Pop current node from the stack Output node value Push right child if it exists Push left child if it exists Output newline after traversal Purpose: Inverts a binary tree in-place and prints its post-order traversal.
  - *container named*: The main() then uses a stack to perform a post‑order traversal, printing each node’s value.

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
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 11 | `root->left = new Node(3);` | left subtree: 3, 1, 6, 4, 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10, 14, 13 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 22 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null node |
| 23 | `queue<Node*> pending;` | BFS traversal to invert subtrees |
| 24 | `pending.push(node);` | start BFS from the root |
| 25 | `while (!pending.empty()) {` | Process nodes level‑by‑level |
| 26 | `Node* current = pending.front();` | Dequeue current node |
| 27 | `pending.pop();` | Remove it from the queue |
| 28 | `Node* spare = current->left;` | Save left child before swapping |
| 29 | `current->left = current->right;` | Swap left and right children |
| 30 | `current->right = spare;` | Restore saved left child |
| 31 | `if (current->left) pending.push(current->left);` | Enqueue left child if it exists |
| 32 | `if (current->right) pending.push(current->right);` | Enqueue right child if it exists |
| 36 | `Node* root = sample();` | Build the test tree |
| 37 | `invert(root);` | Invert the tree to simulate a mirror image |
| 38 | `stack<Node*> s; s.push(root);` | Iterative inorder traversal using a stack |
| 39 | `while (!s.empty()) {` | Process nodes in inorder order |
| 40 | `Node* c = s.top(); s.pop();` | Pop current node from the stack |
| 41 | `cout << c->value << " ";` | Output node value |
| 42 | `if (c->right) s.push(c->right);` | Push right child if it exists |
| 43 | `if (c->left) s.push(c->left);` | Push left child if it exists |
| 44 | `}` | Output newline after traversal |

**Explanation**

Purpose: Inverts a binary tree in-place and prints its post-order traversal.  
Input: None (main reads a pre‑built sample tree).  
Output: Prints the tree’s post-order sequence to std::cout.  
Algorithm: The sample() function builds a complete binary tree; invert() performs a breadth‑first traversal, swapping each node’s left and right children. The main() then uses a stack to perform a post‑order traversal, printing each node’s value.

---

## quicksort_ranges — recursive

- anchors: 0 exact, 7 relocated, **1 quoting a line that is not in the file**, of 8
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
| 10 | `if (low >= high) return;` | Base case: if the sub‑array is empty or a single element, it is already sorted. |
| 11 | `int split = partition(values, low, high);` | Locate the pivot position using the Lomuto partition scheme. |
| 12 | `quicksort(values, low, split - 1);` | Recursively sort the left partition. |
| 13 | `quicksort(values, split + 1, high);` | Recursively sort the right partition. |
| 16 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Initial sample data; the algorithm will sort this array. |
| 17 | `quicksort(values, 0, values.size() - 1);` | Sort the entire vector in‑place. |
| 18 | `for (int v : values) cout << v << " ";` | Output the sorted array. |
| 19 | `cout << '\n';` | Ensure a newline after the output. |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑range.  
Output: `void` – the vector `values` is reordered in‑place; `int` – the pivot index after partitioning.  
Algorithm: Recursively selects a pivot element from the last element, partitions the remaining elements into two groups (elements ≤ pivot and elements > pivot), and swaps the pivot into its final position. The recursion continues on the left and right partitions until the sub‑range is empty.

---

## quicksort_ranges — iterative

> **describes this loop as recursive**

- anchors: 3 exact, 7 relocated, **1 quoting a line that is not in the file**, of 11
- containers in the code: stack

  - *recursion claim*: Place pivot at its final position Return index of pivot after partition Recursively sort left sub‑array Recursively sort right sub‑array Base case: empty or single element range Select pivot and partition Push left sub‑range for further recursion Push right sub‑range for further recursion Print sorted array Add newline for clarity Success Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
  - *recursion claim*: After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed.
  - *container named*: Algorithm: Uses a stack to perform a depth‑first traversal of the range, applying the `partition` helper to locate the pivot and split the range.
  - *container named*: After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed.

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
| 10 | `swap(values[boundary + 1], values[high]);` | Place pivot at its final position |
| 11 | `return boundary + 1;` | Return index of pivot after partition |
| 16 | `ranges.push({low, split - 1});` | Recursively sort left sub‑array |
| 17 | `ranges.push({split + 1, range.second});` | Recursively sort right sub‑array |
| 21 | `if (range.first >= range.second) continue;` | Base case: empty or single element range |
| 23 | `int split = partition(values, range.first, range.second);` | Select pivot and partition |
| 24 | `ranges.push({range.first, split - 1});` | Push left sub‑range for further recursion |
| 25 | `ranges.push({split + 1, range.second});` | Push right sub‑range for further recursion |
| 29 | `for (int v : values) cout << v << " ";` | Print sorted array |
| 30 | `cout << "\n";` | Add newline for clarity |
| 32 | `return 0;` | Success |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑range.  
Output: The same vector `values` is reordered in‑place; the function returns `void`.  
Algorithm: Uses a stack to perform a depth‑first traversal of the range, applying the `partition` helper to locate the pivot and split the range. After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed. The main loop terminates when the stack is empty.

---

## graph_dfs — recursive

> **names a container the code does not use**

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

  - *container NOT in the code*: Perform DFS on the unvisited neighbor; recursion unwinds when the stack is empty.

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
| 10 | `for (int next : graph[node]) dfs(next, seen);` | Perform DFS on the unvisited neighbor; recursion unwinds when the stack is empty. |
| 14 | `vector<bool> seen(graph.size(), false);` | Mark all vertices as unvisited before the first DFS call. |
| 15 | `dfs(0, seen);` | Start DFS from vertex 0; prints the path 0 1 2 3 4 5 6. |
| 16 | `cout << "\n";` | Output a newline to separate the traversal from the final message. |

**Explanation**

Purpose: Perform a depth‑first search on an undirected graph and print each visited node.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited nodes.  
Output: Prints node values in the order they are visited to `std::cout`.  
Algorithm: Initialize a visited flag vector, then recursively visit nodes starting from index 0, marking each node as seen and outputting it. The recursion stops when a node is already marked, preventing cycles.

---

## graph_dfs — iterative

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
- containers in the code: stack

  - *container named*: Process nodes in depth‑first order using a stack.
  - *container named*: Remove it from the stack.

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
| 10 | `while (!pending.empty()) {` | Process nodes in depth‑first order using a stack. |
| 11 | `int current = pending.top();` | Pop the next node to explore. |
| 12 | `pending.pop();` | Remove it from the stack. |
| 13 | `if (seen[current]) continue;` | Skip already visited nodes to avoid revisiting. |
| 14 | `seen[current] = true;` | Mark the node as visited. |
| 15 | `cout << current << " ";` | Output the node's label. |
| 16 | `for (int i = graph[current].size() - 1; i >= 0; i--)` | Push all unvisited neighbors onto the stack in reverse order to achieve post‑order traversal. |
| 17 | `if (!seen[graph[current][i]]) pending.push(graph[current][i]);` | Push only those neighbors that have not been visited yet. |
| 20 | `vector<bool> seen(graph.size(), false);` | Initialize a visited flag for each vertex. |
| 21 | `dfs(0, seen);` | Start DFS from vertex 0. |
| 22 | `cout << "\n";` | Output a newline after the traversal. |

**Explanation**

Purpose: Perform a depth‑first search (DFS) traversal of an undirected graph starting from node 0 and output the visited vertices.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking which vertices have been visited.  
Output: Prints the vertices in the order they are visited to `std::cout`, followed by a newline.  
Algorithm: Initialize a stack with the start node and a boolean vector marking all vertices unvisited. While the stack is non‑empty, pop the top, mark it as visited, output it, then push all unvisited neighbors onto the stack in reverse order to achieve depth‑first traversal. The loop stops when the stack is empty.

---

## flood_fill — recursive

- anchors: 0 exact, 15 relocated, **0 quoting a line that is not in the file**, of 15
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
| 10 | `if (row < 0 \|\| row >= rows \|\| col < 0 \|\| col >= cols) return;` | If the target cell is out of bounds, stop recursion. |
| 11 | `if (grid[row][col] != from) return;` | If the target cell does not contain the source value, stop recursion. |
| 12 | `grid[row][col] = to;` | Replace the source value with the target value. |
| 13 | `fill(row + 1, col, from, to);` | Recursively fill all four adjacent cells. |
| 14 | `fill(row - 1, col, from, to);` | Note: the original code had a typo here – it should be `fill(row - 1, col, from, to);`. |
| 15 | `fill(row, col + 1, from, to);` | Note: the original code had a typo here – it should be `fill(row, col + 1, from, to);`. |
| 16 | `fill(row, col - 1, from, to);` | Note: the original code had a typo here – it should be `fill(row, col - 1, from, to);`. |
| 20 | `cin >> rows >> cols;` | Read the grid dimensions. |
| 21 | `grid.assign(rows, vector<int>(cols));` | Allocate the grid with the given dimensions. |
| 22 | `for (int r = 0; r < rows; r++)` | Read the grid values row‑wise. |
| 24 | `fill(0, 0, grid[0][0], 9);` | Start flooding from the top‑left corner with value 9. |
| 25 | `for (int r = 0; r < rows; r++) {` | Output the filled grid. |
| 26 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Each cell is printed followed by a space. |
| 27 | `cout << "\n";` | After each row, output a newline. |
| 28 | `return 0;` | Normal exit. |

**Explanation**

Purpose: Replace the top‑left cell of a grid with a specific value and flood‑fill all cells of the same value in all four cardinal directions.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of integers; `from` – value to flood‑fill; `to` – replacement value.  
Output: Prints the modified grid to standard output.  
Algorithm: Read the grid dimensions, then read the initial cell value. Perform a depth‑first flood‑fill from the top‑left corner, replacing each cell with `to` when it matches `from`. Finally, output the grid.

---

## flood_fill — iterative

- anchors: 16 exact, 5 relocated, **0 quoting a line that is not in the file**, of 21
- containers in the code: stack

  - *container named*: Push the start cell onto the stack for DFS.
  - *container named*: Pop the top cell from the stack.

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

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (from == to) return;` | If the target value is already present, nothing to do. |
| 12 | `pending.push({row, col});` | Push the start cell onto the stack for DFS. |
| 14 | `while (!pending.empty()) {` | Perform a depth‑first search from the start cell. |
| 15 | `pair<int, int> cell = pending.top();` | Pop the top cell from the stack. |
| 16 | `pending.pop();` | Remove it from the stack. |
| 17 | `int r = cell.first, c = cell.second;` | Extract the coordinates. |
| 18 | `if (r < 0 \|\| r >= rows \|\| c < 0 \|\| c >= cols) continue;` | Skip out‑of‑bounds cells. |
| 19 | `if (grid[r][c] != from) continue;` | Skip cells that are not the source value. |
| 20 | `grid[r][c] = to;` | Replace the source value with the target value. |
| 21 | `pending.push({r - 1, c});` | Push adjacent cells in clockwise order. |
| 22 | `pending.push({r, c - 1});` | Note: the original code had a typo here – it should be {r, c - 1} instead of {r, c - 1} – but the intended effect is to fill the four adjacent cells. |
| 23 | `pending.push({r, c + 1});` | Note: the original code had a typo here – it should be {r, c + 1} instead of {r, c + 1} – but the intended effect is to fill the four adjacent cells. |
| 24 | `pending.push({r + 1, c});` | Note: the original code had a typo here – it should be {r + 1, c} instead of {r + 1, c} – but the intended effect is to fill the four adjacent cells. |
| 28 | `cin >> rows >> cols;` | Read the grid dimensions. |
| 30 | `for (int r = 0; r < rows; r++)` | Read the grid values. |
| 32 | `for (int c = 0; c < cols; c++) cin >> grid[r][c];` | Note: the original code had a typo here – it should be grid[r][c] = to; – but the intended effect is to replace the source value with the target value. |
| 33 | `fill(0, 0, grid[0][0], 9);` | Fill the top‑left cell with value 9. |
| 34 | `for (int r = 0; r < rows; r++) {` | Output the modified grid. |
| 35 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Note: the original code had a typo here – it should be grid[r][c] << " "; – but the intended effect is to print each cell followed by a space. |
| 36 | `cout << "\n";` | Note: the original code had a typo here – it should be cout << "\n"; – but the intended effect is to print a newline after each row. |
| 37 | `return 0;` | Success. |

**Explanation**

Purpose: Flood‑fill a 2‑D grid starting from a given cell, replacing all occurrences of a specified value with another.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of integers; `(0,0)` – starting cell coordinates; `from` – value to replace; `to` – replacement value.  
Output: Prints the modified grid to standard output.  
Algorithm: Perform a depth‑first search using a stack, pushing adjacent cells only when they are within bounds and have the source value. Continue until the stack is empty, then output the grid.

---

## sum_digits_tree — recursive

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
| 10 | `Node* root = new Node(8);` | Create the binary tree structure: 8 (root) 3 10 1 6 4 7 14 13 |
| 14 | `carried = carried * 10 + node->value;` | Build the decimal number from the current path |
| 15 | `if (node->left == nullptr && node->right == nullptr) return carried;` | Leaf node: the accumulated number is a valid path |
| 16 | `return paths(node->left, carried) + paths(node->right, carried);` | Propagate the accumulated number to children |
| 19 | `cout << paths(sample(), 0) << "\n";` | Print the total number of paths from the root to leaf nodes |

**Explanation**

Purpose: Count all root‑to‑leaf paths whose values form a valid decimal number.  
Input: Node* root – pointer to the binary tree root (or nullptr). int carried – accumulator for the current number formed by traversing the path so far.  
Output: int – total number of such paths.  
Algorithm: Perform a depth‑first search, appending each node’s value to the accumulator. When a leaf is reached, convert the accumulated value to an integer and return it. The recursion accumulates results from left and right subtrees, yielding the total count.

---

## sum_digits_tree — iterative

- anchors: 0 exact, 16 relocated, **1 quoting a line that is not in the file**, of 17
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated value.
  - *container named*: The traversal continues until the stack is empty.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree structure; each node holds an integer value and pointers to its children. |
| 11 | `root->left = new Node(3);` | Build the left subtree: 8 → 3 |
| 12 | `root->right = new Node(10);` | Build the right subtree: 8 → 10 |
| 13 | `root->left->left = new Node(1);` | Build the left‑left subtree: 3 → 1 |
| 14 | `root->left->right = new Node(6);` | Build the left‑right subtree: 3 → 6 |
| 15 | `root->left->right->left = new Node(4);` | Build the left‑right‑left subtree: 6 → 4 |
| 16 | `root->left->right->right = new Node(7);` | Build the left‑right‑right subtree: 6 → 7 |
| 17 | `root->right->right = new Node(14);` | Build the right‑right subtree: 10 → 14 |
| 18 | `root->right->right->left = new Node(13);` | Build the right‑right‑left subtree: 14 → 13 |
| 21 | `Node* current = item.first;` | current is the node whose path is being examined |
| 22 | `int running = item.second * 10 + current->value;` | running accumulates the value of the current node in the current path |
| 23 | `if (current->left == nullptr && current->right == nullptr) {` | If the node is a leaf, the accumulated path value is a valid path |
| 24 | `total += running;` | add this path to the total count |
| 26 | `if (current->left) pending.push({current->left, running});` | Push left child with the updated running value |
| 27 | `if (current->right) pending.push({current->right, running});` | Push right child with the updated running value |
| 30 | `return total;` | Return the total number of paths that end at the current node |
| 33 | `cout << paths(sample(), 0) << "\n";` | Print the total number of paths in the sample tree |

**Explanation**

Purpose: Counts all paths from the root to leaf nodes whose values form a number divisible by 10.  
Input: Node* root – pointer to the binary tree root; int carried – accumulator for the current number.  
Output: int – total number of such paths.  
Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated value. When a leaf is reached, add the accumulated value to the total only if it is divisible by 10. The traversal continues until the stack is empty.

---
