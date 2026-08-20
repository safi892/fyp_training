# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 92 |
| valid JSON, of output that finished | 89/90 |
| ran past the token budget | 2/92 |
| anchors quoting a real line | 636/644 (99%) |
| named a container the code declares | 3/3 |
| named a container that is not there | 1/92 |
| loops described as recursive | 1/46 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## dataset.jsonl#0 — recursive

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
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
| 10 | `return min(arr[n - 1], getMin(arr, n - 1));` | If there is a single element, return it. Else, return the minimum of the first element and the minimum of the remaining array. |
| 15 | `return max(arr[n - 1], getMax(arr, n - 1));` | If there is a single element, return it. Else, return the maximum of the first element and the maximum of the remaining array. |
| 20 | `cout << "Minimum element of array: " << getMin(arr, n) << "\n";` | Print the minimum and maximum elements of the array. |

**Explanation**

Purpose: Compute the minimum and maximum values in a vector of integers.  
Input: const vector<int>& arr – the array to examine; int n – number of elements to consider (n ≤ arr.size()).  
Output: int – the minimum (or maximum) element of the specified sub‑array.  
Algorithm: Uses a simple divide‑and‑conquer approach: if the sub‑array contains only one element, it returns that element; otherwise it recursively finds the minimum of the last element and the minimum of the rest, then returns the smaller (or larger) of the two results. The recursion stops when the sub‑array size reaches one.

---

## dataset.jsonl#0 — iterative

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
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
| 10 | `cout << "Minimum element of array: " << getMin(arr) << "\n";` | Print the smallest value in the array. |
| 11 | `cout << "Maximum element of array: " << getMax(arr) << "\n";` | Print the largest value in the array. |

**Explanation**

Purpose: Compute the minimum and maximum values in a vector of integers.  
Input: const vector<int>& arr – the source data.  
Output: int – the minimum element (for getMax) and the maximum element (for getMin).  
Algorithm: Initialize the result with the first element, then iterate from the second element, updating the result with the smaller (for getMax) or larger (for getMin) element. The final result is returned.

---

## dataset.jsonl#1 — recursive

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
Output: The same stack, now in reversed order.  
Algorithm: `reverseStack` pops the top element, recursively reverses the remainder, and then inserts it at the bottom. `insertAtBottom` uses a simple loop to move the top element to the bottom of the stack, effectively reversing the order.

---

## dataset.jsonl#1 — iterative

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
- containers in the code: stack

  - *container named*: Transfer all elements from st to aux in reverse order push the current top onto aux remove the element from st swap the two stacks to reverse the order initialise stack with some values ...
  - *container named*: Print the reversed stack Purpose: Reverses the order of elements in a stack in place.

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
| 10 | `while (!st.empty()) {` | Transfer all elements from st to aux in reverse order |
| 11 | `aux.push(st.top());` | push the current top onto aux |
| 12 | `st.pop();` | remove the element from st |
| 15 | `swap(st, aux);` | swap the two stacks to reverse the order |
| 20 | `st.push(1);` | initialise stack with some values |
| 21 | `st.push(2);` | ... |
| 22 | `st.push(3);` | ... |
| 23 | `st.push(4);` | ... |
| 26 | `while (!st.empty()) {` | Print the reversed stack |

**Explanation**

Purpose: Reverses the order of elements in a stack in place.  
Input: A reference to a std::stack<int> containing the elements to be reversed.  
Output: The same stack is modified so that its top becomes the original bottom, and its bottom becomes the original top.  
Algorithm: Iterate over the stack, pushing each element onto a temporary auxiliary stack, then swap the original stack with the auxiliary stack. This effectively reverses the stack order.

---

## dataset.jsonl#2 — recursive

- anchors: 0 exact, 8 relocated, **1 quoting a line that is not in the file**, of 9
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
| 10 | `ch = toupper(ch);` | convert to uppercase to match the vowel list |
| 12 | `return !(ch == 'A' \|\| ch == 'E' \|\|` | return true only if the character is a consonant |
| 15 | `ch >= 65 && ch <= 90;` | and falls within the ASCII range for uppercase letters |
| 19 | `if (n == 1)` | base case: single character |
| 20 | `return isConsonant(str[0]);` | count only if it is a consonant |
| 22 | `return totalConsonants(str, n - 1) +` | recursively count the rest and add the current character |
| 24 | `isConsonant(str[n-1]);` | count the last character |
| 27 | `string str = "abc de";` | test string |
| 28 | `cout << totalConsonants(str, str.length());` | output total consonants in the string |

**Explanation**

Purpose: Counts the total number of consonants in a given string.  
Input: `string str` – the string to examine; `int n` – length of the string (unused in the original implementation).  
Output: `int` – total count of consonants in `str`.  
Algorithm: Uses a helper `isConsonant` to test each character for consonant status. The main function recursively processes the string, adding the result of the last character to the sum of the rest, terminating when the length reaches 1.

---

## dataset.jsonl#2 — iterative

- anchors: 0 exact, 6 relocated, **1 quoting a line that is not in the file**, of 7
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
| 10 | `ch = toupper(ch);` | convert to uppercase to match the vowel list |
| 12 | `return !(ch == 'A' \|\| ch == 'E' \|\|` | return true only if ch is a consonant |
| 15 | `ch >= 65 && ch <= 90);` | and lies in the ASCII range for uppercase letters |
| 20 | `for (int i = 0; i < str.length(); i++)` | iterate over each character in the string |
| 21 | `if (isConsonant(str[i]))` | increment count if the character is a consonant |
| 24 | `return count;` | total number of consonants in the string |
| 27 | `string str = "abc de";` | test case: "abc de" contains 3 consonants |

**Explanation**

Purpose: Counts the total number of consonants in a given string.  
Input: A std::string containing the text to analyze.  
Output: An int representing the count of consonants.  
Algorithm: Iterates over each character, converts it to uppercase, and checks against the list of vowels; if the character is not a vowel and is an uppercase letter, it increments a counter. The final counter is returned.

---

## dataset.jsonl#3 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 10 | `char res = first(str);` | Call the recursive helper; the default start index is 0. |
| 11 | `if (res == 0)` | If the helper returns 0, the string contains only lowercase letters. |
| 12 | `cout << "No uppercase letter";` | Print a message indicating the absence of an uppercase letter. |
| 13 | `else` | Otherwise, the first uppercase letter was found. |
| 14 | `cout << res << "\n";` | Output the found uppercase letter followed by a newline. |

**Explanation**

Purpose: Find the first uppercase letter in a string.  
Input: `string str` – the source text; `int i` – current index (default 0).  
Output: `char` – the first uppercase character, or 0 if none exists.  
Algorithm: Recursively scan the string from index i. If the character is uppercase, return it; otherwise, recurse with the next index. The recursion terminates when the end of the string is reached.

---

## dataset.jsonl#3 — iterative

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
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
| 4 | `for (int i = 0; i < str.length(); i++)` | Iterate over each character in the string. |
| 5 | `if (isupper(str[i]))` | Check if the current character is an uppercase letter. |
| 6 | `return str[i];` | Return the first uppercase letter found. |
| 7 | `return 0;` | If no uppercase letter is found, return 0 (undefined behavior). |
| 11 | `string str = "geeksforGeeKS";` | Example string to search for the first uppercase letter. |
| 12 | `char res = first(str);` | Call the first function to locate the first uppercase letter. |
| 13 | `if (res == 0)` | If the result is 0, it means no uppercase letter was found. |
| 14 | `cout << "No uppercase letter";` | Print a message indicating that no uppercase letter was found. |
| 15 | `else` | Otherwise, print the found uppercase letter. |
| 16 | `cout << res << "\n";` | Print the found uppercase letter followed by a newline. |
| 17 | `return 0;` | Return 0 to indicate successful execution. |

**Explanation**

Purpose: To locate and return the first uppercase letter in a given string.
Input: A single `std::string` parameter `str`.
Output: Returns a `char` representing the first uppercase letter found, or `0` if none exists.
Algorithm: Iterates through each character of the string, checking if it is uppercase using `isupper`. Returns the character immediately upon finding it, otherwise returns `0` after the loop completes.

---

## dataset.jsonl#4 — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
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

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Determines whether a string can be expressed as the sum of two non‑empty additive sub‑strings.  
Input: `string s` – the number to test.  
Output: `bool` – `true` if `s` can be written as `a + b` where `a` and `b` are additive sub‑strings, otherwise `false`.  
Algorithm: The function enumerates all possible lengths for the first and second additive sub‑strings, checks each pair with `checkAddition`, and returns `true` on the first successful match. If none succeed, it returns `false`.

---

## dataset.jsonl#4 — iterative

> **describes this loop as recursive**

- anchors: 0 exact, 20 relocated, **0 quoting a line that is not in the file**, of 20
- containers in the code: none

  - *recursion claim*: Algorithm: For each possible split point `i`, recursively try to match the prefix `f` and suffix `s` with the rest of `s` using `strAdd`.

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
| 10 | `for(int i = s1.size()-1, j = s2.size()-1; i >= 0 \|\| j >= 0; i--, j--){` | iterate from the least‑significant digit, handling carry |
| 11 | `int a = i >= 0 ? (s1[i] - '0') : 0;` | extract digit from s1 (or 0 if index out of range) |
| 12 | `int b = j >= 0 ? (s2[j] - '0') : 0;` | extract digit from s2 (or 0 if index out of range) |
| 13 | `sum = to_string((a + b + c) % 10) + sum;` | compute next digit and prepend to result |
| 14 | `c = (a + b + c) / 10;` | propagate carry to next iteration |
| 18 | `if(sum == num.substr(i, num.size() - i))` | compare current sum with the remainder of the string |
| 20 | `f = s;` | advance to next candidate pair |
| 21 | `s = sum;` | update second candidate |
| 22 | `i += sum.size();` | skip digits consumed by the current sum |
| 26 | `if((f.size() > 1 && f[0] == '0') \|\| (s.size() > 1 && s[0] == '0'))` | reject leading zeros to avoid invalid additive pairs |
| 30 | `if(isAdditiveNumberUtil(s, s.substr(0, i+1), s.substr(i+1, j-i)))` | try every possible split point |
| 34 | `return false;` | no additive decomposition found |
| 38 | `int len = s.size();` | length of the input string |
| 39 | `if(len < 3) return false;` | a number with fewer than three digits cannot be additive |
| 41 | `for(int i = 0; i < len; i++)` | try every possible split point |
| 42 | `for(int j = i + 1; j < len; j++)` | split into two substrings |
| 43 | `if(isAdditiveNumberUtil(s, s.substr(0, i+1), s.substr(i+1, j-i)))` | recursively test additive decomposition |
| 47 | `return false;` | no additive decomposition found |
| 51 | `string s = "235813";` | example number to test |
| 53 | `if (isAdditive(s))` | output result |

**Explanation**

Purpose: Determines whether a given string can be expressed as the sum of two or more additive numbers.  
Input: `string s` – the number to test.  
Output: `bool` – `true` if `s` is an additive number, otherwise `false`.  
Algorithm: For each possible split point `i`, recursively try to match the prefix `f` and suffix `s` with the rest of `s` using `strAdd`. If a match is found, return `true`; otherwise backtrack and try different splits. The function exhaustively checks all possible splits.

---

## dataset.jsonl#5 — recursive

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
Input: `char* input` – the source string; `int index` – current position in `input`; `char* output` – buffer for the current combination; `int outLength` – length of the current combination.  
Output: Prints each combination to `stdout` followed by a newline.  
Algorithm: Recursively select each character, append it to the output, and recurse with the next index. When the end of the input is reached, terminate the output string and output it. The function also handles the case where the next character is null, skipping it.

---

## dataset.jsonl#5 — iterative

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
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
| 3 | `int l = strlen(s);` | Determine the length of the input string (excluding the terminating '\0'). |
| 5 | `for(int i = 0; i < pow(2, l - 1); i++){` | Generate all possible combinations of the string by iterating over all 2^(n‑1) bit patterns. |
| 6 | `int k = i, x = 0;` | k tracks the current bit pattern; x indexes the current character in the string. |
| 7 | `cout << s[x];` | Output the first character of the string. |
| 8 | `x++;` | Advance to the next character. |
| 10 | `for(int j = 0; j < strlen(s) - 1; j++){` | Process each bit position in the pattern. |
| 11 | `if(k & 1)` | If the current bit is set, output a space. |
| 12 | `k = k >> 1;` | Shift the pattern right to examine the next bit. |
| 13 | `cout << s[x];` | Output the next character of the string. |
| 14 | `x++;` | Advance to the next character. |
| 16 | `cout << "\n";` | End of the current combination. |
| 20 | `char input[] = "1214";` | Example usage: prints all possible combinations of the string "1214". |

