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
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | **yes** |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 1/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 0/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 1/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 2/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 0/3 | **yes** |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | **yes** |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 1/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 0/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 2/2 | no |

**10/55 problems named** · **9/20 samples drew a confidently false description**

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
outer loop: each pass moves the largest unsorted element to its correct position
inner loop: compare adjacent elements and swap if they are out of order
compare current element with next element
swap elements to restore order
no effect on the loop condition; the inner loop naturally terminates when the array is sorted
Purpose: Sorts an array of integers in ascending order using the bubble sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in the array.  
Output: The same array `data` is sorted in‑place; no return value.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times each outer iteration, and the swap operation swaps the first two elements that are out of order.
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
initialise search bounds to the whole array
binary search loop: stop when the interval is empty
compute middle index (integer division)
exact match found
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if the target is absent.  
Algorithm: Perform a classic binary search, narrowing the search interval based on comparison of `arr[mid]` with `target`. The loop stops when the interval collapses, indicating the target is absent.
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
Iterate over the vector while preserving the original order.
If the current element is negative, erase it from the vector.
Purpose: Removes all negative integers from a vector.  
Input: std::vector<int>& values – a mutable reference to the vector to be modified.  
Output: void – the vector is modified in‑place; no value is returned.  
Algorithm: Iterate with an iterator over the vector; when an element is negative, erase it using the iterator. The loop runs in O(n) time and O(1) extra space.
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

**Model output** — found 0/3, **asserted something false**

```
Build a string that describes the integer code. The original code uses a literal string, which is not safe for internationalization; it also appends a literal "code: " prefix, which may be confusing for callers.
Return a reference to the constructed string, allowing callers to treat it as read‑only.
Purpose: Returns a string describing the given integer code.  
Input: An int `code` representing the entity to describe.  
Output: A const reference to a std::string containing the formatted description.  
Algorithm: Constructs a literal string with the format “code: <code>”, converts the code to a string via std::to_string, and returns a reference to the result. No side‑effects other than the literal string.
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
accumulator for occurrences of wanted
iterate over each element; using size_t for index avoids signed/unsigned warnings
compare current element with wanted value
increment accumulator when a match is found
return total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Iterate over the vector with a size_t index, increment a counter each time the current element equals wanted, and finally return the counter. The counter is re‑initialized on each iteration, which is unnecessary and can lead to incorrect results.
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

**Model output** — found 1/4

```
Iterate over the vector up to the second‑last element; the last element is implicitly compared to the next element, which is undefined behavior for an empty vector.
If any two consecutive elements are out of order, the series cannot be strictly ascending.
Early exit on first violation.
All pairs are in ascending order.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if the sequence is strictly increasing, false otherwise.  
Algorithm: Iterate from the first element to the second‑last, comparing each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
```

Scored on:

- …red to the next element, which is undefined behavior for an empty vector. if any two consecutive elements…

Concepts not named: `wrap|underflow|overflow|huge|enormous|SIZE_MAX|maximum value`, `out of (bounds|range)|out-of-bounds|past the end`, `unsigned`

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

**Model output** — found 0/3

```
pointer to the allocated integer array
number of elements in the buffer
Constructor: allocate a buffer of size n and initialize its length.
Copy constructor: copy the raw pointer and length from another Buffer.
Purpose: Provides a simple wrapper for a dynamically allocated integer array.  
Input: `std::size_t n` – the number of elements to allocate.  
Output: No return value; manages the underlying memory via a pointer and length.  
Algorithm: Constructor allocates `n` ints with `new[]`, stores the pointer and length. Destructor deallocates the memory. Copy constructor copies the pointer and length from the source buffer.
```

Concepts not named: `shallow`, `double (free|delete)|twice|same (memory|pointer|buffer|array)`, `deep copy|rule of (three|3|five|5)`

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
Iterate over each integer from 2 up to (and including) limit.
Flag to detect if i is a prime number.
Check divisibility up to sqrt(i); if any divisor is found, i is composite.
If a divisor is found, i is composite.
If i is prime, add it to the total count.
Return the sum of all prime numbers up to limit.
Purpose: Counts how many positive integers ≤ limit are prime.  
Input: int limit – the upper bound (inclusive) for the search.  
Output: int – the sum of all prime numbers not exceeding limit.  
Algorithm: For each i from 2 to limit, test whether i is prime by checking divisibility up to √i; if i is prime, add it to the total. The outer loop runs O(limit) times, and the inner loop runs O(√i) times per i.
```

