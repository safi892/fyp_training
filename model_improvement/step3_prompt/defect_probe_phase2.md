# Defect-awareness probe

Does explicit wording get the model to report what a line *does* rather than
what the function looks like it was meant to do? The trained wording is the
control: it is exactly what `/analyze` sends today.

A phrasing only helps if it moves the first two columns without moving the
third — correct code is the product's normal input, and inventing defects in
it would be a worse failure than missing real ones.

| phrasing | problems named | false claims (of 8) | defects invented on correct code (of 4) | anchor validity |
| --- | :---: | :---: | :---: | :---: |
| `trained_wording` | 8/55 | 7 | 1 | 95/95 |
| `describe_effect` | 8/55 | 8 | 0 | 92/92 |
| `assume_nothing` | 16/55 | 8 | 0 | 100/100 |

---

## trained_wording

> *(the trained instruction, unchanged)*

### broken_swap — found 0/3, **asserted something false**

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

### overflow_mid — found 0/1

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

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the size.
If the current element is negative, erase it.
Purpose: Removes all negative integers from a vector.
Input: A reference to a vector of integers.
Output: None (the vector is modified in place).
Algorithm: Iterates through the vector and erases elements that are negative.
```

### dangling_reference — found 0/3

```
Build a descriptive string containing the code value.
Return a non‑const reference to the constructed string.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only reference to a string containing "code: " followed by the code.  
Algorithm: Constructs a string by concatenating "code: " with std::to_string(code), then returns a reference to that string. No mutation occurs.
```

### self_shadowing_counter — found 0/3

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

### unsigned_wraparound — found 0/4

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

### shallow_copy_double_free — found 1/3

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

### misleading_function_name — found 3/3

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

### loop_bound_off_by_one — found 1/3

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

### assignment_in_condition — found 1/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to 'value'. If the comparison is true, the function returns true immediately.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a specified target.
Input: Two integers, `value` and `target`.
Output: A boolean indicating whether `value` equals `target`.
Algorithm: Compares `value` with `target` and returns true if they are equal, otherwise false.
```

### switch_fallthrough — found 1/3

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

### accumulated_float_equality — found 0/3

```
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the total distance covered.
After the loop, compare the accumulated distance to 1.0.
Purpose: Determines whether a sequence of adding a fixed step to zero reaches exactly 1.0 after a specified number of steps.  
Input: <code>double step</code> – the increment applied each iteration; <code>int steps</code> – total iterations.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum equals 1.0, otherwise <code>false</code>.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times, adding <code>step</code> each iteration. Finally, compare the total to 1.0 and return the result.
```

### sizeof_on_decayed_array — found 0/3, **asserted something false**

```
Returns the number of elements in the array. Assumes arr is a valid pointer to the first element; otherwise the behavior is undefined.
Purpose: Counts the number of elements in an integer array.  
Input: `int arr[]` – a pointer to the first element of the array.  
Output: `int` – the total count of elements in the array.  
Algorithm: The function computes the size of the array in bytes and divides it by the size of a single element, yielding the element count. No bounds checking is performed, so passing a null pointer or an empty array yields undefined behavior.
```

### leak_on_early_return — found 0/2

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

### recursion_without_base_case — found 0/3

```
Recursive definition: countDown(n) = n + countDown(n‑1)
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding 1 each time, until n reaches zero, then returns the accumulated count.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the original values.  
Output: The vector is modified in place; no return value.  
Algorithm: Iterate over the vector with a range‑based for loop, and for each element insert it back into the vector using push_back. This effectively doubles the size of the vector.
```

### integer_division_before_widening — found 1/2

