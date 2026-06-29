"""Send a mock LLM trace to the self-hosted Langfuse v2 instance.

Fulfills rubric B2 checkpoint requirements.
"""
from __future__ import annotations

import os
from langfuse import Langfuse


def main():
    # Set environment variables for self-hosted Langfuse
    os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-day23-lab-public-key"
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-day23-lab-secret-key"
    os.environ["LANGFUSE_HOST"] = "http://localhost:3300"

    print("Initializing Langfuse client...")
    langfuse = Langfuse()

    print("Creating trace and generation...")
    trace = langfuse.trace(
        name="day23-lab-llm-trace",
        user_id="heval111",
        metadata={"env": "lab"}
    )

    generation = trace.generation(
        name="ask-gpt-4o",
        model="gpt-4o-mini",
        input={"messages": [{"role": "user", "content": "Một câu về observability."}]},
        output={"choices": [{"message": {"role": "assistant", "content": "Observability giúp bạn hiểu rõ trạng thái hoạt động bên trong của hệ thống dựa trên dữ liệu đầu ra."}}]},
        usage={
            "input_tokens": 15,
            "output_tokens": 30,
            "total_tokens": 45,
            "unit": "TOKENS"
        },
        metadata={"temperature": 0.7}
    )

    print("Flushing traces to Langfuse...")
    langfuse.flush()
    print("Trace successfully sent to Langfuse!")


if __name__ == "__main__":
    main()