**Explanation**

Purpose: Prints all possible binary‑encoded combinations of a character string.  
Input: A null‑terminated character array `s` containing the characters to combine.  
Output: Writes each combination to `stdout`, each on a separate line.  
Algorithm: For each of the 2^(n‑1) possible bit patterns of length n‑1, it prints the first character of `s`, then iterates over the remaining characters, printing a space when the current bit is set and the character otherwise. The loop repeats for all patterns.

---

## dataset.jsonl#6 — recursive

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
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
| 10 | `if (idx >= s.size() \|\| s[idx] < '0' \|\| s[idx] > '9')` | If the current character is not a digit, we have reached the end of the number or a non‑digit separator. |
| 11 | `return res * sign;` | Return the accumulated result multiplied by the sign. |
| 14 | `int digit = s[idx] - '0';` | Convert the character digit to its numeric value. |
| 15 | `if (res > (INT_MAX - digit) / 10)` | Check for overflow before adding the next digit. |
| 16 | `return sign == 1 ? INT_MAX : INT_MIN;` | If overflow would occur, clamp the result to INT_MAX or INT_MIN. |
| 17 | `return parseDigits(s, idx + 1, res * 10 + digit, sign);` | Recursively process the next character. |
| 20 | `int idx = 0;` | Skip leading spaces. |
| 22 | `if (idx < s.size() && (s[idx] == '-' \|\| s[idx] == '+')) {` | Detect optional sign character. |
| 23 | `if (s[idx] == '-')` | Sign '-' indicates a negative number. |
| 25 | `idx++;` | Advance past the sign character. |
| 28 | `return parseDigits(s, idx, 0, sign);` | Start parsing the first digit. |
| 31 | `string s = " -0012g4";` | Test case: leading spaces, sign, and trailing garbage. |

**Explanation**

Purpose: Convert a string representation of an integer to its numeric value, handling optional sign and leading zeros.  
Input: `string &s` – the string to parse.  
Output: `int` – the parsed integer, clamped to INT_MAX/INT_MIN if overflow occurs.  
Algorithm: Skip leading spaces, detect the sign, and recursively parse each digit, building the result while enforcing overflow checks. The recursion stops when a non‑digit is encountered or the end of the string is reached.

---

## dataset.jsonl#6 — iterative

- anchors: 2 exact, 5 relocated, **0 quoting a line that is not in the file**, of 7
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
| 10 | `while (idx < s.size() && s[idx] == ' ') {` | skip leading spaces |
| 12 | `if (idx < s.size() && (s[idx] == '-' \|\| s[idx] == '+')) {` | detect optional sign character |
| 13 | `if (s[idx++] == '-')` | handle '-' sign |
| 15 | `while (idx < s.size() && s[idx] >= '0' && s[idx] <= '9') {` | parse digits |
| 16 | `if (res > INT_MAX / 10 \|\| (res == INT_MAX / 10 && s[idx] - '0' > 7)) {` | detect overflow before multiplying |
| 19 | `res = 10 * res + (s[idx++] - '0');` | accumulate digit |
| 21 | `return res * sign;` | apply sign and return result |

**Explanation**

Purpose: Convert a string representation of an integer to its numeric value, handling optional sign and leading zeros.  
Input: A reference to a std::string containing the integer to parse.  
Output: An int representing the parsed integer, or INT_MAX/INT_MIN if overflow occurs.  
Algorithm: Skip leading spaces, detect optional sign, then iterate over digits, accumulating the result while enforcing a 32‑bit overflow check. Finally apply the sign and return the result.

---

## dataset.jsonl#7 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
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
| 3 | `s2[index] = s1[index];` | copy the current character from s1 to s2 |
| 4 | `if (s1[index] == '\0')` | base case: when the source string ends, stop recursion |
| 7 | `myCopy(s1, s2, index + 1);` | recurse to copy the next character |
| 10 | `char s1[100] = "GEEKSFORGEEKS";` | source string to copy |
| 11 | `char s2[100] = "";` | destination string, initially empty |
| 12 | `myCopy(s1, s2);` | start copying from the first character |
| 13 | `cout << s2;` | output the copied characters |

**Explanation**

Purpose: Copies characters from the first string to the second string up to the first null terminator.  
Input: Two character arrays `s1` and `s2`, with `s2` initialized to an empty string. An optional `index` parameter defaults to 0.  
Output: Writes the copied characters into `s2` and returns the number of characters copied.  
Algorithm: The function recursively copies characters from `s1` to `s2`, stopping when `s1[index]` is '\0'. It uses a simple loop that increments `index` and writes the current character to `s2[index]`.

---

## dataset.jsonl#7 — iterative

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
| 4 | `for (i = 0; s1[i] != '\0'; i++)` | Copy characters from s1 up to the terminating '\0'. The loop stops when the source string ends. |
| 5 | `s2[i] = s1[i];` | Copy the character from s1 to s2. |
| 6 | `s2[i] = '\0';` | Ensure the destination string ends with a null terminator. |
| 10 | `char s1[100] = "GEEKSFORGEEKS";` | Source string containing the characters to be copied. |
| 11 | `char s2[100] = "";` | Destination string that will hold the copied characters. |
| 12 | `myCopy(s1, s2);` | Perform the copy operation. |
| 13 | `cout << s2;` | Output the copied string to verify correctness. |

**Explanation**

Purpose: Copies the contents of one character array into another, handling null termination.  
Input: Two character arrays `s1` and `s2`, where `s1` is the source and `s2` is the destination.  
Output: Writes the copied string to `s2` and returns the length of the copied string.  
Algorithm: Iterates over `s1` until a null terminator is encountered, copying each character to `s2`. After the loop, appends a null terminator to `s2` and returns the index of the null terminator (length).  
Edge cases: If `s1` is shorter than `s2`, the remaining characters in `s2` are left unchanged. If `s1` is longer, the extra characters are not copied.

---

## dataset.jsonl#8 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 12 | `if (!root)` | Base case: empty subtree – nothing to print. |
| 15 | `cout << root->data << " ";` | Leaf node: output its data and a trailing space. |
| 18 | `if (root->left)` | Non‑leaf node: recurse into left subtree. |
| 21 | `if (root->right)` | Recurse into right subtree. |
| 24 | `Node *root = new Node(1);` | Build a simple binary tree: 1 / \ 2 / \ 3 / \ 4 / \ 5 / \ 6 / \ 7 / \ 8 / \ 9 / \ 10 |

**Explanation**

Purpose: Prints all leaf nodes of a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: void – writes leaf node values to standard output separated by spaces.  
Algorithm: Perform a depth‑first traversal; when a node has no children, output its data. Recursively traverse the left and right subtrees, stopping at leaf nodes.

---

## dataset.jsonl#8 — iterative

- anchors: 0 exact, 19 relocated, **0 quoting a line that is not in the file**, of 19
- containers in the code: queue

  - *container named*: Algorithm: Perform a breadth‑first traversal using a queue, enqueueing each node.
  - *container named*: Continue until the queue is empty.

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
| 12 | `if (!root)` | empty subtree: nothing to print |
| 15 | `q.push(root);` | start BFS from the root |
| 19 | `if (!root->left && !root->right)` | leaf node reached |
| 20 | `cout << root->data << " ";` | output leaf value |
| 23 | `if (root->left)` | enqueue left child if present |
| 24 | `q.push(root->left);` | left child is a potential leaf |
| 25 | `if (root->right)` | enqueue right child if present |
| 26 | `q.push(root->right);` | right child is a potential leaf |
| 30 | `Node *root = new Node(1);` | build a simple binary tree |
| 31 | `root->left = new Node(2);` | left child of root |
| 32 | `root->right = new Node(3);` | right child of root |
| 33 | `root->left->left = new Node(4);` | left child of left child |
| 34 | `root->right->left = new Node(5);` | left child of right child |
| 35 | `root->right->right = new Node(8);` | right child of right child |
| 36 | `root->right->left->left = new Node(6);` | left child of right child's left child |
| 37 | `root->right->left->right = new Node(7);` | right child of right child's left child |
| 38 | `root->right->right->left = new Node(9);` | left child of right child's right child |
| 39 | `root->right->right->right = new Node(10);` | right child of right child's right child |
| 40 | `printLeafNodes(root);` | output leaf nodes |

**Explanation**

Purpose: Prints all leaf nodes of a binary tree in ascending order of their data.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: void – writes leaf node values to standard output separated by spaces.  
Algorithm: Perform a breadth‑first traversal using a queue, enqueueing each node. For each dequeued node, check if it has no children; if so, output its data. Enqueue its left child if present, then its right child. Continue until the queue is empty.

---

## dataset.jsonl#9 — recursive

- anchors: 1 exact, 26 relocated, **1 quoting a line that is not in the file**, of 28
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
| 10 | `for (int i = m - 1; i >= 0; --i) {` | fill DP table from bottom‑right to top‑left |
| 14 | `if (s1[i] == s2[j])` | characters match → extend LCS |
| 15 | `dp[i][j] = dp[i + 1][j + 1] + 1;` | extend diagonal entry |
| 16 | `else` | characters differ → take best from right or down |
| 20 | `if (cur.size() == lcsLen) {` | when the current prefix matches the required length, store it |
| 21 | `res.push_back(cur);` | store the LCS |
| 22 | `return;` | stop recursion |
| 25 | `if (i == (int)s1.size() \|\| j == (int)s2.size())` | one string has been fully processed → backtrack |
| 29 | `for (char ch = 'a'; ch <= 'z'; ++ch) {` | try every possible character from both strings |
| 30 | `for (int ii = i; ii < (int)s1.size(); ++ii) {` | search for a character that can extend the current LCS |
| 31 | `if (s1[ii] != ch) continue;` | skip if the character is not present in s1 |
| 32 | `for (int jj = j; jj < (int)s2.size(); ++jj) {` | search for a character that can extend the current LCS |
| 33 | `if (s2[jj] == ch && dp[ii][jj] == lcsLen - built) {` | only accept if the character is present in s2 and the remaining length matches the LCS length |
| 34 | `cur.push_back(ch);` | extend the current LCS candidate |
| 35 | `backtrack(s1, s2, ii + 1, jj + 1, lcsLen, dp, cur, res);` | recurse with the extended prefix |
| 36 | `cur.pop_back();` | backtrack to explore other possibilities |
| 37 | `found = true;` | mark that a valid extension was found |
| 38 | `break;` | stop inner loop |
| 41 | `}` | try all lowercase letters |
| 44 | `}` | stop outer loop |
| 47 | `return res;` | return all LCS candidates |
| 50 | `cout << "[";` | print the list of LCS candidates |
| 51 | `for (int i = 0; i < res.size(); ++i) {` | format the output |
| 52 | `cout << "\"" << res[i] << "\""` | print each LCS |
| 53 | `if (i + 1 < res.size()) cout << ", ";` | comma‑separated list |
| 54 | `}` | end of loop |
| 55 | `cout << "]\n";` | close the JSON array |
| 59 | `return 0;` | main function |

**Explanation**

Purpose: Find all longest common subsequences of two strings.  
Input: two std::string objects s1 and s2.  
Output: a std::vector<std::string> containing every LCS of s1 and s2.  
Algorithm: Compute the LCS length using a bottom‑up DP table, then backtrack from that length to collect all possible subsequences by enumerating all characters and pruning those that cannot extend the current LCS. The backtrack uses a depth‑first search with backtracking to explore all possibilities.

---

## dataset.jsonl#9 — iterative

- anchors: 0 exact, 15 relocated, **3 quoting a line that is not in the file**, of 18
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
| 10 | `while (i < t.size() && j < s.size()) {` | Scan both strings in lock‑step; stop when either reaches the end. |
| 11 | `if (t[i] == s[j])` | If characters match, advance the target index. |
| 12 | `++i;` | Match found: extend the LCS candidate. |
| 13 | `++j;` | Move to the next character in the source. |
| 16 | `return i == t.size();` | True only when the target string was fully consumed. |
| 20 | `for (int mask = 0; mask < (1 << n); ++mask) {` | Generate every possible substring of s1 using bit masking. |
| 21 | `string sub;` | Build the candidate substring from the set bits. |
| 22 | `for (int i = 0; i < n; ++i) {` | Iterate over the string; if the i‑th bit is set, include s1[i]. |
| 25 | `int len = sub.size();` | Record the length of the current candidate. |
| 26 | `if (len < best)` | Discard shorter candidates; they cannot be longer LCSs. |
| 27 | `continue;` | Skip to the next mask. |
| 28 | `if (isSubseq(sub, s2)) {` | Check whether this substring appears in s2. |
| 29 | `if (len > best) {` | A longer LCS was found; clear the set and insert the new candidate. |
| 32 | `st.insert(sub);` | Insert the candidate into the set. |
| 35 | `for (auto i : st)` | Collect all LCS substrings from the set. |
| 38 | `cout << "["` | Output the result in a JSON‑style array. |
| 40 | `cout << "],";` | Separate elements with commas. |
| 42 | `cout << "]
";` | Close the array and terminate the program. |

