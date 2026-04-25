# Update Landing Hero Content and Images

## Motivation
The current hero slider in the landing page (`HeroSection.astro`) contains placeholder data with three identical slides. To better communicate the core value proposition, the academy/educational offering, and the booking experience, this content needs to be updated with distinct, targeted copy and imagery that aligns with the brand's aesthetics (K-Beauty Aesthetics, Service Menu, and Exclusive In-Person Courses).

## Proposed Solution
- Update the hardcoded `slides` array in `landing/src/components/organisms/HeroSection.astro` with the new content for the 3 distinct slides (Core Value Proposition, Academy/Educational Offering, The Experience/Booking Focus).
- Generate or source 3 high-quality images that match the brand guidelines (warm tones, professional aesthetic).
- Place the images in `landing/src/assets/images/` as `hero-treatments.webp`, `hero-academy.webp`, and `hero-experience.webp`.
- Import the new images in `HeroSection.astro` and assign them to the respective slides.

## Capabilities Impacted
- `landing-ui-content`: A new capability spec detailing the content requirements for the landing page UI components.
