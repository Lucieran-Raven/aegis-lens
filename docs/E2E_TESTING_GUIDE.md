# Aegis Lens MVP 1.0 — End-to-End Testing Guide

This guide provides step-by-step instructions for performing a complete real-world end-to-end test of the Aegis Lens MVP 1.0 system.

---

## PREREQUISITES

### Hardware Required
- **Computer 1 (HR/Interviewer):** Windows/Mac with Chrome/Edge browser, webcam, microphone
- **Computer 2 (Candidate):** Windows/Mac with Chrome/Edge browser, webcam, microphone
- **Network:** Stable internet connection (Wi-Fi or Ethernet)

### Software Required
- **Docker & Docker Compose:** Installed on the deployment machine
- **Browser:** Chrome 120+ or Edge 120+ (both computers)
- **Git:** For cloning the repository

### Optional Testing Tools
- **VM software** (VirtualBox, VMware) for CHRONOS testing
- **Bluetooth earpiece** for ECHO testing
- **Deepfake software or pre-recorded video** for IRIS/LIPSYNC testing

---

## PART 1: DEPLOYMENT

### Step 1.1: Clone the Repository

```bash
git clone https://github.com/Lucieran-Raven/aegis-lens.git
cd aegis-lens
```

### Step 1.2: Set Environment Variables

Create a `.env` file in the root directory:

```bash
# Database Passwords
PG_PASSWORD=aegis_dev_password
TIMESCALE_PASSWORD=aegis_dev_password
NEO4J_PASSWORD=aegis_dev_password

# Application Ports (defaults are fine for local testing)
REDIS_PORT=6379
POSTGRES_PORT=5432
TIMESCALE_PORT=5433
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
PHYSICS_ENGINE_PORT=8080
AGENTS_PORT=8081
ORCHESTRATOR_PORT=8082
SIGNALING_PORT=8083
CANDIDATE_UI_PORT=3002
HR_DASHBOARD_PORT=3003
```

### Step 1.3: Build and Start All Services

```bash
# Build all services
docker-compose build

# Start all services in detached mode
docker-compose up -d

# Check service status
docker-compose ps
```

**Expected Output:**
All 10 services should show as "Up" or "healthy":
- aegis-redis
- aegis-postgres
- aegis-timescale
- aegis-neo4j
- aegis-physics-engine
- aegis-agents
- aegis-orchestrator
- aegis-signaling
- aegis-candidate-ui
- aegis-hr-dashboard

### Step 1.4: Verify Services are Running

```bash
# Check logs for any errors
docker-compose logs

# Test individual services
curl http://localhost:8080/health  # Physics Engine
curl http://localhost:8081/health  # Agents
curl http://localhost:8082/health  # Orchestrator
curl http://localhost:8083/health  # Signaling
```

### Step 1.5: Access the Web Interfaces

- **Candidate UI:** http://localhost:3002
- **HR Dashboard:** http://localhost:3003

Both should load without errors.

---

## PART 2: HAPPY PATH TEST (NO CHEATING)

### Test 2.1: Complete Interview Flow

#### Setup
- **HR Computer:** Open http://localhost:3003
- **Candidate Computer:** Open http://localhost:3002

#### Step 1: Start the Interview (HR Side)

1. **Log into HR Dashboard**
   - Use default credentials or create a test account
   - Verify dashboard loads correctly

2. **Create New Interview Session**
   - Click "New Interview"
   - Enter candidate details
   - Click "Create Session"
   - Verify session ID is generated

3. **Send Session Link to Candidate**
   - Copy the session link
   - Send to candidate (via email/chat)

4. **Start the Session**
   - Click "Start Session"
   - Verify status changes to "Waiting for candidate"

**Verification Checklist:**
- [ ] HR Dashboard loads correctly
- [ ] Session is created with unique ID
- [ ] Session link is generated
- [ ] Start button works
- [ ] Status shows "Waiting for candidate"

#### Step 2: Join the Interview (Candidate Side)

1. **Open Session Link**
   - Candidate opens the link in browser
   - Verify Candidate UI loads

2. **Grant Permissions**
   - Browser requests camera access → Allow
   - Browser requests microphone access → Allow
   - Verify camera turns on (1080p/60fps)
   - Verify microphone works (audio levels visible)

3. **Join Session**
   - Click "Join Interview"
   - Verify connection established

**Verification Checklist:**
- [ ] Candidate UI loads correctly
- [ ] Camera turns on (1080p/60fps)
- [ ] Microphone works (audio levels visible)
- [ ] Candidate sees HR video feed
- [ ] HR sees Candidate video feed
- [ ] Audio is clear (no echo, no delay)

#### Step 3: Conduct the Interview (10-15 minutes)

1. **HR asks first question**
   - Question appears on Candidate UI
   - Verify question is visible

2. **Candidate answers**
   - Candidate speaks
   - Verify live transcript appears on HR Dashboard

3. **Monitor Trust Score**
   - Trust Score should update in real-time (0.00-1.00)
   - Should be > 0.8 for legitimate candidate
   - Agent Status should show all 4 agents: CLEAR

