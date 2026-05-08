# Design: Remove Stagehand

## Overview
The decision to remove Stagehand stems from the inherent instability of relying on LLM calls for deterministic UI testing and validation in our current setup.

## Impact
By deleting the `stagehand` directory, we remove the `landing-test` and `automate` commands. This leaves a temporary gap in automated E2E testing for the landing page. In the future, if automated E2E testing is required, we will favor deterministic frameworks like standard Playwright or Cypress without the AI extraction layer.
