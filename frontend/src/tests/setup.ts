/**
 * Test setup file for Vitest
 *
 * Configures testing environment with:
 * - jsdom for browser API simulation
 * - Testing Library matchers
 */

import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Add custom matchers
expect.extend({})