4. **Continue interview**
   - Ask 5-10 follow-up questions
   - Verify analytics update (confidence, stress, engagement)
   - Verify question suggestions appear

**Verification Checklist:**
- [ ] Questions appear on Candidate UI
- [ ] Live transcript appears on HR Dashboard
- [ ] Trust Score updates in real-time (0.00-1.00)
- [ ] Agent Status shows all 4 agents: CLEAR
- [ ] No anomalies detected
- [ ] Question suggestions appear
- [ ] Candidate analytics show (confidence, stress, engagement)
- [ ] Final Trust Score > 0.8
- [ ] Final Status: CLEAR

#### Step 4: End the Interview

1. **HR clicks "End Session"**
   - Verify session ends cleanly

2. **Wait for Report Generation**
   - Should complete within 30 seconds
   - Verify report appears

3. **Review Report**
   - Verify status: CLEAR
   - Verify all questions and answers are present
   - Verify Trust Score is correct
   - Verify agent status for all 4 agents
   - Download PDF report

**Verification Checklist:**
- [ ] Session ends cleanly
- [ ] Report generates within 30 seconds
- [ ] Report shows: CLEAR status
- [ ] Report contains all questions and answers
- [ ] Report contains Trust Score
- [ ] Report contains agent status
- [ ] Report is downloadable as PDF

---

## PART 3: CHEATING SCENARIO TESTS

### Test 3.1: CHRONOS — VM/Emulator Detection

#### Setup
1. Set up a Virtual Machine (VirtualBox, VMware) on Computer 2
2. Install Chrome/Edge in the VM
3. Join the interview from the VM

#### Expected Results
- [ ] CHRONOS Agent detects VM environment
- [ ] Trust Score drops below 0.5
- [ ] Status changes to ANOMALY
- [ ] Alert appears: "VM/Emulator Detected"
- [ ] Alert appears within 10 seconds
- [ ] Alert contains details: "Frame-timing entropy anomaly detected"
- [ ] Report shows: CHRONOS = ANOMALY

### Test 3.2: ECHO — Hidden Earpiece Detection

#### Setup
1. Connect a Bluetooth earpiece to Computer 2
2. Place the earpiece in ear (or simulate)
3. Join the interview

#### Expected Results
- [ ] ECHO Agent detects audio delay > 6ms
- [ ] Trust Score drops below 0.5
- [ ] Status changes to ANOMALY
- [ ] Alert appears: "Audio Routing / Hidden Earpiece Detected"
- [ ] Alert appears within 10 seconds
- [ ] Alert contains details: "Acoustic time-of-flight anomaly: 8ms delay detected"
- [ ] Report shows: ECHO = ANOMALY

### Test 3.3: IRIS — Deepfake/Proxy Detection

#### Setup (choose one):
- Use a deepfake video or AI avatar
- Use a photo/static image (hold up to camera)
- Have another person take the interview (proxy)

#### Expected Results
- [ ] IRIS Agent detects corneal reflection anomaly
- [ ] Trust Score drops below 0.5
- [ ] Status changes to ANOMALY
- [ ] Alert appears: "Face Anomaly / Potential Proxy Detected"
- [ ] Alert appears within 30 seconds
- [ ] Alert contains details: "Corneal reflection parallax anomaly detected"
- [ ] Report shows: IRIS = ANOMALY

### Test 3.4: LIPSYNC — Pre-recorded Video Detection

#### Setup (choose one):
- Record a video of a person speaking
- Play the video during the interview (point camera at screen)
- Use OBS virtual camera with pre-recorded video

#### Expected Results
- [ ] LIPSYNC Agent detects AV-sync drift > 86ms
- [ ] Trust Score drops below 0.5
- [ ] Status changes to ANOMALY
- [ ] Alert appears: "AV-Sync Anomaly / Pre-recorded Video Detected"
- [ ] Alert appears within 30 seconds
- [ ] Alert contains details: "AV-sync drift: 120ms detected"
- [ ] Report shows: LIPSYNC = ANOMALY

### Test 3.5: Multiple Anomalies (Combined Attack)

#### Setup
- Use VM + hidden earpiece + deepfake simultaneously
- Join the interview

#### Expected Results
- [ ] Multiple agents detect anomalies
- [ ] Trust Score drops below 0.3
- [ ] Status changes to FRAUD_DETECTED
- [ ] Alerts appear for all anomalies
- [ ] All relevant alerts appear
- [ ] Final verdict: FRAUD_DETECTED
- [ ] Report shows all anomalies

---

## PART 4: PERFORMANCE & RELIABILITY TESTS

### Test 4.1: Video/Audio Quality

**Verification Checklist:**
- [ ] Video resolution: 1080p (1920x1080)
- [ ] Video frame rate: 30fps (smooth)
- [ ] Audio sample rate: 48kHz (clear)
- [ ] End-to-end latency: < 180ms
- [ ] No dropped frames
- [ ] No audio glitches

### Test 4.2: Network Resilience

#### Setup
1. Start interview with good connection
2. Simulate network issues (use Chrome DevTools → Network → Throttling)
3. Resume normal connection

