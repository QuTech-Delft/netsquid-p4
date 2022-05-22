"""Utilities for tests."""


def handler(sent, msg):
    assert msg is not None
    assert len(msg.items) == 1
    sent.append(msg.items[0])


def assert_handler(msg):
    assert msg is None
