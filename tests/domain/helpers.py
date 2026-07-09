from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from custom_components.owlbrain.models.entity import EntityModel


class EntityTestHelper:
	def __init__(
		self,
		entity_cls: type,
		manager=None,
		hass=None,
		metadata=None,
		domain="test",
	):
		self.entity_cls = entity_cls
		self.namespace = "test"
		self.domain = domain
		self.unique_id = "1234"
		self.initial_metadata = metadata if metadata is not None else {}
		self.manager = manager
		self.hass = hass

	def create_entity(self):
		"""Instantiate entity with a valid EntityModel."""
		model = EntityModel(
			namespace=self.namespace,
			domain=self.domain,
			unique_id=self.unique_id,
			entity_id="test.entity",
			metadata=self.initial_metadata,
		)
		entity = self.entity_cls(self.hass, self.manager, model)
		entity.async_write_ha_state = lambda *args, **kwargs: None
		return entity

	async def run_metadata_matrix(
		self,
		matrix: list[
			tuple[
				str,  # key name
				Any,  # value to apply
				type[Exception] | None,  # expected exception
				dict[str, Any],  # expected reflected properties
			]
		],
	):
		for key, value, expected_exc, expected_props in matrix:
			entity = self.create_entity()
			metadata = dict(entity.owl_model.metadata)
			metadata[key] = value

			if expected_exc:
				with pytest.raises(expected_exc):
					await entity.async_update_metadata(metadata)
			else:
				await entity.async_update_metadata(metadata)

			# Validate metadata reflection
			for prop, expected in expected_props.items():
				actual = getattr(entity, prop)
				assert actual == expected, (
					f"when metadata {key} is {value}, property {prop} was "
					f"expected to be {expected}, but got {actual}"
				)

	async def run_data_matrix(
		self,
		matrix: list[
			tuple[
				str,  # key name
				Any,  # value to apply
				type[Exception] | None,  # expected exception
				dict[str, Any],  # expected reflected properties
			]
		],
	):
		for key, value, expected_exc, expected_props in matrix:
			entity = self.create_entity()
			new_data = {key: value}

			if expected_exc:
				with pytest.raises(expected_exc):
					await entity.async_update_data(new_data)
			else:
				await entity.async_update_data(new_data)

			# Validate reflected properties
			for prop, expected in expected_props.items():
				actual = getattr(entity, prop)
				assert actual == expected, (
					f"when data {key} is {value}, property {prop} was "
					f"expected to be {expected}, but got {actual}"
				)

	async def run_action_matrix(
		self,
		matrix: list[
			tuple[
				str,  # entity method name (e.g. "async_turn_on")
				Any,  # args: dict for kwargs OR tuple/list for positional args
				str,  # expected broadcast action name
				Any,  # expected broadcast data
			]
		],
	):
		for method_name, args, expected_action, expected_data in matrix:
			entity = self.create_entity()

			mock_broadcaster = AsyncMock()
			mock_manager = type(
				"MockManager",
				(),
				{
					"broadcaster": type(
						"MockBroadcaster",
						(),
						{"broadcast_entity_action": mock_broadcaster},
					)()
				},
			)()

			entity._manager = mock_manager

			method = getattr(entity, method_name)

			if args is None:
				# no arguments at all
				await method()
			elif isinstance(args, dict):
				# kwargs
				await method(**args)
			elif isinstance(args, (tuple, list)):
				# positional args
				await method(*args)
			else:
				# single positional argument
				await method(args)

			mock_broadcaster.assert_awaited_once_with(
				entity.owl_namespace,
				entity.owl_entity_id,
				expected_action,
				expected_data,
			)

	async def run_platform_registration_test(self, setup_fn):
		"""Test that async_setup_entry registers the correct platform."""
		from unittest.mock import AsyncMock, MagicMock

		async_add_entities = AsyncMock()

		entry = MagicMock()

		mock_manager = MagicMock()
		mock_manager.entities = MagicMock()
		mock_manager.entities.register_platform = MagicMock()

		self.hass.data = {"owlbrain": {"manager": mock_manager}}

		await setup_fn(self.hass, entry, async_add_entities)

		mock_manager.entities.register_platform.assert_called_once_with(
			self.domain, async_add_entities
		)
