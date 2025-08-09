// Definition for singly-linked list.
// function ListNode(val, next) {
//     this.val = (val===undefined ? 0 : val);
//     this.next = (next===undefined ? null : next);
// }

class Solution {
    addTwoNumbers(l1, l2) {
        const dummy = new ListNode(0);
        let current = dummy;
        let carry = 0;
        
        while (l1 !== null || l2 !== null || carry > 0) {
            const val1 = l1 !== null ? l1.val : 0;
            const val2 = l2 !== null ? l2.val : 0;
            
            const total = val1 + val2 + carry;
            carry = Math.floor(total / 10);
            const digit = total % 10;
            
            current.next = new ListNode(digit);
            current = current.next;
            
            l1 = l1 !== null ? l1.next : null;
            l2 = l2 !== null ? l2.next : null;
        }
        
        return dummy.next;
    }
}