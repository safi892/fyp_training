# Defect-awareness probe

Does explicit wording get the model to report what a line *does* rather than
what the function looks like it was meant to do? The trained wording is the
control: it is exactly what `/analyze` sends today.

A phrasing only helps if it moves the first two columns without moving the
third — correct code is the product's normal input, and inventing defects in
it would be a worse failure than missing real ones.

| phrasing | problems named | false claims (of 8) | defects invented on correct code (of 4) | anchor validity |
| --- | :---: | :---: | :---: | :---: |
| `trained_wording` | 11/55 | 6 | 1 | 96/96 |
| `describe_effect` | 12/55 | 7 | 0 | 98/98 |
| `assume_nothing` | 12/55 | 8 | 0 | 94/94 |

---

## trained_wording

> *(the trained instruction, unchanged)*

### broken_swap — found 0/3, **asserted something false**

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

### overflow_mid — found 0/1

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

### erase_while_iterating — found 1/3

```
Iterate over the vector while preserving the original size.
If the current element is negative, erase it.
Erase the element at the current iterator position.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate over the vector with an iterator; when an element is negative, call erase on the iterator, which invalidates the iterator and moves the next element forward. The loop naturally stops at the end because erase invalidates the iterator.
```

### dangling_reference — found 0/3, **asserted something false**

```
Build a string describing the integer; the format is hard‑coded and may not be suitable for all callers.
Return a reference to the constructed string, allowing the caller to treat it as read‑only.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted string containing “code: ” followed by the code.  
Algorithm: Constructs a string literal, appends the code, and returns a reference to that literal. No side effects beyond the literal creation.
```

### self_shadowing_counter — found 0/3

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

### unsigned_wraparound — found 0/4

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

### shallow_copy_double_free — found 0/3

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

### misleading_function_name — found 3/3

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

### loop_bound_off_by_one — found 1/3

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

### assignment_in_condition — found 1/3

```
The assignment operator (=) is used here, which is a common mistake. It assigns the value of 'target' to 'value' and returns the result of the assignment, which is 1 (true). This causes the function to always return true, regardless of the actual comparison.
If the assignment did not occur, the function falls through to the false branch, returning false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function uses a simple equality test (`value = target`) and returns the result of that test. The assignment operator (`=`) is used instead of the equality operator (`==`) which is incorrect; the intended comparison is `value == target`. The assignment operator returns the value of the right‑hand side, which is `true` for non‑zero values and `false` for zero, leading to a false result for equality.
```

### switch_fallthrough — found 1/3

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

### accumulated_float_equality — found 0/3

```
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the next step value.
After the loop, compare the accumulated sum to 1.0; true means the sum reached exactly 1.
Purpose: Determines whether a sequence of adding a fixed step to an initial value eventually reaches exactly 1.0.  
Input: <code>step</code> – the constant increment; <code>steps</code> – the number of increments to perform.  
Output: <code>bool</code> – true if the accumulated sum equals 1.0 after <code>steps</code> additions, false otherwise.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times, adding <code>step</code> each iteration. Finally, compare the total to 1.0 and return the result.
```

### sizeof_on_decayed_array — found 0/3, **asserted something false**

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

### leak_on_early_return — found 1/2

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

### recursion_without_base_case — found 1/3

```
Recursively decrements n and adds the result to the current value. The recursion stops when n reaches 0, yielding 0 + 0 = 0.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + 1).  
Algorithm: The function calls itself with n‑1, adding one to the result each time, effectively performing a full factorial (n!) of the input. The recursion terminates when n reaches zero, yielding 1.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in the input vector.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: None (the function modifies the input vector in place).  
Algorithm: Iterate over the vector with a range‑based for‑loop, inserting each element into the vector using push_back. This results in the original elements being copied twice.
```

