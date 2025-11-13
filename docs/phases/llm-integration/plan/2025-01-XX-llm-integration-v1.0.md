# Feature Plan: LLM Integration (VIN Decode & GPT Summary)

**Date:** 2025-01-XX  
**Phase:** LLM Integration (Step 8)  
**Status:** 🟡 Planning

---

## Feature Overview

### What It Does
This phase adds two key integration features to enhance the damage estimation system:
1. **VIN Decode** - Decodes Vehicle Identification Numbers (VIN) using the NHTSA API to retrieve vehicle information (make, model, year, etc.)
2. **GPT Summary** - Generates optional human-readable summaries of damage reports using OpenAI's GPT API, making technical damage assessments more accessible to users

### Why It's Needed
- **VIN Decode**: Provides vehicle context for more accurate cost estimation and better report documentation
- **GPT Summary**: Improves user experience by translating technical damage detection results into natural language that's easier to understand
- **Explainability**: Aligns with project goal of transparency and explainability in damage assessment
- **User Experience**: Makes reports more professional and accessible to non-technical users

### User Story
As a user, I want:
- To optionally provide my vehicle's VIN so the system can include vehicle details in my damage report
- To receive a natural language summary of the damage assessment that explains what was found in plain English
- To understand the damage assessment without needing technical knowledge of car parts and repair terminology

---

## Technical Requirements

### Backend Changes

#### VIN Decode Service
- [ ] Create VIN decode service (`apps/api/services/integration/vin_decode.py`)
- [ ] Integrate with NHTSA API (free, no authentication required)
- [ ] Handle VIN validation (17 characters, alphanumeric)
- [ ] Parse NHTSA API response (make, model, year, body type, etc.)
- [ ] Cache VIN decode results (optional, to reduce API calls)
- [ ] Handle API errors and rate limiting gracefully

#### GPT Summary Service
- [ ] Create GPT summary service (`apps/api/services/integration/gpt_summary.py`)
- [ ] Integrate with OpenAI API (gpt-4o-mini for cost efficiency)
- [ ] Design prompt template for damage report summarization
- [ ] Handle API authentication (API key from environment)
- [ ] Implement error handling and retry logic
- [ ] Add cost tracking/monitoring (optional)

#### API Endpoints
- [ ] `POST /api/v1/vin/decode` - Decode VIN and return vehicle information
- [ ] `POST /api/v1/report/summary` - Generate GPT summary for damage report
- [ ] Update `POST /api/v1/report/pdf` - Optionally include VIN info and GPT summary in PDF

#### Data Models
- [ ] Create VIN decode request/response models
- [ ] Create GPT summary request/response models
- [ ] Update report models to include optional VIN info and summary

