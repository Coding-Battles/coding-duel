// Definition for a binary tree node.
// function TreeNode(val, left, right) {
//     this.val = (val===undefined ? 0 : val)
//     this.left = (left===undefined ? null : left)
//     this.right = (right===undefined ? null : right)
// }
class Solution {
    maxDepth(root) {
        if (root === null) {
            return 0;
        }
        
        const leftDepth = this.maxDepth(root.left);
        const rightDepth = this.maxDepth(root.right);
        
        return Math.max(leftDepth, rightDepth) + 1;
    }
}