**Explanation**

Purpose: Find all longest common subsequences (LCS) between two strings.  
Input: two std::string objects `s1` and `s2`.  
Output: a std::vector<std::string> containing all LCS of `s1` and `s2`.  
Algorithm: Enumerate every subset of `s1` using bitmasking, build each candidate LCS, and use `isSubseq` to verify membership in `s2`. Track the longest LCS and collect all equal‑length ones; finally return the collected LCSes.

---

## dataset.jsonl#10 — recursive

- anchors: 1 exact, 8 relocated, **0 quoting a line that is not in the file**, of 9
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
| 10 | `result.push_back(currentNumber);` | when all digits have been chosen, store the formed number |
| 13 | `for (int nextDigit = currentDigit + 1; nextDigit <= 9; nextDigit++)` | try each successor digit greater than the current one |
| 16 | `generateNumbers(remainingDigits - 1, nextDigit,` | recursively generate numbers with one fewer digit |
| 20 | `if (n == 1)` | single‑digit numbers are the only ones that can be formed |
| 22 | `for (int digit = 0; digit <= 9; digit++)` | all single‑digit numbers are valid |
| 25 | `if (n > 9)` | n > 9 is impossible for a single‑digit number |
| 28 | `for (int firstDigit = 1; firstDigit <= 9; firstDigit++)` | first digit must be at least 1 to avoid leading zeros |
| 31 | `generateNumbers(n - 1, firstDigit, firstDigit, result);` | start building numbers with the first digit |
| 35 | `cout << "[";` | output the generated numbers enclosed in brackets |

**Explanation**

Purpose: Generate all n‑digit strictly increasing numbers using digits 0‑9.  
Input: int n – the desired number of digits (n ≥ 1).  
Output: vector<int> containing every such number in ascending order.  
Algorithm: Uses backtracking; for n = 1 it enumerates single‑digit numbers, for n > 1 it enumerates numbers starting with each digit 1‑9, and for n ≤ 9 it enumerates numbers starting with 1‑9. Each recursive call appends the current number to the result when the required digit count is reached.

---

## dataset.jsonl#10 — iterative

- anchors: 1 exact, 13 relocated, **1 quoting a line that is not in the file**, of 15
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
| 10 | `if (s.length() != n)` | If the number of digits differs from the requested length, it cannot be increasing. |
| 15 | `for (int i = 1; i < n; i++)` | Verify that each digit is strictly greater than the previous one. |
| 20 | `return true;` | All digits satisfy the increasing condition. |
| 24 | `if (n > 9)` | For n > 9, no n‑digit increasing numbers exist. |
| 28 | `int start = (n == 1) ? 0 : pow(10, n - 1);` | Generate the smallest n‑digit number (n == 1 → 0, n > 1 → 10^(n‑1)). |
| 30 | `int end = pow(10, n) - 1;` | Generate the largest n‑digit number (n == 1 → 9, n > 1 → 99…999). |
| 32 | `for (int num = start; num <= end; num++)` | Iterate over all numbers in the range and collect those that are strictly increasing. |
| 36 | `return result;` | Return the list of increasing numbers. |
| 40 | `int n = 1;` | Example usage: list all 1‑digit increasing numbers. |
| 41 | `vector<int> ans = increasingNumbers(n);` | Call the function and store the result. |
| 42 | `cout << "["` | Output the collected numbers in a readable format. |
| 43 | `for (int i = 0; i < ans.size(); i++)` | Iterate over the vector and print each element. |
| 44 | `cout << ans[i];` | Print each element. |
| 45 | `if (i != ans.size() - 1)` | Add comma and space except for the last element. |
| 46 | `cout << "]" << endl;` | Close the array brackets and terminate the line. |

**Explanation**

Purpose: Generate all n‑digit positive integers whose decimal digits strictly increase.  
Input: int n – the desired digit length (n ≥ 1).  
Output: vector<int> containing every such integer in ascending order.  
Algorithm: Compute the minimal and maximal n‑digit numbers using integer arithmetic, then iterate from start to end, applying the helper function hasIncreasingDigits to filter numbers that satisfy the digit‑increasing property. The result is collected in a vector and returned.

---

## dataset.jsonl#11 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 3 | `if (l > r)` | Base case: when the current sub‑array is empty, output the accumulated sum. |
| 6 | `subsetSums(arr, l + 1, r, sum + arr[l]);` | Include the element at index l in the current subset. |
| 7 | `subsetSums(arr, l + 1, r, sum);` | Exclude the element at index l from the current subset. |
| 11 | `vector<int> arr = { 5, 4, 3 };` | Example array; the function will compute all possible subset sums. |
| 12 | `int n = arr.size();` | Number of elements in the array. |
| 14 | `subsetSums(arr, 0, n - 1);` | Start the recursive subset‑sum generation from the first element. |

**Explanation**

Purpose: Prints all possible subset sums of the input array.  
Input: `vector<int>& arr` – the array to process; `int l` and `int r` – inclusive indices defining the current subset.  
Output: `void` – prints each sum to `std::cout` separated by spaces.  
Algorithm: Uses depth‑first recursion; for each element it either includes it in the current subset and recurses, or excludes it and recurses without including. The base case prints the accumulated sum when the index reaches the end.

---

## dataset.jsonl#11 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 5 | `for (long long i = 0; i < total; i++)` | iterate over each subset represented by a bitmask |
| 6 | `long long sum = 0;` | accumulate sum of elements in the current subset |
| 7 | `for (int j = 0; j < n; j++)` | examine each element; if bit j is set, add arr[j] to sum |
| 10 | `cout << sum << " ";` | output the subset sum followed by a space |

**Explanation**

Purpose: Prints all possible subset sums of a given integer array.  
Input: `vector<int>& arr` – the array of integers; `int n` – number of elements in `arr`.  
Output: `void` – writes each subset sum to `std::cout` separated by spaces.  
Algorithm: Compute the total number of subsets (2ⁿ). For each subset represented by a bitmask, iterate over the elements, add the element to the sum if it is included, and output the sum. The loop runs O(2ⁿ) time.

---

## dataset.jsonl#12 — recursive

- anchors: 0 exact, 5 relocated, **1 quoting a line that is not in the file**, of 6
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
| 4 | `if (remainingPlaces == 0)` | Base case: when all positions are filled, output the generated number. |
| 10 | `printRec(str + "1", extraOnes + 1, remainingPlaces - 1);` | Place a '1' in the current position and recurse with one fewer extra '1' and one fewer remaining slots. |
| 11 | `if (extraOnes > 0)` | If there are still extra '1's available, place a '0' in the current position and recurse with one fewer extra '1' and one fewer remaining slots. |
| 14 | `string str = "";` | Start with an empty string to build the number incrementally. |
| 15 | `printRec(str, 0, n);` | Generate all n‑digit numbers using the helper function. |
| 18 | `int n = 4;` | Example call: generate all 4‑digit numbers. |

**Explanation**

Purpose: Generates and prints all possible binary strings of length n that contain exactly n ones.  
Input: int n – the desired length of the binary strings.  
Output: Prints each valid binary string to standard output, separated by spaces.  
Algorithm: Uses a depth‑first recursion that builds each string by appending either ‘1’ or ‘0’. When the recursion depth equals n, the built string is printed. The recursion explores both choices for each position, pruning branches when the required ‘1’ count is exceeded.

---

## dataset.jsonl#12 — iterative

- anchors: 2 exact, 33 relocated, **0 quoting a line that is not in the file**, of 35
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
| 10 | `while (num_of_bits >= 0)` | Build the binary representation digit‑by‑digit, LSB first |
| 12 | `r.append("1");` | set bit |
| 13 | `else` | clear bit |
| 16 | `num_of_bits--;` | move to next bit position |
| 20 | `int first = 1 << (N - 1);` | smallest N‑bit number (all 1s) |
| 21 | `int last = first * 2;` | largest N‑bit number (all 0s) |
| 23 | `for (int i = last - 1; i >= first; --i)` | iterate from largest to smallest N‑bit number |
| 25 | `int zero_cnt = 0;` | count of 0 bits in the current number |
| 26 | `int one_cnt = 0;` | count of 1 bits in the current number |
| 27 | `int t = i;` | work on a copy to avoid modifying the original |
| 28 | `int num_of_bits = 0;` | number of bits processed so far |
| 29 | `while (t)` | count bits in the current number |
| 31 | `num_of_bits++;` | one more bit processed |
| 33 | `t = t >> 1;` | shift right to examine the next bit |
| 35 | `if (one_cnt >= zero_cnt)` | only keep numbers with at least as many 1s as 0s |
| 37 | `bool all_prefix_match = true;` | check that all prefixes of the number have at least as many 1s as 0s |
| 38 | `int msk = (1 << num_of_bits) - 2;` | mask for the current prefix length |
| 39 | `int prefix_shift = 1;` | shift to align the prefix with the current bit position |
| 40 | `while (msk)` | examine each prefix of the current number |
| 42 | `int prefix = (msk & i) >> prefix_shift;` | extract the current prefix |
| 43 | `int prefix_one_cnt = 0;` | count of 1s in the current prefix |
| 44 | `int prefix_zero_cnt = 0;` | count of 0s in the current prefix |
| 45 | `while (prefix)` | count bits in the current prefix |
| 47 | `prefix_shift++;` | move to the next bit position |
| 48 | `msk = msk & (msk << 1);` | shift mask to examine the next prefix length |
| 50 | `if (prefix_zero_cnt > prefix_one_cnt)` | if a prefix has more 0s than 1s, the number cannot be a prefix of another |
| 51 | `all_prefix_match = false;` | stop checking this prefix |
| 52 | `break;` | no need to check further prefixes |
| 54 | `if (all_prefix_match)` | only keep numbers that satisfy the prefix condition |
| 55 | `r.push_back(getBinaryRep(i, num_of_bits));` | store the binary representation of the current number |
| 59 | `int n = 4;` | example input: 4‑bit numbers |
| 60 | `vector<string> results = NBitBinary(n);` | generate all N‑bit binary numbers with at least as many 1s as 0s |
| 61 | `for (int i = 0; i < results.size(); ++i)` | print each result |
| 62 | `cout << results[i] << " ";` | each result is printed followed by a space |
| 63 | `cout << endl;` | end of output |

**Explanation**

Purpose: Generate all binary strings of length N that contain at least one ‘1’ and have the same number of ‘1’s in each prefix.  
Input: int N – desired bit length.  
Output: vector<string> – list of qualifying binary strings.  
Algorithm: Enumerate all integers in the range [2^{N‑1}, 2·2^{N‑1}) and count the number of ‘1’s in each prefix. For each integer, compute its binary representation and verify that the count of ‘1’s in each prefix is at least half the total. If so, store the binary string.

---

## dataset.jsonl#13 — recursive

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
| 3 | `if (n == 0)` | Base case: if the number is zero, its digit sum is zero. |
| 6 | `return (n % 10) + sumOfDigits(n / 10);` | Recursive step: extract the least‑significant digit using %10, add it to the sum of the remaining digits obtained by integer division. |
| 10 | `cout << sumOfDigits(12345);` | Print the digit sum of the integer 12345. |

**Explanation**

Purpose: Computes the sum of the decimal digits of a non‑negative integer.  
Input: int n – the integer whose digit sum is required.  
Output: int – the sum of the digits of n (0 for n == 0).  
Algorithm: Uses recursion; returns 0 when n is zero, otherwise returns the last digit plus the sum of the remaining digits obtained by integer division. The recursion naturally handles the base case and propagates the result upward.

---

## dataset.jsonl#13 — iterative

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
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
| 4 | `string s = to_string(n);` | Convert the integer to its decimal representation as a string. |
| 5 | `int sum = 0;` | Accumulator for the digit sum. |
| 7 | `sum += ch - '0';` | Convert each character back to its numeric value and add to the sum. |
| 10 | `int n = 12345;` | Example usage: sum of digits of 12345. |

**Explanation**

Purpose: Computes the sum of the decimal digits of a non‑negative integer.  
Input: int n – the integer whose digit sum is to be calculated.  
Output: int – the total of all decimal digits in n.  
Algorithm: Convert n to a string, iterate over each character, convert each character back to an integer, and accumulate the sum. The loop runs O(log n) times, yielding O(1) time complexity.

