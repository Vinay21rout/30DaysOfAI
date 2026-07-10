import os
import sys
import importlib.util

# Dynamic import to handle the hyphenated script filename
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "agent_system", 
    os.path.join(os.path.dirname(__file__), "skills-powered-agentic-system.py")
)
agent_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_system)

SkillRegistry = agent_system.SkillRegistry
ToolExecutor = agent_system.ToolExecutor
SkillLoader = agent_system.SkillLoader
Agent = agent_system.Agent

def test_agentic_routing():
    # 1. Setup registry and loader
    registry = SkillRegistry()
    executor = ToolExecutor()
    loader = SkillLoader(registry)
    
    # 2. Register local skills
    print("📂 Discovering and registering local skills...")
    try:
        loader.register_skill("calculator")
        loader.register_skill("data-and-analytics")
    except Exception as e:
        print(f"⚠️ Failed to register skills: {e}")
        return
        
    # 3. Instantiate Agent
    agent = Agent(registry, executor, loader)
    
    # 4. Define test queries
    queries = [
        "analyze StudentsPerformance.csv using the data-and-analytics skill",
        "find correlations in the StudentsPerformance.csv scores using data-and-analytics",
        "group math score averages by lunch type using data-and-analytics"
    ]
    
    print("\n🧪 Running Agent Quality & Correctness Tests...\n")
    
    for query in queries:
        print(f"💬 Query: \"{query}\"")
        try:
            agent.handle_query(query)
        except Exception as e:
            print(f"❌ Execution crashed: {e}")
        print("-" * 60)

if __name__ == "__main__":
    test_agentic_routing()
