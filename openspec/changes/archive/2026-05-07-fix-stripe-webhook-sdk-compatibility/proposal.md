# Proposal: Fix Stripe Webhook SDK Compatibility

## Why
In production, successful Stripe payments are not updating the booking status to `PAID` because the webhook handler crashes with an `AttributeError`. This is due to the Stripe SDK no longer supporting `.get()` on Stripe event and session objects.

## What Changes
We need to switch to attribute access (`.id`, `.data.object`, etc.) to restore payment confirmation functionality.

## Objective
Fix the `AttributeError: get` exception in `StripeWebhookView` caused by upgrading the Stripe Python SDK to version 11+, which removes dictionary-like access (`.get()`) from Stripe objects.

## Motivation
See "Why".

## Scope
- Modify `StripeWebhookView` in `dashboard/booking/views.py` to use dot notation for Stripe object property access.
- Ensure existing tests pass or update them if they relied on dictionary-like mock objects that no longer reflect the SDK's behavior.

## Out of Scope
- Upgrading the Stripe SDK to a newer version (we are just fixing compatibility with the current `stripe>=11.4.0` version).
- Refactoring the entire checkout process.
