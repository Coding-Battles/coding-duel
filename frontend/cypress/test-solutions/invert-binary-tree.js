// Definition for a binary tree node.
// function TreeNode(val, left, right) {
//     this.val = (val===undefined ? 0 : val)
//     this.left = (left===undefined ? null : left)
//     this.right = (right===undefined ? null : right)
// }
class Solution {
    invertTree(root) {
        if (root === null) {
            return null;
        }
        
        // Swap left and right children
        const temp = root.left;
        root.left = root.right;
        root.right = temp;
        
        // Recursively invert subtrees
        this.invertTree(root.left);
        this.invertTree(root.right);
        
        return root;
    }
}