Scored on:

- …rom 2 up to (and including) limit. flag to detect if i is a prime number. check divisibility up to sqrt(i…
- …osite. if i is prime, add it to the total count. return the sum of all prime numbers up to limit. purpo…
- …luding) limit. flag to detect if i is a prime number. check divisibility up to sqrt(i); if any divisor is f…

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
NOTE: the loop runs one element past the last index, which is undefined for an empty vector. This leads to an out‑of‑bounds access when i == values.size(). The loop also includes the element at position i == values.size(), which is not intended.
accumulate the current element; no bounds check is performed
return the total sum (may be undefined for empty vectors)
Purpose: Computes the sum of all elements in a vector, including out‑of‑range indices.  
Input: const std::vector<int>& values – the collection of integers to be summed.  
Output: int – the total sum of the vector elements.  
Algorithm: Initialize a running total to zero, then iterate over the vector with a loop that runs one element past the vector size (to handle out‑of‑range indices). Add each element to the total; the loop naturally skips the last element, yielding the correct sum for the vector.
```

Scored on:

- …x, which is undefined for an empty vector. this leads to an out-of-bounds access when i == values.size(). the loo…

Concepts not named: `off.?by.?one|one (too many|extra|past)`, `undefined behavi|\bUB\b|crash`

## assignment_in_condition

*= instead of ==; assigns, then tests the assigned value*

```cpp
bool isTarget(int value, int target) {
    if (value = target)
        return true;
    return false;
}
```

**Model output** — found 2/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to the left operand, which is then compared to the right operand. This results in a side‑effect of modifying the left operand, which is not intended for this boolean function.
If the comparison is true, the function returns true; otherwise it returns false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function uses a simple equality test; if the comparison succeeds, it returns `true`; otherwise it returns `false`. The assignment operator `=` is used instead of the intended equality operator `==`, which leads to a logical error.
```

Scored on:

- …the two integers; the assignment operator (=) is used to assign the resu…
- …n  d to the right operand. this results in a side-effect of modifying the left operand, which is not inte…

Concepts not named: `always (true|returns true|be true)|never (returns? )?false`

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

**Model output** — found 0/3, **asserted something false**

```
accumulator for the total points for the given grade
map the letter grade to its numeric score; the default branch handles unrecognized grades
A is the highest grade, receives the maximum points
B is the second highest, receives 3 points
C is the third highest, receives 2 points
any other character is treated as a failure, yielding 0 points
return the computed score for the grade
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter grade ('A', 'B', 'C', or any other character).  
Output: An `int` where 'A' maps to 4, 'B' to 3, 'C' to 2, and any other character defaults to 0.  
Algorithm: Initializes a result counter to 0, then uses a `switch` statement to assign the appropriate numeric value based on the grade. The default case provides a fallback for unrecognized grades.
```

Concepts not named: `fall(s|ing)?[ -]?through|fallthrough`, `\bbreak\b`, `always (return|be|yield|give)s?.{0,12}(0|zero)`

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
Iterate 'steps' times, accumulating the step value each iteration.
Add the current step to the running total.
After the loop, compare the accumulated sum to 1.0; true means the sum reached exactly 1.
Purpose: Determines whether the sum of a given step size repeated a specified number of times equals 1.0.  
Input: <code>step</code> – the value added each iteration; <code>steps</code> – the count of iterations.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum reaches exactly 1.0, otherwise <code>false</code>.  
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
Returns the number of elements in the array; assumes arr is a valid, non‑null pointer to the first element. The division truncates, yielding the count of elements, which may be incorrect for empty or non‑array inputs.
Purpose: Returns the number of elements in an integer array.  
Input: An array of integers (int arr[]).  
Output: An int representing the array's length.  
Algorithm: The function uses the standard library size calculation to compute the total bytes of the array and divides by the size of a single element to obtain the count. No bounds checking is performed; calling with a null pointer yields undefined behavior.
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
allocate a temporary array to track which elements have been seen
accumulator for the sum of all values that are not greater than limit
iterate over the input vector
early exit: any value exceeding the limit is invalid
return -1 to signal invalid input
accumulate valid values
release the temporary array
return the total sum of all non‑exceeding values
Purpose: Compute the sum of all values in a vector that are strictly less than a given limit.  
Input: const std::vector<int>& values – the list of integers; int limit – the upper bound.  
Output: int – the total sum of qualifying values, or -1 if any value exceeds the limit.  
Algorithm: Allocate a temporary array of size values.size(), iterate over the vector, and accumulate values that are strictly less than limit. If any value exceeds limit, return -1; otherwise, free the array and return the accumulated sum.
```

Concepts not named: `leak`, `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 1/3

