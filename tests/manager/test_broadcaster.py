import pytest
from unittest.mock import Mock, call

from custom_components.owlbrain.manager.broadcaster import OwlBrainBroadcaster
from custom_components.owlbrain.const import WS_MESSAGE_VERSION


@pytest.fixture
def mock_manager():
    manager = Mock()
    manager.entities.force_ha_refresh = Mock()
    return manager


@pytest.fixture
def broadcaster(mock_manager):
    return OwlBrainBroadcaster(mock_manager)


# -----------------------------
#region ADD
# -----------------------------


def test_add_adds_connection_and_triggers_refresh(broadcaster, mock_manager):
    # Arrange
    namespace = "ns1"
    conn = Mock()

    # Act
    broadcaster.add(namespace, conn)

    # Assert
    assert broadcaster.available(namespace) is True
    assert conn in broadcaster._subs[namespace]
    mock_manager.entities.force_ha_refresh.assert_called_once_with(namespace)


# endregion -------------------
#region REMOVE
# -----------------------------

def test_remove_removes_connection_and_triggers_refresh_when_last(broadcaster, mock_manager):
    # Arrange
    namespace = "ns1"
    conn = Mock()
    broadcaster.add(namespace, conn)

    # Act
    broadcaster.remove(namespace, conn)

    # Assert
    assert broadcaster.available(namespace) is False
    mock_manager.entities.force_ha_refresh.assert_called_with(namespace)


def test_remove_does_not_trigger_refresh_if_other_connections_remain(broadcaster, mock_manager):
    # Arrange
    namespace = "ns1"
    conn1 = Mock()
    conn2 = Mock()
    broadcaster.add(namespace, conn1)
    broadcaster.add(namespace, conn2)
    mock_manager.entities.force_ha_refresh.reset_mock()

    # Act
    broadcaster.remove(namespace, conn1)

    # Assert
    assert broadcaster.available(namespace) is True
    mock_manager.entities.force_ha_refresh.assert_not_called()

# endregion -------------------
#region AVAILABLE
# -----------------------------

@pytest.mark.parametrize(
    "existing, expected",
    [
        ([], False),
        ([Mock()], True),
    ],
)
def test_available_reports_correct_status(broadcaster, existing, expected):
    # Arrange
    namespace = "ns1"
    for conn in existing:
        broadcaster.add(namespace, conn)

    # Act
    result = broadcaster.available(namespace)

    # Assert
    assert result is expected

# endregion -------------------
#region BROADCAST
# -----------------------------

def test_broadcast_sends_message_to_all_connections(broadcaster):
    # Arrange
    namespace = "ns1"
    conn1 = Mock()
    conn2 = Mock()
    broadcaster.add(namespace, conn1)
    broadcaster.add(namespace, conn2)
    message = {"hello": "world"}

    # Act
    broadcaster.broadcast(namespace, message)

    # Assert
    conn1.send_message.assert_called_once_with(message)
    conn2.send_message.assert_called_once_with(message)

@pytest.mark.asyncio
async def test_broadcast_entity_action_constructs_and_broadcasts_message(broadcaster):
    # Arrange
    namespace = "ns1"
    conn = Mock()
    broadcaster.add(namespace, conn)

    entity_id = "entity123"
    action = "update"
    data = {"value": 42}

    # Act
    await broadcaster.broadcast_entity_action(namespace, entity_id, action, data)

    # Assert
    expected_message = {
        "type": "owlbrain_entity_action",
        "version": WS_MESSAGE_VERSION,
        "namespace": namespace,
        "entity_id": entity_id,
        "action": action,
        "data": data,
    }
    conn.send_message.assert_called_once_with(expected_message)


def test_broadcast_no_subscribers_does_not_fail(broadcaster):
    # Arrange
    namespace = "empty"

    # Act / Assert (no exception)
    broadcaster.broadcast(namespace, {"msg": "test"})

#endregion