```
Compute the arithmetic mean by dividing total by count. This assumes count > 0; otherwise the result is undefined.
Purpose: Computes the arithmetic mean of a total value divided by a count.  
Input: `total` – the sum or total value; `count` – the number of elements or observations.  
Output: Returns a `double` representing the mean (total / count).  
Algorithm: Performs integer division to obtain the mean, which may truncate towards zero for negative inputs. No explicit handling of division‑by‑zero or overflow is performed.
```

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag represented by 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given integer mask.
Input: Two integers, `flags` and `mask`, where `flags` is the integer containing the flags and `mask` is the integer defining the flag to check.
Output: A boolean value indicating whether the flag is set in the mask.
Algorithm: Performs a bitwise AND operation between `flags` and `mask`. If the result equals `mask`, it means the flag is set, and the function returns `true`; otherwise, it returns `false`.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j]; data[j] = data[i] ^ data[j]; data[i] = data[i] ^ data[j];
After the first XOR, data[j] becomes the original value of data[i].
The final XOR restores data[i] to its original value.
Purpose: Swaps the elements at two specified indices in an integer array.
Input: `data` (int array), `i` (index of first element), `j` (index of second element).
Output: None (the array is modified in place).
Algorithm: Uses bitwise XOR to swap the values at indices `i` and `j` without using a temporary variable.
```

### index_past_last_character — found 0/2, **asserted something false**

```
Access the character at the last position; undefined for empty strings.
Purpose: Returns the last character of a given string.
Input: A constant reference to a std::string.
Output: A char representing the last character of the string.
Algorithm: Directly accesses the element at the last index of the string.
```

### correct_swap — **invented a defect**

```
Outer loop: each pass sorts the next largest element from the unsorted part
Inner loop: compare adjacent elements and swap if they are in the wrong order
If the current element is greater than the next, swap them
Store the current element temporarily
Move the next element forward
Place the stored element at the correct position
Purpose: Sort an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order. The outer loop runs `n‑1` times, each inner loop processes the remaining unsorted segment. This bubble‑sort implementation runs in O(n²) time and O(1) extra space.
```

### correct_binary_search — clean, as it should be

```
Initialize search bounds: low points to the first element, high points to the last element.
Perform binary search until the subarray is empty.
Compute middle index to avoid overflow.
If target is found at mid, return its index.
Target lies in the right half; shrink left boundary.
Target lies in the left half; shrink right boundary.
If loop exits without finding target, return -1.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present, otherwise `-1`.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and repeat with the remaining interval.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the container size.
If the current element is negative, erase it and advance the iterator.
Erase the element at 'it' and re‑assign the iterator to the new end.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: std::vector<int>& values – the vector to be modified in‑place.  
Output: void – the vector is mutated in‑place; no return value.  
Algorithm: Iterate with an iterator; if the element is negative, erase it and re‑compute the iterator. If the element is non‑negative, simply advance the iterator. This runs in O(n) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the number of occurrences of wanted
iterate over each element; size_t avoids signed/unsigned warnings
increment only when the current item matches wanted
note: if wanted is not present, found remains 0
NOTE: if wanted is not present, found remains 0
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Iterate over the vector with a size_t index, increment a counter each time the current element equals wanted, and finally return the counter.
```

## describe_effect

> Describe what each line actually does when executed. Do not describe what the function appears intended to do.

### broken_swap — found 0/3, **asserted something false**

```
Outer loop: each pass sorts the next largest element from the unsorted part
Inner loop: compare adjacent elements and swap if they are in the wrong order
If the current element is greater than the next, swap them
Move the larger element to the front
Place the original element at the correct position
Purpose: Sorts an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly traverse the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop repeats `n‑1` times, each inner loop processes the remaining unsorted segment. This bubble‑sort implementation runs in O(n²) time.
```

### overflow_mid — found 0/1

```
Binary search loop: shrink the search interval until low > high.
Compute midpoint to decide which half to explore.
Target found at mid; return its index.
Target lies in the right half; move low to mid+1.
Target lies in the left half; move high to mid-1.
Target not present in the array.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present; otherwise returns -1.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element with the target. If the middle element equals the target, return its index. If it is less, discard the left half; if it is greater, discard the right half. Continue until the interval is empty.
```

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the size.
If the current element is negative, erase it.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no return value.  
Algorithm: Iterate over the vector with an iterator; when an element is negative, erase it from the container. This yields a vector with only non‑negative values.
```

### dangling_reference — found 0/3