---

## dataset.jsonl#14 — recursive

- anchors: 1 exact, 5 relocated, **0 quoting a line that is not in the file**, of 6
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
| 10 | `ans.push_back(num);` | a valid combination of bits ending at position pos is stored |
| 13 | `dfs(pos + 1, n, 0, num << 1, ans);` | include the current bit as 0 |
| 14 | `dfs(pos + 1, n, 1, (num << 1) \| 1, ans);` | include the current bit as 1 |
| 17 | `ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());` | remove the empty (all‑zero) combination |
| 20 | `int n = 3;` | generate all binary numbers of length 3 without consecutive 1s |
| 22 | `for (int x : ans)` | print each valid combination |

**Explanation**

Purpose: Generate all binary numbers of length n that contain no two consecutive 1s.  
Input: int n – desired bit length.  
Output: vector<int> – list of valid numbers in ascending order.  
Algorithm: Perform a depth‑first search over all possible bit patterns of length n, pruning branches when a 1 is placed immediately after another 1. After enumeration, remove the zero‑prefix entry and return the remaining numbers.

---

## dataset.jsonl#14 — iterative

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
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
| 13 | `return true;` | all bits are either 0 or 1 |
| 17 | `for (int num = 0; num < (1 << n); num++)` | generate all n‑bit numbers |
| 18 | `if (isValid(num))` | keep only those whose bits are not both 1 |
| 21 | `ans.erase(remove(ans.begin(), ans.end(), 0), ans.end());` | remove the zero entry that was accidentally included |
| 22 | `return ans;` | return the filtered list |
| 26 | `int n = 3;` | number of bits per number |
| 27 | `vector<int> ans = noConsecutiveOnes(n);` | collect all n‑bit numbers with no consecutive 1s |
| 28 | `for (int x : ans)` | print each number |

**Explanation**

Purpose: Generate all binary numbers of length n that contain no two consecutive 1‑bits.  
Input: int n – the desired bit length.  
Output: vector<int> – list of numbers meeting the criteria.  
Algorithm: Enumerate all 2ⁿ numbers using a simple loop, test each with a helper that rejects numbers with both LSB and second LSB set, collect valid ones, and finally remove the zero entry. The result is returned as a vector.

---

## dataset.jsonl#15 — recursive

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
| 10 | `int newChoc = choc / wrap;` | Compute how many chocolates can be obtained from the current stock. |
| 11 | `return newChoc + countRec(newChoc + choc % wrap, wrap);` | Recurse with the remainder chocolates and the same wrap count. |
| 14 | `int choc = money / price;` | Determine how many chocolates can be bought with the given money. |
| 15 | `return choc + countRec(choc, wrap);` | Add the chocolates obtained from the initial purchase. |
| 18 | `cout << countChocolates(money, price, wrap);` | Output the total number of chocolates that can be obtained. |

**Explanation**

Purpose: Compute the total number of chocolates you can obtain from a given amount of money, assuming each chocolate costs $2 and each chocolate gives one chocolate and one free wrap.  
Input: money – total cash in dollars; price – cost per chocolate in dollars; wrap – number of chocolates obtained for each free wrap.  
Output: int – total number of chocolates that can be obtained.  
Algorithm: First, determine how many chocolates can be bought with the initial cash. Then recursively count the additional chocolates obtained by exchanging each bought chocolate for a free wrap, adding the result to the initial count. The recursion stops when no more free wraps can be obtained.

---

## dataset.jsonl#15 — iterative

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
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
| 3 | `if (money < price)` | If the customer cannot afford even one chocolate, they cannot obtain any. |
| 6 | `int choc = money / price;` | Initial count of chocolates based on the price per chocolate. |
| 7 | `choc = choc + (choc - 1) / (wrap - 1);` | Adjust for wrapping: each full wrap yields one extra chocolate, so we add the quotient of (choc - 1) / (wrap - 1). |
| 10 | `cout << countChocolates(money, price, wrap);` | Output the total number of chocolates the customer can buy. |

**Explanation**

Purpose: Compute the maximum number of chocolates that can be bought with a given amount of money, considering a price per chocolate and a wrap‑for‑one discount.  
Input: three integers – `money` (total cash), `price` (cost per chocolate), `wrap` (number of chocolates obtained for one wrapped chocolate).  
Output: an integer representing the total number of chocolates that can be obtained.  
Algorithm: If the money is insufficient, return 0. Otherwise, calculate the initial number of chocolates by dividing money by price, then adjust for the wrap‑for‑one effect by adding the integer part of (initial chocolates - 1) / (wrap - 1). The result is returned.

---

## dataset.jsonl#16 — recursive

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
| 13 | `if (curr == d)` | If we have reached the target, return the number of steps taken. |
| 16 | `int left = minRecur(curr - steps - 1, steps + 1, d);` | Explore the left side of the board: move one step left, then one step right. |
| 17 | `int right = minRecur(curr + steps + 1, steps + 1, d);` | Explore the right side of the board: move one step right, then one step left. |
| 18 | `return min(left, right);` | Return the minimum number of steps required to reach the target. |
| 21 | `d = abs(d);` | Ensure the distance is non‑negative for the recursive helper. |
| 22 | `return minRecur(0, 0, d);` | Start from the origin with zero steps. |
| 25 | `int d = 2;` | Example distance; the function returns the minimal steps to reach 2. |

**Explanation**

Purpose: Compute the minimum number of steps required to reach the target distance d starting from 0.  
Input: int d – the target distance (positive or negative).  
Output: int – the minimal step count, or INT_MAX if the distance is unreachable.  
Algorithm: minSteps normalizes d to its absolute value, then calls minRecur with an initial position of 0, a zero accumulated steps, and the normalized distance. minRecur recursively explores the left and right reachable positions, pruning deeper branches when the current position exceeds d, and returns the smallest step count among the two branches.

---

## dataset.jsonl#16 — iterative

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
| 3 | `d = abs(d);` | ensure distance is non‑negative for the algorithm |
| 5 | `int sum = 0, step = 0;` | sum of first step numbers: 0, 1, 3, 6, … |
| 6 | `while (sum < d \|\| (sum - d) % 2 != 0)` | loop until the accumulated sum reaches d or is odd |
| 7 | `step++;` | increment step count |
| 8 | `sum += step;` | add the next step number to the sum |
| 11 | `return step;` | return the minimal number of steps |
| 14 | `int d = 2;` | example distance; the function will compute the minimal steps for this value |

**Explanation**

Purpose: Compute the minimum number of steps required to reach a distance d starting from 0.  
Input: int d – the target distance (may be negative).  
Output: int – the minimal step count.  
Algorithm: Convert d to absolute value, then repeatedly add consecutive integers until the accumulated sum reaches or exceeds d, ensuring the last step is even to avoid overshooting. The loop runs at most d+1 times.

---

## dataset.jsonl#17 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

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
| 3 | `if (n <= 1)` | Base case: the first two Fibonacci numbers are defined as 0 and 1. |
| 5 | `return fibonacci(n - 1) + fibonacci(n - 2);` | Recursive step: each number is the sum of the two preceding ones. |
| 9 | `cin >> n;` | Read the index from the user; assumes the input is non‑negative. |
| 10 | `cout << fibonacci(n);` | Output the n‑th Fibonacci number. |

**Explanation**

Purpose: Computes the nth Fibonacci number.  
Input: An integer n representing the position in the sequence.  
Output: An integer equal to F(n), where F is the Fibonacci function.  
Algorithm: Uses a simple recursive definition: F(0)=0, F(1)=1, and for n > 1 it returns F(n‑1) + F(n‑2). The recursion terminates when n ≤ 1, yielding the base case directly.

---

## dataset.jsonl#17 — iterative

- anchors: 0 exact, 8 relocated, **0 quoting a line that is not in the file**, of 8
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
| 3 | `if (n <= 1)` | Base case: the first two Fibonacci numbers are defined as 0 and 1. |
| 10 | `for (int i = 2; i <= n; ++i)` | Iterate from the third term up to n, building the sequence incrementally. |
| 11 | `current = prev1 + prev2;` | Compute the next Fibonacci number by summing the two preceding ones. |
| 12 | `prev2 = prev1;` | Shift the last two values forward for the next iteration. |
| 13 | `prev1 = current;` | Update the last two values for the next iteration. |
| 16 | `return current;` | Return the n‑th Fibonacci number. |
| 20 | `cin >> n;` | Read the desired index from standard input. |
| 21 | `cout << fibonacci(n) << endl;` | Output the Fibonacci number at position n. |

**Explanation**

Purpose: Compute the n‑th Fibonacci number.  
Input: An integer n representing the position in the sequence.  
Output: An integer equal to F(n), the sum of the two preceding Fibonacci numbers.  
Algorithm: Handles the trivial cases n ≤ 1 directly. For n > 1 it iteratively builds the sequence using three variables (prev2, prev1, current) and updates them each iteration, returning the final value.

---

## dataset.jsonl#18 — recursive

- anchors: 1 exact, 12 relocated, **0 quoting a line that is not in the file**, of 13
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
| 10 | `long long MOD = 10000000007LL;` | modulus for the result to avoid overflow |
| 11 | `long long totalWays = ((long long)stepPerms(n - 1) +` | compute total ways using the recurrence relation |
| 12 | `(long long)stepPerms(n - 2) +` | n‑1, n‑2, n‑3 |
| 13 | `(long long)stepPerms(n - 3)) % MOD;` | apply modular reduction to stay within 32‑bit range |
| 14 | `memo[n] = totalWays;` | store result for future calls |
| 15 | `return memo[n];` | return cached value |
| 20 | `int s;` | number of test cases |
| 21 | `cin >> s;` | read number of test cases |
| 22 | `while (s--)` | process each test case |
| 23 | `int n;` | current step count |
| 24 | `cin >> n;` | read step count |
| 25 | `cout << stepPerms(n) << endl;` | output result |
| 28 | `return 0;` | exiting the program |

**Explanation**

Purpose: Compute the number of distinct ways to climb a staircase of n steps, where one can take 1, 2, or 3 steps at a time.  
Input: An integer n representing the total number of steps.  
Output: An integer indicating the total number of distinct stepping sequences modulo 1 000 000 007.  
Algorithm: Uses a bottom‑up dynamic programming approach with memoization. For each step i (0 ≤ i ≤ n), it sums the counts of ways to reach the previous three steps, applying modulo 1 000 000 007 to avoid overflow. The base cases handle the trivial cases n = 0 and n < 0.

---

## dataset.jsonl#18 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 10 | `for (int i = 4; i <= n; i++)` | Iterate from the 4‑th step up to the target step. The recurrence relation for the number of ways to reach the i‑th step is a + b + c, where a, b, and c are the counts for the previous three steps. The loop runs O(n) time and O(1) extra space. |
| 11 | `current = (a + b + c) % MOD;` | Compute the next count modulo the required precision. |
| 12 | `a = b;` | Shift the previous counts forward. |
| 13 | `b = c;` | Shift the previous counts forward. |
| 14 | `c = current;` | Shift the previous counts forward. |
| 16 | `return current;` | Return the count for the target step. |

**Explanation**

Purpose: Compute the number of distinct ways to climb a staircase of n steps, where each step can be taken from 1, 2, or 3 steps at a time.  
Input: An integer n representing the total number of steps.  
Output: An integer representing the total number of distinct stepping sequences modulo 1 000 000 007.  
Algorithm: Uses a classic combinatorial recurrence (Fibonacci‑like) to count sequences, maintaining three previous values modulo 1 000 000 007 to avoid overflow. The loop runs from 4 to n, updating the current value with the sum of the three previous values.

---

## dataset.jsonl#19 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
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
| 10 | `while (modernSum > 0)` | Reduce the number to its single‑digit super‑digit recursively. |
| 14 | `initialSum *= k;` | Multiply the accumulated digit sum by the multiplier k. |
| 17 | `cin >> n >> k;` | Read the input string and multiplier from standard input. |
| 18 | `cout << superDigit(n, k) << endl;` | Output the super‑digit of the transformed number. |

**Explanation**

Purpose: Compute the super‑digit of a number formed by repeating a string k times.  
Input: `n` – a decimal string representing the base number; `k` – an integer repetition factor.  
Output: An `int` representing the final super‑digit.  
Algorithm: First, compute the sum of the digits of `n` multiplied by `k`. Then repeatedly reduce this sum modulo 9, stopping when the result is less than 9, which yields the super‑digit.

---

