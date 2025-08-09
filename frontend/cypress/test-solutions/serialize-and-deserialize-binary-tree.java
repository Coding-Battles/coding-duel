/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode(int x) { val = x; }
 * }
 */
class Solution {
    
    // Encodes a tree to a single string.
    public String serialize(TreeNode root) {
        List<String> vals = new ArrayList<>();
        preorder(root, vals);
        return String.join(",", vals);
    }
    
    private void preorder(TreeNode node, List<String> vals) {
        if (node == null) {
            vals.add("null");
        } else {
            vals.add(String.valueOf(node.val));
            preorder(node.left, vals);
            preorder(node.right, vals);
        }
    }

    // Decodes your encoded data to tree.
    public TreeNode deserialize(String data) {
        String[] vals = data.split(",");
        return build(new int[]{0}, vals);
    }
    
    private TreeNode build(int[] index, String[] vals) {
        if (index[0] >= vals.length || vals[index[0]].equals("null")) {
            index[0]++;
            return null;
        }
        TreeNode node = new TreeNode(Integer.valueOf(vals[index[0]]));
        index[0]++;
        node.left = build(index, vals);
        node.right = build(index, vals);
        return node;
    }
}