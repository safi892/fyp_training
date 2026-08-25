# Hard-example evaluation

Code where the plausible answer is the wrong one. Each sample resembles a
familiar algorithm and behaves differently. **finds** is how many of the real
problems were named; **false claim** means the model asserted the code does
something it does not, without naming the defect.

| sample | the trap | JSON | finds | false claim |
| --- | --- | :---: | :---: | :---: |
| `broken_swap` | looks exactly like bubble sort; the swap has no temporary and destroys data | ok | 0/3 | **yes** |
| `overflow_mid` | textbook binary search, but (low + high) overflows on large inputs | ok | 0/1 | no |
| `erase_while_iterating` | erase() invalidates the iterator; the loop is undefined behaviour | ok | 0/3 | **yes** |
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | no |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 1/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 1/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 2/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 3/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 1/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | **yes** |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | **yes** |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 2/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 2/2 | no |

**16/55 problems named** · **8/20 samples drew a confidently false description**

---

## broken_swap

*looks exactly like bubble sort; the swap has no temporary and destroys data*

```cpp
void sortValues(int data[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (data[j] > data[j + 1]) {
                data[j] = data[j + 1];
                data[j + 1] = data[j];
            }
        }
    }
}
```

**Model output** — found 0/3, **asserted something false**

```
Outer loop: each pass sorts the next largest element from the unsorted part
Inner loop: compare adjacent elements and swap if they are in wrong order
If the current element is greater than the next, swap them
Move the larger element to the front
Place the original element at its correct position
After each outer pass, the largest element is at the end of the array
Purpose: Sort an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order, until the array is sorted. The outer loop runs n‑1 times, each inner loop runs n‑i‑1 times, yielding O(n²) time.
```

Concepts not named: `overwrit|destroy|lose|lost|clobber|duplicat`, `no temporar|without a temporar|missing temporar|third variable`, `\bbug|incorrect|broken|does not (work|sort)|fails to|is not a( real)? swap`

## overflow_mid

*textbook binary search, but (low + high) overflows on large inputs*

```cpp
int findValue(int arr[], int size, int target) {
    int low = 0, high = size - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
```

**Model output** — found 0/1

```
Binary search loop: shrink the search interval until low > high.
Compute midpoint to decide which half to explore.
Target found at mid; return its index.
Target lies in the right half; move low to mid+1.
Target lies in the left half; move high to mid-1.
Target not present in the array.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present, otherwise `-1`.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half of the interval that cannot contain the target and repeat. The loop terminates when the interval is empty, indicating the target is absent.
```

Concepts not named: `overflow`

## erase_while_iterating

*erase() invalidates the iterator; the loop is undefined behaviour*

```cpp
void removeNegatives(std::vector<int>& values) {
    for (auto it = values.begin(); it != values.end(); ++it) {
        if (*it < 0)
            values.erase(it);
    }
}
```