## dataset.jsonl#19 — iterative

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
| 3 | `for (char c : n)` | Compute the sum of the decimal digits of n. |
| 4 | `initial_sum += (c - '0');` | Convert each character to its numeric value and add to the running total. |
| 6 | `long long total_sum = initial_sum * k;` | Multiply the digit sum by the multiplier k. |
| 7 | `if (total_sum == 0)` | If the product is zero, the super‑digit is zero. |
| 9 | `long long result = total_sum % 9;` | The super‑digit is the remainder of total_sum modulo 9. |
| 10 | `return (result == 0) ? 9 : result;` | If the remainder is zero, the super‑digit is 9; otherwise it is the remainder. |

**Explanation**

Purpose: Compute the superdigit of a number formed by repeating a string k times.  
Input: `n` – a decimal string representing the number; `k` – an integer repetition factor.  
Output: An `int` representing the superdigit (0 if the final sum is 0).  
Algorithm: Convert `n` to an integer sum, multiply by `k`, then reduce modulo 9 to obtain the superdigit. Edge case: if the total sum is 0, return 0.

---

## dataset.jsonl#20 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 3 | `if (n == 0)` | Base case: stop recursion when the countdown reaches zero. |
| 6 | `printRecursion(n - 1);` | Recurse to the next lower value, ensuring the recursion depth is limited. |
| 7 | `cout << "I love Recursion" << endl;` | Print the final message after the recursive call. |
| 10 | `cin >> n;` | Read the user‑provided integer; the function assumes a non‑negative input. |
| 11 | `printRecursion(n);` | Start the recursion chain. |
| 12 | `return 0;` | Normal exit point. |

**Explanation**

Purpose: Prints the string "I love Recursion" n times using recursion.  
Input: An integer n specifying how many times to repeat the output.  
Output: No return value; writes the repeated string to standard output.  
Algorithm: The function checks for the base case n == 0 and returns early. Otherwise it recursively calls itself with n‑1, then prints the message, achieving a classic “factorial‑like” recursion.

---

## dataset.jsonl#20 — iterative

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
| 7 | `return 0;` | Normal exit point |

**Explanation**

Purpose: Prints the phrase "I love Recursion" exactly n times.  
Input: An integer n representing the number of repetitions.  
Output: No return value; writes n lines to standard output.  
Algorithm: Reads n from standard input, then iterates i from 0 to n‑1, outputting the phrase each iteration. No conditionals or loops are used; the loop simply repeats the statement.

---

## dataset.jsonl#21 — recursive

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
| 3 | `if (n == 0)` | Base case: stop recursion when the count reaches zero. |
| 6 | `printNumbers(n - 1);` | Recursively print all numbers from 1 to n‑1. |
| 7 | `cout << n << endl;` | After the recursive call, output the current number. |
| 10 | `cin >> n;` | Read the desired count from standard input. |
| 11 | `printNumbers(n);` | Start the recursive printing sequence. |
| 12 | `return 0;` | Normal exit. |

**Explanation**

Purpose: Prints all integers from 1 to n in ascending order.  
Input: An integer n – the upper bound of the sequence.  
Output: No return value; side‑effects are the printed numbers.  
Algorithm: Uses a simple recursive loop that decrements n each call, printing the current value after each recursive call. The base case stops the recursion when n reaches 0.

---

## dataset.jsonl#21 — iterative

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
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
| 3 | `cin >> n;` | Read the number of integers to output; assumes the input fits in an int. |
| 5 | `cout << i << endl;` | Output each integer from 1 to n, followed by a newline. |

**Explanation**

Purpose: Prints the first n positive integers to standard output.  
Input: An integer n specifying how many consecutive integers to output.  
Output: Writes each integer from 1 to n to std::cout, each followed by a newline.  
Algorithm: Reads the count, then iterates from 1 to n, outputting each iteration. No special handling for negative or zero inputs.

---

## dataset.jsonl#22 — recursive

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
| 3 | `if (n == 0)` | Base case: stop recursion when the input reaches zero. |
| 6 | `cout << n << endl;` | Output the current number followed by a newline. |
| 7 | `printNumbers(n - 1);` | Recursively print the next smaller number. |
| 10 | `cin >> n;` | Read the integer from standard input. |
| 11 | `printNumbers(n);` | Start the recursive printing process. |

**Explanation**

Purpose: Prints all positive integers from n down to 1 in ascending order.  
Input: An integer n (the starting count).  
Output: No return value; writes each number to standard output.  
Algorithm: Uses a simple recursive call that prints the current value, decrements n, and recurses until n reaches 0, effectively reversing the natural order.

---

## dataset.jsonl#22 — iterative

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
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
| 3 | `cin >> n;` | read the number of repetitions from the standard input |
| 5 | `cout << i << endl;` | output each integer from n down to 1, each followed by a newline |

**Explanation**

Purpose: Prints the integers from n down to 1, each followed by a newline.  
Input: An integer n read from standard input.  
Output: No return value; writes the sequence to standard output.  
Algorithm: Reads the integer, then iterates from n down to 1, outputting each value with a newline. The loop naturally handles the case where n is 0 or negative by skipping the loop body.

---

## dataset.jsonl#23 — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
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
| 10 | `while (T--)` | Process each test case independently. |
| 12 | `printDigits(n);` | Recurse to print the first digit, then the rest. |
| 13 | `cout << endl;` | End the line after the digit sequence. |

**Explanation**

Purpose: Prints each decimal digit of a non‑negative integer in ascending order.  
Input: Reads an integer T (test cases) and a sequence of long long integers n.  
Output: For each n, prints the digits of n in increasing order followed by a newline.  
Algorithm: Uses recursion to repeatedly divide n by 10, printing the remainder digit each time, until n becomes a single‑digit number, then prints that digit. The recursion naturally orders the digits.

---

## dataset.jsonl#23 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 4 | `cin >> T;` | read number of test cases |
| 6 | `while (T--)` | process each test case |
| 7 | `string n;` | read the integer represented as a string |
| 9 | `for (char digit : n)` | output each digit of the number |
| 12 | `cout << endl;` | end of current test case |

**Explanation**

Purpose: Prints each digit of a given integer as a separate space-separated character.  
Input: An integer `T` (number of test cases) followed by `T` strings `n`.  
Output: For each string, the digits are printed on a single line, each digit followed by a space.  
Algorithm: Read `T`, then for each `T` iterations read a string `n`. Iterate over each character of `n`, outputting it followed by a space, and finally output a newline. The loop repeats until all strings have been processed.

---

## dataset.jsonl#24 — recursive

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
| 7 | `decimalToBinary(n / 2);` | Recurse first to handle the higher‑order bits; the result is discarded. |
| 8 | `cout << n % 2;` | Output the current least‑significant bit. |
| 12 | `cin >> T;` | Read the number of test cases. |
| 14 | `while (T--)` | Process each test case. |
| 15 | `int n;` | Read the decimal number to convert. |
| 17 | `decimalToBinary(n);` | Convert the number to binary and output it. |
| 18 | `cout << endl;` | End the line for the current test case. |

**Explanation**

Purpose: Convert an integer to its binary representation and print it.  
Input: An integer `n` (the number to be converted).  
Output: Prints the binary representation of `n` to `std::cout`, followed by a newline.  
Algorithm: Uses recursion to repeatedly divide `n` by 2, collecting remainders in reverse order, and finally prints the collected bits.

---

## dataset.jsonl#24 — iterative

- anchors: 3 exact, 9 relocated, **0 quoting a line that is not in the file**, of 12
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
| 10 | `while (n > 0)` | Extract each binary digit from the least‑significant bit upwards. |
| 12 | `result += char('0' + (n % 2));` | Append the current bit as a character. |
| 13 | `n /= 2;` | Shift right to process the next bit. |
| 15 | `reverse(result.begin(), result.end());` | Reverse to obtain the correct binary representation. |
| 16 | `return result;` | Return the binary string. |
| 20 | `int T;` | Number of test cases. |
| 21 | `cin >> T;` | Read the number of test cases. |
| 23 | `while (T--)` | Process each test case. |
| 24 | `int n;` | Current decimal number. |
| 25 | `cin >> n;` | Read the decimal number. |
| 26 | `cout << decimalToBinary(n) << endl;` | Output the binary representation. |
| 28 | `return 0;` | Return success. |

**Explanation**

Purpose: Convert an integer from decimal to its binary representation.  
Input: An integer `n` (the number to convert).  
Output: A `std::string` containing the binary digits of `n` in little‑endian order.  
Algorithm: Repeatedly divide `n` by 2, appending the remainder to a result string, until `n` becomes zero. Finally reverse the string to obtain the correct binary order.

---

## dataset.jsonl#25 — recursive

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
| 4 | `if (index < 0)` | Stop recursion when the current index is negative; otherwise we would access an out‑of‑range element. |
| 7 | `if (index % 2 == 0)` | Print the element only if its position is even (0‑based indexing). |
| 10 | `printEvenIndices(a, index - 1);` | Recursively process the next index, ensuring the loop naturally stops at the first element. |
| 13 | `int n;` | Read the number of elements from standard input. |
| 15 | `vector<long long> a(n);` | Allocate a vector of long long to store the input sequence. |
| 16 | `for (int i = 0; i < n; i++)` | Read each element from standard input and store it in the vector. |
| 19 | `printEvenIndices(a, n - 1);` | Start the recursive printing from the last element, which is the only even‑indexed element in a non‑decreasing sequence. |
| 20 | `cout << endl;` | Output a newline to separate the result from any trailing output. |

**Explanation**

Purpose: Prints all elements at even indices of a vector in ascending order.  
Input: `vector<long long>& a` – the source vector; `int index` – the current position to examine.  
Output: Writes selected elements to `std::cout`, separated by spaces; returns `int` for compatibility with `main`.  
Algorithm: Recursively traverse the vector from the last element up to the first, skipping odd indices. When an even index is reached, output the element and recurse further. The recursion stops when the index reaches –1.

---

## dataset.jsonl#25 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 4 | `cin >> n;` | read number of elements |
| 5 | `vector<long long> a(n);` | allocate storage for the sequence |
| 6 | `for (int i = 0; i < n; i++)` | read all elements |
| 10 | `if (i % 2 == 0)` | output only elements at even positions (0‑based) |
| 13 | `cout << endl;` | terminate output line |

**Explanation**

Purpose: Prints the elements of a vector that are located at even indices.  
Input: An integer n followed by n long‑long integers.  
Output: Prints the selected elements to standard output, each separated by a space.  
Algorithm: Read the vector size, then iterate from the last element backwards, outputting only those elements whose index is even. Finally, output a newline.

---

## dataset.jsonl#26 — recursive

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
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
| 3 | `if (count == 0)` | Base case: stop recursion when the desired star count is zero |
| 6 | `cout << "*";` | Print the current star character |
| 7 | `printStars(count - 1);` | Recurse with one fewer star to build the next row |
| 11 | `if (current > n)` | Stop recursion when the current row exceeds the desired height |
| 14 | `printStars(current);` | Print the current row of stars |
| 15 | `cout << endl;` | Move to the next line after printing the row |
| 16 | `printPyramid(n, current + 1);` | Recursively generate the next row |
| 20 | `cin >> n;` | Read the desired height of the pyramid from standard input |
| 21 | `printPyramid(n);` | Start generating the pyramid |

**Explanation**

Purpose: Prints a right‑angled triangular pattern of asterisks.  
Input: An integer n specifying the number of rows (or columns) in the pattern.  
Output: Writes the pattern to standard output; no return value.  
Algorithm: Uses two recursive functions: printStars prints a row of stars, while printPyramid recursively prints each row, increasing the row count until it reaches n. The recursion stops when the current row exceeds n.

---

## dataset.jsonl#26 — iterative

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
| 3 | `cin >> n;` | read the number of rows (and columns) from the user |
| 5 | `for (int i = 1; i <= n; i++)` | iterate over each row |
| 6 | `for (int j = 1; j <= i; j++)` | print the required number of '*' characters for the current row |
| 10 | `return 0;` | normal exit point |

**Explanation**

Purpose: Prints a right‑angled triangle composed of asterisks.  
Input: An integer n specifying the number of rows (and columns) in the triangle.  
Output: Writes the triangle to standard output, each row followed by a newline.  
Algorithm: Reads n, then iterates i from 1 to n, printing i asterisks per row and a newline after each row. The nested loops achieve the triangular shape.

---

## dataset.jsonl#27 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 10 | `cout << "*";` | Print the current row of stars |
| 11 | `printStars(n - 1);` | Recurse to print the remaining rows |
| 15 | `cout << endl;` | End the current row with a newline |
| 16 | `printPyramid(n - 1);` | Recurse to print the next row |
| 20 | `cin >> n;` | Read the desired height of the pyramid |
| 21 | `printPyramid(n);` | Generate and display the pyramid |

