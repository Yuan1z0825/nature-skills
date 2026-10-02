# Methods / algorithm / system paper

Emphasize the problem-to-solution chain.

- Reconstruct inputs, outputs, modules, training requirements, external tools, feedback loops, and inference-time cost.
- Distinguish the core insight from the implementation bundle.
- Map each ablation to one component and check whether the comparison changes only that component.
- Check baseline fairness, backbone parity, data leakage, compute budget, oracle inputs, and end-to-end status.
- Treat a component's intended role as an author claim until an isolation experiment supports it.
- In Section 16, propose ideas that change a specific assumption, mechanism, or bottleneck and define a budget-fair validation.
- When a resource or dataset is a substantial secondary contribution, also load the `resource` lens instead of treating data volume as an unexplained implementation detail.
