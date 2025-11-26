/**
 * Tests for App component
 *
 * Demonstrates production-ready frontend testing:
 * - Component rendering
 * - User interactions
 * - Accessibility
 */

import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders the app title', () => {
    render(<App />)
    expect(screen.getByText(/Glitch Forge HITL/i)).toBeInTheDocument()
  })

  it('renders welcome message', () => {
    render(<App />)
    expect(screen.getByText(/Welcome to Glitch Forge/i)).toBeInTheDocument()
  })

  it('increments counter when button is clicked', () => {
    render(<App />)

    const button = screen.getByText(/Increment Counter/i)
    const counter = screen.getByText('0')

    expect(counter).toBeInTheDocument()

    fireEvent.click(button)
    expect(screen.getByText('1')).toBeInTheDocument()

    fireEvent.click(button)
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('renders feature cards', () => {
    render(<App />)

    expect(screen.getByText(/🚀 Fast/i)).toBeInTheDocument()
    expect(screen.getByText(/📱 Mobile-First/i)).toBeInTheDocument()
    expect(screen.getByText(/🔒 Secure/i)).toBeInTheDocument()
  })
})
