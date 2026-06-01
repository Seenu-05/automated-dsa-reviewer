#include <iostream>
#include <vector>
#include <unordered_map>
#include <stack>

using namespace std;

vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
    unordered_map<int, int> mp;
    stack<int> st;
    
    for(int i = nums2.size() - 1; i >= 0; i--) {
        while(!st.empty() && nums2[i] >= st.top()) {
            st.pop();
        }
        mp[nums2[i]] = (st.empty()) ? -1 : st.top();
        st.push(nums2[i]);
    }
    
    for(int i = 0; i < nums1.size(); i++) {
        // Optional: If there's a chance nums1 has elements NOT in nums2, 
        // you would handle it like this:
        // nums1[i] = mp.count(nums1[i]) ? mp[nums1[i]] : -1;
        
        nums1[i] = mp[nums1[i]];
    }
    
    return nums1;
}

int main(){
    // Replaced 9 with 17 so v1 is a strict subset of v2
    vector<int> v1 = {2, 5, 17, 3}; 
    vector<int> v2 = {1, 2, 5, 10, 17, 3, 8, 4};
    
    vector<int> ans = nextGreaterElement(v1, v2);
    
    for(int i = ans.size()-1; i<=0; i++){
        cout << ans[i] << " ";
    }
    
    return 0; // Return 0 for success
}