```
Base case: when n reaches 0, recursion stops and the accumulated sum is returned.
Recursive case: adds n to the result of the call with n decremented by one.
Purpose: Counts down from a given integer to zero, returning the total count.  
Input: An integer `n` representing the starting value.  
Output: An integer equal to `n + countDown(n‑1)`, i.e., the sum of `n` and the recursive call.  
Algorithm: The function calls itself with `n‑1`, accumulating the result in the call stack. The recursion terminates when `n` reaches zero, yielding `0 + countDown(‑1)` which is `0`. The final result is the sum of all intermediate calls.
```

Scored on:

- …base case: when n reaches 0, recursion stops and…

Concepts not named: `infinite|never (end|stop)|forever|unbounded`, `stack overflow|exhaust|crash`

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
Iterate over each element in the input vector and push it back into the same vector. This effectively duplicates each element, resulting in a vector that contains the original elements followed by copies of them.
Append the current element to the end of the vector, creating a copy.
Purpose: To duplicate each element in a vector by appending it to the end of the vector.
Input: A reference to a vector of integers (`std::vector<int>& values`).
Output: None (the function modifies the input vector in place).
Algorithm: Iterate through each element in the input vector and push it back into the same vector, effectively duplicating each element.
```

Concepts not named: `invalidat`, `undefined behavi|\bUB\b`, `infinite|grow(s|ing)? (forever|without)|reallocat|never (end|terminat)`

## integer_division_before_widening

*both operands are int, so the fraction is gone before the double is made*

```cpp
double meanOf(int total, int count) {
    return total / count;
}
```

**Model output** — found 0/2

```
Compute the arithmetic mean by dividing the total by the count. This assumes count > 0; otherwise division by zero is undefined.
Purpose: Computes the arithmetic mean of a set of values.  
Input: two integers – `total` (sum of all values) and `count` (number of values).  
Output: a double representing the mean (total / count).  
Algorithm: The function simply divides `total` by `count`, yielding the average. No special handling for zero or negative counts is performed.
```

Concepts not named: `integer division|truncat|discard|drops? the (fraction|decimal|remainder)`, `cast|static_cast|convert|widen`

## operator_precedence

*== binds tighter than &, so the mask is compared, not applied*

```cpp
bool hasFlag(int flags, int mask) {
    return flags & mask == mask;
}
```

**Model output** — found 0/2, **asserted something false**

```
Returns true if the flag represented by mask is set in flags. The expression uses bitwise AND; if the result equals mask, the flag is present.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: <code>flags</code> – an integer representing the combined flag values; <code>mask</code> – an integer defining which flags are relevant.  
Output: <code>bool</code> – <code>true</code> if the <code>mask</code> flags are all present in <code>flags</code>, otherwise <code>false</code>.  
Algorithm: Performs a bitwise AND between <code>flags</code> and <code>mask</code>; if the result equals <code>mask</code>, the flags are all set; otherwise they are not.
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
XOR swap: the XOR of two values yields the third value, so we can swap them without a temporary variable.
After the first swap, data[j] holds the original value of data[i].
Now data[i] holds the original value of data[j], so we can swap them again.
Purpose: To swap two elements in an array without using a temporary variable.
Input: An integer array `data`, and two indices `i` and `j`.
Output: None (the function modifies the array in place).
Algorithm: Uses bitwise XOR to swap the values without using a temporary variable.
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
Returns the character at the last position of the string. If the string is empty, this yields undefined behavior because accessing an out‑of‑bounds index is undefined.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null terminator if the string is empty.  
Algorithm: The function accesses the string’s size via text.size() and indexes the string with that offset, which yields the last character. No bounds checking is performed; callers must ensure the string is non‑empty.
```

Scored on:

- …output: char - the character at index text.size()-1, or the null terminator if the string is empty.   al…
- …r is required.   output: char - the character at index text.size()-1, or the null terminator if the string i…