**Model output** — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the size.
If the current element is negative, erase it.
Erase the element at the current iterator position.
Purpose: Removes all negative integers from a vector.  
Input: std::vector<int>& values – the vector to be modified.  
Output: void – the vector is mutated in‑place; no return value.  
Algorithm: Iterate with an iterator; when an element is found to be negative, erase it from the container. The loop naturally handles the case where the vector is empty, leaving it unchanged.
```

Concepts not named: `invalidat`, `undefined behavi|\bUB\b`, `skips? (over |an? )?(element|item|value|entry|negative)|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent`

## dangling_reference

*returns a reference to a local that dies at the closing brace*

```cpp
const std::string& describe(int code) {
    std::string result = "code: " + std::to_string(code);
    return result;
}
```

**Model output** — found 0/3

```
Build a descriptive string by concatenating a fixed prefix with the integer value.
Return a reference to the immutable result; the caller may modify it but the function itself does not modify the object.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted description.  
Algorithm: Constructs a string with the literal prefix “code: ” and the integer’s decimal representation, then returns the result by value. No mutation occurs; the caller receives a copy of the constructed string.
```

Concepts not named: `dangl`, `local|out of scope|goes out of|lifetime|destroy`, `undefined behavi|\bUB\b`

## self_shadowing_counter

*the inner declaration shadows the counter and reads itself uninitialised*

```cpp
int countMatches(const std::vector<int>& items, int wanted) {
    int found = 0;
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (items[i] == wanted) {
            int found = found + 1;
        }
    }
    return found;
}
```

**Model output** — found 1/3

```
accumulator for the number of occurrences of wanted
iterate over each element; using size_t avoids signed/unsigned warnings
compare current element with the target value
increment the counter; this line is redundant because the loop body never uses the accumulator
if the element matches, the loop body is skipped
note: the loop body never updates the accumulator; the final value is 0
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index. For each element, if it equals wanted, increment the counter; otherwise do nothing. Finally return the counter.
```

Scored on:

- …ement matches, the loop body is skipped note: the loop body never updates the accumulator; the final value is 0…

Concepts not named: `shadow`, `uninitiali[sz]ed|indeterminate|itself`

## unsigned_wraparound

*size() - 1 on an empty vector wraps to a huge value and reads out of bounds*

```cpp
bool isAscending(const std::vector<int>& series) {
    for (std::size_t i = 0; i < series.size() - 1; ++i) {
        if (series[i] > series[i + 1])
            return false;
    }
    return true;
}
```

**Model output** — found 0/4

```
Iterate through the vector, comparing each element with its successor.
If any element is greater than the next, the series is not strictly ascending.
Early exit on first violation.
If the loop completes without finding a descending pair, the series is ascending.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last, comparing each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
```

Concepts not named: `empty`, `wrap|underflow|overflow|huge|enormous|SIZE_MAX|maximum value`, `out of (bounds|range)|out-of-bounds|past the end`, `unsigned`

## shallow_copy_double_free

*the copy constructor copies the pointer, so both objects delete it*

```cpp
class Buffer {
    int* data;
    std::size_t len;
public:
    Buffer(std::size_t n) : data(new int[n]), len(n) {}
    ~Buffer() { delete[] data; }
    Buffer(const Buffer& other) : data(other.data), len(other.len) {}
};
```

**Model output** — found 1/3

```
pointer to the allocated integer array
number of elements in the buffer
public interface for the buffer
constructor: allocate n integers and store the size
destructor: free the allocated memory
copy constructor: copy the raw pointer and size from another buffer
Purpose: Provide a simple, copy‑elided buffer class that owns an integer array.  
Input: `std::size_t n` – size of the buffer to allocate.  
Output: Constructs a `Buffer` with a dynamically allocated integer array of length `n`, and optionally copies the contents of another `Buffer`.  
Algorithm: The constructor allocates `n` integers with `new[]`, stores the pointer and length, and the destructor deallocates the memory. The copy constructor copies the raw pointer and length, which is a shallow copy; the copy assignment operator does not handle the deallocation of the existing buffer, leading to a double‑free.
```

Scored on:

- …y constructor copies the raw pointer and length, which is a shallow copy; the copy assignment operator does…

Concepts not named: `double (free|delete)|twice|same (memory|pointer|buffer|array)`, `deep copy|rule of (three|3|five|5)`

## misleading_function_name

*named bubbleSort; actually sums the primes up to a limit*

```cpp
int bubbleSort(int limit) {
    int total = 0;
    for (int i = 2; i <= limit; i++) {
        bool flag = true;
        for (int j = 2; j * j <= i; j++)
            if (i % j == 0) { flag = false; break; }
        if (flag) total += i;
    }
    return total;
}
```

**Model output** — found 3/3

```
accumulator for the sum of perfect squares
iterate over each integer from 2 up to (and including) limit
flag tracks whether i is a perfect square
test divisibility up to sqrt(i)
if i has a divisor other than 1 and itself, i is not a perfect square
if i is a perfect square, add it to the total
note: the original code would incorrectly add 1 and 2, which are not perfect squares
return the sum of all perfect squares ≤ limit
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each integer i from 2 to limit, a nested loop tests divisibility by all integers j ≤ √i; if none divide i, i is prime and added to the total. The outer loop runs O(limit) times, yielding O(limit√limit) time.
```

Scored on:

- …t purpose: counts how many integers up to a given limit are prime.   input: int limit - the inclusive upp…
- …accumulator for the sum of perfect squares iterat…
- …uding) limit flag tracks whether i is a perfect square test divisibility up to sqrt(i) if i has a divisor o…

## loop_bound_off_by_one

*<= size() reads one element past the end of the vector*

```cpp
int sumAll(const std::vector<int>& values) {
    int total = 0;
    for (std::size_t i = 0; i <= values.size(); ++i)
        total += values[i];
    return total;
}
```

**Model output** — found 2/3

```
accumulator for the sum
iterate over the vector; the loop runs one extra time to include the last element
add the current element to the total
return the accumulated sum
Purpose: Computes the sum of all elements in a vector, including out‑of‑range indices.  
Input: const std::vector<int>& values – the source collection of integers.  
Output: int – the total sum of the vector’s elements, possibly including undefined behavior for out‑of‑range indices.  
Algorithm: Initializes a total to zero, then iterates over the vector with a size‑one step, adding each element to the total. The loop runs one extra iteration (i == values.size()) to ensure the loop runs at least once, which may be unnecessary for empty vectors.
```

Scored on:

- …umulator for the sum iterate over the vector; the loop runs one extra time to include the last element add th…
- …the total sum of the vector's elements, possibly including undefined behavior for out-of-range indices.   algorithm…

Concepts not named: `out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)`

## assignment_in_condition

*= instead of ==; assigns, then tests the assigned value*

```cpp
bool isTarget(int value, int target) {
    if (value = target)
        return true;
    return false;
}
```

**Model output** — found 3/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to 'value'. This is a common pitfall because it modifies the left operand while the right operand is evaluated. The assignment operator returns the value of the right operand, which is then compared to the left operand. The result is always true because the assignment always succeeds.
If the comparison is true, the function returns true.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function performs a simple equality check using the assignment operator; if the comparison succeeds, it returns `true`; otherwise it returns `false`. This yields a false‑positive for equality, which is the intended behavior.
```

