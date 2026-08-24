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
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 1/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 1/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 1/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | no |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 0/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 0/2 | **yes** |

**8/55 problems named** · **7/20 samples drew a confidently false description**

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
Outer loop: each pass places the smallest element of the unsorted suffix at the front.
Inner loop: compare adjacent elements and swap them if they are in the wrong order.
If the current element is larger than the next, swap them.
Move the larger element to the front.
Place the smaller element at the current position.
After each outer pass, the smallest element of the unsorted suffix is at the front.
Purpose: Sort an array of integers in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order, until the array is sorted.
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
Initialize search bounds: low points to the first element, high points to the last element.
Perform binary search until the sub‑array is empty.
Compute middle index to divide the current search interval.
If the middle element matches the target, we found the value.
If the middle element is smaller, the target must be in the upper half.
Otherwise, the target must be in the lower half.
If the loop completes without finding the target, return -1.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present, otherwise `-1`.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and repeat with the remaining interval.
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
Purpose: Removes all negative integers from a vector.
Input: A reference to a vector of integers.
Output: None (the vector is modified in place).
Algorithm: Iterates through the vector and erases elements that are negative.
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
Build a descriptive string containing the code value.
Return a non‑const reference to the constructed string.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only reference to a string containing "code: " followed by the code.  
Algorithm: Constructs a string by concatenating "code: " with std::to_string(code), then returns a reference to that string. No mutation occurs.
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

**Model output** — found 0/3

```
accumulator for the number of occurrences of 'wanted'
iterate over each item; using size_t for indices avoids signed/unsigned warnings
compare current item with the target value
increment the counter; this line is misplaced; it should be inside the if block
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Iterate over the vector with a size_t index, increment a counter each time the current element equals wanted, and finally return the counter.
```

Concepts not named: `shadow`, `uninitiali[sz]ed|indeterminate|itself`, `always (return|be|yield)|never (increment|updat|chang)|discarded|inner`

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
If the loop completes without finding a violation, the series is ascending.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate through the vector with a size‑one step, comparing each element with its successor. Return false immediately on the first violation; otherwise return true after the loop.
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
Constructor: allocate n integers and store the size. Caller must ensure n > 0; otherwise undefined behavior.
Copy constructor: copy the raw pointer and size from another Buffer. This is a shallow copy; the caller must guarantee that the source buffer is valid for the lifetime of the copy.
Purpose: Provides a simple, copy‑elided buffer class that owns an integer array.  
Input: `std::size_t n` – size of the buffer to allocate.  
Output: None (default‑constructed, copy‑constructed, or destructed).  
Algorithm: Constructs a raw integer array with `new[]`, stores its pointer and length, and provides copy‑constructor and destructor to manage lifetime. No explicit initialization or deallocation is performed.
```

Scored on:

- …opy the raw pointer and size from another buffer. this is a shallow copy; the caller must guarantee that th…

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
iterate over each integer from 2 up to the given limit
flag to detect if i is a perfect square
test divisibility up to sqrt(i)
if a divisor is found, i is not a perfect square
if i is a perfect square, add it to the total
return the sum of all perfect squares ≤ limit
Purpose: Counts all integers ≤ limit that are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each i from 2 to limit, a nested loop tests divisibility up to √i; if none divide i, i is prime and added to the total. The outer loop runs O(limit) times, yielding O(√limit) time.
```

Scored on:

- …uares ≤ limit purpose: counts all integers ≤ limit that are prime.   input: int limit - the inclusive upp…
- …accumulator for the sum of perfect squares iterat…
- …he given limit flag to detect if i is a perfect square test divisibility up to sqrt(i) if a divisor is foun…

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

**Model output** — found 1/3

```
accumulator for the sum
iterate over the vector; the loop runs one extra time to include the last element
add the current element to the total
return the accumulated sum (undefined if the vector is empty)
Purpose: Computes the cumulative sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer sequence.  
Output: int – the sum of the vector elements (including the default‑initialized element at index values.size()).  
Algorithm: Initializes a total to zero, then iterates from 0 to the vector size, adding each element to the total. The final total is returned.
```

Scored on:

- …umulator for the sum iterate over the vector; the loop runs one extra time to include the last element add th…

Concepts not named: `out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)`, `undefined behavi|\bUB\b|crash`

## assignment_in_condition

*= instead of ==; assigns, then tests the assigned value*

```cpp
bool isTarget(int value, int target) {
    if (value = target)
        return true;
    return false;
}
```

