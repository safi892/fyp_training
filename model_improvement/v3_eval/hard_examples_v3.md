# Hard-example evaluation

Code where the plausible answer is the wrong one. Each sample resembles a
familiar algorithm and behaves differently. **finds** is how many of the real
problems were named; **false claim** means the model asserted the code does
something it does not, without naming the defect.

| sample | the trap | JSON | finds | false claim |
| --- | --- | :---: | :---: | :---: |
| `broken_swap` | looks exactly like bubble sort; the swap has no temporary and destroys data | ok | 0/3 | **yes** |
| `overflow_mid` | textbook binary search, but (low + high) overflows on large inputs | ok | 0/1 | no |
| `erase_while_iterating` | erase() invalidates the iterator; the loop is undefined behaviour | ok | 1/3 | no |
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | **yes** |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 0/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 1/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 1/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 1/2 | no |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 1/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 0/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 2/2 | no |

**11/55 problems named** · **6/20 samples drew a confidently false description**

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
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap only when the current element is larger than the next
swap elements
restore original order of the swapped element
continue until the entire array is sorted
Purpose: Sorts an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The function modifies `data` in place; it returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing adjacent elements and swapping them if they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, ensuring each element is moved to its correct position in the final pass.
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
Binary search loop: shrink the search interval until low crosses high.
Compute midpoint to decide which half to discard.
Target found – return its index.
Target lies in the right half; shrink left boundary.
Target lies in the left half; shrink right boundary.
Loop ends when low > high, meaning the target was not present.
Fallback: target not found.
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not present.  
Algorithm: Perform a binary search, narrowing the search interval based on comparisons with the middle element. Continue until the interval collapses, then return the index or -1 if the target is absent.
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

**Model output** — found 1/3

```
Iterate over the vector while preserving the original size.
If the current element is negative, erase it.
Erase the element at the current iterator position.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate over the vector with an iterator; when an element is negative, call erase on the iterator, which invalidates the iterator and moves the next element forward. The loop naturally stops at the end because erase invalidates the iterator.
```

Scored on:

- …n an element is negative, call erase on the iterator, which invalidates the iterator and moves the next eleme…

Concepts not named: `undefined behavi|\bUB\b`, `skips? (over |an? )?(element|item|value|entry|negative)|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent`

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
Build a string describing the integer; the format is hard‑coded and may not be suitable for all callers.
Return a reference to the constructed string, allowing the caller to treat it as read‑only.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted string containing “code: ” followed by the code.  
Algorithm: Constructs a string literal, appends the code, and returns a reference to that literal. No side effects beyond the literal creation.
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
accumulator for the count of occurrences
iterate over each element; size_t is used for indices
match the target value
increment the counter; this is a re‑declaration of found, causing undefined behavior
continue loop for the next element
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. After the loop, return the counter.
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
Iterate over the vector up to the second last element; the last element is always ascending.
If any two consecutive elements are out of order, the sequence is not ascending.
Early exit: no need to check further.
All pairs were in ascending order.
Purpose: Determines whether a sequence of integers is strictly increasing.  
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

**Model output** — found 0/3

```
Pointer to the dynamically allocated integer array that holds the buffer contents.
Number of elements currently allocated in the buffer.
Constructor that allocates a buffer of size n and initializes its length.
Copy constructor that copies the data pointer and length from another Buffer object.
Purpose: Provides a simple, stack‑allocated integer buffer with automatic memory management.  
Input: std::size_t n – desired size of the buffer.  
Output: Buffer – a copy‑constructor that copies the internal pointer and length.  
Algorithm: Constructor allocates n ints on the heap, stores the pointer and length, and calls delete[] in the destructor. Copy constructor copies the pointer and length from the source object, leaving the heap allocation intact.
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
accumulator for the sum of primes up to limit
iterate over each integer i from 2 up to limit
flag to detect primality of i
test divisibility up to sqrt(i)
if i has a divisor, it is composite; stop early
if i is prime, add it to the total
return the accumulated sum of primes
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each i from 2 to limit, a flag tracks primality; the inner loop tests divisibility up to √i; if no divisor is found, i is added to the total. The final total is returned.
```

Scored on:

- …accumulator for the sum of primes up to limit iterate over each integer…
- …accumulator for the sum of primes up to limit ite…
- …ger i from 2 up to limit flag to detect primality of i test divisibility up to sqrt(i) if i has a divisor,…

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
return the accumulated sum
Purpose: Computes the sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer data.  
Output: int – the total sum of the vector’s elements.  
Algorithm: Initializes a running total to zero, then iterates over the indices from 0 to the vector’s size (inclusive). For each index it adds the corresponding element to the total. The final total is returned.
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
The assignment operator (=) is used here, which is a common mistake. It assigns the value of 'target' to 'value' and returns the result of the assignment, which is 1 (true). This causes the function to always return true, regardless of the actual comparison.
If the assignment did not occur, the function falls through to the false branch, returning false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function uses a simple equality test (`value = target`) and returns the result of that test. The assignment operator (`=`) is used instead of the equality operator (`==`) which is incorrect; the intended comparison is `value == target`. The assignment operator returns the value of the right‑hand side, which is `true` for non‑zero values and `false` for zero, leading to a false result for equality.
```

Scored on:

- …the assignment operator (=) is used here, which is a c…

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
accumulator for the numeric score
map a single‑character grade to its numeric value
A is the highest grade, worth 4 points
B is the next highest, worth 3 points
C is the third highest, worth 2 points
any other grade maps to 0 points (e.g., F)
fall‑through: the switch body is empty
return the computed score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter grade ('A', 'B', 'C', or any other character).  
Output: An `int` score (4 for 'A', 3 for 'B', 2 for 'C', 0 for any other character).  
Algorithm: Initializes a score accumulator to zero, then uses a switch statement to assign the appropriate numeric value based on the grade. If the grade does not match any known letter, it defaults to zero.
```

