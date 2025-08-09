// Definition for a binary tree node.
// function TreeNode(val, left, right) {
//     this.val = (val===undefined ? 0 : val)
//     this.left = (left===undefined ? null : left)
//     this.right = (right===undefined ? null : right)
// }
class Solution {
    isSameTree(p, q) {
        if (p === null && q === null) {
            return true;
        }
        
        if (p === null || q === null) {
            return false;
        }
        
        if (p.val !== q.val) {
            return false;
        }
        
        return this.isSameTree(p.left, q.left) && this.isSameTree(p.right, q.right);
    }
}