**Explanation**

Purpose: Prints a right‑angled triangular pattern of asterisks.  
Input: An integer n specifying the number of rows (including the base).  
Output: Writes the pattern to standard output, each row followed by a newline.  
Algorithm: Uses two recursive helper functions: printStars prints n asterisks, printPyramid prints n rows, each followed by a newline. The recursion stops when n reaches zero.

---

## dataset.jsonl#27 — iterative

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
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
| 7 | `cout << "*";` | output a single asterisk |
| 8 | `}` | note: the original code had a typo here; the loop body should be indented |
| 9 | `cout << endl;` | end the current row with a newline |
| 11 | `return 0;` | success exit code |

**Explanation**

Purpose: Prints a descending staircase pattern of asterisks.  
Input: An integer n representing the number of rows in the staircase.  
Output: Writes the staircase to standard output, each row followed by a newline.  
Algorithm: Reads n, then iterates i from n down to 1, printing i asterisks per row and a newline after each row. The loop naturally produces a descending staircase.

---

## dataset.jsonl#28 — recursive

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
| 10 | `if (index == s.length())` | Base case: when we have processed the whole string, count is zero. |
| 13 | `return isVowel(s[index]) + countVowels(s, index + 1);` | Count the current character if it is a vowel, then recurse for the next position. |
| 17 | `string s;` | Read the entire input line into a string. |
| 18 | `getline(cin, s);` | Read the whole line; getline strips the trailing newline. |
| 19 | `cout << countVowels(s, 0) << endl;` | Output the total number of vowels in the string. |

**Explanation**

Purpose: Counts the number of vowels in a given string starting from a specified index.  
Input: `const string& s` – the source text; `int index` – the zero‑based position to begin counting.  
Output: `int` – total count of vowels in `s` from `index` to the end.  
Algorithm: Recursively examine each character at `index`; if it is a vowel, add one to the accumulator; otherwise add zero. The recursion stops when `index` reaches the string length.

---

## dataset.jsonl#28 — iterative

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 3 | `return c == 'a' \|\| c == 'e' \|\| c == 'i' \|\| c == 'o' \|\| c == 'u' \|\|` | Returns true if the character is a lowercase vowel (a‑z). Note: no case‑insensitive check is performed; only vowels are counted. |
| 10 | `getline(cin, s);` | Read the whole line into a string; assumes the input fits within the string's capacity. |
| 12 | `for (char c : s)` | Iterate over each character in the string; the loop variable is a copy of the character. |
| 13 | `if (isVowel(c))` | Increment the vowel count only if the character is a vowel. |
| 16 | `cout << count << endl;` | Output the total number of vowels found. |

**Explanation**

Purpose: Counts the number of vowels in a given string.  
Input: A std::string containing the text to be examined.  
Output: An int representing the total count of vowels in the string.  
Algorithm: Reads the entire line from standard input, then iterates over each character, using a simple vowel‑check predicate to increment a counter for each vowel encountered. Finally, it prints the counter.

---

## dataset.jsonl#29 — recursive

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
| 3 | `if (n <= 1)` | Base case: factorial of 0 or 1 is defined as 1 |
| 6 | `return n * factorial(n - 1);` | Recursive step: multiply current number by factorial of (n‑1) |
| 10 | `cin >> n;` | Read input integer; assumes the caller guarantees a valid n |
| 11 | `cout << factorial(n) << endl;` | Output the computed factorial followed by a newline |

**Explanation**

Purpose: Computes the factorial of a non‑negative integer.  
Input: An integer n (expected to be ≥ 0).  
Output: A long long representing n! (or 1 for n ≤ 1).  
Algorithm: Uses a simple recursive definition: factorial(0) = 1, factorial(n) = n * factorial(n‑1). The recursion terminates when n ≤ 1, returning 1. The result is printed to standard output.

---

## dataset.jsonl#29 — iterative

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
| 3 | `cin >> n;` | read the number whose factorial is to be computed |
| 5 | `long long result = 1;` | start with 1! = 1 (factorial of 0 or 1) |
| 6 | `for (int i = 2; i <= n; i++)` | multiply by each integer from 2 up to n inclusive |
| 7 | `result *= i;` | accumulate product; using *= avoids overflow for large n |
| 9 | `cout << result << endl;` | output the computed factorial |

**Explanation**

Purpose: Computes the factorial of a given integer.  
Input: Reads an integer `n` from standard input.  
Output: Prints the factorial value of `n` to standard output.  
Algorithm: Initializes a result variable to 1, then iteratively multiplies it by each integer from 2 up to `n`. Finally, outputs the accumulated product.

---

## dataset.jsonl#30 — recursive

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
| 10 | `return max(a[n - 1], findMax(a, n - 1));` | Recursively compute the maximum of the current element and the maximum of the rest of the array. |
| 13 | `cin >> n;` | Read the number of elements. |
| 14 | `vector<long long> a(n);` | Allocate space for the input array. |
| 15 | `for (int i = 0; i < n; i++)` | Read each element of the array. |
| 18 | `cout << findMax(a, n) << endl;` | Output the maximum value. |

**Explanation**

Purpose: Compute the maximum element in a vector of long long integers.  
Input: const vector<long long>& a – the sequence to examine; int n – number of elements to consider.  
Output: long long – the largest value among the first n elements.  
Algorithm: If n equals 1, return the single element. Otherwise, recursively find the maximum of the last element and the maximum of the rest of the vector, then return the larger of the two. The recursion stops when only one element remains.

---

## dataset.jsonl#30 — iterative

- anchors: 0 exact, 1 relocated, **0 quoting a line that is not in the file**, of 1
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
| 10 | `cout << maximum << endl;` | Output the largest element found in the array. |

**Explanation**

Purpose: Find and print the largest integer in a sequence.  
Input: An integer n followed by n long‑long integers.  
Output: Prints the maximum value to standard output; returns 0.  
Algorithm: Read the first element as the initial maximum, then iterate from the second element, updating the maximum whenever a larger value is encountered. Finally, output the maximum.

---

## dataset.jsonl#31 — recursive

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
| 3 | `if (n == 0)` | Base case: when the sub‑array has zero elements, the sum is zero. |
| 6 | `return a[n - 1] + sum(a, n - 1);` | Recursive step: add the last element of the current sub‑array to the sum of the rest. |
| 10 | `cin >> n;` | Read the number of elements in the array. |
| 11 | `vector<long long> a(n);` | Allocate a vector of length n to hold the input values. |
| 12 | `for (int i = 0; i < n; i++)` | Read each element from standard input. |
| 15 | `cout << sum(a, n) << endl;` | Output the computed sum. |

**Explanation**

Purpose: Compute the sum of the first n elements of a long‑long integer vector.  
Input: `const vector<long long>& a` – the vector to sum; `int n` – number of elements to include.  
Output: `long long` – the total sum of the selected elements.  
Algorithm: Uses a simple recursive reduction: if n is zero, return 0; otherwise return a[n‑1] plus the sum of the vector up to n‑1. The recursion unwinds, accumulating the sum.

---

## dataset.jsonl#31 — iterative

- anchors: 0 exact, 2 relocated, **0 quoting a line that is not in the file**, of 2
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
| 10 | `for (int i = 0; i < n; i++)` | Compute the sum of all elements in the array. |
| 13 | `cout << total << endl;` | Output the accumulated sum. |

**Explanation**

Purpose: Compute the sum of the first n integers read from standard input.  
Input: An integer n specifying the number of elements, followed by n long‑long integers.  
Output: Prints the accumulated sum to standard output.  
Algorithm: Read the count, allocate a vector of that size, read the values, add them together, and output the total. Edge cases such as n ≤ 0 or overflow are not handled.

---

## dataset.jsonl#32 — recursive

- anchors: 1 exact, 3 relocated, **0 quoting a line that is not in the file**, of 4
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
| 13 | `cin >> n >> m;` | Read the number of elements and the required suffix length. |
| 15 | `cin >> a[i];` | Read each element of the array. |
| 18 | `cout << suffixSum(a, n - 1, m) << endl;` | Output the computed suffix sum. |

**Explanation**

Purpose: Compute the sum of the last m elements of a vector.  
Input: `a` – a vector of long long integers; `index` – the starting position (0‑based); `m` – the number of elements to sum.  
Output: A long long representing the sum of the suffix.  
Algorithm: Recursively add the current element to the result of the suffix sum of the preceding element, stopping when `m` reaches zero. The base case returns 0.

---

## dataset.jsonl#32 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
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
| 10 | `for (int i = n - m; i < n; i++)` | Compute the sum of the last m elements of the array. |
| 11 | `sum += a[i];` | Accumulate the selected elements. |
| 12 | `cout << sum << endl;` | Output the total sum. |

**Explanation**

Purpose: Compute the sum of the last m elements of a sequence of n integers.  
Input: n – number of elements; m – number of elements to sum from the end (0 ≤ m ≤ n).  
Output: Prints the computed sum to standard output.  
Algorithm: Read the whole sequence, then iterate over the last m elements, accumulating their values in a running total. Finally output the total.

---

## dataset.jsonl#33 — recursive

- anchors: 1 exact, 4 relocated, **0 quoting a line that is not in the file**, of 5
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
| 10 | `cout << A[r][c] + B[r][c];` | Output the element of the first matrix. |
| 11 | `if (c == C - 1)` | If we are at the last column of the current row, start a new line. |
| 12 | `cout << endl;` | End the current row. |
| 13 | `sumMatrix(A, B, r + 1, 0, R, C);` | Move to the next row, reset column to 0, and recurse. |
| 14 | `cout << " ";` | If not at the last column, output a space and continue to the next column. |

**Explanation**

Purpose: Compute the element‑wise sum of two square matrices and print the result in a single‑column format.  
Input: Two R×C matrices A and B, each stored as R rows of C long‑long columns.  
Output: Prints the sum of the two matrices to standard output, each element separated by a space and each row terminated by a newline.  
Algorithm: Recursively traverse the matrices row‑wise, adding the corresponding elements. When a column reaches the last row, output a newline and move to the next row; otherwise output a space and continue to the next column.

---

## dataset.jsonl#33 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 18 | `for (int i = 0; i < R; i++)` | Perform element‑wise addition and output |
| 20 | `cout << A[i][j] + B[i][j];` | Add corresponding entries and output |
| 21 | `if (j < C - 1)` | Separate columns with a space except for the last one |
| 23 | `cout << endl;` | End the current row |

**Explanation**

Purpose: Adds corresponding elements of two R×C integer matrices and prints the result.  
Input: Reads R and C (matrix dimensions) followed by R*C integers for each matrix.  
Output: Prints R rows of C space‑separated sums, each row followed by a newline.  
Algorithm: Allocates two R×C vectors, reads the first matrix, reads the second, then iterates over the rows and columns, adding the elements and outputting the sum. Edge cases such as empty matrices are not handled.

---

## dataset.jsonl#34 — recursive

> **names a container the code does not use**

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: none

  - *container NOT in the code*: The recursion repeats indefinitely for large n, leading to exponential time and stack overflow.

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
| 3 | `if (n == 1)` | Base case: the first Fibonacci number is 0. |
| 4 | `if (n == 2)` | Base case: the second Fibonacci number is 1. |
| 5 | `return fibonacci(n - 1) + fibonacci(n - 2);` | Recursive definition: each term equals the sum of the two preceding ones. |
| 9 | `cin >> n;` | Read the desired index from standard input. |
| 10 | `cout << fibonacci(n) << endl;` | Output the n‑th Fibonacci number. |

**Explanation**

Purpose: Computes the n‑th Fibonacci number using a naive recursive definition.  
Input: An integer n representing the position in the sequence.  
Output: A long long containing the Fibonacci number Fₙ.  
Algorithm: Handles the base cases n = 1 and n = 2 directly. For n > 2 it recursively calls itself with n‑1 and n‑2, accumulating the sum. The recursion repeats indefinitely for large n, leading to exponential time and stack overflow.

---

## dataset.jsonl#34 — iterative

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
| 3 | `cin >> n;` | read the number of terms to generate |
| 5 | `long long a = 0, b = 1;` | initialize the first two Fibonacci numbers |
| 7 | `for (int i = 1; i < n; i++)` | generate the next n‑1 terms using the classic loop |
| 8 | `long long c = a + b;` | compute the next Fibonacci number |
| 9 | `a = b;` | shift the sequence forward |
| 11 | `cout << a << endl;` | output the last term (Fibonacci(n)) |

**Explanation**

