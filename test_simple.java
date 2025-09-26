🧪 Testing template structure with simple code...
🔧 [JAVA SIGNATURE] Loaded signature for word-break-ii: {'parameters': [{'name': 's', 'type': 'string'}, {'name': 'wordDict', 'type': 'string[]'}], 'returnType': 'string[]'}
🔧 [JAVA SIGNATURE] Loaded signature for word-break-ii: {'parameters': [{'name': 's', 'type': 'string'}, {'name': 'wordDict', 'type': 'string[]'}], 'returnType': 'string[]'}
🔧 [JAVA WRAPPER] User has Solution class, injecting main method
📋 Full generated wrapper (504 lines):
  1: import java.util.*;
  2: import java.lang.reflect.*;
  3: 
  4: 
  5: // VersionControl API for first-bad-version problem
  6: class VersionControl {
  7:     private static int badVersion = 0;
  8:     
  9:     public static void setBadVersion(int bad) {
 10:         badVersion = bad;
 11:     }
 12:     
 13:     public static boolean isBadVersion(int version) {
 14:         return version >= badVersion;
 15:     }
 16: }
 17: 
 18: class Solution {
 19:     public int test() { return 42; }
 20: 
 21:     // Data structure definitions for linked list and tree problems
 22:     static class ListNode {
 23:         int val;
 24:         ListNode next;
 25:         ListNode() {}
 26:         ListNode(int val) { this.val = val; }
 27:         ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 28:     }
 29:     
 30:     static class TreeNode {
 31:         int val;
 32:         TreeNode left;
 33:         TreeNode right;
 34:         TreeNode() {}
 35:         TreeNode(int val) { this.val = val; }
 36:         TreeNode(int val, TreeNode left, TreeNode right) {
 37:             this.val = val;
 38:             this.left = left;
 39:             this.right = right;
 40:         }
 41:     }
 42:     
 43:     // Embedded signature information for type conversion (base64 encoded)
 44:     private static final String SIGNATURE_B64 = "eyJwYXJhbWV0ZXJzIjogW3sibmFtZSI6ICJzIiwgInR5cGUiOiAic3RyaW5nIn0sIHsibmFtZSI6ICJ3b3JkRGljdCIsICJ0eXBlIjogInN0cmluZ1tdIn1dLCAicmV0dXJuVHlwZSI6ICJzdHJpbmdbXSJ9";
 45: 
 46:     // Injected main method for wrapper functionality
 47:     public static void main(String[] args) {
 48:         if (args.length < 2) {
 49:             System.out.println("{\"result\": \"Missing arguments: expected method name and input data\", \"execution_time\": 0}");
 50:             return;
 51:         }
 52:         
 53:         String methodName = args[0];
 54:         String inputJson = args[1];
 55:         long startTime = System.nanoTime();
 56:         
 57:         try {
 58:             Solution sol = new Solution();
 59:             Object result = null;
 60:             
 61:             // Special handling for first-bad-version problem
 62:             if ("firstBadVersion".equals(methodName)) {
 63:                 int n = extractIntValue(inputJson, "n");
 64:                 int bad = extractIntValue(inputJson, "bad");
 65:                 
 66:                 VersionControl.setBadVersion(bad);
 67:                 
 68:                 java.lang.reflect.Method method = Solution.class.getMethod("firstBadVersion", int.class);
 69:                 result = method.invoke(sol, n);
 70:             } else {
 71:                 // Generic method calling using reflection with signature-based parameter conversion
 72:                 java.lang.reflect.Method targetMethod = null;
 73:                 java.lang.reflect.Method[] methods = Solution.class.getMethods();
 74:                 for (java.lang.reflect.Method method : methods) {
 75:                     if (method.getName().equals(methodName)) {
 76:                         targetMethod = method;
 77:                         break;
 78:                     }
 79:                 }
 80:                 
 81:                 if (targetMethod == null) {
 82:                     throw new RuntimeException("Method " + methodName + " not found in Solution class");
 83:                 }
 84:                 
 85:                 Object[] params = extractParametersWithSignature(inputJson, methodName);
 86:                 result = targetMethod.invoke(sol, params);
 87:             }
 88:             
 89:             long endTime = System.nanoTime();
 90:             double executionTime = (endTime - startTime) / 1_000_000.0;
 91:             
 92:             // Format output
 93:             if (result instanceof int[]) {
 94:                 int[] arr = (int[]) result;
 95:                 StringBuilder sb = new StringBuilder("[");
 96:                 for (int i = 0; i < arr.length; i++) {
 97:                     if (i > 0) sb.append(", ");
 98:                     sb.append(arr[i]);
 99:                 }
100:                 sb.append("]");
101:                 System.out.println("{\"result\": " + sb.toString() + ", \"execution_time\": " + executionTime + "}");
102:             } else if (result instanceof Integer) {
103:                 System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
104:             } else if (result instanceof Boolean) {
105:                 System.out.println("{\"result\": " + result + ", \"execution_time\": " + executionTime + "}");
106:             } else if (result instanceof String) {
107:                 System.out.println("{\"result\": \"" + result.toString().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
108:             } else {
109:                 System.out.println("{\"result\": \"" + String.valueOf(result).replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
110:             }
111:             
112:         } catch (Exception e) {
113:             long endTime = System.nanoTime();
114:             double executionTime = (endTime - startTime) / 1_000_000.0;
115:             System.out.println("{\"result\": \"" + e.getMessage().replace("\"", "\\\"") + "\", \"execution_time\": " + executionTime + "}");
116:         }
117:     }
118:     
119:     // Helper methods
120:     private static int extractIntValue(String json, String key) {
121:         String pattern = "\"" + key + "\"\\s*:\\s*(-?\\d+)";
122:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
123:         java.util.regex.Matcher m = p.matcher(json);
124:         if (m.find()) {
125:             return Integer.parseInt(m.group(1));
126:         }
127:         throw new RuntimeException("Could not find key: " + key);
128:     }
129:     
130:     private static Object[] extractParametersWithSignature(String json, String methodName) {
131:         java.util.List<Object> params = new java.util.ArrayList<>();
132:         
133:         try {
134:             // Parse signature information - decode base64 first
135:             if (!SIGNATURE_B64.isEmpty()) {
136:                 System.err.println("🔧 [SIGNATURE] Using signature-based parameter conversion for " + methodName);
137:                 
138:                 // Decode base64 signature
139:                 String signatureJson = new String(java.util.Base64.getDecoder().decode(SIGNATURE_B64));
140:                 System.err.println("🔧 [SIGNATURE] Decoded signature: " + signatureJson);
141:                 
142:                 // Simple JSON parsing for signature information  
143:                 // Extract params array from signature JSON
144:                 String paramsSection = extractJsonSection(signatureJson, "params");
145:                 if (paramsSection != null) {
146:                     String[] paramDefs = parseParamDefinitions(paramsSection);
147:                     
148:                     for (String paramDef : paramDefs) {
149:                         String paramName = extractJsonValue(paramDef, "name");
150:                         String paramType = extractJsonValue(paramDef, "type");
151:                         
152:                         if (paramName != null && paramType != null) {
153:                             System.err.println("🔧 [SIGNATURE] Processing param: " + paramName + " (" + paramType + ")");
154:                             Object value = convertParameterByType(json, paramName, paramType);
155:                             params.add(value);
156:                         }
157:                     }
158:                     
159:                     return params.toArray();
160:                 }
161:             }
162:             
163:             // Fallback to legacy hardcoded patterns if no signature
164:             System.err.println("⚠️  [SIGNATURE] No signature available, using legacy parameter extraction");
165:             return extractParametersInJsonOrder(json);
166:             
167:         } catch (Exception e) {
168:             System.err.println("❌ [SIGNATURE] Error in signature-based conversion: " + e.getMessage());
169:             // Fallback to legacy method
170:             return extractParametersInJsonOrder(json);
171:         }
172:     }
173:     
174:     private static String extractJsonSection(String json, String key) {
175:         try {
176:             String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
177:             java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
178:             java.util.regex.Matcher m = p.matcher(json);
179:             if (m.find()) {
180:                 return m.group(1);
181:             }
182:         } catch (Exception e) {
183:             System.err.println("Error extracting JSON section: " + e.getMessage());
184:         }
185:         return null;
186:     }
187:     
188:     private static String[] parseParamDefinitions(String paramsSection) {
189:         // Simple parsing for parameter definitions
190:         java.util.List<String> paramDefs = new java.util.ArrayList<>();
191:         int braceLevel = 0;
192:         StringBuilder current = new StringBuilder();
193:         
194:         for (int i = 0; i < paramsSection.length(); i++) {
195:             char c = paramsSection.charAt(i);
196:             if (c == '{') {
197:                 braceLevel++;
198:                 current.append(c);
199:             } else if (c == '}') {
200:                 braceLevel--;
201:                 current.append(c);
202:                 if (braceLevel == 0) {
203:                     paramDefs.add(current.toString());
204:                     current = new StringBuilder();
205:                 }
206:             } else if (c == ',' && braceLevel == 0) {
207:                 // Skip comma at top level
208:             } else {
209:                 current.append(c);
210:             }
211:         }
212:         
213:         return paramDefs.toArray(new String[0]);
214:     }
215:     
216:     private static String extractJsonValue(String jsonObject, String key) {
217:         try {
218:             String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
219:             java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
220:             java.util.regex.Matcher m = p.matcher(jsonObject);
221:             if (m.find()) {
222:                 return m.group(1);
223:             }
224:         } catch (Exception e) {
225:             System.err.println("Error extracting JSON value: " + e.getMessage());
226:         }
227:         return null;
228:     }
229:     
230:     private static Object convertParameterByType(String json, String paramName, String paramType) {
231:         try {
232:             switch (paramType) {
233:                 case "int":
234:                     return extractIntValue(json, paramName);
235:                 case "string":
236:                     return extractStringValue(json, paramName);
237:                 case "boolean":
238:                     return extractBooleanValue(json, paramName);
239:                 case "int[]":
240:                     return extractIntArray(json, paramName);
241:                 case "int[][]":
242:                     return extract2DIntArray(json, paramName);
243:                 case "ListNode":
244:                     int[] listArray = extractIntArray(json, paramName);
245:                     return arrayToListNode(listArray);
246:                 case "TreeNode":
247:                     Integer[] treeArray = extractIntArrayWithNulls(json, paramName);
248:                     return arrayToTreeNode(treeArray);
249:                 case "string[]":
250:                     return extractStringArray(json, paramName);
251:                 case "list<string>":
252:                     return extractStringArray(json, paramName);
253:                 case "ListNode[]":
254:                     // Handle array of ListNodes (for merge-k-sorted-lists)
255:                     String pattern = "\"" + paramName + "\"\\s*:\\s*\\[([^\\]]+)\\]";
256:                     java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
257:                     java.util.regex.Matcher m = p.matcher(json);
258:                     if (m.find()) {
259:                         String arrayContent = m.group(1);
260:                         // Split by ], [ to get individual list arrays
261:                         String[] listStrings = arrayContent.split("\\],\\s*\\[");
262:                         ListNode[] result = new ListNode[listStrings.length];
263:                         for (int i = 0; i < listStrings.length; i++) {
264:                             String listStr = listStrings[i].replaceAll("^\\[|\\]$", "");
265:                             int[] listArray = parseIntArray(listStr);
266:                             result[i] = arrayToListNode(listArray);
267:                         }
268:                         return result;
269:                     }
270:                     return new ListNode[0];
271:                 default:
272:                     System.err.println("⚠️  [SIGNATURE] Unknown parameter type: " + paramType + ", treating as string");
273:                     return extractStringValue(json, paramName);
274:             }
275:         } catch (Exception e) {
276:             System.err.println("❌ [SIGNATURE] Error converting parameter " + paramName + " (" + paramType + "): " + e.getMessage());
277:             throw new RuntimeException("Parameter conversion failed for " + paramName + ": " + e.getMessage());
278:         }
279:     }
280:     
281:     private static String extractStringValue(String json, String key) {
282:         String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
283:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
284:         java.util.regex.Matcher m = p.matcher(json);
285:         if (m.find()) {
286:             return m.group(1);
287:         }
288:         throw new RuntimeException("Could not find string key: " + key);
289:     }
290:     
291:     private static boolean extractBooleanValue(String json, String key) {
292:         String pattern = "\"" + key + "\"\\s*:\\s*(true|false)";
293:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
294:         java.util.regex.Matcher m = p.matcher(json);
295:         if (m.find()) {
296:             return Boolean.parseBoolean(m.group(1));
297:         }
298:         throw new RuntimeException("Could not find boolean key: " + key);
299:     }
300:     
301:     private static String[] extractStringArray(String json, String key) {
302:         String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
303:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
304:         java.util.regex.Matcher m = p.matcher(json);
305:         if (m.find()) {
306:             String arrayContent = m.group(1);
307:             String[] elements = arrayContent.split(",");
308:             String[] result = new String[elements.length];
309:             for (int i = 0; i < elements.length; i++) {
310:                 String element = elements[i].trim();
311:                 if (element.startsWith("\"") && element.endsWith("\"")) {
312:                     element = element.substring(1, element.length() - 1);
313:                 }
314:                 result[i] = element;
315:             }
316:             return result;
317:         }
318:         return new String[0];
319:     }
320:                     element = element.substring(1, element.length() - 1);
321:                 }
322:                 result[i] = element;
323:             }
324:             return result;
325:         }
326:         return new String[0];
327:     }
328:     
329:     // Legacy parameter extraction methods (kept as fallback)
330:     private static Object[] extractParametersInJsonOrder(String json) {
331:         java.util.List<Object> params = new java.util.ArrayList<>();
332:         
333:         try {
334:             // Enhanced JSON parsing for complex data structures
335:             if (json.contains("\"nums\"") && json.contains("\"target\"")) {
336:                 // twoSum pattern: {"nums": [2, 7, 11, 15], "target": 9}
337:                 int[] nums = extractIntArray(json, "nums");
338:                 int target = extractIntValue(json, "target");
339:                 params.add(nums);
340:                 params.add(target);
341:             } else if (json.contains("\"l1\"") && json.contains("\"l2\"")) {
342:                 // addTwoNumbers pattern: {"l1": [2, 4, 3], "l2": [5, 6, 4]}
343:                 ListNode l1 = arrayToListNode(extractIntArray(json, "l1"));
344:                 ListNode l2 = arrayToListNode(extractIntArray(json, "l2"));
345:                 params.add(l1);
346:                 params.add(l2);
347:             } else if (json.contains("\"list1\"") && json.contains("\"list2\"")) {
348:                 // mergeTwoLists pattern: {"list1": [1, 2, 4], "list2": [1, 3, 4]}
349:                 ListNode list1 = arrayToListNode(extractIntArray(json, "list1"));
350:                 ListNode list2 = arrayToListNode(extractIntArray(json, "list2"));
351:                 params.add(list1);
352:                 params.add(list2);
353:             } else if (json.contains("\"root\"")) {
354:                 // Tree problems pattern: {"root": [4, 2, 7, 1, 3, 6, 9]}
355:                 TreeNode root = arrayToTreeNode(extractIntArrayWithNulls(json, "root"));
356:                 params.add(root);
357:             } else if (json.contains("\"p\"") && json.contains("\"q\"")) {
358:                 // Same tree pattern: {"p": [1, 2, 3], "q": [1, 2, 3]}
359:                 TreeNode p = arrayToTreeNode(extractIntArrayWithNulls(json, "p"));
360:                 TreeNode q = arrayToTreeNode(extractIntArrayWithNulls(json, "q"));
361:                 params.add(p);
362:                 params.add(q);
363:             } else if (json.contains("\"a\"") && json.contains("\"b\"")) {
364:                 // String problems like add-binary: {"a": "11", "b": "1"}
365:                 String a = extractStringValue(json, "a");
366:                 String b = extractStringValue(json, "b");
367:                 params.add(a);
368:                 params.add(b);
369:             } else if (json.contains("\"intervals\"")) {
370:                 // Intervals pattern: {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}
371:                 int[][] intervals = extract2DIntArray(json, "intervals");
372:                 params.add(intervals);
373:             } else {
374:                 // Generic fallback - extract all values in order from JSON
375:                 java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("\"([^\"]+)\"\\s*:\\s*([^,}]+)");
376:                 java.util.regex.Matcher matcher = pattern.matcher(json);
377:                 while (matcher.find()) {
378:                     String value = matcher.group(2).trim();
379:                     if (value.startsWith("\"") && value.endsWith("\"")) {
380:                         // String value
381:                         params.add(value.substring(1, value.length() - 1));
382:                     } else if (value.startsWith("[") && value.endsWith("]")) {
383:                         // Array value - try to parse as int array
384:                         try {
385:                             String arrayContent = value.substring(1, value.length() - 1);
386:                             if (arrayContent.trim().isEmpty()) {
387:                                 params.add(new int[0]);
388:                             } else {
389:                                 String[] elements = arrayContent.split(",");
390:                                 int[] intArray = new int[elements.length];
391:                                 for (int i = 0; i < elements.length; i++) {
392:                                     intArray[i] = Integer.parseInt(elements[i].trim());
393:                                 }
394:                                 params.add(intArray);
395:                             }
396:                         } catch (NumberFormatException e) {
397:                             // If not integers, treat as string array
398:                             params.add(value);
399:                         }
400:                     } else {
401:                         // Try to parse as integer, fall back to string
402:                         try {
403:                             params.add(Integer.parseInt(value));
404:                         } catch (NumberFormatException e) {
405:                             params.add(value);
406:                         }
407:                     }
408:                 }
409:             }
410:         } catch (Exception e) {
411:             // If parsing fails, return empty array to trigger error
412:             System.err.println("Error parsing parameters: " + e.getMessage());
413:         }
414:         
415:         return params.toArray();
416:     }
417:     
418:     private static int[] extractIntArray(String json, String key) {
419:         String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
420:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
421:         java.util.regex.Matcher m = p.matcher(json);
422:         if (m.find()) {
423:             String arrayContent = m.group(1);
424:             String[] elements = arrayContent.split(",");
425:             int[] result = new int[elements.length];
426:             for (int i = 0; i < elements.length; i++) {
427:                 result[i] = Integer.parseInt(elements[i].trim());
428:             }
429:             return result;
430:         }
431:         return new int[0];
432:     }
433:     
434:     private static Integer[] extractIntArrayWithNulls(String json, String key) {
435:         String pattern = "\"" + key + "\"\\s*:\\s*\\[([^\\]]+)\\]";
436:         java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
437:         java.util.regex.Matcher m = p.matcher(json);
438:         if (m.find()) {
439:             String arrayContent = m.group(1);
440:             String[] elements = arrayContent.split(",");
441:             Integer[] result = new Integer[elements.length];
442:             for (int i = 0; i < elements.length; i++) {
443:                 String element = elements[i].trim();
444:                 if (element.equals("null")) {
445:                     result[i] = null;
446:                 } else {
447:                     result[i] = Integer.parseInt(element);
448:                 }
449:             }
450:             return result;
451:         }
452:         return new Integer[0];
453:     }
454:     
455:     private static int[][] extract2DIntArray(String json, String key) {
456:         // Implementation for 2D array extraction
457:         return new int[0][0]; // Placeholder
458:     }
459:     
460:     private static int[] parseIntArray(String arrayStr) {
461:         if (arrayStr.trim().isEmpty()) return new int[0];
462:         String[] elements = arrayStr.split(",");
463:         int[] result = new int[elements.length];
464:         for (int i = 0; i < elements.length; i++) {
465:             result[i] = Integer.parseInt(elements[i].trim());
466:         }
467:         return result;
468:     }
469:     
470:     private static ListNode arrayToListNode(int[] arr) {
471:         if (arr.length == 0) return null;
472:         ListNode head = new ListNode(arr[0]);
473:         ListNode current = head;
474:         for (int i = 1; i < arr.length; i++) {
475:             current.next = new ListNode(arr[i]);
476:             current = current.next;
477:         }
478:         return head;
479:     }
480:     
481:     private static TreeNode arrayToTreeNode(Integer[] arr) {
482:         if (arr.length == 0 || arr[0] == null) return null;
483:         TreeNode root = new TreeNode(arr[0]);
484:         java.util.Queue<TreeNode> queue = new java.util.LinkedList<>();
485:         queue.offer(root);
486:         int i = 1;
487:         while (!queue.isEmpty() && i < arr.length) {
488:             TreeNode node = queue.poll();
489:             if (i < arr.length && arr[i] != null) {
490:                 node.left = new TreeNode(arr[i]);
491:                 queue.offer(node.left);
492:             }
493:             i++;
494:             if (i < arr.length && arr[i] != null) {
495:                 node.right = new TreeNode(arr[i]);
496:                 queue.offer(node.right);
497:             }
498:             i++;
499:         }
500:         return root;
501:     }
502: }
503: 
504: 