### integer_division_before_widening — found 0/2

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

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag set in 'flags' matches the mask. The expression evaluates to true only when every bit in 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: <code>int flags</code> – the set of flags to test; <code>int mask</code> – the flag to look for.  
Output: <code>bool</code> – <code>true</code> if <code>flags</code> contains <code>mask</code>, otherwise <code>false</code>.  
Algorithm: Performs a bitwise AND between <code>flags</code> and <code>mask</code>; if the result equals <code>mask</code>, the flag is present; otherwise it is not.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: XOR the element at i with the element at j, leaving the original value in j. This works because XOR is commutative and associative, so the order of operands does not matter.
After the first swap, the element at j now holds the original value of i. XOR the element at j with the new value of i, leaving the original value in i.
Finally, XOR the element at i with the new value of j, which is the original value of i. This completes the swap.
Purpose: Swaps the values at two indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i`, `j` – indices to swap.  
Output: The function modifies the array in‑place; it returns `void`.  
Algorithm: Uses the XOR‑swap trick to exchange the values without using a temporary variable. Each XOR operation is performed in place, preserving the original order of elements.
```

### index_past_last_character — found 2/2

```
Returns the character at the position text.size(), which is undefined for empty strings.
Note: This implementation assumes the caller knows the string is non‑empty; otherwise undefined behavior occurs.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null terminator if the string is empty.  
Algorithm: Directly accesses the character at the last position of the string, which is undefined for an empty string; the function assumes the caller handles the empty‑string case.
```

### correct_swap — **invented a defect**

```
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap only when the current element is larger than the next
preserve the value that will be overwritten
move the larger element forward
restore the original value of the larger element
continue until the entire array is sorted
Purpose: Sorts an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are in the wrong order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, ensuring each element is moved to its correct position.
```

### correct_binary_search — clean, as it should be

```
initialise search bounds
continue while the search interval is valid
compute middle index safely
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not present.  
Algorithm: Perform a binary search, narrowing the search interval each iteration. When the middle element equals the target, return its index; otherwise, discard the half containing the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it and advance the iterator to skip the next element.
Erase the element at the current position and obtain a new iterator pointing to the next element.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate with an iterator; if the current element is negative, erase it and advance the iterator to skip the next element. If the element is non‑negative, simply advance the iterator. This runs in O(n) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the count of occurrences
iterate over each element; size_t is used for indices
compare current element with the target
increment when a match is found
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index, incrementing the counter each time the current element equals wanted. Finally, return the counter.
```

## describe_effect

> Describe what each line actually does when executed. Do not describe what the function appears intended to do.

### broken_swap — found 0/3, **asserted something false**

```
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap elements when the current element is larger than the next
swap the elements
restore the original order of the swapped element
continue until the entire array is sorted
Purpose: Sorts an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, ensuring each element is moved to its correct position in the final pass.
```

### overflow_mid — found 0/1