Purpose: Compute the nth Fibonacci number.  
Input: An integer n specifying the position in the sequence.  
Output: Prints the n‑th Fibonacci number as a long long to standard output.  
Algorithm: Initialize two variables to the first two Fibonacci numbers (0, 1). Repeatedly add the last two numbers to obtain the next number, updating the variables accordingly until the desired index is reached. The final value is printed.

---

## dataset.jsonl#35 — recursive

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
| 3 | `if (n < 2)` | Base case: the smallest power of two is 2, so log2Floor(1) returns 0. |
| 5 | `return 1 + log2Floor(n / 2);` | Recursive step: compute log2Floor for the halved value, then add 1 for the current factor of 2. |
| 9 | `cin >> n;` | Read the input number; assumes the caller guarantees a non‑negative unsigned value. |
| 10 | `cout << log2Floor(n) << endl;` | Output the floor of the base‑2 logarithm of the input. |

**Explanation**

Purpose: Compute the greatest integer k such that 2^k ≤ n.  
Input: An unsigned long long n – the number whose binary logarithm floor is required.  
Output: An int representing the floor of log₂(n).  
Algorithm: Recursively halve n while subtracting one from the result each time, stopping when n becomes less than 2. The recursion depth equals the floor of log₂(n). The final result is returned as an int.

---

## dataset.jsonl#35 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 4 | `cin >> n;` | read the input integer |
| 6 | `long long answer = 0;` | count how many times we can halve n |
| 7 | `while (n >= 2)` | continue while n is still greater than or equal to 2 |
| 8 | `n /= 2;` | halve n; integer division truncates towards zero |
| 9 | `answer++;` | increment the count of halving operations |
| 12 | `cout << answer << endl;` | output the total number of halving steps |

**Explanation**

Purpose: Counts how many times the integer can be halved before it becomes less than 2.  
Input: Reads an unsigned 64‑bit integer from standard input.  
Output: Prints the count of halving operations to standard output.  
Algorithm: Initializes a counter to zero, repeatedly divides the input by 2 while the result is at least 2, incrementing the counter each time. After the loop, outputs the counter.

---

## dataset.jsonl#36 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 3 | `if (n == 1)` | Base case: the sequence starting with 1 contains exactly one term. |
| 6 | `if (n % 2 == 0)` | If n is even, the next term is n/2, which reduces the problem size. |
| 9 | `return 1 + sequenceLength(3 * n + 1);` | If n is odd, the next term is 3*n+1, which grows the sequence exponentially. |
| 13 | `cin >> n;` | Read the starting number from standard input. |
| 14 | `cout << sequenceLength(n) << endl;` | Output the length of the Collatz sequence for the given n. |

**Explanation**

Purpose: Computes the length of the Collatz sequence starting from n.  
Input: long long n – the initial term of the sequence.  
Output: long long – the total number of terms in the sequence.  
Algorithm: Uses a simple recursive definition: if n is 1, the length is 1; otherwise it adds one and recurses on n/2 for even n or 3*n+1 for odd n. The recursion terminates when n reaches 1.

---

## dataset.jsonl#36 — iterative

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
| 4 | `cin >> n;` | read the starting integer |
| 6 | `long long length = 1;` | length of the Collatz sequence so far |
| 7 | `while (n != 1)` | continue until the sequence reaches 1 |
| 8 | `if (n % 2 == 0)` | even case: divide by 2 |
| 10 | `n = 3 * n + 1;` | odd case: apply the Collatz rule |
| 12 | `length++;` | count the step |
| 15 | `cout << length << endl;` | output the total length |

**Explanation**

Purpose: Computes the length of the Collatz sequence starting from n.  
Input: A single long long n read from standard input.  
Output: Prints the integer length of the sequence to standard output.  
Algorithm: Repeatedly apply the Collatz rule (n → n/2 if even, n → 3n+1 if odd) while n ≠ 1, incrementing a counter each iteration. The final counter value is printed.

---

## dataset.jsonl#37 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
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
| 3 | `if (left >= right)` | Base case: when the sub‑array has zero or one element, it is trivially a palindrome. |
| 5 | `if (a[left] != a[right])` | If the first and last elements differ, the whole segment cannot be a palindrome. |
| 8 | `return isPalindrome(a, left + 1, right - 1);` | Recursively test the inner segment; the function assumes the outer pair is already verified. |
| 12 | `cin >> n;` | Read the number of elements; the vector will be resized accordingly. |
| 14 | `for (int i = 0; i < n; i++)` | Read the sequence of integers; the vector is populated with the input values. |
| 17 | `cout << "YES" << endl;` | If the whole array is a palindrome, output "YES". |
| 18 | `else` | Otherwise, output "NO". |

**Explanation**

Purpose: Determines whether a sequence of long long integers is a palindrome.  
Input: `n` – size of the vector; `a` – vector of long long integers.  
Output: `YES` if `a` is a palindrome, otherwise `NO`.  
Algorithm: Recursively compares the first and last elements; if they differ, returns false. Otherwise, it recurses on the inner segment, stopping when the indices meet or cross.

---

## dataset.jsonl#37 — iterative

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
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
| 10 | `for (int i = 0; i < n / 2; i++)` | Compare mirrored positions to detect a palindrome. |
| 11 | `if (a[i] != a[n - 1 - i])` | If any pair differs, the sequence cannot be a palindrome. |
| 12 | `palindrome = false;` | Early exit: a mismatch marks the sequence as non‑palindrome. |
| 15 | `if (palindrome)` | Output the result based on the palindrome flag. |

**Explanation**

Purpose: Determines whether a sequence of integers reads the same forwards and backwards.  
Input: Reads an integer n followed by n long‑long integers.  
Output: Prints "YES" if the sequence is a palindrome, otherwise "NO".  
Algorithm: Constructs a vector from the input, then scans the first half of the vector against the mirrored counterpart; if any pair differs, the palindrome flag is cleared and the loop breaks. Finally, prints the appropriate verdict.

---

## dataset.jsonl#38 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 10 | `return a[n - 1] + sum(a, n - 1);` | Base case: when n == 0, the sum is 0. Otherwise, add the last element of the vector to the sum of the rest of the vector. |
| 14 | `cin >> n;` | Read the number of elements from standard input. |
| 15 | `vector<long long> a(n);` | Allocate a vector to store the input numbers. |
| 16 | `for (int i = 0; i < n; i++)` | Read each element of the vector from standard input. |
| 19 | `double average = sum(a, n) / n;` | Compute the arithmetic mean by dividing the total sum by the count. |
| 20 | `cout << fixed << setprecision(6) << average << endl;` | Output the average with 6 decimal places. |

**Explanation**

Purpose: Compute the arithmetic mean of the first n elements of a long‑long integer array.  
Input: n – size of the array; a – vector of long long containing the elements.  
Output: double – the mean of the first n elements, rounded to six decimal places.  
Algorithm: Uses a simple recursive sum function that adds the last element of the vector to the sum of the rest of the vector, terminating when the index reaches zero. The final average is obtained by dividing the accumulated sum by n. The result is printed with fixed‑point precision.

---

## dataset.jsonl#38 — iterative

- anchors: 0 exact, 3 relocated, **0 quoting a line that is not in the file**, of 3
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
| 10 | `for (int i = 0; i < n; i++)` | Read each element and accumulate its sum |
| 14 | `double average = (double)total / n;` | Compute the arithmetic mean; cast total to double to avoid overflow |
| 15 | `cout << fixed << setprecision(6) << average << endl;` | Output the average with 6 decimal places |

**Explanation**

Purpose: Compute and output the arithmetic mean of a sequence of integers.  
Input: Reads an integer n followed by n long‑long integers.  
Output: Prints a double‑precision floating‑point average rounded to six decimal places.  
Algorithm: Reads all n values, sums them, divides by n, and prints the result. Edge cases such as n = 0 or a single‑element sequence are not handled.

---

## dataset.jsonl#39 — recursive

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
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
| 3 | `if (r == 0 \|\| r == n)` | Base case: empty set or full set → exactly one way to choose 0 or n elements |
| 7 | `return combination(n - 1, r - 1) + combination(n - 1, r);` | Recursive formula: sum of combinations of (n‑1) elements with (r‑1) and (n‑1) with r |
| 11 | `cin >> n >> r;` | Read input: n is total number of elements, r is number of elements to choose |
| 12 | `if (r > n)` | If r exceeds n, it's impossible to choose more elements than are available → zero combinations |
| 13 | `cout << 0 << endl;` | Output: 0 if r > n, otherwise compute and output the binomial coefficient |

**Explanation**

Purpose: Computes the binomial coefficient C(n, r) using recursion.  
Input: Two integers n and r representing the combination size and position.  
Output: Prints the coefficient as a long long; prints 0 if r exceeds n.  
Algorithm: Uses the classic recursive formula C(n, r) = C(n‑1, r‑1) + C(n‑1, r) with base cases C(0,0)=C(n,0)=1. The recursion unwinds until it reaches the base cases, accumulating the sum of all possible combinations.

---

## dataset.jsonl#39 — iterative

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
| 4 | `cin >> n >> r;` | read input: n = total items, r = number of items to choose |
| 6 | `cout << 0 << endl;` | if r exceeds n, the selection is impossible → result is 0 |
| 10 | `for (int i = 1; i <= r; i++)` | compute the binomial coefficient C(n, r) using the multiplicative formula |
| 11 | `result = result * (n - i + 1) / i;` | multiply by (n‑i+1) and divide by i to avoid overflow |
| 13 | `cout << result << endl;` | output the computed value |

**Explanation**

Purpose: Compute the number of ways to choose r items from n distinct items without repetition and order mattering.  
Input: Two integers n (total items) and r (items to choose).  
Output: Prints an integer representing the combinatorial result (0 if r > n).  
Algorithm: If r exceeds n, output 0 immediately. Otherwise, iteratively multiply (n‑i+1) by the running product, dividing by i each step to avoid overflow and keep the result integral. The final product is printed.

---

## dataset.jsonl#40 — recursive

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
| 10 | `if (index == 0 \|\| capacity == 0)` | Base case: either no items left or no capacity left → optimal value is 0 |
| 12 | `if (weight[index - 1] > capacity)` | Item cannot fit: skip it and move to the next item |
| 15 | `return max(` | Choose the best between skipping the current item or including it |
| 16 | `knapsack(weight, value, index - 1, capacity),` | skip current item |
| 17 | `value[index - 1] + knapsack(weight, value, index - 1, capacity - weight[index - 1])` | include current item, reducing remaining capacity by its weight |
| 20 | `int n, W;` | Read number of items and knapsack capacity from standard input |
| 22 | `vector<int> weight(n), value(n);` | Store weights and values of each item |
| 24 | `for (int i = 0; i < n; i++)` | Read item weights and values from standard input |
| 27 | `cout << knapsack(weight, value, n, W) << endl;` | Output the maximum total value that can be packed into the knapsack |

**Explanation**

Purpose: Compute the maximum total value achievable in a knapsack with given item weights and values, using at most a specified capacity.  
Input: `weight` – vector of item weights; `value` – vector of item values; `index` – current item to consider; `capacity` – remaining capacity.  
Output: `long long` – maximum total value for the knapsack.  
Algorithm: Uses a recursive depth‑first search with memoization, pruning branches where the item cannot fit, and returns the best achievable value for the remaining items and capacity. The base case handles empty list or zero capacity, and the recursive case selects the optimal choice between skipping the item or including it.

---

## dataset.jsonl#40 — iterative

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
| 10 | `for (int i = 0; i < n; i++)` | read item weights and values |
| 14 | `vector<vector<long long>> dp(n + 1, vector<long long>(W + 1, 0));` | dp[i][w] = maximum value obtainable with first i items and total weight ≤ w |
| 16 | `for (int i = 1; i <= n; i++)` | iterate over each item |
| 17 | `for (int w = 0; w <= W; w++)` | iterate over possible total weight |
| 18 | `dp[i][w] = dp[i - 1][w];` | skip current item when it cannot fit |
| 19 | `if (weight[i - 1] <= w)` | consider taking the item |
| 20 | `dp[i][w] = max(dp[i][w], value[i - 1] + dp[i - 1][w - weight[i - 1]]);` | take the item and update best value |
| 23 | `cout << dp[n][W] << endl;` | output optimal total value |

**Explanation**

Purpose: Solve the 0/1 knapsack problem to find the maximum total value that can be packed into a knapsack of capacity W.  
Input: n (number of items), W (knapsack capacity), weight[i] (weight of item i), value[i] (value of item i).  
Output: Prints the maximum achievable value as an integer.  
Algorithm: Dynamic programming builds a table dp[i][w] where dp[i][w] stores the best value for the first i items with a knapsack capacity of w. For each item, it either skips it or takes it, updating the table accordingly. The final answer is dp[n][W].