```
Build a descriptive string by concatenating a fixed prefix with the integer value.
Return a non‑const reference to the constructed string; callers may modify it.
Purpose: Returns a string describing the given integer code.  
Input: An `int` `code` representing the value to describe.  
Output: A `const std::string&` containing the formatted description.  
Algorithm: Constructs a string by concatenating the literal prefix with the integer’s string representation, then returns the result by value.
```

### self_shadowing_counter — found 0/3

```
accumulator for the number of occurrences of wanted
iterate over each element; size_t is used for safety with empty vectors
compare current element with the target value
increment the counter; this is a no‑op because the variable is re‑declared
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: `items` – a const reference to a vector of ints; `wanted` – the target integer to search for.  
Output: An int representing the number of occurrences of `wanted` in `items`.  
Algorithm: Initializes a counter to zero, then iterates over the vector, incrementing the counter each time the current element equals `wanted`. Finally, returns the counter value.
```

### unsigned_wraparound — found 0/4

```
Iterate over the vector, comparing each element with its successor.
If any element is greater than the next, the series is not strictly ascending.
Early exit on first violation.
If the loop completes without finding a violation, the series is ascending.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last, comparing each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
```

### shallow_copy_double_free — found 1/3

```
pointer to the allocated integer array
number of elements in the buffer
Constructor: allocate n integers and store the size. Caller must ensure n > 0; otherwise undefined behavior.
Copy constructor: copy the raw pointer and size from another Buffer. This is a shallow copy; the caller must ensure the source buffer is valid.
Purpose: Provides a simple, copy‑elided buffer class that owns an array of ints.  
Input: `std::size_t n` – size of the buffer to allocate.  
Output: Constructs a `Buffer` object; no return value.  
Algorithm: The constructor allocates `n` ints on the heap and stores the pointer and length. The destructor deletes the allocated memory. The copy constructor copies the pointer and length from the source object, relying on copy elision to avoid copying the pointer.
```

### misleading_function_name — found 3/3

```
accumulator for sum of perfect squares ≤ limit
iterate over each integer i from 2 up to limit
flag tracks whether i is a perfect square
test divisibility up to sqrt(i)
if i has a divisor other than 1 or itself, i is not a perfect square
if i is a perfect square, add it to the total
continue outer loop for next i
total now holds sum of all perfect squares ≤ limit
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each integer i from 2 to limit, a nested loop tests divisibility by all numbers j ≤ √i; if none divide i, i is prime and added to the total. The outer loop runs O(limit) times, yielding O(√limit) time.
```

### loop_bound_off_by_one — found 1/3

```
accumulator for the sum
iterate over the vector; the loop runs one extra time to include the last element
add the current element to the total
return the accumulated sum (undefined for empty vector)
Purpose: Computes the cumulative sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer sequence to sum.  
Output: int – the total sum of the vector elements.  
Algorithm: Initializes a running total to zero, then iterates over the vector indices from 0 to the vector size (inclusive) and adds each element to the total. The final total is returned.
```

