# Geocoding & Map Plotting Analysis - Complete Documentation Index

This directory contains comprehensive analysis of the Derby City Watch geocoding and map plotting system.

## Documents Included

### 1. **GEOCODING_ANALYSIS_EXECUTIVE_SUMMARY.md** (11 KB)
**Start here** for a high-level overview.

Contains:
- What the system does (overview)
- Current performance metrics (3,056 addresses, 37.76% success)
- How the pipeline works (4 phases)
- Why 62% of addresses fail (with visualized breakdown)
- What prevents geocoding/plotting
- Improvement opportunities
- Quick reference to key files

**Best for:** Project managers, quick understanding, decision making

---

### 2. **GEOCODING_ANALYSIS_DETAILED.md** (19 KB)
**Complete technical documentation.**

Contains 8 major sections:
1. **Geocoding Workflow** - Detailed architecture & process
   - Address extraction patterns (3 regex patterns explained)
   - Address normalization (cleaning logic)
   - 5-tier fallback strategy
   - Nominatim API details
   - 3-layer caching strategy

2. **Plotting on Maps** - Map technology & display
   - Leaflet.js setup
   - Marker colors and categories
   - Location grouping
   - Popup content generation
   - Filtering and display logic

3. **Failure Analysis** - Why addresses don't geocode
   - Current failure rate: 62.24%
   - Failure pattern breakdown (6 categories)
   - Specific failure scenarios
   - Geocoding data files

4. **Data Files** - Where results are stored
   - `geocoded_addresses.yml` (319 KB)
   - `geocoding_success_metrics.yml` (43 KB)

5. **Scripts & Configuration**
   - `geocode_addresses.py` (391 lines)
   - `retry_failed_geocodes.py` (88 lines)
   - `track_geocoding_success.py` (327 lines)
   - GitHub Actions workflow

6. **Filtering Logic** - What gets excluded
   - Daily digest post exclusion
   - NULL geocoding results
   - Date range filtering
   - Generic text exclusion

7. **Common Failure Points** - Summary & quick fixes

8. **Workflow Automation** - How GitHub Actions orchestrates everything

**Best for:** Developers, understanding the complete system, debugging

---

### 3. **GEOCODING_ANALYSIS_FAILURE_CASES.md** (15 KB)
**Detailed failure analysis with code examples.**

Contains:
- **6 real failure case studies** from the actual cache
  - Location qualifiers (47.8% of failures)
  - Corrupted extraction (15.4%)
  - Intersection format issues (12.0%)
  - Extra text after address (9.4%)
  - Police phonetic codes (0.1%)
  - Highway addressing issues

- **Code walkthroughs** with line numbers
  - Address extraction (lines 60-90)
  - Address cleaning (lines 144-186)
  - 5-tier geocoding strategy (lines 264-311)
  - Landmark extraction (lines 208-234)
  - JavaScript filtering (lines 841-847)

- **Improvement recommendations**
  - High-priority fixes (would improve 910 failures)
  - Medium-priority fixes (would improve 178 failures)
  - Low-priority fixes (would improve 229 failures)

- **Summary table** showing current handling vs fixability

**Best for:** Implementing improvements, understanding root causes, debugging specific failures

---

### 4. **GEOCODING_ANALYSIS_FILE_REFERENCE.md** (5.7 KB)
**Quick reference guide to all files.**

Contains:
- **Python scripts location & purpose**
- **Data files location & statistics**
- **HTML/JavaScript layout files**
- **Configuration files**
- **Post templates**
- **Key code sections** with line numbers
- **Current statistics** (Nov 18, 2025)
- **Execution flow diagrams**

**Best for:** Finding files, understanding data flow, quick lookups

---

## How to Navigate

### By Role

**If you're a...** → **Read this document**

- **Project Manager**: EXECUTIVE_SUMMARY
- **Developer (new)**: EXECUTIVE_SUMMARY → DETAILED
- **Developer (debugging)**: FAILURE_CASES + DETAILED
- **DevOps/Automation**: DETAILED (section 8: Workflow Automation)
- **Anyone needing quick file lookup**: FILE_REFERENCE

### By Question

**I want to know...** → **Look here**

