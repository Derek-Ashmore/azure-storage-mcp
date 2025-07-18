# Initial swarm command to plan

> Results Tag: ```1-initial-plan```

npx claude-flow@alpha swarm "review the INITIAL.md in root and create a detailed technical implementation plan in /plans using TDD in Python with a pip install and the UV packaging manager. Just do the research, don’t start implementation yet" --claude

# Initial swarm command to implement

> Results Tag: ```1-initial-implement```

npx claude-flow@alpha swarm "implement the requirements in INITIAL.md in the root by using the plan you developed and documented in technical_implementation_plan in folder plans. You are logged into Azure and can use that login. Please make me aware of any additional resources you need." --claude