**Model output** — found 1/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to 'value'. If the comparison is true, the function returns true immediately.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a specified target.
Input: Two integers, `value` and `target`.
Output: A boolean indicating whether `value` equals `target`.
Algorithm: Compares `value` with `target` and returns true if they are equal, otherwise false.
```

Scored on:

- …the two integers; the assignment operator (=) is used to assign the resu…

Concepts not named: `always (true|returns true|be true)|never (returns? )?false`, `modif|overwrit|changes the`

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
map letter grade to numeric score
A is the highest grade
B is the second highest
C is the third highest
any other grade yields zero points
fall‑through: the default case is intentionally empty
return the accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter grade ('A', 'B', 'C', or any other character).  
Output: An `int` where 'A' maps to 4, 'B' to 3, 'C' to 2, and any other character maps to 0.  
Algorithm: Initializes a result variable to 0, then uses a switch statement to assign the appropriate score based on the grade. The default case handles unrecognized grades by setting the result to 0.
```

Scored on:

- …t c is the third highest any other grade yields zero points fall-through: the default case is intentionally empt…

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

**Model output** — found 0/3

```
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the total distance covered.
After the loop, compare the accumulated distance to 1.0.
Purpose: Determines whether a sequence of adding a fixed step to zero reaches exactly 1.0 after a specified number of steps.  
Input: <code>double step</code> – the increment applied each iteration; <code>int steps</code> – total iterations.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum equals 1.0, otherwise <code>false</code>.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times, adding <code>step</code> each iteration. Finally, compare the total to 1.0 and return the result.
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
Returns the number of elements in the array. Assumes arr is a valid pointer to the first element; otherwise the behavior is undefined.
Purpose: Counts the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of the array.  
Output: `int` – the total count of elements in the array.  
Algorithm: The function computes the size of the array in bytes and divides it by the size of a single element, yielding the element count. No bounds checking is performed, so passing a null pointer or an empty array yields undefined behavior.
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

**Model output** — found 0/2

```
allocate a boolean array to track which elements have been seen
accumulate the total of all elements
iterate over the input vector
early exit: any element exceeding the limit is invalid
return sentinel error code
accumulate the current element
release the allocated memory
return the total sum of valid elements
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: const std::vector<int>& values – the list of integers; int limit – the threshold.  
Output: int – the total sum of qualifying elements, or -1 if any element exceeds limit.  
Algorithm: Allocate a boolean array of size values.size() to mark seen elements, iterate over the vector, and accumulate only those values that are less than limit. If any value exceeds limit, return -1; otherwise return the accumulated sum.
```

Concepts not named: `leak`, `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 0/3

```
Recursive definition: countDown(n) = n + countDown(n‑1)
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding 1 each time, until n reaches zero, then returns the accumulated count.
```

Concepts not named: `base case|termination|terminat|stop(ping)? condition`, `infinite|never (end|stop)|forever|unbounded`, `stack overflow|exhaust|crash`

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
Input: A reference to a std::vector<int> containing the original values.  
Output: The vector is modified in place; no return value.  
Algorithm: Iterate over the vector with a range‑based for loop, and for each element insert it back into the vector using push_back. This effectively doubles the size of the vector.
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
Compute the arithmetic mean by dividing total by count. This assumes count > 0; otherwise the result is undefined.
Purpose: Computes the arithmetic mean of a total value divided by a count.  
Input: `total` – the sum or total value; `count` – the number of elements or observations.  
Output: Returns a `double` representing the mean (total / count).  
Algorithm: Performs integer division to obtain the mean, which may truncate towards zero for negative inputs. No explicit handling of division‑by‑zero or overflow is performed.
```

Scored on:

- …epresenting the mean (total / count).   algorithm: performs integer division to obtain the mean, which may truncate…

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
Returns true if the flag represented by 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given integer mask.
Input: Two integers, `flags` and `mask`, where `flags` is the integer containing the flags and `mask` is the integer defining the flag to check.
Output: A boolean value indicating whether the flag is set in the mask.
Algorithm: Performs a bitwise AND operation between `flags` and `mask`. If the result equals `mask`, it means the flag is set, and the function returns `true`; otherwise, it returns `false`.
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
Input: `data` (int array), `i` (index of first element), `j` (index of second element).
Output: None (the array is modified in place).
Algorithm: Uses bitwise XOR to swap the values at indices `i` and `j` without using a temporary variable.
```

Concepts not named: `same (index|position|element)|identical indices|\bi == j\b|self`, `zero(ed|es|s)?|destroy|lose|lost|wipe`, `guard|check|special case`

## index_past_last_character

*index size() is the terminator; the last character is at size() - 1*

```cpp
char lastChar(const std::string& text) {
    return text[text.size()];
}
```

**Model output** — found 0/2, **asserted something false**

```
Access the character at the last position; undefined for empty strings.
Purpose: Returns the last character of a given string.
Input: A constant reference to a std::string.
Output: A char representing the last character of the string.
Algorithm: Directly accesses the element at the last index of the string.
```

Concepts not named: `null|terminator|'\\\\0'`, `size\(\) ?- ?1|one past|off.?by.?one|last .{0,15}is at`
