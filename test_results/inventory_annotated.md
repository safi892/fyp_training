# inventory.cpp — line-by-line

`best_adapter` · 121 lines · 8 chunks · 48/48 anchors verified against the file

Every comment below was checked against the line it points at. Anything the model invented was dropped rather than shown.

```cpp
   1  #include <iostream>                                                 
   2  #include <vector>                                                   
   3  #include <string>                                                   
   4  #include <algorithm>                                                
   5                                                                      
   6  // A small inventory manager used to exercise whole-file annotation.
   7                                                                      
   8  struct Item                                                         
   9  {                                                                   
  10    std::string name;                                                    // name of the item
  11    int quantity;                                                        // number of units currently in stock
  12    double price;                                                        // cost per unit in dollars
  13  };                                                                  
  14                                                                      
  15  class Inventory                                                     
  16  {                                                                   
  17  public:                                                             
  18    void add(const std::string& name, int quantity, double price)     
  19    {                                                                 
  20      for (size_t i = 0; i < items.size(); i++)                          // Iterate over all existing items to see if we already have one with this name.
  21      {                                                               
  22        if (items[i].name == name)                                       // If a matching item is found, simply increment its quantity and exit early.
  23        {                                                             
  24          items[i].quantity += quantity;                              
  25          return;                                                     
  26        }                                                             
  27      }                                                               
  28      Item fresh;                                                        // No matching entry exists – create a new item with the provided details.
  29      fresh.name = name;                                                 // Copy the supplied name into the new item.
  30      fresh.quantity = quantity;                                         // Record the requested quantity.
  31      fresh.price = price;                                               // Store the unit price.
  32      items.push_back(fresh);                                            // Append the newly created item to the container.
  33    }                                                                 
  34                                                                      
  35    bool remove(const std::string& name, int quantity)                
  36    {                                                                 
  37      for (size_t i = 0; i < items.size(); i++)                          // Iterate over each item in the inventory.
  38      {                                                               
  39        if (items[i].name == name)                                       // If the current item matches the target name.
  40        {                                                             
  41          if (items[i].quantity < quantity)                              // Check if there are enough units to satisfy the request.
  42            return false;                                                // Not enough stock – transaction fails.
  43          items[i].quantity -= quantity;                                 // Consume the required amount.
  44          if (items[i].quantity == 0)                                    // After consumption, if the item becomes empty, erase it from the container.
  45            items.erase(items.begin() + i);                              // Use `erase` with an iterator to avoid invalidating iterators.
  46          return true;                                                
  47        }                                                             
  48      }                                                               
  49      return false;                                                      // No matching item found.
  50    }                                                                 
  51                                                                      
  52    double totalValue() const                                         
  53    {                                                                 
  54      double sum = 0.0;                                                  // accumulator for the total value
  55      for (size_t i = 0; i < items.size(); i++)                          // iterate over each item in order to compute its contribution
  56        sum += items[i].quantity * items[i].price;                       // add product of quantity and price to the running total
  57      return sum;                                                     
  58    }                                                                 
  59                                                                      
  60  private:                                                            
  61    std::vector<Item> items;                                          
  62  };                                                                  
  63                                                                      
  64  int binarySearch(const std::vector<int>& sorted, int target)        
  65  {                                                                   
  66    int low = 0;                                                         // start search at first index
  67    int high = static_cast<int>(sorted.size()) - 1;                      // end search at last index (or one past the end)
  68    while (low <= high)                                                  // continue while there is still a valid interval
  69    {                                                                 
  70      int mid = low + (high - low) / 2;                                  // compute middle index safely to avoid overflow
  71      if (sorted[mid] == target)                                         // target found exactly at mid
  72        return mid;                                                      // return its position
  73      if (sorted[mid] < target)                                          // target lies in the right half
  74        low = mid + 1;                                                   // discard left half including mid
  75      else                                                               // target lies in the left half
  76        high = mid - 1;                                                  // discard right half including mid
  77    }                                                                 
  78    return -1;                                                           // target not present in the array
  79  }                                                                   
  80                                                                      
  81  int gcd(int a, int b)                                               
  82  {                                                                   
  83    while (b != 0)                                                       // Repeatedly apply the Euclidean algorithm until b becomes zero.
  84    {                                                                 
  85      int rest = a % b;                                                  // Compute remainder; this step implements the division‑by‑remainder rule.
  86      a = b;                                                             // Shift the larger value to become the divisor for the next iteration.
  87      b = rest;                                                          // The current remainder becomes the new dividend.
  88    }                                                                    // When b reaches zero, a holds the greatest common divisor.
  89    return a;                                                         
  90  }                                                                   
  91                                                                      
  92  void bubbleSort(std::vector<int>& data)                             
  93  {                                                                   
  94    for (size_t pass = 0; pass + 1 < data.size(); pass++)                // Outer loop controls how many passes we perform; each iteration reduces the unsorted portion by one element.
  95    {                                                                 
  96      for (size_t j = 0; j + 1 < data.size() - pass; j++)                // Inner loop compares adjacent elements and swaps them when they are out of order.
  97      {                                                               
  98        if (data[j] > data[j + 1])                                       // Swap only if the current element is greater than its successor.
  99        {                                                             
 100          int keep = data[j];                                         
 101          data[j] = data[j + 1];                                      
 102          data[j + 1] = keep;                                         
 103        }                                                             
 104      }                                                               
 105    }                                                                 
 106  }                                                                   
 107                                                                      
 108  int main()                                                          
 109  {                                                                   
 110    Inventory store;                                                     // create an empty inventory
 111    store.add("bolt", 40, 0.25);                                         // add bolt with quantity 40 at price 0.25
 112    store.add("nut", 60, 0.10);                                          // add nut with quantity 60 at price 0.10
 113    store.remove("bolt", 5);                                             // remove 5 bolts to keep stock at 40
 114    std::cout << "value: " << store.totalValue() << std::endl;           // display total monetary value of all items
 115                                                                      
 116    std::vector<int> numbers = {9, 4, 7, 1, 3};                       
 117    bubbleSort(numbers);                                                 // sort the vector in ascending order using bubble sort
 118    std::cout << "index: " << binarySearch(numbers, 7) << std::endl;     // locate index of element 7; assumes 7 exists
 119    std::cout << "gcd: " << gcd(48, 18) << std::endl;                    // compute greatest common divisor of 48 and 18
 120    return 0;                                                         
 121  }                                                                   
```