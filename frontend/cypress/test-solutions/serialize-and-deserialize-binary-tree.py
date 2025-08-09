# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def serialize(self, root):
        """Encodes a tree to a single string."""
        def preorder(node):
            if not node:
                vals.append("null")
            else:
                vals.append(str(node.val))
                preorder(node.left)
                preorder(node.right)
        
        vals = []
        preorder(root)
        return ','.join(vals)

    def deserialize(self, data):
        """Decodes your encoded data to tree."""
        def build():
            val = next(vals)
            if val == "null":
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node
        
        vals = iter(data.split(','))
        return build()