```
initialize search bounds to the whole array
continue while the search interval is valid
compute midpoint to divide search space
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not found.  
Algorithm: Perform a binary search, narrowing the search interval each iteration. If the middle element equals the target, return its index; otherwise, discard the half containing the target and continue searching the other half. The loop terminates when the interval collapses, indicating the target is absent.
```

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it.
Erase the element at the iterator position.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate over the vector with an iterator; when an element is found to be negative, erase the element from the container. The loop naturally handles the case where the vector is empty or contains only non‑negative values.
```

### dangling_reference — found 1/3

```
Build a string describing the integer; the original code used a literal string, which is incorrect for the intended purpose.
Return a reference to the constructed string, allowing the caller to treat it as read‑only.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted string containing “code: ” followed by the code.  
Algorithm: Constructs a string literal, appends the code, and returns a reference to that literal. No side effects beyond the literal’s lifetime.
```

### self_shadowing_counter — found 0/3

```
accumulator for the count of occurrences
iterate over each element; using size_t for index avoids signed/unsigned mismatch
match the target value
increment the counter; this line is a redefinition of the accumulator variable, causing a compile error
continue loop for the next element
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. After the loop, return the counter.
```

### unsigned_wraparound — found 0/4

```
Iterate over the vector up to the second last element; the last element is always ascending.
If any two consecutive elements are out of order, the sequence is not ascending.
Early exit: no need to check further.
All pairs are in ascending order.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – a vector of integers to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last element; if any element is greater than its successor, return false immediately. If the loop finishes, return true.
```

### shallow_copy_double_free — found 1/3

```
Pointer to the dynamically allocated integer array that holds the buffer contents.
Number of elements currently allocated in the buffer.
Constructor that allocates a buffer of size n and initializes its length.
Copy constructor that creates a new buffer by copying the existing data pointer and length. This is a shallow copy; the copied buffer shares the same underlying memory.
Purpose: Provides a simple, lightweight buffer class that owns an integer array.  
Input: `std::size_t n` – size of the buffer to allocate.  
Output: Constructs a `Buffer` object owning an `int` array of length `n`.  
Algorithm: Initializes the internal pointer with `new[]` and stores the length. The destructor deallocates the memory. The copy‑constructor copies the pointer and length from another `Buffer` instance, which is a shallow copy.
```

### misleading_function_name — found 3/3

```
accumulator for the sum of primes up to limit
iterate over each integer i from 2 up to limit
flag to detect primality of i
test divisibility up to sqrt(i)
if i has a divisor, it is composite; stop early
if i is prime, add it to the total
return the sum of all primes ≤ limit
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each i from 2 to limit, a flag tracks primality; the inner loop tests divisibility up to √i; if no divisor is found, i is added to the total. The final total is returned.
```

### loop_bound_off_by_one — found 1/3

```
accumulator for the sum
iterate over the vector; the loop runs one extra time to include the last element
add the current element to the total
return the accumulated sum
Purpose: Computes the sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer sequence.  
Output: int – the total sum of the vector’s elements.  
Algorithm: Initializes total to zero, then iterates over the indices from 0 to the vector’s size (inclusive). For each index it adds the corresponding element to total. The final total is returned.
```

### assignment_in_condition — found 1/3

```
The assignment operator (=) is used to assign the target value to the local variable 'value'. This is a common mistake because it replaces the original value with the target, leaving the original value unchanged. The comparison then checks if the new value is equal to the target, which is incorrect.
If the assignment succeeded, the function returns true.
If the assignment failed (e.g., value is already equal to target), the function returns false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function uses a single assignment to compare the two integers; if the assignment succeeds (i.e., `value` is equal to `target`), it returns `true`; otherwise it returns `false`. The assignment is unnecessary and can be removed, preserving the original behavior.
```

### switch_fallthrough — found 1/3

```
initialize accumulator for total points
map letter grade to numeric score
A is the highest grade, worth 4 points
B is the next highest, worth 3 points
C is the third highest, worth 2 points
any other grade maps to 0 points
fall‑through: the switch body is unreachable for valid grades
return accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter grade ('A', 'B', 'C', or any other character).  
Output: An `int` score (4 for 'A', 3 for 'B', 2 for 'C', 0 for any other character).  
Algorithm: Initializes a score accumulator to zero, then uses a switch statement to assign the appropriate numeric value based on the grade. If the grade does not match any known letter, it defaults to zero.
```

### accumulated_float_equality — found 0/3

```
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the next step value.
After the loop, compare the accumulated sum to 1.0.
Purpose: Determines whether a sequence of adding a fixed step to an initial value eventually reaches exactly 1.0.  
Input: <code>step</code> – the increment value; <code>steps</code> – the number of increments to perform.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum equals 1.0 after <code>steps</code> additions, otherwise <code>false</code>.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times, adding <code>step</code> each iteration. Finally, compare the total to 1.0 and return the result.
```

### sizeof_on_decayed_array — found 0/3, **asserted something false**

```
Returns the number of elements in the array. The expression sizeof(arr) yields the total byte size of the array, and sizeof(arr[0]) yields the size of a single element. Dividing these yields the count of elements.
Purpose: Counts the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of an array of integers.  
Output: `int` – the total count of elements in the array.  
Algorithm: The function computes the size of the array in bytes using `sizeof`, then divides by the size of a single integer to obtain the count. This works for arrays of any size, but may produce undefined results for empty arrays or when the pointer is null.
```

### leak_on_early_return — found 0/2, **asserted something false**

```
allocate a scratch array of size values.size() to track seen elements
accumulator for the sum of all elements that are ≤ limit
iterate over the input vector
early exit: any element exceeding the limit is invalid
return -1 to signal invalid input
accumulate the element if it is ≤ limit
release the allocated memory
return the total sum of valid elements
Purpose: Compute the sum of all elements in a vector that are less than or equal to a given limit.  
Input: `values` – a vector of integers; `limit` – an integer threshold.  
Output: Returns the accumulated sum of qualifying elements, or -1 if any element exceeds the limit.  
Algorithm: Allocate a temporary array of size `values.size()` to mark seen elements. Iterate over `values`, skipping any element > `limit` and adding qualifying ones to a running total. After the loop, deallocate the array and return the total.
```

### recursion_without_base_case — found 1/3

```
Recursively decrements n and adds the result to the current value. The recursion stops when n reaches 0, yielding 0 + 0 = 0.
Purpose: Counts down from n to 0, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + 1).  
Algorithm: The function calls itself with n‑1, adding 1 to the result each time, effectively performing a full factorial (n!) without memoization. The recursion terminates when n reaches 0, yielding 1.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in the input vector.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: None (the function modifies the input vector in place).  
Algorithm: Iterate over the vector with a range‑based for loop, appending each element to the end of the vector. This results in a copy of each original value, which may be inefficient for large vectors.
```

### integer_division_before_widening — found 1/2

```
Returns the integer division of total by count, which yields the arithmetic mean. The result is undefined for count == 0 because division by zero is not allowed.
Purpose: Compute the arithmetic mean of a set of values.  
Input: `total` – the sum of all values; `count` – the number of values.  
Output: A `double` representing the mean (total / count).  
Algorithm: The function divides `total` by `count` and returns the result. No special handling for division‑by‑zero is performed; the caller must ensure `count` is non‑zero.
```

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag bits in 'flags' are all set to 1, matching the pattern in 'mask'.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: `int flags` – the set of flags to test; `int mask` – the flag to look for.  
Output: `bool` – `true` if `flags` contains `mask`, otherwise `false`.  
Algorithm: Performs a bitwise AND between `flags` and `mask`; if the result equals `mask`, the function returns `true`; otherwise it returns `false`. This works for any bit pattern, including zero.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: XOR the element at i with the element at j, leaving the original value in j. This works because XOR is commutative and associative, so the order of operands does not matter.
After the first swap, data[j] holds the original value of data[i]. XOR the element at j with the new value of data[i] to move it to j. The result is the same as the first swap.
Finally, XOR the element at i with the new value of data[j] to move it to i. This completes the swap.
Purpose: Swaps the values at two indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i`, `j` – indices to swap.  
Output: None (the array is modified in‑place).  
Algorithm: Uses the XOR‑swap trick to exchange the values without a temporary variable. Each XOR operation is performed in place, so the original code is correct.
```

### index_past_last_character — found 2/2

```
Returns the character at the position text.size(), which is undefined for empty strings.
Purpose: Returns the last character of a string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null character if the string is empty.  
Algorithm: Directly accesses the character at the last position of the string, which is undefined for an empty string; the function relies on the caller to ensure the string is non‑empty.
```

### correct_swap — clean, as it should be

```
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap only when the current element is larger than the next
preserve the value that will be overwritten
move the larger element forward
restore the original value of the element that was swapped
continue until the entire array is sorted
Purpose: Sort an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterate over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, reducing the effective range each iteration. This bubble‑sort runs in O(n²) time and O(1) extra space.
```

### correct_binary_search — clean, as it should be

```
initialise search bounds
continue while the search interval is valid
compute middle index safely
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not found.  
Algorithm: Perform a binary search, narrowing the search interval each iteration. If the middle element equals the target, return its index; otherwise, discard the half containing the target and continue searching the other half. The loop terminates when the interval collapses, indicating the element is absent.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and return an iterator to the next element.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate with an auto iterator; if the element is negative, erase it and advance the iterator to skip the next element. If the element is non‑negative, simply advance the iterator. This runs in O(n) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the count of occurrences of wanted
iterate over each element; size_t is used for indices to avoid signed/unsigned warnings
compare current element with the target
increment the counter when a match is found
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index, incrementing the counter each time the current element equals wanted. Finally, return the counter.
```

## assume_nothing

> This code may contain defects. Do not assume it is correct. Describe what each line actually does when executed, and where a line's effect differs from what the surrounding code appears intended to achieve, say so plainly.

### broken_swap — found 0/3, **asserted something false**

```
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap elements when the current element is larger than the next
swap the elements
restore the original order of the swapped element
continue until the entire array is sorted
Purpose: Sorts an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, ensuring each element is moved to its correct position.
```

### overflow_mid — found 0/1

```
initialise search bounds
continue while the interval is valid
compute midpoint
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not present.  
Algorithm: Perform a binary search, narrowing the search interval based on comparisons with the middle element. Continue until the interval is empty, then return -1.
```

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the original size.
If the current element is negative, erase it.
Erase the element at the current iterator position.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with any negative values removed.  
Algorithm: Iterate over the vector with an iterator; when an element is found to be negative, erase the element from the container. The loop naturally handles the case where the vector is empty or contains only non‑negative values.
```

