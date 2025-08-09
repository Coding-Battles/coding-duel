/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
public:
    // Encodes a tree to a single string.
    string serialize(TreeNode* root) {
        vector<string> vals;
        preorder(root, vals);
        return join(vals, ",");
    }
    
private:
    void preorder(TreeNode* node, vector<string>& vals) {
        if (!node) {
            vals.push_back("null");
        } else {
            vals.push_back(to_string(node->val));
            preorder(node->left, vals);
            preorder(node->right, vals);
        }
    }
    
    string join(const vector<string>& vals, const string& delimiter) {
        if (vals.empty()) return "";
        string result = vals[0];
        for (int i = 1; i < vals.size(); i++) {
            result += delimiter + vals[i];
        }
        return result;
    }
    
public:
    // Decodes your encoded data to tree.
    TreeNode* deserialize(string data) {
        vector<string> vals = split(data, ",");
        int index = 0;
        return build(vals, index);
    }
    
private:
    vector<string> split(const string& str, const string& delimiter) {
        vector<string> tokens;
        size_t start = 0;
        size_t end = str.find(delimiter);
        
        while (end != string::npos) {
            tokens.push_back(str.substr(start, end - start));
            start = end + delimiter.length();
            end = str.find(delimiter, start);
        }
        tokens.push_back(str.substr(start));
        return tokens;
    }
    
    TreeNode* build(const vector<string>& vals, int& index) {
        if (index >= vals.size() || vals[index] == "null") {
            index++;
            return nullptr;
        }
        TreeNode* node = new TreeNode(stoi(vals[index]));
        index++;
        node->left = build(vals, index);
        node->right = build(vals, index);
        return node;
    }
};