**Verification Checklist:**
- [ ] Video recovers after network issues
- [ ] Audio recovers after network issues
- [ ] No session disconnection
- [ ] Data is not lost
- [ ] Connection drops and re-establishes
- [ ] Data resumes correctly
- [ ] No data loss

### Test 4.3: Long Interview Duration

#### Setup
1. Start interview
2. Keep it running for 45-60 minutes
3. Monitor system performance

**Verification Checklist:**
- [ ] No memory leaks
- [ ] No performance degradation
- [ ] Trust Score updates consistently
- [ ] No crashes
- [ ] Memory usage < 200MB for all components
- [ ] CPU usage < 80%
- [ ] No errors in logs

---

## PART 5: REPORT GENERATION TESTS

### Test 5.1: Report Accuracy

**Verification Checklist:**
- [ ] Report contains correct Trust Score
- [ ] Report contains correct Status
- [ ] Report contains all questions and answers
- [ ] Report contains all anomalies (if any)
- [ ] Report contains agent status for all 4 agents
- [ ] Report is formatted correctly (PDF)

### Test 5.2: Report Export

**Verification Checklist:**
- [ ] Report can be downloaded as PDF
- [ ] PDF is readable
- [ ] PDF contains all data
- [ ] PDF is formatted professionally

---

## PART 6: EDGE CASE TESTS

### Test 6.1: Candidate Denies Camera Access

**Setup:** Deny camera permission when prompted

**Verification Checklist:**
- [ ] IRIS Agent shows: NO_FACE
- [ ] IRIS status: SUSPECT or ANOMALY
- [ ] Trust Score affected
- [ ] Alert: "Camera Access Denied"

### Test 6.2: Candidate Denies Microphone Access

**Setup:** Deny microphone permission when prompted

**Verification Checklist:**
- [ ] ECHO Agent shows: NO_AUDIO
- [ ] ECHO status: SUSPECT or ANOMALY
- [ ] Trust Score affected
- [ ] Alert: "Microphone Access Denied"

### Test 6.3: Candidate Leaves Mid-Interview

**Setup:** Candidate closes browser or disconnects

**Verification Checklist:**
- [ ] Session ends cleanly
- [ ] Partial report generated
- [ ] Data preserved

### Test 6.4: Very Low Bandwidth

**Setup:** Use Chrome DevTools → Network → Throttling → "Slow 3G"

**Verification Checklist:**
- [ ] Video quality degrades gracefully
- [ ] Audio remains clear
- [ ] Physics data still collected
- [ ] Trust Score still calculated

---

## PART 7: DOCUMENTATION

### Step 7.1: Complete the Test Report

Open `docs/REAL_WORLD_E2E_TEST_REPORT.md` and fill in all test results:

1. Fill in date, testers, environment
2. Mark each test as PASS/FAIL
3. Add notes for any issues
4. Add screenshots (upload to image host and add links)
5. Document any bugs found
6. Record performance metrics
7. Provide final recommendation

### Step 7.2: Submit the Report

Commit the completed test report:

```bash
git add docs/REAL_WORLD_E2E_TEST_REPORT.md
git commit -m "test: Complete E2E test report"
git push
```

---

## TROUBLESHOOTING

### Services Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Restart services
docker-compose restart

# Rebuild services
docker-compose down
docker-compose build
docker-compose up -d
```

### Can't Access Web Interfaces

```bash
# Check if ports are in use
netstat -ano | findstr :3002
netstat -ano | findstr :3003

# Kill processes using ports (Windows)
taskkill /PID [PID] /F

# Kill processes using ports (Mac/Linux)
kill -9 [PID]
```

### Database Connection Errors

```bash
# Check database health
docker-compose exec postgres pg_isready -U aegis
docker-compose exec timescaledb pg_isready -U aegis
docker-compose exec neo4j curl -f http://localhost:7474

# Restart databases
docker-compose restart postgres timescaledb neo4j
```

### Clear All Data and Start Fresh

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## SUCCESS CRITERIA

The E2E test is COMPLETE when:

- ✅ ALL tests in Parts 2-6 are PASSING
- ✅ ALL components work together
- ✅ Trust Score updates correctly
- ✅ Anomalies are detected correctly
- ✅ Report generates correctly
- ✅ No critical bugs found
- ✅ Test report is documented in `docs/REAL_WORLD_E2E_TEST_REPORT.md`

**IF ANY TEST FAILS:**
1. Document the issue in the test report
2. Fix the issue
3. Re-run ALL tests
4. Update the test report

**ONLY AFTER ALL TESTS PASS:**
Proceed to Category 9 (Polish & Launch).

---

## NEXT STEPS

After completing the E2E test:

1. **Review the test report** with the team
2. **Fix any critical bugs** found during testing
3. **Re-run failed tests** to verify fixes
4. **Update documentation** based on findings
5. **Prepare for launch** if all tests pass

---

**Be BRUTAL. Test EVERYTHING. Find EVERY bug. Fix EVERY issue.**

**ONLY THEN can we say MVP 1.0 is ready for launch.**
