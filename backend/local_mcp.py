class McpServer:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description
        self.resources = {}
        self.tools = {}
    
    def register_resource(self, resource):
        self.resources[resource.name] = resource
    
    def register_tool(self, tool):
        self.tools[tool.name] = tool

class McpResource:
    def __init__(self):
        self.name = ""
        self.description = ""
    
    async def execute(self, params):
        return {}

class McpTool:
    def __init__(self):
        self.name = ""
        self.description = ""
    
    async def execute(self, params):
        return {}

class McpModel:
    def __init__(self, server, system_prompt):
        self.server = server
        self.system_prompt = system_prompt
    
    async def process(self, prompt, context=None):
        return {"response": "MCP running in fallback mode"}