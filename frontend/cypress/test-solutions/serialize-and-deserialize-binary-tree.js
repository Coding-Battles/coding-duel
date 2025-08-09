/**
 * Definition for a binary tree node.
 * function TreeNode(val) {
 *     this.val = val;
 *     this.left = this.right = null;
 * }
 */

class Solution {
    serialize(root) {
        const vals = [];
        
        function preorder(node) {
            if (!node) {
                vals.push("null");
            } else {
                vals.push(node.val.toString());
                preorder(node.left);
                preorder(node.right);
            }
        }
        
        preorder(root);
        return vals.join(',');
    }
    
    deserialize(data) {
        const vals = data.split(',');
        let index = 0;
        
        function build() {
            if (index >= vals.length || vals[index] === "null") {
                index++;
                return null;
            }
            const node = new TreeNode(parseInt(vals[index]));
            index++;
            node.left = build();
            node.right = build();
            return node;
        }
        
        return build();
    }
}