class Solution {
public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        if (lists.empty()) return nullptr;
        
        priority_queue<ListNode*, vector<ListNode*>, function<bool(ListNode*, ListNode*)>> minHeap(
            [](ListNode* a, ListNode* b) { return a->val > b->val; }
        );
        
        for (ListNode* node : lists) {
            if (node) {
                minHeap.push(node);
            }
        }
        
        ListNode dummy(0);
        ListNode* current = &dummy;
        
        while (!minHeap.empty()) {
            ListNode* node = minHeap.top();
            minHeap.pop();
            
            current->next = node;
            current = current->next;
            
            if (node->next) {
                minHeap.push(node->next);
            }
        }
        
        return dummy.next;
    }
};