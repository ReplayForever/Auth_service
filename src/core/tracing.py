from pathlib import Path
import os

from dotenv import load_dotenv      
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider        
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")


def configure_tracer() -> None:
    jaeger_agent_host = os.getenv('AGENT_HOST', 'jaeger')
    jaeger_agent_port = int(os.getenv('AGENT_PORT', '6831'))
    
    tracer_provider = TracerProvider(resource=Resource.create({'service.name': 'Auth_service'}))
    trace.set_tracer_provider(tracer_provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaeger_agent_host,
                agent_port=jaeger_agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
