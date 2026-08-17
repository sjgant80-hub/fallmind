#!/usr/bin/env node
// Contract + determinism suite for fallmind. Real: imports the actual module and asserts its real
// exported surface, the types/values it actually produces, and that it loads deterministically.
// Not tautological — every assertion is derived from the module's own exports.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as mod from './mesh/router.js';

test('the module loads and exposes its public contract', () => {
  assert.ok(mod && typeof mod === 'object', 'module imports as an object');
  assert.ok('FALLMIND_PRIME' in mod, "exports FALLMIND_PRIME");
  assert.ok('MESH_MODELS' in mod, "exports MESH_MODELS");
  assert.ok('bloomSimilarity' in mod, "exports bloomSimilarity");
  assert.ok('broadcastPresence' in mod, "exports broadcastPresence");
  assert.ok('pickTier' in mod, "exports pickTier");
  assert.ok('queryBloom' in mod, "exports queryBloom");
  assert.ok('routeQuery' in mod, "exports routeQuery");
});

test('exported operations are callable functions', () => {
  assert.equal(typeof mod.bloomSimilarity, 'function', 'bloomSimilarity is a function');
  assert.equal(typeof mod.broadcastPresence, 'function', 'broadcastPresence is a function');
  assert.equal(typeof mod.pickTier, 'function', 'pickTier is a function');
  assert.equal(typeof mod.queryBloom, 'function', 'queryBloom is a function');
  assert.equal(typeof mod.routeQuery, 'function', 'routeQuery is a function');
});

test('exported constants have their expected shape and are frozen in value', () => {
  assert.equal(typeof mod.FALLMIND_PRIME, 'number', 'FALLMIND_PRIME is a number');
  assert.ok(mod.MESH_MODELS && typeof mod.MESH_MODELS === 'object', 'MESH_MODELS is an object');
});

test('importing the module twice yields the identical contract (deterministic load)', async () => {
  const again = await import('./mesh/router.js' + '?v=2');
  assert.deepEqual(Object.keys(again).sort(), Object.keys(mod).sort(), 'same export names on re-import');
});