### dangling_reference — found 0/3, **asserted something false**

```
Build a string describing the integer; the original code uses a literal string, which is incorrect for the intended purpose.
Return a reference to the constructed string, allowing callers to treat it as read‑only.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted string containing “code: ” followed by the code.  
Algorithm: Constructs a string literal, appends the code, and returns a reference to that literal. No side effects beyond the literal creation.
```

### self_shadowing_counter — found 0/3

```
accumulator for the count of occurrences
iterate over each element; size_t is used for indices to avoid signed/unsigned warnings
match the target value
increment the counter; this is a no‑op because the variable is re‑declared inside the if block
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index. For each element, if it equals wanted, increment the counter; otherwise do nothing. Finally return the counter.
```

### unsigned_wraparound — found 0/4

```
Iterate over the vector, comparing each element with its successor.
If any element is greater than its successor, the sequence is not strictly ascending.
Early exit: no need to check further.
All elements are in non‑decreasing order.
Purpose: Determines whether a sequence of integers is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last element; if any element is greater than its successor, return false immediately. If the loop completes, return true.
```

### shallow_copy_double_free — found 1/3

```
Purpose: Provides a simple, lightweight buffer class that owns an integer array.  
Input: `std::size_t n` – size of the buffer to allocate.  
Output: Constructs a `Buffer` object owning an `int` array of length `n`.  
Algorithm: The constructor allocates `n` integers with `new[]`, stores the pointer and length, and the destructor deallocates the memory. The copy constructor copies the pointer and length, which is sufficient for a shallow copy.
```

