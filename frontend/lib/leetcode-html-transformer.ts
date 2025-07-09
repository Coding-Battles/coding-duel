/**
 * Transforms HTML content to use LeetCode-style custom classes
 * instead of hardcoded Tailwind classes
 */
export function transformLeetCodeHtml(html: string): string {
  return html
    // Transform the examples container for proper spacing
    .replace(/class="space-y-4"/g, 'class="leetcode-examples-container"')
    
    // Transform example boxes
    .replace(/class="bg-gray-50 p-4 rounded-lg"/g, 'class="leetcode-example"')
    
    // Transform constraints section
    .replace(/class="bg-blue-50 p-4 rounded-lg"/g, 'class="leetcode-constraints"')
    
    // Transform inline code elements
    .replace(/class="bg-gray-100 px-1 py-0\.5 rounded text-sm"/g, 'class="leetcode-code"')
    .replace(/class="bg-white px-1 py-0\.5 rounded"/g, 'class="leetcode-code"')
    
    // Transform headings
    .replace(/class="font-semibold mb-2"/g, 'class="leetcode-heading"')
    .replace(/class="font-semibold mb-2 text-blue-800"/g, 'class="leetcode-heading"')
    
    // Transform input/output sections
    .replace(/class="font-mono text-sm"/g, 'class="leetcode-input-output"')
    
    // Add explanation class to explanation text
    .replace(/<div><strong>Explanation:<\/strong>/g, '<div class="leetcode-explanation"><strong>Explanation:</strong>');
}

/**
 * Gets the appropriate difficulty class based on difficulty level
 */
export function getDifficultyClass(difficulty: string): string {
  switch (difficulty.toLowerCase()) {
    case 'easy':
      return 'leetcode-difficulty-easy';
    case 'medium':
      return 'leetcode-difficulty-medium';
    case 'hard':
      return 'leetcode-difficulty-hard';
    default:
      return 'leetcode-difficulty-easy';
  }
}