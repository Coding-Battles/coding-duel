#!/usr/bin/env ts-node
/**
 * Simple alignment validator
 * Checks that Zod schemas and Python models are reasonably aligned
 */

import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';

// Import our Zod schemas
import {
  CustomUserSchema,
  PlayerInfoSchema,
  OpponentDataSchema,
  TestResultsDataSchema,
  UserStatsSchema,
  GameStateSchema,
  QuestionDataSchema,
  CodeTestResultSchema,
} from '../../shared/schemas';

interface SchemaInfo {
  name: string;
  schema: z.ZodSchema;
  pythonFile: string;
}

const schemasToValidate: SchemaInfo[] = [
  {
    name: 'CustomUser',
    schema: CustomUserSchema,
    pythonFile: '../backend/models/core/user.py',
  },
  {
    name: 'PlayerInfo',
    schema: PlayerInfoSchema,
    pythonFile: '../backend/models/core/user.py',
  },
  {
    name: 'OpponentData',
    schema: OpponentDataSchema,
    pythonFile: '../backend/models/core/user.py',
  },
  {
    name: 'TestResultsData',
    schema: TestResultsDataSchema,
    pythonFile: '../backend/models/core/user.py',
  },
  {
    name: 'UserStats',
    schema: UserStatsSchema,
    pythonFile: '../backend/models/core/user.py',
  },
  {
    name: 'GameState',
    schema: GameStateSchema,
    pythonFile: '../backend/models/core/game.py',
  },
  {
    name: 'QuestionData',
    schema: QuestionDataSchema,
    pythonFile: '../backend/models/core/question.py',
  },
  {
    name: 'CodeTestResult',
    schema: CodeTestResultSchema,
    pythonFile: '../backend/models/core/question.py',
  },
];

function extractZodFields(schema: z.ZodSchema): Set<string> {
  const fields = new Set<string>();
  
  try {
    // Try to get the shape from the schema
    const shape = (schema as any)._def?.shape;
    if (shape) {
      Object.keys(shape).forEach(key => fields.add(key));
    }
    
    // For extended schemas, try to get typeName
    if ((schema as any)._def?.typeName === 'ZodObject') {
      const def = (schema as any)._def;
      if (def.shape) {
        Object.keys(def.shape()).forEach(key => fields.add(key));
      }
    }
  } catch (error) {
    console.warn(`Could not extract fields from schema: ${error}`);
  }
  
  return fields;
}

function extractPythonFields(pythonFilePath: string, className: string): Set<string> {
  const fields = new Set<string>();
  
  try {
    const fullPath = path.join(process.cwd(), pythonFilePath);
    if (!fs.existsSync(fullPath)) {
      console.warn(`Python file not found: ${fullPath}`);
      return fields;
    }
    
    const content = fs.readFileSync(fullPath, 'utf-8');
    const lines = content.split('\n');
    
    let inClass = false;
    let classIndent = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Check if we're entering the target class
      if (line.trim().startsWith(`class ${className}(`)) {
        inClass = true;
        classIndent = line.length - line.trimLeft().length;
        continue;
      }
      
      // Check if we've left the class
      if (inClass && line.trim() && (line.length - line.trimLeft().length) <= classIndent && !line.trim().startsWith('#')) {
        if (!line.trim().startsWith('class') || i === 0) {
          inClass = false;
          continue;
        }
      }
      
      // Extract field definitions
      if (inClass && line.includes(':') && !line.trim().startsWith('#')) {
        const trimmed = line.trim();
        
        // Skip method definitions, class definitions, etc.
        if (trimmed.startsWith('def ') || trimmed.startsWith('class ') || 
            trimmed.startsWith('@') || trimmed === 'class Config:') {
          continue;
        }
        
        // Extract field name
        const match = trimmed.match(/^(\w+)\s*:/);
        if (match) {
          fields.add(match[1]);
        }
      }
    }
  } catch (error) {
    console.warn(`Could not read Python file ${pythonFilePath}: ${error}`);
  }
  
  return fields;
}

function validateSchema(schemaInfo: SchemaInfo): boolean {
  console.log(`\n🔍 Validating ${schemaInfo.name}...`);
  
  const zodFields = extractZodFields(schemaInfo.schema);
  const pythonFields = extractPythonFields(schemaInfo.pythonFile, schemaInfo.name);
  
  console.log(`   TypeScript fields: ${Array.from(zodFields).sort().join(', ') || '(none detected)'}`);
  console.log(`   Python fields:     ${Array.from(pythonFields).sort().join(', ') || '(none detected)'}`);
  
  if (zodFields.size === 0 && pythonFields.size === 0) {
    console.log(`   ⚠️  Could not extract fields from either schema`);
    return false;
  }
  
  if (zodFields.size === 0) {
    console.log(`   ⚠️  Could not extract TypeScript fields`);
    return false;
  }
  
  if (pythonFields.size === 0) {
    console.log(`   ⚠️  Could not extract Python fields`);
    return false;
  }
  
  // Find missing fields
  const missingInPython = Array.from(zodFields).filter(f => !pythonFields.has(f));
  const missingInTypeScript = Array.from(pythonFields).filter(f => !zodFields.has(f));
  
  let isAligned = true;
  
  if (missingInPython.length > 0) {
    console.log(`   ❌ Missing in Python: ${missingInPython.join(', ')}`);
    isAligned = false;
  }
  
  if (missingInTypeScript.length > 0) {
    console.log(`   ❌ Missing in TypeScript: ${missingInTypeScript.join(', ')}`);
    isAligned = false;
  }
  
  if (isAligned) {
    console.log(`   ✅ Fields are aligned!`);
  }
  
  return isAligned;
}

function main() {
  console.log('🔄 Validating Zod schema and Python model alignment...\n');
  
  let allAligned = true;
  let validatedCount = 0;
  
  for (const schemaInfo of schemasToValidate) {
    try {
      const isAligned = validateSchema(schemaInfo);
      if (!isAligned) {
        allAligned = false;
      }
      validatedCount++;
    } catch (error) {
      console.error(`❌ Error validating ${schemaInfo.name}: ${error}`);
      allAligned = false;
    }
  }
  
  console.log(`\n📊 Validation Summary:`);
  console.log(`   📝 Schemas checked: ${validatedCount}`);
  
  if (allAligned) {
    console.log(`   ✅ All schemas are aligned!`);
    console.log(`\n🎉 Type alignment validation passed!`);
    process.exit(0);
  } else {
    console.log(`   ❌ Some schemas are misaligned`);
    console.log(`\n⚠️  Please update the misaligned schemas manually.`);
    console.log(`\n💡 This is expected for complex types - manual alignment is often better than generation.`);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

export { validateSchema, extractZodFields, extractPythonFields };