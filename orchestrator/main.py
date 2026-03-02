"""
Orchestrator 入口点

Usage:
    python -m orchestrator.main "帮我开发一个新的热点监控工作流"
"""

import sys
import uuid
from datetime import datetime

from .graph import run_workflow, build_orchestrator_graph
from .state import create_initial_state, TaskStatus


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python -m orchestrator.main <task_description>")
        print("Example: python -m orchestrator.main '帮我开发一个新的热点监控工作流'")
        sys.exit(1)

    task_description = " ".join(sys.argv[1:])
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    task_type = "feature"  # 默认任务类型

    print(f"\n{'='*60}")
    print(f"PineVC-PR Orchestrator")
    print(f"{'='*60}")
    print(f"Task ID: {task_id}")
    print(f"Task Type: {task_type}")
    print(f"Description: {task_description}")
    print(f"{'='*60}\n")

    try:
        # 运行工作流
        final_state = run_workflow(task_id, task_description, task_type)

        # 输出结果
        print(f"\n{'='*60}")
        print("Workflow Completed")
        print(f"{'='*60}")
        print(f"Status: {final_state.get('current_status')}")
        print(f"Final Agent: {final_state.get('current_agent')}")

        if final_state.get("errors"):
            print("\nErrors:")
            for error in final_state["errors"]:
                print(f"  - {error}")

        if final_state.get("final_output"):
            print(f"\nOutput: {final_state['final_output']}")

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def demo():
    """
    演示模式

    展示工作流图结构和基本运行
    """
    print("\n" + "="*60)
    print("PineVC-PR Orchestrator Demo")
    print("="*60)

    # 构建工作流图
    print("\n[*] Building workflow graph...")
    graph = build_orchestrator_graph()

    # 显示图结构
    print("\n[Graph] Workflow Graph Structure:")
    print("-" * 40)

    # 创建一个测试状态
    test_state = create_initial_state(
        task_id="demo-001",
        task_description="演示任务",
        task_type="feature"
    )

    print(f"\n[OK] Initial State Created:")
    print(f"   Task ID: {test_state['task_id']}")
    print(f"   Status: {test_state['current_status'].value}")

    # 运行工作流
    print("\n[Run] Running workflow...")
    final_state = graph.invoke(test_state)

    print(f"\n[OK] Workflow Completed:")
    print(f"   Status: {final_state.get('current_status')}")
    print(f"   Current Agent: {final_state.get('current_agent')}")
    print(f"   Step: {final_state.get('current_step')}")

    print("\n" + "="*60)
    print("Demo completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # 如果没有参数，运行演示模式
    if len(sys.argv) < 2:
        demo()
    else:
        main()