---

## dataset.jsonl#41 — recursive

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
| 10 | `return canMake(a, index + 1, current + a[index], target) \|\|` | Try adding the current element to the running sum and continue. |
| 11 | `canMake(a, index + 1, current - a[index], target);` | Try subtracting the current element from the running sum and continue. |
| 14 | `return current == target;` | If we reached the end of the array, we have a valid combination. |
| 17 | `cin >> n >> x;` | Read the number of elements and the target sum. |
| 19 | `cin >> a[i];` | Read each element of the array. |
| 22 | `cout << "YES" << endl;` | A valid combination exists. |
| 23 | `else` | No valid combination. |

**Explanation**

Purpose: Determines whether the sum of any subset of a given list of integers equals a specified target.  
Input: `n` – number of elements in `a`; `x` – target sum; `a` – vector of long long integers.  
Output: `YES` if such a subset exists, otherwise `NO`.  
Algorithm: Uses depth‑first recursion with backtracking; at each position it tries adding or subtracting the current element to the running total, and continues recursively until the end. The recursion stops when the index reaches the end and the total matches the target.

---

## dataset.jsonl#41 — iterative

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
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
| 10 | `for (int i = 0; i < n; i++)` | read the sequence of integers |
| 14 | `vector<long long> sums;` | will hold all possible sums after adding/removing each element |
| 15 | `sums.push_back(a[0]);` | initial sum: a[0] (no elements added) |
| 16 | `for (int i = 1; i < n; i++)` | iterate over each element to extend the sum set |
| 17 | `vector<long long> next;` | temporary container for the next generation of sums |
| 18 | `for (long long sum : sums)` | generate all possible sums by adding/removing the current element |
| 21 | `sums = next;` | replace the current set with the new generation |
| 24 | `bool found = false;` | flag to indicate whether the target sum was found |
| 25 | `for (long long sum : sums)` | search for the target sum in the current set |
| 28 | `found = true;` | target sum exists |
| 30 | `break;` | stop early to avoid unnecessary work |
| 32 | `cout << (found ? "YES" : "NO") << endl;` | output the result |

**Explanation**

Purpose: Determine whether any two distinct elements in an array sum to a given target.  
Input: n (size of the array), x (target sum), a[0..n‑1] (array elements).  
Output: Prints "YES" if such a pair exists, otherwise "NO".  
Algorithm: Build a list of all possible sums of the first element with each subsequent element, repeatedly doubling the list size by adding and subtracting the next element. After the doubling, scan the list for the target sum; if found, report success.

---

## dataset.jsonl#42 — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
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
| 8 | `return canReach(n / 10) \|\| (n % 20 == 0 && canReach(n / 20));` | Recurse on the number without its last digit; if that works, we are done. If the number ends in 0, try removing the last two digits (n % 20 == 0) and recurse again. This handles the two-digit case efficiently. |
| 12 | `cin >> t;` | Read the number of test cases. |
| 14 | `while (t--)` | Process each test case. |
| 15 | `long long n;` | Read the current number. |
| 17 | `cout << (canReach(n) ? "YES" : "NO") << endl;` | Output the result: "YES" if reachable, otherwise "NO". |

**Explanation**

Purpose: Determines whether a positive integer can be reduced to 1 by repeatedly removing its last digit until only 1 remains.  
Input: An integer n (1 ≤ n ≤ 10^18) representing the number to test.  
Output: Prints “YES” if the number can be reduced to 1, otherwise “NO”.  
Algorithm: Uses a depth‑first search with backtracking. If the current number is 1, return true; otherwise, if the last digit is not 0, return false. For each digit, try removing it and recursively checking both the reduced number and the number formed by removing the next two digits (if possible).

---

## dataset.jsonl#42 — iterative

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
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
| 10 | `while (n % 10 == 0 && n > 1)` | Keep dividing by 10 while the last digit is zero and n is greater than 1. |
| 11 | `if (n % 20 == 0)` | If the resulting number is divisible by 20, we can safely remove a factor of 20. |
| 12 | `n /= 20;` | Remove a factor of 20. |
| 13 | `else` | Otherwise, remove a factor of 10. |
| 14 | `n /= 10;` | Remove a factor of 10. |
| 16 | `cout << (n == 1 ? "YES" : "NO") << endl;` | Output "YES" if the final number is 1, otherwise "NO". |

**Explanation**

Purpose: Determines whether each integer n can be reduced to 1 by repeatedly dividing by 10 or 20 while keeping the result divisible by 10.  
Input: An integer t (test cases) followed by t long long integers n.  
Output: For each n, prints "YES" if it can be reduced to 1, otherwise "NO".  
Algorithm: For each n, repeatedly divide by 20 if possible, otherwise by 10, until n becomes 1 or cannot be reduced further. Finally, compare n to 1 and output the result.

---

## dataset.jsonl#43 — recursive

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
| 12 | `if (i == n - 1)` | If we are on the last row, only the right‑most column remains. |
| 14 | `if (j == m - 1)` | If we are on the last column, only the bottom row remains. |
| 16 | `return a[i][j] + max(maxPathSum(a, i + 1, j, n, m), maxPathSum(a, i, j + 1, n, m));` | Otherwise, choose the maximum of the two possible next moves and add the current cell's value. |
| 20 | `int n, m;` | Read the grid dimensions from standard input. |
| 22 | `vector<vector<long long>> a(n, vector<long long>(m));` | Allocate a 2‑D vector to store the grid values. |
| 24 | `for (int i = 0; i < n; i++)` | Read the grid entries row‑by‑row. |
| 28 | `cout << maxPathSum(a, 0, 0, n, m) << endl;` | Compute and output the maximum path sum from the top‑left to the bottom‑right. |

**Explanation**

Purpose: Compute the maximum sum of a strictly increasing path from the top‑left to the bottom‑right of a rectangular grid.  
Input: `a` – `n × m` 2‑D vector of long‑long integers; `i`, `j` – start cell indices (0‑based).  
Output: `long long` – the maximal achievable path sum.  
Algorithm: Uses depth‑first recursion with memoization, exploring three sub‑problems: reaching the last row, the last column, or any other interior cell. The function returns the sum of the current cell plus the maximum of the two possible continuation paths, terminating when the destination cell is reached.

---

## dataset.jsonl#43 — iterative

- anchors: 0 exact, 9 relocated, **0 quoting a line that is not in the file**, of 9
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
| 10 | `for (int i = 0; i < n; i++)` | read the matrix row‑wise |
| 14 | `dp[0][0] = a[0][0];` | base case: first element of the first row |
| 15 | `for (int i = 1; i < n; i++)` | fill first row: dp[i][0] = dp[i‑1][0] + a[i][0] |
| 16 | `dp[i][0] = dp[i - 1][0] + a[i][0];` | each element is the sum of the previous element and the current cell value |
| 17 | `for (int j = 1; j < m; j++)` | fill first column: dp[0][j] = dp[0][j‑1] + a[0][j] |
| 18 | `dp[0][j] = dp[0][j - 1] + a[0][j];` | each element is the sum of the previous element and the current cell value |
| 19 | `for (int i = 1; i < n; i++)` | fill interior cells: dp[i][j] = a[i][j] + max(dp[i‑1][j], dp[i][j‑1]) |
| 20 | `dp[i][j] = a[i][j] + max(dp[i - 1][j], dp[i][j - 1]);` | choose the larger of the two adjacent cells and add the current cell value |
| 22 | `cout << dp[n - 1][m - 1] << endl;` | output the optimal path sum |

**Explanation**

Purpose: Compute the maximum sum of a path from the top‑left to the bottom‑right of a grid.  
Input: Two integers n and m specify the grid dimensions, followed by n·m long‑long values representing the grid cells.  
Output: Prints the maximal achievable sum as an integer.  
Algorithm: Initialise a DP table with the first cell’s value. Fill the first row and column using the previous cell’s value plus the current cell’s value. For all other cells, the optimal sum is the maximum of the cell above or to the left plus the current cell’s value. The final cell holds the answer.

---

## dataset.jsonl#44 — recursive

- anchors: 0 exact, 6 relocated, **0 quoting a line that is not in the file**, of 6
- containers in the code: none

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
| 3 | `if (s == e)` | Base case: only one way to reach the target when both start and end are the same. |
| 6 | `if (s > e)` | If the start exceeds the end, it's impossible to reach the end, so return 0. |
| 9 | `return ways(s + 1, e) + ways(s + 2, e) + ways(s + 3, e);` | Recursive case: count the number of ways to reach the end from each of the three possible next steps. |
| 13 | `int s, e;` | Read start and end positions from standard input. |
| 14 | `cin >> s >> e;` | Note: no validation of input ranges is performed. |
| 15 | `cout << ways(s, e) << endl;` | Output the total number of ways to reach the end. |

**Explanation**

Purpose: Compute the number of ways to reach position e starting from s moving one, two, or three steps at a time.  
Input: Two integers s and e representing the start and end positions (inclusive).  
Output: A long long integer indicating the total count of reachable positions.  
Algorithm: Uses a simple recursive back‑tracking approach that adds three recursive calls for each step size, returning 1 when the target is reached, 0 when the start exceeds the end, and otherwise summing the three possibilities. The recursion naturally handles the trivial case s == e.

---

## dataset.jsonl#44 — iterative

- anchors: 0 exact, 10 relocated, **0 quoting a line that is not in the file**, of 10
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
| 3 | `int s, e;` | read inclusive start and end indices |
| 4 | `cin >> s >> e;` | input format: s e |
| 6 | `long long dp[16] = {};` | DP table: dp[i] = number of ways to reach i |
| 7 | `dp[s] = 1;` | base case: only one way to reach s |
| 9 | `dp[i] = dp[i - 1];` | extend previous count |
| 10 | `if (i - 2 >= s)` | add count from i‑2 only if it lies within the range |
| 11 | `dp[i] += dp[i - 2];` | extend previous count |
| 12 | `if (i - 3 >= s)` | add count from i‑3 only if it lies within the range |
| 13 | `dp[i] += dp[i - 3];` | extend previous count |
| 15 | `cout << dp[e] << endl;` | output total ways to reach e |

**Explanation**

Purpose: Compute the number of ways to reach position e from position s using only moves of size 1, 2, or 3.  
Input: Two integers s and e representing the start and end positions (inclusive).  
Output: Prints an integer indicating the count of valid sequences.  
Algorithm: Initialize a DP array with a single entry at s set to 1. Iterate from s+1 to e, propagating the count using the recurrence dp[i] = dp[i‑1] + dp[i‑2] + dp[i‑3]. Finally output dp[e].

---

## dataset.jsonl#45 — recursive

- anchors: 2 exact, 6 relocated, **0 quoting a line that is not in the file**, of 8
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
| 10 | `if (index == a.size())` | Base case: when we have processed all elements, we can stop recursion. |
| 12 | `if (index == 0)` | First element: its left‑max is simply itself. |
| 14 | `result[index] = max(result[index - 1], a[index]);` | Otherwise, the left‑max is the larger of the previous element's left‑max and the current element. |
| 16 | `leftMax(a, result, index + 1);` | Recursively compute left‑max for the next element. |
| 20 | `for (int i = 0; i < n; i++)` | Read input values into the array. |
| 24 | `leftMax(a, result, 0);` | Compute left‑max for the whole array. |
| 25 | `for (int i = 0; i < n; i++)` | Output the computed left‑max values. |
| 29 | `return 0;` | Normal exit. |

**Explanation**

Purpose: Compute the maximum value of the subsequence ending at each position in an array.  
Input: `n` – size of the array; `a` – vector of long long integers.  
Output: Prints the `n` long long values representing the left‑maxima to standard output.  
Algorithm: Uses a depth‑first recursion that fills `result` from the rightmost element, updating each element with the maximum of its own value and the previously computed left‑maxima. The recursion stops when the end of the array is reached.

---

## dataset.jsonl#45 — iterative

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
| 10 | `maximum = max(maximum, a[i]);` | Keep the largest element seen so far |
| 11 | `cout << maximum << " ";` | Output the current maximum followed by a space |
| 13 | `cout << endl;` | Final newline for clean output |

**Explanation**

Purpose: Prints the maximum value from a list of integers.  
Input: Reads an integer n followed by n long‑long integers.  
Output: Writes the maximum value to standard output, each value separated by a space, then a newline.  
Algorithm: Stores the first element as the initial maximum, then iterates over the remaining elements, updating the maximum whenever a larger value is encountered. Finally, it prints the maximum followed by a newline.

---