Scored on:

- …the two integers; the assignment operator (=) is used to assign the resu…
- …perand, which is then  d to the left operand. the result is always true because the assignment always succeeds.…
- …comparison to 'value'. this is a common pitfall because it modifies the left operand while the right ope…

## switch_fallthrough

*no break statements, so every case falls into default*

```cpp
int scoreOf(char grade) {
    int points = 0;
    switch (grade) {
        case 'A': points = 4;
        case 'B': points = 3;
        case 'C': points = 2;
        default: points = 0;
    }
    return points;
}
```

**Model output** — found 1/3

```
initialize score accumulator
map letter grade to numeric points
A earns 4 points
B earns 3 points
C earns 2 points
any other grade yields 0 points
fall‑through: the default case covers all grades
return accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter from 'A' to 'F'.  
Output: An `int` score where 'A' maps to 4, 'B' to 3, 'C' to 2, and all other grades map to 0.  
Algorithm: Initializes a score accumulator to 0, then uses a switch statement to assign the appropriate value based on the grade. The default case handles unrecognized grades by setting the score to 0.
```

Scored on:

- …s 3 points c earns 2 points any other grade yields 0 points fall-through: the default case covers all grades ret…

Concepts not named: `\bbreak\b`, `always (return|be|yield|give)s?.{0,12}(0|zero)`

## accumulated_float_equality

*compares an accumulated double for exact equality*

```cpp
bool reachesOne(double step, int steps) {
    double running = 0.0;
    for (int i = 0; i < steps; ++i)
        running += step;
    return running == 1.0;
}
```

**Model output** — found 0/3, **asserted something false**

```
Accumulate the step value 'steps' times.
Add the current step to the running total.
Loop ends when all 'steps' have been added.
Return true if the accumulated sum equals 1.0.
Purpose: Determines whether a sequence of adding a fixed step to zero eventually reaches exactly 1.0.  
Input: <code>double step</code> – the increment per iteration; <code>int steps</code> – total number of iterations.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum equals 1.0, otherwise <code>false</code>.  
Algorithm: Initializes a running total to zero, then iteratively adds <code>step</code> to it <code>steps</code> times. Finally, compares the total to 1.0 and returns the result.
```

Concepts not named: `floating.?point|rounding|precision|epsilon`, `never (be )?(exactly )?equal|will not be exact|rarely|almost never|cannot be represented`, `toleran|approximat`

## sizeof_on_decayed_array

*an array parameter is a pointer, so sizeof measures the pointer*

```cpp
int countItems(int arr[]) {
    return sizeof(arr) / sizeof(arr[0]);
}
```

**Model output** — found 0/3, **asserted something false**

```
Returns the number of elements in the array. The size of the pointer itself (sizeof(arr)) is divided by the size of the first element (sizeof(arr[0])) to count the items. This works for arrays of any size, but may produce incorrect results for null pointers or arrays with zero elements.
Purpose: Counts the number of elements in an integer array.  
Input: An array of integers passed as a pointer (int arr[]).  
Output: An integer representing the array's length (number of elements).  
Algorithm: The function uses the standard library macro `sizeof` to obtain the total size of the array in bytes and divides it by the size of a single element to compute the count. This yields the number of elements in the array.
```

Concepts not named: `decay`, `always (return|be|give)s?.{0,10}(2|the same)|not the (number|count|length)`, `(size|length) is (lost|not known|unavailable)|cannot (determine|know)`

## leak_on_early_return

*the early return skips the delete[]*

```cpp
int totalUnder(const std::vector<int>& values, int limit) {
    int* seen = new int[values.size()]();
    int sum = 0;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (values[i] > limit)
            return -1;
        sum += values[i];
    }
    delete[] seen;
    return sum;
}
```

**Model output** — found 0/2, **asserted something false**

```
allocate a boolean array to track which elements have been seen
accumulate the total of all elements that are not greater than limit
iterate over the input vector
early exit: any element exceeding the limit is invalid
return error sentinel
accumulate the valid element
release the allocated memory
return the total of all non‑exceeding elements
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: const std::vector<int>& values – the list of integers; int limit – the threshold value.  
Output: int – the total sum of qualifying elements, or -1 if any element exceeds limit.  
Algorithm: Allocate a boolean array of size values.size() to mark seen elements, then iterate over the vector, adding each element to a running total only if it is less than limit. After the loop, deallocate the array and return the accumulated sum.
```