### assignment_in_condition — found 1/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to 'value'. If the comparison is true, the function returns true immediately.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a specified target.  
Input: `int value` – the integer to compare; `int target` – the target value to compare against.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function performs a simple equality check using the assignment operator; if the condition is true, it returns `true`; otherwise it returns `false`. This yields a trivial “equal‑to‑target” predicate.
```

### switch_fallthrough — found 1/3

```
initialize score accumulator
map letter grade to numeric score
A is the highest grade, worth 4 points
B is the second highest, worth 3 points
C is the third highest, worth 2 points
any other grade yields 0 points (e.g., 'D', 'F')
fall‑through: the default case covers all grades
return the accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing a letter from 'A' to 'F'.  
Output: An `int` score where 'A' maps to 4, 'B' to 3, 'C' to 2, and all other grades map to 0.  
Algorithm: Initializes a score accumulator to 0, then uses a switch statement to assign the appropriate value based on the grade. The default case handles any unrecognized grade by setting the score to 0.
```

### accumulated_float_equality — found 0/3

```
Iterate 'steps' times, accumulating 'step' each iteration.
Add the current step to the running total.
After the loop, compare the accumulated sum to 1.0.
Purpose: Determines whether a sequence of adding a fixed step to zero eventually reaches exactly 1.0.  
Input: <code>double step</code> – the increment applied each iteration; <code>int steps</code> – total number of iterations.  
Output: <code>bool</code> – <code>true</code> if the accumulated sum equals 1.0 after <code>steps</code> iterations, otherwise <code>false</code>.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times adding <code>step</code> each iteration. After the loop, compare the total to 1.0 and return the result.
```

### sizeof_on_decayed_array — found 0/3, **asserted something false**

```
Returns the number of elements in the array. The cast to size_t is unnecessary because sizeof(arr) already yields a size_t.
Purpose: Counts the number of elements in an integer array.  
Input: An array of integers (passed as a pointer).  
Output: An integer representing the array's length.  
Algorithm: The function computes the total size of the array using `sizeof` and divides it by the size of a single element to obtain the count. No bounds checking is performed; passing a null pointer yields undefined behavior.
```

### leak_on_early_return — found 0/2, **asserted something false**

```
allocate a boolean array to track which elements have been seen
accumulator for the total of elements that are ≤ limit
iterate over the input vector
early exit: any element exceeding the limit is invalid
return sentinel error code
accumulate only those elements ≤ limit
release the allocated memory
return the total of valid elements
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: `values` – a vector of integers; `limit` – an integer threshold.  
Output: Returns the accumulated sum of qualifying elements; returns -1 if any element exceeds `limit`.  
Algorithm: Allocate a boolean array of size `values.size()` to mark seen elements, initialize a sum accumulator, iterate over `values`, and add each element to the sum only if it is less than `limit`. After the loop, deallocate the array and return the accumulated sum.
```

### recursion_without_base_case — found 0/3

```
Recursive definition: countDown(n) = n + countDown(n‑1)
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (n ≥ 0).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding 1 each time, forming a classic “count down” recursion. The recursion stops when n reaches 0, yielding a total of n + 1 calls.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the original values.  
Output: The vector is modified in‑place; no return value.  
Algorithm: Iterate over the vector with a range‑based for loop, and for each element insert it back into the vector using push_back. This effectively doubles the size of the vector.
```

### integer_division_before_widening — found 1/2

```
Compute the arithmetic mean by dividing total by count. This assumes count is non‑zero; division by zero would be undefined.
Purpose: Computes the arithmetic mean of a total and a count.  
Input: `total` – the sum of all elements; `count` – the number of elements.  
Output: A `double` representing the mean value.  
Algorithm: Performs integer division `total / count`, which truncates towards zero, yielding the arithmetic mean. No explicit handling of division‑by‑zero or overflow is performed.
```

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag represented by 'mask' is set in 'flags'.
Purpose: Determines whether a specific flag is set in a given set of flags.  
Input: `int flags` – the current state of flags; `int mask` – the flag to test.  
Output: `bool` – `true` if `flags` contains `mask`, otherwise `false`.  
Algorithm: Performs a bitwise AND between `flags` and `mask`; if the result equals `mask`, the flag is present; otherwise it is not.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j];
data[j] = data[j] ^ data[i];
data[i] = data[i] ^ data[j];
Purpose: Swaps the elements at two specified indices in an integer array.
Input: `data` (array of integers), `i` (index of the first element), `j` (index of the second element).
Output: None (the function modifies the array in place).
Algorithm: Uses bitwise XOR to swap the values at indices `i` and `j` without using a temporary variable.
```

### index_past_last_character — found 0/2, **asserted something false**

```
Accesses the character at the last position of the string. If the string is empty, this results in undefined behavior because text[text.size()] is out‑of‑bounds.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size() (the string’s length minus one).  
Algorithm: The function computes the string’s length via text.size() and accesses the element at that index, assuming the string is non‑empty; out‑of‑bounds access would be undefined behavior.
```

### correct_swap — clean, as it should be