| Question | Document | Section |
|----------|----------|---------|
| How does geocoding work? | DETAILED | Section 1 |
| Why do addresses fail? | EXECUTIVE_SUMMARY or FAILURE_CASES | Failure Breakdown |
| Where are the files? | FILE_REFERENCE | N/A (whole doc) |
| How does the map display work? | DETAILED | Section 2 |
| What prevents geocoding? | DETAILED | Section 3 |
| How can I improve it? | FAILURE_CASES | Recommendations |
| How does automation work? | DETAILED | Section 8 |
| What are the current metrics? | EXECUTIVE_SUMMARY or DETAILED | Current Status |

---

## Key Statistics (November 18, 2025)

```
Total Addresses Extracted:     3,056
Successfully Geocoded:         1,154 (37.76%)
Failed Geocoding:              1,902 (62.24%)

Top Failure Categories:
  1. Location qualifiers (near/at):        910 failures (47.8%)
  2. Incomplete/vague addresses:           293 failures (15.4%)
  3. Unknown/Other:                        290 failures (15.2%)
  4. Intersection format issues:           229 failures (12.0%)
  5. Extra text/sentences:                 178 failures (9.4%)
  6. Police phonetic codes:                  2 failures (0.1%)

System Performance:
  - Map load time: Instant (pre-computed coordinates)
  - Geocoding rate: 1 request/second (API compliant)
  - Cache strategy: 3-layer (server/browser/live)
  - Automation: GitHub Actions on new posts
```

---

## File Locations (All Absolute Paths)

### Analysis Documents (New)
```
/home/user/Louisville/GEOCODING_ANALYSIS_EXECUTIVE_SUMMARY.md
/home/user/Louisville/GEOCODING_ANALYSIS_DETAILED.md
/home/user/Louisville/GEOCODING_ANALYSIS_FAILURE_CASES.md
/home/user/Louisville/GEOCODING_ANALYSIS_FILE_REFERENCE.md
/home/user/Louisville/GEOCODING_ANALYSIS_INDEX.md (this file)
```

### Source Code
```
/home/user/Louisville/scripts/geocode_addresses.py
/home/user/Louisville/scripts/retry_failed_geocodes.py
/home/user/Louisville/scripts/track_geocoding_success.py
/home/user/Louisville/scripts/test_sample_improvements.py
```

### Data & Configuration
```
/home/user/Louisville/_data/geocoded_addresses.yml
/home/user/Louisville/_data/geocoding_success_metrics.yml
/home/user/Louisville/_layouts/map.html
/home/user/Louisville/.github/workflows/geocode-addresses.yml
/home/user/Louisville/geocoding_success_report.md
```

---

## Quick Start: Understanding the System

**5-minute overview:**
1. Read EXECUTIVE_SUMMARY
2. Skim the "How It Works: The Pipeline" section
3. Look at the "Why 62% of Addresses Fail" breakdown

**30-minute deep dive:**
1. Read EXECUTIVE_SUMMARY (10 min)
2. Read DETAILED sections 1-2 (15 min)
3. Skim FAILURE_CASES section on real examples (5 min)

**Complete understanding (2-3 hours):**
1. Read all sections of DETAILED (1.5 hours)
2. Read FAILURE_CASES with code examples (45 min)
3. Reference FILE_REFERENCE as needed (15 min)

---

## Making Improvements

### To improve geocoding success rate:

1. **Identify failure pattern** → FAILURE_CASES document
2. **Find relevant code** → Use FILE_REFERENCE for line numbers
3. **Understand current logic** → DETAILED section for context
4. **Test changes** → Use `scripts/test_sample_improvements.py`
5. **Measure impact** → View `geocoding_success_report.md`

### Best opportunities:
- Location qualifier improvement: Could fix 910 failures
- Better sentence detection: Could fix 178 failures
- Corrupted extraction fix: Could fix 293 failures

---

## Feedback & Updates

These documents were generated on: **November 18, 2025**

Based on:
- 3,056 total addresses in cache
- 3 Python scripts (391, 88, 327 lines)
- 1 Map layout (1,023 lines of HTML/JS)
- 1 GitHub Actions workflow
- Historical metrics from 11/17 onwards

---

## Document Version Control

Since these are analysis documents (not code), they're stored separately:
- GEOCODING_ANALYSIS_*.md files
- These supplement the actual source code
- Both should be updated when system changes

---