### misleading_function_name — found 3/3

```
accumulator for the sum of primes up to limit
iterate over each integer i from 2 up to limit
flag to detect primality of i
test divisibility up to sqrt(i)
if i has a divisor other than 1 or itself, i is composite
if i is prime, add it to the total
return the sum of all primes ≤ limit
Purpose: Counts all integers up to a given limit that are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all primes ≤ limit.  
Algorithm: For each integer i from 2 to limit, test whether i has any divisor other than 1 and i itself. If none do, i is prime and is added to the total. The outer loop runs O(limit) times, yielding O(limit²) time.
```

### loop_bound_off_by_one — found 3/3

```
accumulator for the sum
iterate over the vector; the loop runs one extra time to include the last element
add the current element to the total
return the accumulated sum
Purpose: Computes the sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer container.  
Output: int – the total sum of the vector’s elements.  
Algorithm: Initializes a running total to zero, then iterates over the indices from 0 to the vector’s size (inclusive). For each index it adds the corresponding element to the total, which yields the sum. The loop runs one extra iteration (at index values.size()) because the original code would access out‑of‑bounds elements, leading to undefined behavior.
```

### assignment_in_condition — found 1/3

```
The assignment operator (=) is used here, which is a common mistake. It assigns the value of 'target' to 'value' and returns the result of the assignment, which is 1 for true and 0 for false. This causes the function to always return true, regardless of the actual comparison.
If the assignment fails (e.g., value is not an int), the function returns false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function uses a simple equality test; if the comparison succeeds, it returns true; otherwise it returns false. The assignment operator `=` is used instead of the intended equality operator `==`, which leads to undefined behavior.
```