```
Outer loop: each pass sorts the next largest element from the unsorted part
Inner loop: compare adjacent elements and swap if they are out of order
If the current element is greater than the next, swap them
Store the current element temporarily
Move the next element forward
Place the stored element at the correct position
Purpose: Sort an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order. The outer loop runs n‑1 times, each inner loop processes the remaining unsorted segment. This bubble‑sort implementation runs in O(n²) time.
```

### correct_binary_search — clean, as it should be

```
Binary search loop: shrink the search interval until low > high.
Compute middle index to avoid overflow.
Target found at mid.
Target lies in the right half.
Target lies in the left half.
Target not present in the array.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present; otherwise returns -1.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half of the interval that cannot contain the target and repeat. The loop terminates when the interval is empty, indicating the target is absent.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while maintaining a valid iterator.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and re‑assign the iterator.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no return value.  
Algorithm: Iterate with an iterator; if the element is negative, erase it and re‑assign the iterator to the new position (which may be the end). If the element is non‑negative, simply advance the iterator. This eliminates negatives in‑place.
```

### correct_counter — clean, as it should be

```
accumulator for the number of occurrences of wanted
iterate over the entire vector; using size_t avoids signed/unsigned warnings
increment only when the current element equals wanted
accumulate the count
return the total occurrences
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initializes a counter to zero, then iterates over the vector, incrementing the counter each time the current element equals wanted. Finally returns the counter.
```

## assume_nothing

> This code may contain defects. Do not assume it is correct. Describe what each line actually does when executed, and where a line's effect differs from what the surrounding code appears intended to achieve, say so plainly.

### broken_swap — found 0/3, **asserted something false**

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

### overflow_mid — found 0/1

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

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the size.
If the current element is negative, erase it.
Erase the element at the current iterator position.
Purpose: Removes all negative integers from a vector.  
Input: std::vector<int>& values – the vector to be modified.  
Output: void – the vector is mutated in‑place; no return value.  
Algorithm: Iterate with an iterator; when an element is found to be negative, erase it from the container. The loop naturally handles the case where the vector is empty, leaving it unchanged.
```

### dangling_reference — found 0/3

```
Build a descriptive string by concatenating a fixed prefix with the integer value.
Return a reference to the immutable result; the caller may modify it but the function itself does not modify the object.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to describe.  
Output: const std::string& – a read‑only copy of a formatted description.  
Algorithm: Constructs a string with the literal prefix “code: ” and the integer’s decimal representation, then returns the result by value. No mutation occurs; the caller receives a copy of the constructed string.
```

### self_shadowing_counter — found 1/3

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

### unsigned_wraparound — found 0/4

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

### shallow_copy_double_free — found 1/3

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

### misleading_function_name — found 3/3

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

### loop_bound_off_by_one — found 2/3

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

### assignment_in_condition — found 3/3

```
Compare the two integers; the assignment operator (=) is used to assign the result of the comparison to 'value'. This is a common pitfall because it modifies the left operand while the right operand is evaluated. The assignment operator returns the value of the right operand, which is then compared to the left operand. The result is always true because the assignment always succeeds.
If the comparison is true, the function returns true.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function performs a simple equality check using the assignment operator; if the comparison succeeds, it returns `true`; otherwise it returns `false`. This yields a false‑positive for equality, which is the intended behavior.
```

### switch_fallthrough — found 1/3

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

### accumulated_float_equality — found 0/3, **asserted something false**

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

### sizeof_on_decayed_array — found 0/3, **asserted something false**

```
Returns the number of elements in the array. The size of the pointer itself (sizeof(arr)) is divided by the size of the first element (sizeof(arr[0])) to count the items. This works for arrays of any size, but may produce incorrect results for null pointers or arrays with zero elements.
Purpose: Counts the number of elements in an integer array.  
Input: An array of integers passed as a pointer (int arr[]).  
Output: An integer representing the array's length (number of elements).  
Algorithm: The function uses the standard library macro `sizeof` to obtain the total size of the array in bytes and divides it by the size of a single element to compute the count. This yields the number of elements in the array.
```

### leak_on_early_return — found 0/2, **asserted something false**

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

### recursion_without_base_case — found 2/3

```
This recursive definition is incorrect because it does not terminate for n <= 0. The recursion would continue indefinitely, leading to a stack overflow.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding 1 each time, until n reaches zero, then returns the accumulated count. The recursion depth grows exponentially, leading to a stack overflow for large n.
```

### grow_during_range_for — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the source values.  
Output: The same vector is modified in place; no return value.  
Algorithm: Iterate over the vector with a range‑based for‑loop, inserting each element into the vector using push_back. This results in a vector with twice the original size, each element appearing twice.
```

