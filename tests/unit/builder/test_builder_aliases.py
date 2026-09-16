"""Builder methods accept the pure-Python plugins' keyword names (drop-in rename)."""

import pytest
from pynenc import PynencBuilder

from pynenc_rustvello.builder import _amqp_url_from_parts, _mongo_url_from_parts


def test_mongo3_accepts_pynenc_mongo_keywords() -> None:
    builder = (
        PynencBuilder()
        .app_id("alias_mongo3")
        .rustvello_mongo3(
            host="mongo.internal",
            port=27017,
            username="calc",
            password="p@ss/word",
            auth_source="admin",
            db="pynenc",
        )
    )
    assert builder._config["orchestrator_cls"] == "RustMongo3NativeOrchestrator"
    assert builder._config["broker_cls"] == "RustMongo3Broker"
    assert (
        builder._config["mongo_url"]
        == "mongodb://calc:p%40ss%2Fword@mongo.internal:27017/?authSource=admin"
    )
    assert builder._config["mongo_db_name"] == "pynenc"


def test_mongo3_url_keyword_wins_over_parts() -> None:
    builder = (
        PynencBuilder()
        .app_id("alias_url")
        .rustvello_mongo3(url="mongodb://x:27017", host="ignored")
    )
    assert builder._config["mongo_url"] == "mongodb://x:27017"


def test_rabbitmq_broker_accepts_pynenc_rabbitmq_keywords() -> None:
    builder = (
        PynencBuilder()
        .app_id("alias_rmq")
        .rustvello_mem()
        .rustvello_rabbitmq_broker(host="rabbitmq-service")
    )
    assert builder._config["broker_cls"] == "RustRabbitmqBroker"
    assert builder._config["rabbitmq_url"] == "amqp://guest:guest@rabbitmq-service:5672"
    assert builder._config["orchestrator_cls"] == "RustMemNativeOrchestrator"


def test_rabbitmq_broker_requires_url_or_host() -> None:
    with pytest.raises(ValueError, match="rabbitmq_url or host"):
        PynencBuilder().app_id(
            "alias_rmq_err"
        ).rustvello_mem().rustvello_rabbitmq_broker()


def test_uri_helpers_quote_and_default() -> None:
    assert (
        _mongo_url_from_parts(None, None, None, None, None)
        == "mongodb://localhost:27017"
    )
    assert (
        _amqp_url_from_parts("h", 5673, "u", "p w", "prod")
        == "amqp://u:p%20w@h:5673/prod"
    )