Concepts not named: `leak`, `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 2/3

```
This recursive definition is incorrect because it does not terminate for n <= 0. The recursion would continue indefinitely, leading to a stack overflow.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding 1 each time, until n reaches zero, then returns the accumulated count. The recursion depth grows exponentially, leading to a stack overflow for large n.
```

Scored on:

- …this recursive definition is incorrect because it does not terminate for n <= 0. the recursion would contin…
- …0. the recursion would continue indefinitely, leading to a stack overflow. purpose: counts down from a given inte…

Concepts not named: `infinite|never (end|stop)|forever|unbounded`

## grow_during_range_for

*push_back inside a range-for invalidates the iterators it is using*

```cpp
void duplicate(std::vector<int>& values) {
    for (int value : values)
        values.push_back(value);
}
```

**Model output** — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the source values.  
Output: The same vector is modified in place; no return value.  
Algorithm: Iterate over the vector with a range‑based for‑loop, inserting each element into the vector using push_back. This results in a vector with twice the original size, each element appearing twice.
```

Concepts not named: `invalidat`, `undefined behavi|\bUB\b`, `infinite|grow(s|ing)? (forever|without)|reallocat|never (end|terminat)`

## integer_division_before_widening

*both operands are int, so the fraction is gone before the double is made*

```cpp
double meanOf(int total, int count) {
    return total / count;
}
```

**Model output** — found 1/2

```
Returns the integer division of total by count, which is the arithmetic mean.
Purpose: Computes the arithmetic mean of a total and a count.  
Input: `total` – the sum of all elements; `count` – the number of elements.  
Output: A `double` representing the mean (total / count).  
Algorithm: Performs integer division, which truncates towards zero, yielding the floor division result. No explicit handling of division‑by‑zero or overflow is performed.
```

Scored on:

- …returns the integer division of total by count, which is the arithme…

Concepts not named: `cast|static_cast|convert|widen`

## operator_precedence

*== binds tighter than &, so the mask is compared, not applied*

```cpp
bool hasFlag(int flags, int mask) {
    return flags & mask == mask;
}
```

**Model output** — found 0/2, **asserted something false**

```
Returns true if the flag represented by 'mask' is set in 'flags'. The expression evaluates to true only when 'flags' contains exactly the bits specified by 'mask' (i.e., 'flags & mask == mask').
Purpose: Determines whether a specific flag is set in a given integer mask.
Input: Two integers, `flags` and `mask`, where `flags` is the integer containing the flags and `mask` is the integer defining the flag to check.
Output: A boolean indicating whether the flag is set in the mask.
Algorithm: Performs a bitwise AND operation between `flags` and `mask`. If the result equals `mask`, the flag is set; otherwise, it is not.
```

Concepts not named: `precedence|parenthes|binds? (more )?tight|evaluat.{0,25}(first|before)`, `(lowest|first|least significant) bit|always|\b& 1\b`

## xor_swap_same_index

*an xor swap zeroes the element when both indices are the same*

```cpp
void swapAt(int data[], int i, int j) {
    data[i] ^= data[j];
    data[j] ^= data[i];
    data[i] ^= data[j];
}
```

**Model output** — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j]; data[j] = data[i] ^ data[j]; data[i] = data[i] ^ data[j];
After the first XOR, data[j] becomes the original value of data[i].
The final XOR restores data[i] to its original value.
Purpose: Swaps the elements at two specified indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i` and `j` – indices of the elements to exchange.  
Output: None (the array is modified in‑place).  
Algorithm: Uses the XOR‑swap technique to swap `data[i]` and `data[j]` without using a temporary variable. Each XOR operation is performed in a single statement, which is efficient and concise.
```

Concepts not named: `same (index|position|element)|identical indices|\bi == j\b|self`, `zero(ed|es|s)?|destroy|lose|lost|wipe`, `guard|check|special case`

## index_past_last_character

*index size() is the terminator; the last character is at size() - 1*

```cpp
char lastChar(const std::string& text) {
    return text[text.size()];
}
```

**Model output** — found 2/2

```
Accesses the character at the last position of the string. If the string is empty, this yields undefined behavior because text[text.size()] is out‑of‑bounds.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null terminator if the string is empty.  
Algorithm: Directly accesses the string’s size and returns the character at that position, which is undefined for an empty string because the size is out‑of‑range. No bounds checking is performed.
```

Scored on:

- …output: char - the character at index text.size()-1, or the null terminator if the string is empty.   al…
- …r is required.   output: char - the character at index text.size()-1, or the null terminator if the string i…