Scored on:

- …, worth 2 points any other grade maps to 0 points (e.g., f) fall-through: the switch body is empty return the co…

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
Accumulate the next step value.
After the loop, compare the accumulated sum to 1.0; true means the sum reached exactly 1.
Purpose: Determines whether a sequence of adding a fixed step to an initial value eventually reaches exactly 1.0.  
Input: <code>step</code> – the constant increment; <code>steps</code> – the number of increments to perform.  
Output: <code>bool</code> – true if the accumulated sum equals 1.0 after <code>steps</code> additions, false otherwise.  
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
Purpose: Count the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of an array of integers.  
Output: `int` – the total count of elements in the array.  
Algorithm: The function computes the total size of the array using `sizeof`, then divides by the size of a single element to obtain the count. This works for arrays of any size, but relies on the caller providing a valid, non‑null pointer.
Purpose: Counts the number of elements in an integer array.  
Input: An array of ints (passed as a pointer to its first element).  
Output: An int representing the array's length (number of elements).  
Algorithm: The function computes the total size of the array in bytes and divides it by the size of a single int, yielding the count. No bounds checking is performed; calling with a null pointer or an empty array yields undefined behavior.
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

**Model output** — found 1/2

```
Allocate a temporary array to mark which elements have been seen; each element is initialized to 0.
Accumulator for the sum of all values that are ≤ limit.
Iterate over the input vector; the loop runs in O(n) time.
If the current value exceeds the limit, the function cannot sum all qualifying values; return -1 to signal failure.
Deallocate the temporary array to avoid memory leak.
Return the accumulated sum of all values ≤ limit.
Purpose: Compute the sum of all elements in a vector that are less than or equal to a given limit.  
Input: `values` – a vector of integers; `limit` – an integer threshold.  
Output: Returns the accumulated sum if all elements are ≤ limit; otherwise returns –1.  
Algorithm: Allocate a temporary array of size `values.size()` to mark seen elements, iterate over `values`, accumulate values that are ≤ `limit`, and finally deallocate the array. If any element exceeds `limit`, the function aborts early and returns –1.
```

Scored on:

- …nal failure. deallocate the temporary array to avoid memory leak. return the accumulated sum of all valu…

Concepts not named: `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 1/3

```
Recursively decrements n and adds the result to the current value. The recursion stops when n reaches 0, yielding 0 + 0 = 0.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + 1).  
Algorithm: The function calls itself with n‑1, adding one to the result each time, effectively performing a full factorial (n!) of the input. The recursion terminates when n reaches zero, yielding 1.
```

Scored on:

- …erforming a full factorial (n!) of the input. the recursion terminates when n reaches zero, yielding 1.…

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
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in the input vector.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: None (the function modifies the input vector in place).  
Algorithm: Iterate over the vector with a range‑based for‑loop, inserting each element into the vector using push_back. This results in the original elements being copied twice.
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
Purpose: Compute the arithmetic mean of a set of values.  
Input: `total` – the sum of all elements; `count` – the number of elements.  
Output: A `double` representing the mean (total / count).  
Algorithm: The function simply divides the total by the count, assuming `count` is non‑zero. No special handling for division‑by‑zero is performed.
Purpose: Compute the arithmetic mean of a set of values.  
Input: <code>total</code> – sum of all elements; <code>count</code> – number of elements.  
Output: <code>double</code> – the mean value (total divided by count).  
Algorithm: The function simply divides the total by the count, assuming count is non‑zero. No special handling for zero or negative counts is provided.
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
Returns true if the flag set in 'flags' matches the mask. The expression evaluates to true only when every bit in 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: <code>int flags</code> – the set of flags to test; <code>int mask</code> – the flag to look for.  
Output: <code>bool</code> – <code>true</code> if <code>flags</code> contains <code>mask</code>, otherwise <code>false</code>.  
Algorithm: Performs a bitwise AND between <code>flags</code> and <code>mask</code>; if the result equals <code>mask</code>, the flag is present; otherwise it is not.
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
XOR swap: XOR the element at i with the element at j, leaving the original value in j. This works because XOR is commutative and associative, so the order of operands does not matter.
After the first swap, the element at j now holds the original value of i. XOR the element at j with the new value of i, leaving the original value in i.
Finally, XOR the element at i with the new value of j, which is the original value of i. This completes the swap.
Purpose: Swaps the values at two indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i`, `j` – indices to swap.  
Output: The function modifies the array in‑place; it returns `void`.  
Algorithm: Uses the XOR‑swap trick to exchange the values without using a temporary variable. Each XOR operation is performed in place, preserving the original order of elements.
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
Returns the character at the position text.size(), which is undefined for empty strings.
Note: This implementation assumes the caller knows the string is non‑empty; otherwise undefined behavior occurs.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null terminator if the string is empty.  
Algorithm: Directly accesses the character at the last position of the string, which is undefined for an empty string; the function assumes the caller handles the empty‑string case.
```

Scored on:

- …output: char - the character at index text.size()-1, or the null terminator if the string is empty.   al…
- …r is required.   output: char - the character at index text.size()-1, or the null terminator if the string i…