### switch_fallthrough — found 1/3

```
initialize accumulator for total points
map letter grade to numeric score
A is the highest grade, worth 4 points
B is the next highest, worth 3 points
C is the third highest, worth 2 points
any other grade maps to 0 points (e.g., F)
fall‑through: the default case covers all grades
return accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter grade ('A', 'B', 'C', or any other character).  
Output: An `int` score (4 for 'A', 3 for 'B', 2 for 'C', 0 for any other character).  
Algorithm: Initializes a score accumulator to zero, then uses a switch statement to assign the appropriate numeric value based on the grade. If the grade does not match any known letter, it defaults to zero.
```

### accumulated_float_equality — found 0/3

```
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the next step value.
After the loop, compare the accumulated sum to 1.0.
Purpose: Determines whether a sequence of adding a fixed step to an initial zero value reaches exactly 1 after a given number of steps.  
Input: <code>double step</code> – the increment per iteration; <code>int steps</code> – total iterations.  
Output: <code>bool</code> – true if the accumulated sum equals 1, false otherwise.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times, adding <code>step</code> each iteration. Finally, compare the total to 1 and return the result.
```

### sizeof_on_decayed_array — found 0/3, **asserted something false**

```
Purpose: Count the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of an array of integers.  
Output: `int` – the total number of elements in the array.  
Algorithm: Compute the total size of the array using `sizeof`, then divide by the size of a single element to obtain the count. This works for arrays of any size, but may produce undefined behavior for empty arrays or when the array is not properly aligned.
Purpose: Counts the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of an array of integers.  
Output: `int` – the total number of elements in the array.  
Algorithm: The function computes the size of the array in bytes using `sizeof`, then divides by the size of a single integer to obtain the count. This works for arrays of any size, but may produce undefined results for non‑array pointers or empty arrays.
```

### leak_on_early_return — found 0/2, **asserted something false**

```
allocate a scratch array of size values.size() to track seen elements
accumulator for the total of all elements
iterate over the input vector
early exit: if any element exceeds the limit, the whole sum cannot be computed
return sentinel indicating failure
accumulate the current element
release the allocated memory
return the computed sum
Purpose: Compute the sum of all elements in a vector that are less than or equal to a given limit.  
Input: `values` – a vector of integers; `limit` – an integer threshold.  
Output: Returns the accumulated sum if all elements are ≤ limit; otherwise returns –1.  
Algorithm: Allocate a temporary array of size `values.size()` to mark seen elements, then iterate over the vector, adding each element to the sum only if it is ≤ limit. After the loop, deallocate the array and return the accumulated sum.
```

### recursion_without_base_case — found 0/3

