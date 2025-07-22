// Working solutions for Add Two Numbers problem in all supported languages

export const addTwoNumbersSolutions = {
  // Python solution
  python: `# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        current = dummy
        carry = 0
        
        while l1 or l2 or carry:
            sum_val = carry
            if l1:
                sum_val += l1.val
                l1 = l1.next
            if l2:
                sum_val += l2.val
                l2 = l2.next
                
            carry = sum_val // 10
            current.next = ListNode(sum_val % 10)
            current = current.next
            
        return dummy.next`,

  // JavaScript solution
  javascript: `/**
 * Definition for singly-linked list.
 * function ListNode(val, next) {
 *     this.val = (val===undefined ? 0 : val)
 *     this.next = (next===undefined ? null : next)
 * }
 */
class Solution {
    addTwoNumbers(l1, l2) {
        const dummy = new ListNode(0);
        let current = dummy;
        let carry = 0;
        
        while (l1 || l2 || carry) {
            let sumVal = carry;
            if (l1) {
                sumVal += l1.val;
                l1 = l1.next;
            }
            if (l2) {
                sumVal += l2.val;
                l2 = l2.next;
            }
            
            carry = Math.floor(sumVal / 10);
            current.next = new ListNode(sumVal % 10);
            current = current.next;
        }
        
        return dummy.next;
    }
}`,

  // Java solution
  java: `/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        int carry = 0;
        
        while (l1 != null || l2 != null || carry != 0) {
            int sumVal = carry;
            if (l1 != null) {
                sumVal += l1.val;
                l1 = l1.next;
            }
            if (l2 != null) {
                sumVal += l2.val;
                l2 = l2.next;
            }
            
            carry = sumVal / 10;
            current.next = new ListNode(sumVal % 10);
            current = current.next;
        }
        
        return dummy.next;
    }
}`,

  // C++ solution
  cpp: `/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode* dummy = new ListNode(0);
        ListNode* current = dummy;
        int carry = 0;
        
        while (l1 || l2 || carry) {
            int sumVal = carry;
            if (l1) {
                sumVal += l1->val;
                l1 = l1->next;
            }
            if (l2) {
                sumVal += l2->val;
                l2 = l2->next;
            }
            
            carry = sumVal / 10;
            current->next = new ListNode(sumVal % 10);
            current = current->next;
        }
        
        return dummy->next;
    }
};`
};