### integer_division_before_widening — found 1/2

```
Returns the integer division of total by count, which is the arithmetic mean.
Purpose: Computes the arithmetic mean of a total and a count.  
Input: `total` – the sum of all elements; `count` – the number of elements.  
Output: A `double` representing the mean (total / count).  
Algorithm: Performs integer division, which truncates towards zero, yielding the floor division result. No explicit handling of division‑by‑zero or overflow is performed.
```

### operator_precedence — found 0/2, **asserted something false**

```
Returns true if the flag represented by 'mask' is set in 'flags'. The expression evaluates to true only when 'flags' contains exactly the bits specified by 'mask' (i.e., 'flags & mask == mask').
Purpose: Determines whether a specific flag is set in a given integer mask.
Input: Two integers, `flags` and `mask`, where `flags` is the integer containing the flags and `mask` is the integer defining the flag to check.
Output: A boolean indicating whether the flag is set in the mask.
Algorithm: Performs a bitwise AND operation between `flags` and `mask`. If the result equals `mask`, the flag is set; otherwise, it is not.
```

### xor_swap_same_index — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j]; data[j] = data[i] ^ data[j]; data[i] = data[i] ^ data[j];
After the first XOR, data[j] becomes the original value of data[i].
The final XOR restores data[i] to its original value.
Purpose: Swaps the elements at two specified indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i` and `j` – indices of the elements to exchange.  
Output: None (the array is modified in‑place).  
Algorithm: Uses the XOR‑swap technique to swap `data[i]` and `data[j]` without using a temporary variable. Each XOR operation is performed in a single statement, which is efficient and concise.
```

### index_past_last_character — found 2/2

```
Accesses the character at the last position of the string. If the string is empty, this yields undefined behavior because text[text.size()] is out‑of‑bounds.
Purpose: Returns the last character of a given string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or the null terminator if the string is empty.  
Algorithm: Directly accesses the string’s size and returns the character at that position, which is undefined for an empty string because the size is out‑of‑range. No bounds checking is performed.
```

### correct_swap — clean, as it should be

```
Outer loop: each pass sorts the next largest element from the unsorted part
Inner loop: compare adjacent elements and swap if they are out of order
If the current element is greater than the next, swap them
Store the current element temporarily
Move the next element forward
Place the stored element at the correct position
After each outer loop, the largest element is at the end of the array
Purpose: Sort an integer array in ascending order using bubble sort.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly scan the array from the start, swapping adjacent elements when they are out of order. The outer loop runs n‑1 times, the inner loop runs n‑i‑1 times, yielding O(n²) time and O(1) extra space.
```

### correct_binary_search — clean, as it should be

```
Binary search loop: shrink the search interval until low > high.
Compute middle index to avoid overflow.
Target found at mid.
Target lies in the right half.
Target lies in the left half.
Target not present in the array.
Purpose: Locate the index of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Returns the index of `target` if present, otherwise `-1`.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, indicating the target is absent.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the container size.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and re‑assign the iterator to the new end.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no return value.  
Algorithm: Iterate with an iterator; if the element is negative, erase it and advance the iterator; otherwise, simply advance. This eliminates negatives in‑place and preserves the original order.
```

### correct_counter — clean, as it should be

```
accumulator for the number of occurrences of wanted
iterate over each element; size_t avoids signed/unsigned warnings
compare current element with the target value
increment count when a match is found
return total occurrences
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to count.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero, then iterate over the vector with a size_t index, incrementing the counter each time the current element equals wanted. Finally return the counter.
```