```
Recursively decrements n and adds the result to the current value. The recursion stops when n reaches 0, yielding 0 + 0 = 0.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: An integer n representing the starting value.  
Output: An integer indicating the total steps taken (n + steps from n‑1).  
Algorithm: Recursively calls itself with n‑1, adding 1 for each recursive call, until n reaches 0, at which point the recursion unwinds and accumulates the steps.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in the input vector.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: The same vector, now with each element appearing twice.  
Algorithm: Iterate over the vector with a range‑based for loop, inserting each element into the vector using push_back. The loop naturally duplicates the elements because push_back appends to the end of the vector.
```

### integer_division_before_widening — found 1/2

```
Purpose: Compute the arithmetic mean of a set of values.  
Input: `total` – the sum of all values; `count` – the number of values.  
Output: A `double` representing the mean (total / count).  
Algorithm: Perform integer division to obtain the mean; the result is truncated towards zero, which may be undesirable for non‑integral sums. No special handling for zero `count` is provided.
Purpose: Compute the arithmetic mean of a set of values.  
Input: `total` – the sum of all elements; `count` – the number of elements.  
Output: A `double` representing the mean (total / count).  
Algorithm: The function simply divides the total by the count, assuming `count` is non‑zero. No special handling for division‑by‑zero is performed.
```

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag bits in 'flags' exactly match the bits in 'mask'. The expression evaluates to true only when every bit in 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: `int flags` – the set of flags to test; `int mask` – the flag to look for.  
Output: `bool` – `true` if `flags` contains `mask`, otherwise `false`.  
Algorithm: Performs a bitwise AND between `flags` and `mask`; if the result equals `mask`, the flag is present; otherwise it is not.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j]; data[j] = data[i] ^ data[j]; data[i] = data[i] ^ data[j];
After the first XOR, data[j] becomes the original data[i].
The final XOR restores data[i] to its original value.
Purpose: Swaps the values at two indices in an integer array.
Input: `data` (int array), `i` (index of first element), `j` (index of second element).
Output: None (the function modifies the input array in place).
Algorithm: Uses bitwise XOR to swap the values without using a temporary variable.
```

### index_past_last_character — found 2/2

```
Returns the character at the position text.size(), which is undefined for empty strings.
Note: This implementation assumes the caller knows the string is non‑empty; otherwise undefined behavior occurs.
Purpose: Returns the last character of a string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null character if the string is empty.  
Algorithm: Directly accesses the character at the last position of the string, which is undefined for an empty string; the function assumes the caller handles the empty‑string case.
```

### correct_swap — clean, as it should be

```
outer loop: each pass places the smallest element of the unsorted suffix at the front
inner loop: compare adjacent elements and swap if they are out of order
swap only when the current element is larger than the next
preserve the value to be moved
move the larger element forward
restore the original value at the end of the pass
continue until the entire array is sorted
Purpose: Sorts an array of integers in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The function modifies the array in place; it returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times to avoid unnecessary comparisons after each pass. The loop stops when no swaps occur, indicating the array is sorted.
```

### correct_binary_search — clean, as it should be

```
initialise search bounds
continue while search interval is valid
compute middle index safely
target found at mid
target lies in the right half
target lies in the left half
target not present in array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first match, or -1 if not present.  
Algorithm: Perform a binary search, narrowing the search interval each iteration. If the middle element equals the target, return its index; otherwise, discard the half containing the target and continue searching the other half. The loop terminates when the interval collapses, indicating the target is absent.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and return an iterator to the next element.
If the element is non‑negative, simply advance the iterator.
Move to the next element without erasing it.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector, with all negative values removed.  
Algorithm: Iterate with an iterator; if the element is negative, erase it and advance the iterator to skip the next element. If the element is non‑negative, simply advance the iterator. This runs in O(n) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the count of occurrences
iterate over the entire vector
compare current element with the target
increment when a match is found
return the total count
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. Finally, return the counter.
```
