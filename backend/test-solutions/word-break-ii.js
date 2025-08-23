class Solution {
  wordBreak(s, wordDict) {
    const wordSet = new Set(wordDict);
    const memo = new Map();

    function dfs(start) {
      if (memo.has(start)) {
        return memo.get(start);
      }

      if (start === s.length) {
        return [""];
      }

      const result = [];
      for (let end = start + 1; end <= s.length; end++) {
        const word = s.substring(start, end);
        if (wordSet.has(word)) {
          const rest = dfs(end);
          for (const sentence of rest) {
            if (sentence) {
              result.push(word + " " + sentence);
            } else {
              result.push(word);
            }
          }
        }
      }

      memo.set(start, result);
      return result;
    }

    return dfs(0);
  }
}
