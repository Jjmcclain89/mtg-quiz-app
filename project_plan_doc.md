# Project Planning Document

## Project Overview

**Project Name:** MTG Card Name Learning Tool  
**Project Lead:** Josh McClain

## Goals & Objectives

### Primary Goal
Create a web-based learning tool to help Magic: The Gathering players memorize card names by showing card images without names and having users guess the correct name with autocomplete assistance.

### Success Criteria
- [ ] Successfully display random MTG cards without names visible
- [ ] Implement working autocomplete using Scryfall API
- [ ] Provide immediate feedback on correct/incorrect guesses
- [ ] Allow users to customize card pools through settings
- [ ] Responsive design that works well on mobile devices

### Scope
**In Scope:**
- Card image display with name hidden
- Multiple input modes: autocomplete, plain text, and multiple choice
- Score tracking for current session
- Format dropdown filter (Standard, Modern, Legacy, etc.)
- Expansion/Set dropdown filter (populated from Scryfall sets API)
- Filtered card pool based on selected format/expansion
- Difficulty level system (framework and basic implementation)
- Mobile-responsive design
- Skip card functionality

**Out of Scope:**
- User accounts or persistent data storage
- Backend server or database
- Advanced statistics or progress tracking
- Multiplayer features
- Native mobile app (future enhancement)

## Tech Stack

### Frontend
- **Framework:** React with TypeScript (for type safety with API responses)
- **Styling:** Tailwind CSS (for rapid responsive design)
- **Build Tool:** Vite (fast development and building)
- **State Management:** React hooks (useState, useEffect, useContext)

### Infrastructure & Tools
- **Hosting:** Vercel or Netlify (easy static site deployment)
- **Version Control:** Git/GitHub
- **Development:** VS Code with React/TypeScript extensions
- **Testing:** Jest + React Testing Library (for component testing)

### Third-Party Services
- **Scryfall API:** Primary data source for card information
  - `/cards/random` - Get random cards (with search filters)
  - `/cards/autocomplete` - Card name autocomplete
  - `/cards/search` - Search cards by format, set, and other criteria
  - `/sets` - Get all MTG sets/expansions for dropdown population
  - `/catalog/formats` - Get available formats for dropdown population
- **Image Handling:** Direct URLs from Scryfall API responses

## Project Plan

### Phase 1: Setup & API Data Integration (Week 1)
- [ ] Set up React + TypeScript + Vite project
- [ ] Configure Tailwind CSS
- [ ] Set up ESLint and Prettier
- [ ] Create basic project structure and components
- [ ] Implement Scryfall API service layer
- [ ] Build Format dropdown (fetch from `/catalog/formats`)
- [ ] Build Expansion dropdown (fetch from `/sets` API)
- [ ] Implement search filtering logic (format + expansion combination)
- [ ] Create temporary JSON display component to show filtered card results
- [ ] Test all filter combinations and validate API responses

### Phase 2: Card Display & Core Guessing Game (Week 2)
- [ ] Build card display component (with name hidden from image)
- [ ] Implement random card selection from filtered results
- [ ] Create guess input with Scryfall autocomplete
- [ ] Add guess submission and validation logic
- [ ] Implement basic feedback system (correct/incorrect indicators)
- [ ] Remove temporary JSON display and integrate with card display
- [ ] Add skip card functionality
- [ ] Handle card image loading states and errors

### Phase 3: Enhanced Functionality & Input Modes (Week 3)
- [ ] Add basic score tracking for current session
- [ ] Implement streak tracking
- [ ] Add "All Formats" and "All Expansions" default options
- [ ] Handle edge cases (no cards found, API errors)
- [ ] Implement local storage for filter preferences
- [ ] Add clear/reset filter functionality
- [ ] **Build input mode selector with three options:**
  - [ ] Autocomplete input (current implementation)
  - [ ] Plain text input (no autocomplete assistance)
  - [ ] Multiple choice options (generated from card pool)
- [ ] Implement logic for each input mode type
- [ ] Improve UX with loading states and transitions

### Phase 4: Difficulty Level Implementation (Week 4)
- [ ] **Implement difficulty level system:**
  - [ ] Create difficulty level selector (Easy, Medium, Hard, Expert)
  - [ ] Define difficulty parameters and game rules for each level
  - [ ] Implement time limits and timer functionality
  - [ ] Add hint system for easier difficulties
  - [ ] Implement card pool filtering by difficulty (popular vs obscure cards)
  - [ ] Adjust scoring system based on difficulty level
  - [ ] Add difficulty-specific feedback and encouragement
- [ ] Performance optimization (image preloading, caching)
- [ ] Error handling improvements

