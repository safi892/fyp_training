#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

// A small inventory manager used to exercise whole-file annotation.

struct Item
{
  std::string name;
  int quantity;
  double price;
};

class Inventory
{
public:
  void add(const std::string& name, int quantity, double price)
  {
    for (size_t i = 0; i < items.size(); i++)
    {
      if (items[i].name == name)
      {
        items[i].quantity += quantity;
        return;
      }
    }
    Item fresh;
    fresh.name = name;
    fresh.quantity = quantity;
    fresh.price = price;
    items.push_back(fresh);
  }

  bool remove(const std::string& name, int quantity)
  {
    for (size_t i = 0; i < items.size(); i++)
    {
      if (items[i].name == name)
      {
        if (items[i].quantity < quantity)
          return false;
        items[i].quantity -= quantity;
        if (items[i].quantity == 0)
          items.erase(items.begin() + i);
        return true;
      }
    }
    return false;
  }

  double totalValue() const
  {
    double sum = 0.0;
    for (size_t i = 0; i < items.size(); i++)
      sum += items[i].quantity * items[i].price;
    return sum;
  }

private:
  std::vector<Item> items;
};

int binarySearch(const std::vector<int>& sorted, int target)
{
  int low = 0;
  int high = static_cast<int>(sorted.size()) - 1;
  while (low <= high)
  {
    int mid = low + (high - low) / 2;
    if (sorted[mid] == target)
      return mid;
    if (sorted[mid] < target)
      low = mid + 1;
    else
      high = mid - 1;
  }
  return -1;
}

int gcd(int a, int b)
{
  while (b != 0)
  {
    int rest = a % b;
    a = b;
    b = rest;
  }
  return a;
}

void bubbleSort(std::vector<int>& data)
{
  for (size_t pass = 0; pass + 1 < data.size(); pass++)
  {
    for (size_t j = 0; j + 1 < data.size() - pass; j++)
    {
      if (data[j] > data[j + 1])
      {
        int keep = data[j];
        data[j] = data[j + 1];
        data[j + 1] = keep;
      }
    }
  }
}

int main()
{
  Inventory store;
  store.add("bolt", 40, 0.25);
  store.add("nut", 60, 0.10);
  store.remove("bolt", 5);
  std::cout << "value: " << store.totalValue() << std::endl;

  std::vector<int> numbers = {9, 4, 7, 1, 3};
  bubbleSort(numbers);
  std::cout << "index: " << binarySearch(numbers, 7) << std::endl;
  std::cout << "gcd: " << gcd(48, 18) << std::endl;
  return 0;
}
