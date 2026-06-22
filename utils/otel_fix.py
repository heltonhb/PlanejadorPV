"""
OpenTelemetry Blocker

Bloqueia imports de opentelemetry antes do ChromaDB carregar.
O opentelemetry-proto gera _pb2.py que depende de protobuf-upb, ausente
no Python 3.14. Injetamos módulos fantasma em sys.modules para evitar
que a cadeia de imports rompa.

Uso: import utils.otel_fix  # (deve ser o primeiro import após stdlib)
"""
import sys
import types

# ---------------------------------------------------------------------------
# Módulos fantasma para opentelemetry
# ---------------------------------------------------------------------------

_OT_NAMES = [
    "opentelemetry",
    "opentelemetry.api",
    "opentelemetry.api.logs",
    "opentelemetry.api.metrics",
    "opentelemetry.api.trace",
    "opentelemetry.context",
    "opentelemetry.context.context",
    "opentelemetry.exporter",
    "opentelemetry.exporter.otlp",
    "opentelemetry.exporter.otlp.proto",
    "opentelemetry.exporter.otlp.proto.grpc",
    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
    "opentelemetry.metrics",
    "opentelemetry.metrics._internal",
    "opentelemetry.metrics._internal.export",
    "opentelemetry.metrics.export",
    "opentelemetry.proto",
    "opentelemetry.proto.common",
    "opentelemetry.proto.common.v1",
    "opentelemetry.proto.common.v1.common_pb2",
    "opentelemetry.proto.resource",
    "opentelemetry.proto.resource.v1",
    "opentelemetry.proto.resource.v1.resource_pb2",
    "opentelemetry.proto.trace",
    "opentelemetry.proto.trace.v1",
    "opentelemetry.proto.trace.v1.trace_pb2",
    "opentelemetry.sdk",
    "opentelemetry.sdk.environment_variables",
    "opentelemetry.sdk.resources",
    "opentelemetry.sdk.trace",
    "opentelemetry.sdk.trace.export",
    "opentelemetry.sdk.trace.export.in_memory",
    "opentelemetry.trace",
    "opentelemetry.trace.propagation",
    "opentelemetry.trace.span",
    "opentelemetry.util",
    "opentelemetry.util._once",
]


class _FakeModule(types.ModuleType):
    """Módulo-fantasma que ignora qualquer atributo/import."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _FakeModule(f"{self.__name__}.{name}")

    def __call__(self, *a, **kw):
        return self


def _instalar():
    """Instala os módulos fantasma no sys.modules (idempotente)."""
    for _name in _OT_NAMES:
        if _name not in sys.modules:
            sys.modules[_name] = _FakeModule(_name)

    # classes frequentemente referenciadas
    sys.modules["opentelemetry.trace"].get_tracer_provider = lambda: None
    sys.modules["opentelemetry.trace"].get_tracer = lambda *a, **kw: None
    sys.modules["opentelemetry.trace"].set_tracer_provider = lambda *a, **kw: None
    sys.modules["opentelemetry.trace"].NonRecordingSpan = type(
        "NonRecordingSpan", (), {}
    )
    sys.modules["opentelemetry.trace"].Span = type("Span", (), {})
    sys.modules["opentelemetry.trace"].Link = type("Link", (), {})
    sys.modules["opentelemetry.trace"].SpanContext = type("SpanContext", (), {})
    sys.modules["opentelemetry.trace"].SpanKind = type(
        "SpanKind",
        (),
        {"INTERNAL": 0, "SERVER": 1, "CLIENT": 2, "PRODUCER": 3, "CONSUMER": 4},
    )
    sys.modules["opentelemetry.trace"].StatusCode = type(
        "StatusCode", (), {"UNSET": 0, "OK": 1, "ERROR": 2}
    )
    sys.modules["opentelemetry.sdk.trace.export"].SpanExporter = type(
        "SpanExporter", (), {}
    )
    sys.modules["opentelemetry.sdk.resources"].Resource = type("Resource", (), {})
    sys.modules["opentelemetry.api"].set_tracer_provider = lambda *a, **kw: None
    sys.modules["opentelemetry.api"].get_tracer_provider = lambda: None


_instalar()
