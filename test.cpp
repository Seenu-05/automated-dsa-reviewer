#include <iostream>
#include <vector>

using namespace std;

// Inefficient sorting algorithm
void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    
    cout << "Original array: ";
    for (int num : data) cout << num << " ";
    cout << endl;

    bubbleSort(data);

    cout << "Sorted array: ";
    for (int num : data) cout << num << " ";
    cout << endl;

    return 0;
}