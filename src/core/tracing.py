from pathlib import Path

from dotenv import load_dotenv      
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")


def configure_tracer() -> None:
    tracer_provider = TracerProvider(resource=Resource.create({'service.name': 'Auth_service'}))
    trace.set_tracer_provider(tracer_provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.tracing.jaeger_agent_host,
                agent_port=settings.tracing.jaeger_agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