#### Configuration
- [ ] Add OpenAI API key to environment variables
- [ ] Add NHTSA API base URL to config (or hardcode, it's public)
- [ ] Add GPT model selection to config (default: gpt-4o-mini)
- [ ] Add summary generation toggle (enable/disable feature)

#### Dependencies Needed
- [ ] `openai` - OpenAI Python SDK
- [ ] `httpx` or `requests` - For NHTSA API calls (requests already in use)
- [ ] `python-dotenv` - Already in use for environment variables

### Frontend Changes

#### VIN Input (Optional)
- [ ] Add optional VIN input field to Upload page
- [ ] Add "Decode VIN" button or auto-decode on input
- [ ] Display decoded vehicle information (make, model, year)
- [ ] Show loading state during VIN decode
- [ ] Handle VIN decode errors gracefully

#### GPT Summary Display (Optional)
- [ ] Add toggle/checkbox to enable/disable GPT summary generation
- [ ] Display GPT summary in report view
- [ ] Show loading state during summary generation
- [ ] Handle summary generation errors gracefully
- [ ] Optionally include summary in PDF export

### Database Changes
- [ ] None (stateless API calls, no persistent storage needed)

### API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/v1/vin/decode` | Decode VIN and return vehicle information | Planned |
| POST | `/api/v1/report/summary` | Generate GPT summary for damage report | Planned |
| POST | `/api/v1/report/pdf` | Generate PDF (updated to include VIN/summary) | Update |

---

## Implementation Details

### Architecture Approach

#### VIN Decode Flow
```
User provides VIN
  ↓
Frontend sends VIN to /api/v1/vin/decode
  ↓
Backend validates VIN format
  ↓
Backend calls NHTSA API
  ↓
Backend parses response and returns vehicle info
  ↓
Frontend displays vehicle information
```

#### GPT Summary Flow
```
User requests summary (optional)
  ↓
Frontend sends report data to /api/v1/report/summary
  ↓
Backend formats damage report data
  ↓
Backend calls OpenAI API with prompt
  ↓
Backend receives summary text
  ↓
Backend returns summary to frontend
  ↓
Frontend displays summary (and optionally includes in PDF)
```

### File Structure
```
apps/api/
├── services/
│   └── integration/
│       ├── __init__.py
│       ├── vin_decode.py      # NEW - VIN decode service
│       └── gpt_summary.py     # NEW - GPT summary service
├── routes/
│   ├── vin.py                 # NEW - VIN decode endpoint
│   └── report.py              # UPDATE - Add summary endpoint
├── models/
│   ├── vin.py                 # NEW - VIN request/response models
│   └── report.py              # UPDATE - Add summary fields
└── core/
    └── config.py              # UPDATE - Add OpenAI API key config
```

### Component Breakdown

#### VIN Decode Service (`vin_decode.py`)
- **Responsibilities:**
  - Validate VIN format (17 characters, alphanumeric, no I/O/Q)
  - Call NHTSA API endpoint
  - Parse NHTSA response (JSON)
  - Extract relevant vehicle information
  - Handle API errors and rate limiting
  - Return structured vehicle data

#### GPT Summary Service (`gpt_summary.py`)
- **Responsibilities:**
  - Format damage report data into prompt
  - Call OpenAI API with appropriate model
  - Handle API authentication
  - Parse and return summary text
  - Handle errors and retries
  - Track API costs (optional)

#### VIN Decode Route (`routes/vin.py`)
- **Endpoint:** `POST /api/v1/vin/decode`
- **Request:** VIN string
- **Response:** Vehicle information (make, model, year, etc.)
- **Error Handling:** Invalid VIN format, NHTSA API errors

#### Report Summary Route (`routes/report.py`)
- **Endpoint:** `POST /api/v1/report/summary`
- **Request:** Report data (detections, estimates, etc.)
- **Response:** GPT-generated summary text
- **Error Handling:** OpenAI API errors, rate limits, invalid requests

### Data Flow

#### VIN Decode
1. User enters VIN in frontend
2. Frontend validates basic format (17 chars)
3. Frontend calls `/api/v1/vin/decode` with VIN
4. Backend validates VIN format
5. Backend calls NHTSA API: `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json`
6. Backend parses NHTSA response
7. Backend returns structured vehicle data
8. Frontend displays vehicle information

#### GPT Summary
1. User requests summary (optional checkbox/toggle)
2. Frontend collects report data (detections, estimates, totals)
3. Frontend calls `/api/v1/report/summary` with report data
4. Backend formats data into prompt template
5. Backend calls OpenAI API with prompt
6. Backend receives summary text
7. Backend returns summary to frontend
8. Frontend displays summary (and optionally includes in PDF)

### Prompt Design (GPT Summary)

The GPT prompt should:
- Include all damage detections (part, damage type, severity)
- Include cost estimates (line items and totals)
- Request natural language summary
- Emphasize clarity and accessibility
- Include vehicle information if available (from VIN)
- Request professional but friendly tone

**Example Prompt Structure:**
```
You are a professional automotive damage assessment assistant. 

Generate a clear, natural language summary of the following vehicle damage assessment:

Vehicle Information:
[Make, Model, Year from VIN if available]

Damage Detections:
[Part, Damage Type, Severity for each detection]

Cost Estimate:
[Line items with costs]
[Total estimates: min/likely/max]

Please provide a summary that:
1. Explains the damage found in plain language
2. Describes the repair requirements
3. Explains the cost estimate range
4. Is professional but accessible to non-technical users
5. Is concise (2-3 paragraphs)
```

---

## Testing Requirements

### Test Scenarios

#### VIN Decode - Happy Path
1. **Scenario:** User provides valid VIN and receives vehicle information
   - **Steps:**
     1. User enters valid 17-character VIN
     2. User clicks "Decode VIN" or VIN auto-decodes
     3. System calls NHTSA API
   - **Expected Frontend:** Vehicle information displayed (make, model, year)
   - **Expected Backend:** Successful API call, parsed response returned
   - **Success Criteria:** Vehicle information correctly displayed

#### VIN Decode - Invalid VIN
1. **Scenario:** User provides invalid VIN format
   - **Steps:**
     1. User enters invalid VIN (wrong length, invalid characters)
     2. User attempts to decode
   - **Expected:** Error message displayed, no API call made
   - **Success Criteria:** Clear error message, no unnecessary API calls

#### VIN Decode - NHTSA API Error
1. **Scenario:** NHTSA API returns error or is unavailable
   - **Steps:**
     1. User provides valid VIN
     2. NHTSA API returns error or times out
   - **Expected:** Graceful error handling, user-friendly error message
   - **Success Criteria:** System doesn't crash, error is handled gracefully

#### GPT Summary - Happy Path
1. **Scenario:** User requests summary and receives GPT-generated text
   - **Steps:**
     1. User completes damage analysis
     2. User enables "Generate Summary" option
     3. System calls OpenAI API
   - **Expected Frontend:** Summary text displayed in report
   - **Expected Backend:** Successful API call, summary text returned
   - **Success Criteria:** Summary is clear, relevant, and includes key information

#### GPT Summary - API Error
1. **Scenario:** OpenAI API returns error or is unavailable
   - **Steps:**
     1. User requests summary
     2. OpenAI API returns error or times out
   - **Expected:** Graceful error handling, fallback message or option to retry
   - **Success Criteria:** System doesn't crash, user can still view report without summary

#### GPT Summary - Cost Tracking
1. **Scenario:** System tracks API costs
   - **Steps:**
     1. Multiple summaries generated
     2. System logs API usage
   - **Expected:** Cost tracking in logs (optional)
   - **Success Criteria:** Can monitor API usage and costs

#### Integration - PDF with VIN and Summary
1. **Scenario:** PDF report includes VIN info and GPT summary
   - **Steps:**
     1. User provides VIN and requests summary
     2. User generates PDF report
   - **Expected:** PDF includes vehicle information and summary section
   - **Success Criteria:** PDF is complete and professional

### Integration Testing
- [ ] VIN decode works with real NHTSA API
- [ ] GPT summary generation works with real OpenAI API
- [ ] Both features work together in report generation
- [ ] PDF generation includes VIN and summary when available
- [ ] Error handling works for both services
- [ ] Frontend displays all information correctly

### Regression Testing
- [ ] Existing report generation still works
- [ ] Existing API endpoints unaffected
- [ ] Frontend upload/analyze workflow unchanged
- [ ] PDF generation works with and without VIN/summary

---

## Deliverables

### Final Output
- Working VIN decode integration with NHTSA API
- Working GPT summary generation with OpenAI API
- Updated API endpoints for both features
- Frontend integration for VIN input and summary display
- Updated PDF generation to include VIN and summary
- Comprehensive error handling for both services
- Documentation for API usage

### Acceptance Criteria
- [ ] VIN decode successfully retrieves vehicle information from NHTSA API
- [ ] GPT summary successfully generates human-readable summaries
- [ ] Both features are optional and don't break existing functionality
- [ ] Error handling works for both API integrations
- [ ] Frontend displays VIN info and summary correctly
- [ ] PDF reports include VIN and summary when available
- [ ] All tests pass
- [ ] Documentation is complete

### What "Done" Looks Like
- User can optionally provide VIN and see vehicle information in the report
- User can optionally request GPT summary and see it in the report
- Both features work seamlessly with existing damage detection workflow
- PDF reports can include vehicle information and summary
- All error cases are handled gracefully
- System is ready for production use

---

## Dependencies

### Prerequisites
- [ ] FastAPI backend foundation complete (✅ Done)
- [ ] Frontend integration complete (✅ Done)
- [ ] OpenAI API key obtained
- [ ] NHTSA API access (free, no key needed)

### Blockers
- [ ] None identified

### External Services
- **NHTSA API**: Free, public API, no authentication required
  - Endpoint: `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json`
  - Rate Limits: Not specified, but should be reasonable
- **OpenAI API**: Requires API key, pay-per-use
  - Model: `gpt-4o-mini` (recommended for cost efficiency)
  - Cost: ~$0.0003 per request (very low)
  - Rate Limits: Based on API tier

---

## Notes

### Cost Considerations
- **NHTSA API**: Free, no cost
- **OpenAI API**: ~$0.0003 per summary request
  - For 100 reports/month: ~$0.03/month
  - For 1000 reports/month: ~$0.30/month
  - Very affordable for MVP

### Security Considerations
- OpenAI API key must be stored securely (environment variable)
- API key should never be exposed to frontend
- Consider rate limiting for GPT summary endpoint
- Consider caching VIN decode results (optional)

### Future Enhancements
- Cache VIN decode results to reduce API calls
- Add summary caching to reduce OpenAI API calls
- Add summary customization options (tone, length)
- Add multiple language support for summaries
- Add summary history/versioning

### Implementation Order
1. VIN decode service and endpoint (simpler, no API key needed)
2. Frontend VIN input integration
3. GPT summary service and endpoint
4. Frontend summary display integration
5. PDF generation updates
6. Testing and error handling refinement

---

## Implementation Status

### Completed
- [ ] Planning phase

### In Progress
- [ ] None

### Pending
- [ ] VIN decode service implementation
- [ ] GPT summary service implementation
- [ ] API endpoint implementation
- [ ] Frontend integration
- [ ] PDF generation updates
- [ ] Testing

---

## Testing Status

### Passed
- [ ] None yet

### Failed
- [ ] None yet

### Pending
- [ ] All test scenarios

---

## Changes from Original Plan

[To be updated during implementation if plan changes]

---

**Remember:** This plan is the contract. Refer back to it during implementation and testing to stay on track!

