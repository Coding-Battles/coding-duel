"""
Universal signature handler for dynamic code execution.
Maps question signature metadata to language-specific types and parameter extraction.
"""

import json
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SignatureHandler:
    """Handles signature-based parameter extraction and type mapping for all languages."""
    
    # Type mapping from signature types to language-specific types
    TYPE_MAPPINGS = {
        "java": {
            "string": "String",
            "int": "int", 
            "boolean": "boolean",
            "int[]": "int[]",
            "string[]": "List<String>",
            "char[]": "char[]",
        },
        "cpp": {
            "string": "string",
            "int": "int",
            "boolean": "bool", 
            "int[]": "vector<int>",
            "string[]": "vector<string>",
            "char[]": "string",  # C++ treats char[] as string
        },
        "python": {
            "string": "str",
            "int": "int",
            "boolean": "bool",
            "int[]": "List[int]", 
            "string[]": "List[str]",
            "char[]": "str",
        }
    }
    
    @staticmethod
    def map_signature_type(signature_type: str, language: str) -> str:
        """Map signature type to language-specific type."""
        mappings = SignatureHandler.TYPE_MAPPINGS.get(language, {})
        return mappings.get(signature_type, signature_type)
    
    @staticmethod
    def extract_parameter_from_json(
        param_name: str, 
        param_type: str, 
        test_input: Dict[str, Any], 
        language: str
    ) -> Any:
        """Extract and convert parameter from JSON test input to language-appropriate format."""
        
        if param_name not in test_input:
            raise ValueError(f"Parameter '{param_name}' not found in test input: {test_input}")
        
        value = test_input[param_name]
        
        # Handle different parameter types
        if param_type == "string":
            return str(value) if value is not None else ""
            
        elif param_type == "int":
            return int(value) if value is not None else 0
            
        elif param_type == "boolean":
            return bool(value) if value is not None else False
            
        elif param_type == "int[]":
            if not isinstance(value, list):
                raise ValueError(f"Expected list for {param_name}, got {type(value)}")
            return [int(x) for x in value]
            
        elif param_type == "string[]":
            if not isinstance(value, list):
                raise ValueError(f"Expected list for {param_name}, got {type(value)}")
            return [str(x) for x in value]
            
        elif param_type == "char[]":
            # Convert string to char array based on language
            if language == "java":
                return f'"{value}".toCharArray()' if isinstance(value, str) else value
            else:
                return str(value) if value is not None else ""
        
        else:
            logger.warning(f"Unknown parameter type: {param_type}, returning raw value")
            return value
    
    @staticmethod
    def generate_java_parameter_extraction(
        signature: Dict[str, Any], 
        test_input_var: str = "inputJson"
    ) -> Tuple[List[str], List[str]]:
        """
        Generate Java code for parameter extraction based on signature.
        
        Returns:
            (extraction_statements, parameter_names)
        """
        extraction_statements = []
        parameter_names = []
        
        params = signature.get("params", [])
        
        for i, param in enumerate(params):
            param_name = param["name"]
            param_type = param["type"]
            parameter_names.append(param_name)
            
            if param_type == "string":
                extraction_statements.append(
                    f'String {param_name} = extractStringValue({test_input_var}, "{param_name}");'
                )
                
            elif param_type == "int":
                extraction_statements.append(
                    f'int {param_name} = extractIntValue({test_input_var}, "{param_name}");'
                )
                
            elif param_type == "boolean":
                extraction_statements.append(
                    f'boolean {param_name} = extractBooleanValue({test_input_var}, "{param_name}");'
                )
                
            elif param_type == "int[]":
                extraction_statements.append(
                    f'int[] {param_name} = extractIntArray({test_input_var}, "{param_name}");'
                )
                
            elif param_type == "string[]":
                extraction_statements.append(
                    f'List<String> {param_name} = extractStringArray({test_input_var}, "{param_name}");'
                )
                
            elif param_type == "char[]":
                extraction_statements.append(
                    f'char[] {param_name} = extractStringValue({test_input_var}, "{param_name}").toCharArray();'
                )
            
            else:
                logger.warning(f"Unsupported Java parameter type: {param_type}")
                extraction_statements.append(
                    f'Object {param_name} = extractObjectValue({test_input_var}, "{param_name}");'
                )
        
        return extraction_statements, parameter_names
    
    @staticmethod
    def generate_cpp_parameter_extraction(
        signature: Dict[str, Any]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate C++ code for parameter extraction and declarations.
        
        Returns:
            (includes, declarations, parameter_names)
        """
        includes = set()
        declarations = []
        parameter_names = []
        
        params = signature.get("params", [])
        
        for param in params:
            param_name = param["name"]
            param_type = param["type"]
            parameter_names.append(param_name)
            
            if param_type == "string":
                includes.add("#include <string>")
                declarations.append(f'string {param_name} = input["{param_name}"];')
                
            elif param_type == "int":
                declarations.append(f'int {param_name} = input["{param_name}"];')
                
            elif param_type == "boolean":
                declarations.append(f'bool {param_name} = input["{param_name}"];')
                
            elif param_type == "int[]":
                includes.add("#include <vector>")
                declarations.append(f'''vector<int> {param_name};
        for (auto& val : input["{param_name}"]) {{
            {param_name}.push_back(val);
        }}''')
                
            elif param_type == "string[]":
                includes.add("#include <vector>")
                includes.add("#include <string>")
                declarations.append(f'''vector<string> {param_name};
        for (auto& val : input["{param_name}"]) {{
            {param_name}.push_back(val);
        }}''')
                
            elif param_type == "char[]":
                includes.add("#include <string>")
                declarations.append(f'string {param_name} = input["{param_name}"];')
            
            else:
                logger.warning(f"Unsupported C++ parameter type: {param_type}")
                declarations.append(f'auto {param_name} = input["{param_name}"];')
        
        return list(includes), declarations, parameter_names
    
    @staticmethod
    def get_java_return_type(signature: Dict[str, Any]) -> str:
        """Get Java return type from signature."""
        return_type = signature.get("return_type", "Object")
        return SignatureHandler.map_signature_type(return_type, "java")
    
    @staticmethod 
    def get_cpp_return_type(signature: Dict[str, Any]) -> str:
        """Get C++ return type from signature."""
        return_type = signature.get("return_type", "auto")
        return SignatureHandler.map_signature_type(return_type, "cpp")
    
    @staticmethod
    def validate_signature(signature: Dict[str, Any]) -> bool:
        """Validate that signature has required fields."""
        if not isinstance(signature, dict):
            return False
            
        if "params" not in signature:
            return False
            
        params = signature["params"]
        if not isinstance(params, list):
            return False
            
        for param in params:
            if not isinstance(param, dict):
                return False
            if "name" not in param or "type" not in param:
                return False
                
        return True