### Phase 5: Mobile Optimization, Deployment & Final Testing (Week 5)
- [ ] Ensure fully responsive design for mobile devices
- [ ] Mobile-specific UX improvements and touch interactions
- [ ] Add loading animations and better mobile UX
- [ ] Implement keyboard shortcuts (Enter to submit, etc.)
- [ ] Cross-browser testing and mobile device testing
- [ ] Deploy to Vercel/Netlify
- [ ] Performance audit and optimization for mobile
- [ ] Final bug fixes and polish
- [ ] Documentation and README

## Risk Management

### Potential Risks
| Risk | Impact | Likelihood | Mitigation Strategy |
|------|---------|------------|-------------------|
| Scryfall API rate limiting | High | Medium | Implement request caching, add delays between requests, have fallback card sets |
| Filter combinations returning no cards | Medium | Medium | Validate filter combinations, show warnings, fallback to broader search |
| Large set data slowing dropdown population | Medium | Low | Cache set/format data, implement loading states, lazy load if needed |
| Multiple choice generation being too easy/hard | Medium | Medium | Test different algorithms for generating similar cards, allow difficulty adjustment |
| Scryfall API changes/downtime | High | Low | Cache responses locally, have backup card data, monitor API status |
| Card images taking too long to load | Medium | Medium | Implement image preloading, show loading states, optimize image sizes |
| Mobile performance with large card pools | Medium | Medium | Limit search results, optimize bundle size, implement pagination |

## Success Metrics

### Technical Metrics
- [ ] Application loads in under 3 seconds on mobile
- [ ] Card images load within 2 seconds
- [ ] Autocomplete responds within 500ms
- [ ] Works across major browsers (Chrome, Safari, Firefox)
- [ ] No critical errors or crashes

### User Experience Metrics
- [ ] Users can successfully guess card names with autocomplete
- [ ] Settings properly filter card pools
- [ ] Mobile experience is smooth and usable
- [ ] Keyboard navigation works properly
- [ ] Clear feedback for correct/incorrect guesses

## Resources & Dependencies

### Development Resources
- Scryfall API documentation: https://scryfall.com/docs/api
- React TypeScript documentation
- Tailwind CSS documentation

### External Dependencies
- **Scryfall API** (free, no API key required)
  - Rate limit: ~100 requests per second
  - Reliable uptime and comprehensive MTG data
- **Internet connection** for API calls and image loading
- **Modern browser** with JavaScript enabled

### Key API Endpoints
- `GET /cards/search?q={query}` - Search cards with format/set filters
  - Example: `/cards/search?q=format:standard` for Standard cards
  - Example: `/cards/search?q=set:neo` for Kamigawa: Neon Dynasty cards
  - Example: `/cards/search?q=format:modern set:mh2` for Modern Horizons 2 cards in Modern
- `GET /cards/autocomplete?q={query}` - Autocomplete card names
- `GET /sets` - Get all MTG sets/expansions for dropdown
- `GET /catalog/formats` - Get available play formats
- Card images available via `image_uris` in API responses

## Communication Plan

- **Daily:** Personal progress tracking and commits
- **Weekly:** Review completed features and plan next phase
- **Project Updates:** Update README and deployment status

---

## Notes & Decisions

### Technical Decisions
- **No backend needed:** Scryfall API provides everything required
- **TypeScript chosen:** Better type safety when working with API responses
- **Tailwind CSS:** Faster development and easier responsive design
- **Local storage only:** Settings persistence without complexity
- **Search-based card fetching:** Instead of random cards, use `/cards/search` with filters and random page selection
- **Dropdown population on load:** Fetch formats and sets once on app initialization and cache

### Card Pool Strategy
- When no filters selected: Use `/cards/search?q=*` with random page
- When format selected: Use `/cards/search?q=format:{format_name}`
- When expansion selected: Use `/cards/search?q=set:{set_code}`
- When both selected: Use `/cards/search?q=format:{format} set:{set_code}`
- Handle pagination by randomly selecting from available pages

### Future Enhancement Ideas
- Convert to React Native/Expo for mobile app
- Add user accounts and progress tracking
- Implement different game modes (multiple choice, etc.)
- Add card art recognition (guess from cropped art)
- Support for other card games
- Advanced difficulty settings (time limits, hint systems, etc.)
- Leaderboards and social features

### Input Mode Considerations
- **Autocomplete:** Uses Scryfall autocomplete API for assistance
- **Plain Text:** Manual typing with exact name matching required
- **Multiple Choice:** Generate 3-4 options from similar cards in the pool (same CMC, type, or set)
- All modes should support the same scoring and feedback systems

### Difficulty Level Ideas (To Develop)
- **Easy:** Autocomplete mode, longer time limits, hints available
- **Medium:** Plain text mode, moderate time limits
- **Hard:** Multiple choice with similar cards, shorter time limits
- **Expert:** Plain text, no skips, timer pressure
- Could also affect card pool (popular vs obscure cards)

**Last Updated:** [Date]